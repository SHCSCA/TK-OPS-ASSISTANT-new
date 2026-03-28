(function () {
    'use strict';

    var shared = window.__pageLoaderShared;
    if (!shared) {
        throw new Error('page loader shared helpers not loaded');
    }

    var loaders = window._pageLoaders;
    if (!loaders) {
        throw new Error('page loader registries not loaded');
    }

    var _esc = shared.esc;
    var _normalizeTaskStatus = shared.normalizeTaskStatus;
    var _taskStatusLabel = shared.taskStatusLabel;
    var _taskStatusTone = shared.taskStatusTone;
    var _taskTypeLabel = shared.taskTypeLabel;
    var _taskTime = shared.taskTime;

    loaders['auto-reply'] = function () { _loadTaskOpsPage({ routeKey: 'auto-reply', title: '自动回复', tableMode: 'reply' }); };
    loaders['scheduled-publish'] = function () { _loadTaskOpsPage({ routeKey: 'scheduled-publish', title: '定时发布', tableMode: 'publish' }); };
    loaders['task-hall'] = function () { _loadTaskOpsPage({ routeKey: 'task-hall', title: '任务大厅', tableMode: 'generic' }); };
    loaders['data-collector'] = function () { _loadTaskOpsPage({ routeKey: 'data-collector', title: '数据采集助手', tableMode: 'collector' }); };
    loaders['auto-like'] = function () { _loadTaskOpsPage({ routeKey: 'auto-like', title: '自动点赞', tableMode: 'interaction' }); };
    loaders['auto-comment'] = function () { _loadTaskOpsPage({ routeKey: 'auto-comment', title: '自动评论', tableMode: 'interaction' }); };
    loaders['auto-message'] = function () { _loadTaskOpsPage({ routeKey: 'auto-message', title: '自动私信', tableMode: 'interaction' }); };
    loaders['task-scheduler'] = function () { _loadTaskOpsPage({ routeKey: 'task-scheduler', title: '任务调度', tableMode: 'calendar' }); };

    function _loadTaskOpsPage(config) {
        Promise.all([
            api.tasks.list().catch(function () { return []; }),
            api.accounts.list().catch(function () { return []; }),
            api.assets.list().catch(function () { return []; }),
        ]).then(function (results) {
            var tasks = results[0] || [];
            var accounts = results[1] || [];
            var assets = results[2] || [];
            var scopedTasks = _filterTasksForOpsMode(tasks, config.tableMode);
            var activeFilter = 'all';

            function render(filterKey) {
                activeFilter = filterKey || 'all';
                var filtered = _filterTasksByKey(scopedTasks, activeFilter);
                _updateTaskOpsMetrics(filtered, accounts, assets, config);
                _updateTaskOpsFilterTabs(scopedTasks, activeFilter);
                _renderTaskOpsBody(filtered, accounts, assets, config);
                _renderTaskOpsDetail(filtered, accounts, assets, config);
                _bindTaskOpsTaskActions(filtered, config);
                if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
            }

            _bindTaskOpsFilterTabs(scopedTasks, render);
            _bindTaskOpsHeaderActions(config, accounts);
            render(activeFilter);
        }).catch(function (e) {
            console.warn('[page-loaders] ' + config.routeKey + ' load failed:', e);
        });
    }

    function _updateTaskOpsMetrics(tasks, accounts, assets, config) {
        var cards = document.querySelectorAll('#mainHost .stat-grid .stat-card');
        if (cards.length >= 3) {
            cards[0].querySelector('.stat-card__value').textContent = String(tasks.length);
            cards[1].querySelector('.stat-card__value').textContent = String(tasks.filter(function (task) {
                return _normalizeTaskStatus(task.status) === 'failed' || _normalizeTaskStatus(task.status) === 'paused';
            }).length);
            cards[2].querySelector('.stat-card__value').textContent = Math.max(0, Math.min(100, Math.round((tasks.filter(function (task) {
                return _normalizeTaskStatus(task.status) === 'completed';
            }).length / Math.max(1, tasks.length)) * 100))) + '%';
        }
    }

    function _updateTaskOpsFilterTabs(tasks, activeFilter) {
        var counts = {
            all: tasks.length,
            running: 0,
            paused: 0,
            failed: 0,
            completed: 0,
            pending: 0,
        };
        tasks.forEach(function (task) {
            var status = _normalizeTaskStatus(task.status);
            if (counts[status] !== undefined) counts[status] += 1;
        });
        document.querySelectorAll('#mainHost .task-filter-tab').forEach(function (tab) {
            var key = _taskTabKey(tab.textContent);
            var label = _taskTabLabel(key);
            tab.textContent = label + ' (' + String(counts[key] || 0) + ')';
            tab.classList.toggle('is-active', key === activeFilter);
        });
    }

    function _bindTaskOpsFilterTabs(tasks, render) {
        _rewireElements('#mainHost .task-filter-tab', function (tab) {
            tab.addEventListener('click', function () {
                render(_taskTabKey(tab.textContent));
            });
        });
        _rewireElements('#mainHost .task-view-btn', function (btn) {
            btn.addEventListener('click', function () {
                document.querySelectorAll('#mainHost .task-view-btn').forEach(function (item) {
                    item.classList.remove('is-active');
                });
                btn.classList.add('is-active');
            });
        });
    }

    function _bindTaskOpsHeaderActions(config, accounts) {
        var title = typeof config === 'string' ? config : config.title;
        _rewireElements('#mainHost .page-header .primary-button', function (btn) {
            btn.addEventListener('click', function () {
                if (typeof openTaskForm === 'function' && config && typeof config === 'object') {
                    openTaskForm(_taskDraftForOpsRoute(config, accounts));
                    return;
                }
                showToast(title + ' 已接入真实任务池', 'info');
            });
        });
        _rewireElements('#mainHost .page-header .secondary-button', function (btn) {
            btn.addEventListener('click', function () {
                if (config && config.tableMode === 'interaction') {
                    _runInteractionQuickAction(config);
                    return;
                }
                showToast('已根据真实状态刷新 ' + title + ' 视图', 'success');
                if (typeof currentRoute !== 'undefined' && loaders[currentRoute]) loaders[currentRoute]();
            });
        });
    }

    function _runInteractionQuickAction(config) {
        api.tasks.list().then(function (tasks) {
            var scoped = _filterTasksForOpsMode(tasks || [], 'interaction');
            if (config.routeKey === 'auto-like') {
                var whitelistTargets = scoped.filter(function (task) {
                    return _normalizeTaskStatus(task.status) !== 'completed';
                }).slice(0, 5);
                if (!whitelistTargets.length) {
                    showToast('当前没有可加入白名单的任务', 'warning');
                    return;
                }
                Promise.all(whitelistTargets.map(function (task) {
                    var summary = String(task.result_summary || '');
                    if (summary.indexOf('[白名单]') === -1) summary = '[白名单] ' + summary;
                    return api.tasks.update(task.id, { result_summary: summary });
                })).then(function () {
                    showToast('已批量更新白名单策略（' + whitelistTargets.length + ' 条）', 'success');
                    if (loaders[config.routeKey]) loaders[config.routeKey]();
                });
                return;
            }
            if (config.routeKey === 'auto-comment') {
                var running = scoped.filter(function (task) {
                    return _normalizeTaskStatus(task.status) === 'running';
                });
                var overflow = running.slice(2);
                if (!overflow.length) {
                    showToast('当前评论节流阈值内，无需调整', 'info');
                    return;
                }
                Promise.all(overflow.map(function (task) {
                    return api.tasks.update(task.id, { status: 'paused', result_summary: '[节流] 超过并发阈值，自动暂停' });
                })).then(function () {
                    showToast('已执行评论节流：暂停 ' + overflow.length + ' 条任务', 'warning');
                    if (loaders[config.routeKey]) loaders[config.routeKey]();
                });
                return;
            }
            if (config.routeKey === 'auto-message') {
                var pending = scoped.filter(function (task) {
                    return _normalizeTaskStatus(task.status) === 'pending';
                }).slice(0, 6);
                if (!pending.length) {
                    showToast('当前没有待限速的私信任务', 'info');
                    return;
                }
                Promise.all(pending.map(function (task, index) {
                    var summary = '[发送限制] 波次 ' + (index + 1) + '，间隔 90 秒';
                    return api.tasks.update(task.id, { priority: index < 2 ? 'high' : 'medium', result_summary: summary });
                })).then(function () {
                    showToast('已刷新私信发送限制（' + pending.length + ' 条）', 'success');
                    if (loaders[config.routeKey]) loaders[config.routeKey]();
                });
                return;
            }
            if (loaders[config.routeKey]) loaders[config.routeKey]();
        }).catch(function (err) {
            showToast('执行联动操作失败: ' + err.message, 'error');
        });
    }

    function _renderTaskOpsBody(tasks, accounts, assets, config) {
        if (document.querySelector('#mainHost .calendar-grid')) {
            _renderTaskOpsCalendar(tasks);
        } else if (document.querySelector('#mainHost .kanban-grid')) {
            _renderTaskOpsKanban(tasks, config);
        }
        _renderTaskOpsTable(tasks, accounts, config);
    }

    function _renderTaskOpsKanban(tasks, config) {
        var columns = document.querySelectorAll('#mainHost .kanban-column');
        if (!columns.length) return;
        columns.forEach(function (column, index) {
            var title = column.querySelector('.kanban-column__title');
            var list = column.querySelector('.kanban-list');
            if (!list) return;
            var targetStatus = _kanbanStatusByTitle(title ? title.textContent : '', index, config);
            var bucket = tasks.filter(function (task) {
                return _normalizeTaskStatus(task.status) === targetStatus;
            });
            if (!bucket.length && index === 0) bucket = tasks.slice(0, 3);
            list.innerHTML = bucket.length ? bucket.slice(0, 4).map(function (task) {
                return _taskTicketHtml(task);
            }).join('') : '<article class="ticket-card"><strong>暂无任务</strong><div class="subtle">当前筛选条件下没有匹配项</div></article>';
        });
    }

    function _renderTaskOpsCalendar(tasks) {
        var days = document.querySelectorAll('#mainHost .calendar-day');
        if (!days.length) return;
        days.forEach(function (day, index) {
            var slots = tasks.filter(function (_task, taskIndex) {
                return taskIndex % days.length === index;
            });
            var existing = day.querySelectorAll('.calendar-slot');
            existing.forEach(function (node) { node.remove(); });
            (slots.length ? slots.slice(0, 2) : [null]).forEach(function (task) {
                var slot = document.createElement('div');
                slot.className = 'calendar-slot';
                slot.textContent = task ? ((_taskTime(task, index) + ' ' + (task.title || _taskTypeLabel(task.task_type)))) : '暂无排期';
                day.appendChild(slot);
            });
        });
    }

    function _renderTaskOpsTable(tasks, accounts, config) {
        var tbody = document.querySelector('#mainHost .table-wrapper tbody');
        if (!tbody) return;
        var rows = tasks.slice(0, 8).map(function (task, index) {
            var actions = _taskInlineActionButtons(task, config);
            if (config.tableMode === 'reply') {
                return '<tr class="route-row" data-task-id="' + (task.id || '') + '" data-search="' + _esc((task.title || '') + ' ' + _taskStatusLabel(task.status)) + '"><td><strong>' + _esc(task.title || ('回复规则 ' + (index + 1))) + '</strong></td><td>' + _esc((accounts[index] && accounts[index].region) || '全站') + '</td><td><span class="tag ' + _taskStatusTone(task.status) + '">' + (_normalizeTaskStatus(task.status) === 'failed' ? '高' : '中') + '</span></td><td><div class="list-row"><span class="status-chip ' + _taskStatusTone(task.status) + '">' + _taskStatusLabel(task.status) + '</span><span class="detail-actions">' + actions + '</span></div></td></tr>';
            }
            if (config.tableMode === 'publish') {
                return '<tr class="route-row" data-task-id="' + (task.id || '') + '" data-search="' + _esc((task.title || '') + ' ' + _taskStatusLabel(task.status)) + '"><td><strong>' + _esc(task.title || ('发布计划 ' + (index + 1))) + '</strong></td><td>' + _taskTime(task, index) + '</td><td>' + _esc((accounts[index] && accounts[index].platform) || 'TikTok') + '</td><td><div class="list-row"><span>' + _taskStatusLabel(task.status) + '</span><span class="detail-actions">' + actions + '</span></div></td></tr>';
            }
            if (config.tableMode === 'collector') {
                return '<tr class="route-row" data-task-id="' + (task.id || '') + '" data-search="' + _esc((task.title || '') + ' ' + _taskTypeLabel(task.task_type)) + '"><td><strong>' + _esc(task.title || ('采集任务 ' + (index + 1))) + '</strong></td><td>' + _taskTypeLabel(task.task_type) + '</td><td>' + _taskStatusLabel(task.status) + '</td><td><div class="list-row"><span>' + _esc((accounts[index] && accounts[index].region) || '多区域') + '</span><span class="detail-actions">' + actions + '</span></div></td></tr>';
            }
            return '<tr class="route-row" data-task-id="' + (task.id || '') + '" data-search="' + _esc((task.title || '') + ' ' + _taskStatusLabel(task.status)) + '"><td><strong>' + _esc(task.title || ('任务 ' + (index + 1))) + '</strong></td><td>' + _taskTypeLabel(task.task_type) + '</td><td>' + _taskStatusLabel(task.status) + '</td><td><div class="list-row"><span>' + _taskTime(task, index) + '</span><span class="detail-actions">' + actions + '</span></div></td></tr>';
        });
        tbody.innerHTML = rows.length ? rows.join('') : '<tr><td colspan="4" style="text-align:center;padding:32px;">暂无任务数据</td></tr>';
    }

    function _taskInlineActionButtons(task, config) {
        var status = _normalizeTaskStatus(task.status);
        var buttons = [];
        if (status === 'pending' || status === 'paused' || status === 'failed') {
            buttons.push('<button class="ghost-button js-taskop-start" data-id="' + (task.id || '') + '">启动</button>');
        }
        if (status === 'running') {
            buttons.push('<button class="ghost-button js-taskop-complete" data-id="' + (task.id || '') + '">完成</button>');
            buttons.push('<button class="ghost-button js-taskop-pause" data-id="' + (task.id || '') + '">暂停</button>');
            buttons.push('<button class="ghost-button js-taskop-fail" data-id="' + (task.id || '') + '">标记失败</button>');
        }
        if (status === 'failed') {
            buttons.push('<button class="ghost-button js-taskop-retry" data-id="' + (task.id || '') + '">重试</button>');
        }
        if (config && config.tableMode === 'interaction') {
            buttons.push('<button class="ghost-button js-taskop-whitelist" data-id="' + (task.id || '') + '">白名单</button>');
        }
        buttons.push('<button class="ghost-button js-taskop-edit" data-id="' + (task.id || '') + '">编辑</button>');
        buttons.push('<button class="danger-button js-taskop-delete" data-id="' + (task.id || '') + '">删除</button>');
        return buttons.join('');
    }

    function _bindTaskOpsTaskActions(tasks, config) {
        _rewireElements('#mainHost .js-taskop-start', function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                api.tasks.start(id).then(function () {
                    showToast('任务已启动', 'success');
                    if (loaders[config.routeKey]) loaders[config.routeKey]();
                }).catch(function (err) {
                    showToast('启动失败: ' + err.message, 'error');
                });
            });
        });
        _rewireElements('#mainHost .js-taskop-complete', function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                api.tasks.complete(id).then(function () {
                    showToast('任务已完成', 'success');
                    if (loaders[config.routeKey]) loaders[config.routeKey]();
                }).catch(function (err) {
                    showToast('完成失败: ' + err.message, 'error');
                });
            });
        });
        _rewireElements('#mainHost .js-taskop-pause', function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                api.tasks.update(id, { status: 'paused' }).then(function () {
                    showToast('任务已暂停', 'warning');
                    if (loaders[config.routeKey]) loaders[config.routeKey]();
                }).catch(function (err) {
                    showToast('暂停失败: ' + err.message, 'error');
                });
            });
        });
        _rewireElements('#mainHost .js-taskop-fail', function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                api.tasks.fail(id).then(function () {
                    showToast('任务已标记失败', 'warning');
                    if (loaders[config.routeKey]) loaders[config.routeKey]();
                }).catch(function (err) {
                    showToast('标记失败失败: ' + err.message, 'error');
                });
            });
        });
        _rewireElements('#mainHost .js-taskop-retry', function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                api.tasks.start(id).then(function () {
                    showToast('任务已重试', 'success');
                    if (loaders[config.routeKey]) loaders[config.routeKey]();
                }).catch(function (err) {
                    showToast('重试失败: ' + err.message, 'error');
                });
            });
        });
        _rewireElements('#mainHost .js-taskop-whitelist', function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                var task = (tasks || []).find(function (item) { return Number(item.id) === id; });
                if (!task) return;
                var summary = String(task.result_summary || '');
                if (summary.indexOf('[白名单]') === -1) summary = '[白名单] ' + summary;
                api.tasks.update(id, { result_summary: summary }).then(function () {
                    showToast('已加入白名单策略', 'success');
                    if (loaders[config.routeKey]) loaders[config.routeKey]();
                }).catch(function (err) {
                    showToast('白名单更新失败: ' + err.message, 'error');
                });
            });
        });
        _rewireElements('#mainHost .js-taskop-edit', function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                var task = (tasks || []).find(function (item) { return Number(item.id) === id; });
                if (task && typeof openTaskForm === 'function') openTaskForm(task);
            });
        });
        _rewireElements('#mainHost .js-taskop-delete', function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                confirmModal({
                    title: '删除任务',
                    message: '确定要删除这条任务记录？此操作不可恢复。',
                    confirmText: '删除',
                    tone: 'danger',
                }).then(function (ok) {
                    if (!ok) return;
                    api.tasks.remove(id).then(function () {
                        showToast('任务已删除', 'success');
                        if (loaders[config.routeKey]) loaders[config.routeKey]();
                    }).catch(function (err) {
                        showToast('删除失败: ' + err.message, 'error');
                    });
                });
            });
        });
    }

    function _renderTaskOpsDetail(tasks, accounts, assets, config) {
        var detailItems = document.querySelectorAll('#detailHost .detail-item strong');
        if (detailItems.length >= 3) {
            detailItems[0].textContent = String(tasks.length) + ' 条任务已接入';
            detailItems[1].textContent = String(tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'failed'; }).length) + ' 条需关注';
            detailItems[2].textContent = '账号 ' + accounts.length + ' / 素材 ' + assets.length;
        }
        var boardList = document.querySelector('#detailHost .board-list');
        if (boardList) {
            boardList.innerHTML = tasks.slice(0, 3).map(function (task) {
                return '<article class="board-card"><strong>' + _esc(task.title || _taskTypeLabel(task.task_type)) + '</strong><div class="subtle">'
                    + _esc(task.result_summary || ('当前状态：' + _taskStatusLabel(task.status))) + '</div><div class="status-strip"><span class="pill ' + _taskStatusTone(task.status) + '">' + _taskStatusLabel(task.status) + '</span></div></article>';
            }).join('');
        }
    }

    function _filterTasksByKey(tasks, key) {
        if (!key || key === 'all') return tasks.slice();
        return tasks.filter(function (task) {
            return _normalizeTaskStatus(task.status) === key;
        });
    }

    function _filterTasksForOpsMode(tasks, tableMode) {
        var typeMap = {
            reply: ['interact'],
            publish: ['publish'],
            collector: ['scrape'],
            interaction: ['interact'],
            calendar: ['publish', 'interact', 'scrape', 'report', 'maintenance'],
            generic: ['publish', 'interact', 'scrape', 'report', 'maintenance'],
        };
        var allowed = typeMap[tableMode] || typeMap.generic;
        return (tasks || []).filter(function (task) {
            return allowed.indexOf(String(task.task_type || '').toLowerCase()) !== -1;
        });
    }

    function _taskDraftForOpsRoute(config, accounts) {
        var interactionDraftByRoute = {
            'auto-like': { title: '自动点赞规则', task_type: 'interact', priority: 'medium', result_summary: '来源页面：自动点赞' },
            'auto-comment': { title: '自动评论规则', task_type: 'interact', priority: 'high', result_summary: '来源页面：自动评论' },
            'auto-message': { title: '自动私信计划', task_type: 'interact', priority: 'high', result_summary: '来源页面：自动私信' },
        };
        var drafts = {
            reply: { title: '自动回复策略', task_type: 'interact', priority: 'high', result_summary: '来源页面：自动回复' },
            publish: { title: '定时发布计划', task_type: 'publish', priority: 'high', result_summary: '来源页面：定时发布' },
            collector: { title: '数据采集任务', task_type: 'scrape', priority: 'high', result_summary: '来源页面：数据采集助手' },
            interaction: interactionDraftByRoute[config.routeKey] || { title: '互动自动化任务', task_type: 'interact', priority: 'medium', result_summary: '来源页面：互动自动化' },
            calendar: { title: '任务调度计划', task_type: 'maintenance', priority: 'medium', result_summary: '来源页面：任务调度' },
            generic: { title: '自动化任务', task_type: 'report', priority: 'medium', result_summary: '来源页面：自动化工作台' },
        };
        var draft = drafts[config.tableMode] || drafts.generic;
        return {
            title: draft.title,
            task_type: draft.task_type,
            priority: draft.priority,
            result_summary: draft.result_summary,
            account_id: accounts[0] ? accounts[0].id : '',
        };
    }

    function _taskTabKey(text) {
        var value = String(text || '');
        if (value.indexOf('运行') !== -1) return 'running';
        if (value.indexOf('暂停') !== -1) return 'paused';
        if (value.indexOf('失败') !== -1 || value.indexOf('异常') !== -1) return 'failed';
        if (value.indexOf('完成') !== -1) return 'completed';
        if (value.indexOf('等待') !== -1 || value.indexOf('排队') !== -1) return 'pending';
        return 'all';
    }

    function _taskTabLabel(key) {
        var labels = {
            all: '全部',
            running: '运行中',
            paused: '暂停',
            failed: '失败',
            completed: '已完成',
            pending: '待执行',
        };
        return labels[key] || '全部';
    }

    function _kanbanStatusByTitle(title, index, config) {
        var value = String(title || '');
        if (value.indexOf('待') !== -1) return 'pending';
        if (value.indexOf('运行') !== -1 || value.indexOf('进行') !== -1) return 'running';
        if (value.indexOf('异常') !== -1 || value.indexOf('失败') !== -1) return 'failed';
        if (value.indexOf('完成') !== -1) return 'completed';
        if (config.tableMode === 'calendar') return index === 0 ? 'pending' : index === 1 ? 'running' : 'completed';
        return index === 0 ? 'pending' : index === 1 ? 'running' : 'completed';
    }

    function _taskTicketHtml(task) {
        return '<article class="ticket-card"><strong>' + _esc(task.title || _taskTypeLabel(task.task_type)) + '</strong><div class="subtle">'
            + _esc(_taskTime(task) + ' · ' + _taskStatusLabel(task.status)) + '</div></article>';
    }

    function _rewireElements(selector, binder) {
        document.querySelectorAll(selector).forEach(function (node) {
            var clone = node.cloneNode(true);
            node.parentNode.replaceChild(clone, node);
            binder(clone);
        });
    }
})();
