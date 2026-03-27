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
    var _buildAccountViewModel = shared.buildAccountViewModel;
    var _accountFilterStatus = shared.accountFilterStatus;
    var _accountSortOrder = shared.accountSortOrder;
    var _buildAccountSearchText = shared.buildAccountSearchText;
    var _buildAccountAdvice = shared.buildAccountAdvice;
    var _buildAccountDutySummary = shared.buildAccountDutySummary;
    var _splitAccountTags = shared.splitAccountTags;
    var _mergeAccountTags = shared.mergeAccountTags;
    var _esc = shared.esc;
    var _findAccountViewModel = shared.findAccountViewModel;
    var _openAccountEnvironment = shared.openAccountEnvironment;
    var _openAccountCookieModal = shared.openAccountCookieModal;
    var _openAccountProxyConfig = shared.openAccountProxyConfig;
    var _runAccountLoginValidation = shared.runAccountLoginValidation;
    var _runAccountConnectionTest = shared.runAccountConnectionTest;

    function _confirmDeleteAccount(accountId) {
        var id = parseInt(accountId, 10);
        if (!id) return;
        confirmModal({
            title: '删除账号',
            message: '确定要删除此账号？系统会自动解绑相关任务和素材引用，此操作不可恢复。',
            confirmText: '删除账号',
            tone: 'danger',
        }).then(function (ok) {
            if (!ok) return;
            api.accounts.remove(id).then(function () {
                showToast('账号已删除', 'success');
                if (uiState.account) uiState.account.selectedId = null;
                loaders['account']();
            }).catch(function (err) {
                showToast('删除失败: ' + (((err && err.message) || '未知错误')), 'error');
            });
        });
    }

    function _renderEmptyAccountDetail() {
        var detailHost = document.getElementById('detailHost');
        var template = document.getElementById('route-account-detail-default');
        if (!detailHost || !template) return;
        detailHost.innerHTML = template.innerHTML;
    }

    function _bindAccountDetailActions(accounts) {
        var detailHost = document.getElementById('detailHost');
        if (!detailHost) return;

        detailHost.querySelectorAll('.js-edit-account').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var acc = _findAccountViewModel(accounts, btn.dataset.id);
                if (acc) openAccountForm(acc);
            });
        });

        detailHost.querySelectorAll('.js-delete-account').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                _confirmDeleteAccount(btn.dataset.id);
            });
        });

        detailHost.querySelectorAll('.js-account-open-environment').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var acc = _findAccountViewModel(accounts, btn.dataset.id);
                if (acc) _openAccountEnvironment(acc);
            });
        });

        detailHost.querySelectorAll('.js-account-manage-cookies').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var acc = _findAccountViewModel(accounts, btn.dataset.id);
                if (acc) _openAccountCookieModal(acc);
            });
        });

        detailHost.querySelectorAll('.js-validate-account-login').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                _runAccountLoginValidation(btn.dataset.id, btn);
            });
        });

        detailHost.querySelectorAll('.js-test-account-connection').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                _runAccountConnectionTest(btn.dataset.id, btn);
            });
        });

        detailHost.querySelectorAll('.js-account-configure-proxy').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var acc = _findAccountViewModel(accounts, btn.dataset.id);
                if (acc) _openAccountProxyConfig(acc);
            });
        });

        detailHost.querySelectorAll('.js-account-rebind-validate').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var acc = _findAccountViewModel(accounts, btn.dataset.id);
                if (acc) _openAccountProxyConfig(acc, { quickValidate: true });
            });
        });
    }

    function _renderAccountDetail(account) {
        if (!account) {
            _renderEmptyAccountDetail();
            return;
        }
        var detailHost = document.getElementById('detailHost');
        if (!detailHost) return;
        var globalAdvice = _buildAccountAdvice(account);
        var dutySummary = _buildAccountDutySummary(account, globalAdvice);
        detailHost.innerHTML = '<div class="detail-root">'
            + '<section class="panel">'
            + '<div class="panel__header"><div><strong>' + _esc(account.username || '账号详情') + '</strong><div class="subtle mono">ID ' + _esc(account.id || '-') + '</div><div class="subtle">' + _esc(account.subtitle || '账号详情') + '</div></div><span class="status-chip ' + account.statusTone + '">' + _esc(account.statusLabel) + '</span></div>'
            + '<div class="detail-stack">'
            + '<div class="data-points">'
            + '<div class="data-point"><span class="subtle">Cookie 状态</span><strong>' + _esc(account.cookieLabel) + '</strong></div>'
            + '<div class="data-point"><span class="subtle">登录态校验</span><strong>' + _esc(account.loginCheckLabel) + '</strong></div>'
            + '<div class="data-point"><span class="subtle">隔离环境</span><strong>' + _esc(account.isolationLabel) + '</strong></div>'
            + '<div class="data-point"><span class="subtle">Cookie 更新</span><strong>' + _esc(account.cookieUpdatedLabel) + '</strong></div>'
            + '<div class="data-point"><span class="subtle">最近登录</span><strong>' + _esc(account.lastLoginLabel) + '</strong></div>'
            + '<div class="data-point"><span class="subtle">代理检测</span><strong>' + _esc(account.connectionLabel) + '</strong></div>'
            + '</div>'
            + '<div class="detail-list">'
            + '<div class="detail-item"><span class="subtle">平台 / 区域</span><strong>' + _esc(account.platformLabel + ' / ' + account.regionLabel) + '</strong></div>'
            + '<div class="detail-item detail-item--stacked"><span class="subtle">代理地址</span><strong class="mono account-detail__mono-break">' + _esc(account.proxyLabel) + '</strong></div>'
            + '<div class="detail-item"><span class="subtle">检测范围</span><strong>' + _esc(account.connectionScopeLabel) + '</strong></div>'
            + '<div class="detail-item"><span class="subtle">Cookie 内容</span><strong>' + _esc(account.cookieContentSummary) + '</strong></div>'
            + '<div class="detail-item detail-item--stacked"><span class="subtle">登录态说明</span><strong class="account-detail__message">' + _esc(account.loginCheckMessage) + '</strong></div>'
            + '<div class="detail-item"><span class="subtle">标签</span><strong>' + _esc(account.tags.length ? account.tags.join(' / ') : '未打标签') + '</strong></div>'
            + '<div class="detail-item"><span class="subtle">备注</span><strong>' + _esc(account.notes || '暂无备注') + '</strong></div>'
            + '</div>'
            + '<div class="detail-actions account-detail__actions">'
            + '<button class="primary-button js-account-open-environment" data-id="' + account.id + '" type="button">进入环境</button>'
            + '<button class="secondary-button js-account-manage-cookies" data-id="' + account.id + '" type="button">Cookie 状态</button>'
            + '<button class="secondary-button js-account-rebind-validate" data-id="' + account.id + '" type="button">重绑并校验</button>'
            + '<button class="secondary-button js-validate-account-login" data-id="' + account.id + '" type="button">校验登录态</button>'
            + '<button class="secondary-button js-test-account-connection" data-id="' + account.id + '" type="button">检测代理</button>'
            + '<button class="secondary-button js-account-configure-proxy" data-id="' + account.id + '" type="button">配置代理</button>'
            + '<button class="ghost-button js-edit-account" data-id="' + account.id + '" type="button">编辑账号</button>'
            + '<button class="danger-button js-delete-account" data-id="' + account.id + '" type="button">删除账号</button>'
            + '</div>'
            + '</div>'
            + '</section>'
            + '<section class="panel">'
            + '<div class="panel__header"><div><strong>' + _esc(dutySummary.title) + '</strong><div class="subtle">' + _esc(dutySummary.copy) + '</div></div><span class="status-chip ' + dutySummary.tone + '">' + _esc(dutySummary.badge) + '</span></div>'
            + '<div class="audit-list">'
            + globalAdvice.map(function (item) {
                return '<div class="audit-item"><div><strong>' + _esc(item.title) + '</strong><div class="subtle audit-item__copy">' + _esc(item.copy) + '</div></div><span class="pill ' + item.tone + '">' + _esc(item.badge) + '</span></div>';
            }).join('')
            + '</div>'
            + '</section>'
            + '</div>';
        _bindAccountDetailActions(window.__accountPageData || [account]);
    }

    function _renderAccountGrid(accounts) {
        var grid = document.querySelector('#mainHost .account-grid');
        if (!grid) return;
        if (!accounts.length) {
            grid.innerHTML = '<div class="empty-state" style="padding:48px;text-align:center;"><p>暂无账号数据</p><p class="subtle">点击右上角「新建账号」添加第一个账号</p></div>';
            return;
        }

        grid.innerHTML = accounts.map(function (account) {
            var tagMarkup = account.tags.slice(0, 3).map(function (tag) {
                return '<span class="pill info">' + _esc(tag) + '</span>';
            }).join('');
            return '<article class="account-card detail-trigger" data-id="' + (account.id || '') + '" data-detail-target="' + _esc(account.detailTarget) + '" data-status="' + _esc(_accountFilterStatus(account.status)) + '" data-order="' + _esc(_accountSortOrder(account.status)) + '" data-search="' + _esc(_buildAccountSearchText(account.raw, account.device, account.tags, { label: account.cookieLabel }, { label: account.connectionLabel })) + '">'
                + '<input type="checkbox" class="batch-check js-batch-account" data-id="' + (account.id || '') + '" aria-label="选择账号 ' + _esc(account.username || '') + '">'
                + '<div class="account-card__head"><div><strong>' + _esc(account.username || '') + '</strong><div class="subtle">' + _esc(account.subtitle || '') + '</div></div><span class="status-chip ' + account.statusTone + '">' + _esc(account.statusLabel) + '</span></div>'
                + '<div class="account-card__meta">'
                + '<div class="list-row"><span class="subtle">账号 ID</span><strong class="mono">' + (account.id || '-') + '</strong></div>'
                + '<div class="list-row"><span class="subtle">代理 IP</span><strong class="mono">' + _esc(account.proxyLabel) + '</strong></div>'
                + '<div class="list-row"><span class="subtle">上次登录</span><strong>' + _esc(account.lastLoginLabel) + '</strong></div>'
                + '<div class="list-row"><span class="subtle">Cookie 状态</span><span class="tag ' + account.cookieTone + '">' + _esc(account.cookieLabel) + '</span></div>'
                + '<div class="list-row"><span class="subtle">登录态校验</span><span class="tag ' + account.loginCheckTone + '">' + _esc(account.loginCheckLabel) + '</span></div>'
                + '<div class="list-row"><span class="subtle">标签</span><div class="account-card__tags">' + (tagMarkup || '<span class="subtle">未打标签</span>') + '</div></div>'
                + '</div>'
                + '<div class="detail-actions account-card__actions">'
                + '<button class="primary-button js-account-open-environment" data-id="' + (account.id || '') + '" type="button">进入环境</button>'
                + '<button class="secondary-button js-account-manage-cookies" data-id="' + (account.id || '') + '" type="button">Cookie 状态</button>'
                + '<button class="secondary-button js-account-rebind-validate" data-id="' + (account.id || '') + '" type="button">重绑并校验</button>'
                + '<button class="ghost-button js-view-account" data-id="' + (account.id || '') + '" type="button">查看详情与更多操作</button>'
                + '</div></article>';
        }).join('');
    }

    function _syncAccountControls() {
        if (!uiState.account) return;
        if (typeof uiState.account.batchMode === 'undefined') uiState.account.batchMode = false;

        document.querySelectorAll('#mainHost .js-account-status-tab').forEach(function (tab) {
            var active = (tab.dataset.filterValue || 'all') === uiState.account.statusFilter;
            tab.classList.toggle('is-active', active);
            tab.classList.toggle('is-selected', active);
        });
        document.querySelectorAll('#mainHost .js-account-view').forEach(function (btn) {
            var active = (btn.dataset.view || 'card') === uiState.account.view;
            btn.classList.toggle('is-active', active);
            btn.classList.toggle('is-selected', active);
        });

        var batchTagBtn = document.querySelector('#mainHost .js-account-tag-batch');
        if (batchTagBtn) {
            batchTagBtn.textContent = uiState.account.batchMode ? '为已选账号打标签' : '批量打标签';
            batchTagBtn.classList.toggle('is-active', uiState.account.batchMode);
        }

        var batchCancelBtn = document.querySelector('#mainHost .js-account-batch-cancel');
        if (batchCancelBtn) {
            batchCancelBtn.classList.toggle('shell-hidden', !uiState.account.batchMode);
        }

        var grid = document.querySelector('#mainHost .account-grid');
        if (grid) {
            grid.classList.toggle('is-batch-mode', Boolean(uiState.account.batchMode));
        }
    }

    function _updateAccountTabs(accounts) {
        var counts = { all: accounts.length, online: 0, offline: 0, exception: 0 };
        accounts.forEach(function (account) {
            if (account.filterStatus === 'online') counts.online += 1;
            else if (account.filterStatus === 'offline') counts.offline += 1;
            else counts.exception += 1;
        });
        var tabs = document.querySelectorAll('#mainHost .local-tab');
        if (tabs.length >= 4) {
            tabs[0].textContent = '全部账号 (' + counts.all + ')';
            tabs[1].textContent = '在线 (' + counts.online + ')';
            tabs[2].textContent = '离线 (' + counts.offline + ')';
            tabs[3].textContent = '异常 (' + counts.exception + ')';
        }
    }

    function _syncAccountBanner(accounts, dismissed) {
        var banner = document.querySelector('#mainHost .js-account-isolation-banner');
        if (!banner) return;
        var pending = accounts.filter(function (account) { return !account.isolationEnabled; });
        var copy = banner.querySelector('.js-account-isolation-copy');
        if (copy) {
            if (!pending.length) copy.textContent = '当前账号已经全部启用隔离环境，可以继续执行批量登录和导入。';
            else copy.textContent = '当前仍有 ' + pending.length + ' 个账号未启用隔离环境，建议先完成浏览器隔离配置，再继续登录和导入。';
        }
        banner.classList.toggle('shell-hidden', dismissed || pending.length === 0);
    }

    function _clearAccountBatchSelection() {
        document.querySelectorAll('.js-batch-account').forEach(function (cb) {
            cb.checked = false;
        });
        document.querySelectorAll('.batch-bar').forEach(function (bar) { bar.remove(); });
    }

    function _setAccountBatchMode(enabled) {
        if (!uiState.account) uiState.account = { statusFilter: 'all', view: 'card', sortMode: 'default', selectedId: null, batchMode: false };
        uiState.account.batchMode = !!enabled;
        if (!enabled) {
            _clearAccountBatchSelection();
        }
        _syncAccountControls();
        if (typeof applyCurrentRouteState === 'function') applyCurrentRouteState();
    }

    function _openAccountTagBatchModal(accounts) {
        var selectedIds = [];
        document.querySelectorAll('.js-batch-account:checked').forEach(function (cb) {
            selectedIds.push(String(cb.dataset.id || ''));
        });
        if (!selectedIds.length) {
            showToast('请先勾选需要打标签的账号', 'warning');
            return;
        }

        openModal({
            title: '批量打标签',
            submitText: '保存标签',
            fields: [
                {
                    key: 'tags',
                    label: '标签',
                    placeholder: '例如：重点, 续签, 北美',
                    hint: '用逗号分隔，可直接输入自定义标签。系统会在原有标签基础上合并去重。',
                    required: true,
                },
            ],
            onSubmit: function (data) {
                var incoming = _splitAccountTags(data.tags || '');
                if (!incoming.length) {
                    throw new Error('请至少填写一个标签');
                }
                var jobs = selectedIds.map(function (id) {
                    var account = _findAccountViewModel(accounts, id);
                    return api.accounts.update(id, {
                        tags: _mergeAccountTags(account ? account.tags : [], incoming),
                    });
                });
                return Promise.all(jobs).then(function () {
                    showToast('已为 ' + selectedIds.length + ' 个账号补充标签', 'success');
                    loaders['account']();
                });
            },
        });
    }

    function _selectAccountCard(accountId, accounts) {
        var selected = _findAccountViewModel(accounts, accountId);
        if (!selected) {
            selected = (accounts || [])[0] || null;
        }
        document.querySelectorAll('#mainHost .account-card').forEach(function (card) {
            card.classList.toggle('is-selected', String(card.dataset.id || '') === String(selected ? selected.id : ''));
        });
        if (!uiState.account) uiState.account = { statusFilter: 'all', view: 'card', sortMode: 'default' };
        uiState.account.selectedId = selected ? selected.id : null;
        _renderAccountDetail(selected);
    }

    function _bindAccountToolbar(accounts) {
        document.querySelectorAll('#mainHost .js-account-status-tab').forEach(function (tab) {
            _bindButtonAction(tab, 'tkopsAccountStatusBound', function () {
                if (!uiState.account) uiState.account = { statusFilter: 'all', view: 'card', sortMode: 'default' };
                uiState.account.statusFilter = tab.dataset.filterValue || 'all';
                _syncAccountControls();
                if (typeof applyCurrentRouteState === 'function') applyCurrentRouteState();
            });
        });

        document.querySelectorAll('#mainHost .js-account-view').forEach(function (btn) {
            _bindButtonAction(btn, 'tkopsAccountViewBound', function () {
                if (!uiState.account) uiState.account = { statusFilter: 'all', view: 'card', sortMode: 'default' };
                uiState.account.view = btn.dataset.view || 'card';
                _syncAccountControls();
                if (typeof applyCurrentRouteState === 'function') applyCurrentRouteState();
            });
        });

        var dismissBtn = document.querySelector('#mainHost .js-account-dismiss-reminder');
        if (dismissBtn) {
            _bindButtonAction(dismissBtn, 'tkopsAccountBannerDismissBound', function () {
                api.settings.set('account.isolation.notice.dismissed', '1').then(function () {
                    var banner = document.querySelector('#mainHost .js-account-isolation-banner');
                    if (banner) banner.classList.add('shell-hidden');
                    showToast('本轮已隐藏隔离提醒', 'info');
                }).catch(function (err) {
                    showToast('提醒设置保存失败: ' + ((err && err.message) || '未知错误'), 'error');
                });
            });
        }

        var isolationBtn = document.querySelector('#mainHost .js-account-open-isolation');
        if (isolationBtn) {
            _bindButtonAction(isolationBtn, 'tkopsAccountIsolationBound', function () {
                if (typeof renderRoute === 'function') renderRoute('device-management');
            });
        }

        var batchTagBtn = document.querySelector('#mainHost .js-account-tag-batch');
        if (batchTagBtn) {
            _bindButtonAction(batchTagBtn, 'tkopsAccountBatchTagBound', function () {
                if (!uiState.account) uiState.account = { statusFilter: 'all', view: 'card', sortMode: 'default', selectedId: null, batchMode: false };
                if (!uiState.account.batchMode) {
                    _setAccountBatchMode(true);
                    showToast('已进入批量模式，请勾选账号后继续打标签', 'info');
                    return;
                }
                _openAccountTagBatchModal(accounts);
            });
        }

        var batchCancelBtn = document.querySelector('#mainHost .js-account-batch-cancel');
        if (batchCancelBtn) {
            _bindButtonAction(batchCancelBtn, 'tkopsAccountBatchCancelBound', function () {
                _setAccountBatchMode(false);
                showToast('已退出批量模式', 'info');
            });
        }
    }

    function _bindAccountActions(accounts) {
        document.querySelectorAll('#mainHost .account-card').forEach(function (card) {
            card.addEventListener('click', function (event) {
                if (event.target.closest('button, input, textarea, select, label')) return;
                _selectAccountCard(card.dataset.id, accounts);
            });
        });

        document.querySelectorAll('.js-edit-account').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var id = parseInt(btn.dataset.id, 10);
                var account = (accounts || []).find(function (item) { return item.id === id; });
                if (account) openAccountForm(account);
            });
        });
        document.querySelectorAll('.js-delete-account').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                _confirmDeleteAccount(btn.dataset.id);
            });
        });
        document.querySelectorAll('.js-view-account').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                _selectAccountCard(btn.dataset.id, accounts);
            });
        });

        document.querySelectorAll('.js-account-open-environment').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var account = _findAccountViewModel(accounts, btn.dataset.id);
                if (account) _openAccountEnvironment(account);
            });
        });

        document.querySelectorAll('.js-account-manage-cookies').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var account = _findAccountViewModel(accounts, btn.dataset.id);
                if (account) _openAccountCookieModal(account);
            });
        });

        document.querySelectorAll('.js-validate-account-login').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                _runAccountLoginValidation(btn.dataset.id, btn);
            });
        });

        document.querySelectorAll('.js-test-account-connection').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                _runAccountConnectionTest(btn.dataset.id, btn);
            });
        });

        document.querySelectorAll('.js-account-configure-proxy').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var account = _findAccountViewModel(accounts, btn.dataset.id);
                if (account) _openAccountProxyConfig(account);
            });
        });

        document.querySelectorAll('.js-account-rebind-validate').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var account = _findAccountViewModel(accounts, btn.dataset.id);
                if (account) _openAccountProxyConfig(account, { quickValidate: true });
            });
        });
    }

    loaders['account'] = function () {
        _wireHeaderPrimary(function () { openAccountForm(); }, '新建账号');
        if (!uiState.account) uiState.account = { statusFilter: 'all', view: 'card', sortMode: 'default', selectedId: null, batchMode: false };
        if (typeof uiState.account.batchMode === 'undefined') uiState.account.batchMode = false;

        Promise.all([
            api.accounts.list(),
            api.devices.list(),
            api.settings.get('account.isolation.notice.dismissed'),
        ]).then(function (results) {
            var accounts = results[0] || [];
            var devices = results[1] || [];
            var reminderSetting = String(results[2] || '').toLowerCase();
            var reminderDismissed = reminderSetting === '1' || reminderSetting === 'true' || reminderSetting === 'yes';
            var deviceMap = {};
            devices.forEach(function (device) {
                deviceMap[String(device.id)] = device;
            });

            var viewModels = accounts.map(function (account) {
                return _buildAccountViewModel(account, deviceMap[String(account.device_id || '')] || null);
            });
            window.__accountPageData = viewModels;

            runtimeSummaryHandlers['account']({ accounts: accounts });
            _updateAccountTabs(viewModels);
            _syncAccountBanner(viewModels, reminderDismissed);
            _syncAccountControls();
            _renderAccountGrid(viewModels);
            _bindAccountToolbar(viewModels);
            _bindAccountActions(viewModels);
            _bindBatchBar('.js-batch-account', function (ids) {
                return _batchDelete(ids, api.accounts.remove, '账号', 'account');
            });

            if (!viewModels.length) {
                window.__accountPageData = [];
                _renderEmptyAccountDetail();
                return;
            }

            var preferredId = uiState.account && uiState.account.selectedId ? String(uiState.account.selectedId) : String(viewModels[0].id || '');
            _selectAccountCard(preferredId, viewModels);
            if (typeof applyCurrentRouteState === 'function') applyCurrentRouteState();
        }).catch(function (error) {
            console.warn('[page-loaders] account load failed:', error);
            window.__accountPageData = [];
            showToast('账号数据加载失败: ' + ((error && error.message) || '未知错误'), 'error');
            _renderEmptyAccountDetail();
        });
    };

    window.__accountPageMain = {
        selectAccountCard: function (accountId) {
            var cards = document.querySelectorAll('#mainHost .account-card');
            if (!cards.length) return;
            _selectAccountCard(accountId, (window.__accountPageData || []));
        },
    };

    window.__selectAccountCard = window.__accountPageMain.selectAccountCard;
})();