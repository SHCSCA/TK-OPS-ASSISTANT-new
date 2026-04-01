/* ── bindings/video-editor-bindings.js ─ 视频剪辑页交互绑定 ──
   负责 video-editor 路由的按鈕、工具栏与键盘交互。
   依赖：bindings.js（全局 bindRouteInteractions 注册机制）
   ──────────────────────────────────────────────────── */
(function () {
    'use strict';

    function _esc(value) {
        return String(value == null ? '' : value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function _typeLabel(value) {
        var type = String(value || '').toLowerCase();
        if (type === 'text' || type === 'subtitle') return '字幕';
        if (type === 'video') return '视频';
        if (type === 'audio') return '音频';
        if (type === 'image' || type === 'template') return '图片';
        return '素材';
    }

    function _parseJsonObject(value) {
        try {
            var parsed = JSON.parse(String(value || '{}'));
            return parsed && typeof parsed === 'object' ? parsed : {};
        } catch (error) {
            return {};
        }
    }

    function _clamp(number, minValue, maxValue) {
        return Math.max(minValue, Math.min(maxValue, number));
    }

    function _audioState(clip) {
        var meta = _parseJsonObject(clip && clip.meta_json);
        var currentVolume = Number(clip && clip.volume || 0);
        var rememberedVolume = Number(meta.pre_mute_volume || (currentVolume > 0 ? currentVolume : 1));
        var muted = !!meta.audio_muted || currentVolume <= 0.0001;
        return {
            muted: muted,
            volume: _clamp(currentVolume, 0, 2),
            rememberedVolume: _clamp(rememberedVolume > 0 ? rememberedVolume : 1, 0, 2),
        };
    }

    function _bindOnce(selector, binderKey, handler) {
        document.querySelectorAll(selector).forEach(function (node) {
            if (node.dataset[binderKey] === '1') return;
            node.dataset[binderKey] = '1';
            node.addEventListener('click', function (event) {
                event.preventDefault();
                event.stopPropagation();
                handler(node, event);
            });
        });
    }

    function _page() {
        return window.__videoEditorPage || null;
    }

    function _selectedAsset() {
        var page = _page();
        if (!page || typeof page.getSelectedAsset !== 'function') return null;
        return page.getSelectedAsset();
    }

    function _selectedClip() {
        var page = _page();
        if (!page || typeof page.getSelectedClip !== 'function') return null;
        return page.getSelectedClip();
    }

    function _selectedSubtitle() {
        var page = _page();
        if (!page || typeof page.getSelectedSubtitle !== 'function') return null;
        return page.getSelectedSubtitle();
    }

    function _currentContext() {
        var page = _page();
        if (!page || typeof page.getContext !== 'function') return null;
        return page.getContext();
    }

    function _refreshPage() {
        var page = _page();
        if (page && typeof page.refresh === 'function') return page.refresh();
        return Promise.resolve();
    }

    function _validateSubtitlePayload(payload) {
        if (!String(payload.text || '').trim()) {
            throw new Error('字幕内容不能为空');
        }
        if (Number(payload.end_ms || 0) <= Number(payload.start_ms || 0)) {
            throw new Error('字幕结束时间必须晚于开始时间');
        }
    }

    function _libraryAssetIds() {
        var page = _page();
        if (!page || typeof page.getLibraryAssetIds !== 'function') return [];
        return page.getLibraryAssetIds();
    }

    function _videoProjectApi() {
        return window.api && window.api.videoProjects ? window.api.videoProjects : null;
    }

    function _timelineEditingApi() {
        var api = _videoProjectApi();
        if (!api || typeof api.addAssetsToTimeline !== 'function') return null;
        return api;
    }

    function _clipOnlyWarning() {
        var api = _timelineEditingApi();
        if (typeof showToast === 'function') {
            showToast(api
                ? '当前素材尚未进入时间轴，当前仅可预览；拖拽到时间轴后才可以做剪辑操作'
                : '当前版本暂不支持将素材拖入时间轴，请先升级 Bridge 与前端运行时', 'warning');
        }
    }

    function _appendAssets(assetIds, successText) {
        var context = _currentContext();
        var ids = (assetIds || []).map(function (assetId) {
            return parseInt(assetId || '0', 10);
        }).filter(Boolean);
        if (!ids.length) {
            return Promise.reject(new Error('请先选择至少一个素材'));
        }
        if (!context || !window.api || !window.api.videoProjects || typeof window.api.videoProjects.appendAssetsToSequence !== 'function') {
            return Promise.reject(new Error('当前版本暂不支持将素材加入序列'));
        }
        return window.api.videoProjects.appendAssetsToSequence({
            project_id: context.projectId,
            sequence_id: context.sequenceId,
            asset_ids: ids,
        }).then(function (result) {
            if (typeof showToast === 'function') {
                showToast(successText || ('已导入 ' + (result && result.count ? result.count : ids.length) + ' 个素材到当前素材库'), 'success');
            }
            return _refreshPage().then(function () {
                return result;
            });
        });
    }

    function _openTrimModal() {
        var clip = _selectedClip();
        var api = _timelineEditingApi();
        if (!clip) {
            _clipOnlyWarning();
            return;
        }
        if (!api || typeof api.trimVideoClip !== 'function') {
            if (typeof showToast === 'function') showToast('当前版本暂不支持裁切时间线片段', 'error');
            return;
        }

        openModal({
            title: '裁切时间线片段',
            submitText: '保存裁切',
            fields: [
                { key: 'source_in_ms', label: '入点 (ms)', type: 'number', value: Number(clip.source_in_ms || 0), min: 0, step: 100, required: true, hint: '只有时间轴片段可以做裁切操作。' },
                { key: 'source_out_ms', label: '出点 (ms)', type: 'number', value: Number(clip.source_out_ms || clip.duration_ms || 5000), min: 100, step: 100, required: true, hint: '修改后会重新计算片段时长与后续片段起点。' },
            ],
            onSubmit: function (data) {
                if (Number(data.source_out_ms || 0) <= Number(data.source_in_ms || 0)) {
                    throw new Error('出点必须晚于入点');
                }
                return api.trimVideoClip({
                    clip_id: clip.id,
                    source_in_ms: Number(data.source_in_ms || 0),
                    source_out_ms: Number(data.source_out_ms || 0),
                }).then(function () {
                    if (typeof showToast === 'function') showToast('片段裁切已保存', 'success');
                    return _refreshPage();
                });
            },
        });
    }

    function _openSubtitleModal() {
        var subtitle = _selectedSubtitle();
        var clip = _selectedClip();
        var context = _currentContext();
        var api = _videoProjectApi();
        if (!context || !api || typeof api.createVideoSubtitle !== 'function' || typeof api.updateVideoSubtitle !== 'function' || typeof api.deleteVideoSubtitle !== 'function') {
            if (typeof showToast === 'function') showToast('当前版本暂不支持字幕块编辑', 'error');
            return;
        }

        var defaultStart = subtitle ? Number(subtitle.start_ms || 0) : Number(clip ? clip.start_ms : 0);
        var defaultEnd = subtitle
            ? Number(subtitle.end_ms || 0)
            : Number(clip ? ((clip.start_ms || 0) + (clip.duration_ms || 2000)) : 2000);

        openModal({
            title: subtitle ? '编辑字幕块' : '新增字幕块',
            submitText: subtitle ? '保存字幕' : '创建字幕',
            fields: [
                { key: 'start_ms', label: '开始时间 (ms)', type: 'number', value: defaultStart, min: 0, step: 100, required: true },
                { key: 'end_ms', label: '结束时间 (ms)', type: 'number', value: defaultEnd, min: 100, step: 100, required: true },
                { key: 'text', label: '字幕内容', type: 'textarea', value: subtitle ? String(subtitle.text || '') : '', required: true, rows: 4, hint: subtitle ? '已选中时间轴字幕块，可直接修改或删除。' : '可基于当前选中片段新增字幕块。' },
            ],
            onOpen: function (ctx) {
                if (!subtitle) return;
                var deleteBtn = document.createElement('button');
                deleteBtn.type = 'button';
                deleteBtn.className = 'danger-button';
                deleteBtn.textContent = '删除字幕';
                deleteBtn.addEventListener('click', function () {
                    confirmModal({
                        title: '删除字幕块',
                        message: '确定删除当前字幕块？该操作会同步移除时间轴上的字幕段。',
                        confirmText: '删除',
                        tone: 'danger',
                    }).then(function (ok) {
                        if (!ok) return;
                        api.deleteVideoSubtitle({ subtitle_id: subtitle.id }).then(function () {
                            if (typeof showToast === 'function') showToast('字幕块已删除', 'success');
                            ctx.close();
                            return _refreshPage();
                        }).catch(function (err) {
                            if (typeof showToast === 'function') showToast('删除失败：' + (err.message || err), 'error');
                        });
                    });
                });
                ctx.footer.insertBefore(deleteBtn, ctx.submitButton);
            },
            onSubmit: function (data) {
                var payload = {
                    start_ms: Number(data.start_ms || 0),
                    end_ms: Number(data.end_ms || 0),
                    text: String(data.text || ''),
                };
                _validateSubtitlePayload(payload);
                var request = subtitle
                    ? api.updateVideoSubtitle({ subtitle_id: subtitle.id, start_ms: payload.start_ms, end_ms: payload.end_ms, text: payload.text })
                    : api.createVideoSubtitle({ project_id: context.projectId, sequence_id: context.sequenceId, start_ms: payload.start_ms, end_ms: payload.end_ms, text: payload.text });
                return request.then(function () {
                    if (typeof showToast === 'function') showToast(subtitle ? '字幕块已更新' : '字幕块已创建', 'success');
                    return _refreshPage();
                });
            },
        });
    }

    function _openAudioModal() {
        var clip = _selectedClip();
        var asset = _selectedAsset();
        var context = _currentContext();
        var api = _videoProjectApi();
        var isAudioClip = !!(clip && String(clip.track_type || '').toLowerCase() === 'audio');
        var isAudioAsset = !!(asset && String(asset.asset_type || '').toLowerCase() === 'audio');

        if (!context || !api || typeof api.addAssetsToTimeline !== 'function' || typeof api.updateVideoClipAudio !== 'function') {
            if (typeof showToast === 'function') showToast('当前版本暂不支持 A1 音频调节', 'error');
            return;
        }
        if (!isAudioClip && !isAudioAsset) {
            if (typeof showToast === 'function') showToast('请先选中 A1 音频片段，或在素材库中选中一个音频素材', 'warning');
            return;
        }

        var currentAudio = _audioState(clip);
        var defaultVolume = Math.round((isAudioClip ? (currentAudio.muted ? currentAudio.rememberedVolume : currentAudio.volume) : 1) * 100);
        var defaultMute = isAudioClip && currentAudio.muted ? 'muted' : 'normal';

        openModal({
            title: isAudioClip ? 'A1 音频调节' : '加入 A1 音频轨',
            submitText: isAudioClip ? '保存音频' : '加入 A1',
            fields: [
                { key: 'volume_percent', label: '音量 (%)', type: 'number', value: defaultVolume, min: 0, max: 200, step: 5, required: true, hint: isAudioClip ? '范围 0 - 200，静音会把当前输出音量压到 0。' : '加入 A1 时会同步写入当前音量。' },
                { key: 'mute', label: '静音状态', type: 'select', value: defaultMute, options: [{ value: 'normal', label: '正常输出' }, { value: 'muted', label: '静音' }], required: true },
            ],
            onSubmit: function (data) {
                var volumeValue = _clamp(Number(data.volume_percent || 0), 0, 200) / 100;
                var muteState = String(data.mute || 'normal') === 'muted';
                if (isAudioClip) {
                    return api.updateVideoClipAudio({
                        clip_id: clip.id,
                        volume: volumeValue,
                        muted: muteState,
                    }).then(function () {
                        if (typeof showToast === 'function') showToast('A1 音频已更新', 'success');
                        return _refreshPage();
                    });
                }

                return api.addAssetsToTimeline({
                    project_id: context.projectId,
                    sequence_id: context.sequenceId,
                    asset_ids: [parseInt(asset.id || '0', 10)],
                    track_type: 'audio',
                    track_index: 0,
                }).then(function (result) {
                    var clipId = result && result.clip_ids && result.clip_ids[0] ? parseInt(result.clip_ids[0], 10) : 0;
                    if (!clipId) return result;
                    return api.updateVideoClipAudio({
                        clip_id: clipId,
                        volume: volumeValue,
                        muted: muteState,
                    }).then(function () {
                        return result;
                    });
                }).then(function () {
                    if (typeof showToast === 'function') showToast('音频素材已加入 A1', 'success');
                    return _refreshPage();
                });
            },
        });
    }

    function _openAssetCenterPicker() {
        if (!window.api || !window.api.assets || typeof window.api.assets.list !== 'function') {
            if (typeof showToast === 'function') showToast('当前版本暂不支持读取素材中心', 'error');
            return;
        }

        window.api.assets.list().then(function (assets) {
            var importedIds = _libraryAssetIds();
            var candidates = (assets || []).filter(function (asset) {
                return importedIds.indexOf(String(asset.id || '')) === -1;
            });
            if (!candidates.length) {
                if (typeof showToast === 'function') showToast('素材中心里没有可导入的新素材', 'info');
                return;
            }

            var selectedIds = [];

            openModal({
                title: '导入素材中心素材',
                submitText: '导入选中素材',
                fields: [
                    { key: 'keyword', label: '搜索素材', placeholder: '输入文件名 / 标签 / 路径关键词' },
                ],
                onOpen: function (ctx) {
                    var block = document.createElement('section');
                    block.className = 'form-group video-asset-picker';
                    block.innerHTML = ''
                        + '<label class="form-label">批量选择素材 <span class="form-required">*</span></label>'
                        + '<div class="subtle">已选 <strong class="js-video-asset-select-count">0</strong> / ' + candidates.length + '</div>'
                        + '<div class="video-asset-picker__layout">'
                        + '<div class="batch-select-list js-video-asset-select-list"></div>'
                        + '</div>'
                        + '<div style="display:flex;gap:8px;margin-top:8px;">'
                        + '<button type="button" class="secondary-button js-video-asset-check-all">全选</button>'
                        + '<button type="button" class="secondary-button js-video-asset-check-none">清空</button>'
                        + '</div>'
                        ;
                    ctx.form.insertBefore(block, ctx.form.firstChild);

                    var countEl = ctx.form.querySelector('.js-video-asset-select-count');
                    var listHost = ctx.form.querySelector('.js-video-asset-select-list');
                    var keywordInput = ctx.form.querySelector('[name="keyword"]');

                    function syncVisualSelection() {
                        ctx.form.querySelectorAll('.js-video-asset-choice').forEach(function (choice) {
                            var item = choice.closest('.batch-select-item--media');
                            var thumb = item ? item.querySelector('.source-thumb') : null;
                            if (thumb) thumb.classList.toggle('is-selected', !!choice.checked);
                        });
                    }

                    function syncSelection() {
                        selectedIds = Array.prototype.slice.call(ctx.form.querySelectorAll('.js-video-asset-choice:checked')).map(function (choice) {
                            return parseInt(choice.value || '0', 10);
                        }).filter(Boolean);
                        if (countEl) countEl.textContent = String(selectedIds.length);
                        ctx.submitButton.disabled = !selectedIds.length;
                    }

                    function renderList(keyword) {
                        var normalized = String(keyword || '').trim().toLowerCase();
                        var filtered = candidates.filter(function (asset) {
                            if (!normalized) return true;
                            var haystack = [asset.filename, asset.tags, asset.file_path, asset.asset_type].join(' ').toLowerCase();
                            return haystack.indexOf(normalized) !== -1;
                        });
                        if (!filtered.length) {
                            listHost.innerHTML = '<div class="subtle">没有匹配的素材，请换个关键词。</div>';
                            syncSelection();
                            return;
                        }
                        listHost.innerHTML = filtered.map(function (asset) {
                            var checked = selectedIds.indexOf(parseInt(asset.id || '0', 10)) !== -1 ? ' checked' : '';
                            return ''
                                + '<label class="batch-select-item batch-select-item--media" data-preview-id="' + _esc(String(asset.id)) + '">'
                                + '<input class="js-video-asset-choice" type="checkbox" value="' + _esc(String(asset.id)) + '"' + checked + '> '
                                + '<span class="batch-select-item__body">'
                                + window._editorShared.buildAssetThumb(asset, checked.trim() === 'checked')
                                + '<small>' + _esc(_typeLabel(asset.asset_type) + ' / ' + (asset.file_path || '未记录路径')) + '</small>'
                                + '</span>'
                                + '</label>';
                        }).join('');
                        if (window._editorShared && typeof window._editorShared.hydrateRuntimePreviews === 'function') {
                            window._editorShared.hydrateRuntimePreviews(listHost);
                        }
                        ctx.form.querySelectorAll('.js-video-asset-choice').forEach(function (choice) {
                            choice.addEventListener('change', function () {
                                syncVisualSelection();
                                syncSelection();
                            });
                        });
                        syncVisualSelection();
                        syncSelection();
                    }

                    if (keywordInput && keywordInput.dataset.videoAssetKeywordBound !== '1') {
                        keywordInput.dataset.videoAssetKeywordBound = '1';
                        keywordInput.addEventListener('input', function () {
                            renderList(keywordInput.value || '');
                        });
                    }

                    var checkAllBtn = ctx.form.querySelector('.js-video-asset-check-all');
                    if (checkAllBtn) {
                        checkAllBtn.addEventListener('click', function () {
                            ctx.form.querySelectorAll('.js-video-asset-choice').forEach(function (choice) {
                                choice.checked = true;
                            });
                            syncVisualSelection();
                            syncSelection();
                        });
                    }

                    var checkNoneBtn = ctx.form.querySelector('.js-video-asset-check-none');
                    if (checkNoneBtn) {
                        checkNoneBtn.addEventListener('click', function () {
                            ctx.form.querySelectorAll('.js-video-asset-choice').forEach(function (choice) {
                                choice.checked = false;
                            });
                            syncVisualSelection();
                            syncSelection();
                        });
                    }

                    ctx.submitButton.disabled = true;
                    renderList('');
                },
                onSubmit: function () {
                    if (!selectedIds.length) {
                        throw new Error('请先勾选要导入的素材');
                    }
                    return _appendAssets(selectedIds, '已导入 ' + selectedIds.length + ' 个素材到当前素材库');
                },
            });
        }).catch(function (err) {
            if (typeof showToast === 'function') showToast('加载素材中心失败：' + (err.message || err), 'error');
        });
    }

    window._videoEditorBindings = function () {
        _bindOnce('#mainHost .source-browser-tabs [data-type]', 'videoAssetFilterBound', function (tab) {
            var page = _page();
            if (!page || typeof page.setAssetType !== 'function') return;
            page.setAssetType(tab.dataset.type || 'video');
        });

        _bindOnce('#detailHost .video-inspector-tabs [data-tab]', 'videoInspectorTabBound', function (tab) {
            var page = _page();
            if (!page || typeof page.setInspectorTab !== 'function') return;
            page.setInspectorTab(tab.dataset.tab || 'properties');
        });

        _bindOnce('#mainHost .js-video-import-asset-center', 'videoAppendAssetBound', function () {
            _openAssetCenterPicker();
        });

        _bindOnce('#mainHost .js-video-import-external-assets', 'videoImportExternalBound', function () {
            if (typeof _pickFilesAndImportAssets !== 'function') {
                if (typeof showToast === 'function') showToast('当前版本暂不支持导入本地素材', 'error');
                return;
            }
            Promise.resolve(_pickFilesAndImportAssets('video-editor')).then(function (results) {
                var assetIds = (results || []).map(function (item) {
                    return item && item.id ? parseInt(item.id, 10) : 0;
                }).filter(Boolean);
                if (!assetIds.length) {
                    return _refreshPage().then(function () {
                        return null;
                    });
                }
                return _appendAssets(assetIds, '本地素材已加入当前素材库');
            }).catch(function (err) {
                if (typeof showToast === 'function') showToast('导入失败：' + (err.message || err), 'error');
            });
        });

        _bindOnce('#mainHost .js-video-trim-selected-clip', 'videoTrimClipBound', function () {
            _openTrimModal();
        });

        _bindOnce('#mainHost .js-video-toggle-playback, #mainHost .js-video-monitor-toggle-playback', 'videoMonitorToggleBound', function () {
            var page = _page();
            if (!page || typeof page.toggleMonitorPlayback !== 'function') {
                if (typeof showToast === 'function') showToast('当前版本暂不支持原生监视器播放控制', 'error');
                return;
            }
            page.toggleMonitorPlayback().catch(function (err) {
                if (typeof showToast === 'function') showToast('播放失败：' + (err.message || err), 'error');
            });
        });

        _bindOnce('#mainHost .js-video-monitor-surface', 'videoMonitorSurfaceBound', function (surface, event) {
            if (event.target && event.target.closest && event.target.closest('button, audio')) {
                return;
            }
            var page = _page();
            var asset = _selectedAsset();
            var clip = _selectedClip();
            var assetType = String((asset && asset.asset_type) || (clip && clip.asset_type) || '').toLowerCase();
            if (!page || typeof page.toggleMonitorPlayback !== 'function' || assetType !== 'video') {
                return;
            }
            page.toggleMonitorPlayback().catch(function (err) {
                if (typeof showToast === 'function') showToast('播放失败：' + (err.message || err), 'error');
            });
        });

        _bindOnce('#mainHost .js-video-seek-start', 'videoSeekStartBound', function () {
            var page = _page();
            if (!page || typeof page.seekMonitorStart !== 'function') return;
            page.seekMonitorStart().catch(function (err) {
                if (typeof showToast === 'function') showToast('定位失败：' + (err.message || err), 'error');
            });
        });

        _bindOnce('#mainHost .js-video-step-forward', 'videoStepForwardBound', function () {
            var page = _page();
            if (!page || typeof page.stepMonitorForward !== 'function') return;
            page.stepMonitorForward().catch(function (err) {
                if (typeof showToast === 'function') showToast('逐帧失败：' + (err.message || err), 'error');
            });
        });

        _bindOnce('#mainHost .js-video-delete-selected-clip', 'videoDeleteClipBound', function () {
            var clip = _selectedClip();
            var page = _page();
            if (!clip) {
                _clipOnlyWarning();
                return;
            }
            if (!page || typeof page.deleteSelectedClip !== 'function') {
                if (typeof showToast === 'function') showToast('当前版本暂不支持删除时间线片段', 'error');
                return;
            }
            confirmModal({
                title: '删除时间线片段',
                message: '确定删除当前选中的片段？后续片段会自动回填时间轴空位。',
                confirmText: '删除',
                tone: 'danger',
            }).then(function (ok) {
                if (!ok) return;
                page.deleteSelectedClip().then(function () {
                    if (typeof showToast === 'function') showToast('片段已删除', 'success');
                }).catch(function (err) {
                    if (typeof showToast === 'function') showToast('删除失败：' + (err.message || err), 'error');
                });
            });
        });

        _bindOnce('#mainHost .js-video-add-subtitle', 'videoSubtitleBound', function () {
            _openSubtitleModal();
        });

        _bindOnce('#mainHost .js-video-edit-audio', 'videoAudioBound', function () {
            _openAudioModal();
        });

        _bindOnce('#mainHost .js-switch-video-sequence', 'videoSwitchSequenceBound', function () {
            var page = _page();
            if (!page || typeof page.cycleSequence !== 'function') return;
            page.cycleSequence();
        });

        _bindOnce('#mainHost .js-export-final, #mainHost [data-action="export-final"]', 'videoExportBound', function () {
            var context = _currentContext();
            if (!context || !window.api || !window.api.videoProjects || typeof window.api.videoProjects.createVideoExport !== 'function') {
                if (typeof showToast === 'function') showToast('导出功能暂不可用', 'error');
                return;
            }
            window.api.videoProjects.createVideoExport({
                project_id: context.projectId,
                sequence_id: context.sequenceId,
            }).then(function () {
                if (typeof showToast === 'function') showToast('终版导出记录已创建，请等待后端执行链路接入', 'success');
                return _refreshPage();
            }).catch(function (err) {
                if (typeof showToast === 'function') showToast('导出失败：' + (err.message || err), 'error');
            });
        });
    };

}());
