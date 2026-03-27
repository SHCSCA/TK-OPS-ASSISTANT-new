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

    var deviceEnvironment = window.__deviceEnvironmentHelpers;
    if (!deviceEnvironment) {
        throw new Error('device environment helpers not loaded');
    }

    var _wireHeaderPrimary = shared.wireHeaderPrimary;
    var _bindBatchBar = shared.bindBatchBar;
    var _batchDelete = shared.batchDelete;
    var _buildDeviceViewModel = shared.buildDeviceViewModel;
    var _deviceBool = shared.deviceBool;
    var _esc = shared.esc;
    var _formatNum = shared.formatNum;
    var _formatRelativeDate = shared.formatRelativeDate;
    var _runDeviceRepair = deviceEnvironment.runDeviceRepair;
    var _openDeviceEnvironment = deviceEnvironment.openDeviceEnvironment;
    var _exportDeviceLog = deviceEnvironment.exportDeviceLog;

    function _renderDeviceFilterTabs(models) {
        var counts = { all: (models || []).length, healthy: 0, warning: 0, error: 0, idle: 0 };
        (models || []).forEach(function (item) {
            var key = String(item.status || '').toLowerCase();
            if (counts[key] !== undefined) counts[key] += 1;
        });
        document.querySelectorAll('#mainHost [data-filter-group="device-status"] .local-tab').forEach(function (tab) {
            var key = tab.dataset.filterValue || 'all';
            var labels = {
                all: '全部',
                healthy: '正常',
                warning: '告警',
                error: '异常',
                idle: '空闲',
            }
            tab.textContent = (labels[key] || '全部') + ' (' + (counts[key] || 0) + ')';
        });
    }

    function _renderDeviceMetrics(models, accounts) {
        var statCards = document.querySelectorAll('#mainHost .stat-card');
        if (statCards.length < 4) return;
        var totalAccounts = (accounts || []).length;
        var isolatedAccounts = (accounts || []).filter(function (account) { return _deviceBool(account.isolation_enabled) && account.device_id; }).length;
        var abnormalDevices = (models || []).filter(function (item) { return item.status === 'error' || item.status === 'warning'; }).length;
        var idleDevices = (models || []).filter(function (item) { return item.status === 'idle'; }).length;
        var values = [
            _formatNum((models || []).length),
            _safePercent(isolatedAccounts, totalAccounts),
            _formatNum(abnormalDevices),
            _formatNum(idleDevices),
        ];
        statCards.forEach(function (card, index) {
            var valueEl = card.querySelector('.stat-card__value');
            if (valueEl) valueEl.textContent = values[index] || '--';
        });
    }

    function _renderDeviceBanner(models) {
        var banner = document.querySelector('#mainHost [data-device-banner]');
        if (!banner) return;
        var abnormal = (models || []).filter(function (item) { return item.status === 'error'; });
        var warning = (models || []).filter(function (item) { return item.status === 'warning'; });
        var summary = abnormal.length ? ('当前有 ' + abnormal.length + ' 台异常设备待处理') : (warning.length ? ('当前有 ' + warning.length + ' 台告警设备待复核') : '当前设备环境整体稳定');
        var detail = abnormal.length || warning.length
            ? (abnormal.length
                ? ('优先处理：' + abnormal.slice(0, 2).map(function (item) { return item.name; }).join('、') + (warning.length ? ('；其次复核 ' + warning.slice(0, 2).map(function (item) { return item.name; }).join('、')) : ''))
                : ('优先复核：' + warning.slice(0, 2).map(function (item) { return item.name; }).join('、')))
            : '所有设备已按真实代理、指纹与绑定关系完成归类，可继续做环境调度。';
        banner.innerHTML = '<div><strong>' + _esc(summary) + '</strong><div>' + _esc(detail) + '</div></div><div class="toolbar__group"><button class="primary-button js-device-banner-repair" type="button">批量修复</button><button class="ghost-button js-device-banner-focus" type="button">查看详情</button></div>';
    }

    function _renderDeviceGrid(models) {
        var grid = document.querySelector('#mainHost .device-env-grid');
        if (!grid) return;
        if (!(models || []).length) {
            grid.innerHTML = '<div class="empty-state" style="padding:48px;text-align:center;grid-column:1/-1;"><p>暂无设备</p><p class="subtle">点击「新增设备环境」添加第一台设备</p></div>';
            return;
        }
        grid.innerHTML = (models || []).map(function (item) {
            return '<article class="device-env-card device-env-card--' + _esc(item.status) + '" data-id="' + (item.id || '') + '" data-status="' + _esc(item.status) + '" data-search="' + _esc(item.searchText) + '">'
                + '<div class="device-env-card__head"><label class="batch-check-wrap"><input type="checkbox" class="batch-check js-batch-device" data-id="' + (item.id || '') + '" aria-label="选择设备 ' + _esc(item.name) + '"><span></span></label><strong>' + _esc(item.name) + '</strong><span class="status-chip ' + item.statusMeta.tone + '">' + _esc(item.statusMeta.label) + '</span></div>'
                + '<div class="device-env-card__meta">'
                + '<div class="list-row"><span class="subtle">设备编码</span><strong class="mono">' + _esc(item.deviceCode) + '</strong></div>'
                + '<div class="list-row"><span class="subtle">代理 IP</span><strong class="mono">' + _esc(item.proxyLabel) + '</strong></div>'
                + '<div class="list-row"><span class="subtle">地区</span><strong>' + _esc(item.regionLabel) + '</strong></div>'
                + '<div class="list-row"><span class="subtle">绑定账号</span><strong>' + _esc(_formatNum(item.boundCount)) + ' 个</strong></div>'
                + '<div class="list-row"><span class="subtle">隔离覆盖</span><strong>' + _esc(item.coveragePercent + '%') + '</strong></div>'
                + '<div class="list-row"><span class="subtle">最近巡检</span><strong>' + _esc(item.lastInspectionLabel) + '</strong></div>'
                + '</div>'
                + '<div class="detail-actions">'
                + '<button class="secondary-button js-view-device" data-id="' + (item.id || '') + '" type="button">查看详情</button>'
                + '<button class="ghost-button js-edit-device" data-id="' + (item.id || '') + '" type="button">编辑</button>'
                + '</div></article>';
        }).join('');
    }

    function _renderDeviceBindingTable(models) {
        var tbody = document.querySelector('#mainHost [data-device-binding-body]');
        if (!tbody) return;
        if (!(models || []).length) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:32px;">暂无绑定数据</td></tr>';
            return;
        }
        tbody.innerHTML = models.map(function (item) {
            var accountsMarkup = item.boundAccounts.length
                ? item.boundAccounts.map(function (account) {
                    var tone = _deviceBool(account.isolation_enabled) ? 'success' : 'warning';
                    return '<span class="tag ' + tone + '">' + _esc(account.username || ('账号#' + account.id)) + '</span>';
                }).join(' ')
                : '<span class="subtle">暂无绑定账号</span>';
            return '<tr class="route-row js-device-binding-row" data-id="' + (item.id || '') + '" data-search="' + _esc(item.searchText) + '">'
                + '<td class="mono"><strong>' + _esc(item.deviceCode) + '</strong></td>'
                + '<td>' + accountsMarkup + '</td>'
                + '<td>' + _esc(item.coveragePercent + '% / 已隔离 ' + item.isolatedCount + ' 个') + '</td>'
                + '<td><span class="status-chip ' + item.statusMeta.tone + '">' + _esc(item.statusMeta.label) + '</span></td>'
                + '<td><button class="ghost-button js-adjust-device-binding" data-id="' + (item.id || '') + '" type="button">调整绑定</button></td>'
                + '</tr>';
        }).join('');
    }

    function _renderDeviceCoverage(models, accounts) {
        var panel = document.querySelector('#mainHost [data-device-coverage-panel]');
        if (!panel) return;
        var boundAccounts = (accounts || []).filter(function (account) { return account.device_id; });
        var isolatedAccounts = boundAccounts.filter(function (account) { return _deviceBool(account.isolation_enabled); });
        var uncoveredAccounts = (accounts || []).filter(function (account) { return !account.device_id || !_deviceBool(account.isolation_enabled); });
        var fill = panel.querySelector('.coverage-fill');
        if (fill) fill.style.width = _safePercent(isolatedAccounts.length, (accounts || []).length);
        var labels = panel.querySelectorAll('.coverage-labels span');
        if (labels.length >= 2) {
            labels[0].textContent = '已隔离 ' + _formatNum(isolatedAccounts.length) + ' 个账号';
            labels[1].textContent = '未覆盖 ' + _formatNum(uncoveredAccounts.length) + ' 个账号';
        }
        var summary = panel.querySelector('.device-pool-summary');
        if (!summary) return;
        var idleDevices = (models || []).filter(function (item) { return item.status === 'idle'; });
        var riskyAccounts = uncoveredAccounts.slice(0, 3).map(function (account) { return account.username || ('账号#' + account.id); }).join('、') || '暂无';
        summary.innerHTML = ''
            + '<div class="task-item is-selected"><div><strong>未覆盖账号</strong><div class="subtle">' + _esc(riskyAccounts) + '</div></div><span class="pill warning">' + _esc(_safePercent(isolatedAccounts.length, (accounts || []).length)) + '</span></div>'
            + '<div class="task-item"><div><strong>空闲设备池</strong><div class="subtle">当前有 ' + _esc(_formatNum(idleDevices.length)) + ' 台空闲设备可分配</div></div><span class="pill info">调度</span></div>';
    }

    function _renderDeviceLogPanel(logs, deviceId) {
        var limit = 12;
        var total = Array.isArray(logs) ? logs.length : 0;
        var expanded = Boolean(uiState['device-management'] && String(uiState['device-management'].expandedLogDeviceId || '') === String(deviceId || ''));
        var visibleLogs = expanded ? (logs || []) : (logs || []).slice(0, limit);
        if (!logs || !logs.length) {
            return '<section class="panel"><div class="panel__header"><div><strong>环境日志</strong><div class="subtle">当前设备还没有环境动作记录</div></div></div><div class="audit-list"><div class="audit-item"><div><strong>暂无日志</strong><div class="subtle audit-item__copy">执行打开环境、巡检或修复后，会在这里展示设备级日志详情。</div></div><span class="pill info">空</span></div></div></section>';
        }
        return '<section class="panel device-log-panel"><div class="panel__header"><div><strong>环境日志</strong><div class="subtle">当前设备最近 ' + _esc(String(total)) + ' 条动作记录</div></div>'
            + (total > limit ? '<div class="device-log-panel__header-actions"><button class="ghost-button js-device-toggle-logs" data-id="' + _esc(String(deviceId || '')) + '" type="button">' + (expanded ? '收起较早日志' : '展开全部 ' + total + ' 条') + '</button></div>' : '')
            + '</div><div class="audit-list device-log-list' + (expanded ? ' is-expanded' : '') + '">'
            + visibleLogs.map(function (entry) {
                var tone = String(entry.category || '').indexOf('repair') >= 0 ? 'success' : (String(entry.category || '').indexOf('inspection') >= 0 ? 'warning' : 'info');
                return '<div class="audit-item device-log-item"><div class="device-log-item__body"><strong>' + _esc(entry.title || '设备日志') + '</strong><div class="subtle audit-item__copy device-log-item__message">' + _esc(entry.message || '系统记录已同步') + '</div><div class="subtle device-log-item__meta">' + _esc(_formatRelativeDate(entry.created_at)) + '</div></div><span class="pill ' + tone + '">' + _esc(entry.category || 'log') + '</span></div>';
            }).join('')
            + (!expanded && total > limit ? '<div class="audit-item device-log-item device-log-item--summary"><div class="device-log-item__body"><strong>还有 ' + _esc(String(total - limit)) + ' 条较早日志</strong><div class="subtle audit-item__copy device-log-item__message">默认只展示最新 ' + limit + ' 条，避免右侧详情区被超长日志撑满。点击上方按钮可展开完整记录。</div></div><span class="pill info">折叠</span></div>' : '')
            + '</div></section>';
    }

    function _renderDeviceDetail(deviceModel, logs) {
        var detailHost = document.getElementById('detailHost');
        if (!detailHost) return;
        if (!deviceModel) {
            detailHost.innerHTML = '<div class="detail-root"><section class="panel"><div class="panel__header"><div><strong>设备详情</strong><div class="subtle">请先在左侧选择设备</div></div><span class="status-chip info">待选择</span></div></section></div>';
            return;
        }
        var issueMarkup = deviceModel.issues.length
            ? deviceModel.issues.map(function (issue) {
                return '<div class="audit-item"><div><strong>' + _esc(issue.title) + '</strong><div class="subtle audit-item__copy">' + _esc(issue.copy) + '</div></div><span class="pill ' + _esc(issue.tone) + '">' + _esc(issue.tone === 'error' ? '阻塞' : issue.tone === 'warning' ? '待处理' : '提示') + '</span></div>';
            }).join('')
            : '<div class="audit-item"><div><strong>当前设备状态正常</strong><div class="subtle audit-item__copy">代理、指纹和绑定账号状态均未发现明显阻塞。</div></div><span class="pill success">正常</span></div>';
        detailHost.innerHTML = '<div class="detail-root">'
            + '<section class="panel"><div class="panel__header"><div><strong>' + _esc(deviceModel.name) + '</strong><div class="subtle mono">' + _esc(deviceModel.deviceCode) + '</div></div><span class="status-chip ' + deviceModel.statusMeta.tone + '">' + _esc(deviceModel.statusMeta.label) + '</span></div>'
            + '<div class="detail-list">'
            + '<div class="detail-item"><span class="subtle">代理地址</span><strong class="mono">' + _esc(deviceModel.proxyLabel) + '</strong></div>'
            + '<div class="detail-item"><span class="subtle">代理状态</span><strong>' + _esc(deviceModel.proxyStatusLabel) + '</strong></div>'
            + '<div class="detail-item"><span class="subtle">地区</span><strong>' + _esc(deviceModel.regionLabel) + '</strong></div>'
            + '<div class="detail-item"><span class="subtle">指纹状态</span><strong>' + _esc(deviceModel.fingerprintLabel) + '</strong></div>'
            + '<div class="detail-item"><span class="subtle">绑定账号</span><strong>' + _esc(_formatNum(deviceModel.boundCount)) + ' 个</strong></div>'
            + '<div class="detail-item"><span class="subtle">隔离覆盖</span><strong>' + _esc(deviceModel.coveragePercent + '%') + '</strong></div>'
            + '<div class="detail-item"><span class="subtle">最近巡检</span><strong>' + _esc(deviceModel.lastInspectionLabel) + '</strong></div>'
            + '</div>'
            + '<div class="detail-actions account-detail__actions">'
            + '<button class="primary-button js-device-open-environment" data-id="' + deviceModel.id + '" type="button">打开环境</button>'
            + '<button class="secondary-button js-adjust-device-binding" data-id="' + deviceModel.id + '" type="button">修改绑定</button>'
            + '<button class="secondary-button js-device-repair" data-id="' + deviceModel.id + '" type="button">修复环境</button>'
            + '<button class="ghost-button js-device-export-log" data-id="' + deviceModel.id + '" type="button">环境日志</button>'
            + '<button class="ghost-button js-edit-device" data-id="' + deviceModel.id + '" type="button">编辑设备</button>'
            + '<button class="danger-button js-delete-device" data-id="' + deviceModel.id + '" type="button">删除设备</button>'
            + '</div></section>'
            + '<section class="panel"><div class="panel__header"><div><strong>巡检结果</strong><div class="subtle">根据真实代理、指纹、账号绑定与登录态汇总</div></div></div><div class="audit-list">' + issueMarkup + '</div></section>'
            + _renderDeviceLogPanel(Array.isArray(logs) ? logs : (deviceModel.logs || []), deviceModel.id)
            + '</div>';
        _bindDeviceDetailActions(window.__devicePageData || []);
    }

    function _selectDeviceCard(deviceId, models) {
        var selectedId = String(deviceId || '');
        document.querySelectorAll('#mainHost .device-env-card').forEach(function (node) {
            node.classList.toggle('is-selected', String(node.dataset.id || '') === selectedId);
        });
        var deviceModel = (models || []).find(function (item) { return String(item.id || '') === selectedId; }) || null;
        if (uiState['device-management']) uiState['device-management'].selectedId = deviceModel ? deviceModel.id : null;
        _renderDeviceDetail(deviceModel);
    }

    function _bindDeviceFilterControls() {
        document.querySelectorAll('#mainHost [data-filter-group="device-status"] .local-tab').forEach(function (tab) {
            tab.addEventListener('click', function () {
                document.querySelectorAll('#mainHost [data-filter-group="device-status"] .local-tab').forEach(function (node) {
                    node.classList.remove('is-active');
                });
                tab.classList.add('is-active');
                uiState['device-management'] = uiState['device-management'] || { statusFilter: 'all', view: 'card', selectedId: null };
                uiState['device-management'].statusFilter = tab.dataset.filterValue || 'all';
                applyCurrentRouteState();
            });
        });
        document.querySelectorAll('#mainHost [data-view-toggle="devices"] button').forEach(function (btn) {
            btn.addEventListener('click', function () {
                document.querySelectorAll('#mainHost [data-view-toggle="devices"] button').forEach(function (node) {
                    node.classList.remove('is-active');
                });
                btn.classList.add('is-active');
                uiState['device-management'] = uiState['device-management'] || { statusFilter: 'all', view: 'card', selectedId: null };
                uiState['device-management'].view = btn.dataset.view || 'card';
                var grid = document.querySelector('#mainHost .device-env-grid');
                if (grid) grid.classList.toggle('list-mode', uiState['device-management'].view === 'list');
            });
        });
        var grid = document.querySelector('#mainHost .device-env-grid');
        if (grid && uiState['device-management']) {
            grid.classList.toggle('list-mode', uiState['device-management'].view === 'list');
        }
        document.querySelectorAll('#mainHost [data-view-toggle="devices"] button').forEach(function (btn) {
            btn.classList.toggle('is-active', (uiState['device-management'] && uiState['device-management'].view || 'card') === (btn.dataset.view || 'card'));
        });
    }

    function _bindDeviceBannerActions(models) {
        var banner = document.querySelector('#mainHost [data-device-banner]');
        if (!banner) return;
        var firstProblem = (models || []).find(function (item) { return item.status === 'error' || item.status === 'warning'; }) || (models || [])[0] || null;
        var repairBtn = banner.querySelector('.js-device-banner-repair');
        var focusBtn = banner.querySelector('.js-device-banner-focus');
        if (repairBtn) {
            repairBtn.addEventListener('click', function () {
                _runDeviceRepair(firstProblem ? [firstProblem.id] : null);
            });
        }
        if (focusBtn) {
            focusBtn.addEventListener('click', function () {
                if (firstProblem) {
                    _selectDeviceCard(firstProblem.id, models || []);
                }
            });
        }
    }

    function _bindDeviceDetailActions(models) {
        var detailHost = document.getElementById('detailHost');
        if (!detailHost) return;
        detailHost.querySelectorAll('.js-adjust-device-binding').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                if (typeof _openDeviceBindingModal === 'function') _openDeviceBindingModal(btn);
            });
        });
        detailHost.querySelectorAll('.js-device-repair').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                _runDeviceRepair([parseInt(btn.dataset.id, 10)]);
            });
        });
        detailHost.querySelectorAll('.js-device-open-environment').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                _openDeviceEnvironment(parseInt(btn.dataset.id, 10) || null);
            });
        });
        detailHost.querySelectorAll('.js-device-export-log').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                _exportDeviceLog(parseInt(btn.dataset.id, 10));
            });
        });
        detailHost.querySelectorAll('.js-device-toggle-logs').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var id = parseInt(btn.dataset.id, 10);
                var state = uiState['device-management'] || (uiState['device-management'] = { statusFilter: 'all', view: 'card', selectedId: null });
                state.expandedLogDeviceId = String(state.expandedLogDeviceId || '') === String(id || '') ? null : id;
                _exportDeviceLog(id, { silent: true });
            });
        });
        detailHost.querySelectorAll('.js-edit-device').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var target = (models || []).find(function (item) { return String(item.id || '') === String(btn.dataset.id || ''); });
                if (target) openDeviceForm(target.raw);
            });
        });
        detailHost.querySelectorAll('.js-delete-device').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var id = parseInt(btn.dataset.id, 10);
                if (!id) return;
                confirmModal({
                    title: '删除设备',
                    message: '确定删除此设备？绑定的账号关系将同时解除。',
                    confirmText: '删除',
                    tone: 'danger',
                }).then(function (ok) {
                    if (!ok) return;
                    api.devices.remove(id).then(function () {
                        showToast('设备已删除', 'success');
                        loaders['device-management']();
                    }).catch(function (err) {
                        showToast('删除失败: ' + ((err && err.message) || '未知错误'), 'error');
                    });
                });
            });
        });
    }

    function _bindDeviceActions(models) {
        document.querySelectorAll('#mainHost .device-env-card').forEach(function (card) {
            card.addEventListener('click', function (e) {
                if (e.target.closest('button') || e.target.closest('input')) return;
                _selectDeviceCard(card.dataset.id, models || []);
            });
        });
        document.querySelectorAll('.js-view-device, .js-device-binding-row').forEach(function (node) {
            node.addEventListener('click', function (e) {
                if (e.target.closest('button') && !e.target.classList.contains('js-view-device')) return;
                _selectDeviceCard(node.dataset.id, models || []);
            });
        });
        document.querySelectorAll('.js-edit-device').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var target = (models || []).find(function (item) { return String(item.id || '') === String(btn.dataset.id || ''); });
                if (target) openDeviceForm(target.raw);
            });
        });
        document.querySelectorAll('.js-delete-device').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var id = parseInt(btn.dataset.id, 10);
                if (!id) return;
                confirmModal({
                    title: '删除设备',
                    message: '确定删除此设备？绑定的账号关系将同时解除。',
                    confirmText: '删除',
                    tone: 'danger',
                }).then(function (ok) {
                    if (!ok) return;
                    api.devices.remove(id).then(function () {
                        showToast('设备已删除', 'success');
                        loaders['device-management']();
                    }).catch(function (err) {
                        showToast('删除失败: ' + ((err && err.message) || '未知错误'), 'error');
                    });
                });
            });
        });
        document.querySelectorAll('.js-adjust-device-binding').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                if (typeof _openDeviceBindingModal === 'function') _openDeviceBindingModal(btn);
            });
        });
        document.querySelectorAll('.js-device-repair').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                _runDeviceRepair([parseInt(btn.dataset.id, 10)]);
            });
        });
        document.querySelectorAll('.js-device-open-environment').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                _openDeviceEnvironment(parseInt(btn.dataset.id, 10) || null);
            });
        });
        document.querySelectorAll('.js-device-export-log').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                _exportDeviceLog(parseInt(btn.dataset.id, 10));
            });
        });
    }

    loaders['device-management'] = function () {
        _wireHeaderPrimary(function () { openDeviceForm(); });

        Promise.all([
            api.devices.list(),
            api.accounts.list(),
        ]).then(function (results) {
            var devices = results[0] || [];
            var accounts = results[1] || [];
            var models = (devices || []).map(function (device) {
                return _buildDeviceViewModel(device, accounts || []);
            }).sort(function (left, right) {
                if (left.sortOrder !== right.sortOrder) return left.sortOrder - right.sortOrder;
                return String(left.name || '').localeCompare(String(right.name || ''), 'zh-CN');
            });

            window.__devicePageData = models;
            window.__devicePageAccounts = accounts || [];

            runtimeSummaryHandlers['device-management']({ devices: devices, accounts: accounts });
            _renderDeviceMetrics(models, accounts || []);
            _renderDeviceFilterTabs(models);
            _renderDeviceBanner(models);
            _renderDeviceGrid(models);
            _renderDeviceBindingTable(models);
            _renderDeviceCoverage(models, accounts || []);
            _bindDeviceActions(models);
            _bindDeviceFilterControls();
            _bindDeviceBannerActions(models);

            var preferredDeviceId = uiState['device-management'] && uiState['device-management'].selectedId ? String(uiState['device-management'].selectedId) : '';
            var selected = models.find(function (item) { return String(item.id || '') === preferredDeviceId; }) || models[0] || null;
            if (selected) {
                _selectDeviceCard(selected.id, models);
            } else {
                _renderDeviceDetail(null);
            }

            _bindBatchBar('.js-batch-device', function (ids) {
                return _batchDelete(ids, api.devices.remove, '设备', 'device-management');
            });
            applyCurrentRouteState();
        }).catch(function (error) {
            window.__devicePageData = [];
            window.__devicePageAccounts = [];
            console.warn('[page-loaders] device-management load failed:', error);
        });
    };

    window.__deviceManagementPageMain = {
        renderDeviceDetail: _renderDeviceDetail,
        selectDeviceCard: _selectDeviceCard,
    };
})();