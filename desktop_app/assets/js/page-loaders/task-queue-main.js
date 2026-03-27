(function () {
    'use strict';

    var shared = window.__pageLoaderShared;
    if (!shared) {
        throw new Error('page loader shared helpers not loaded');
    }

    var loaders = window._pageLoaders;
    var runtimeSummaryHandlers = window.__runtimeSummaryHandlers;
    if (!loaders || !runtimeSummaryHandlers) {
        throw new Error('page loader registries not loaded');
    }

    var _wireHeaderPrimary = shared.wireHeaderPrimary;
    var _bindBatchBar = shared.bindBatchBar;
    var _batchDelete = shared.batchDelete;
    var _esc = shared.esc;

    function _taskStatusTone(status) {
        var value = (status || '').toLowerCase();
        if (value === 'running') return 'info';
        if (value === 'completed') return 'success';
        if (value === 'pending') return 'warning';
        if (value === 'failed') return 'error';
        return 'info';
    }

    function _taskStatusLabel(status) {
        var map = { running: '运行中', completed: '已完成', pending: '排队中', failed: '失败', paused: '已暂停' };
        return map[(status || '').toLowerCase()] || status || '未知';
    }

    function _taskAction(task) {
        var status = (task.status || '').toLowerCase();
        var id = task.id || '';
        if (status === 'pending') return '<button class="ghost-button js-start-task" data-id="' + id + '">启动</button>';
        if (status === 'running') return '<button class="ghost-button js-complete-task" data-id="' + id + '">完成</button>';
        if (status === 'completed') return '<span class="subtle">已完成</span>';
        if (status === 'failed') return '<button class="ghost-button js-start-task" data-id="' + id + '">重试</button>'
            + '<button class="ghost-button js-delete-task" data-id="' + id + '">删除</button>';
        return '<button class="ghost-button js-delete-task" data-id="' + id + '">删除</button>';
    }

    function _renderTaskDetail(task) {
        if (!task) return;
        var detailHost = document.getElementById('detailHost');
        if (!detailHost) return;
        detailHost.innerHTML = '<div class="detail-root"><section class="panel"><div class="panel__header"><div><strong>' + _esc(task.title || '任务详情') + '</strong><div class="subtle">' + _esc(task.task_type || '-') + '</div></div><span class="status-chip ' + _taskStatusTone(task.status) + '">' + _esc(_taskStatusLabel(task.status)) + '</span></div><div class="detail-list"><div class="detail-item"><span class="subtle">优先级</span><strong>' + _esc(task.priority || '-') + '</strong></div><div class="detail-item"><span class="subtle">关联账号</span><strong>' + _esc(task.account_id || '-') + '</strong></div><div class="detail-item"><span class="subtle">结果摘要</span><strong>' + _esc(task.result_summary || '无') + '</strong></div></div></section></div>';
    }

    function _syncTaskQueueFilterTabs(activeFilter) {
        document.querySelectorAll('#mainHost [data-filter-group="tasks-status"] .local-tab').forEach(function (tab) {
            tab.classList.toggle('is-active', (tab.dataset.filterValue || 'all') === (activeFilter || 'all'));
        });
    }

    function _bindTaskQueueFilterTabs() {
        document.querySelectorAll('#mainHost [data-filter-group="tasks-status"] .local-tab').forEach(function (tab) {
            if (tab.dataset.taskQueueTabBound === '1') return;
            tab.dataset.taskQueueTabBound = '1';
            tab.addEventListener('click', function () {
                uiState['task-queue'] = uiState['task-queue'] || { statusFilter: 'all' };
                uiState['task-queue'].statusFilter = tab.dataset.filterValue || 'all';
                _syncTaskQueueFilterTabs(uiState['task-queue'].statusFilter);
                if (typeof applyCurrentRouteState === 'function') applyCurrentRouteState();
            });
        });
    }

    function _bindTaskActions(tasks) {
        document.querySelectorAll('.js-start-task').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                api.tasks.start(id).then(function () {
                    showToast('任务已启动');
                    loaders['task-queue']();
                });
            });
        });
        document.querySelectorAll('.js-complete-task').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                api.tasks.complete(id).then(function () {
                    showToast('任务已完成');
                    loaders['task-queue']();
                });
            });
        });
        document.querySelectorAll('.js-edit-task').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                var task = (tasks || []).find(function (item) { return item.id === id; });
                if (task) openTaskForm(task);
                if (task) _renderTaskDetail(task);
            });
        });
        document.querySelectorAll('.js-delete-task').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                confirmModal({
                    title: '删除任务',
                    message: '确定删除此任务？此操作不可恢复。',
                    confirmText: '删除',
                    tone: 'danger',
                }).then(function (ok) {
                    if (!ok) return;
                    api.tasks.remove(id).then(function () {
                        showToast('任务已删除');
                        loaders['task-queue']();
                    });
                });
            });
        });
    }

    loaders['task-queue'] = function () {
        _wireHeaderPrimary(function () { openTaskForm(); });
        uiState['task-queue'] = uiState['task-queue'] || { statusFilter: 'all' };

        api.tasks.list().then(function (tasks) {
            tasks = tasks || [];
            runtimeSummaryHandlers['task-queue']({ tasks: tasks });

            var counts = { all: tasks.length, running: 0, completed: 0, pending: 0, failed: 0 };
            tasks.forEach(function (task) {
                var status = (task.status || '').toLowerCase();
                if (status === 'running') counts.running++;
                else if (status === 'completed') counts.completed++;
                else if (status === 'pending') counts.pending++;
                else if (status === 'failed') counts.failed++;
            });
            var tabs = document.querySelectorAll('#mainHost .local-tab');
            if (tabs.length >= 5) {
                tabs[0].textContent = '全部任务 (' + counts.all + ')';
                tabs[0].dataset.filterValue = 'all';
                tabs[1].textContent = '进行中 (' + counts.running + ')';
                tabs[1].dataset.filterValue = 'running';
                tabs[2].textContent = '已完成 (' + counts.completed + ')';
                tabs[2].dataset.filterValue = 'completed';
                tabs[3].textContent = '排队中 (' + counts.pending + ')';
                tabs[3].dataset.filterValue = 'pending';
                tabs[4].textContent = '异常 (' + counts.failed + ')';
                tabs[4].dataset.filterValue = 'failed';
            }

            var tbody = document.querySelector('#mainHost .table-wrapper tbody');
            if (!tbody) return;
            if (tasks.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:32px;">暂无任务数据</td></tr>';
                return;
            }
            tbody.innerHTML = tasks.map(function (task) {
                var statusClass = _taskStatusTone(task.status);
                var statusLabel = _taskStatusLabel(task.status);
                return '<tr class="route-row" data-id="' + (task.id || '') + '" data-status="' + _esc((task.status || '').toLowerCase()) + '" data-search="' + _esc((task.title || '') + ' ' + (task.task_type || '') + ' ' + (task.status || '') + ' ' + (task.priority || '') + ' ' + (task.result_summary || '')) + '">'
                    + '<td><input type="checkbox" class="batch-check js-batch-task" data-id="' + (task.id || '') + '"></td>'
                    + '<td><strong>' + _esc(task.title || '') + '</strong></td>'
                    + '<td>' + _esc(task.task_type || '-') + '</td>'
                    + '<td><span class="status-chip ' + statusClass + '">' + statusLabel + '</span></td>'
                    + '<td>' + _esc(task.priority || '-') + '</td>'
                    + '<td class="subtle">' + _esc(task.created_at || '-') + '</td>'
                    + '<td>' + _taskAction(task) + '</td>'
                    + '<td><button class="ghost-button js-edit-task" data-id="' + (task.id || '') + '">编辑</button></td>'
                    + '</tr>';
            }).join('');

            _bindTaskActions(tasks);
            _bindTaskQueueFilterTabs();
            _syncTaskQueueFilterTabs(uiState['task-queue'].statusFilter || 'all');
            if (typeof applyCurrentRouteState === 'function') applyCurrentRouteState();
            _bindBatchBar('.js-batch-task', function (ids) {
                return _batchDelete(ids, api.tasks.remove, '任务', 'task-queue');
            });
            ensurePagination(tbody.closest('.table-card, .panel'), '共 ' + tasks.length + ' 条任务，当前第 1 页');
        }).catch(function (error) {
            console.warn('[page-loaders] task-queue load failed:', error);
        });
    };

    window.__taskQueuePageMain = {
        renderTaskDetail: _renderTaskDetail,
    };
})();