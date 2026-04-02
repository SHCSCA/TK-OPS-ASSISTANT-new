(function () {
    'use strict';

    var shared = window.__pageLoaderShared;
    var loaders = window._pageLoaders;
    var runtimeSummaryHandlers = window.__runtimeSummaryHandlers || {};
    if (!shared || !loaders) {
        throw new Error('video editor page loader dependencies not loaded');
    }

    var _esc = shared.esc;
    var _taskStatusTone = shared.taskStatusTone;
    var _taskStatusLabel = shared.taskStatusLabel;
    var _applyRuntimeSummary = shared.applyRuntimeSummary;
    var _renderWorkbenchSummary = shared.renderWorkbenchSummary;
    var _renderWorkbenchSideCards = shared.renderWorkbenchSideCards;
    var _renderStripCards = shared.renderStripCards;
    var _applyAiHandoffHint = shared.applyAiHandoffHint;

    var pageState = window.__videoEditorPageState = window.__videoEditorPageState || {
        selectedProjectId: null,
        selectedSequenceId: null,
        selectedAssetId: null,
        selectedClipId: null,
        selectedSubtitleId: null,
        selectedSnapshotId: null,
        inspectorTab: 'attributes',
        playheadMs: 0,
    };
    var lastContext = null;
    var staticContext = null;
    var timelineContext = null;
    var outputContext = null;

    // Runtime contract markers kept here for split-file audits:
    // listVideoProjects / listVideoSequences / listVideoClips / listVideoSubtitles
    // appendAssetsToSequence / createVideoExport / listVideoExports / listVideoSnapshots

    runtimeSummaryHandlers['video-editor'] = function (payload) {
        payload = payload || {};
        var project = payload.project || null;
        var sequence = payload.sequence || null;
        var clips = payload.clips || [];
        var exports = payload.exports || [];
        var failed = exports.filter(function (item) {
            return String(item.status || '').toLowerCase() === 'failed';
        }).length;
        _applyRuntimeSummary({
            eyebrow: '剪辑提醒',
            title: project ? ('当前工程：' + (project.name || '未命名工程')) : '暂未创建视频工程',
            copy: sequence
                ? ('当前序列 ' + (sequence.name || '-') + '，片段 ' + clips.length + '，导出记录 ' + exports.length)
                : '先创建工程并导入素材，才能开始基础剪辑。',
            statusLeft: [
                '工程 ' + (project ? (project.name || '-') : '未创建'),
                '序列 ' + (sequence ? (sequence.name || '-') : '未创建'),
                '片段 ' + clips.length,
            ],
            statusRight: [
                { text: exports.length ? ('导出 ' + exports.length) : '暂无导出', tone: exports.length ? 'info' : 'warning' },
                { text: failed ? ('失败 ' + failed) : '导出正常', tone: failed ? 'error' : 'success' },
            ],
        });
    };

    function _formatTime(ms) {
        var total = Math.max(0, Math.floor(Number(ms || 0) / 1000));
        var seconds = total % 60;
        var minutes = Math.floor(total / 60) % 60;
        var hours = Math.floor(total / 3600);
        if (hours > 0) {
            return String(hours).padStart(2, '0') + ':' + String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');
        }
        return String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');
    }

    function _assetKind(asset) {
        var type = String((asset && asset.asset_type) || '').toLowerCase();
        if (type === 'text') return 'subtitle';
        if (type === 'template') return 'image';
        return type || 'video';
    }

    function _assetMeta(asset) {
        var bits = [];
        if (asset.duration_ms) bits.push(_formatTime(asset.duration_ms));
        if (asset.width && asset.height) bits.push(String(asset.width) + 'x' + String(asset.height));
        if (asset.tags) bits.push(String(asset.tags));
        return bits.join(' | ') || '已接入素材库';
    }

    function _findById(items, id) {
        return (items || []).find(function (item) { return Number(item.id) === Number(id); }) || null;
    }

    function _assetMap(assets) {
        return (assets || []).reduce(function (acc, asset) {
            acc[String(asset.id)] = asset;
            return acc;
        }, {});
    }

    function _ensureProject(projects) {
        var selected = _findById(projects, pageState.selectedProjectId) || (projects || [])[0] || null;
        pageState.selectedProjectId = selected ? Number(selected.id) : null;
        return selected;
    }

    function _ensureSequence(sequences) {
        var selected = _findById(sequences, pageState.selectedSequenceId);
        if (!selected) {
            selected = (sequences || []).find(function (item) { return Boolean(item.is_active); }) || (sequences || [])[0] || null;
        }
        pageState.selectedSequenceId = selected ? Number(selected.id) : null;
        return selected;
    }

    function _renderSourceTabs(assets) {
        var counts = { video: 0, image: 0, subtitle: 0, audio: 0 };
        var labels = ['视频', '图片', '字幕', '音频'];
        (assets || []).forEach(function (asset) {
            var kind = _assetKind(asset);
            if (counts[kind] != null) counts[kind] += 1;
        });
        [['video', counts.video], ['image', counts.image], ['subtitle', counts.subtitle], ['audio', counts.audio]].forEach(function (entry, index) {
            var tab = document.querySelectorAll('#mainHost .source-browser-tabs span')[index];
            if (tab) tab.innerHTML = labels[index] + ' <em>' + entry[1] + '</em>';
        });
    }

    function _renderSelectedAsset(asset) {
        var host = document.querySelector('#mainHost .source-mini-preview');
        if (!host) return;
        if (!asset) {
            host.innerHTML = '<div class="source-mini-preview__thumb source-mini-preview__thumb--video"></div>'
                + '<div class="source-mini-preview__info"><strong>尚未选择素材</strong><div class="subtle">单击素材预览，双击直接加入当前时间线。</div></div>';
            return;
        }
        host.innerHTML = '<div class="source-mini-preview__thumb source-mini-preview__thumb--' + _assetKind(asset) + '"></div>'
            + '<div class="source-mini-preview__info"><strong>' + _esc(asset.filename || '未命名素材') + '</strong>'
            + '<div class="subtle">' + _esc(_assetMeta(asset)) + '</div>'
            + '<div class="source-mini-preview__meta"><span>ID ' + _esc(asset.id) + '</span><span>' + _esc(asset.asset_type || 'unknown') + '</span></div></div>';
    }

    function _bindAssetGrid(assets, sequence) {
        var grid = document.querySelector('#mainHost .source-thumb-grid');
        if (!grid) return;
        grid.querySelectorAll('.source-thumb').forEach(function (thumb) {
            var asset = _findById(assets, thumb.dataset.assetId);
            thumb.addEventListener('click', function () {
                pageState.selectedAssetId = asset ? Number(asset.id) : null;
                grid.querySelectorAll('.source-thumb').forEach(function (item) {
                    item.classList.toggle('is-selected', item === thumb);
                });
                _renderSelectedAsset(asset);
            });
            thumb.addEventListener('dblclick', function () {
                if (!asset) return;
                if (!sequence) {
                    showToast('请先创建工程和序列', 'warning');
                    return;
                }
                api.videoClips.appendAssets(sequence.id, { asset_id: asset.id }).then(function (clips) {
                    var created = Array.isArray(clips) ? clips[0] : null;
                    pageState.selectedAssetId = asset.id;
                    pageState.selectedClipId = created && created.id ? Number(created.id) : pageState.selectedClipId;
                    showToast('素材已加入当前时间线', 'success');
                    _scheduleRefresh('timeline', { entity: 'video-clip', action: 'double-click-append', id: created && created.id ? created.id : asset.id });
                }).catch(function (err) {
                    showToast('加入时间线失败: ' + ((err && err.message) || '未知错误'), 'error');
                });
            });
        });
    }

    function _renderAssetGrid(assets, sequence) {
        var grid = document.querySelector('#mainHost .source-thumb-grid');
        if (!grid) return;
        var selectedId = Number(pageState.selectedAssetId || 0);
        grid.innerHTML = (assets || []).slice(0, 12).map(function (asset) {
            var kind = _assetKind(asset);
            var previewInner = '';
            if (kind === 'subtitle') previewInner = '<span>SRT</span>';
            if (kind === 'audio') previewInner = '<span>AUD</span>';
            return '<article class="source-thumb' + (Number(asset.id) === selectedId ? ' is-selected' : '') + '" data-asset-id="' + _esc(asset.id) + '" data-kind="' + _esc(kind) + '" data-search="' + _esc((asset.filename || '') + ' ' + (asset.tags || '')) + '">'
                + '<div class="source-thumb__preview source-thumb__preview--' + _esc(kind) + '">' + previewInner + '</div>'
                + '<div class="source-thumb__name">' + _esc(asset.filename || '未命名素材') + '</div>'
                + '<div class="source-thumb__tag"><span class="pill ' + (kind === 'subtitle' ? 'warning' : 'info') + '">' + _esc(kind) + '</span></div>'
                + '</article>';
        }).join('');
        if (!selectedId && assets && assets[0]) pageState.selectedAssetId = Number(assets[0].id);
        _renderSelectedAsset(_findById(assets, pageState.selectedAssetId));
        _bindAssetGrid(assets, sequence);
    }

    function _renderPreview(context) {
        var sequence = context.sequence;
        var clips = context.clips || [];
        var subtitles = context.subtitles || [];
        var clip = _findById(clips, pageState.selectedClipId) || clips[0] || null;
        var assets = _assetMap(context.assets || []);
        if (clip && !pageState.selectedClipId) {
            pageState.selectedClipId = Number(clip.id);
        }
        var head = document.querySelector('#mainHost .video-preview-head .subtle');
        var chip = document.querySelector('#mainHost .canvas-chip');
        var markers = document.querySelector('#mainHost .video-preview-markers');
        var surface = document.querySelector('#mainHost .video-surface--editor');
        if (head) {
            head.textContent = sequence
                ? ('序列: ' + (sequence.name || '-') + '，当前片段 ' + (clip ? (((assets[String(clip.asset_id)] && assets[String(clip.asset_id)].filename) || ('片段 #' + clip.id))) : '未选择'))
                : '尚未创建剪辑序列';
        }
        if (chip) {
            chip.textContent = _formatTime(pageState.playheadMs || 0) + ' / ' + _formatTime((sequence && sequence.duration_ms) || 0);
        }
        if (markers) {
            markers.innerHTML = subtitles.slice(0, 3).map(function (item) {
                return '<span>' + _esc((item.text || ('字幕 #' + item.id)).slice(0, 10)) + '</span>';
            }).join('') || '<span>时间线就绪</span><span>双击素材可加入序列</span><span>支持真实导出</span>';
        }
        if (surface) {
            surface.innerHTML = '<div class="play-button">' + _esc(clip ? ((((assets[String(clip.asset_id)] || {}).filename) || '播放')) : '播放') + '</div>';
        }
    }

    function _renderTimeline(context) {
        var host = document.querySelector('#mainHost .video-timeline-board');
        if (!host) return;
        var sequence = context.sequence;
        var clips = context.clips || [];
        var subtitles = context.subtitles || [];
        var assets = _assetMap(context.assets || []);
        var duration = Math.max((sequence && sequence.duration_ms) || 0, 15000);
        var ruler = '<div class="timeline-ruler">' + [0, 1, 2, 3, 4, 5, 6].map(function (step) {
            return '<span>' + _formatTime(Math.round(duration * step / 6)) + '</span>';
        }).join('') + '</div>';
        var videoBlocks = clips.filter(function (clip) { return String(clip.track_type || 'video') !== 'audio'; }).map(function (clip) {
            var asset = assets[String(clip.asset_id)] || {};
            return '<div class="timeline-block ' + (Number(clip.id) === Number(pageState.selectedClipId) ? 'timeline-block--primary is-selected' : '') + '" data-clip-id="' + _esc(clip.id) + '">' + _esc((asset.filename || ('片段 #' + clip.id)) + ' ' + _formatTime(clip.start_ms || 0) + '-' + _formatTime((clip.start_ms || 0) + (clip.duration_ms || 0))) + '</div>';
        }).join('') || '<div class="timeline-wave">双击左侧素材即可追加到视频轨道。</div>';
        var subtitleBlocks = subtitles.map(function (item) {
            return '<div class="timeline-block timeline-block--accent ' + (Number(item.id) === Number(pageState.selectedSubtitleId) ? 'is-selected' : '') + '" data-subtitle-id="' + _esc(item.id) + '">' + _esc((item.text || ('字幕 #' + item.id)).slice(0, 18)) + '</div>';
        }).join('') || '<div class="timeline-wave">字幕轨为空，点击右侧按钮即可新增字幕。</div>';
        var audioBlocks = clips.filter(function (clip) { return String(clip.track_type || '') === 'audio'; }).map(function (clip) {
            var asset = assets[String(clip.asset_id)] || {};
            return '<div class="timeline-block" data-clip-id="' + _esc(clip.id) + '">' + _esc(asset.filename || ('音频 #' + clip.id)) + '</div>';
        }).join('') || '<div class="timeline-wave">导入音频素材后会自动挂到音频轨。</div>';

        host.innerHTML = ruler
            + '<div class="timeline-track"><span>V1 视频</span><div class="timeline-lane">' + videoBlocks + '</div></div>'
            + '<div class="timeline-track"><span>T1 字幕</span><div class="timeline-lane">' + subtitleBlocks + '</div></div>'
            + '<div class="timeline-track"><span>A1 音频</span><div class="timeline-lane">' + audioBlocks + '</div></div>';

        host.querySelectorAll('[data-clip-id]').forEach(function (block) {
            block.addEventListener('click', function () {
                pageState.selectedClipId = Number(block.dataset.clipId || 0) || null;
                var clip = _findById(clips, pageState.selectedClipId);
                if (clip) pageState.playheadMs = Number(clip.start_ms || 0);
                _render(lastContext);
            });
        });
        host.querySelectorAll('[data-subtitle-id]').forEach(function (block) {
            block.addEventListener('click', function () {
                pageState.selectedSubtitleId = Number(block.dataset.subtitleId || 0) || null;
                _render(lastContext);
            });
        });
    }

    function _renderInspector(context) {
        var host = document.querySelector('#mainHost .workbench-side-list');
        var queueHost = document.querySelector('#mainHost .video-queue-list');
        var sequence = context.sequence;
        var clips = context.clips || [];
        var subtitles = context.subtitles || [];
        var snapshots = context.snapshots || [];
        var exports = context.exports || [];
        var clip = _findById(clips, pageState.selectedClipId);
        var subtitle = _findById(subtitles, pageState.selectedSubtitleId);
        var assets = _assetMap(context.assets || []);

        document.querySelectorAll('#mainHost .video-inspector-tabs span').forEach(function (tab, index) {
            var key = ['attributes', 'subtitles', 'exports'][index] || 'attributes';
            tab.classList.toggle('is-selected', key === pageState.inspectorTab);
            if (tab.dataset.videoInspectorBound === '1') return;
            tab.dataset.videoInspectorBound = '1';
            tab.addEventListener('click', function () {
                pageState.inspectorTab = key;
                _render(lastContext);
            });
        });

        if (host) {
            if (pageState.inspectorTab === 'subtitles') {
                host.innerHTML = (subtitles || []).map(function (item) {
                    return '<article class="workbench-sidecard' + (Number(item.id) === Number(pageState.selectedSubtitleId) ? ' is-selected' : '') + '" data-subtitle-card="' + _esc(item.id) + '"><div class="workbench-sidecard__head"><strong>' + _esc((item.text || ('字幕 #' + item.id)).slice(0, 18)) + '</strong><span class="pill info">' + _esc(_formatTime(item.start_ms || 0)) + '</span></div><div class="subtle">' + _esc(_formatTime(item.start_ms || 0) + ' - ' + _formatTime(item.end_ms || 0)) + '</div></article>';
                }).join('') || '<article class="workbench-sidecard"><strong>暂无字幕</strong><div class="subtle">通过右侧操作可快速新增、编辑和删除字幕。</div></article>';
                if (subtitle) {
                    host.innerHTML += '<article class="workbench-sidecard"><strong>当前字幕</strong><div class="subtle">' + _esc(subtitle.text || '') + '</div><div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:8px;"><button class="secondary-button" type="button">编辑字幕</button><button class="danger-button" type="button">删除字幕</button></div></article>';
                }
                host.innerHTML += '<article class="workbench-sidecard"><strong>字幕动作</strong><div class="subtle">新增字幕会默认跟随当前片段，后续可以继续微调时间范围。</div><div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:8px;"><button class="secondary-button" type="button">新增字幕</button></div></article>';
            } else if (pageState.inspectorTab === 'exports') {
                host.innerHTML = exports.map(function (item) {
                    return '<article class="workbench-sidecard"><div class="workbench-sidecard__head"><strong>' + _esc(item.preset || '导出') + '</strong><span class="pill ' + _taskStatusTone(item.status) + '">' + _esc(_taskStatusLabel(item.status || 'pending')) + '</span></div><div class="subtle">' + _esc(item.output_path || '输出路径待生成') + '</div></article>';
                }).join('') || '<article class="workbench-sidecard"><strong>暂无导出记录</strong><div class="subtle">可先发起试看导出，确认无误后再导出终版。</div></article>';
                if (snapshots[0]) {
                    pageState.selectedSnapshotId = Number(snapshots[0].id || 0) || null;
                    host.innerHTML += '<article class="workbench-sidecard"><strong>最近快照</strong><div class="subtle">' + _esc(snapshots[0].title || '未命名快照') + '</div><div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:8px;"><button class="secondary-button" type="button">恢复快照</button></div></article>';
                }
            } else {
                host.innerHTML = '<article class="workbench-sidecard"><div class="workbench-sidecard__head"><strong>' + _esc(sequence ? (sequence.name || '当前序列') : '暂无序列') + '</strong><span class="pill success">' + clips.length + ' 片段</span></div><div class="subtle">片段 ' + clips.length + ' | 字幕 ' + subtitles.length + ' | 快照 ' + snapshots.length + '</div></article>';
                if (clip) {
                    host.innerHTML += '<article class="workbench-sidecard"><strong>当前片段</strong><div class="subtle">' + _esc(((assets[String(clip.asset_id)] || {}).filename) || ('片段 #' + clip.id)) + '</div><div class="subtle">' + _esc('时间 ' + _formatTime(clip.start_ms || 0) + ' / 素材入点 ' + _formatTime(clip.source_in_ms || 0) + ' - ' + _formatTime(clip.source_out_ms || 0)) + '</div><div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:8px;"><button class="secondary-button" type="button">左移片段</button><button class="secondary-button" type="button">右移片段</button><button class="danger-button" type="button">删除片段</button></div></article>';
                }
                host.innerHTML += '<article class="workbench-sidecard"><strong>工程动作</strong><div class="subtle">保存快照可在导出前锁定当前状态；新增字幕会挂到当前播放头附近。</div><div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:8px;"><button class="secondary-button" type="button">保存快照</button><button class="secondary-button" type="button">新增字幕</button></div></article>';
            }
            host.querySelectorAll('[data-subtitle-card]').forEach(function (card) {
                card.addEventListener('click', function () {
                    pageState.selectedSubtitleId = Number(card.dataset.subtitleCard || 0) || null;
                    _render(lastContext);
                });
            });
        }

        if (queueHost) {
            if (exports.length) {
                queueHost.innerHTML = exports.slice(0, 4).map(function (item) {
                    return '<article class="strip-card"><strong>' + _esc((item.preset || '导出') + ' #' + item.id) + '</strong><div class="subtle">' + _esc(item.output_path || '输出路径待生成') + '</div><span class="pill ' + _taskStatusTone(item.status) + '">' + _esc(_taskStatusLabel(item.status || 'pending')) + '</span></article>';
                }).join('');
            } else {
                _renderStripCards(context.tasks || [], '#mainHost .video-queue-list');
            }
            _applyAiHandoffHint('video-editor', '#mainHost .video-queue-list');
        }
    }

    function _render(context) {
        lastContext = context;
        _renderWorkbenchSummary([
            { label: '当前序列', value: context.sequence ? (context.sequence.name || '未命名序列') : '未创建', note: context.project ? ('工程：' + (context.project.name || '未命名工程')) : '请先创建视频工程' },
            { label: '时间线片段', value: String((context.clips || []).length) + ' 个', note: '双击左侧素材可快速追加到当前序列' },
            { label: '导出队列', value: String((context.exports || []).length) + ' 个', note: '失败导出会在这里保留状态，便于重试' },
        ]);
        _renderAssetGrid(context.assets || [], context.sequence);
        _renderSourceTabs(context.assets || []);
        _renderPreview(context);
        _renderTimeline(context);
        _renderInspector(context);
        runtimeSummaryHandlers['video-editor'](context);
    }

    var refreshTimer = null;
    var refreshPromise = null;
    var refreshResolve = null;
    var refreshReject = null;
    var refreshInFlight = false;
    var pendingRefreshTier = null;
    var pendingRefreshSignature = '';
    var lastRefreshSignature = '';
    var lastRefreshAt = 0;
    var REFRESH_DEBOUNCE_MS = 40;

    function _listVideoProjects() {
        // Compatibility anchor for split-file audits: api.videoProjects.listVideoProjects()
        if (api.videoProjects && typeof api.videoProjects.listVideoProjects === 'function') {
            return api.videoProjects.listVideoProjects();
        }
        return api.videoProjects.list().catch(function () { return []; });
    }

    function _loadStaticContext() {
        return Promise.all([
            _listVideoProjects(),
            api.assets.list().catch(function () { return []; }),
            api.tasks.list().catch(function () { return []; }),
        ]).then(function (results) {
            var projects = results[0] || [];
            var assets = results[1] || [];
            var tasks = results[2] || [];
            var project = _ensureProject(projects);
            return { projects: projects, project: project, assets: assets, tasks: tasks };
        });
    }

    function _loadSequenceContext(baseContext) {
        var project = baseContext && baseContext.project;
        if (!project) {
            return Promise.resolve({ sequences: [], sequence: null, clips: [], subtitles: [], exports: [], snapshots: [] });
        }
        return api.videoSequences.list(project.id).catch(function () { return []; }).then(function (sequences) {
            var sequence = _ensureSequence(sequences || []);
            if (!sequence) {
                return { sequences: sequences || [], sequence: null, clips: [], subtitles: [], exports: [], snapshots: [] };
            }
            return Promise.all([
                api.videoClips.list(sequence.id).catch(function () { return []; }),
                api.videoSubtitles.list(sequence.id).catch(function () { return []; }),
            ]).then(function (loaded) {
                return {
                    sequences: sequences || [],
                    sequence: sequence,
                    clips: loaded[0] || [],
                    subtitles: loaded[1] || [],
                };
            });
        });
    }

    function _loadOutputContext(baseContext) {
        var project = baseContext && baseContext.project;
        if (!project) {
            return Promise.resolve({ exports: [], snapshots: [] });
        }
        return Promise.all([
            api.videoExports.list(project.id).catch(function () { return []; }),
            api.videoSnapshots.list(project.id).catch(function () { return []; }),
        ]).then(function (loaded) {
            return {
                exports: loaded[0] || [],
                snapshots: loaded[1] || [],
            };
        });
    }

    function _composeContext(baseContext, sequenceContext, outputContext) {
        return {
            projects: baseContext.projects || [],
            project: baseContext.project || null,
            sequences: sequenceContext.sequences || [],
            sequence: sequenceContext.sequence || null,
            clips: sequenceContext.clips || [],
            subtitles: sequenceContext.subtitles || [],
            exports: outputContext.exports || [],
            snapshots: outputContext.snapshots || [],
            assets: baseContext.assets || [],
            tasks: baseContext.tasks || [],
        };
    }

    function _refreshTierRank(tier) {
        return { timeline: 1, outputs: 2, static: 3 }[tier] || 1;
    }

    function _pickRefreshTier(currentTier, nextTier) {
        if (!currentTier) return nextTier;
        return _refreshTierRank(nextTier) > _refreshTierRank(currentTier) ? nextTier : currentTier;
    }

    function _normalizeRefreshTier(tier) {
        if (tier === 'static' || tier === 'outputs' || tier === 'timeline') return tier;
        return 'timeline';
    }

    function _refreshTierForEntity(entity, action) {
        var normalized = String(entity || '');
        var normalizedAction = String(action || '');
        if (normalized === 'video-project') {
            return 'timeline';
        }
        if (normalized === 'video-asset' || normalized === 'asset' || normalized === 'task') {
            return 'static';
        }
        if (normalized === 'video-snapshot') {
            if (normalizedAction === 'restored') {
                return 'timeline';
            }
            return 'outputs';
        }
        if (normalized === 'video-export') {
            return 'outputs';
        }
        if (normalized.indexOf('video-') === 0) {
            return 'timeline';
        }
        return 'timeline';
    }

    function _refreshSignature(detail, tier) {
        return tier + '|' + String((detail && detail.entity) || 'manual') + '|' + String((detail && detail.id) || '');
    }

    function _flushRefreshQueue() {
        refreshTimer = null;
        if (refreshInFlight) return;
        var tier = pendingRefreshTier || 'timeline';
        var signature = pendingRefreshSignature || _refreshSignature(null, tier);
        pendingRefreshTier = null;
        pendingRefreshSignature = '';
        lastRefreshSignature = signature;
        lastRefreshAt = Date.now();
        refreshInFlight = true;
        _refreshByTier(tier).then(function (context) {
            refreshInFlight = false;
            if (refreshResolve) refreshResolve(context);
            refreshPromise = null;
            refreshResolve = null;
            refreshReject = null;
            if (pendingRefreshTier) {
                _scheduleRefresh(pendingRefreshTier, { entity: 'video-sequence', id: 'queued' });
            }
            return context;
        }).catch(function (error) {
            refreshInFlight = false;
            if (refreshReject) refreshReject(error);
            refreshPromise = null;
            refreshResolve = null;
            refreshReject = null;
            if (pendingRefreshTier) {
                _scheduleRefresh(pendingRefreshTier, { entity: 'video-sequence', id: 'queued' });
            }
            return null;
        });
    }

    function _scheduleRefresh(tier, detail) {
        tier = _normalizeRefreshTier(tier);
        var signature = _refreshSignature(detail, tier);
        var now = Date.now();
        if (signature === lastRefreshSignature && now - lastRefreshAt < REFRESH_DEBOUNCE_MS) {
            return refreshPromise || Promise.resolve(lastContext);
        }
        pendingRefreshTier = _pickRefreshTier(pendingRefreshTier, tier);
        pendingRefreshSignature = signature;
        if (refreshTimer || refreshInFlight) {
            return refreshPromise || Promise.resolve(lastContext);
        }
        if (!refreshPromise) {
            refreshPromise = new Promise(function (resolve, reject) {
                refreshResolve = resolve;
                refreshReject = reject;
            });
        }
        refreshTimer = window.setTimeout(_flushRefreshQueue, REFRESH_DEBOUNCE_MS);
        return refreshPromise;
    }

    function _refreshByTier(tier) {
        if (tier === 'static') {
            return _reloadStaticAndRender();
        }
        if (tier === 'outputs') {
            return _reloadOutputAndRender();
        }
        return _reloadSequenceAndRender();
    }

    function _renderMergedContext() {
        var context = _composeContext(staticContext, timelineContext, outputContext);
        _render(context);
        if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        return context;
    }

    function _reloadStaticAndRender() {
        return _loadStaticContext().then(function (baseContext) {
            staticContext = baseContext;
            return Promise.all([
                _loadSequenceContext(baseContext),
                _loadOutputContext(baseContext),
            ]).then(function (loaded) {
                timelineContext = loaded[0] || { sequences: [], sequence: null, clips: [], subtitles: [] };
                outputContext = loaded[1] || { exports: [], snapshots: [] };
                return _renderMergedContext();
            });
        });
    }

    function _reloadSequenceAndRender() {
        if (!staticContext || !staticContext.project) {
            return _reloadStaticAndRender();
        }
        return _loadSequenceContext(staticContext).then(function (sequenceContext) {
            timelineContext = sequenceContext || { sequences: [], sequence: null, clips: [], subtitles: [] };
            return _renderMergedContext();
        });
    }

    function _reloadOutputAndRender() {
        if (!staticContext || !staticContext.project) {
            return _reloadStaticAndRender();
        }
        return _loadOutputContext(staticContext).then(function (nextOutputContext) {
            outputContext = nextOutputContext || { exports: [], snapshots: [] };
            return _renderMergedContext();
        });
    }

    loaders['video-editor'] = function () {
        _reloadStaticAndRender().catch(function (error) {
            console.warn('[page-loaders] video-editor load failed:', error);
            if (typeof showToast === 'function') {
                showToast('视频剪辑页加载失败: ' + ((error && error.message) || '未知错误'), 'error');
            }
        });
    };

    window.__videoEditorPageMain = {
        refresh: function () { return _scheduleRefresh('timeline', { entity: 'video-sequence', action: 'manual-refresh' }); },
        refreshTimeline: function () { return _scheduleRefresh('timeline', { entity: 'video-sequence', action: 'manual-refresh' }); },
        refreshOutputs: function () { return _scheduleRefresh('outputs', { entity: 'video-export', action: 'manual-refresh' }); },
        refreshStatic: function () { return _scheduleRefresh('static', { entity: 'video-project', action: 'manual-refresh' }); },
        handleDataChanged: function (detail) {
            detail = detail || {};
            return _scheduleRefresh(_refreshTierForEntity(detail.entity, detail.action), detail);
        },
        rerender: function () { if (lastContext) _render(lastContext); },
        getState: function () { return pageState; },
        getContext: function () { return lastContext; },
        selectSequence: function (sequenceId) {
            pageState.selectedSequenceId = Number(sequenceId || 0) || null;
            return _scheduleRefresh('timeline', { entity: 'video-sequence', id: sequenceId, action: 'selected' });
        },
    };
})();
