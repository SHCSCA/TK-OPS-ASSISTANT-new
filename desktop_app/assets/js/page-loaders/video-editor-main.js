/* ── page-loaders/video-editor-main.js ─ 视频剪辑页面加载器 ──
   从 page-loaders.js 主文件拆出，注册到全局 loaders 表。
   依赖：page-loaders.js（提供 loaders 对象与共享工具函数）
         page-loaders/editor-shared.js（buildAssetThumb / bindAssetThumbs）
   ──────────────────────────────────────────────────── */
(function () {
    'use strict';

    if (typeof window._pageLoaders === 'undefined') {
        console.warn('[video-editor-main] _pageLoaders not ready, deferring');
        return;
    }

    var runtimeSummaryHandlers = window.__runtimeSummaryHandlers || {};

    var _runtime = {
        assets: [],
        projects: [],
        counts: { video: 0, image: 0, subtitle: 0, audio: 0 },
        snapMs: 200,
        monitor: {
            selectionKey: '',
            pollHandle: null,
            requestId: 0,
            state: {
                ready: false,
                source_path: '',
                duration_ms: 0,
                position_ms: 0,
                clip_start_ms: 0,
                clip_end_ms: 0,
                playing: false,
                status: 'idle',
                error: '',
                frame_token: 0,
                frame_data: '',
            },
        },
    };
    var _dragPayload = null;

    function _state() {
        if (typeof uiState === 'undefined') {
            return { assetType: 'video', selectedAssetId: null, selectedClipId: null, selectedSubtitleId: null, inspectorTab: 'properties', projectId: null, sequenceId: null };
        }
        uiState['video-editor'] = uiState['video-editor'] || { assetType: 'video', selectedAssetId: null, selectedClipId: null, selectedSubtitleId: null, inspectorTab: 'properties', projectId: null, sequenceId: null };
        if (typeof uiState['video-editor'].selectedClipId === 'undefined') {
            uiState['video-editor'].selectedClipId = null;
        }
        if (typeof uiState['video-editor'].selectedSubtitleId === 'undefined') {
            uiState['video-editor'].selectedSubtitleId = null;
        }
        return uiState['video-editor'];
    }

    function _toId(value) {
        return value === undefined || value === null || value === '' ? null : String(value);
    }

    function _toNumber(value) {
        var number = parseInt(value || 0, 10);
        return Number.isFinite(number) ? number : 0;
    }

    function _timecode(ms) {
        var totalSeconds = Math.max(0, Math.floor(_toNumber(ms) / 1000));
        var hours = Math.floor(totalSeconds / 3600);
        var minutes = Math.floor((totalSeconds % 3600) / 60);
        var seconds = totalSeconds % 60;
        if (hours > 0) {
            return String(hours).padStart(2, '0') + ':' + String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');
        }
        return String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');
    }

    function _normalizeAssetType(asset) {
        var type = String((asset && asset.asset_type) || '').toLowerCase();
        if (type === 'text') return 'subtitle';
        if (type === 'template') return 'image';
        if (type === 'video' || type === 'image' || type === 'audio' || type === 'subtitle') return type;
        return 'image';
    }

    function _countAssets(assets) {
        var counts = { video: 0, image: 0, subtitle: 0, audio: 0 };
        (assets || []).forEach(function (asset) {
            counts[_normalizeAssetType(asset)] += 1;
        });
        return counts;
    }

    function _typeLabel(type) {
        if (type === 'video') return '视频';
        if (type === 'image') return '图片';
        if (type === 'subtitle') return '字幕';
        if (type === 'audio') return '音频';
        return '素材';
    }

    function _splitTags(asset) {
        return String((asset && asset.tags) || '')
            .split(/[，,、/\s]+/)
            .map(function (item) { return item.trim(); })
            .filter(Boolean);
    }

    function _parseJsonObject(value) {
        try {
            var parsed = JSON.parse(String(value || '{}'));
            return parsed && typeof parsed === 'object' ? parsed : {};
        } catch (error) {
            return {};
        }
    }

    function _clipDurationMs(clip) {
        var duration = _toNumber(clip && clip.duration_ms);
        if (duration > 0) return duration;
        return Math.max(0, _toNumber(clip && clip.source_out_ms) - _toNumber(clip && clip.source_in_ms));
    }

    function _clipEndMs(clip) {
        return _toNumber(clip && clip.start_ms) + _clipDurationMs(clip);
    }

    function _sequenceDurationMs(context) {
        var sequenceDuration = _toNumber(context.sequence && context.sequence.duration_ms);
        var clipDuration = (context.activeClips || []).reduce(function (maxValue, clip) {
            return Math.max(maxValue, _clipEndMs(clip));
        }, 0);
        var subtitleDuration = (context.subtitles || []).reduce(function (maxValue, subtitle) {
            return Math.max(maxValue, _toNumber(subtitle && subtitle.end_ms));
        }, 0);
        return Math.max(sequenceDuration, clipDuration, subtitleDuration, 1000);
    }

    function _trackLabel(trackType, trackIndex) {
        var prefix = String(trackType || '').toLowerCase() === 'audio' ? 'A' : 'V';
        return prefix + String(_toNumber(trackIndex) + 1);
    }

    function _audioClipState(clip) {
        if (!clip || String(clip.track_type || '').toLowerCase() !== 'audio') return null;
        var meta = _parseJsonObject(clip.meta_json);
        var volume = Math.max(0, Math.min(2, Number(clip.volume || 0)));
        var remembered = Number(meta.pre_mute_volume || (volume > 0 ? volume : 1));
        var muted = !!meta.audio_muted || volume <= 0.0001;
        var activeVolume = muted ? Math.max(0, Math.min(2, remembered || 1)) : volume;
        return {
            muted: muted,
            volume: volume,
            rememberedVolume: Math.max(0, Math.min(2, remembered || 1)),
            label: muted ? '已静音' : ('音量 ' + Math.round(activeVolume * 100) + '%'),
        };
    }

    function _exportStatusText(status) {
        var normalized = String(status || '').toLowerCase();
        if (normalized === 'completed') return '已完成';
        if (normalized === 'failed') return '失败';
        if (normalized === 'processing' || normalized === 'running') return '处理中';
        return '待处理';
    }

    function _exportStatusTone(status) {
        var normalized = String(status || '').toLowerCase();
        if (normalized === 'completed') return 'success';
        if (normalized === 'failed') return 'error';
        return 'warning';
    }

    function _filteredAssets(assets, assetType) {
        return (assets || []).filter(function (asset) {
            return _normalizeAssetType(asset) === (assetType || 'video');
        });
    }

    function _sequenceEntries(projects) {
        var entries = [];
        (projects || []).forEach(function (project) {
            (project.sequences || []).forEach(function (sequence) {
                entries.push({
                    projectId: _toId(project.id),
                    projectName: project.name || '未命名项目',
                    sequenceId: _toId(sequence.id),
                    sequenceName: sequence.name || '主序列',
                });
            });
        });
        return entries;
    }

    function _resolveContext(projects, state) {
        var selectedProject = null;
        var selectedSequence = null;
        var selectedProjectId = _toId(state.projectId);
        var selectedSequenceId = _toId(state.sequenceId);

        (projects || []).some(function (project) {
            if (_toId(project.id) !== selectedProjectId) return false;
            selectedProject = project;
            return true;
        });
        if (!selectedProject) {
            selectedProject = (projects || [])[0] || null;
        }

        if (selectedProject) {
            if (selectedSequenceId) {
                (selectedProject.sequences || []).some(function (sequence) {
                    if (_toId(sequence.id) !== selectedSequenceId) return false;
                    selectedSequence = sequence;
                    return true;
                });
            }
            if (!selectedSequence && selectedProject.active_sequence_id) {
                (selectedProject.sequences || []).some(function (sequence) {
                    if (_toId(sequence.id) !== _toId(selectedProject.active_sequence_id)) return false;
                    selectedSequence = sequence;
                    return true;
                });
            }
            if (!selectedSequence) {
                selectedSequence = (selectedProject.sequences || [])[0] || null;
            }
        }

        state.projectId = selectedProject ? _toId(selectedProject.id) : null;
        state.sequenceId = selectedSequence ? _toId(selectedSequence.id) : null;

        return {
            project: selectedProject,
            sequence: selectedSequence,
            exports: selectedProject && selectedProject.exports ? selectedProject.exports : [],
            activeClips: selectedSequence && selectedSequence.clips ? selectedSequence.clips : [],
            subtitles: selectedSequence && selectedSequence.subtitles ? selectedSequence.subtitles : [],
            sequenceAssets: selectedSequence && selectedSequence.assets ? selectedSequence.assets : [],
            validation: selectedProject && selectedProject.export_validation
                ? selectedProject.export_validation
                : { ok: false, errors: ['当前还没有可导出的活动序列'] },
        };
    }

    function _applyRuntimeSummary(context, counts) {
        var handler = runtimeSummaryHandlers['video-editor'];
        if (typeof handler !== 'function') return;
        handler({
            project: context.project,
            sequence: context.sequence,
            exports: context.exports || [],
            clips: context.activeClips || [],
            subtitles: context.subtitles || [],
            counts: counts || _runtime.counts,
            validation: context.validation || { ok: false, errors: [] },
        });
    }

    function _findAssetById(assets, assetId) {
        var normalizedId = _toId(assetId);
        var match = null;
        (assets || []).some(function (asset) {
            if (_toId(asset.id) !== normalizedId) return false;
            match = asset;
            return true;
        });
        return match;
    }

    function _findClipById(clips, clipId) {
        var normalizedId = _toId(clipId);
        var match = null;
        (clips || []).some(function (clip) {
            if (_toId(clip.id) !== normalizedId) return false;
            match = clip;
            return true;
        });
        return match;
    }

    function _findSubtitleById(subtitles, subtitleId) {
        var normalizedId = _toId(subtitleId);
        var match = null;
        (subtitles || []).some(function (subtitle) {
            if (_toId(subtitle.id) !== normalizedId) return false;
            match = subtitle;
            return true;
        });
        return match;
    }

    function _findClipForAsset(clips, assetId) {
        var normalizedId = _toId(assetId);
        var match = null;
        (clips || []).some(function (clip) {
            if (_toId(clip.asset_id) !== normalizedId) return false;
            match = clip;
            return true;
        });
        return match;
    }

    function _assetFromClip(clip) {
        if (!clip || !_toId(clip.asset_id)) return null;
        return {
            id: _toId(clip.asset_id),
            filename: clip.asset_filename || ('素材 #' + _toId(clip.asset_id)),
            asset_type: clip.asset_type || 'video',
            file_path: clip.asset_file_path || '',
            poster_path: clip.poster_path || '',
        };
    }

    function _timelineWidthPx(sequenceDurationMs) {
        return Math.max(960, Math.round(Math.max(sequenceDurationMs, 1000) / 1000 * 96));
    }

    function _timelineLabelWidthPx() {
        return 92;
    }

    function _timelineOffsetPx(positionMs, totalDurationMs, widthPx) {
        if (widthPx <= 0 || totalDurationMs <= 0) return 0;
        return Math.max(0, Math.min(widthPx, Math.round((Math.max(0, positionMs) / totalDurationMs) * widthPx)));
    }

    function _snapMs(positionMs) {
        var snapMs = Math.max(40, _toNumber(_runtime.snapMs || 200));
        return Math.round(Math.max(0, positionMs) / snapMs) * snapMs;
    }

    function _monitorApi() {
        return window.api && window.api.videoProjects ? window.api.videoProjects : null;
    }

    function _emptyMonitorState() {
        return {
            ready: false,
            source_path: '',
            duration_ms: 0,
            position_ms: 0,
            clip_start_ms: 0,
            clip_end_ms: 0,
            playing: false,
            status: 'idle',
            error: '',
            frame_token: 0,
            frame_data: '',
        };
    }

    function _updateMonitorState(nextState) {
        _runtime.monitor.state = Object.assign(_emptyMonitorState(), nextState || {});
    }

    function _stopMonitorPolling() {
        if (_runtime.monitor.pollHandle) {
            clearInterval(_runtime.monitor.pollHandle);
            _runtime.monitor.pollHandle = null;
        }
    }

    function _pollMonitorState() {
        var api = _monitorApi();
        if (!api || typeof api.getVideoMonitorState !== 'function') return Promise.resolve(_runtime.monitor.state);
        return api.getVideoMonitorState().then(function (state) {
            _updateMonitorState(state);
            return _runtime.monitor.state;
        }).catch(function () {
            return _runtime.monitor.state;
        });
    }

    function _startMonitorPolling() {
        _stopMonitorPolling();
        _runtime.monitor.pollHandle = setInterval(function () {
            _pollMonitorState().then(function () {
                _applyMonitorDom();
                _updatePlayheadDom();
            });
        }, 180);
    }

    function _monitorSelection(selection, fallbackAsset) {
        var asset = selection && selection.clip
            ? (_findAssetById(_runtime.assets, selection.clip.asset_id) || _assetFromClip(selection.clip) || fallbackAsset)
            : fallbackAsset;
        if (!asset || _normalizeAssetType(asset) !== 'video' || !asset.file_path) return null;
        var clip = selection && selection.clip ? selection.clip : null;
        return {
            asset: asset,
            startMs: clip ? _toNumber(clip.source_in_ms) : 0,
            endMs: clip ? _toNumber(clip.source_out_ms) : 0,
            selectionKey: [
                _toId(asset.id),
                clip ? _toId(clip.id) : 'asset',
                clip ? _toNumber(clip.source_in_ms) : 0,
                clip ? _toNumber(clip.source_out_ms) : 0,
                asset.file_path || '',
            ].join('::'),
        };
    }

    function _resolveSelection(state, context) {
        var filteredAssets = _filteredAssets(_runtime.assets, state.assetType);
        var selectedClip = _findClipById(context.activeClips, state.selectedClipId);
        var selectedSubtitle = _findSubtitleById(context.subtitles, state.selectedSubtitleId);
        var selectedAsset = selectedClip
            ? (_findAssetById(_runtime.assets, selectedClip.asset_id) || _assetFromClip(selectedClip))
            : _findAssetById(_runtime.assets, state.selectedAssetId);

        if (selectedAsset) {
            var selectedType = _normalizeAssetType(selectedAsset);
            if (selectedType !== state.assetType) {
                state.assetType = selectedType;
                filteredAssets = _filteredAssets(_runtime.assets, state.assetType);
            }
        }
        if (!selectedAsset && filteredAssets.length && !selectedSubtitle) {
            selectedAsset = filteredAssets[0];
        }
        if (!selectedClip) {
            selectedClip = null;
        }
        if (selectedClip) {
            selectedSubtitle = null;
        }

        state.selectedAssetId = selectedAsset ? _toId(selectedAsset.id) : null;
        state.selectedClipId = selectedClip ? _toId(selectedClip.id) : null;
        state.selectedSubtitleId = selectedSubtitle ? _toId(selectedSubtitle.id) : null;

        return {
            filteredAssets: filteredAssets,
            asset: selectedAsset,
            clip: selectedClip,
            subtitle: selectedSubtitle,
        };
    }

    function _cardHtml(card) {
        return '<article class="workbench-sidecard"><div class="workbench-sidecard__head"><strong>' + (card.title || '信息') + '</strong><span class="pill ' + (card.tone || 'info') + '">' + (card.badge || '已同步') + '</span></div><div class="subtle">' + (card.desc || '暂无说明') + '</div></article>';
    }

    function _buildInspectorCards(tabKey, selection, context, counts) {
        var asset = selection.asset;
        var clip = selection.clip;
        var subtitle = selection.subtitle;
        var audioState = _audioClipState(clip);
        var totalAssets = counts.video + counts.image + counts.subtitle + counts.audio;
        if (tabKey === 'subtitle') {
            return [
                { title: '字幕轨', desc: context.subtitles.length ? ('当前序列共有 ' + context.subtitles.length + ' 条字幕段，最晚覆盖到 ' + _timecode((context.subtitles[context.subtitles.length - 1] || {}).end_ms) + '。') : '当前还没有字幕段，可直接在时间轴上新建。', badge: context.subtitles.length + ' 条', tone: context.subtitles.length ? 'success' : 'warning' },
                { title: '当前字幕', desc: subtitle ? ((subtitle.text || '未命名字幕段') + ' / ' + _timecode(subtitle.start_ms) + ' - ' + _timecode(subtitle.end_ms)) : '尚未选中字幕块，可点击时间轴字幕段或使用“字幕块”按钮新建。', badge: subtitle ? '已选中' : '等待选择', tone: subtitle ? 'info' : 'warning' },
                { title: '字幕动作', desc: subtitle ? '当前字幕块可继续改文案、改入出点或直接删除。' : (clip ? ('可基于当前片段 ' + _timecode(clip.start_ms) + ' - ' + _timecode(_clipEndMs(clip)) + ' 快速补字幕。') : '先选中时间轴片段，再补当前口播或画面说明。'), badge: subtitle ? '可编辑' : (clip ? '快速新建' : '等待片段'), tone: subtitle || clip ? 'info' : 'warning' },
            ];
        }
        if (tabKey === 'export') {
            var validationErrors = (context.validation && context.validation.errors) || [];
            var latestExport = context.exports && context.exports.length ? context.exports[0] : null;
            return [
                { title: '当前项目', desc: ((context.project && context.project.name) || '视频剪辑工作区') + ' / ' + ((context.sequence && context.sequence.name) || '主序列') + ' / 片段 ' + context.activeClips.length + ' 段 / 字幕 ' + context.subtitles.length + ' 条', badge: '项目', tone: 'info' },
                { title: '导出校验', desc: context.validation && context.validation.ok ? '当前序列已通过基础导出校验，可直接发起终版导出。' : (validationErrors[0] || '当前序列还不能导出。'), badge: context.validation && context.validation.ok ? '通过' : ('待处理 ' + validationErrors.length), tone: context.validation && context.validation.ok ? 'success' : 'warning' },
                { title: '最近导出', desc: latestExport ? ('预设 ' + (latestExport.preset || 'mp4_1080p') + ' / 状态 ' + _exportStatusText(latestExport.status) + (latestExport.output_path ? (' / ' + latestExport.output_path) : '')) : '当前还没有导出记录。', badge: latestExport ? _exportStatusText(latestExport.status) : '待发起', tone: latestExport ? _exportStatusTone(latestExport.status) : 'warning' },
            ];
        }
        return [
            { title: '当前对象', desc: clip ? ((asset ? asset.filename : (clip.asset_filename || '未绑定素材')) + ' / ' + _trackLabel(clip.track_type, clip.track_index) + (audioState ? (' / ' + audioState.label) : '')) : (asset ? (asset.filename + ' / ' + _typeLabel(_normalizeAssetType(asset))) : '尚未选中素材，请先在素材库或时间轴中点选一个条目。'), badge: clip ? '时间线片段' : (asset ? '素材预览' : '待选择'), tone: asset || clip ? 'success' : 'warning' },
            { title: '当前操作', desc: clip ? (audioState ? ('当前位于 A1 音频轨，' + (audioState.muted ? '已静音，可通过“A1 音频”恢复或继续调音量。' : ('输出' + audioState.label + '，可继续静音、改音量或删除片段。'))) : ('入点 ' + _timecode(clip.source_in_ms) + ' / 出点 ' + _timecode(clip.source_out_ms) + ' / 可继续裁切、删除或补字幕。')) : (asset ? (_normalizeAssetType(asset) === 'audio' ? '当前音频仅处于序列素材池，可拖到 A1 或使用“A1 音频”直接加入。' : '当前素材仅处于序列素材池，拖拽到时间轴后才进入可编辑状态。') : '当前还没有选中时间线片段。'), badge: clip ? '可编辑' : (asset ? '仅可预览' : '未绑定'), tone: clip ? 'info' : 'warning' },
            { title: '当前序列', desc: (context.sequence ? context.sequence.name : '主序列') + ' / 素材池 ' + totalAssets + ' 条 / 时间线 ' + context.activeClips.length + ' 段 / 字幕 ' + context.subtitles.length + ' 条 / 总时长 ' + _timecode(_sequenceDurationMs(context)), badge: '序列', tone: 'info' },
        ];
    }

    function _renderTabs(state, counts) {
        var labels = {
            video: ['视频', counts.video],
            image: ['图片', counts.image],
            subtitle: ['字幕', counts.subtitle],
            audio: ['音频', counts.audio],
        };
        document.querySelectorAll('#mainHost .source-browser-tabs [data-type]').forEach(function (tab) {
            var type = tab.dataset.type || 'video';
            var label = labels[type] || ['素材', 0];
            tab.classList.toggle('is-selected', type === state.assetType);
            tab.innerHTML = label[0] + ' <em>' + label[1] + '</em>';
        });
    }

    function _renderHeader(context, counts, selection) {
        var previewMeta = document.querySelector('#mainHost .video-preview-head .subtle');
        var projectCopy = document.querySelector('#mainHost .js-video-project-copy');
        var projectMeta = document.querySelector('#mainHost .js-video-project-meta');
        var validationErrors = (context.validation && context.validation.errors) || [];
        var latestExport = context.exports && context.exports.length ? context.exports[0] : null;
        if (previewMeta) {
            var clipSummary = selection.clip
                ? ('当前片段 ' + _trackLabel(selection.clip.track_type, selection.clip.track_index) + ' / ' + _timecode(selection.clip.start_ms) + ' - ' + _timecode(_clipEndMs(selection.clip)))
                : (selection.asset ? '素材库预览 / 拖拽到时间轴后可编辑' : '等待选择时间轴片段或素材');
            previewMeta.textContent = clipSummary;
        }
        if (projectCopy) {
            projectCopy.textContent = ((context.project && context.project.name) || '当前工程') + ' / ' + ((context.sequence && context.sequence.name) || '主序列') + ' / 素材池 ' + (counts.video + counts.image + counts.subtitle + counts.audio) + ' 条 / 字幕 ' + context.subtitles.length + ' 条 / ' + (context.validation && context.validation.ok ? '已通过导出校验' : ('导出前仍需处理 ' + validationErrors.length + ' 项'));
        }
        if (projectMeta) {
            projectMeta.innerHTML = '<span class="pill info">序列 ' + ((context.sequence && context.sequence.name) || '主序列') + '</span>'
                + '<span class="pill success">时长 ' + _timecode(_sequenceDurationMs(context)) + '</span>'
                + '<span class="pill info">字幕 ' + context.subtitles.length + ' 条</span>'
                + '<span class="pill ' + ((context.validation && context.validation.ok) ? 'success' : 'warning') + '">' + ((context.validation && context.validation.ok) ? '可导出' : '待校验') + '</span>';
            if (latestExport) {
                projectMeta.innerHTML += '<span class="pill ' + _exportStatusTone(latestExport.status) + '">最近导出 ' + _exportStatusText(latestExport.status) + '</span>';
            }
        }
    }

    function _renderInspector(state, selection, context, counts) {
        document.querySelectorAll('#detailHost .video-inspector-tabs [data-tab]').forEach(function (tab) {
            tab.classList.toggle('is-selected', (tab.dataset.tab || 'properties') === state.inspectorTab);
        });
        var inspectorCopy = document.querySelector('#detailHost .js-video-inspector-copy');
        var contentHost = document.querySelector('#detailHost .js-video-inspector-content');
        var audioState = _audioClipState(selection.clip);
        if (inspectorCopy) {
            inspectorCopy.textContent = state.inspectorTab === 'subtitle'
                ? (selection.subtitle ? '当前正在编辑时间轴字幕块，可直接改文案与时间范围' : '仅显示字幕轨、当前字幕块和补字幕动作')
                : state.inspectorTab === 'export'
                    ? '仅显示当前导出校验、未闭环问题与最近一次导出状态'
                    : (audioState ? '当前为 A1 音频片段，可直接调整音量与静音' : '仅显示当前素材、片段和序列状态');
        }
        if (contentHost) {
            contentHost.innerHTML = _buildInspectorCards(state.inspectorTab, selection, context, counts).map(_cardHtml).join('');
        }
    }

    function _buildRulerMarks(sequenceDurationMs) {
        var marks = [];
        var steps = 6;
        var total = Math.max(sequenceDurationMs, 1000);
        for (var index = 0; index <= steps; index += 1) {
            marks.push({
                label: _timecode(Math.round(total * (index / steps))),
                ratio: index / steps,
            });
        }
        return marks;
    }

    function _monitorStatusText() {
        var state = _runtime.monitor.state || _emptyMonitorState();
        if (state.error) return state.error;
        if (state.playing) return '正在播放';
        if (state.status === 'loading' || state.status === 'buffering') return '正在加载';
        if (state.status === 'paused' || state.status === 'loaded' || state.status === 'buffered') return '已暂停';
        if (state.status === 'ended') return '播放完成';
        if (state.status === 'unsupported') return '当前环境不支持原生预览';
        return '准备预览';
    }

    function _applyMonitorDom(selection, context, videoPreviewAsset) {
        var frame = document.querySelector('#mainHost .js-video-monitor-frame');
        var button = document.querySelector('#mainHost .js-video-monitor-toggle-playback');
        var status = document.querySelector('#mainHost .js-video-monitor-status');
        var chip = document.querySelector('#mainHost .js-video-monitor-chip');
        var meta = document.querySelector('#mainHost .js-video-monitor-meta');
        var monitorState = _runtime.monitor.state || _emptyMonitorState();
        var sequenceDurationText = _timecode(_sequenceDurationMs(context || {}));
        var activePosition = _timecode(monitorState.position_ms || 0);
        var activeDuration = _timecode((monitorState.clip_end_ms || monitorState.duration_ms || 0));
        if (frame && monitorState.frame_data) {
            frame.src = monitorState.frame_data;
        }
        if (button) {
            button.textContent = monitorState.playing ? '暂停' : '播放';
            button.disabled = !videoPreviewAsset || _normalizeAssetType(videoPreviewAsset) !== 'video' || !!monitorState.error;
        }
        if (status) {
            status.textContent = _monitorStatusText();
            status.classList.toggle('is-error', !!monitorState.error);
            status.classList.toggle('is-playing', !!monitorState.playing);
        }
        if (chip) {
            if (!videoPreviewAsset) {
                chip.textContent = '等待选择';
            } else if (selection && selection.clip) {
                chip.textContent = activePosition + ' / ' + (activeDuration === '00:00' ? sequenceDurationText : activeDuration);
            } else {
                chip.textContent = '素材预览 / ' + (activeDuration === '00:00' ? sequenceDurationText : activeDuration);
            }
        }
        if (meta) {
            if (!videoPreviewAsset) {
                meta.textContent = '等待选择素材或片段';
            } else if (selection && selection.clip) {
                meta.textContent = ((context && context.sequence && context.sequence.name) || '主序列') + ' / 片段预览 / ' + (videoPreviewAsset.filename || '未命名素材');
            } else {
                meta.textContent = ((context && context.sequence && context.sequence.name) || '主序列') + ' / 素材库预览 / ' + (videoPreviewAsset.filename || '未命名素材') + ' / 拖拽到时间轴后可剪辑';
            }
        }
        var readout = document.querySelector('#mainHost .js-video-playhead-readout');
        if (readout) {
            readout.textContent = '当前 ' + activePosition + ' / ' + (activeDuration === '00:00' ? sequenceDurationText : activeDuration);
        }
    }

    function _updatePlayheadDom() {
        var board = document.querySelector('#mainHost .js-video-timeline-board');
        if (!board) return;
        var surface = board.querySelector('.js-video-timeline-board-surface');
        var playhead = board.querySelector('.js-video-timeline-playhead');
        var label = board.querySelector('.js-video-timeline-playhead-label');
        if (!surface || !playhead || !label) return;
        var width = _toNumber(surface.dataset.timelineWidth || 0);
        var total = _toNumber(surface.dataset.timelineDuration || 0);
        var labelWidth = _toNumber(surface.dataset.timelineLabelWidth || _timelineLabelWidthPx());
        var position = _snapMs(_runtime.monitor.state && _runtime.monitor.state.position_ms ? _runtime.monitor.state.position_ms : 0);
        var offset = labelWidth + _timelineOffsetPx(position, total, width);
        playhead.style.left = offset + 'px';
        label.style.left = offset + 'px';
        label.textContent = _timecode(position);
    }

    function _prepareMonitor(selection, context, videoPreviewAsset) {
        var api = _monitorApi();
        var monitorSelection = _monitorSelection(selection, videoPreviewAsset);
        if (!api || typeof api.prepareVideoMonitor !== 'function') {
            return Promise.resolve(_runtime.monitor.state);
        }
        if (!monitorSelection) {
            _runtime.monitor.selectionKey = '';
            _stopMonitorPolling();
            _updateMonitorState(_emptyMonitorState());
            _applyMonitorDom(selection, context, videoPreviewAsset);
            _updatePlayheadDom();
            return Promise.resolve(_runtime.monitor.state);
        }
        if (_runtime.monitor.selectionKey === monitorSelection.selectionKey) {
            _applyMonitorDom(selection, context, videoPreviewAsset);
            _updatePlayheadDom();
            return Promise.resolve(_runtime.monitor.state);
        }
        _runtime.monitor.selectionKey = monitorSelection.selectionKey;
        _runtime.monitor.requestId += 1;
        var requestId = _runtime.monitor.requestId;
        return api.prepareVideoMonitor({
            file_path: monitorSelection.asset.file_path,
            start_ms: monitorSelection.startMs,
            end_ms: monitorSelection.endMs,
            autoplay: false,
        }).then(function (state) {
            if (requestId !== _runtime.monitor.requestId) return _runtime.monitor.state;
            _updateMonitorState(state);
            _startMonitorPolling();
            _applyMonitorDom(selection, context, videoPreviewAsset);
            _updatePlayheadDom();
            return _runtime.monitor.state;
        }).catch(function (err) {
            _updateMonitorState(Object.assign(_emptyMonitorState(), { error: (err && err.message) || '预览不可用', status: 'error' }));
            _applyMonitorDom(selection, context, videoPreviewAsset);
            _updatePlayheadDom();
            return _runtime.monitor.state;
        });
    }

    function _renderMonitor(selection, context) {
        var surface = document.querySelector('#mainHost .js-video-monitor-surface');
        var chip = document.querySelector('#mainHost .js-video-monitor-chip');
        var videoPreviewAsset = selection.clip
            ? (_findAssetById(_runtime.assets, selection.clip.asset_id) || _assetFromClip(selection.clip) || selection.asset)
            : selection.asset;
        var sequenceDurationText = _timecode(_sequenceDurationMs(context));

        if (chip) {
            chip.textContent = selection.clip
                ? (_timecode(selection.clip.start_ms) + ' - ' + _timecode(_clipEndMs(selection.clip)) + ' / ' + sequenceDurationText)
                : (selection.asset ? ('素材预览 / ' + sequenceDurationText) : '等待选择');
        }
        if (!surface) return;
        if (!videoPreviewAsset || !window._editorShared || typeof window._editorShared.buildStagePreview !== 'function') {
            surface.innerHTML = '<div class="video-monitor-stage video-monitor-stage--empty"><div class="video-monitor-stage__empty"><strong>等待选择</strong><span>从左侧素材库或下方时间轴选择一个片段</span></div></div>';
            _applyMonitorDom(selection, context, null);
            return;
        }
        surface.innerHTML = window._editorShared.buildStagePreview(videoPreviewAsset, {
            secondaryText: selection.clip
                ? (((context.sequence && context.sequence.name) || '主序列') + ' / 起点 ' + _timecode(selection.clip.start_ms))
                : (((context.sequence && context.sequence.name) || '主序列') + ' / 素材池预览'),
            durationText: selection.clip ? ('时长 ' + _timecode(_clipDurationMs(selection.clip))) : ('序列 ' + sequenceDurationText),
            markerText: selection.clip ? ('轨道 ' + _trackLabel(selection.clip.track_type, selection.clip.track_index)) : _typeLabel(_normalizeAssetType(videoPreviewAsset)),
        });
        if (typeof window._editorShared.hydrateRuntimePreviews === 'function') {
            window._editorShared.hydrateRuntimePreviews(surface);
        }
        _applyMonitorDom(selection, context, videoPreviewAsset);
        _prepareMonitor(selection, context, videoPreviewAsset);
    }

    function _buildTimelineClipBlock(clip, asset, selected, totalDurationMs, widthPx) {
        var label = asset ? asset.filename : (clip.asset_filename || '未绑定素材');
        var toneClass = String(clip.track_type || '').toLowerCase() === 'audio' ? ' timeline-block--accent' : ' timeline-block--primary';
        var startPx = _timelineOffsetPx(_toNumber(clip.start_ms), totalDurationMs, widthPx);
        var clipWidth = Math.max(88, _timelineOffsetPx(_clipDurationMs(clip), totalDurationMs, widthPx));
        return ''
            + '<button class="timeline-block timeline-block--timed' + toneClass + (selected ? ' is-selected' : '') + '" type="button" draggable="true" data-clip-id="' + _toId(clip.id) + '" data-asset-id="' + _toId(clip.asset_id) + '" data-track-type="' + String(clip.track_type || 'video') + '" style="left:' + startPx + 'px;width:' + clipWidth + 'px;">'
            + '<strong>' + label + '</strong>'
            + '<small>' + _timecode(clip.start_ms) + ' - ' + _timecode(_clipEndMs(clip)) + '</small>'
            + '</button>';
    }

    function _buildTimelineSubtitleBlock(subtitle, index, selected, totalDurationMs, widthPx) {
        var startPx = _timelineOffsetPx(_toNumber(subtitle.start_ms), totalDurationMs, widthPx);
        var subtitleWidth = Math.max(72, _timelineOffsetPx(_toNumber(subtitle.end_ms) - _toNumber(subtitle.start_ms), totalDurationMs, widthPx));
        return ''
            + '<button class="timeline-block timeline-block--timed timeline-block--accent timeline-block--subtitle' + (selected ? ' is-selected' : '') + '" type="button" data-subtitle-id="' + _toId(subtitle.id) + '" style="left:' + startPx + 'px;width:' + subtitleWidth + 'px;">'
            + '<strong>' + (subtitle.text || ('字幕段 #' + (index + 1))) + '</strong>'
            + '<small>' + _timecode(subtitle.start_ms) + ' - ' + _timecode(subtitle.end_ms) + '</small>'
            + '</button>';
    }

    function _currentClipOrderIds(clips) {
        return (clips || []).map(function (clip) { return _toId(clip.id); }).filter(Boolean);
    }

    function _orderedIdsAfterTrackDrop(clips, trackType, draggedClipId, targetClipId, placeAfter) {
        var normalizedTrack = String(trackType || 'video').toLowerCase();
        var videoIds = (clips || []).filter(function (clip) {
            return String(clip.track_type || 'video').toLowerCase() !== 'audio';
        }).map(function (clip) { return _toId(clip.id); });
        var audioIds = (clips || []).filter(function (clip) {
            return String(clip.track_type || '').toLowerCase() === 'audio';
        }).map(function (clip) { return _toId(clip.id); });

        function reorder(trackIds) {
            var draggedId = _toId(draggedClipId);
            if (trackIds.indexOf(draggedId) === -1) return trackIds;
            var remaining = trackIds.filter(function (id) { return id !== draggedId; });
            var targetId = _toId(targetClipId);
            if (!targetId || remaining.indexOf(targetId) === -1) {
                remaining.push(draggedId);
                return remaining;
            }
            var insertIndex = remaining.indexOf(targetId);
            if (placeAfter) insertIndex += 1;
            remaining.splice(insertIndex, 0, draggedId);
            return remaining;
        }

        if (normalizedTrack === 'audio') {
            audioIds = reorder(audioIds);
        } else {
            videoIds = reorder(videoIds);
        }
        return videoIds.concat(audioIds);
    }

    function _handleTimelineMutation(promise, successText, stateUpdater) {
        if (!promise || typeof promise.then !== 'function') return;
        promise.then(function (result) {
            if (typeof stateUpdater === 'function') stateUpdater(result || {});
            if (typeof showToast === 'function' && successText) showToast(successText, 'success');
            _refresh();
        }).catch(function (err) {
            if (typeof showToast === 'function') showToast((err && err.message) || String(err || '时间线更新失败'), 'error');
        });
    }

    function _renderTimeline(state, selection, context) {
        var board = document.querySelector('#mainHost .js-video-timeline-board');
        if (!board) return;

        var videoClips = (context.activeClips || []).filter(function (clip) {
            return String(clip.track_type || 'video').toLowerCase() !== 'audio';
        });
        var audioClips = (context.activeClips || []).filter(function (clip) {
            return String(clip.track_type || '').toLowerCase() === 'audio';
        });
        var selectedAudioState = _audioClipState(selection.clip);
        var latestExport = context.exports && context.exports.length ? context.exports[0] : null;
        var totalDurationMs = _sequenceDurationMs(context);
        var timelineWidthPx = _timelineWidthPx(totalDurationMs);
        var timelineLabelWidth = _timelineLabelWidthPx();
        var rulerHtml = _buildRulerMarks(totalDurationMs).map(function (mark) {
            return '<span style="left:' + Math.round(mark.ratio * timelineWidthPx) + 'px;">' + mark.label + '</span>';
        }).join('');
        var playheadMs = _snapMs((_runtime.monitor.state && _runtime.monitor.state.position_ms) || 0);
        var playheadOffset = timelineLabelWidth + _timelineOffsetPx(playheadMs, totalDurationMs, timelineWidthPx);

        function laneHtml(items, emptyText, extraClass) {
            if (!items.length) {
                return '<div class="timeline-lane__canvas' + (extraClass ? (' ' + extraClass) : '') + '" style="width:' + timelineWidthPx + 'px;" data-timeline-width="' + timelineWidthPx + '" data-timeline-duration="' + totalDurationMs + '" data-seek-scope="timeline"><div class="timeline-wave timeline-wave--empty">' + emptyText + '</div></div>';
            }
            return '<div class="timeline-lane__canvas' + (extraClass ? (' ' + extraClass) : '') + '" style="width:' + timelineWidthPx + 'px;" data-timeline-width="' + timelineWidthPx + '" data-timeline-duration="' + totalDurationMs + '" data-seek-scope="timeline">' + items.join('') + '</div>';
        }

        board.innerHTML = ''
            + '<div class="timeline-toolbar">'
            + '<div class="timeline-toolbar__actions">'
            + '<button class="secondary-button js-video-toggle-playback" type="button">播放</button>'
            + '<button class="secondary-button js-video-seek-start" type="button">回到开头</button>'
            + '<button class="secondary-button js-video-step-forward" type="button">逐帧</button>'
            + '<button class="secondary-button js-video-trim-selected-clip" type="button">裁切</button>'
            + '<button class="secondary-button js-video-add-subtitle" type="button">字幕块</button>'
            + '<button class="secondary-button js-video-edit-audio" type="button">A1 音频</button>'
            + '<button class="danger-button js-video-delete-selected-clip" type="button">删除片段</button>'
            + '</div>'
            + '<div class="timeline-toolbar__meta">'
            + '<span class="timeline-toolbar__chip js-video-playhead-readout">当前 00:00 / 00:00</span>'
            + '<span class="timeline-toolbar__chip ' + (selectedAudioState ? 'timeline-toolbar__chip--focus' : '') + '">' + (selectedAudioState ? ('A1 ' + selectedAudioState.label) : 'A1 等待选择') + '</span>'
            + '<span class="timeline-toolbar__chip ' + ((context.validation && context.validation.ok) ? 'timeline-toolbar__chip--ok' : 'timeline-toolbar__chip--warn') + '">' + (latestExport ? ('最近导出 ' + _exportStatusText(latestExport.status)) : ((context.validation && context.validation.ok) ? '可发起终版导出' : '导出待校验')) + '</span>'
            + '</div>'
            + '</div>'
            + '<div class="timeline-scroll">'
            + '<div class="timeline-board-surface js-video-timeline-board-surface" data-timeline-width="' + timelineWidthPx + '" data-timeline-duration="' + totalDurationMs + '" data-timeline-label-width="' + timelineLabelWidth + '">'
            + '<div class="timeline-ruler timeline-ruler--absolute"><div class="timeline-track__label timeline-track__label--ruler">时间</div><div class="timeline-ruler__inner" style="width:' + timelineWidthPx + 'px;">' + rulerHtml + '</div></div>'
            + '<div class="timeline-playhead js-video-timeline-playhead" style="left:' + playheadOffset + 'px;"></div><div class="timeline-playhead-label js-video-timeline-playhead-label" style="left:' + playheadOffset + 'px;">' + _timecode(playheadMs) + '</div>'
            + '<div class="timeline-track"><span class="timeline-track__label">V1 主轨 <em class="timeline-track__hint">视频与图片主剪轨</em></span><div class="timeline-lane" data-drop-track="video" data-track-index="0">'
            + laneHtml(videoClips.map(function (clip) {
                return _buildTimelineClipBlock(clip, _findAssetById(_runtime.assets, clip.asset_id), _toId(clip.id) === _toId(selection.clip && selection.clip.id), totalDurationMs, timelineWidthPx);
            }), '当前视频轨还没有片段，拖拽素材到这里后再开始裁切', 'timeline-lane__canvas--video')
            + '</div></div>'
            + '<div class="timeline-track"><span class="timeline-track__label">T1 字幕 <em class="timeline-track__hint">点击字幕块可直接改文案</em></span><div class="timeline-lane" data-drop-track="subtitle" data-track-index="0">'
            + laneHtml((context.subtitles || []).map(function (subtitle, index) {
                return _buildTimelineSubtitleBlock(subtitle, index, _toId(subtitle.id) === _toId(selection.subtitle && selection.subtitle.id), totalDurationMs, timelineWidthPx);
            }), '当前还没有字幕段', 'timeline-lane__canvas--subtitle')
            + '</div></div>'
            + '<div class="timeline-track"><span class="timeline-track__label">A1 音频 <em class="timeline-track__hint">选中片段后可调音量或静音</em></span><div class="timeline-lane" data-drop-track="audio" data-track-index="0">'
            + laneHtml(audioClips.map(function (clip) {
                return _buildTimelineClipBlock(clip, _findAssetById(_runtime.assets, clip.asset_id), _toId(clip.id) === _toId(selection.clip && selection.clip.id), totalDurationMs, timelineWidthPx);
            }), '当前音频轨还没有片段，拖拽音频素材到这里后再开始编辑', 'timeline-lane__canvas--audio')
            + '</div></div>'
            + '</div></div>';

        _updatePlayheadDom();

        board.querySelectorAll('.timeline-lane__canvas[data-seek-scope="timeline"]').forEach(function (canvas) {
            canvas.addEventListener('click', function (event) {
                if (event.target && event.target.closest && event.target.closest('.timeline-block')) {
                    return;
                }
                var rect = canvas.getBoundingClientRect();
                if (!rect.width) return;
                var rawPosition = ((event.clientX - rect.left) / rect.width) * totalDurationMs;
                var snapped = _snapMs(rawPosition);
                var page = window.__videoEditorPage;
                if (page && typeof page.seekMonitor === 'function') {
                    page.seekMonitor(snapped);
                }
            });
        });

        board.querySelectorAll('.timeline-block[data-clip-id]').forEach(function (node) {
            node.addEventListener('click', function () {
                var stateValue = _state();
                var clip = _findClipById(context.activeClips, node.dataset.clipId);
                stateValue.selectedClipId = _toId(node.dataset.clipId);
                stateValue.selectedSubtitleId = null;
                stateValue.selectedAssetId = clip ? _toId(clip.asset_id) : null;
                if (clip) {
                    var asset = _findAssetById(_runtime.assets, clip.asset_id);
                    if (asset) stateValue.assetType = _normalizeAssetType(asset);
                }
                _renderPage();
                var page = window.__videoEditorPage;
                if (page && clip && typeof page.seekMonitor === 'function') {
                    page.seekMonitor(_toNumber(clip.source_in_ms));
                }
            });
            node.addEventListener('dragstart', function (event) {
                _dragPayload = {
                    kind: 'clip',
                    clipId: _toId(node.dataset.clipId),
                    trackType: String(node.dataset.trackType || 'video').toLowerCase(),
                };
                node.classList.add('is-dragging');
                if (event.dataTransfer) {
                    event.dataTransfer.effectAllowed = 'move';
                    event.dataTransfer.setData('text/plain', JSON.stringify(_dragPayload));
                }
            });
            node.addEventListener('dragend', function () {
                node.classList.remove('is-dragging');
                _dragPayload = null;
                board.querySelectorAll('.timeline-lane').forEach(function (lane) {
                    lane.classList.remove('is-drop-target');
                });
            });
        });

        board.querySelectorAll('.timeline-block[data-subtitle-id]').forEach(function (node) {
            node.addEventListener('click', function () {
                var stateValue = _state();
                stateValue.selectedSubtitleId = _toId(node.dataset.subtitleId);
                stateValue.selectedClipId = null;
                stateValue.selectedAssetId = null;
                stateValue.inspectorTab = 'subtitle';
                _renderPage();
            });
        });

        board.querySelectorAll('.timeline-lane[data-drop-track]').forEach(function (lane) {
            lane.addEventListener('dragover', function (event) {
                if (!_dragPayload) return;
                event.preventDefault();
                if (event.dataTransfer) event.dataTransfer.dropEffect = 'move';
                lane.classList.add('is-drop-target');
            });
            lane.addEventListener('dragleave', function (event) {
                if (!lane.contains(event.relatedTarget)) {
                    lane.classList.remove('is-drop-target');
                }
            });
            lane.addEventListener('drop', function (event) {
                var payload = _dragPayload;
                lane.classList.remove('is-drop-target');
                _dragPayload = null;
                if (!payload) return;
                event.preventDefault();

                var trackType = String(lane.dataset.dropTrack || 'video').toLowerCase();
                if (payload.kind === 'asset') {
                    if (trackType === 'subtitle') {
                        if (typeof showToast === 'function') showToast('字幕块请通过“新增/编辑字幕”创建，当前拖拽只支持视频轨和音频轨', 'warning');
                        return;
                    }
                    var asset = _findAssetById(_runtime.assets, payload.assetId);
                    if (!asset) return;
                    var normalizedType = _normalizeAssetType(asset);
                    if (normalizedType === 'audio' && trackType !== 'audio') {
                        if (typeof showToast === 'function') showToast('音频素材只能拖入 A1 音频轨', 'warning');
                        return;
                    }
                    if (normalizedType !== 'audio' && trackType === 'audio') {
                        if (typeof showToast === 'function') showToast('当前素材只能拖入 V1 主轨', 'warning');
                        return;
                    }
                    _handleTimelineMutation(
                        window.api.videoProjects.addAssetsToTimeline({
                            project_id: context.project ? context.project.id : null,
                            sequence_id: context.sequence ? context.sequence.id : null,
                            asset_ids: [parseInt(payload.assetId || '0', 10)],
                            track_type: trackType,
                            track_index: parseInt(lane.dataset.trackIndex || '0', 10),
                        }),
                        '素材已拖入时间轴',
                        function (result) {
                            var stateValue = _state();
                            stateValue.selectedAssetId = _toId(payload.assetId);
                            stateValue.selectedClipId = result && result.clip_ids && result.clip_ids[0] ? _toId(result.clip_ids[0]) : null;
                            stateValue.selectedSubtitleId = null;
                        }
                    );
                    return;
                }

                if (payload.kind === 'clip') {
                    if (trackType === 'subtitle') {
                        if (typeof showToast === 'function') showToast('当前只支持在视频轨或音频轨中拖拽重排片段', 'warning');
                        return;
                    }
                    if (String(payload.trackType || 'video') !== trackType) {
                        if (typeof showToast === 'function') showToast('当前只支持同轨内拖拽重排片段', 'warning');
                        return;
                    }
                    var targetNode = event.target && event.target.closest ? event.target.closest('.timeline-block[data-clip-id]') : null;
                    var placeAfter = true;
                    if (targetNode && typeof targetNode.getBoundingClientRect === 'function') {
                        var rect = targetNode.getBoundingClientRect();
                        placeAfter = event.clientX > (rect.left + rect.width / 2);
                    }
                    var orderedIds = _orderedIdsAfterTrackDrop(
                        context.activeClips,
                        trackType,
                        payload.clipId,
                        targetNode ? targetNode.dataset.clipId : null,
                        placeAfter
                    );
                    if (!orderedIds.length || orderedIds.join(',') === _currentClipOrderIds(context.activeClips).join(',')) {
                        return;
                    }
                    _handleTimelineMutation(
                        window.api.videoProjects.reorderVideoClips({
                            project_id: context.project ? context.project.id : null,
                            sequence_id: context.sequence ? context.sequence.id : null,
                            clip_ids: orderedIds.map(function (id) { return parseInt(id || '0', 10); }).filter(Boolean),
                        }),
                        '时间轴顺序已更新',
                        function () {
                            var stateValue = _state();
                            stateValue.selectedClipId = _toId(payload.clipId);
                            stateValue.selectedSubtitleId = null;
                        }
                    );
                }
            });
        });
    }

    function _renderGrid(state, context, selection) {
        var grid = document.querySelector('#mainHost .source-thumb-grid');
        if (!grid) return;
        var filtered = selection.filteredAssets;
        var asset = selection.asset;

        if (!filtered.length) {
            var emptyTitle = _runtime.assets.length ? '当前筛选没有素材' : '当前素材库还是空的';
            var emptyCopy = _runtime.assets.length ? '可以切换类型筛选，或继续导入其它素材。' : '先从素材中心批量导入，或直接导入其它素材到当前序列。';
            grid.innerHTML = '<div class="empty-state" style="padding:24px;text-align:center;grid-column:1/-1;"><p>' + emptyTitle + '</p><p class="subtle">' + emptyCopy + '</p></div>';
            return;
        }

        grid.innerHTML = filtered.slice(0, 24).map(function (item) {
            var normalizedType = _normalizeAssetType(item);
            return window._editorShared.buildAssetThumb({
                id: item.id,
                asset_type: normalizedType === 'subtitle' ? 'text' : normalizedType,
                filename: item.filename,
                file_size: item.file_size,
                tags: item.tags,
                file_path: item.file_path,
                poster_path: item.poster_path,
                created_at: item.created_at,
            }, _toId(item.id) === _toId(state.selectedAssetId), { compact: true });
        }).join('');

        if (window._editorShared && typeof window._editorShared.hydrateRuntimePreviews === 'function') {
            window._editorShared.hydrateRuntimePreviews(grid);
        }

        grid.querySelectorAll('.source-thumb').forEach(function (thumb) {
            if (thumb.dataset.videoGridBound === '1') return;
            thumb.dataset.videoGridBound = '1';
            thumb.addEventListener('click', function () {
                state.selectedAssetId = _toId(thumb.dataset.assetId);
                state.selectedClipId = null;
                state.selectedSubtitleId = null;
                _renderPage();
            });
            thumb.setAttribute('draggable', 'true');
            thumb.addEventListener('dragstart', function (event) {
                _dragPayload = {
                    kind: 'asset',
                    assetId: _toId(thumb.dataset.assetId),
                };
                thumb.classList.add('is-dragging');
                if (event.dataTransfer) {
                    event.dataTransfer.effectAllowed = 'copyMove';
                    event.dataTransfer.setData('text/plain', JSON.stringify(_dragPayload));
                }
            });
            thumb.addEventListener('dragend', function () {
                thumb.classList.remove('is-dragging');
                _dragPayload = null;
                document.querySelectorAll('#mainHost .timeline-lane').forEach(function (lane) {
                    lane.classList.remove('is-drop-target');
                });
            });
        });

    }

    function _renderPage() {
        var state = _state();
        var context = _resolveContext(_runtime.projects, state);
        _runtime.assets = context.sequenceAssets || [];
        _runtime.counts = _countAssets(_runtime.assets);
        var selection = _resolveSelection(state, context);
        _renderTabs(state, _runtime.counts);
        _renderHeader(context, _runtime.counts, selection);
        _renderGrid(state, context, selection);
        _renderMonitor(selection, context);
        _renderTimeline(state, selection, context);
        _renderInspector(state, selection, context, _runtime.counts);
        _applyRuntimeSummary(context, _runtime.counts);
    }

    function _loadProjects() {
        if (!window.api || !window.api.videoProjects || typeof window.api.videoProjects.listVideoProjects !== 'function') {
            return Promise.resolve([]);
        }
        return window.api.videoProjects.listVideoProjects().then(function (projects) {
            _runtime.projects = projects || [];
            return _runtime.projects;
        });
    }

    function _refresh(options) {
        options = options || {};
        _stopMonitorPolling();
        return _loadProjects().then(function () {
            if (options.resetMonitor) {
                _runtime.monitor.selectionKey = '';
                _updateMonitorState(_emptyMonitorState());
            }
            _renderPage();
            return _runtime.projects;
        });
    }

    function _cycleSequence() {
        var state = _state();
        var entries = _sequenceEntries(_runtime.projects);
        if (!entries.length) {
            if (typeof showToast === 'function') showToast('当前还没有可切换的剪辑序列', 'warning');
            return;
        }
        var currentId = _toId(state.sequenceId);
        var index = entries.findIndex(function (entry) {
            return entry.sequenceId === currentId;
        });
        var next = entries[(index + 1 + entries.length) % entries.length];
        state.projectId = next.projectId;
        state.sequenceId = next.sequenceId;
        state.selectedAssetId = null;
        state.selectedClipId = null;
        state.selectedSubtitleId = null;
        _renderPage();
        if (typeof showToast === 'function') showToast('已切换到 ' + next.sequenceName, 'success');
    }

    function _registerPageApi() {
        window.__videoEditorPage = {
            refresh: _refresh,
            setAssetType: function (type) {
                var state = _state();
                state.assetType = type || 'video';
                state.selectedAssetId = null;
                state.selectedClipId = null;
                state.selectedSubtitleId = null;
                _renderPage();
            },
            setInspectorTab: function (tabKey) {
                var state = _state();
                state.inspectorTab = tabKey || 'properties';
                _renderPage();
            },
            setSelectedClip: function (clipId) {
                var state = _state();
                state.selectedClipId = _toId(clipId);
                state.selectedSubtitleId = null;
                _renderPage();
            },
            setSelectedSubtitle: function (subtitleId) {
                var state = _state();
                state.selectedSubtitleId = _toId(subtitleId);
                state.selectedClipId = null;
                _renderPage();
            },
            getSelectedAsset: function () {
                return _resolveSelection(_state(), _resolveContext(_runtime.projects, _state())).asset;
            },
            getSelectedClip: function () {
                return _resolveSelection(_state(), _resolveContext(_runtime.projects, _state())).clip;
            },
            getSelectedSubtitle: function () {
                return _resolveSelection(_state(), _resolveContext(_runtime.projects, _state())).subtitle;
            },
            getContext: function () {
                var context = _resolveContext(_runtime.projects, _state());
                return {
                    projectId: context.project ? context.project.id : null,
                    sequenceId: context.sequence ? context.sequence.id : null,
                };
            },
            toggleMonitorPlayback: function () {
                var api = _monitorApi();
                if (!api) return Promise.resolve(_runtime.monitor.state);
                var action = _runtime.monitor.state && _runtime.monitor.state.playing ? api.pauseVideoMonitor : api.playVideoMonitor;
                if (typeof action !== 'function') return Promise.resolve(_runtime.monitor.state);
                return action().then(function (state) {
                    _updateMonitorState(state);
                    _applyMonitorDom(_resolveSelection(_state(), _resolveContext(_runtime.projects, _state())), _resolveContext(_runtime.projects, _state()), _resolveSelection(_state(), _resolveContext(_runtime.projects, _state())).asset);
                    _updatePlayheadDom();
                    return _runtime.monitor.state;
                });
            },
            seekMonitor: function (positionMs) {
                var api = _monitorApi();
                if (!api || typeof api.seekVideoMonitor !== 'function') return Promise.resolve(_runtime.monitor.state);
                return api.seekVideoMonitor(_snapMs(positionMs)).then(function (state) {
                    _updateMonitorState(state);
                    _updatePlayheadDom();
                    _applyMonitorDom(_resolveSelection(_state(), _resolveContext(_runtime.projects, _state())), _resolveContext(_runtime.projects, _state()), _resolveSelection(_state(), _resolveContext(_runtime.projects, _state())).asset);
                    return _runtime.monitor.state;
                });
            },
            seekMonitorStart: function () {
                return this.seekMonitor(0);
            },
            stepMonitorForward: function () {
                var api = _monitorApi();
                if (!api || typeof api.stepVideoMonitor !== 'function') return Promise.resolve(_runtime.monitor.state);
                return api.stepVideoMonitor(40).then(function (state) {
                    _updateMonitorState(state);
                    _updatePlayheadDom();
                    _applyMonitorDom(_resolveSelection(_state(), _resolveContext(_runtime.projects, _state())), _resolveContext(_runtime.projects, _state()), _resolveSelection(_state(), _resolveContext(_runtime.projects, _state())).asset);
                    return _runtime.monitor.state;
                });
            },
            deleteSelectedClip: function () {
                var clip = _resolveSelection(_state(), _resolveContext(_runtime.projects, _state())).clip;
                var api = _monitorApi();
                if (!clip || !api || typeof api.deleteVideoClip !== 'function') {
                    return Promise.reject(new Error('当前没有可删除的时间线片段'));
                }
                return api.deleteVideoClip({ clip_id: clip.id }).then(function (result) {
                    var state = _state();
                    state.selectedClipId = null;
                    _runtime.monitor.selectionKey = '';
                    _stopMonitorPolling();
                    _updateMonitorState(_emptyMonitorState());
                    return _refresh({ resetMonitor: true }).then(function () {
                        return result;
                    });
                });
            },
            getLibraryAssetIds: function () {
                return (_runtime.assets || []).map(function (asset) { return _toId(asset.id); }).filter(Boolean);
            },
            cycleSequence: _cycleSequence,
        };
    }

    window._pageLoaders['video-editor'] = function () {
        _stopMonitorPolling();
        Promise.all([
            _loadProjects().catch(function () { return []; }),
        ]).then(function () {
            _runtime.assets = [];

            _registerPageApi();
            _renderPage();

            if (typeof _applyAiHandoffHint === 'function') {
                _applyAiHandoffHint('video-editor', '#detailHost .js-video-inspector-content');
            }


                runtimeSummaryHandlers['video-editor'] = function (payload) {
                    payload = payload || {};
                    var project = payload.project || null;
                    var sequence = payload.sequence || null;
                    var exports = payload.exports || [];
                    var clips = payload.clips || [];
                    var subtitles = payload.subtitles || [];
                    var counts = payload.counts || { video: 0, image: 0, subtitle: 0, audio: 0 };
                    var validation = payload.validation || { ok: false, errors: [] };
                    var totalAssets = (counts.video || 0) + (counts.image || 0) + (counts.subtitle || 0) + (counts.audio || 0);
                    var latestExport = exports.length ? exports[0] : null;
                    var errors = validation.errors || [];
                    var exportLabel = latestExport ? ('最近导出 ' + _exportStatusText(latestExport.status)) : (validation.ok ? '可发起终版导出' : ('待处理 ' + errors.length + ' 项'));

                    if (typeof window.setShellRouteSummary === 'function') {
                        window.setShellRouteSummary({
                            eyebrow: '剪辑提醒',
                            title: project ? ((project.name || '当前工程') + (validation.ok ? ' 已通过导出校验' : ' 仍有待处理项')) : '视频工程摘要',
                            copy: project
                                ? ((sequence ? (sequence.name || '主序列') : '主序列') + ' / 素材池 ' + totalAssets + ' 条 / 时间线 ' + clips.length + ' 段 / 字幕 ' + subtitles.length + ' 条')
                                : '等待工程数据加载后同步摘要。',
                            statusLeft: [
                                '素材池 ' + totalAssets + ' 条',
                                '时间线 ' + clips.length + ' 段',
                                '字幕 ' + subtitles.length + ' 条',
                            ],
                            statusRight: [
                                { text: validation.ok ? '导出校验通过' : (errors[0] || '导出待校验'), tone: validation.ok ? 'success' : 'warning' },
                                { text: exportLabel, tone: latestExport ? _exportStatusTone(latestExport.status) : (validation.ok ? 'info' : 'warning') },
                            ],
                        });
                    }
                };
            // 运行时摘要
            if (window._pageAudits && window._pageAudits['video-editor']) {
                window._pageAudits['video-editor']({ assets: _runtime.assets, projects: _runtime.projects });
            }

            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (e) {
            console.warn('[page-loaders] video-editor load failed:', e);
        });
    };

    // appendAssetsToSequence / addAssetsToTimeline / reorderVideoClips / trimVideoClip / createVideoExport / subtitle CRUD 由后端 Bridge 提供

}());
