(function () {
    'use strict';

    if (typeof window.registerBindingModule !== 'function') {
        throw new Error('binding module registry not loaded');
    }

    function _page() {
        return window.__videoEditorPageMain || null;
    }

    function _context() {
        var page = _page();
        return page && typeof page.getContext === 'function' ? page.getContext() : null;
    }

    function _state() {
        return window.__videoEditorPageState = window.__videoEditorPageState || {};
    }

    function _refresh(kind, detail) {
        var page = _page();
        if (!page) return;
        if (kind === 'static' && typeof page.refreshStatic === 'function') {
            page.refreshStatic();
            return;
        }
        if (kind === 'outputs' && typeof page.refreshOutputs === 'function') {
            page.refreshOutputs();
            return;
        }
        if (kind === 'timeline' && typeof page.refreshTimeline === 'function') {
            page.refreshTimeline();
            return;
        }
        if (kind && typeof page.handleDataChanged === 'function') {
            page.handleDataChanged(detail || {});
            return;
        }
        if (typeof page.refresh === 'function') page.refresh();
    }

    function _rerender() {
        var page = _page();
        if (page && typeof page.rerender === 'function') page.rerender();
    }

    function _ensureProjectSequence() {
        var ctx = _context();
        if (ctx && ctx.project && ctx.sequence) {
            return Promise.resolve({ project: ctx.project, sequence: ctx.sequence, context: ctx });
        }
        return api.videoProjects.create({ name: '默认视频工程' }).then(function (project) {
            _state().selectedProjectId = Number(project.id || 0) || null;
            return api.videoSequences.list(project.id).then(function (sequences) {
                var sequence = (sequences || [])[0] || null;
                _state().selectedSequenceId = sequence ? Number(sequence.id) : null;
                return { project: project, sequence: sequence, context: { project: project, sequence: sequence, sequences: sequences || [] } };
            });
        });
    }

    function _selectedClip() {
        var ctx = _context();
        if (!ctx) return null;
        return (ctx.clips || []).find(function (clip) {
            return Number(clip.id) === Number(_state().selectedClipId);
        }) || (ctx.clips || [])[0] || null;
    }

    function _selectedSubtitle() {
        var ctx = _context();
        if (!ctx) return null;
        return (ctx.subtitles || []).find(function (item) {
            return Number(item.id) === Number(_state().selectedSubtitleId);
        }) || null;
    }

    function _sequenceLabel(sequence) {
        return sequence && sequence.name ? sequence.name : '未命名序列';
    }

    function _createSubtitle() {
        return _ensureProjectSequence().then(function (payload) {
            if (!payload.sequence) {
                showToast('当前工程没有可用序列', 'warning');
                return null;
            }
            var clip = _selectedClip();
            var state = _state();
            var promptText = window.prompt('请输入字幕内容', clip ? '新字幕' : '字幕');
            if (!promptText) return null;
            var startMs = clip ? Number(clip.start_ms || 0) : Number(state.playheadMs || 0);
            var endMs = clip ? (Number(clip.start_ms || 0) + Math.min(Number(clip.duration_ms || 2000), 3000)) : (startMs + 2000);
            return api.videoSubtitles.create({
                sequence_id: payload.sequence.id,
                start_ms: startMs,
                end_ms: endMs,
                text: promptText,
            }).then(function (subtitle) {
                state.selectedSubtitleId = subtitle && subtitle.id ? Number(subtitle.id) : state.selectedSubtitleId;
                showToast('字幕已创建', 'success');
                _refresh('timeline', { entity: 'video-subtitle', action: 'created' });
                return subtitle;
            });
        }).catch(function (err) {
            showToast('创建字幕失败: ' + ((err && err.message) || '未知错误'), 'error');
            return null;
        });
    }

    function _runExport(preset) {
        return _ensureProjectSequence().then(function (payload) {
            if (!payload.sequence) {
                showToast('当前工程没有可用序列', 'warning');
                return null;
            }
            return api.videoExports.create({
                project_id: payload.project.id,
                sequence_id: payload.sequence.id,
                preset: preset || 'final',
            }).then(function (result) {
                var exportId = result && (result.export_id || (result.export && result.export.id));
                if (!exportId) {
                    showToast('导出任务已创建', 'success');
                    _refresh('outputs', { entity: 'video-export', action: 'created' });
                    return result;
                }
                return api.videoExports.run(exportId).then(function (exportRow) {
                    showToast((preset === 'preview' ? '试看导出' : '终版导出') + '已完成', 'success');
                    _refresh('outputs', { entity: 'video-export', preset: preset || 'final', action: 'finished' });
                    return exportRow;
                });
            });
        }).catch(function (err) {
            showToast('导出失败: ' + ((err && err.message) || '未知错误'), 'error');
            return null;
        });
    }

    function _switchSequence() {
        return _ensureProjectSequence().then(function (payload) {
            var ctx = _context() || payload.context;
            var sequences = (ctx && ctx.sequences) || [];
            var project = payload.project || (ctx && ctx.project);
            if (!project) {
                showToast('当前没有可用工程', 'warning');
                return null;
            }
            if (sequences.length <= 1) {
                return api.videoSequences.create({
                    project_id: project.id,
                    name: '序列 ' + (sequences.length + 1),
                }).then(function (sequence) {
                    return api.videoSequences.setActive(project.id, sequence.id).then(function () {
                        _state().selectedSequenceId = Number(sequence.id);
                        showToast('已创建并切换到 ' + _sequenceLabel(sequence), 'success');
                        _refresh('timeline', { entity: 'video-sequence', action: 'created-and-activated' });
                        return sequence;
                    });
                });
            }
            var currentId = Number(_state().selectedSequenceId || (payload.sequence && payload.sequence.id) || 0);
            var currentIndex = sequences.findIndex(function (item) { return Number(item.id) === currentId; });
            var next = sequences[(currentIndex + 1 + sequences.length) % sequences.length];
            return api.videoSequences.setActive(project.id, next.id).then(function () {
                _state().selectedSequenceId = Number(next.id);
                showToast('已切换到 ' + _sequenceLabel(next), 'success');
                _refresh('timeline', { entity: 'video-sequence', action: 'activated' });
                return next;
            });
        }).catch(function (err) {
            showToast('切换序列失败: ' + ((err && err.message) || '未知错误'), 'error');
            return null;
        });
    }

    function _trimSelectedClip(edge) {
        var clip = _selectedClip();
        if (!clip) {
            showToast('请先选中一个片段', 'warning');
            return Promise.resolve(null);
        }
        var state = _state();
        var playheadMs = Number(state.playheadMs || 0);
        var offset = Math.max(0, playheadMs - Number(clip.start_ms || 0));
        var nextIn = Number(clip.source_in_ms || 0);
        var nextOut = Number(clip.source_out_ms || 0);
        if (edge === 'in') {
            nextIn = Math.min(nextOut - 40, Math.max(0, nextIn + offset));
        } else {
            nextOut = Math.max(nextIn + 40, Math.min(nextOut, Number(clip.source_in_ms || 0) + offset));
        }
        return api.videoClips.update(clip.id, {
            source_in_ms: nextIn,
            source_out_ms: nextOut,
        }).then(function () {
            showToast(edge === 'in' ? '入点已更新' : '出点已更新', 'success');
            _refresh('timeline', { entity: 'video-clip', edge: edge, action: 'trimmed' });
        }).catch(function (err) {
            showToast('裁切失败: ' + ((err && err.message) || '未知错误'), 'error');
            return null;
        });
    }

    function _moveClip(direction) {
        var clip = _selectedClip();
        if (!clip) {
            showToast('请先选中一个片段', 'warning');
            return Promise.resolve(null);
        }
        return api.videoClips.update(clip.id, {
            direction: direction,
            sequence_id: clip.sequence_id,
        }).then(function () {
            showToast(direction === 'left' ? '片段已左移' : '片段已右移', 'success');
            _refresh('timeline', { entity: 'video-clip', direction: direction, action: 'moved' });
        }).catch(function (err) {
            showToast('移动片段失败: ' + ((err && err.message) || '未知错误'), 'error');
            return null;
        });
    }

    function _deleteClip() {
        var clip = _selectedClip();
        if (!clip) {
            showToast('请先选中一个片段', 'warning');
            return Promise.resolve(null);
        }
        if (!window.confirm('确定删除当前片段吗？')) {
            return Promise.resolve(null);
        }
        return api.videoClips.remove(clip.id).then(function () {
            _state().selectedClipId = null;
            showToast('片段已删除', 'success');
            _refresh('timeline', { entity: 'video-clip', action: 'deleted' });
        }).catch(function (err) {
            showToast('删除片段失败: ' + ((err && err.message) || '未知错误'), 'error');
            return null;
        });
    }

    function _editSubtitle() {
        var subtitle = _selectedSubtitle();
        if (!subtitle) {
            showToast('请先选中一条字幕', 'warning');
            return Promise.resolve(null);
        }
        var nextText = window.prompt('编辑字幕内容', subtitle.text || '');
        if (!nextText) return Promise.resolve(null);
        return api.videoSubtitles.update(subtitle.id, { text: nextText }).then(function () {
            showToast('字幕已更新', 'success');
            _refresh('timeline', { entity: 'video-subtitle', action: 'updated' });
        }).catch(function (err) {
            showToast('更新字幕失败: ' + ((err && err.message) || '未知错误'), 'error');
            return null;
        });
    }

    function _deleteSubtitle() {
        var subtitle = _selectedSubtitle();
        if (!subtitle) {
            showToast('请先选中一条字幕', 'warning');
            return Promise.resolve(null);
        }
        if (!window.confirm('确定删除当前字幕吗？')) {
            return Promise.resolve(null);
        }
        return api.videoSubtitles.remove(subtitle.id).then(function () {
            _state().selectedSubtitleId = null;
            showToast('字幕已删除', 'success');
            _refresh('timeline', { entity: 'video-subtitle', action: 'deleted' });
        }).catch(function (err) {
            showToast('删除字幕失败: ' + ((err && err.message) || '未知错误'), 'error');
            return null;
        });
    }

    function _saveSnapshot() {
        return _ensureProjectSequence().then(function (payload) {
            var title = window.prompt('请输入快照标题', '自动保存快照');
            if (!title) return null;
            return api.videoSnapshots.create({
                project_id: payload.project.id,
                title: title,
            }).then(function (snapshot) {
                _state().selectedSnapshotId = snapshot && snapshot.id ? Number(snapshot.id) : null;
                showToast('快照已保存', 'success');
                _refresh('outputs', { entity: 'video-snapshot', action: 'created' });
                return snapshot;
            });
        }).catch(function (err) {
            showToast('保存快照失败: ' + ((err && err.message) || '未知错误'), 'error');
            return null;
        });
    }

    function _restoreSnapshot() {
        var ctx = _context();
        var snapshotId = Number(_state().selectedSnapshotId || 0);
        if (!snapshotId && ctx && ctx.snapshots && ctx.snapshots[0]) {
            snapshotId = Number(ctx.snapshots[0].id || 0);
        }
        if (!snapshotId) {
            showToast('没有可恢复的快照', 'warning');
            return Promise.resolve(null);
        }
        return api.videoSnapshots.restore(snapshotId).then(function () {
            showToast('快照已恢复', 'success');
            _refresh('timeline', { entity: 'video-snapshot', action: 'restored' });
        }).catch(function (err) {
            showToast('恢复快照失败: ' + ((err && err.message) || '未知错误'), 'error');
            return null;
        });
    }

    window.registerBindingModule('video-editor', function () {
        return {
            '发起终版导出': function () { return _runExport('final'); },
            '试看导出': function () { return _runExport('preview'); },
            '切换剪辑序列': _switchSequence,
            '导入素材': function () {
                return _ensureProjectSequence().then(function (payload) {
                    return _pickFilesAndImportAssets(currentRoute).then(function (assets) {
                        var ids = (assets || []).map(function (asset) { return asset && asset.id; }).filter(Boolean);
                        if (!ids.length || !payload.sequence) {
                            _refresh('timeline', { entity: 'video-clip', action: 'import-skipped' });
                            return null;
                        }
                        return api.videoClips.appendAssets(payload.sequence.id, { asset_ids: ids }).then(function () {
                            showToast('导入素材已自动加入时间线', 'success');
                            _refresh('timeline', { entity: 'video-clip', action: 'imported' });
                        });
                    });
                }).catch(function (err) {
                    showToast('导入并挂载素材失败: ' + ((err && err.message) || '未知错误'), 'error');
                    return null;
                });
            },
            '添加批注': _createSubtitle,
            '新增字幕': _createSubtitle,
            '编辑字幕': _editSubtitle,
            '删除字幕': _deleteSubtitle,
            '保存快照': _saveSnapshot,
            '恢复快照': _restoreSnapshot,
            '回到开头': function () {
                _state().playheadMs = 0;
                _rerender();
            },
            '逐帧': function () {
                _state().playheadMs = Number(_state().playheadMs || 0) + 40;
                _rerender();
            },
            '设入点': function () { return _trimSelectedClip('in'); },
            '设出点': function () { return _trimSelectedClip('out'); },
            '左移片段': function () { return _moveClip('left'); },
            '右移片段': function () { return _moveClip('right'); },
            '删除片段': _deleteClip,
        };
    });
})();
