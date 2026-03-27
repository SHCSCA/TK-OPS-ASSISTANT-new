/* 鈹€鈹€ page-loaders.js 鈹€ 椤甸潰绾ф暟鎹姞杞藉櫒 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
   姣忎釜璺敱娓叉煋瀹岄潤鎬佹ā鏉垮悗锛屽搴旂殑 loader 鎷夊彇鐪熷疄鏁版嵁
   骞舵敞鍏?DOM銆傜敱 loadRouteData(routeKey) 缁熶竴璋冨害銆?   鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€ */
(function () {
    'use strict';

    var loaders = {};
    var runtimeSummaryHandlers = {
        'dashboard': function (payload) {
            payload = payload || {};
            var stats = payload.stats || {};
            var accountStatuses = (stats.accounts && stats.accounts.byStatus) || {};
            var taskStatuses = (stats.tasks && stats.tasks.byStatus) || {};
            var deviceStatuses = (stats.devices && stats.devices.byStatus) || {};
            _applyRuntimeSummary({
                eyebrow: '浠婃棩閲嶇偣',
                title: '绯荤粺瀹炴椂杩愯鎽樿',
                copy: '璐﹀彿 ' + (stats.accounts ? stats.accounts.total || 0 : 0)
                    + ' / 浠诲姟 ' + (stats.tasks ? stats.tasks.total || 0 : 0)
                    + ' / 璁惧 ' + (stats.devices ? stats.devices.total || 0 : 0)
                    + ' / 渚涘簲鍟?' + (stats.providers || 0)
                    + ' / 绱犳潗 ' + (stats.assets || 0),
                statusLeft: [
                    '璐﹀彿 ' + (accountStatuses.active || 0) + ' 娲昏穬 / ' + ((stats.accounts && stats.accounts.total) || 0) + ' 鎬婚噺',
                    '浠诲姟杩愯涓?' + (taskStatuses.running || 0) + ' / 鎺掗槦 ' + (taskStatuses.pending || 0),
                    '璁惧鍋ュ悍 ' + (deviceStatuses.healthy || 0) + ' / 寮傚父 ' + (deviceStatuses.error || 0),
                ],
                statusRight: [
                    { text: (taskStatuses.failed || 0) > 0 ? ('浠诲姟寮傚父 ' + (taskStatuses.failed || 0)) : '浠诲姟绋冲畾', tone: (taskStatuses.failed || 0) > 0 ? 'error' : 'success' },
                    { text: (stats.providers || 0) > 0 ? ('宸叉帴鍏ヤ緵搴斿晢 ' + (stats.providers || 0)) : '鏈厤缃緵搴斿晢', tone: (stats.providers || 0) > 0 ? 'info' : 'warning' },
                ],
            });
        },
        'account': function (payload) {
            payload = payload || {};
            var accounts = payload.accounts || [];
            var counts = { total: accounts.length, online: 0, offline: 0, error: 0 };
            accounts.forEach(function (a) {
                var s = (a.status || '').toLowerCase();
                if (s === 'online' || s === '鍦ㄧ嚎' || s === 'active') counts.online++;
                else if (s === 'offline' || s === '绂荤嚎' || s === 'idle') counts.offline++;
                else if (s === 'error' || s === 'warning' || s === '寮傚父' || s === 'suspended' || s === 'warming') counts.error++;
            });
            _applyRuntimeSummary({
                eyebrow: '褰撳墠鎻愰啋',
                title: counts.error > 0 ? (counts.error + ' 涓紓甯歌处鍙峰緟澶勭悊') : '璐﹀彿鐘舵€佺ǔ瀹?,
                copy: '鍦ㄧ嚎 ' + counts.online + ' / 绂荤嚎 ' + counts.offline + ' / 寮傚父 ' + counts.error + ' / 鎬婚噺 ' + counts.total,
                statusLeft: [
                    '璐﹀彿鎬婚噺 ' + counts.total,
                    '鍦ㄧ嚎璐﹀彿 ' + counts.online,
                    '寮傚父璐﹀彿 ' + counts.error,
                ],
                statusRight: [
                    { text: counts.online > 0 ? ('鍦ㄧ嚎 ' + counts.online) : '鏆傛棤鍦ㄧ嚎璐﹀彿', tone: counts.online > 0 ? 'success' : 'warning' },
                    { text: counts.error > 0 ? ('寮傚父 ' + counts.error) : '鏃犲紓甯?, tone: counts.error > 0 ? 'error' : 'info' },
                ],
            });
        },
        'group-management': function (payload) {
            payload = payload || {};
            var groups = payload.groups || [];
            var described = groups.filter(function (g) { return !!(g.description || '').trim(); }).length;
            var colored = groups.filter(function (g) { return !!(g.color || '').trim(); }).length;
            _applyRuntimeSummary({
                eyebrow: '缁勭粐鎻愰啋',
                title: groups.length ? ('鍒嗙粍缁撴瀯宸插姞杞?' + groups.length + ' 椤?) : '鏆傛棤鍒嗙粍缁撴瀯',
                copy: '宸叉弿杩?' + described + ' / 宸查厤鑹?' + colored + ' / 鎬婚噺 ' + groups.length,
                statusLeft: ['鍒嗙粍鎬婚噺 ' + groups.length, '宸叉弿杩板垎缁?' + described, '宸查厤鑹插垎缁?' + colored],
                statusRight: [
                    { text: groups.length ? '鍒嗙粍宸叉帴绾? : '绛夊緟鍒涘缓鍒嗙粍', tone: groups.length ? 'success' : 'warning' },
                    { text: '瀹炴椂姹囨€?, tone: 'info' },
                ],
            });
        },
        'device-management': function (payload) {
            payload = payload || {};
            var devices = payload.devices || [];
            var healthy = devices.filter(function (d) { return (d.status || '').toLowerCase() === 'healthy'; }).length;
            var warning = devices.filter(function (d) { return (d.status || '').toLowerCase() === 'warning'; }).length;
            var error = devices.filter(function (d) { return (d.status || '').toLowerCase() === 'error'; }).length;
            var rate = devices.length ? Math.round((healthy / devices.length) * 100) : 0;
            _applyRuntimeSummary({
                eyebrow: '鐜鎻愰啋',
                title: error > 0 ? (error + ' 鍙板紓甯歌澶囧緟澶勭悊') : '璁惧鐜鐘舵€佺ǔ瀹?,
                copy: '鍋ュ悍 ' + healthy + ' / 鍛婅 ' + warning + ' / 寮傚父 ' + error + ' / 鎬婚噺 ' + devices.length,
                statusLeft: ['璁惧鎬婚噺 ' + devices.length, '鍋ュ悍瑕嗙洊鐜?' + rate + '%', '寮傚父璁惧 ' + error],
                statusRight: [
                    { text: error > 0 ? ('寮傚父 ' + error) : '鐜姝ｅ父', tone: error > 0 ? 'error' : 'success' },
                    { text: warning > 0 ? ('鍛婅 ' + warning) : '鏃犲憡璀?, tone: warning > 0 ? 'warning' : 'info' },
                ],
            });
        },
        'ai-provider': function (payload) {
            payload = payload || {};
            var providers = payload.providers || [];
            var active = providers.filter(function (p) { return p.is_active === true || p.is_active === 'True'; });
            var primary = active[0] || providers[0] || null;
            _applyRuntimeSummary({
                eyebrow: '閰嶇疆寤鸿',
                title: providers.length ? ('宸叉帴鍏?' + providers.length + ' 涓緵搴斿晢') : '灏氭湭閰嶇疆渚涘簲鍟?,
                copy: primary ? ('褰撳墠榛樿妯″瀷 ' + (primary.default_model || '-') + ' / 渚涘簲鍟?' + (primary.name || '-')) : '璇峰厛娣诲姞渚涘簲鍟嗗苟瀹屾垚杩炴帴娴嬭瘯銆?,
                statusLeft: ['渚涘簲鍟嗘€婚噺 ' + providers.length, '鍚敤渚涘簲鍟?' + active.length, '榛樿妯″瀷 ' + (primary ? (primary.default_model || '-') : '-')],
                statusRight: [
                    { text: active.length ? ('鍚敤涓?' + active.length) : '鏈惎鐢?, tone: active.length ? 'success' : 'warning' },
                    { text: primary ? (primary.name || '宸查厤缃?) : '绛夊緟鍔犺浇', tone: primary ? 'info' : 'warning' },
                ],
            });
        },
        'task-queue': function (payload) {
            payload = payload || {};
            var tasks = payload.tasks || [];
            var counts = { total: tasks.length, running: 0, pending: 0, completed: 0, failed: 0 };
            tasks.forEach(function (task) {
                var s = (task.status || '').toLowerCase();
                if (s === 'running') counts.running++;
                else if (s === 'pending') counts.pending++;
                else if (s === 'completed') counts.completed++;
                else if (s === 'failed') counts.failed++;
            });
            _applyRuntimeSummary({
                eyebrow: '闃熷垪鎽樿',
                title: tasks.length ? ('杩愯涓?' + counts.running + ' 鏉★紝鎺掗槦 ' + counts.pending + ' 鏉?) : '鏆傛棤浠诲姟闃熷垪鏁版嵁',
                copy: '宸插畬鎴?' + counts.completed + ' / 寮傚父 ' + counts.failed + ' / 鎬婚噺 ' + counts.total,
                statusLeft: ['浠诲姟鎬婚噺 ' + counts.total, '杩愯涓换鍔?' + counts.running, '鎺掗槦浠诲姟 ' + counts.pending],
                statusRight: [
                    { text: counts.completed ? ('宸插畬鎴?' + counts.completed) : '寰呭畬鎴愪换鍔?, tone: counts.completed ? 'success' : 'info' },
                    { text: counts.failed ? ('闇€閲嶈瘯 ' + counts.failed) : '鏃犲紓甯?, tone: counts.failed ? 'error' : 'info' },
                ],
            });
        },
        'asset-center': function (payload) {
            payload = payload || {};
            var assets = payload.assets || [];
            var stats = payload.stats || { total: assets.length, byType: {} };
            var total = stats.total || assets.length;
            var byType = stats.byType || {};
            var reviewCount = (byType.text || 0) + (byType.template || 0);
            var reusable = total ? Math.round(((byType.video || 0) + (byType.image || 0)) / total * 100) : 0;
            _applyRuntimeSummary({
                eyebrow: '绱犳潗鎻愰啋',
                title: total ? ('绱犳潗搴撳瓨 ' + total + ' 椤?) : '鏆傛棤绱犳潗搴撳瓨',
                copy: '寰呮暣鐞?' + reviewCount + ' / 鍥剧墖瑙嗛鍗犳瘮 ' + reusable + '%',
                statusLeft: ['绱犳潗鎬婚噺 ' + total, '寰呮暣鐞嗙礌鏉?' + reviewCount, '鍥剧墖/瑙嗛鍗犳瘮 ' + reusable + '%'],
                statusRight: [
                    { text: total ? '搴撳瓨宸插姞杞? : '绛夊緟涓婁紶绱犳潗', tone: total ? 'success' : 'warning' },
                    { text: reviewCount ? ('寰呮暣鐞?' + reviewCount) : '宸叉暣鐞?, tone: reviewCount ? 'warning' : 'info' },
                ],
            });
        },
    };
    var pageAudits = {
        'dashboard': {
            dataSources: ['getDashboardStats'],
            interactions: ['create', 'detail', 'filter', 'navigate'],
        },
        'account': {
            dataSources: ['listAccounts'],
            interactions: ['create', 'edit', 'delete', 'filter', 'detail', 'batch', 'task'],
        },
        'ai-provider': {
            dataSources: ['listProviders'],
            interactions: ['create', 'edit', 'activate', 'delete', 'detail'],
        },
        'task-queue': {
            dataSources: ['listTasks'],
            interactions: ['create', 'edit', 'start', 'complete', 'delete', 'filter', 'batch', 'detail'],
        },
        'group-management': {
            dataSources: ['listGroups'],
            interactions: ['create', 'edit', 'delete', 'filter', 'detail'],
        },
        'device-management': {
            dataSources: ['listDevices'],
            interactions: ['create', 'edit', 'delete', 'filter', 'detail', 'batch'],
        },
        'asset-center': {
            dataSources: ['listAssets', 'getAssetStats'],
            interactions: ['create', 'edit', 'delete', 'filter', 'detail'],
        },
    };

    function _applyRuntimeSummary(summary) {
        if (!summary) return;
        if (typeof renderSidebarSummary === 'function') {
            renderSidebarSummary({
                eyebrow: summary.eyebrow || '',
                title: summary.title || '',
                copy: summary.copy || '',
            });
        } else {
            var titleNode = document.getElementById('sidebarSummaryTitle');
            var copyNode = document.getElementById('sidebarSummaryCopy');
            if (titleNode) titleNode.textContent = summary.title || '';
            if (copyNode) copyNode.textContent = summary.copy || '';
        }
        var leftHost = document.getElementById('statusLeft');
        var rightHost = document.getElementById('statusRight');
        if (leftHost && Array.isArray(summary.statusLeft)) {
            leftHost.innerHTML = summary.statusLeft.map(function (text) {
                return '<span class="status-text">' + _esc(text) + '</span>';
            }).join('');
        }
        if (rightHost && Array.isArray(summary.statusRight)) {
            rightHost.innerHTML = summary.statusRight.map(function (item) {
                return '<span class="status-chip ' + _esc(item.tone || 'info') + '">' + _esc(item.text || '') + '</span>';
            }).join('');
        }
    }

    /* 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲
       Account 椤甸潰
       鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲 */
    loaders['account'] = function () {
        _wireHeaderPrimary(function () { openAccountForm(); }, '鏂板缓璐﹀彿');

        api.accounts.list().then(function (accounts) {
            accounts = accounts || [];
            runtimeSummaryHandlers['account']({ accounts: accounts });
            // 鈹€鈹€ 鏇存柊 tabs 璁℃暟 鈹€鈹€
            var counts = { all: accounts.length, online: 0, offline: 0, error: 0 };
            accounts.forEach(function (a) {
                var s = (a.status || '').toLowerCase();
                if (s === 'online' || s === '鍦ㄧ嚎' || s === 'active') counts.online++;
                else if (s === 'offline' || s === '绂荤嚎' || s === 'idle') counts.offline++;
                else if (s === 'error' || s === 'warning' || s === '寮傚父' || s === 'suspended') counts.error++;
            });
            var tabs = document.querySelectorAll('#mainHost .local-tab');
            if (tabs.length >= 4) {
                tabs[0].textContent = '鍏ㄩ儴璐﹀彿 (' + counts.all + ')';
                tabs[1].textContent = '鍦ㄧ嚎 (' + counts.online + ')';
                tabs[2].textContent = '绂荤嚎 (' + (counts.all - counts.online - counts.error) + ')';
                tabs[3].textContent = '寮傚父 (' + counts.error + ')';
            }

            // 鈹€鈹€ 娓叉煋鍗＄墖 鈹€鈹€
            var grid = document.querySelector('#mainHost .account-grid');
            if (!grid) return;
            if (accounts.length === 0) {
                grid.innerHTML = '<div class="empty-state" style="padding:48px;text-align:center;"><p>鏆傛棤璐﹀彿鏁版嵁</p><p class="subtle">鐐瑰嚮鍙充笂瑙掋€屾柊寤鸿处鍙枫€嶆坊鍔犵涓€涓处鍙?/p></div>';
                return;
            }
            grid.innerHTML = accounts.map(function (a, i) {
                var statusClass = _accountStatusTone(a.status);
                var statusLabel = a.status || '鏈煡';
                return '<article class="account-card' + (i === 0 ? ' is-selected' : '') + '" data-id="' + (a.id || '') + '" data-status="' + _esc((a.status || '').toLowerCase()) + '" data-order="' + _esc(_accountSortOrder(a.status)) + '" data-search="' + _esc((a.username || '') + ' ' + (a.platform || '') + ' ' + (a.region || '') + ' ' + (a.status || '') + ' ' + (a.notes || '')) + '">'
                    + '<input type="checkbox" class="batch-check js-batch-account" data-id="' + (a.id || '') + '">'
                    + '<div class="account-card__head"><div><strong>' + _esc(a.username || '') + '</strong>'
                    + '<div class="subtle">' + _esc(a.platform || '') + ' 路 ' + _esc(a.region || '') + '</div></div>'
                    + '<span class="status-chip ' + statusClass + '">' + _esc(statusLabel) + '</span></div>'
                    + '<div class="account-card__meta">'
                    + '<div class="list-row"><span class="subtle">璐﹀彿 ID</span><strong class="mono">' + (a.id || '-') + '</strong></div>'
                    + '<div class="list-row"><span class="subtle">绮変笣</span><strong>' + _formatNum(a.followers || 0) + '</strong></div>'
                    + '<div class="list-row"><span class="subtle">鍒涘缓鏃堕棿</span><strong>' + _esc(a.created_at || '-') + '</strong></div>'
                    + '</div>'
                    + '<div class="detail-actions">'
                    + '<button class="secondary-button js-edit-account" data-id="' + (a.id || '') + '">缂栬緫</button>'
                    + '<button class="ghost-button js-view-account" data-id="' + (a.id || '') + '">鏌ョ湅璇︽儏</button>'
                    + '<button class="danger-button js-delete-account" data-id="' + (a.id || '') + '">鍒犻櫎</button>'
                    + '</div></article>';
            }).join('');

            _bindAccountActions(accounts);
            _bindBatchBar('.js-batch-account', function (ids) {
                return _batchDelete(ids, api.accounts.remove, '璐﹀彿', 'account');
            });
        }).catch(function (e) {
        });
    };

    function _bindAccountActions(accounts) {
        // 缂栬緫璐﹀彿
        document.querySelectorAll('.js-edit-account').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var id = parseInt(btn.dataset.id, 10);
                var acc = (accounts || []).find(function (a) { return a.id === id; });
                if (acc) openAccountForm(acc);
            });
        });
        // 鍒犻櫎璐﹀彿
        document.querySelectorAll('.js-delete-account').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var id = parseInt(btn.dataset.id, 10);
                if (!id) return;
                confirmModal({
                    title: '鍒犻櫎璐﹀彿',
                    message: '纭畾瑕佸垹闄ゆ璐﹀彿锛熸鎿嶄綔涓嶅彲鎭㈠銆?,
                    confirmText: '鍒犻櫎',
                    tone: 'danger',
                }).then(function (ok) {
                    if (!ok) return;
                    api.accounts.remove(id).then(function () {
                        showToast('璐﹀彿宸插垹闄?);
                        loaders['account']();
                    }).catch(function (err) {
                        showToast('鍒犻櫎澶辫触: ' + err.message, 'error');
                    });
                });
            });
        });
        // 鏌ョ湅璇︽儏
        document.querySelectorAll('.js-view-account').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var id = btn.dataset.id;
                var cards = document.querySelectorAll('.account-card');
                cards.forEach(function (c) { c.classList.toggle('is-selected', c.dataset.id === id); });
                _renderAccountDetail((accounts || []).find(function (a) { return String(a.id) === String(id); }));
            });
        });
    }

    function _renderAccountDetail(account) {
        if (!account) return;
        var detailHost = document.getElementById('detailHost');
        if (!detailHost) return;
        detailHost.innerHTML = '<div class="detail-root"><section class="panel"><div class="panel__header"><div><strong>' + _esc(account.username || '璐﹀彿璇︽儏') + '</strong><div class="subtle mono">ID ' + _esc(account.id || '-') + '</div></div><span class="status-chip ' + _accountStatusTone(account.status) + '">' + _esc(account.status || '鏈煡') + '</span></div><div class="detail-list"><div class="detail-item"><span class="subtle">骞冲彴</span><strong>' + _esc(account.platform || '-') + '</strong></div><div class="detail-item"><span class="subtle">鍦板尯</span><strong>' + _esc(account.region || '-') + '</strong></div><div class="detail-item"><span class="subtle">绮変笣鏁?/span><strong>' + _formatNum(account.followers || 0) + '</strong></div><div class="detail-item"><span class="subtle">澶囨敞</span><strong>' + _esc(account.notes || '鏃?) + '</strong></div></div></section></div>';
    }

    function _accountStatusTone(status) {
        if (!status) return 'info';
        var s = status.toLowerCase();
        if (s === 'online' || s === '鍦ㄧ嚎' || s === 'active') return 'success';
        if (s === 'offline' || s === '绂荤嚎' || s === 'idle') return 'info';
        if (s === 'warning' || s === '璀﹀憡' || s === 'warming') return 'warning';
        return 'error';
    }

    function _accountSortOrder(status) {
        var s = (status || '').toLowerCase();
        if (s === 'error' || s === '寮傚父' || s === 'suspended') return '1';
        if (s === 'warning' || s === 'warming') return '2';
        if (s === 'offline' || s === '绂荤嚎' || s === 'idle') return '3';
        return '4';
    }

    /* 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲
       Dashboard 椤甸潰
       鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲 */
    loaders['dashboard'] = function () {
        api.dashboard.stats().then(function (stats) {
            if (!stats) return;
            runtimeSummaryHandlers['dashboard']({ stats: stats });
            var cards = document.querySelectorAll('#mainHost .stat-card');
            if (cards.length >= 4) {
                // Total Accounts
                var acVal = cards[0].querySelector('.stat-card__value');
                if (acVal) acVal.textContent = _formatNum(stats.accounts ? stats.accounts.total : 0);
                // AI Tasks (浣跨敤 tasks total)
                var tkVal = cards[1].querySelector('.stat-card__value');
                if (tkVal) tkVal.textContent = _formatNum(stats.tasks ? stats.tasks.total : 0);
                // Providers count 鈫?System Health placeholder
                var sysVal = cards[2].querySelector('.stat-card__value');
                if (sysVal) {
                    var provCount = stats.providers || 0;
                    sysVal.textContent = provCount > 0 ? '姝ｅ父' : '鏈厤缃?;
                }
                // Groups 鈫?ROI placeholder
                var grpVal = cards[3].querySelector('.stat-card__value');
                if (grpVal) grpVal.textContent = _formatNum(stats.groups || 0) + ' 缁?;
            }

            // 鈹€鈹€ 鏇存柊渚ф爮 AI 寮曟搸鐘舵€?鈹€鈹€
            _updateDashboardSidebar(stats);
        }).catch(function (e) {
            console.warn('[page-loaders] dashboard load failed:', e);
        });
    };

    function _updateDashboardSidebar(stats) {
        // 鏇存柊浠诲姟 byStatus 鏄剧ず
        var taskItems = document.querySelectorAll('#mainHost .metric-list .task-item');
        if (taskItems.length >= 1 && stats.tasks && stats.tasks.byStatus) {
            var bs = stats.tasks.byStatus;
            var running = bs['running'] || 0;
            var pending = bs['pending'] || 0;
            var completed = bs['completed'] || 0;
            var failed = bs['failed'] || 0;
            // 鏇存柊绗竴涓?task-item 灞曠ず浠诲姟杩愯鐘舵€?            var firstStrong = taskItems[0].querySelector('strong');
            if (firstStrong) firstStrong.textContent = '浠诲姟鎵ц寮曟搸';
            var firstSubtle = taskItems[0].querySelector('.subtle');
            if (firstSubtle) firstSubtle.textContent = '杩愯涓?' + running + ' / 鎺掗槦 ' + pending;
            var firstPill = taskItems[0].querySelector('.pill');
            if (firstPill) {
                firstPill.textContent = failed > 0 ? failed + ' 寮傚父' : '姝ｅ父';
                firstPill.className = 'pill ' + (failed > 0 ? 'error' : 'success');
            }
        }
    }

    /* 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲
       Task Queue 椤甸潰
       鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲 */
    loaders['task-queue'] = function () {
        _wireHeaderPrimary(function () { openTaskForm(); });

        api.tasks.list().then(function (tasks) {
            tasks = tasks || [];
            runtimeSummaryHandlers['task-queue']({ tasks: tasks });
            // 鈹€鈹€ 鏇存柊 tabs 鈹€鈹€
            var counts = { all: tasks.length, running: 0, completed: 0, pending: 0, failed: 0 };
            tasks.forEach(function (t) {
                var s = (t.status || '').toLowerCase();
                if (s === 'running') counts.running++;
                else if (s === 'completed') counts.completed++;
                else if (s === 'pending') counts.pending++;
                else if (s === 'failed') counts.failed++;
            });
            var tabs = document.querySelectorAll('#mainHost .local-tab');
            if (tabs.length >= 5) {
                tabs[0].textContent = '鍏ㄩ儴浠诲姟 (' + counts.all + ')';
                tabs[1].textContent = '杩涜涓?(' + counts.running + ')';
                tabs[2].textContent = '宸插畬鎴?(' + counts.completed + ')';
                tabs[3].textContent = '鎺掗槦涓?(' + counts.pending + ')';
                tabs[4].textContent = '寮傚父 (' + counts.failed + ')';
            }

            // 鈹€鈹€ 娓叉煋琛ㄦ牸 鈹€鈹€
            var tbody = document.querySelector('#mainHost .table-wrapper tbody');
            if (!tbody) return;
            if (tasks.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:32px;">鏆傛棤浠诲姟鏁版嵁</td></tr>';
                return;
            }
            tbody.innerHTML = tasks.map(function (t) {
                var statusClass = _taskStatusTone(t.status);
                var statusLabel = _taskStatusLabel(t.status);
                return '<tr class="route-row" data-id="' + (t.id || '') + '" data-status="' + _esc((t.status || '').toLowerCase()) + '" data-search="' + _esc((t.title || '') + ' ' + (t.task_type || '') + ' ' + (t.status || '') + ' ' + (t.priority || '') + ' ' + (t.result_summary || '')) + '">'
                    + '<td><input type="checkbox" class="batch-check js-batch-task" data-id="' + (t.id || '') + '"></td>'
                    + '<td><strong>' + _esc(t.title || '') + '</strong></td>'
                    + '<td>' + _esc(t.task_type || '-') + '</td>'
                    + '<td><span class="status-chip ' + statusClass + '">' + statusLabel + '</span></td>'
                    + '<td>' + _esc(t.priority || '-') + '</td>'
                    + '<td class="subtle">' + _esc(t.created_at || '-') + '</td>'
                    + '<td>' + _taskAction(t) + '</td>'
                    + '<td><button class="ghost-button js-edit-task" data-id="' + (t.id || '') + '">缂栬緫</button></td>'
                    + '</tr>';
            }).join('');

            _bindTaskActions(tasks);
            _bindBatchBar('.js-batch-task', function (ids) {
                return _batchDelete(ids, api.tasks.remove, '浠诲姟', 'task-queue');
            });
        }).catch(function (e) {
            console.warn('[page-loaders] task-queue load failed:', e);
        });
    };

    function _bindTaskActions(tasks) {
        document.querySelectorAll('.js-start-task').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                api.tasks.start(id).then(function () {
                    showToast('浠诲姟宸插惎鍔?);
                    loaders['task-queue']();
                });
            });
        });
        document.querySelectorAll('.js-complete-task').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                api.tasks.complete(id).then(function () {
                    showToast('浠诲姟宸插畬鎴?);
                    loaders['task-queue']();
                });
            });
        });
        document.querySelectorAll('.js-edit-task').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                var task = (tasks || []).find(function (t) { return t.id === id; });
                if (task) openTaskForm(task);
                if (task) _renderTaskDetail(task);
            });
        });
        document.querySelectorAll('.js-delete-task').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                confirmModal({
                    title: '鍒犻櫎浠诲姟',
                    message: '纭畾鍒犻櫎姝や换鍔★紵姝ゆ搷浣滀笉鍙仮澶嶃€?,
                    confirmText: '鍒犻櫎',
                    tone: 'danger',
                }).then(function (ok) {
                    if (!ok) return;
                    api.tasks.remove(id).then(function () {
                        showToast('浠诲姟宸插垹闄?);
                        loaders['task-queue']();
                    });
                });
            });
        });
    }

    function _renderTaskDetail(task) {
        if (!task) return;
        var detailHost = document.getElementById('detailHost');
        if (!detailHost) return;
        detailHost.innerHTML = '<div class="detail-root"><section class="panel"><div class="panel__header"><div><strong>' + _esc(task.title || '浠诲姟璇︽儏') + '</strong><div class="subtle">' + _esc(task.task_type || '-') + '</div></div><span class="status-chip ' + _taskStatusTone(task.status) + '">' + _esc(_taskStatusLabel(task.status)) + '</span></div><div class="detail-list"><div class="detail-item"><span class="subtle">浼樺厛绾?/span><strong>' + _esc(task.priority || '-') + '</strong></div><div class="detail-item"><span class="subtle">鍏宠仈璐﹀彿</span><strong>' + _esc(task.account_id || '-') + '</strong></div><div class="detail-item"><span class="subtle">缁撴灉鎽樿</span><strong>' + _esc(task.result_summary || '鏃?) + '</strong></div></div></section></div>';
    }

    function _taskAction(t) {
        var s = (t.status || '').toLowerCase();
        var id = t.id || '';
        if (s === 'pending') return '<button class="ghost-button js-start-task" data-id="' + id + '">鍚姩</button>';
        if (s === 'running') return '<button class="ghost-button js-complete-task" data-id="' + id + '">瀹屾垚</button>';
        if (s === 'completed') return '<span class="subtle">宸插畬鎴?/span>';
        if (s === 'failed') return '<button class="ghost-button js-start-task" data-id="' + id + '">閲嶈瘯</button>'
            + '<button class="ghost-button js-delete-task" data-id="' + id + '">鍒犻櫎</button>';
        return '<button class="ghost-button js-delete-task" data-id="' + id + '">鍒犻櫎</button>';
    }

    function _taskStatusTone(status) {
        var s = (status || '').toLowerCase();
        if (s === 'running') return 'info';
        if (s === 'completed') return 'success';
        if (s === 'pending') return 'warning';
        if (s === 'failed') return 'error';
        return 'info';
    }

    function _taskStatusLabel(status) {
        var map = { running: '杩愯涓?, completed: '宸插畬鎴?, pending: '鎺掗槦涓?, failed: '澶辫触', paused: '宸叉殏鍋? };
        return map[(status || '').toLowerCase()] || status || '鏈煡';
    }

    /* 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲
       AI Provider 椤甸潰
       鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲 */
    loaders['ai-provider'] = function () {
        _wireHeaderPrimary(function () { openProviderForm(); }, '娣诲姞渚涘簲鍟?);

        api.providers.list().then(function (providers) {
            providers = providers || [];
            runtimeSummaryHandlers['ai-provider']({ providers: providers });
            // 灏濊瘯娓叉煋鍒拌〃鏍?            var tbody = document.querySelector('#mainHost .table-wrapper tbody');
            if (tbody) {
                if (providers.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:32px;">鏆傛棤 AI 渚涘簲鍟嗭紝鐐瑰嚮銆屾坊鍔犱緵搴斿晢銆嶅紑濮嬮厤缃?/td></tr>';
                    return;
                }
                tbody.innerHTML = providers.map(function (p) {
                    var active = p.is_active === 'True' || p.is_active === true;
                    return '<tr data-id="' + (p.id || '') + '">'
                        + '<td><strong>' + _esc(p.name || '') + '</strong></td>'
                        + '<td>' + _esc(p.provider_type || '') + '</td>'
                        + '<td class="mono">' + _esc(p.default_model || '-') + '</td>'
                        + '<td><span class="status-chip ' + (active ? 'success' : 'info') + '">' + (active ? '鍚敤涓? : '鏈惎鐢?) + '</span></td>'
                        + '<td>'
                        + '<button class="ghost-button js-edit-provider" data-id="' + (p.id || '') + '">缂栬緫</button>'
                        + (active ? '' : '<button class="ghost-button js-activate-provider" data-id="' + (p.id || '') + '">鍚敤</button>')
                        + '<button class="ghost-button js-delete-provider" data-id="' + (p.id || '') + '" style="color:var(--status-error);">鍒犻櫎</button>'
                        + '</td></tr>';
                }).join('');
                _bindProviderActions(providers);
                return;
            }
            // 鍥為€€锛氭覆鏌撳埌鍒楄〃瀹瑰櫒
            var list = document.querySelector('#mainHost .metric-list, #mainHost .detail-list');
            if (!list) return;
            if (providers.length === 0) {
                list.innerHTML = '<div class="task-item"><div><strong>鏆傛棤 AI 渚涘簲鍟?/strong><div class="subtle">璇风偣鍑汇€屾坊鍔犱緵搴斿晢銆嶅紑濮嬮厤缃?/div></div></div>';
                return;
            }
            list.innerHTML = providers.map(function (p) {
                var active = p.is_active === 'True' || p.is_active === true;
                return '<div class="task-item" data-id="' + (p.id || '') + '">'
                    + '<div><strong>' + _esc(p.name || '') + '</strong>'
                    + '<div class="subtle">' + _esc(p.provider_type || '') + ' 路 ' + _esc(p.api_base || '') + '</div></div>'
                    + '<div style="display:flex;gap:6px;align-items:center;">'
                    + '<button class="ghost-button js-edit-provider" data-id="' + (p.id || '') + '">缂栬緫</button>'
                    + '<span class="pill ' + (active ? 'success' : 'info') + '">' + (active ? '娲昏穬' : '鏈惎鐢?) + '</span>'
                    + '</div></div>';
            }).join('');
            _bindProviderActions(providers);
        }).catch(function (e) {
            console.warn('[page-loaders] ai-provider load failed:', e);
        });
    };

    function _bindProviderActions(providers) {
        document.querySelectorAll('#mainHost .table-wrapper tbody tr[data-id], #mainHost .metric-list .task-item[data-id]').forEach(function (row) {
            row.addEventListener('click', function (e) {
                if (e.target.closest('button')) return;
                var id = parseInt(row.dataset.id, 10);
                _renderProviderDetail((providers || []).find(function (p) { return p.id === id; }));
            });
        });
        document.querySelectorAll('.js-edit-provider').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var id = parseInt(btn.dataset.id, 10);
                var prov = (providers || []).find(function (p) { return p.id === id; });
                if (prov) openProviderForm(prov);
                if (prov) _renderProviderDetail(prov);
            });
        });
        document.querySelectorAll('.js-activate-provider').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var id = parseInt(btn.dataset.id, 10);
                api.providers.activate(id).then(function () {
                    showToast('渚涘簲鍟嗗凡鍚敤', 'success');
                    loaders['ai-provider']();
                });
            });
        });
        document.querySelectorAll('.js-delete-provider').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var id = parseInt(btn.dataset.id, 10);
                if (!id) return;
                confirmModal({
                    title: '鍒犻櫎渚涘簲鍟?,
                    message: '鍒犻櫎鍚庢墍鏈変娇鐢ㄦ渚涘簲鍟嗙殑浠诲姟灏嗗彈鍒板奖鍝嶃€傜‘瀹氱户缁紵',
                    confirmText: '鍒犻櫎',
                    tone: 'danger',
                }).then(function (ok) {
                    if (!ok) return;
                    api.providers.remove(id).then(function () {
                        showToast('渚涘簲鍟嗗凡鍒犻櫎');
                        loaders['ai-provider']();
                    });
                });
            });
        });
    }

    /* 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲
       Group Management 椤甸潰
       鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲 */
    loaders['group-management'] = function () {
        _wireHeaderPrimary(function () { openGroupForm(); });

        api.groups.list().then(function (groups) {
            groups = groups || [];
            runtimeSummaryHandlers['group-management']({ groups: groups });
            // 鏇存柊鎸囨爣鍗?            var statCards = document.querySelectorAll('#mainHost .stat-card');
            if (statCards.length >= 3) {
                var v0 = statCards[0].querySelector('.stat-card__value');
                if (v0) v0.textContent = groups.length;
                var v1 = statCards[1].querySelector('.stat-card__value');
                if (v1) v1.textContent = '0';
                var v2 = statCards[2].querySelector('.stat-card__value');
                if (v2) v2.textContent = groups.length > 0 ? '100%' : '0%';
            }
            // 娓叉煋鍒嗙粍鍒楄〃
            var list = document.querySelector('#mainHost .workbench-list');
            if (!list) return;
            if (groups.length === 0) {
                list.innerHTML = '<div class="empty-state" style="padding:32px;text-align:center;"><p>鏆傛棤鍒嗙粍</p><p class="subtle">鐐瑰嚮銆屾柊寤哄垎缁勩€嶅紑濮嬬粍缁囪处鍙?/p></div>';
                return;
            }
            list.innerHTML = groups.map(function (g) {
                var color = g.color || '#6366f1';
                return '<div class="task-item" data-id="' + (g.id || '') + '" data-search="' + _esc((g.name || '') + ' ' + (g.description || '') + ' ' + (g.color || '')) + '" style="border-left:3px solid ' + _esc(color) + ';">'
                    + '<div><strong>' + _esc(g.name || '') + '</strong>'
                    + '<div class="subtle">' + _esc(g.description || '鏆傛棤鎻忚堪') + '</div></div>'
                    + '<div style="display:flex;gap:6px;align-items:center;">'
                    + '<button class="ghost-button js-edit-group" data-id="' + (g.id || '') + '">缂栬緫</button>'
                    + '<button class="ghost-button js-delete-group" data-id="' + (g.id || '') + '" style="color:var(--status-error);">鍒犻櫎</button>'
                    + '</div></div>';
            }).join('');
            _bindGroupActions(groups);
        }).catch(function (e) {
            console.warn('[page-loaders] group-management load failed:', e);
        });
    };

    function _bindGroupActions(groups) {
        document.querySelectorAll('#mainHost .workbench-list .task-item').forEach(function (item) {
            item.addEventListener('click', function (e) {
                if (e.target.closest('button')) return;
                document.querySelectorAll('#mainHost .workbench-list .task-item').forEach(function (node) { node.classList.remove('is-selected'); });
                item.classList.add('is-selected');
                var id = parseInt(item.dataset.id, 10);
                _renderGroupDetail((groups || []).find(function (g) { return g.id === id; }));
            });
        });
        document.querySelectorAll('.js-edit-group').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var id = parseInt(btn.dataset.id, 10);
                var grp = (groups || []).find(function (g) { return g.id === id; });
                if (grp) openGroupForm(grp);
                if (grp) _renderGroupDetail(grp);
            });
        });
        document.querySelectorAll('.js-delete-group').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var id = parseInt(btn.dataset.id, 10);
                if (!id) return;
                confirmModal({
                    title: '鍒犻櫎鍒嗙粍',
                    message: '鍒犻櫎鍒嗙粍涓嶄細鍒犻櫎缁勫唴璐﹀彿锛屼絾浼氳В闄ょ粦瀹氬叧绯汇€傜‘瀹氱户缁紵',
                    confirmText: '鍒犻櫎',
                    tone: 'danger',
                }).then(function (ok) {
                    if (!ok) return;
                    api.groups.remove(id).then(function () {
                        showToast('鍒嗙粍宸插垹闄?);
                        loaders['group-management']();
                    }).catch(function (err) {
                        showToast('鍒犻櫎澶辫触: ' + err.message, 'error');
                    });
                });
            });
        });
    }

    function _renderProviderDetail(provider) {
        if (!provider) return;
        var detailHost = document.getElementById('detailHost');
        if (!detailHost) return;
        var active = provider.is_active === true || provider.is_active === 'True';
        detailHost.innerHTML = '<div class="detail-root"><section class="panel"><div class="panel__header"><div><strong>' + _esc(provider.name || '渚涘簲鍟嗚鎯?) + '</strong><div class="subtle">' + _esc(provider.provider_type || '-') + '</div></div><span class="status-chip ' + (active ? 'success' : 'info') + '">' + (active ? '鍚敤涓? : '鏈惎鐢?) + '</span></div><div class="detail-list"><div class="detail-item"><span class="subtle">榛樿妯″瀷</span><strong>' + _esc(provider.default_model || '-') + '</strong></div><div class="detail-item"><span class="subtle">API 鍦板潃</span><strong>' + _esc(provider.api_base || '-') + '</strong></div><div class="detail-item"><span class="subtle">鏈€澶?Token</span><strong>' + _esc(provider.max_tokens || '-') + '</strong></div></div></section></div>';
    }

    function _renderGroupDetail(group) {
        if (!group) return;
        var detailHost = document.getElementById('detailHost');
        if (!detailHost) return;
        detailHost.innerHTML = '<div class="detail-root"><section class="panel"><div class="panel__header"><div><strong>' + _esc(group.name || '鍒嗙粍璇︽儏') + '</strong><div class="subtle">缁勭粐缂栨帓璇︽儏</div></div><span class="status-chip info">宸插姞杞?/span></div><div class="detail-list"><div class="detail-item"><span class="subtle">鎻忚堪</span><strong>' + _esc(group.description || '鏃?) + '</strong></div><div class="detail-item"><span class="subtle">棰滆壊</span><strong>' + _esc(group.color || '-') + '</strong></div><div class="detail-item"><span class="subtle">鍒嗙粍 ID</span><strong>' + _esc(group.id || '-') + '</strong></div></div></section></div>';
    }

    /* 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲
       Device Management 椤甸潰
       鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲 */
    loaders['device-management'] = function () {
        _wireHeaderPrimary(function () { openDeviceForm(); });

        api.devices.list().then(function (devices) {
            devices = devices || [];
            runtimeSummaryHandlers['device-management']({ devices: devices });
            // 鏇存柊鎸囨爣鍗?            var statCards = document.querySelectorAll('#mainHost .stat-card');
            if (statCards.length >= 4) {
                var v0 = statCards[0].querySelector('.stat-card__value');
                if (v0) v0.textContent = devices.length;
                var healthyCount = devices.filter(function (d) { return d.status === 'healthy'; }).length;
                var v1 = statCards[1].querySelector('.stat-card__value');
                if (v1) v1.textContent = devices.length > 0 ? Math.round(healthyCount / devices.length * 100) + '%' : '0%';
                var errCount = devices.filter(function (d) { return d.status === 'error'; }).length;
                var v2 = statCards[2].querySelector('.stat-card__value');
                if (v2) v2.textContent = errCount;
                var idleCount = devices.filter(function (d) { return d.status === 'idle'; }).length;
                var v3 = statCards[3].querySelector('.stat-card__value');
                if (v3) v3.textContent = idleCount;
            }
            // 鏇存柊 tabs
            var counts = { all: devices.length, healthy: 0, warning: 0, error: 0, idle: 0 };
            devices.forEach(function (d) {
                var s = (d.status || '').toLowerCase();
                if (counts[s] !== undefined) counts[s]++;
            });
            var tabs = document.querySelectorAll('#mainHost .local-tab');
            if (tabs.length >= 5) {
                tabs[0].textContent = '鍏ㄩ儴 (' + counts.all + ')';
                tabs[1].textContent = '姝ｅ父 (' + counts.healthy + ')';
                tabs[2].textContent = '鍛婅 (' + counts.warning + ')';
                tabs[3].textContent = '寮傚父 (' + counts.error + ')';
                tabs[4].textContent = '绌洪棽 (' + counts.idle + ')';
            }
            // 娓叉煋璁惧鍗＄墖
            var grid = document.querySelector('#mainHost .device-env-grid');
            if (!grid) return;
            if (devices.length === 0) {
                grid.innerHTML = '<div class="empty-state" style="padding:48px;text-align:center;grid-column:1/-1;"><p>鏆傛棤璁惧</p><p class="subtle">鐐瑰嚮銆屾柊澧炶澶囩幆澧冦€嶆坊鍔犵涓€鍙拌澶?/p></div>';
                return;
            }
            grid.innerHTML = devices.map(function (d, i) {
                var st = _deviceStatusMap(d.status);
                return '<article class="device-env-card device-env-card--' + (d.status || 'idle') + (i === 0 ? ' is-selected' : '') + '" data-id="' + (d.id || '') + '" data-status="' + _esc((d.status || 'idle').toLowerCase()) + '" data-search="' + _esc((d.name || '') + ' ' + (d.device_code || '') + ' ' + (d.proxy_ip || '') + ' ' + (d.region || '') + ' ' + (d.status || '')) + '">'
                    + '<div class="device-env-card__head"><strong>' + _esc(d.name || '') + '</strong><span class="status-chip ' + st.tone + '">' + st.label + '</span></div>'
                    + '<div class="device-env-card__meta">'
                    + '<div class="list-row"><span class="subtle">璁惧缂栫爜</span><strong class="mono">' + _esc(d.device_code || '-') + '</strong></div>'
                    + '<div class="list-row"><span class="subtle">浠ｇ悊 IP</span><strong class="mono">' + _esc(d.proxy_ip || '-') + '</strong></div>'
                    + '<div class="list-row"><span class="subtle">鍦板尯</span><strong>' + _esc(d.region || '-') + '</strong></div>'
                    + '</div>'
                    + '<div class="detail-actions">'
                    + '<button class="secondary-button js-edit-device" data-id="' + (d.id || '') + '">缂栬緫</button>'
                    + '<button class="danger-button js-delete-device" data-id="' + (d.id || '') + '">鍒犻櫎</button>'
                    + '</div></article>';
            }).join('');
            _bindDeviceActions(devices);
            _bindBatchBar('.js-batch-device', function (ids) {
                return _batchDelete(ids, api.devices.remove, '璁惧', 'device-management');
            });
        }).catch(function (e) {
            console.warn('[page-loaders] device-management load failed:', e);
        });
    };

    function _bindDeviceActions(devices) {
        document.querySelectorAll('#mainHost .device-env-card').forEach(function (card) {
            card.addEventListener('click', function (e) {
                if (e.target.closest('button') || e.target.closest('input')) return;
                document.querySelectorAll('#mainHost .device-env-card').forEach(function (node) { node.classList.remove('is-selected'); });
                card.classList.add('is-selected');
                var id = parseInt(card.dataset.id, 10);
                _renderDeviceDetail((devices || []).find(function (d) { return d.id === id; }));
            });
        });
        document.querySelectorAll('.js-edit-device').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var id = parseInt(btn.dataset.id, 10);
                var dev = (devices || []).find(function (d) { return d.id === id; });
                if (dev) openDeviceForm(dev);
                if (dev) _renderDeviceDetail(dev);
            });
        });
        document.querySelectorAll('.js-delete-device').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var id = parseInt(btn.dataset.id, 10);
                if (!id) return;
                confirmModal({
                    title: '鍒犻櫎璁惧',
                    message: '纭畾鍒犻櫎姝よ澶囷紵缁戝畾鐨勮处鍙峰叧绯诲皢鍚屾椂瑙ｉ櫎銆?,
                    confirmText: '鍒犻櫎',
                    tone: 'danger',
                }).then(function (ok) {
                    if (!ok) return;
                    api.devices.remove(id).then(function () {
                        showToast('璁惧宸插垹闄?);
                        loaders['device-management']();
                    }).catch(function (err) {
                        showToast('鍒犻櫎澶辫触: ' + err.message, 'error');
                    });
                });
            });
        });
    }

    function _renderDeviceDetail(device) {
        if (!device) return;
        var detailHost = document.getElementById('detailHost');
        if (!detailHost) return;
        var status = _deviceStatusMap(device.status);
        detailHost.innerHTML = '<div class="detail-root"><section class="panel"><div class="panel__header"><div><strong>' + _esc(device.name || '璁惧璇︽儏') + '</strong><div class="subtle mono">' + _esc(device.device_code || '-') + '</div></div><span class="status-chip ' + status.tone + '">' + _esc(status.label) + '</span></div><div class="detail-list"><div class="detail-item"><span class="subtle">浠ｇ悊 IP</span><strong>' + _esc(device.proxy_ip || '-') + '</strong></div><div class="detail-item"><span class="subtle">鍦板尯</span><strong>' + _esc(device.region || '-') + '</strong></div><div class="detail-item"><span class="subtle">鐘舵€?/span><strong>' + _esc(device.status || '-') + '</strong></div></div></section></div>';
    }

    function _deviceStatusMap(status) {
        var map = {
            healthy: { label: '姝ｅ父', tone: 'success' },
            warning: { label: '鍛婅', tone: 'warning' },
            error:   { label: '寮傚父', tone: 'error' },
            idle:    { label: '绌洪棽', tone: 'info' },
        };
        return map[(status || '').toLowerCase()] || { label: status || '鏈煡', tone: 'info' };
    }

    /* 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲
       AI Generation 椤甸潰
       鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲 */
    loaders['viral-title'] = function () {
        _loadAiGenerationPage({
            routeKey: 'viral-title',
            preset: 'title-generator',
            actionText: '鐢熸垚鏍囬鏂规',
            inputSelector: '#mainHost .title-editor-textarea',
            triggerSelectors: ['#mainHost .page-header .primary-button', '#mainHost .title-editor-actions .primary-button'],
            beforeCall: function (input) {
                return '璇峰熀浜庝互涓嬩富棰樼敓鎴?3 涓€傚悎 TikTok Shop 鐨勭垎娆炬爣棰樻柟妗堬紝骞剁畝瑕佽鏄庨€傜敤鍦烘櫙锛歕n' + input;
            },
            renderResult: function (result, input) {
                var variants = _extractAiItems(result.content, 3);
                _renderVariantList('#mainHost .variant-list', variants, '鏂规');
                var metricCards = document.querySelectorAll('#mainHost .title-metric-grid .mini-metric-card');
                if (metricCards.length >= 3) {
                    metricCards[0].querySelector('strong').textContent = _calcTitleScore(variants[0] || input) + ' / 10';
                    metricCards[0].querySelector('small').textContent = '鍩轰簬褰撳墠杈撳嚭闀垮害涓庨挬瀛愬瘑搴︿及绠?;
                    metricCards[1].querySelector('strong').textContent = String(Math.min(98, 72 + Math.max(0, result.total_tokens || 0) / 8)).slice(0, 2) + '%';
                    metricCards[1].querySelector('small').textContent = '渚涘簲鍟嗭細' + (result.provider || '-');
                    metricCards[2].querySelector('strong').textContent = Math.min(99, 78 + variants.length * 5) + '%';
                    metricCards[2].querySelector('small').textContent = '鑰楁椂 ' + _formatElapsed(result.elapsed_ms) + ' / ' + (result.model || '-');
                }
                var textarea = document.querySelector('#mainHost .title-editor-textarea');
                if (textarea && variants[0]) textarea.value = variants[0];
            },
            bindExtra: function () {
                document.querySelectorAll('#mainHost .template-showcase-card').forEach(function (card) {
                    card.addEventListener('click', function () {
                        var templateName = extractTextFromEl(card, 'strong');
                        var textarea = document.querySelector('#mainHost .title-editor-textarea');
                        if (!textarea || !templateName) return;
                        textarea.value = templateName + '锝? + textarea.value;
                    });
                });
            },
        });
    };

    loaders['product-title'] = function () {
        _loadAiGenerationPage({
            routeKey: 'product-title',
            preset: 'seo-optimizer',
            actionText: '浼樺寲鍟嗗搧鏍囬',
            inputSelector: '#mainHost .product-input-row input',
            triggerSelectors: ['#mainHost .page-header .primary-button', '#mainHost .product-input-row .primary-button'],
            beforeCall: function (input) {
                return '璇锋妸浠ヤ笅鍟嗗搧鏍囬浼樺寲涓?2 涓増鏈細楂樿浆鍖栫増鍜?SEO 鐗堛€傝姹備繚鐣欐牳蹇冨搧绫昏瘝锛屽苟璇存槑鎺ㄨ崘鍦烘櫙銆俓n鍟嗗搧鏍囬锛? + input;
            },
            renderResult: function (result, input) {
                var variants = _extractAiItems(result.content, 2);
                _renderVariantList('#mainHost .product-result-board .variant-list', variants, ['楂樿浆鍖栧瀷', 'SEO 鍔犲己鍨?]);
                var detailItems = document.querySelectorAll('#mainHost .product-insight-grid .detail-item strong');
                if (detailItems.length >= 3) {
                    var tokens = _keywordChunks(input);
                    detailItems[0].textContent = (tokens[0] || '鏍稿績璇?) + ' ' + _keywordDensity(input, tokens[0]) + '%';
                    detailItems[1].textContent = (tokens[1] || '灞炴€ц瘝') + ' ' + _keywordDensity(input, tokens[1]) + '%';
                    detailItems[2].textContent = (tokens[2] || '淇グ璇?) + ' ' + _keywordDensity(input, tokens[2]) + '%';
                }
            },
        });
    };

    loaders['ai-copywriter'] = function () {
        _loadAiGenerationPage({
            routeKey: 'ai-copywriter',
            preset: 'copywriter',
            actionText: '鐢熸垚钀ラ攢鏂囨',
            inputSelector: '#mainHost .copy-settings-column textarea',
            triggerSelectors: ['#mainHost .page-header .primary-button'],
            beforeCall: function (input) {
                var toneBtn = document.querySelector('#mainHost .copy-tone-list .is-active');
                var tone = toneBtn ? toneBtn.textContent.trim() : '涓撲笟涓ヨ皑';
                return '璇风敤鈥? + tone + '鈥濊姘旓紝鍩轰簬浠ヤ笅浜у搧淇℃伅鐢熸垚 3 涓枃妗堢増鏈紝骞跺崟鐙粰鍑轰竴鏉￠闄╄閬垮缓璁€俓n' + input;
            },
            renderResult: function (result) {
                var variants = _extractAiItems(result.content, 3);
                _renderVariantList('#mainHost .copy-results-column .variant-list', variants, ['Variant 01', 'Variant 02', 'Variant 03']);
                _renderCompliance('#mainHost .copy-compliance-column', result.content);
            },
            bindExtra: function () {
                var buttons = document.querySelectorAll('#mainHost .copy-tone-list button');
                buttons.forEach(function (btn) {
                    btn.addEventListener('click', function () {
                        buttons.forEach(function (b) { b.classList.remove('is-active'); });
                        btn.classList.add('is-active');
                    });
                });
            },
        });
    };

    loaders['script-extractor'] = function () {
        _loadAiGenerationPage({
            routeKey: 'script-extractor',
            preset: 'script-extractor',
            actionText: '鎻愬彇鑴氭湰缁撴瀯',
            inputSelector: '#mainHost .extractor-url-field input',
            triggerSelectors: ['#mainHost .page-header .primary-button'],
            beforeCall: function (input) {
                return '璇峰熀浜庝互涓嬭棰戦摼鎺ユ垨鎻忚堪锛岃緭鍑鸿剼鏈椂闂磋酱銆佺粨鏋勬爣绛惧拰鍙鐢ㄧ粨璁恒€俓n杈撳叆锛? + input;
            },
            renderResult: function (result, input) {
                _renderExtractorResult(result.content);
                var progressText = document.querySelector('#mainHost .extractor-progress-row strong');
                if (progressText) progressText.textContent = '100%';
                var progressBar = document.querySelector('#mainHost .progress-bar span');
                if (progressBar) progressBar.style.width = '100%';
                var summary = document.querySelector('#mainHost .extractor-preview-column .panel p.subtle');
                if (summary) summary.textContent = '宸插畬鎴愮粨鏋勬彁鍙栵細鏉ユ簮 ' + input + '锛屾ā鍨?' + (result.model || '-') + '锛屾€?tokens ' + (result.total_tokens || 0) + '銆?;
            },
        });
    };

    /* 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲
       Asset Center 椤甸潰
       鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲 */
    loaders['asset-center'] = function () {
        _wireHeaderPrimary(function () { openAssetForm(); }, '涓婁紶绱犳潗');
        Promise.all([
            api.assets.list().catch(function () { return []; }),
            api.assets.stats().catch(function () { return { total: 0, byType: {} }; }),
        ]).then(function (results) {
            var assets = results[0] || [];
            var stats = results[1] || { total: 0, byType: {} };
            var currentType = 'all';

            runtimeSummaryHandlers['asset-center']({ assets: assets, stats: stats });
            _updateAssetStats(assets, stats);
            _renderAssetCategories(stats.byType || {}, assets.length);

            function renderGrid(type) {
                currentType = type || 'all';
                var filtered = currentType === 'all'
                    ? assets.slice()
                    : assets.filter(function (asset) { return (asset.asset_type || '').toLowerCase() === currentType; });
                var grid = document.querySelector('#mainHost .asset-source-grid');
                if (!grid) return;
                if (!filtered.length) {
                    grid.innerHTML = '<div class="empty-state" style="padding:32px;text-align:center;grid-column:1/-1;"><p>鏆傛棤璇ュ垎绫荤礌鏉?/p><p class="subtle">褰撳墠鍒嗙被涓嬫病鏈夊彲灞曠ず鐨勭礌鏉愯褰?/p></div>';
                    return;
                }
                grid.innerHTML = filtered.slice(0, 12).map(function (asset, index) {
                    return _buildAssetThumb(asset, index === 0);
                }).join('');
                _bindAssetThumbs(filtered);
                _renderAssetDetail(filtered[0]);
                if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
            }

            renderGrid('all');
            document.querySelectorAll('#mainHost .asset-category-item').forEach(function (btn) {
                btn.addEventListener('click', function () {
                    document.querySelectorAll('#mainHost .asset-category-item').forEach(function (item) {
                        item.classList.remove('is-active');
                    });
                    btn.classList.add('is-active');
                    renderGrid(btn.dataset.assetType || 'all');
                });
            });
        }).catch(function (e) {
            console.warn('[page-loaders] asset-center load failed:', e);
        });
    };

    /* 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲
       System Settings 椤甸潰
       鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲 */
    loaders['system-settings'] = function () {
        Promise.all([
            api.settings.all().catch(function () { return {}; }),
            api.theme.get().catch(function () { return 'light'; }),
            api.version.current().catch(function () { return { version: '-' }; }),
        ]).then(function (results) {
            var settings = results[0] || {};
            var theme = results[1] || 'light';
            var version = results[2] || { version: '-' };
            _materializeSettingsControls(settings, theme);
            _updateSettingsSummary(settings, theme, version);
            _bindSystemSettingsActions(settings, theme);
            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (e) {
            console.warn('[page-loaders] system-settings load failed:', e);
        });
    };

    /* 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲
       Analytics 椤甸潰
       鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲 */
    loaders['visual-lab'] = function () {
        Promise.all([
            api.analytics.summary().catch(function () { return {}; }),
            api.experiments.projects().catch(function () { return []; }),
            api.experiments.views().catch(function () { return []; }),
        ]).then(function (results) {
            var summary = results[0] || {};
            var projects = results[1] || [];
            var views = results[2] || [];
            var stats = {
                accounts: summary.accounts || {},
                tasks: summary.tasks || {},
                assets: summary.assets || {},
                providers: summary.providers || {},
            };
            var assetStats = { total: (summary.assets && summary.assets.total) || 0, byType: (summary.assets && summary.assets.by_type) || {} };
            var providers = new Array((summary.providers && summary.providers.total) || 0).fill({});
            var cards = document.querySelectorAll('#mainHost .stat-grid .stat-card');
            if (cards.length >= 3) {
                cards[0].querySelector('.stat-card__value').textContent = String(projects.length || ((summary.experiments && summary.experiments.projects) || 0));
                cards[1].querySelector('.stat-card__value').textContent = String(Math.max(views.length, Object.keys(assetStats.byType || {}).length));
                cards[2].querySelector('.stat-card__value').textContent = ((summary.providers && summary.providers.models) || []).length + ' 涓?;
            }
            var sourceList = document.querySelector('#mainHost .data-source-list');
            if (sourceList) {
                sourceList.innerHTML = [
                    { title: '瀹為獙椤圭洰', meta: '椤圭洰 ' + projects.length + ' / 鎸佷箙鍖栧悓姝? },
                    { title: '瀹為獙瑙嗗浘', meta: '瑙嗗浘 ' + views.length + ' / 鍙敤浜庡鐓? },
                    { title: '绱犳潗璧勪骇搴?, meta: '绱犳潗 ' + (assetStats.total || 0) + ' / 宸茶繛鎺? },
                    { title: 'AI 妯″瀷姹?, meta: '妯″瀷 ' + (((summary.providers && summary.providers.models) || []).length) + ' / 鍙敤' },
                ].map(function (item, index) {
                    return '<button class="data-source-item ' + (index === 0 ? 'is-selected' : '') + '" type="button"><strong>' + _esc(item.title) + '</strong><span>' + _esc(item.meta) + '</span></button>';
                }).join('');
            }
            var overlay = document.querySelectorAll('#mainHost .visual-preview-overlay span');
            if (overlay.length >= 3) {
                overlay[0].textContent = '椤圭洰 ' + projects.length;
                overlay[1].textContent = '瑙嗗浘 ' + views.length;
                overlay[2].textContent = '绱犳潗 ' + (assetStats.total || 0);
            }
            _setAnalyticsSeed({
                visualTrend: [
                    projects.length,
                    views.length,
                    assetStats.total || 0,
                    (summary.providers && summary.providers.active) || 0,
                    ((summary.providers && summary.providers.models) || []).length,
                ],
            });
            _bindAnalyticsHeaderActions('visual-lab', { stats: stats, assets: assetStats, providers: providers, experiments: projects, views: views });
            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (e) {
            console.warn('[page-loaders] visual-lab load failed:', e);
        });
    };

    loaders['profit-analysis'] = function () {
        Promise.all([
            api.analytics.summary().catch(function () { return {}; }),
            api.analytics.conversion().catch(function () { return { counts: {}, funnel: [] }; }),
        ]).then(function (results) {
            var summary = results[0] || {};
            var conversion = results[1] || { counts: {}, funnel: [] };
            var counts = conversion.counts || {};
            var accountsTotal = (summary.accounts && summary.accounts.total) || 0;
            var activeAccounts = (summary.accounts && summary.accounts.active) || 0;
            var assetsTotal = (summary.assets && summary.assets.total) || 0;
            var completedTasks = counts.completed_tasks || (summary.tasks && summary.tasks.completed) || 0;
            var failedTasks = (summary.tasks && summary.tasks.failed) || 0;
            var cards = document.querySelectorAll('#mainHost .stat-grid .stat-card');
            if (cards.length >= 4) {
                cards[0].querySelector('.stat-card__value').textContent = _formatNum(completedTasks);
                cards[1].querySelector('.stat-card__value').textContent = _formatNum(failedTasks);
                cards[2].querySelector('.stat-card__value').textContent = _formatNum(assetsTotal);
                cards[3].querySelector('.stat-card__value').textContent = _formatNum(activeAccounts);
            }
            var costGrid = document.querySelectorAll('#mainHost .profit-ledger-grid article');
            if (costGrid.length >= 4) {
                costGrid[0].querySelector('strong').textContent = _formatNum(completedTasks);
                costGrid[1].querySelector('strong').textContent = _formatNum(activeAccounts);
                costGrid[2].querySelector('strong').textContent = _formatNum(failedTasks);
                costGrid[3].querySelector('strong').textContent = _formatNum(assetsTotal);
            }
            var tbody = document.querySelector('#mainHost .table-wrapper tbody');
            if (tbody) {
                tbody.innerHTML = _buildTruthfulProfitRows(summary, conversion).join('');
            }
            _setAnalyticsSeed({
                profitBars: [
                    Math.max(24, Math.min(88, activeAccounts * 8 + 24)),
                    Math.max(26, Math.min(92, completedTasks * 10 + 26)),
                ],
            });
            _bindAnalyticsHeaderActions('profit-analysis', { summary: summary, conversion: conversion, accounts: new Array(accountsTotal), tasks: new Array((summary.tasks && summary.tasks.total) || 0), assets: { total: assetsTotal } });
            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (e) {
            console.warn('[page-loaders] profit-analysis load failed:', e);
        });
    };

    loaders['competitor-monitor'] = function () {
        Promise.all([
            api.analytics.competitor().catch(function () { return { metrics: {}, rivals: [], rows: [], bars: [] }; }),
            api.accounts.list().catch(function () { return []; }),
            api.tasks.list().catch(function () { return []; }),
        ]).then(function (results) {
            var analysis = results[0] || { metrics: {}, rivals: [], rows: [], bars: [] };
            var accounts = results[1] || [];
            var tasks = results[2] || [];
            var metrics = analysis.metrics || {};
            var cards = document.querySelectorAll('#mainHost .stat-grid .stat-card');
            if (cards.length >= 3) {
                cards[0].querySelector('.stat-card__value').textContent = String(metrics.monitored_accounts || 0);
                cards[1].querySelector('.stat-card__value').textContent = String(metrics.failed_tasks || 0);
                cards[2].querySelector('.stat-card__value').textContent = String(metrics.regions || 0);
            }
            var rivalStrip = document.querySelector('#mainHost .rival-strip');
            if (rivalStrip) {
                rivalStrip.innerHTML = (analysis.rivals || []).slice(0, 4).map(function (item, index) {
                    var name = item.name || ('璐﹀彿 ' + (index + 1));
                    return '<article class="rival-card ' + (index === 0 ? 'is-self' : '') + '"><div class="rival-avatar">' + _esc(name.slice(0, 1).toUpperCase()) + '</div><strong>' + _esc(name) + '</strong><span>' + _formatNum(item.followers || 0) + '</span><em class="' + _esc(item.tone || 'info') + '">' + _esc(item.delta || '鎸佺画璺熻釜') + '</em></article>';
                }).join('');
            }
            var tbody = document.querySelector('#mainHost .table-wrapper tbody');
            if (tbody) {
                tbody.innerHTML = (analysis.rows || []).slice(0, 4).map(function (row) {
                    return '<tr class="route-row" data-search="' + _esc((row.title || '') + ' ' + (row.meta || '')) + '"><td><strong>' + _esc(row.title || '璐﹀彿') + '</strong></td><td>' + _formatNum(row.value || 0) + '</td><td>' + _esc(row.meta || '绛夊緟鏁版嵁') + '</td><td>' + _esc(row.conclusion || '缁х画瑙傚療') + '</td></tr>';
                }).join('');
            }
            _setAnalyticsSeed({
                rivalBars: (analysis.bars || []).slice(0, 6),
            });
            _bindAnalyticsHeaderActions('competitor-monitor', { accounts: accounts, tasks: tasks });
            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (e) {
            console.warn('[page-loaders] competitor-monitor load failed:', e);
        });
    };

    loaders['traffic-board'] = function () {
        Promise.all([
            api.analytics.traffic().catch(function () { return { metrics: {}, sources: [], rows: [], trend: [] }; }),
            api.accounts.list().catch(function () { return []; }),
            api.tasks.list().catch(function () { return []; }),
        ]).then(function (results) {
            var analysis = results[0] || { metrics: {}, sources: [], rows: [], trend: [] };
            var accounts = results[1] || [];
            var tasks = results[2] || [];
            var metrics = analysis.metrics || {};
            var cards = document.querySelectorAll('#mainHost .stat-grid .stat-card');
            if (cards.length >= 3) {
                cards[0].querySelector('.stat-card__value').textContent = _formatNum(metrics.account_sample || 0);
                cards[1].querySelector('.stat-card__value').textContent = String(metrics.task_completion_rate || 0) + '%';
                cards[2].querySelector('.stat-card__value').textContent = String(metrics.failed_tasks || 0);
            }
            var sourceCards = document.querySelectorAll('#mainHost .traffic-source-grid .traffic-source-card');
            if (sourceCards.length >= 3) {
                (analysis.sources || []).slice(0, 3).forEach(function (item, index) {
                    _setTrafficSourceCard(sourceCards[index], item.value || 0, item.meta || '绛夊緟鏁版嵁');
                });
            }
            var tbody = document.querySelector('#mainHost .table-wrapper tbody');
            if (tbody) {
                tbody.innerHTML = (analysis.rows || []).slice(0, 4).map(function (row) {
                    return '<tr class="route-row" data-search="' + _esc((row.label || '') + ' ' + (row.reason || '')) + '"><td><strong>' + _esc(row.label || '鍖哄煙') + '</strong></td><td>' + _esc(row.delta || '绛夊緟鏁版嵁') + '</td><td>' + _esc(row.reason || '绛夊緟鏁版嵁') + '</td><td>' + _esc(row.action || '缁х画瑙傚療') + '</td></tr>';
                }).join('');
            }
            _setAnalyticsSeed({
                trafficTrend: (analysis.trend || []).slice(0, 12),
            });
            _bindAnalyticsHeaderActions('traffic-board', { stats: analysis, accounts: accounts, tasks: tasks });
            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (e) {
            console.warn('[page-loaders] traffic-board load failed:', e);
        });
    };

    loaders['blue-ocean'] = function () {
        Promise.all([
            api.analytics.blueOcean().catch(function () { return { metrics: {}, topics: [], lead: {}, matrix: [] }; }),
            api.accounts.list().catch(function () { return []; }),
            api.assets.stats().catch(function () { return { total: 0, byType: {} }; }),
            api.tasks.list().catch(function () { return []; }),
        ]).then(function (results) {
            var analysis = results[0] || { metrics: {}, topics: [], lead: {}, matrix: [] };
            var accounts = results[1] || [];
            var assetStats = results[2] || { total: 0, byType: {} };
            var tasks = results[3] || [];
            var metrics = analysis.metrics || {};
            var cards = document.querySelectorAll('#mainHost .stat-grid .stat-card');
            if (cards.length >= 3) {
                cards[0].querySelector('.stat-card__value').textContent = String(metrics.candidate_topics || 0);
                cards[1].querySelector('.stat-card__value').textContent = String(metrics.asset_topics || 0);
                cards[2].querySelector('.stat-card__value').textContent = String(metrics.failed_tasks || 0);
            }
            var bubbles = document.querySelectorAll('#mainHost .matrix-bubble');
            var bubbleLabels = (analysis.topics || []).length ? analysis.topics : _buildBlueOceanTopics(accounts, assetStats);
            bubbles.forEach(function (bubble, index) {
                if (bubbleLabels[index]) bubble.textContent = bubbleLabels[index];
            });
            var detailCard = document.querySelector('#mainHost .opportunity-detail-card');
            if (detailCard) {
                var lead = analysis.lead || {};
                var title = detailCard.querySelector('strong');
                var statsList = detailCard.querySelectorAll('.detail-item strong');
                var desc = detailCard.querySelector('p');
                if (title) title.textContent = lead.title || bubbleLabels[0] || '鍐呭鏈轰細';
                if (statsList.length >= 3) {
                    statsList[0].textContent = String(lead.heat || 0);
                    statsList[1].textContent = String(lead.competition || 0);
                    statsList[2].textContent = String(lead.coverage || 0) + '%';
                }
                if (desc) desc.textContent = lead.description || '鏈轰細鍒ゆ柇宸叉牴鎹处鍙枫€佺礌鏉愪笌浠诲姟鍙嶉鑷姩鍒锋柊銆?;
            }
            _setAnalyticsSeed({
                blueOcean: (analysis.matrix || []).map(function (item) {
                    return {
                        label: item.label,
                        heat: item.heat,
                        competition: item.competition,
                        margin: item.coverage,
                    };
                }),
            });
            _bindAnalyticsHeaderActions('blue-ocean', { accounts: accounts, tasks: tasks, assets: assetStats });
            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (e) {
            console.warn('[page-loaders] blue-ocean load failed:', e);
        });
    };

    loaders['report-center'] = function () {
        Promise.all([
            api.reports.list().catch(function () { return []; }),
            api.analytics.summary().catch(function () { return {}; }),
            api.activity.list().catch(function () { return []; }),
        ]).then(function (results) {
            var reports = results[0] || [];
            var summary = results[1] || {};
            var activity = results[2] || [];
            var cards = document.querySelectorAll('#mainHost .stat-grid .stat-card');
            if (cards.length >= 3) {
                cards[0].querySelector('.stat-card__value').textContent = String(reports.length);
                cards[1].querySelector('.stat-card__value').textContent = String(reports.filter(function (report) {
                    return String(report.status || '').toLowerCase() !== 'completed';
                }).length);
                cards[2].querySelector('.stat-card__value').textContent = String(activity.length);
            }
            var templates = document.querySelectorAll('#mainHost .report-template-list .data-source-item');
            templates.forEach(function (item, index) {
                var title = item.querySelector('strong');
                var meta = item.querySelector('span');
                if (title && meta) {
                    var report = reports[index];
                    title.textContent = report ? (report.title || ('鎶ュ憡 ' + (index + 1))) : (['缁忚惀鏃ユ姤', '鍒╂鼎涓撻', '浜掑姩娲炲療', '钃濇捣璋冪爺'][index] || ('妯℃澘 ' + (index + 1)));
                    meta.textContent = report ? ('鐘舵€?' + (report.status || 'pending')) : '绛夊緟鐢熸垚';
                }
            });
            var previewRows = document.querySelectorAll('#mainHost .report-preview-table div span');
            if (previewRows.length >= 3) {
                previewRows[0].textContent = '褰撳墠宸叉矇娣€ ' + reports.length + ' 浠芥姤鍛婅褰?;
                previewRows[1].textContent = '鏈€杩戞椿鍔ㄦ棩蹇?' + activity.length + ' 鏉★紝鍙拷韪姤鍛婂姩浣?;
                previewRows[2].textContent = '璐﹀彿鎬婚噺 ' + ((summary.accounts && summary.accounts.total) || 0) + ' / 绱犳潗鎬婚噺 ' + ((summary.assets && summary.assets.total) || 0);
            }
            _setAnalyticsSeed({
                reportTrend: [reports.length, activity.length, ((summary.accounts && summary.accounts.total) || 0), ((summary.assets && summary.assets.total) || 0)],
            });
            _bindAnalyticsHeaderActions('report-center', { reports: reports, activity: activity, summary: summary, accounts: new Array((summary.accounts && summary.accounts.total) || 0), tasks: [], assets: { total: ((summary.assets && summary.assets.total) || 0) } });
            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (e) {
            console.warn('[page-loaders] report-center load failed:', e);
        });
    };

    loaders['interaction-analysis'] = function () {
        Promise.all([
            api.analytics.interaction().catch(function () { return { metrics: {}, sentiment: {}, keywords: [], heatmap: [], affinity: [] }; }),
            api.accounts.list().catch(function () { return []; }),
            api.tasks.list().catch(function () { return []; }),
            api.assets.list().catch(function () { return []; }),
        ]).then(function (results) {
            var analysis = results[0] || { metrics: {}, sentiment: {}, keywords: [], heatmap: [], affinity: [] };
            var accounts = results[1] || [];
            var tasks = results[2] || [];
            var assets = results[3] || [];
            var metrics = analysis.metrics || {};
            var sentiment = analysis.sentiment || {};
            var cards = document.querySelectorAll('#mainHost .stat-grid .stat-card');
            if (cards.length >= 3) {
                cards[0].querySelector('.stat-card__value').textContent = _formatNum(metrics.followers_total || 0);
                cards[1].querySelector('.stat-card__value').textContent = String(metrics.positive_share || 0) + '%';
                cards[2].querySelector('.stat-card__value').textContent = String(metrics.risk_items || 0);
            }
            var donut = document.querySelector('#mainHost .sentiment-donut__inner strong');
            if (donut) donut.textContent = String(sentiment.positive || 0) + '%';
            var legends = document.querySelectorAll('#mainHost .sentiment-legend span');
            if (legends.length >= 3) {
                legends[0].lastChild.textContent = '姝ｅ悜 ' + String(sentiment.positive || 0) + '%';
                legends[1].lastChild.textContent = '涓珛 ' + String(sentiment.neutral || 0) + '%';
                legends[2].lastChild.textContent = '璐熷悜 ' + String(sentiment.negative || 0) + '%';
            }
            var keywordCloud = document.querySelector('#mainHost .keyword-cloud');
            if (keywordCloud) {
                keywordCloud.innerHTML = (analysis.keywords || []).map(function (keyword, index) {
                    var size = index === 0 ? 'xl' : index < 3 ? 'lg' : index < 5 ? 'md' : 'sm';
                    return '<span class="' + size + '">' + _esc(keyword) + '</span>';
                }).join('');
            }
            _setAnalyticsSeed({
                heatmap: analysis.heatmap || [],
                affinity: analysis.affinity || [],
            });
            _bindAnalyticsHeaderActions('interaction-analysis', { accounts: accounts, tasks: tasks, assets: assets });
            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (e) {
            console.warn('[page-loaders] interaction-analysis load failed:', e);
        });
    };

    loaders['ecommerce-conversion'] = function () {
        Promise.all([
            api.analytics.conversion().catch(function () { return { counts: {}, funnel: [] }; }),
            api.analytics.summary().catch(function () { return {}; }),
        ]).then(function (results) {
            var conversion = results[0] || { counts: {}, funnel: [] };
            var summary = results[1] || {};
            var counts = conversion.counts || {};
            var cards = document.querySelectorAll('#mainHost .stat-grid .stat-card');
            if (cards.length >= 3) {
                cards[0].querySelector('.stat-card__value').textContent = _safePercent(counts.active_accounts, counts.accounts);
                cards[1].querySelector('.stat-card__value').textContent = _safePercent(counts.completed_tasks, counts.tasks);
                cards[2].querySelector('.stat-card__value').textContent = _safePercent(counts.assets, counts.completed_tasks || counts.tasks);
            }
            var steps = document.querySelectorAll('#mainHost .funnel-step strong');
            if (steps.length >= 5 && conversion.funnel) {
                conversion.funnel.forEach(function (step, index) {
                    if (steps[index]) steps[index].textContent = _formatNum(step.value || 0);
                });
                _setAnalyticsSeed({
                    funnel: conversion.funnel.map(function (step) { return step.value || 0; }),
                });
            }
            _bindAnalyticsHeaderActions('ecommerce-conversion', { conversion: conversion, summary: summary, accounts: new Array(counts.accounts || 0), tasks: new Array(counts.tasks || 0), assets: { total: counts.assets || 0 } });
            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (e) {
            console.warn('[page-loaders] ecommerce-conversion load failed:', e);
        });
    };

    loaders['fan-profile'] = function () {
        Promise.all([
            api.analytics.persona().catch(function () { return { segments: [], regions: [], interest_clusters: [] }; }),
            api.analytics.summary().catch(function () { return {}; }),
        ]).then(function (results) {
            var persona = results[0] || { segments: [], regions: [], interest_clusters: [] };
            var summary = results[1] || {};
            var assetsTotal = (summary.assets && summary.assets.total) || 0;
            var tasksTotal = (summary.tasks && summary.tasks.total) || 0;
            var accountsTotal = (summary.accounts && summary.accounts.total) || 0;
            var cards = document.querySelectorAll('#mainHost .stat-grid .stat-card');
            if (cards.length >= 3) {
                cards[0].querySelector('.stat-card__value').textContent = _formatNum((persona.segments[0] && persona.segments[0].count) || 0);
                cards[1].querySelector('.stat-card__value').textContent = String(persona.segments.length || 0);
                cards[2].querySelector('.stat-card__value').textContent = String((persona.interest_clusters || []).length || 0);
            }
            var affinityBars = document.querySelectorAll('#mainHost .affinity-bars div');
            if (affinityBars.length >= 4) {
                (persona.segments || []).slice(0, 4).forEach(function (segment, index) {
                    _setAffinityBar(affinityBars[index], Math.max(18, Math.min(96, 22 + (segment.count || 0) * 14)), segment.label || segment.key || ('鍒嗗眰 ' + (index + 1)));
                });
            }
            _setAnalyticsSeed({
                affinity: (persona.segments || []).slice(0, 4).map(function (segment) {
                    return Math.max(18, Math.min(96, 22 + (segment.count || 0) * 14));
                }),
            });
            _bindAnalyticsHeaderActions('fan-profile', { persona: persona, summary: summary, accounts: new Array(accountsTotal), tasks: new Array(tasksTotal), assets: { total: assetsTotal } });
            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (e) {
            console.warn('[page-loaders] fan-profile load failed:', e);
        });
    };

    loaders['auto-reply'] = function () { _loadTaskOpsPage({ routeKey: 'auto-reply', title: '鑷姩鍥炲', tableMode: 'reply' }); };
    loaders['scheduled-publish'] = function () { _loadTaskOpsPage({ routeKey: 'scheduled-publish', title: '瀹氭椂鍙戝竷', tableMode: 'publish' }); };
    loaders['task-hall'] = function () { _loadTaskOpsPage({ routeKey: 'task-hall', title: '浠诲姟澶у巺', tableMode: 'generic' }); };
    loaders['data-collector'] = function () { _loadTaskOpsPage({ routeKey: 'data-collector', title: '鏁版嵁閲囬泦鍔╂墜', tableMode: 'collector' }); };
    loaders['auto-like'] = function () { _loadTaskOpsPage({ routeKey: 'auto-like', title: '鑷姩鐐硅禐', tableMode: 'interaction' }); };
    loaders['auto-comment'] = function () { _loadTaskOpsPage({ routeKey: 'auto-comment', title: '鑷姩璇勮', tableMode: 'interaction' }); };
    loaders['auto-message'] = function () { _loadTaskOpsPage({ routeKey: 'auto-message', title: '鑷姩绉佷俊', tableMode: 'interaction' }); };
    loaders['task-scheduler'] = function () { _loadTaskOpsPage({ routeKey: 'task-scheduler', title: '浠诲姟璋冨害', tableMode: 'calendar' }); };

    loaders['video-editor'] = function () {
        Promise.all([
            api.assets.list().catch(function () { return []; }),
            api.tasks.list().catch(function () { return []; }),
        ]).then(function (results) {
            var assets = results[0] || [];
            var tasks = results[1] || [];
            _renderWorkbenchSummary([
                { label: '褰撳墠搴忓垪', value: '绱犳潗 ' + assets.length + ' 鏉?, note: '宸叉帴鍏ョ湡瀹炵礌鏉愬簱涓庢椂闂寸嚎鍊欓€夈€? },
                { label: '鏈В鍐抽樆濉?, value: String(tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'failed'; }).length) + ' 涓?, note: '寮傚父浠诲姟浼氶樆濉炲鍑轰笌鎵瑰鐞嗐€? },
                { label: '瀵煎嚭闃熷垪', value: String(tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'running'; }).length) + ' 涓帓闃?, note: '杩愯涓换鍔″凡鏄犲皠涓哄鍑烘垨澶勭悊闃熷垪銆? },
            ]);
            _renderVideoEditorAssets(assets);
            _renderWorkbenchSideCards(tasks, '#mainHost .workbench-side-list');
            _renderStripCards(tasks, '#mainHost .video-queue-list');
            _applyAiHandoffHint('video-editor', '#mainHost .video-queue-list');
            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (e) {
            console.warn('[page-loaders] video-editor load failed:', e);
        });
    };

    loaders['creative-workshop'] = function () {
        Promise.all([
            api.accounts.list().catch(function () { return []; }),
            api.assets.list().catch(function () { return []; }),
            api.tasks.list().catch(function () { return []; }),
            api.experiments.projects().catch(function () { return []; }),
        ]).then(function (results) {
            var accounts = results[0] || [];
            var assets = results[1] || [];
            var tasks = results[2] || [];
            var projects = results[3] || [];
            _renderWorkbenchSummary([
                { label: '褰撳墠瀹為獙', value: projects[0] ? (projects[0].name || '瀹為獙宸蹭繚瀛?) : (accounts.length ? (accounts[0].region || '澶氬湴鍖哄疄楠?) : '瀹為獙寰呭惎鍔?), note: '璐﹀彿涓庡湴鍩熺粨鏋勫凡鍚屾杩涘垱鎰忓姣斻€?},
                { label: '寰呭喅绛?, value: String(Math.max(2, tasks.length)) + ' 缁?, note: '鏉ヨ嚜鐪熷疄浠诲姟姹犵殑鎵ц鍙嶉宸插洖鍐欍€?},
                { label: '淇濈暀鍊惧悜', value: assets.length > 3 ? '绱犳潗鍏呭垎' : '绱犳潗鍋忓皯', note: '浼樺厛閫夋嫨鏈夎冻澶熺礌鏉愭敮鎾戠殑鏂规銆?},
            ]);
            _renderCreativeFocusCards(accounts, assets, tasks);
            _renderWorkbenchSideCards(tasks, '#mainHost .workbench-side-list');
            _renderStripCards(assets, '#mainHost .workbench-strip-grid', 'asset');
            _applyAiHandoffHint('creative-workshop', '#mainHost .workbench-strip-grid');
            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (e) {
            console.warn('[page-loaders] creative-workshop load failed:', e);
        });
    };

    loaders['visual-editor'] = function () {
        Promise.all([
            api.assets.list().catch(function () { return []; }),
            api.tasks.list().catch(function () { return []; }),
        ]).then(function (results) {
            var assets = results[0] || [];
            var tasks = results[1] || [];
            var cards = document.querySelectorAll('#mainHost .stat-grid .stat-card');
            if (cards.length >= 3) {
                cards[0].querySelector('.stat-card__value').textContent = assets.length ? '1080脳1920' : '寰呴厤缃?;
                cards[1].querySelector('.stat-card__value').textContent = String(Math.max(1, assets.length));
                cards[2].querySelector('.stat-card__value').textContent = String(tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'running'; }).length);
            }
            _renderWorkbenchSideCards(tasks, '#mainHost .workbench-side-list');
            _renderStripCards(assets, '#mainHost .workbench-strip-grid', 'asset');
            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (e) {
            console.warn('[page-loaders] visual-editor load failed:', e);
        });
    };

    loaders['ai-content-factory'] = function () {
        Promise.all([
            api.assets.list().catch(function () { return []; }),
            api.tasks.list().catch(function () { return []; }),
            api.providers.list().catch(function () { return []; }),
            api.workflows.definitions().catch(function () { return []; }),
            api.workflows.runs().catch(function () { return []; }),
        ]).then(function (results) {
            var assets = results[0] || [];
            var tasks = results[1] || [];
            var providers = results[2] || [];
            var definitions = results[3] || [];
            var runs = results[4] || [];
            _renderWorkflowNodes(assets, tasks, providers, definitions, runs);
            _renderWorkbenchSideCards(tasks, '#mainHost .workbench-side-list');
            _renderStripCards(runs.length ? runs : tasks, '#mainHost .workbench-strip-grid');
            _applyAiHandoffHint('ai-content-factory', '#mainHost .workbench-strip-grid');
            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (e) {
            console.warn('[page-loaders] ai-content-factory load failed:', e);
        });
    };

    loaders['setup-wizard'] = function () {
        Promise.all([
            api.license.status().catch(function () { return {}; }),
            api.providers.list().catch(function () { return []; }),
            api.settings.all().catch(function () { return {}; }),
            api.theme.get().catch(function () { return 'light'; }),
        ]).then(function (results) {
            var license = results[0] || {};
            var providers = results[1] || [];
            var settings = results[2] || {};
            var theme = results[3] || 'light';
            _renderSetupWizard(license, providers, settings, theme);
            _bindSetupWizardActions(license, providers, settings, theme);
            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (e) {
            console.warn('[page-loaders] setup-wizard load failed:', e);
        });
    };

    loaders['license-issuer'] = function () {
        api.license.status().then(function (status) {
            _renderLicenseIssuer(status || {});
            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (e) {
            console.warn('[page-loaders] license-issuer load failed:', e);
            _renderLicenseIssuer({ error: e && e.message ? e.message : '璁稿彲璇佺姸鎬佽幏鍙栧け璐? });
            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        });
    };

    loaders['permission-management'] = function () {
        Promise.all([
            api.accounts.list().catch(function () { return []; }),
            api.providers.list().catch(function () { return []; }),
            api.tasks.list().catch(function () { return []; }),
        ]).then(function (results) {
            var accounts = results[0] || [];
            var providers = results[1] || [];
            var tasks = results[2] || [];
            _renderPermissionManagement(accounts, providers, tasks);
            _bindPermissionManagementActions(accounts, providers, tasks);
            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (e) {
            console.warn('[page-loaders] permission-management load failed:', e);
        });
    };

    loaders['downloader'] = function () {
        _loadToolConsolePage({ routeKey: 'downloader', title: '涓嬭浇鍣?, mode: 'downloader' });
    };

    loaders['lan-transfer'] = function () {
        _loadToolConsolePage({ routeKey: 'lan-transfer', title: '灞€鍩熺綉浼犺緭', mode: 'transfer' });
    };

    loaders['network-diagnostics'] = function () {
        _loadToolConsolePage({ routeKey: 'network-diagnostics', title: '缃戠粶璇婃柇', mode: 'diagnostics' });
    };

    loaders['log-center'] = function () {
        _loadToolConsolePage({ routeKey: 'log-center', title: '鏃ュ織涓績', mode: 'log' });
    };

    loaders['operations-center'] = function () {
        _loadListManagementPage({ routeKey: 'operations-center', title: '杩愯惀涓績', mode: 'operations' });
    };

    loaders['order-management'] = function () {
        _loadListManagementPage({ routeKey: 'order-management', title: '璁㈠崟绠＄悊', mode: 'orders' });
    };

    loaders['service-center'] = function () {
        _loadListManagementPage({ routeKey: 'service-center', title: '瀹㈡湇涓績', mode: 'service' });
    };

    loaders['refund-processing'] = function () {
        _loadListManagementPage({ routeKey: 'refund-processing', title: '閫€娆惧鐞?, mode: 'refund' });
    };

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
                showToast(title + ' 宸叉帴鍏ョ湡瀹炰换鍔℃睜', 'info');
            });
        });
        _rewireElements('#mainHost .page-header .secondary-button', function (btn) {
            btn.addEventListener('click', function () {
                if (config && config.tableMode === 'interaction') {
                    _runInteractionQuickAction(config);
                    return;
                }
                showToast('宸叉牴鎹湡瀹炵姸鎬佸埛鏂?' + title + ' 瑙嗗浘', 'success');
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
                    showToast('褰撳墠娌℃湁鍙姞鍏ョ櫧鍚嶅崟鐨勪换鍔?, 'warning');
                    return;
                }
                Promise.all(whitelistTargets.map(function (task) {
                    var summary = String(task.result_summary || '');
                    if (summary.indexOf('[鐧藉悕鍗昡') === -1) summary = '[鐧藉悕鍗昡 ' + summary;
                    return api.tasks.update(task.id, { result_summary: summary });
                })).then(function () {
                    showToast('宸叉壒閲忔洿鏂扮櫧鍚嶅崟绛栫暐锛? + whitelistTargets.length + ' 鏉★級', 'success');
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
                    showToast('褰撳墠璇勮鑺傛祦闃堝€煎唴锛屾棤闇€璋冩暣', 'info');
                    return;
                }
                Promise.all(overflow.map(function (task) {
                    return api.tasks.update(task.id, { status: 'paused', result_summary: '[鑺傛祦] 瓒呰繃骞跺彂闃堝€硷紝鑷姩鏆傚仠' });
                })).then(function () {
                    showToast('宸叉墽琛岃瘎璁鸿妭娴侊細鏆傚仠 ' + overflow.length + ' 鏉′换鍔?, 'warning');
                    if (loaders[config.routeKey]) loaders[config.routeKey]();
                });
                return;
            }
            if (config.routeKey === 'auto-message') {
                var pending = scoped.filter(function (task) {
                    return _normalizeTaskStatus(task.status) === 'pending';
                }).slice(0, 6);
                if (!pending.length) {
                    showToast('褰撳墠娌℃湁寰呴檺閫熺殑绉佷俊浠诲姟', 'info');
                    return;
                }
                Promise.all(pending.map(function (task, index) {
                    var summary = '[鍙戦€侀檺鍒禲 娉㈡ ' + (index + 1) + '锛岄棿闅?90 绉?;
                    return api.tasks.update(task.id, { priority: index < 2 ? 'high' : 'medium', result_summary: summary });
                })).then(function () {
                    showToast('宸插埛鏂扮淇″彂閫侀檺鍒讹紙' + pending.length + ' 鏉★級', 'success');
                    if (loaders[config.routeKey]) loaders[config.routeKey]();
                });
                return;
            }
            if (loaders[config.routeKey]) loaders[config.routeKey]();
        }).catch(function (err) {
            showToast('鎵ц鑱斿姩鎿嶄綔澶辫触: ' + err.message, 'error');
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
            }).join('') : '<article class="ticket-card"><strong>鏆傛棤浠诲姟</strong><div class="subtle">褰撳墠绛涢€夋潯浠朵笅娌℃湁鍖归厤椤?/div></article>';
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
                slot.textContent = task ? ((_taskTime(task, index) + ' ' + (task.title || _taskTypeLabel(task.task_type)))) : '鏆傛棤鎺掓湡';
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
                return '<tr class="route-row" data-task-id="' + (task.id || '') + '" data-search="' + _esc((task.title || '') + ' ' + _taskStatusLabel(task.status)) + '"><td><strong>' + _esc(task.title || ('鍥炲瑙勫垯 ' + (index + 1))) + '</strong></td><td>' + _esc((accounts[index] && accounts[index].region) || '鍏ㄧ珯') + '</td><td><span class="tag ' + _taskStatusTone(task.status) + '">' + (_normalizeTaskStatus(task.status) === 'failed' ? '楂? : '涓?) + '</span></td><td><div class="list-row"><span class="status-chip ' + _taskStatusTone(task.status) + '">' + _taskStatusLabel(task.status) + '</span><span class="detail-actions">' + actions + '</span></div></td></tr>';
            }
            if (config.tableMode === 'publish') {
                return '<tr class="route-row" data-task-id="' + (task.id || '') + '" data-search="' + _esc((task.title || '') + ' ' + _taskStatusLabel(task.status)) + '"><td><strong>' + _esc(task.title || ('鍙戝竷璁″垝 ' + (index + 1))) + '</strong></td><td>' + _taskTime(task, index) + '</td><td>' + _esc((accounts[index] && accounts[index].platform) || 'TikTok') + '</td><td><div class="list-row"><span>' + _taskStatusLabel(task.status) + '</span><span class="detail-actions">' + actions + '</span></div></td></tr>';
            }
            if (config.tableMode === 'collector') {
                return '<tr class="route-row" data-task-id="' + (task.id || '') + '" data-search="' + _esc((task.title || '') + ' ' + _taskTypeLabel(task.task_type)) + '"><td><strong>' + _esc(task.title || ('閲囬泦浠诲姟 ' + (index + 1))) + '</strong></td><td>' + _taskTypeLabel(task.task_type) + '</td><td>' + _taskStatusLabel(task.status) + '</td><td><div class="list-row"><span>' + _esc((accounts[index] && accounts[index].region) || '澶氬尯鍩?) + '</span><span class="detail-actions">' + actions + '</span></div></td></tr>';
            }
            return '<tr class="route-row" data-task-id="' + (task.id || '') + '" data-search="' + _esc((task.title || '') + ' ' + _taskStatusLabel(task.status)) + '"><td><strong>' + _esc(task.title || ('浠诲姟 ' + (index + 1))) + '</strong></td><td>' + _taskTypeLabel(task.task_type) + '</td><td>' + _taskStatusLabel(task.status) + '</td><td><div class="list-row"><span>' + _taskTime(task, index) + '</span><span class="detail-actions">' + actions + '</span></div></td></tr>';
        });
        tbody.innerHTML = rows.length ? rows.join('') : '<tr><td colspan="4" style="text-align:center;padding:32px;">鏆傛棤浠诲姟鏁版嵁</td></tr>';
    }

    function _taskInlineActionButtons(task, config) {
        var status = _normalizeTaskStatus(task.status);
        var buttons = [];
        if (status === 'pending' || status === 'paused' || status === 'failed') {
            buttons.push('<button class="ghost-button js-taskop-start" data-id="' + (task.id || '') + '">鍚姩</button>');
        }
        if (status === 'running') {
            buttons.push('<button class="ghost-button js-taskop-complete" data-id="' + (task.id || '') + '">瀹屾垚</button>');
            buttons.push('<button class="ghost-button js-taskop-pause" data-id="' + (task.id || '') + '">鏆傚仠</button>');
            buttons.push('<button class="ghost-button js-taskop-fail" data-id="' + (task.id || '') + '">鏍囪澶辫触</button>');
        }
        if (status === 'failed') {
            buttons.push('<button class="ghost-button js-taskop-retry" data-id="' + (task.id || '') + '">閲嶈瘯</button>');
        }
        if (config && config.tableMode === 'interaction') {
            buttons.push('<button class="ghost-button js-taskop-whitelist" data-id="' + (task.id || '') + '">鐧藉悕鍗?/button>');
        }
        buttons.push('<button class="ghost-button js-taskop-edit" data-id="' + (task.id || '') + '">缂栬緫</button>');
        buttons.push('<button class="danger-button js-taskop-delete" data-id="' + (task.id || '') + '">鍒犻櫎</button>');
        return buttons.join('');
    }

    function _bindTaskOpsTaskActions(tasks, config) {
        _rewireElements('#mainHost .js-taskop-start', function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                api.tasks.start(id).then(function () {
                    showToast('浠诲姟宸插惎鍔?, 'success');
                    if (loaders[config.routeKey]) loaders[config.routeKey]();
                }).catch(function (err) {
                    showToast('鍚姩澶辫触: ' + err.message, 'error');
                });
            });
        });
        _rewireElements('#mainHost .js-taskop-complete', function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                api.tasks.complete(id).then(function () {
                    showToast('浠诲姟宸插畬鎴?, 'success');
                    if (loaders[config.routeKey]) loaders[config.routeKey]();
                }).catch(function (err) {
                    showToast('瀹屾垚澶辫触: ' + err.message, 'error');
                });
            });
        });
        _rewireElements('#mainHost .js-taskop-pause', function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                api.tasks.update(id, { status: 'paused' }).then(function () {
                    showToast('浠诲姟宸叉殏鍋?, 'warning');
                    if (loaders[config.routeKey]) loaders[config.routeKey]();
                }).catch(function (err) {
                    showToast('鏆傚仠澶辫触: ' + err.message, 'error');
                });
            });
        });
        _rewireElements('#mainHost .js-taskop-fail', function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                api.tasks.fail(id).then(function () {
                    showToast('浠诲姟宸叉爣璁板け璐?, 'warning');
                    if (loaders[config.routeKey]) loaders[config.routeKey]();
                }).catch(function (err) {
                    showToast('鏍囪澶辫触澶辫触: ' + err.message, 'error');
                });
            });
        });
        _rewireElements('#mainHost .js-taskop-retry', function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                api.tasks.start(id).then(function () {
                    showToast('浠诲姟宸查噸璇?, 'success');
                    if (loaders[config.routeKey]) loaders[config.routeKey]();
                }).catch(function (err) {
                    showToast('閲嶈瘯澶辫触: ' + err.message, 'error');
                });
            });
        });
        _rewireElements('#mainHost .js-taskop-whitelist', function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                var task = (tasks || []).find(function (item) { return Number(item.id) === id; });
                if (!task) return;
                var summary = String(task.result_summary || '');
                if (summary.indexOf('[鐧藉悕鍗昡') === -1) summary = '[鐧藉悕鍗昡 ' + summary;
                api.tasks.update(id, { result_summary: summary }).then(function () {
                    showToast('宸插姞鍏ョ櫧鍚嶅崟绛栫暐', 'success');
                    if (loaders[config.routeKey]) loaders[config.routeKey]();
                }).catch(function (err) {
                    showToast('鐧藉悕鍗曟洿鏂板け璐? ' + err.message, 'error');
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
                    title: '鍒犻櫎浠诲姟',
                    message: '纭畾瑕佸垹闄よ繖鏉′换鍔¤褰曪紵姝ゆ搷浣滀笉鍙仮澶嶃€?,
                    confirmText: '鍒犻櫎',
                    tone: 'danger',
                }).then(function (ok) {
                    if (!ok) return;
                    api.tasks.remove(id).then(function () {
                        showToast('浠诲姟宸插垹闄?, 'success');
                        if (loaders[config.routeKey]) loaders[config.routeKey]();
                    }).catch(function (err) {
                        showToast('鍒犻櫎澶辫触: ' + err.message, 'error');
                    });
                });
            });
        });
    }

    function _renderTaskOpsDetail(tasks, accounts, assets, config) {
        var detailItems = document.querySelectorAll('#detailHost .detail-item strong');
        if (detailItems.length >= 3) {
            detailItems[0].textContent = String(tasks.length) + ' 鏉′换鍔″凡鎺ュ叆';
            detailItems[1].textContent = String(tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'failed'; }).length) + ' 鏉￠渶鍏虫敞';
            detailItems[2].textContent = '璐﹀彿 ' + accounts.length + ' / 绱犳潗 ' + assets.length;
        }
        var boardList = document.querySelector('#detailHost .board-list');
        if (boardList) {
            boardList.innerHTML = tasks.slice(0, 3).map(function (task) {
                return '<article class="board-card"><strong>' + _esc(task.title || _taskTypeLabel(task.task_type)) + '</strong><div class="subtle">'
                    + _esc(task.result_summary || ('褰撳墠鐘舵€侊細' + _taskStatusLabel(task.status))) + '</div><div class="status-strip"><span class="pill ' + _taskStatusTone(task.status) + '">' + _taskStatusLabel(task.status) + '</span></div></article>';
            }).join('');
        }
    }

    function _renderWorkbenchSummary(items) {
        var chips = document.querySelectorAll('#mainHost .workbench-summary-chip');
        chips.forEach(function (chip, index) {
            var item = items[index];
            if (!item) return;
            var subtle = chip.querySelector('.subtle');
            var strong = chip.querySelector('strong');
            var small = chip.querySelector('small');
            if (subtle) subtle.textContent = item.label;
            if (strong) strong.textContent = item.value;
            if (small) small.textContent = item.note;
        });
    }

    function _renderVideoEditorAssets(assets) {
        var counts = { video: 0, image: 0, subtitle: 0, audio: 0 };
        assets.forEach(function (asset) {
            var type = String(asset.asset_type || '').toLowerCase();
            if (type === 'video') counts.video += 1;
            else if (type === 'image' || type === 'template') counts.image += 1;
            else if (type === 'text') counts.subtitle += 1;
            else if (type === 'audio') counts.audio += 1;
        });
        var tabs = document.querySelectorAll('#mainHost .source-browser-tabs span');
        var labels = [
            ['瑙嗛', counts.video],
            ['鍥剧墖', counts.image],
            ['瀛楀箷', counts.subtitle],
            ['闊抽', counts.audio],
        ];
        tabs.forEach(function (tab, index) {
            if (labels[index]) tab.innerHTML = labels[index][0] + ' <em>' + labels[index][1] + '</em>';
        });
        var grid = document.querySelector('#mainHost .source-thumb-grid');
        if (grid) {
            grid.innerHTML = assets.slice(0, 8).map(function (asset, index) {
                return _buildAssetThumb({
                    id: asset.id,
                    asset_type: asset.asset_type === 'text' ? 'subtitle' : asset.asset_type,
                    filename: asset.filename,
                    file_size: asset.file_size,
                    tags: asset.tags,
                }, index === 0);
            }).join('');
            _bindAssetThumbs(assets);
        }
        if (assets[0]) _renderAssetDetail(assets[0]);
    }

    function _renderWorkbenchSideCards(items, selector) {
        var host = document.querySelector(selector);
        if (!host) return;
        host.innerHTML = (items || []).slice(0, 3).map(function (item, index) {
            var title = item.title || item.filename || ('椤圭洰 ' + (index + 1));
            var desc = item.result_summary || item.file_path || (_taskTypeLabel(item.task_type) + ' / ' + _taskStatusLabel(item.status));
            var tone = item.status ? _taskStatusTone(item.status) : 'info';
            var badge = item.status ? _taskStatusLabel(item.status) : (item.asset_type || '绱犳潗');
            return '<article class="workbench-sidecard"><div class="workbench-sidecard__head"><strong>' + _esc(title) + '</strong><span class="pill ' + tone + '">' + _esc(badge) + '</span></div><div class="subtle">' + _esc(desc) + '</div></article>';
        }).join('');
    }

    function _renderStripCards(items, selector, mode) {
        var host = document.querySelector(selector);
        if (!host) return;
        host.innerHTML = (items || []).slice(0, 3).map(function (item, index) {
            var title = item.title || item.filename || ('鏉＄洰 ' + (index + 1));
            var desc = mode === 'asset' ? (item.file_path || '宸茶繘鍏ョ礌鏉愮紪缁?) : (item.result_summary || _taskStatusLabel(item.status));
            var badge = mode === 'asset' ? (item.asset_type || '绱犳潗') : _taskStatusLabel(item.status || 'pending');
            var tone = mode === 'asset' ? 'info' : _taskStatusTone(item.status);
            return '<article class="strip-card"><strong>' + _esc(title) + '</strong><div class="subtle">' + _esc(desc) + '</div><span class="pill ' + tone + '">' + _esc(badge) + '</span></article>';
        }).join('');
    }

    function _applyAiHandoffHint(routeKey, selector) {
        var handoff = null;
        try {
            handoff = JSON.parse(window.localStorage.getItem('tkops.ai.handoff') || 'null');
        } catch (_) {
            handoff = null;
        }
        if (!handoff || handoff.targetRoute !== routeKey) return;
        var host = document.querySelector(selector);
        if (!host) return;
        var card = host.querySelector('.strip-card');
        if (!card) return;
        var strong = card.querySelector('strong');
        var subtle = card.querySelector('.subtle');
        var pill = card.querySelector('.pill');
        if (strong) strong.textContent = 'AI 涓嬪彂鍐呭';
        if (subtle) subtle.textContent = String(handoff.text || '').slice(0, 72);
        if (pill) {
            pill.textContent = '宸蹭笅鍙?;
            pill.className = 'pill success';
        }
    }

    function _renderCreativeFocusCards(accounts, assets, tasks) {
        var host = document.querySelector('#mainHost .focus-grid');
        if (!host) return;
        var base = [
            { title: '璐﹀彿鍦板煙缁勫悎', badge: 'A 鏂规', tone: 'success', desc: (accounts[0] ? ((accounts[0].region || '鏍稿績鍦板尯') + ' 琛ㄧ幇鏇寸ǔ') : '鏆傛棤璐﹀彿鍦板煙鏁版嵁'), meta: '浼樺厛淇濈暀楂樹綋閲忓湴鍖哄唴瀹归獙璇? },
            { title: '绱犳潗瑕嗙洊鐜?, badge: 'B 鏂规', tone: 'warning', desc: '褰撳墠宸叉帴鍏?' + assets.length + ' 鏉＄礌鏉愶紝鍙敮鎸佸鐗堟湰鍒涙剰璇曢獙', meta: '绱犳潗鍏呰冻鏃跺彲鎺ㄨ繘鍙岀増鏈苟琛? },
            { title: '鎵ц鍙嶉', badge: '闀滃ご', tone: 'info', desc: '浠诲姟姹犱腑鏈?' + tasks.length + ' 涓浉鍏冲姩浣滅粨鏋滃彲鍥炵湅', meta: '浼樺厛閫夊畬鎴愮巼鏇撮珮鐨勫垱鎰忚矾绾? },
            { title: '杈撳嚭寤鸿', badge: '鍙ｆ挱', tone: 'success', desc: '寤鸿鍏堜骇鍑虹煭鍙ｆ挱鐗堟湰锛屽啀杩涘叆鍓緫椤甸獙璇?, meta: '鍙ｆ挱闀垮害涓庣礌鏉愭暟閲忓凡鑱斿姩璇勪及' },
        ];
        host.innerHTML = base.map(function (card, index) {
            return '<article class="focus-card ' + (index === 0 ? 'focus-card--wide' : '') + '"><div class="focus-card__head"><strong>' + _esc(card.title) + '</strong><span class="pill ' + card.tone + '">' + _esc(card.badge) + '</span></div><div class="subtle">' + _esc(card.desc) + '</div><div class="focus-card__meta">' + _esc(card.meta) + '</div></article>';
        }).join('');
    }

    function _renderWorkflowNodes(assets, tasks, providers, definitions, runs) {
        var nodes = document.querySelectorAll('#mainHost .workflow-node');
        if (!nodes.length) return;
        var summaries = [
            '绱犳潗 ' + assets.length + ' 鏉?,
            '宸ヤ綔娴?' + ((definitions || []).length || tasks.length) + ' 涓?,
            '渚涘簲鍟?' + providers.length + ' 涓?,
            '杩愯涓?' + ((runs || []).filter(function (run) { return _normalizeTaskStatus(run.status) === 'running'; }).length || tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'running'; }).length) + ' 涓?,
        ];
        nodes.forEach(function (node, index) {
            var subtle = node.querySelector('.subtle');
            if (subtle && summaries[index]) subtle.textContent = summaries[index];
            node.classList.toggle('is-active', index === Math.min(3, ((runs || []).filter(function (run) { return _normalizeTaskStatus(run.status) === 'running'; }).length || tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'running'; }).length)));
        });
    }

    function _loadToolConsolePage(config) {
        Promise.all([
            api.tasks.list().catch(function () { return []; }),
            api.assets.list().catch(function () { return []; }),
            api.accounts.list().catch(function () { return []; }),
            api.providers.list().catch(function () { return []; }),
            api.logs && config.mode === 'log' ? api.logs.recent().catch(function () { return null; }) : Promise.resolve(null),
        ]).then(function (results) {
            var tasks = results[0] || [];
            var assets = results[1] || [];
            var accounts = results[2] || [];
            var providers = results[3] || [];
            var logs = results[4] || null;
            _renderToolConsoleMetrics(tasks, assets, accounts, providers, logs, config);
            _renderToolConsoleStrip(tasks, assets, accounts, providers, logs, config);
            _renderToolConsoleForm(tasks, assets, accounts, providers, logs, config);
            _renderToolConsoleList(tasks, assets, accounts, providers, logs, config);
            _renderToolConsoleCards(tasks, assets, accounts, providers, logs, config);
            _renderToolConsoleDetail(tasks, assets, accounts, providers, logs, config);
            _bindToolConsoleActions(config, tasks, assets, accounts, logs);
            if (config.mode === 'diagnostics') {
                var cached = _loadDiagnosticsResult();
                if (cached) {
                    window.__lastDiagnosticsResult = cached;
                    _applyDiagnosticsResult(cached);
                }
            }
            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (e) {
            console.warn('[page-loaders] ' + config.routeKey + ' load failed:', e);
        });
    }

    function _bindToolConsoleActions(config, tasks, assets, accounts, logs) {
        _rewireElements('#mainHost .page-header .primary-button', function (btn) {
            btn.addEventListener('click', function () {
                if (config.mode === 'downloader') {
                    _pickFilesAndImportAsAssets(config.routeKey);
                    return;
                }
                if (config.mode === 'transfer') {
                    _pickFilesAndCreateTransferTasks(config.routeKey, accounts);
                    return;
                }
                if (config.mode === 'diagnostics') {
                    _runNetworkDiagnosticsAndRender(config.routeKey, config.title);
                    return;
                }
                if (config.mode === 'log' && window.api && window.api.utils) {
                    window.api.utils.copyToClipboard((logs && logs.path) || '').then(function () {
                        showToast('鏃ュ織璺緞宸插鍒?, 'success');
                    });
                    return;
                }
                showToast(config.title + ' 宸插悓姝ョ湡瀹炴暟鎹?, 'info');
            });
        });
        _rewireElements('#mainHost .page-header .secondary-button', function (btn) {
            btn.addEventListener('click', function () {
                if (config.mode === 'diagnostics') {
                    _exportDiagnosticsReport(config.title);
                    return;
                }
                if (config.mode === 'log') {
                    _exportLogReport(logs);
                    return;
                }
                if (loaders[config.routeKey]) loaders[config.routeKey]();
                showToast('宸插埛鏂?' + config.title + ' 鏁版嵁', 'success');
            });
        });
        _bindToolQueueActions(config, tasks);
    }

    function _bindToolQueueActions(config, tasks) {
        _rewireElements('#mainHost .js-tool-queue-start', function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                api.tasks.start(id).then(function () {
                    showToast('闃熷垪浠诲姟宸插惎鍔?, 'success');
                    if (loaders[config.routeKey]) loaders[config.routeKey]();
                }).catch(function (err) {
                    showToast('鍚姩澶辫触: ' + err.message, 'error');
                });
            });
        });
        _rewireElements('#mainHost .js-tool-queue-pause', function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                api.tasks.update(id, { status: 'paused' }).then(function () {
                    showToast('闃熷垪浠诲姟宸叉殏鍋?, 'warning');
                    if (loaders[config.routeKey]) loaders[config.routeKey]();
                }).catch(function (err) {
                    showToast('鏆傚仠澶辫触: ' + err.message, 'error');
                });
            });
        });
        _rewireElements('#mainHost .js-tool-queue-cancel', function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                api.tasks.remove(id).then(function () {
                    showToast('闃熷垪浠诲姟宸插彇娑?, 'success');
                    if (loaders[config.routeKey]) loaders[config.routeKey]();
                }).catch(function (err) {
                    showToast('鍙栨秷澶辫触: ' + err.message, 'error');
                });
            });
        });
    }

    function _pickFilesAndImportAsAssets(routeKey) {
        if (!api.utils || typeof api.utils.pickFiles !== 'function') {
            showToast('褰撳墠鐗堟湰涓嶆敮鎸佹枃浠堕€夋嫨', 'warning');
            return;
        }
        api.utils.pickFiles().then(function (files) {
            var list = (files || []).filter(Boolean);
            if (!list.length) {
                showToast('鏈€夋嫨鏂囦欢', 'warning');
                return;
            }
            var jobs = list.map(function (filePath) {
                var parts = String(filePath).split(/[\\/]/);
                var filename = parts[parts.length - 1] || '鏈懡鍚嶆枃浠?;
                return Promise.all([
                    api.assets.create({
                        filename: filename,
                        file_path: filePath,
                        asset_type: _guessAssetTypeByName(filename),
                        tags: '鏂囦欢瀵煎叆',
                    }).catch(function () { return null; }),
                    api.tasks.create({
                        title: '涓嬭浇鍏ュ簱 路 ' + filename,
                        task_type: 'maintenance',
                        priority: 'medium',
                        status: 'pending',
                        result_summary: '鏉ユ簮椤甸潰锛氫笅杞藉櫒 / 鏂囦欢锛? + filePath,
                    }).catch(function () { return null; }),
                ]).then(function (pair) {
                    return pair[0] || pair[1];
                });
            });
            return Promise.all(jobs).then(function (results) {
                var successCount = results.filter(Boolean).length;
                showToast('宸插鍏?' + successCount + ' 涓枃浠?, successCount ? 'success' : 'warning');
                if (loaders[routeKey]) loaders[routeKey]();
            });
        }).catch(function (err) {
            showToast('瀵煎叆澶辫触: ' + err.message, 'error');
        });
    }

    function _pickFilesAndCreateTransferTasks(routeKey, accounts) {
        if (!api.utils || typeof api.utils.pickFiles !== 'function') {
            showToast('褰撳墠鐗堟湰涓嶆敮鎸佹枃浠堕€夋嫨', 'warning');
            return;
        }
        api.utils.pickFiles().then(function (files) {
            var list = (files || []).filter(Boolean);
            if (!list.length) {
                showToast('鏈€夋嫨鍙戦€佹枃浠?, 'warning');
                return;
            }
            var targetId = accounts[0] ? accounts[0].id : '';
            var jobs = list.map(function (filePath) {
                var parts = String(filePath).split(/[\\/]/);
                var filename = parts[parts.length - 1] || '鏂囦欢';
                return api.tasks.create({
                    title: '灞€鍩熺綉浼犺緭 路 ' + filename,
                    task_type: 'maintenance',
                    priority: 'medium',
                    status: 'pending',
                    account_id: targetId,
                    result_summary: '寰呭彂閫佹枃浠讹細' + filePath,
                }).catch(function () { return null; });
            });
            return Promise.all(jobs).then(function (results) {
                var successCount = results.filter(Boolean).length;
                showToast('宸插姞鍏?' + successCount + ' 鏉′紶杈撲换鍔?, successCount ? 'success' : 'warning');
                if (loaders[routeKey]) loaders[routeKey]();
            });
        }).catch(function (err) {
            showToast('鍒涘缓浼犺緭浠诲姟澶辫触: ' + err.message, 'error');
        });
    }

    function _runNetworkDiagnosticsAndRender(routeKey, title) {
        if (!api.diagnostics || typeof api.diagnostics.run !== 'function') {
            showToast('褰撳墠鐗堟湰涓嶆敮鎸佺綉缁滆瘖鏂?, 'warning');
            return;
        }
        api.diagnostics.run().then(function (result) {
            window.__lastDiagnosticsResult = result || null;
            _saveDiagnosticsResult(result || null);
            _applyDiagnosticsResult(result || {});
            showToast(title + ' 宸插畬鎴愭娴?, 'success');
        }).catch(function (err) {
            showToast('璇婃柇澶辫触: ' + err.message, 'error');
            if (loaders[routeKey]) loaders[routeKey]();
        });
    }

    function _exportDiagnosticsReport(title) {
        var result = window.__lastDiagnosticsResult || null;
        if (!result || !result.reportText) {
            showToast('璇峰厛杩愯缃戠粶娴嬭瘯', 'warning');
            return;
        }
        if (!api.utils || typeof api.utils.exportTextFile !== 'function') {
            showToast('褰撳墠鐗堟湰涓嶆敮鎸佸鍑?, 'warning');
            return;
        }
        api.utils.exportTextFile(result.reportText).then(function (saved) {
            if (saved && saved.saved) {
                showToast(title + ' 瀵煎嚭鎴愬姛', 'success');
                return;
            }
            showToast('宸插彇娑堝鍑?, 'warning');
        }).catch(function (err) {
            showToast('瀵煎嚭澶辫触: ' + err.message, 'error');
        });
    }

    function _exportLogReport(logs) {
        var text = ((logs && logs.lines) || []).join('\n');
        if (!text) {
            showToast('褰撳墠娌℃湁鍙鍑虹殑鏃ュ織', 'warning');
            return;
        }
        if (!api.utils || typeof api.utils.exportTextFile !== 'function') {
            showToast('褰撳墠鐗堟湰涓嶆敮鎸佸鍑?, 'warning');
            return;
        }
        api.utils.exportTextFile(text).then(function (saved) {
            if (saved && saved.saved) {
                showToast('鏃ュ織瀵煎嚭鎴愬姛', 'success');
                return;
            }
            showToast('宸插彇娑堝鍑?, 'warning');
        }).catch(function (err) {
            showToast('瀵煎嚭澶辫触: ' + err.message, 'error');
        });
    }

    function _guessAssetTypeByName(filename) {
        var name = String(filename || '').toLowerCase();
        if (/\.(mp4|mov|mkv|avi|webm)$/.test(name)) return 'video';
        if (/\.(png|jpg|jpeg|gif|webp|bmp)$/.test(name)) return 'image';
        if (/\.(mp3|wav|aac|flac|m4a)$/.test(name)) return 'audio';
        if (/\.(txt|md|srt|ass|vtt|doc|docx)$/.test(name)) return 'text';
        return 'template';
    }

    function _applyDiagnosticsResult(result) {
        var checks = result && Array.isArray(result.checks) ? result.checks : [];
        var cards = document.querySelectorAll('#mainHost .stat-grid .stat-card');
        if (cards.length >= 3) {
            cards[0].querySelector('.stat-card__value').textContent = String(checks.length);
            cards[1].querySelector('.stat-card__value').textContent = String(result.errorCount || 0);
            cards[2].querySelector('.stat-card__value').textContent = String(result.score || 0) + '%';
        }

        var strip = document.querySelectorAll('#mainHost .tool-status-strip .timeline-chip strong');
        if (strip.length >= 3) {
            strip[0].textContent = '妫€娴嬮」 ' + checks.length;
            strip[1].textContent = '鍛婅 ' + String(result.warningCount || 0);
            strip[2].textContent = '璇勫垎 ' + String(result.score || 0) + '%';
        }

        var list = document.querySelector('#mainHost .workbench-list');
        if (list) {
            list.innerHTML = (checks.length ? checks : [{ name: '鏃犳娴嬮」', status: 'warning', detail: '璇锋鏌ヨ瘖鏂厤缃? }]).map(function (item, index) {
                var tone = item.status === 'ok' ? 'success' : item.status === 'warning' ? 'warning' : 'error';
                var badge = item.status === 'ok' ? '閫氳繃' : item.status === 'warning' ? '璀﹀憡' : '澶辫触';
                return '<div class="task-item ' + (index === 0 ? 'is-selected' : '') + '"><div><strong>' + _esc(item.name || ('妫€娴嬮」 ' + (index + 1))) + '</strong><div class="subtle">' + _esc(item.detail || '') + '</div></div><span class="pill ' + tone + '">' + badge + '</span></div>';
            }).join('');
        }

        var detailItems = document.querySelectorAll('#detailHost .detail-item strong');
        if (detailItems.length >= 3) {
            detailItems[0].textContent = '妫€鏌ラ」 ' + checks.length;
            detailItems[1].textContent = '閿欒 ' + String(result.errorCount || 0) + ' / 璀﹀憡 ' + String(result.warningCount || 0);
            detailItems[2].textContent = '鐢熸垚鏃堕棿 ' + (result.generatedAt || '-');
        }

        var boardList = document.querySelector('#detailHost .board-list');
        if (boardList) {
            boardList.innerHTML = checks.slice(0, 3).map(function (item) {
                var tone = item.status === 'ok' ? 'success' : item.status === 'warning' ? 'warning' : 'error';
                var badge = item.status === 'ok' ? '閫氳繃' : item.status === 'warning' ? '璀﹀憡' : '澶辫触';
                return '<article class="board-card"><strong>' + _esc(item.name || '妫€娴嬮」') + '</strong><div class="subtle">' + _esc(item.detail || '') + '</div><div class="status-strip"><span class="pill ' + tone + '">' + badge + '</span></div></article>';
            }).join('');
        }
    }

    function _saveDiagnosticsResult(result) {
        try {
            if (!result) {
                window.localStorage.removeItem('tkops.lastDiagnostics');
                return;
            }
            window.localStorage.setItem('tkops.lastDiagnostics', JSON.stringify(result));
        } catch (_) {}
    }

    function _loadDiagnosticsResult() {
        try {
            var raw = window.localStorage.getItem('tkops.lastDiagnostics');
            if (!raw) return null;
            return JSON.parse(raw);
        } catch (_) {
            return null;
        }
    }

    function _loadListManagementPage(config) {
        Promise.all([
            api.tasks.list().catch(function () { return []; }),
            api.accounts.list().catch(function () { return []; }),
            api.assets.list().catch(function () { return []; }),
            api.providers.list().catch(function () { return []; }),
        ]).then(function (results) {
            var tasks = results[0] || [];
            var accounts = results[1] || [];
            var assets = results[2] || [];
            var providers = results[3] || [];
            _renderListManagementMetrics(tasks, accounts, assets, providers, config);
            _renderListManagementItems(tasks, accounts, assets, providers, config);
            _renderListManagementDetail(tasks, accounts, assets, providers, config);
            _bindListManagementActions(config, tasks, accounts, assets, providers);
            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (e) {
            console.warn('[page-loaders] ' + config.routeKey + ' load failed:', e);
        });
    }

    function _bindListManagementActions(config, tasks, accounts, assets, providers) {
        _rewireElements('#mainHost .page-header .primary-button', function (btn) {
            btn.addEventListener('click', function () {
                if (typeof openTaskForm === 'function') {
                    openTaskForm(_listManagementDraft(config, accounts, assets, providers));
                    return;
                }
                showToast(config.title + ' 宸叉帴鍏ョ湡瀹炴暟鎹崏绋?, 'info');
            });
        });
        _rewireElements('#mainHost .page-header .secondary-button', function (btn) {
            btn.addEventListener('click', function () {
                if (loaders[config.routeKey]) loaders[config.routeKey]();
                showToast('宸插埛鏂?' + config.title + ' 鏁版嵁', 'success');
            });
        });
    }

    function _listManagementDraft(config, accounts, assets, providers) {
        var drafts = {
            operations: {
                title: '杩愯惀鎺掓湡鍗忚皟',
                task_type: 'maintenance',
                priority: 'high',
                result_summary: '鏉ユ簮椤甸潰锛氳繍钀ヤ腑蹇?/ 鍗忚皟璐﹀彿銆佺礌鏉愪笌鎺掓湡鍐茬獊',
            },
            orders: {
                title: '璁㈠崟寮傚父澶嶆牳',
                task_type: 'report',
                priority: 'high',
                result_summary: '鏉ユ簮椤甸潰锛氳鍗曠鐞?/ 鑱氱劍瓒呮椂銆佷簤璁笌灞ョ害寮傚父',
            },
            service: {
                title: '瀹㈡湇宸ュ崟璺熻繘',
                task_type: 'interact',
                priority: 'high',
                result_summary: '鏉ユ簮椤甸潰锛氬鏈嶄腑蹇?/ 璺熻繘瓒呮椂宸ュ崟涓庨珮椋庨櫓鎶曡瘔',
            },
            refund: {
                title: '閫€娆惧鎵瑰鐞?,
                task_type: 'maintenance',
                priority: 'high',
                result_summary: '鏉ユ簮椤甸潰锛氶€€娆惧鐞?/ 瀹℃壒楂橀噾棰濅笌鎵归噺閫€娆捐褰?,
            },
        };
        var draft = drafts[config.mode] || drafts.operations;
        return {
            title: draft.title,
            task_type: draft.task_type,
            priority: draft.priority,
            result_summary: draft.result_summary,
            account_id: accounts[0] ? accounts[0].id : '',
        };
    }

    function _listManagementRecords(tasks, accounts, assets, providers, config) {
        if (config.mode === 'operations') {
            return accounts.slice(0, 4).map(function (account, index) {
                var task = tasks[index] || {};
                var asset = assets[index] || {};
                return {
                    title: (account.region || '榛樿鍖哄煙') + ' 杩愯惀鎺掓湡',
                    desc: (account.username || '鏈粦瀹氳礋璐ｄ汉') + ' / 绱犳潗 ' + (asset.filename || '寰呰ˉ榻?) + ' / ' + _taskTypeLabel(task.task_type),
                    badge: task.status ? _taskStatusLabel(task.status) : '寰呭崗璋?,
                    tone: task.status ? _taskStatusTone(task.status) : 'warning',
                };
            });
        }
        if (config.mode === 'orders') {
            return tasks.slice(0, 4).map(function (task, index) {
                var account = accounts[index] || {};
                return {
                    title: 'ORD-' + String(2800 + index + 1),
                    desc: (account.username || account.region || '榛樿搴楅摵') + ' / ' + (task.title || _taskTypeLabel(task.task_type)),
                    badge: _normalizeTaskStatus(task.status) === 'failed' ? '寮傚父' : (_normalizeTaskStatus(task.status) === 'completed' ? '宸插畬鎴? : '澶勭悊涓?),
                    tone: _normalizeTaskStatus(task.status) === 'failed' ? 'error' : (_normalizeTaskStatus(task.status) === 'completed' ? 'success' : 'warning'),
                };
            });
        }
        if (config.mode === 'service') {
            return accounts.slice(0, 4).map(function (account, index) {
                var task = tasks[index] || {};
                return {
                    title: 'CS-' + String(1000 + index + 1),
                    desc: (account.username || '瀹㈡埛璇锋眰') + ' / ' + (task.result_summary || task.title || '寰呰窡杩涘伐鍗?),
                    badge: _normalizeTaskStatus(task.status) === 'failed' ? '瓒呮椂' : '璺熻繘涓?,
                    tone: _normalizeTaskStatus(task.status) === 'failed' ? 'error' : 'warning',
                };
            });
        }
        return tasks.slice(0, 4).map(function (task, index) {
            var provider = providers[index] || {};
            return {
                title: 'RF-' + String(890 + index + 1),
                desc: (task.title || '閫€娆剧敵璇?) + ' / ' + (provider.name || '榛樿瀹℃壒娴?),
                badge: _normalizeTaskStatus(task.status) === 'completed' ? '宸插鏍? : '寰呭鎵?,
                tone: _normalizeTaskStatus(task.status) === 'completed' ? 'success' : 'warning',
            };
        });
    }

    function _renderSetupWizard(license, providers, settings, theme) {
        var machineCode = license.machine_id_short || license.machineCodeShort || license.machine_code_short || license.machine_id || license.machine_code || license.machineCode || license.device_id || license.deviceId || 'MID-UNBOUND';
        var hasLicense = !!(license.activated || license.active || license.is_activated || license.valid || String(license.status || '').toLowerCase() === 'active');
        var licenseTier = license.tier || license.license_tier || (hasLicense ? 'pro' : '鏈縺娲?);
        var activeProvider = (providers || []).find(function (provider) {
            return provider.is_active || provider.active;
        }) || providers[0] || {};
        var market = settings.primary_market || settings.market || '缇庡浗锛圲S锛?;
        var model = settings.default_model || settings.ai_model || settings.defaultModel || 'gpt-4.1-mini';
        var workflow = settings.default_workflow || settings.home_route || settings.workflow || '鍐呭鍒涗綔';
        var activeStep = !hasLicense ? 1 : !providers.length ? 2 : !model ? 3 : 4;
        var steps = document.querySelectorAll('#mainHost .wizard-step');
        steps.forEach(function (step, index) {
            step.classList.toggle('is-done', index < activeStep - 1);
            step.classList.toggle('is-active', index === activeStep - 1);
            var subtle = step.querySelector('.subtle');
            if (subtle) {
                subtle.textContent = index === 0
                    ? (hasLicense ? '璁惧宸茶瘑鍒紝鍙户缁縺娲? : '绛夊緟璁稿彲璇佹縺娲?)
                    : index === 1
                        ? (hasLicense ? '璁稿彲璇佺姸鎬佹甯? : '璇峰厛瀹屾垚鏈満婵€娲?)
                        : index === 2
                            ? (providers.length ? '宸插彂鐜?' + providers.length + ' 涓緵搴斿晢' : '鑷冲皯鎺ュ叆 1 涓緵搴斿晢')
                            : index === 3
                                ? ('褰撳墠榛樿妯″瀷锛? + model)
                                : ('褰撳墠宸ヤ綔娴侊細' + workflow);
            }
        });

        var activeHost = document.querySelector('#mainHost .wizard-active-step');
        if (activeHost) {
            var headerTitle = activeStep === 1 ? '璁稿彲璇佹縺娲? : activeStep === 2 ? '渚涘簲鍟嗘帴鍏? : activeStep === 3 ? '榛樿妯″瀷' : '浣跨敤鍋忓ソ';
            var headerDesc = activeStep === 1
                ? '褰撳墠璁惧宸茶瘑鍒紝瀹屾垚鎺堟潈鍚庢墠鑳借В閿佸悗缁姛鑳姐€?
                : activeStep === 2
                    ? '閫夋嫨涓€涓彲鐢ㄤ緵搴斿晢锛岀郴缁熸墠鑳藉惎鐢?AI 鐢熸垚鑳藉姏銆?
                    : activeStep === 3
                        ? '纭榛樿妯″瀷锛岄伩鍏嶅悗缁笉鍚屽伐浣滄祦閰嶇疆鍒嗘暎銆?
                        : '鏈€鍚庣‘璁ゅ父鐢ㄥ競鍦哄拰榛樿宸ヤ綔娴併€?;
            var fields = activeStep === 1
                ? [
                    { label: '鏈哄櫒鏄剧ず鐮?, value: machineCode, hint: '鐭爜鐢ㄤ簬浜哄伐鏍稿锛屽畬鏁存満鍣ㄧ爜鍙湪婵€娲婚〉澶嶅埗' },
                    { label: '璁稿彲璇佺姸鎬?, value: hasLicense ? ('宸叉縺娲?/ ' + String(licenseTier).toUpperCase()) : '寰呮縺娲?, hint: hasLicense ? '璁稿彲璇佸凡缁戝畾褰撳墠璁惧' : '璇疯緭鍏ユ湁鏁堣鍙瘉瀵嗛挜' },
                ]
                : activeStep === 2
                    ? [
                        { label: '褰撳墠渚涘簲鍟?, value: activeProvider.name || '鏈厤缃?, hint: providers.length ? '宸叉娴嬪埌 ' + providers.length + ' 涓緵搴斿晢閰嶇疆' : '璇疯嚦灏戦厤缃竴涓?AI 渚涘簲鍟? },
                        { label: '鎺ㄨ崘鍔ㄤ綔', value: providers.length ? '楠岃瘉 API Key' : '鏂板缓渚涘簲鍟?, hint: '瀹屾垚杩為€氭€ч獙璇佸悗鍐嶈繘鍏ユā鍨嬮厤缃? },
                    ]
                    : activeStep === 3
                        ? [
                            { label: '榛樿妯″瀷', value: model, hint: '褰撳墠鐢ㄤ簬鏍囬銆佽剼鏈拰鏂囨鐢熸垚' },
                            { label: '涓婚', value: theme === 'dark' ? '娣辫壊' : '娴呰壊', hint: '涓婚宸插悓姝ュ埌褰撳墠妗岄潰澹冲眰' },
                        ]
                        : [
                            { label: '涓昏甯傚満', value: market, hint: '褰卞搷榛樿璐у竵銆佽瑷€涓庢椂鍖? },
                            { label: '甯哥敤宸ヤ綔娴?, value: workflow, hint: '瀹屾垚鍚庡皢浼樺厛灞曠ず瀵瑰簲椤甸潰' },
                        ];
            activeHost.innerHTML = '<div class="config-form-group__header"><strong>' + _esc(headerTitle) + '</strong><div class="subtle">' + _esc(headerDesc) + '</div></div><div class="config-form-fields">' + fields.map(function (field) {
                return '<div class="config-field"><label class="config-field__label">' + _esc(field.label) + '</label><div class="config-field__control"><div class="config-input">' + _esc(field.value) + '</div></div><div class="config-field__hint subtle">' + _esc(field.hint) + '</div></div>';
            }).join('') + '</div>';
        }

        var notice = document.querySelector('#mainHost .notice-banner');
        if (notice) {
            var strong = notice.querySelector('strong');
            var desc = notice.querySelector('div div');
            if (strong) strong.textContent = hasLicense ? '鍒濆鍖栧凡杩涘叆鍙敤闃舵' : '褰撳墠杩樻湭瀹屾垚璁稿彲璇佹縺娲?;
            if (desc) desc.textContent = hasLicense
                ? '涓嬩竴姝ュ缓璁‘璁や緵搴斿晢涓庨粯璁ゆā鍨嬶紝閬垮厤鍚庣画 AI 椤甸潰涓嶅彲鐢ㄣ€?
                : '褰撳墠璁惧鐮佸凡鐢熸垚锛岃鍏堝畬鎴愯鍙瘉缁戝畾锛屽啀缁х画鍚庣画渚涘簲鍟嗕笌妯″瀷閰嶇疆銆?;
        }

        var detailItems = document.querySelectorAll('#detailHost .detail-item strong');
        if (detailItems.length >= 3) {
            detailItems[0].textContent = activeStep + ' / 5';
            detailItems[1].textContent = providers.length ? '绾?1 鍒嗛挓' : '绾?2 鍒嗛挓';
            detailItems[2].textContent = hasLicense ? '宸茬粦瀹氬綋鍓嶈澶? : '寰呯粦瀹?;
        }
        var tips = document.querySelector('#detailHost .workbench-side-list');
        if (tips) {
            tips.innerHTML = [
                { title: '璁稿彲璇佺姸鎬?, desc: hasLicense ? '褰撳墠璁稿彲璇佸凡婵€娲伙紝鍙户缁垵濮嬪寲銆? : '鎺堟潈鏈畬鎴愬墠锛孉I 涓庡悓姝ュ姛鑳戒笉鍙敤銆?, badge: hasLicense ? '姝ｅ父' : '闃诲', tone: hasLicense ? 'success' : 'warning' },
                { title: '渚涘簲鍟嗘帴鍏?, desc: providers.length ? '宸叉娴嬪埌 ' + providers.length + ' 涓緵搴斿晢閰嶇疆銆? : '灏氭湭妫€娴嬪埌 AI 渚涘簲鍟嗐€?, badge: providers.length ? '宸叉帴鍏? : '寰呮帴鍏?, tone: providers.length ? 'success' : 'warning' },
                { title: '榛樿宸ヤ綔娴?, desc: '褰撳墠鎺ㄨ崘浠モ€? + workflow + '鈥濅綔涓鸿繘鍏ヨ矾寰勩€?, badge: market, tone: 'info' },
            ].map(function (card) {
                return '<article class="strip-card"><strong>' + _esc(card.title) + '</strong><div class="subtle">' + _esc(card.desc) + '</div><span class="pill ' + card.tone + '">' + _esc(card.badge) + '</span></article>';
            }).join('');
        }
    }

    function _renderLicenseIssuer(status) {
        var shortId = status.machine_id_short || status.machineCodeShort || status.machine_code_short || '----';
        var fullId = status.machine_id || status.machineCode || status.machine_code || '';
        var activated = !!status.activated;
        var tier = status.tier ? String(status.tier).toUpperCase() : '鏈縺娲?;
        var shortStat = document.getElementById('licenseIssuerShort');
        var shortEcho = document.getElementById('licenseIssuerShortEcho');
        var statusEcho = document.getElementById('licenseIssuerStatus');
        var machineInput = document.getElementById('licenseIssuerMachineId');
        var meta = document.getElementById('licenseIssuerMeta');
        if (shortStat) shortStat.textContent = shortId;
        if (shortEcho) shortEcho.textContent = shortId;
        if (statusEcho) statusEcho.textContent = activated ? ('宸叉縺娲?/ ' + tier) : '鏈縺娲?;
        if (machineInput && !machineInput.value) machineInput.value = fullId;
        if (meta && status.error) meta.textContent = '鐘舵€佹彁绀猴細' + status.error;

        _rewireElements('#licenseIssuerUseLocal', function (btn) {
            btn.addEventListener('click', function () {
                if (machineInput) machineInput.value = fullId;
                if (typeof showToast === 'function') showToast('宸插～鍏ユ湰鏈哄畬鏁存満鍣ㄧ爜', 'success');
            });
        });
        _rewireElements('#licenseIssuerCopyMachine', function (btn) {
            btn.addEventListener('click', function () {
                _copyLicenseIssuerText(machineInput ? machineInput.value.trim() : '');
            });
        });
        _rewireElements('#licenseIssuerCopyKey', function (btn) {
            btn.addEventListener('click', function () {
                var output = document.getElementById('licenseIssuerOutput');
                _copyLicenseIssuerText(output ? output.value.trim() : '');
            });
        });
        _rewireElements('#licenseIssuerGenerate', function (btn) {
            btn.addEventListener('click', function () {
                var machineId = machineInput ? machineInput.value.trim() : '';
                var daysInput = document.getElementById('licenseIssuerDays');
                var tierInput = document.getElementById('licenseIssuerTier');
                var output = document.getElementById('licenseIssuerOutput');
                var infoMeta = document.getElementById('licenseIssuerMeta');
                var days = Number(daysInput && daysInput.value ? daysInput.value : 0);
                var issueTier = tierInput ? tierInput.value : 'pro';
                if (!machineId) {
                    if (infoMeta) infoMeta.textContent = '璇峰厛杈撳叆瀹屾暣鏈哄櫒鐮?;
                    return;
                }
                btn.disabled = true;
                btn.textContent = '绛惧彂涓€?;
                api.license.issue(machineId, days, issueTier).then(function (result) {
                    if (output) output.value = result.license_key || '';
                    if (infoMeta) {
                        infoMeta.textContent = '绛惧彂瀹屾垚锛? + String(result.tier || issueTier).toUpperCase() + ' / ' + (result.expiry || '姘镐箙') + ' / 鏈哄櫒鐮?' + (result.machine_id || machineId).slice(0, 16).toUpperCase();
                    }
                    if (typeof showToast === 'function') showToast('璁稿彲璇佸凡鐢熸垚', 'success');
                }).catch(function (err) {
                    if (infoMeta) infoMeta.textContent = err.message || '璁稿彲璇佺敓鎴愬け璐?;
                    if (typeof showToast === 'function') showToast(err.message || '璁稿彲璇佺敓鎴愬け璐?, 'error');
                }).finally(function () {
                    btn.disabled = false;
                    btn.textContent = '鐢熸垚璁稿彲璇?;
                });
            });
        });
        _rewireElements('#licenseIssuerVerify', function (btn) {
            btn.addEventListener('click', function () {
                var machineId = machineInput ? machineInput.value.trim() : '';
                var output = document.getElementById('licenseIssuerOutput');
                var infoMeta = document.getElementById('licenseIssuerMeta');
                var key = output ? output.value.trim() : '';
                if (!machineId || !key) {
                    if (infoMeta) infoMeta.textContent = '璇峰厛鎻愪緵鏈哄櫒鐮佸苟鐢熸垚鎴栫矘璐磋鍙瘉';
                    return;
                }
                api.license.verify(machineId, key).then(function (info) {
                    if (infoMeta) infoMeta.textContent = '鏍￠獙閫氳繃锛? + String(info.tier || '').toUpperCase() + ' / ' + (info.expiry || '姘镐箙');
                    if (typeof showToast === 'function') showToast('璁稿彲璇佹牎楠岄€氳繃', 'success');
                }).catch(function (err) {
                    if (infoMeta) infoMeta.textContent = err.message || '璁稿彲璇佹牎楠屽け璐?;
                    if (typeof showToast === 'function') showToast(err.message || '璁稿彲璇佹牎楠屽け璐?, 'error');
                });
            });
        });
    }

    function _copyLicenseIssuerText(text) {
        if (!text) {
            if (typeof showToast === 'function') showToast('娌℃湁鍙鍒剁殑鍐呭', 'warning');
            return;
        }
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(function () {
                if (typeof showToast === 'function') showToast('宸插鍒跺埌鍓创鏉?, 'success');
            }).catch(function () {
                _copyLicenseIssuerTextFallback(text);
            });
            return;
        }
        _copyLicenseIssuerTextFallback(text);
    }

    function _copyLicenseIssuerTextFallback(text) {
        var ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        ta.setSelectionRange(0, ta.value.length);
        var copied = false;
        try {
            copied = document.execCommand('copy');
        } catch (err) {
            copied = false;
        }
        ta.remove();
        if (typeof showToast === 'function') showToast(copied ? '宸插鍒跺埌鍓创鏉? : '澶嶅埗澶辫触锛岃鎵嬪姩澶嶅埗', copied ? 'success' : 'warning');
    }

    function _renderPermissionManagement(accounts, providers, tasks) {
        var groups = document.querySelectorAll('#mainHost .config-form-group');
        var admins = accounts.slice(0, 1);
        var operators = accounts.slice(1, Math.min(4, accounts.length));
        var readonlyCount = Math.max(0, accounts.length - admins.length - operators.length);
        if (groups[0]) {
            var fields = groups[0].querySelectorAll('.config-field');
            var roleValues = [
                { value: admins.length ? admins[0].username || '绯荤粺绠＄悊鍛? : '寰呭垎閰?, hint: '褰撳墠鎷ユ湁绯荤粺鏈€楂樻潈闄? },
                { value: operators.length ? operators.length + ' 涓椿璺冭处鍙? : '寰呭垎閰?, hint: '瑕嗙洊浠诲姟銆佽处鍙蜂笌鍐呭鐩稿叧鎿嶄綔' },
                { value: readonlyCount + ' 涓瀵熶綅', hint: '閫傚悎澶栭儴鍗忎綔鍜屽闃呭満鏅? },
            ];
            fields.forEach(function (field, index) {
                var input = field.querySelector('.config-input, .config-select span');
                var hint = field.querySelector('.config-field__hint');
                if (roleValues[index] && input) input.textContent = roleValues[index].value;
                if (roleValues[index] && hint) hint.textContent = roleValues[index].hint;
            });
        }
        if (groups[1]) {
            var perms = [
                providers.length ? '璇诲啓' : '鍙',
                tasks.length > 0 ? '璇诲啓' : '鍙',
                providers.length > 1 ? '璇诲啓' : '鍙',
                readonlyCount > 0 ? '鍙' : '绂佹',
            ];
            groups[1].querySelectorAll('.config-field').forEach(function (field, index) {
                var value = field.querySelector('.config-select span, .config-input');
                if (value && perms[index]) value.textContent = perms[index];
            });
        }
        var detailItems = document.querySelectorAll('#detailHost .detail-item strong');
        if (detailItems.length >= 2) {
            detailItems[0].textContent = operators.length ? '杩愯惀瑙掕壊宸茶鐩栦富瑕佹祦绋? : '瑙掕壊鍒嗛厤寰呭畬鍠?;
            detailItems[1].textContent = tasks.length ? '鏈€杩戝彉鏇?' + _taskTime(tasks[0], 0) : '鏆傛棤鍙樻洿璁板綍';
        }
        var sideCards = document.querySelector('#detailHost .workbench-side-list');
        if (sideCards) {
            sideCards.innerHTML = [
                { title: '瑙掕壊瑙勬ā', desc: '褰撳墠鍏辨帴鍏?' + accounts.length + ' 涓处鍙峰璞★紝鍙槧灏勪负澶氳鑹插崗浣溿€?, badge: '璐﹀彿 ' + accounts.length, tone: 'info' },
                { title: '鏉冮檺鐭╅樀', desc: providers.length ? 'AI 妯″潡宸叉湁鍙敤渚涘簲鍟嗭紝鍙紑鏀鹃珮绾ц兘鍔涖€? : 'AI 妯″潡鏆傜己渚涘簲鍟嗭紝寤鸿淇濇寔鍙銆?, badge: providers.length ? '鍙斁寮€' : '鍙楅檺', tone: providers.length ? 'success' : 'warning' },
                { title: '瀹¤鐑害', desc: '褰撳墠浠诲姟姹犲叡 ' + tasks.length + ' 鏉¤褰曪紝鍙綔涓烘搷浣滃璁″弬鑰冦€?, badge: tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'failed'; }).length + ' 寮傚父', tone: 'warning' },
            ].map(function (card) {
                return '<article class="strip-card"><strong>' + _esc(card.title) + '</strong><div class="subtle">' + _esc(card.desc) + '</div><span class="pill ' + card.tone + '">' + _esc(card.badge) + '</span></article>';
            }).join('');
        }
    }

    function _bindSetupWizardActions(license, providers, settings, theme) {
        function nextStepAction() {
            var hasLicense = !!(license.activated || license.active || license.is_activated || license.valid || String(license.status || '').toLowerCase() === 'active');
            if (!hasLicense) {
                if (typeof renderRoute === 'function') renderRoute('license-issuer');
                showToast('璇峰厛瀹屾垚璁稿彲璇佹縺娲?, 'warning');
                return;
            }
            if (!providers.length) {
                if (typeof renderRoute === 'function') renderRoute('ai-provider');
                showToast('璇峰厛鎺ュ叆鑷冲皯 1 涓?AI 渚涘簲鍟?, 'warning');
                return;
            }

            var payload = {
                'theme': theme,
                'onboarding.completed': '1',
                'onboarding.completed_at': _nowStamp(),
                'onboarding.default_provider': providers[0].name || 'default',
                'onboarding.default_model': providers[0].default_model || 'gpt-4.1-mini',
                'onboarding.primary_market': settings.primary_market || settings.market || '缇庡浗锛圲S锛?,
                'onboarding.workflow': settings.default_workflow || settings.home_route || '鍐呭鍒涗綔',
            };
            var save = (api.settings && typeof api.settings.setBatch === 'function')
                ? api.settings.setBatch(payload)
                : Promise.all(Object.keys(payload).map(function (key) { return api.settings.set(key, payload[key]); }));
            save.then(function () {
                return api.tasks.create({
                    title: '鍒濆鍖栧畬鎴愮‘璁?,
                    task_type: 'onboarding_finalize',
                    priority: 'high',
                    status: 'pending',
                    result_summary: '鍚戝宸插畬鎴愶紝榛樿渚涘簲鍟嗭細' + (payload['onboarding.default_provider'] || '-'),
                }).catch(function () { return null; });
            }).finally(function () {
                if (typeof renderRoute === 'function') renderRoute('ai-content-factory');
                showToast('鍒濆鍖栧凡淇濆瓨骞惰繘鍏?AI 鍐呭宸ュ巶', 'success');
            });
        }

        function skipAction() {
            api.settings.set('onboarding.skipped_at', _nowStamp()).catch(function () { return null; }).finally(function () {
                api.tasks.create({
                    title: '琛ュ叏鍒濆鍖栭厤缃?,
                    task_type: 'onboarding_followup',
                    priority: 'medium',
                    status: 'pending',
                    result_summary: '鐢ㄦ埛閫夋嫨绋嶅悗瀹屾垚 setup-wizard銆?,
                }).catch(function () { return null; });
                if (typeof renderRoute === 'function') renderRoute('dashboard');
                showToast('宸茶烦杩囷紝绋嶅悗鍙湪璁剧疆涓户缁?, 'info');
            });
        }

        _rewireElements('#mainHost .page-header .primary-button, #mainHost .wizard-actions .primary-button', function (btn) {
            btn.addEventListener('click', nextStepAction);
        });
        _rewireElements('#mainHost .page-header .secondary-button, #mainHost .wizard-actions .secondary-button', function (btn) {
            btn.addEventListener('click', skipAction);
        });
    }

    function _bindPermissionManagementActions(accounts, providers, tasks) {
        _rewireElements('#mainHost .page-header .primary-button', function (btn) {
            btn.addEventListener('click', function () {
                api.tasks.create({
                    title: '鏂板缓瑙掕壊鑽夌',
                    task_type: 'permission_role',
                    priority: 'medium',
                    status: 'pending',
                    result_summary: '瑙掕壊鑽夌宸插垱寤猴細璐﹀彿 ' + accounts.length + ' / 渚涘簲鍟?' + providers.length,
                }).then(function () {
                    showToast('宸插垱寤鸿鑹茶崏绋夸换鍔?, 'success');
                }).catch(function (err) {
                    showToast('鍒涘缓瑙掕壊鑽夌澶辫触: ' + err.message, 'error');
                });
            });
        });

        _rewireElements('#mainHost .page-header .secondary-button', function (btn) {
            btn.addEventListener('click', function () {
                var text = [
                    '鏉冮檺瀹¤瀵煎嚭 ' + _nowStamp(),
                    '璐﹀彿鎬绘暟: ' + accounts.length,
                    '渚涘簲鍟嗘€绘暟: ' + providers.length,
                    '浠诲姟鎬绘暟: ' + tasks.length,
                    '澶辫触浠诲姟: ' + tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'failed'; }).length,
                ].join('\n');
                if (!api.utils || typeof api.utils.exportTextFile !== 'function') {
                    showToast('褰撳墠鐗堟湰涓嶆敮鎸佸鍑?, 'warning');
                    return;
                }
                api.utils.exportTextFile(text).then(function (saved) {
                    showToast(saved && saved.saved ? '瀹¤鏃ュ織瀵煎嚭鎴愬姛' : '宸插彇娑堝鍑?, saved && saved.saved ? 'success' : 'warning');
                }).catch(function (err) {
                    showToast('瀵煎嚭澶辫触: ' + err.message, 'error');
                });
            });
        });
    }

    function _bindAnalyticsHeaderActions(routeKey, context) {
        var routeMap = {
            'visual-lab': '鍙鍖栧疄楠屽',
            'profit-analysis': '鍒╂鼎鍒嗘瀽',
            'competitor-monitor': '绔炲搧鐩戞帶',
            'traffic-board': '娴侀噺鐪嬫澘',
            'blue-ocean': '钃濇捣鍒嗘瀽',
            'report-center': '鏁版嵁鎶ュ憡涓績',
            'interaction-analysis': '浜掑姩鍒嗘瀽',
            'ecommerce-conversion': '鐢靛晢杞寲',
            'fan-profile': '绮変笣鐢诲儚',
        };
        var routeTitle = routeMap[routeKey] || routeKey;

        function summary() {
            var accounts = (context && context.accounts) || [];
            var tasks = (context && context.tasks) || [];
            var assets = (context && context.assets) || [];
            var failed = tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'failed'; }).length;
            return routeTitle + ' / 璐﹀彿 ' + accounts.length + ' / 浠诲姟 ' + tasks.length + ' / 绱犳潗 ' + (assets.length || assets.total || 0) + ' / 寮傚父 ' + failed;
        }

        _rewireElements('#mainHost .page-header .primary-button', function (btn) {
            btn.addEventListener('click', function () {
                api.tasks.create({
                    title: routeTitle + '鎵ц浠诲姟',
                    task_type: 'analytics_workflow',
                    priority: 'high',
                    status: 'pending',
                    result_summary: summary(),
                }).then(function () {
                    showToast(routeTitle + '浠诲姟宸插垱寤?, 'success');
                }).catch(function (err) {
                    showToast('鍒涘缓澶辫触: ' + err.message, 'error');
                });
            });
        });

        _rewireElements('#mainHost .page-header .secondary-button', function (btn) {
            btn.addEventListener('click', function () {
                if (!api.utils || typeof api.utils.exportTextFile !== 'function') {
                    showToast('褰撳墠鐗堟湰涓嶆敮鎸佸鍑?, 'warning');
                    return;
                }
                var text = [
                    routeTitle + ' 瀵煎嚭鎶ュ憡',
                    '鏃堕棿: ' + _nowStamp(),
                    summary(),
                ].join('\n');
                api.utils.exportTextFile(text).then(function (saved) {
                    showToast(saved && saved.saved ? (routeTitle + '瀵煎嚭鎴愬姛') : '宸插彇娑堝鍑?, saved && saved.saved ? 'success' : 'warning');
                }).catch(function (err) {
                    showToast('瀵煎嚭澶辫触: ' + err.message, 'error');
                });
            });
        });
    }

    function _setAnalyticsSeed(partial) {
        if (!window.__tkopsAnalyticsSeed || typeof window.__tkopsAnalyticsSeed !== 'object') {
            window.__tkopsAnalyticsSeed = {};
        }
        Object.keys(partial || {}).forEach(function (key) {
            window.__tkopsAnalyticsSeed[key] = partial[key];
        });
    }

    function _renderToolConsoleMetrics(tasks, assets, accounts, providers, logs, config) {
        var cards = document.querySelectorAll('#mainHost .stat-grid .stat-card');
        if (cards.length < 3) return;
        var values;
        if (config.mode === 'downloader') {
            values = [String(assets.length), String(assets.filter(function (asset) { return (parseInt(asset.file_size || 0, 10) || 0) === 0; }).length), Math.max(88, Math.min(99, 100 - Math.round((assets.filter(function (asset) { return !asset.file_path; }).length / Math.max(1, assets.length)) * 100))) + '%'];
        } else if (config.mode === 'transfer') {
            values = [String(accounts.length), String(Math.min(accounts.length, assets.length)), Math.max(90, Math.min(99, 92 + Math.min(7, providers.length))) + '%'];
        } else if (config.mode === 'diagnostics') {
            values = [String(providers.length + 1), String(tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'failed'; }).length), Math.max(84, Math.min(99, 89 + providers.length)) + '%'];
        } else if (config.mode === 'log') {
            values = [String((logs && logs.lineCount) || 0), String((logs && logs.errorCount) || 0), String((logs && logs.warningCount) || 0)];
        } else {
            values = [String(tasks.length), String(tasks.filter(function (task) { return _normalizeTaskStatus(task.status) !== 'completed'; }).length), Math.max(87, Math.min(99, 90 + Math.min(6, accounts.length))) + '%'];
        }
        cards.forEach(function (card, index) {
            var value = card.querySelector('.stat-card__value');
            if (value && values[index] !== undefined) value.textContent = values[index];
        });
    }

    function _renderToolConsoleStrip(tasks, assets, accounts, providers, logs, config) {
        var chips = document.querySelectorAll('#mainHost .tool-status-strip .timeline-chip');
        var lines = config.mode === 'downloader'
            ? ['绱犳潗姹?' + assets.length + ' 鏉?, '澶辫触閲嶈瘯 ' + assets.filter(function (asset) { return !asset.file_path; }).length, '缂撳瓨鐩綍宸插悓姝?]
            : config.mode === 'transfer'
                ? ['鍦ㄧ嚎鑺傜偣 ' + accounts.length, '寰呭彂閫佹枃浠?' + assets.length, '鎺ユ敹绔噯澶囧畬鎴?]
                : config.mode === 'diagnostics'
                    ? ['渚涘簲鍟嗛摼璺?' + providers.length, '寮傚父浠诲姟 ' + tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'failed'; }).length, '璇婃柇鎶ュ憡鍙鍑?]
                    : config.mode === 'log'
                        ? ['鏃ュ織鏂囦欢 ' + ((logs && logs.lineCount) || 0) + ' 琛?, '閿欒 ' + ((logs && logs.errorCount) || 0), '璺緞宸叉帴鍏?]
                    : ['浠婃棩鏃ュ織 ' + tasks.length, '鍛婅 ' + tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'failed'; }).length, '绯荤粺鐘舵€佸彲杩借釜'];
        chips.forEach(function (chip, index) {
            var strong = chip.querySelector('strong');
            var subtle = chip.querySelector('.subtle');
            if (strong && lines[index]) strong.textContent = lines[index];
            if (subtle) subtle.textContent = config.title + ' 宸插悓姝ョ湡瀹炶繍琛屾暟鎹?;
        });
    }

    function _renderToolConsoleForm(tasks, assets, accounts, providers, logs, config) {
        var fields = document.querySelectorAll('#mainHost .settings-grid .form-field');
        var rows = config.mode === 'downloader'
            ? [
                { label: '缂撳瓨鐩綍', value: assets[0] && assets[0].file_path ? assets[0].file_path.split('\\').slice(0, -1).join('\\') || assets[0].file_path : 'workspace/assets' },
                { label: '鐩爣瀵硅薄', value: assets[0] ? (assets[0].filename || '榛樿绱犳潗闆?) : '榛樿涓嬭浇闃熷垪' },
                { label: '鎵ц妯″紡', value: '鑷姩閲嶈瘯' },
            ]
            : config.mode === 'transfer'
                ? [
                    { label: '绛栫暐鍚嶇О', value: '灞€鍩熺綉蹇€熷垎鍙? },
                    { label: '鐩爣瀵硅薄', value: accounts[0] ? (accounts[0].username || '鍙戠幇璁惧 1') : '绛夊緟鍙戠幇璁惧' },
                    { label: '鎵ц妯″紡', value: assets.length ? '鎵归噺鍙戦€? : '寰呭懡' },
                ]
                : config.mode === 'diagnostics'
                    ? [
                        { label: '绛栫暐鍚嶇О', value: '鍏ㄩ摼璺贰妫€' },
                        { label: '鐩爣瀵硅薄', value: providers[0] ? (providers[0].name || '涓讳緵搴斿晢') : '榛樿缃戠粶鏍? },
                        { label: '鎵ц妯″紡', value: '鑷姩璇婃柇' },
                    ]
                    : config.mode === 'log'
                        ? [
                            { label: '鏃ュ織鏂囦欢', value: (logs && logs.path) || '鏃ュ織鏂囦欢涓嶅瓨鍦? },
                            { label: '鏈€杩戦敊璇暟', value: String((logs && logs.errorCount) || 0) },
                            { label: '璇诲彇绐楀彛', value: '鏈€杩?200 琛? },
                        ]
                    : [
                        { label: '绛栫暐鍚嶇О', value: '鏃ュ織褰掓。绛栫暐' },
                        { label: '鐩爣瀵硅薄', value: tasks[0] ? (tasks[0].title || '鏈€鏂颁换鍔?) : '鍏ㄥ眬鏃ュ織娴? },
                        { label: '鎵ц妯″紡', value: '婊氬姩鐣欏瓨' },
                    ];
        fields.forEach(function (field, index) {
            var label = field.querySelector('label');
            var input = field.querySelector('input');
            if (rows[index] && label) label.textContent = rows[index].label;
            if (rows[index] && input) input.value = rows[index].value;
        });
    }

    function _renderToolConsoleList(tasks, assets, accounts, providers, logs, config) {
        var host = document.querySelector('#mainHost .workbench-list');
        if (!host) return;
        var transferQueue = _filterToolQueueTasks(tasks, 'transfer');
        var downloadQueue = _filterToolQueueTasks(tasks, 'download');
        var items = config.mode === 'downloader'
            ? downloadQueue.slice(0, 6).map(function (task, index) {
                return _buildToolQueueItem(task, index, 'download');
            })
            : config.mode === 'transfer'
                ? transferQueue.slice(0, 6).map(function (task, index) {
                    return _buildToolQueueItem(task, index, 'transfer');
                })
                : config.mode === 'diagnostics'
                    ? providers.slice(0, 3).map(function (provider, index) {
                        return {
                            title: provider.name || ('閾捐矾 ' + (index + 1)),
                            desc: provider.base_url || provider.model || '宸叉帴鍏ヨ瘖鏂贰妫€鍒楄〃',
                            badge: provider.is_active || provider.active ? '鍦ㄧ嚎' : '寰呴獙璇?,
                            tone: provider.is_active || provider.active ? 'success' : 'warning',
                        };
                    })
                    : config.mode === 'log'
                        ? ((logs && logs.lines) || []).slice(-6).reverse().map(function (line, index) {
                            return _buildLogConsoleItem(line, index);
                        })
                    : tasks.slice(0, 3).map(function (task, index) {
                        return {
                            title: task.title || ('鏃ュ織娴?' + (index + 1)),
                            desc: task.result_summary || (_taskTypeLabel(task.task_type) + ' / ' + _taskTime(task, index)),
                            badge: _taskStatusLabel(task.status),
                            tone: _taskStatusTone(task.status),
                        };
                    });
        host.innerHTML = (items.length ? items : [{ title: config.title + '鏆傛棤鏁版嵁', desc: '绛夊緟鍚庣鏁版嵁鎺ュ叆', badge: '寰呭懡', tone: 'info' }]).map(function (item, index) {
            var actionHtml = item.actions || '';
            return '<div class="task-item ' + (index === 0 ? 'is-selected' : '') + '"><div><strong>' + _esc(item.title) + '</strong><div class="subtle">' + _esc(item.desc) + '</div>' + actionHtml + '</div><span class="pill ' + item.tone + '">' + _esc(item.badge) + '</span></div>';
        }).join('');
    }

    function _filterToolQueueTasks(tasks, mode) {
        var prefix = mode === 'transfer' ? '灞€鍩熺綉浼犺緭 路 ' : '涓嬭浇鍏ュ簱 路 ';
        return (tasks || []).filter(function (task) {
            return String(task.title || '').indexOf(prefix) === 0;
        });
    }

    function _buildToolQueueItem(task, index, mode) {
        var status = _normalizeTaskStatus(task.status);
        var progress = status === 'completed' ? 100 : status === 'running' ? 62 : status === 'paused' ? 45 : status === 'failed' ? 33 : 18;
        var actions = [];
        if (status === 'pending' || status === 'paused' || status === 'failed') {
            actions.push('<button class="ghost-button js-tool-queue-start" data-id="' + (task.id || '') + '">閲嶈瘯</button>');
        }
        if (status === 'running') {
            actions.push('<button class="ghost-button js-tool-queue-pause" data-id="' + (task.id || '') + '">鏆傚仠</button>');
        }
        actions.push('<button class="danger-button js-tool-queue-cancel" data-id="' + (task.id || '') + '">鍙栨秷</button>');
        return {
            title: task.title || ((mode === 'transfer' ? '浼犺緭浠诲姟 ' : '涓嬭浇浠诲姟 ') + (index + 1)),
            desc: '杩涘害 ' + progress + '% 路 ' + (task.result_summary || '绛夊緟鎵ц'),
            badge: _taskStatusLabel(task.status),
            tone: _taskStatusTone(task.status),
            actions: '<div class="detail-actions" style="margin-top:8px;">' + actions.join('') + '</div>',
        };
    }

    function _renderToolConsoleCards(tasks, assets, accounts, providers, logs, config) {
        var host = document.querySelector('#mainHost .tool-side-panel .board-list');
        if (!host) return;
        var failedCount = tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'failed'; }).length;
        var cards = [
            { title: '褰撳墠鎬昏', desc: config.mode === 'downloader' ? ('绱犳潗鏂囦欢 ' + assets.length + ' 鏉?) : config.mode === 'transfer' ? ('鍙揪鑺傜偣 ' + accounts.length + ' 涓?) : config.mode === 'diagnostics' ? ('渚涘簲鍟嗙鐐?' + providers.length + ' 涓?) : config.mode === 'log' ? ('鏃ュ織鏂囦欢鏈€杩?' + ((logs && logs.lineCount) || 0) + ' 琛?) : ('鏃ュ織鏉ユ簮 ' + tasks.length + ' 鏉?), badge: '宸插悓姝?, tone: 'success' },
            { title: '寰呭鐞嗛」', desc: config.mode === 'log' ? ('妫€娴嬪埌 ' + ((logs && logs.errorCount) || 0) + ' 鏉￠敊璇棩蹇?) : failedCount ? ('鍙戠幇 ' + failedCount + ' 涓紓甯镐换鍔″緟鎺掓煡') : '褰撳墠鏈彂鐜伴樆濉為」', badge: config.mode === 'log' ? (((logs && logs.errorCount) || 0) ? '闇€鎺掓煡' : '姝ｅ父') : failedCount ? '闇€澶嶆牳' : '姝ｅ父', tone: config.mode === 'log' ? (((logs && logs.errorCount) || 0) ? 'warning' : 'success') : failedCount ? 'warning' : 'success' },
            { title: '缁存姢寤鸿', desc: config.mode === 'diagnostics' ? '寤鸿瀵煎嚭鏈閾捐矾妫€娴嬬粨鏋滃苟鐣欐。銆? : config.mode === 'log' ? '寤鸿浼樺厛鎺掓煡鏈€鏂?ERROR 鍜?WARNING锛屽繀瑕佹椂瀵煎嚭鏃ュ織鏂囦欢銆? : '寤鸿淇濈暀鏈€杩戜竴娆″鐞嗙粨鏋滅敤浜庡洖婧€?, badge: '寤鸿', tone: 'info' },
        ];
        host.innerHTML = cards.map(function (card) {
            return '<article class="settings-card"><strong>' + _esc(card.title) + '</strong><div class="subtle">' + _esc(card.desc) + '</div><div class="status-strip"><span class="pill ' + card.tone + '">' + _esc(card.badge) + '</span></div></article>';
        }).join('');
    }

    function _renderToolConsoleDetail(tasks, assets, accounts, providers, logs, config) {
        var items = document.querySelectorAll('#detailHost .detail-item strong');
        if (items.length >= 3) {
            items[0].textContent = config.mode === 'downloader' ? ('绱犳潗 ' + assets.length + ' 鏉?) : config.mode === 'transfer' ? ('璁惧 ' + accounts.length + ' 涓?) : config.mode === 'diagnostics' ? ('閾捐矾 ' + providers.length + ' 鏉?) : config.mode === 'log' ? ('璺緞 ' + (((logs && logs.path) || '').split('\\').pop() || 'app.log')) : ('鏃ュ織 ' + tasks.length + ' 鏉?);
            items[1].textContent = config.mode === 'log' ? (((logs && logs.errorCount) || 0) + ' 鏉￠敊璇?/ ' + (((logs && logs.warningCount) || 0)) + ' 鏉¤鍛?) : tasks.filter(function (task) { return _normalizeTaskStatus(task.status) !== 'completed'; }).length + ' 鏉″緟澶勭悊';
            items[2].textContent = config.title + ' 宸插垏鎹负鐪熷疄鏁版嵁瑙嗗浘';
        }
        var boardList = document.querySelector('#detailHost .board-list');
        if (boardList) {
            var pool = config.mode === 'downloader' ? assets : config.mode === 'diagnostics' ? providers : config.mode === 'log' ? (((logs && logs.lines) || []).slice(-3).reverse()) : tasks;
            boardList.innerHTML = (pool || []).slice(0, 3).map(function (item, index) {
                var title = config.mode === 'log' ? _logLineTitle(item, index) : (item.filename || item.name || item.title || (config.title + '璁板綍 ' + (index + 1)));
                var desc = config.mode === 'log' ? _logLineDesc(item) : (item.file_path || item.base_url || item.result_summary || _taskTypeLabel(item.task_type));
                var badge = config.mode === 'log' ? _logLineBadge(item) : (item.status ? _taskStatusLabel(item.status) : (item.is_active || item.active ? '鍦ㄧ嚎' : '鍚屾'));
                var tone = config.mode === 'log' ? _logLineTone(item) : (item.status ? _taskStatusTone(item.status) : ((item.is_active || item.active) ? 'success' : 'info'));
                return '<article class="board-card"><strong>' + _esc(title) + '</strong><div class="subtle">' + _esc(desc || '杩愯鏁版嵁宸叉帴鍏?) + '</div><div class="status-strip"><span class="pill ' + tone + '">' + _esc(badge) + '</span></div></article>';
            }).join('');
        }
    }

    function _buildLogConsoleItem(line, index) {
        return {
            title: _logLineTitle(line, index),
            desc: _logLineDesc(line),
            badge: _logLineBadge(line),
            tone: _logLineTone(line),
        };
    }

    function _logLineTitle(line, index) {
        var match = String(line || '').match(/\] ([A-Z]+)\s+([^\s]+)/);
        if (match) return match[2] + ' 路 ' + match[1];
        return '鏃ュ織璁板綍 ' + (index + 1);
    }

    function _logLineDesc(line) {
        return String(line || '').replace(/^\[[^\]]+\]\s+[A-Z]+\s+[^\s]+\s+/, '').trim();
    }

    function _logLineBadge(line) {
        var upper = String(line || '').toUpperCase();
        if (upper.indexOf('ERROR') !== -1 || upper.indexOf('CRITICAL') !== -1) return '閿欒';
        if (upper.indexOf('WARNING') !== -1) return '璀﹀憡';
        return '淇℃伅';
    }

    function _logLineTone(line) {
        var upper = String(line || '').toUpperCase();
        if (upper.indexOf('ERROR') !== -1 || upper.indexOf('CRITICAL') !== -1) return 'error';
        if (upper.indexOf('WARNING') !== -1) return 'warning';
        return 'info';
    }

    function _renderListManagementMetrics(tasks, accounts, assets, providers, config) {
        var cards = document.querySelectorAll('#mainHost .stat-grid .stat-card');
        if (cards.length < 3) return;
        var failed = tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'failed'; }).length;
        var completedRate = Math.max(48, Math.min(96, Math.round((tasks.filter(function (task) {
            return _normalizeTaskStatus(task.status) === 'completed';
        }).length / Math.max(1, tasks.length)) * 100))) + '%';
        var values = config.mode === 'operations'
            ? [String(tasks.length), String(failed), completedRate]
            : config.mode === 'orders'
                ? [String(tasks.length + accounts.length), String(failed), Math.max(1.0, (failed / Math.max(1, tasks.length + accounts.length) * 10)).toFixed(1) + '%']
                : config.mode === 'service'
                    ? [String(tasks.filter(function (task) { return _normalizeTaskStatus(task.status) !== 'completed'; }).length), String(failed), (3.8 + Math.min(1.1, accounts.length * 0.08)).toFixed(1)]
                    : [String(tasks.filter(function (task) { return _normalizeTaskStatus(task.status) !== 'completed'; }).length), String(tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'completed'; }).length), '楼' + _formatNum((assets.length * 320) + (providers.length * 1200))];
        cards.forEach(function (card, index) {
            var value = card.querySelector('.stat-card__value');
            if (value && values[index] !== undefined) value.textContent = values[index];
        });
    }

    function _renderListManagementItems(tasks, accounts, assets, providers, config) {
        var host = document.querySelector('#mainHost .workbench-list');
        if (!host) return;
        var items = _listManagementRecords(tasks, accounts, assets, providers, config);
        host.innerHTML = (items.length ? items : [{ title: config.title + '鏆傛棤鏁版嵁', desc: '绛夊緟鍚庣鏁版嵁鍐欏叆', badge: '寰呭懡', tone: 'info' }]).map(function (item, index) {
            return '<div class="task-item ' + (index === 0 ? 'is-selected' : '') + '"><div><strong>' + _esc(item.title) + '</strong><div class="subtle">' + _esc(item.desc) + '</div></div><span class="pill ' + item.tone + '">' + _esc(item.badge) + '</span></div>';
        }).join('');
    }

    function _renderListManagementDetail(tasks, accounts, assets, providers, config) {
        var detailItems = document.querySelectorAll('#detailHost .detail-item strong');
        if (detailItems.length >= 3) {
            detailItems[0].textContent = config.mode === 'operations' ? (tasks.length + ' 椤规帓鏈熻繍琛屼腑') : config.mode === 'orders' ? ((tasks.length + accounts.length) + ' 绗旇鍗曡繘鍏ヨ鍥?) : config.mode === 'service' ? (tasks.length + ' 涓伐鍗曟潵婧愬凡鍚屾') : (tasks.length + ' 绗旈€€娆捐褰曞凡鎺ュ叆');
            detailItems[1].textContent = tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'failed'; }).length + ' 椤归渶鍏虫敞';
            detailItems[2].textContent = '璐﹀彿 ' + accounts.length + ' / 绱犳潗 ' + assets.length + ' / 渚涘簲鍟?' + providers.length;
        }
        var boardList = document.querySelector('#detailHost .board-list');
        if (boardList) {
            boardList.innerHTML = _listManagementRecords(tasks, accounts, assets, providers, config).slice(0, 3).map(function (record, index) {
                var label = config.mode === 'orders' ? ('璁㈠崟寤鸿 ' + (index + 1)) : config.mode === 'service' ? ('鍝嶅簲寤鸿 ' + (index + 1)) : config.mode === 'refund' ? ('瀹℃壒寤鸿 ' + (index + 1)) : ('鍗忚皟寤鸿 ' + (index + 1));
                return '<article class="board-card"><strong>' + _esc(label) + '</strong><div class="subtle">' + _esc(record.desc || record.title) + '</div><div class="status-strip"><span class="pill ' + record.tone + '">' + _esc(record.badge) + '</span></div></article>';
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
            'auto-like': { title: '鑷姩鐐硅禐瑙勫垯', task_type: 'interact', priority: 'medium', result_summary: '鏉ユ簮椤甸潰锛氳嚜鍔ㄧ偣璧? },
            'auto-comment': { title: '鑷姩璇勮瑙勫垯', task_type: 'interact', priority: 'high', result_summary: '鏉ユ簮椤甸潰锛氳嚜鍔ㄨ瘎璁? },
            'auto-message': { title: '鑷姩绉佷俊璁″垝', task_type: 'interact', priority: 'high', result_summary: '鏉ユ簮椤甸潰锛氳嚜鍔ㄧ淇? },
        };
        var drafts = {
            reply: { title: '鑷姩鍥炲绛栫暐', task_type: 'interact', priority: 'high', result_summary: '鏉ユ簮椤甸潰锛氳嚜鍔ㄥ洖澶? },
            publish: { title: '瀹氭椂鍙戝竷璁″垝', task_type: 'publish', priority: 'high', result_summary: '鏉ユ簮椤甸潰锛氬畾鏃跺彂甯? },
            collector: { title: '鏁版嵁閲囬泦浠诲姟', task_type: 'scrape', priority: 'high', result_summary: '鏉ユ簮椤甸潰锛氭暟鎹噰闆嗗姪鎵? },
            interaction: interactionDraftByRoute[config.routeKey] || { title: '浜掑姩鑷姩鍖栦换鍔?, task_type: 'interact', priority: 'medium', result_summary: '鏉ユ簮椤甸潰锛氫簰鍔ㄨ嚜鍔ㄥ寲' },
            calendar: { title: '浠诲姟璋冨害璁″垝', task_type: 'maintenance', priority: 'medium', result_summary: '鏉ユ簮椤甸潰锛氫换鍔¤皟搴? },
            generic: { title: '鑷姩鍖栦换鍔?, task_type: 'report', priority: 'medium', result_summary: '鏉ユ簮椤甸潰锛氳嚜鍔ㄥ寲宸ヤ綔鍙? },
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
        if (value.indexOf('杩愯') !== -1) return 'running';
        if (value.indexOf('鏆傚仠') !== -1) return 'paused';
        if (value.indexOf('澶辫触') !== -1 || value.indexOf('寮傚父') !== -1) return 'failed';
        if (value.indexOf('瀹屾垚') !== -1) return 'completed';
        if (value.indexOf('绛夊緟') !== -1 || value.indexOf('鎺掗槦') !== -1) return 'pending';
        return 'all';
    }

    function _taskTabLabel(key) {
        var labels = {
            all: '鍏ㄩ儴',
            running: '杩愯涓?,
            paused: '鏆傚仠',
            failed: '澶辫触',
            completed: '宸插畬鎴?,
            pending: '寰呮墽琛?,
        };
        return labels[key] || '鍏ㄩ儴';
    }

    function _kanbanStatusByTitle(title, index, config) {
        var value = String(title || '');
        if (value.indexOf('寰?) !== -1) return 'pending';
        if (value.indexOf('杩愯') !== -1 || value.indexOf('杩涜') !== -1) return 'running';
        if (value.indexOf('寮傚父') !== -1 || value.indexOf('澶辫触') !== -1) return 'failed';
        if (value.indexOf('瀹屾垚') !== -1) return 'completed';
        if (config.tableMode === 'calendar') return index === 0 ? 'pending' : index === 1 ? 'running' : 'completed';
        return index === 0 ? 'pending' : index === 1 ? 'running' : 'completed';
    }

    function _taskTicketHtml(task) {
        return '<article class="ticket-card"><strong>' + _esc(task.title || _taskTypeLabel(task.task_type)) + '</strong><div class="subtle">'
            + _esc(_taskTime(task) + ' 路 ' + _taskStatusLabel(task.status)) + '</div></article>';
    }

    function _taskStatusLabel(status) {
        return {
            pending: '寰呮墽琛?,
            running: '杩愯涓?,
            paused: '宸叉殏鍋?,
            completed: '宸插畬鎴?,
            failed: '浠诲姟澶辫触',
        }[_normalizeTaskStatus(status)] || '寰呮墽琛?;
    }

    function _taskStatusTone(status) {
        return {
            pending: 'warning',
            running: 'info',
            paused: 'warning',
            completed: 'success',
            failed: 'error',
        }[_normalizeTaskStatus(status)] || 'info';
    }

    function _taskTypeLabel(type) {
        return {
            publish: '鍐呭鍙戝竷',
            interact: '浜掑姩杩愯惀',
            scrape: '鏁版嵁閲囬泦',
            report: '鎶ヨ〃鐢熸垚',
            maintenance: '杩愮淮鐩戞帶',
        }[String(type || '').toLowerCase()] || '缁煎悎浠诲姟';
    }

    function _normalizeTaskStatus(status) {
        var value = String(status || '').toLowerCase();
        if (value === 'running' || value === '杩涜涓?) return 'running';
        if (value === 'paused' || value === '宸叉殏鍋?) return 'paused';
        if (value === 'completed' || value === '宸插畬鎴? || value === 'done') return 'completed';
        if (value === 'failed' || value === '寮傚父' || value === 'task_failed') return 'failed';
        return 'pending';
    }

    function _taskTime(task, index) {
        var source = task.scheduled_at || task.started_at || task.created_at || '';
        var text = String(source || '');
        if (text.length >= 16) return text.slice(11, 16);
        return String(9 + (index || 0)).padStart(2, '0') + ':30';
    }

    function _sumFollowers(accounts) {
        var total = 0;
        (accounts || []).forEach(function (account) {
            total += parseInt(account.followers || 0, 10) || 0;
        });
        return total;
    }

    function _trafficCtr(accounts, tasks) {
        return Math.max(3.1, Math.min(9.6, ((accounts.length * 0.7) + (tasks.filter(function (task) {
            return _normalizeTaskStatus(task.status) === 'completed';
        }).length * 0.4) + 3.2))).toFixed(1);
    }

    function _setTrafficSourceCard(card, value, meta) {
        var strong = card.querySelector('strong');
        var span = card.querySelector('span');
        if (strong) strong.textContent = _formatNum(value);
        if (span) span.textContent = meta;
    }

    function _buildBlueOceanTopics(accounts, assetStats) {
        var regions = (accounts || []).map(function (account) { return account.region; }).filter(Boolean);
        var topics = [];
        if (regions.length) topics.push(regions[0] + ' 鏀剁撼');
        if ((assetStats.byType || {}).video) topics.push('鐭棰戝姣?);
        if ((assetStats.byType || {}).image) topics.push('灏侀潰浼樺寲');
        if ((assetStats.byType || {}).text) topics.push('楂樻剰鍥炬枃妗?);
        topics.push('浣庣珵浜夊垏鍙?);
        return topics.slice(0, 5);
    }

    function _setAffinityBar(row, width, label) {
        var span = row.querySelector('span');
        var bar = row.querySelector('i');
        if (span) span.textContent = label;
        if (bar) bar.style.width = width + '%';
    }

    function _loadAiGenerationPage(config) {
        Promise.all([
            api.providers.list().catch(function () { return []; }),
            api.ai.usageToday().catch(function () { return []; }),
        ]).then(function (results) {
            _hydrateAiSelects(results[0] || []);
            _updateAiUsageHint(results[1] || []);
        });

        (config.triggerSelectors || []).forEach(function (selector) {
            _rewireElements(selector, function (btn) {
                btn.addEventListener('click', function () {
                    var inputEl = document.querySelector(config.inputSelector);
                    var input = inputEl ? String(inputEl.value || '').trim() : '';
                    _runAiGeneration(config, input, btn, null);
                });
            });
        });

        _rewireElements('#mainHost .page-header .secondary-button', function (btn) {
            btn.addEventListener('click', function () {
                var text = _collectAiResultText(config);
                if (!text) {
                    showToast('褰撳墠娌℃湁鍙鍒跺唴瀹?, 'warning');
                    return;
                }
                if (api.utils && typeof api.utils.copyToClipboard === 'function') {
                    api.utils.copyToClipboard(text).then(function () {
                        showToast('缁撴灉宸插鍒?, 'success');
                    }).catch(function () {
                        showToast('澶嶅埗澶辫触锛岃閲嶈瘯', 'error');
                    });
                    return;
                }
                showToast('澶嶅埗鑳藉姏涓嶅彲鐢?, 'warning');
            });
        });

        _rewireElements('#mainHost .variant-card', function (card) {
            card.addEventListener('click', function () {
                document.querySelectorAll('#mainHost .variant-card').forEach(function (item) {
                    item.classList.remove('is-best');
                });
                card.classList.add('is-best');
                var text = extractTextFromEl(card, 'p');
                var target = document.querySelector(config.inputSelector);
                if (target && text) target.value = text;
                showToast('宸插簲鐢ㄨ鐗堟湰鍒扮紪杈戝尯', 'success');
            });
        });

        _rewireElements('#mainHost .js-ai-regen', function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var card = btn.closest('.variant-card');
                var seed = card ? extractTextFromEl(card, 'p') : '';
                _runAiGeneration(config, seed, btn, { diversify: true });
            });
        });

        _rewireElements('#mainHost .js-ai-apply-next', function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var card = btn.closest('.variant-card');
                var text = card ? extractTextFromEl(card, 'p') : '';
                if (!text) {
                    showToast('褰撳墠鐗堟湰鍐呭涓虹┖', 'warning');
                    return;
                }
                _applyAiResultToDownstream(config, text);
            });
        });

        if (typeof config.bindExtra === 'function') config.bindExtra();
    }

    function _runAiGeneration(config, input, btn, options) {
        var source = String(input || '').trim();
        if (!source) {
            showToast('璇峰厛濉啓鐢熸垚鍐呭', 'warning');
            return;
        }
        var originalText = btn.textContent;
        btn.disabled = true;
        btn.textContent = (options && options.diversify) ? '閲嶇畻涓€? : (config.actionText || '澶勭悊涓€?);
        var prompt = config.beforeCall ? config.beforeCall(source) : source;
        if (options && options.diversify) {
            prompt += '\n璇峰熀浜庡悓涓€涓婚杈撳嚭鍏ㄦ柊瑙掑害锛岄伩鍏嶅鐢ㄥ凡鏈夊彞寮忋€?;
        }
        api.ai.chat({
            preset: config.preset,
            model: _selectedModel(),
            messages: [{ role: 'user', content: prompt }],
            temperature: 0.7,
            max_tokens: 1200,
        }).then(function (result) {
            if (config.renderResult) config.renderResult(result || {}, source);
            showToast((options && options.diversify) ? '宸茬敓鎴愬悓涓婚鏂扮増鏈? : '宸茬敓鎴愭渶鏂扮粨鏋?, 'success');
            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (err) {
            showToast('鐢熸垚澶辫触: ' + err.message, 'error');
        }).finally(function () {
            btn.disabled = false;
            btn.textContent = originalText;
        });
    }

    function _applyAiResultToDownstream(config, text) {
        var map = {
            'viral-title': { route: 'creative-workshop', title: '鏍囬鏂规涓嬪彂', task_type: 'report' },
            'product-title': { route: 'creative-workshop', title: '鍟嗗搧鏍囬涓嬪彂', task_type: 'report' },
            'ai-copywriter': { route: 'ai-content-factory', title: '钀ラ攢鏂囨涓嬪彂', task_type: 'publish' },
            'script-extractor': { route: 'video-editor', title: '鑴氭湰缁撴瀯涓嬪彂', task_type: 'publish' },
        };
        var target = map[config.routeKey] || { route: 'creative-workshop', title: 'AI 缁撴灉涓嬪彂', task_type: 'report' };
        var payload = {
            sourceRoute: config.routeKey,
            targetRoute: target.route,
            text: text,
            createdAt: new Date().toISOString(),
        };
        window.localStorage.setItem('tkops.ai.handoff', JSON.stringify(payload));
        api.tasks.create({
            title: target.title,
            task_type: target.task_type,
            priority: 'high',
            status: 'pending',
            result_summary: text.slice(0, 160),
        }).catch(function () { return null; }).finally(function () {
            if (typeof renderRoute === 'function') renderRoute(target.route);
            showToast('宸蹭笅鍙戝埌 ' + target.route + '锛屽彲缁х画澶勭悊', 'success');
        });
    }

    function _collectAiResultText(config) {
        var selected = document.querySelector('#mainHost .variant-card.is-best p');
        if (selected && selected.textContent.trim()) return selected.textContent.trim();
        var first = document.querySelector('#mainHost .variant-card p');
        if (first && first.textContent.trim()) return first.textContent.trim();
        var inputEl = document.querySelector(config.inputSelector);
        if (inputEl && String(inputEl.value || '').trim()) return String(inputEl.value || '').trim();
        return '';
    }

    function _rewireElements(selector, binder) {
        document.querySelectorAll(selector).forEach(function (node) {
            var clone = node.cloneNode(true);
            node.parentNode.replaceChild(clone, node);
            binder(clone);
        });
    }

    function _hydrateAiSelects(providers) {
        var list = providers || [];
        var active = list.find(function (provider) {
            return provider.is_active === true || provider.is_active === 'True';
        }) || list[0] || null;
        var providerNames = list.map(function (provider) { return provider.name || '鏈懡鍚嶄緵搴斿晢'; });
        var models = [];
        list.forEach(function (provider) {
            if (provider.default_model && models.indexOf(provider.default_model) === -1) {
                models.push(provider.default_model);
            }
        });
        if (!models.length && active && active.default_model) models.push(active.default_model);
        if (!models.length) models = ['GPT-4o'];

        document.querySelectorAll('#mainHost select, #detailHost select').forEach(function (select) {
            var label = _fieldLabel(select);
            if (label.indexOf('渚涘簲鍟?) !== -1) {
                select.innerHTML = providerNames.length
                    ? providerNames.map(function (name) {
                        return '<option' + (active && active.name === name ? ' selected' : '') + '>' + _esc(name) + '</option>';
                    }).join('')
                    : '<option selected>鏈厤缃緵搴斿晢</option>';
            }
            if (label.indexOf('妯″瀷') !== -1) {
                select.innerHTML = models.map(function (name, index) {
                    return '<option' + (index === 0 ? ' selected' : '') + '>' + _esc(name) + '</option>';
                }).join('');
            }
        });
    }

    function _updateAiUsageHint(rows) {
        var totalTokens = 0;
        (rows || []).forEach(function (row) {
            totalTokens += parseInt(row.total_tokens || row.total || 0, 10) || 0;
        });
        var detailItems = document.querySelectorAll('#detailHost .detail-item strong');
        if (detailItems.length >= 1 && totalTokens > 0) {
            detailItems[0].textContent = detailItems[0].textContent + ' / 浠婃棩 tokens ' + totalTokens;
        }
    }

    function _renderVariantList(selector, items, labels) {
        var host = document.querySelector(selector);
        if (!host) return;
        var toneList = ['success', 'info', 'warning'];
        var list = (items || []).filter(Boolean);
        if (!list.length) list = ['鏆傛棤鍙睍绀虹粨鏋?];
        host.innerHTML = list.map(function (item, index) {
            var tag = Array.isArray(labels)
                ? (labels[index] || ('Variant ' + (index + 1)))
                : ((labels || 'Variant') + ' ' + String.fromCharCode(65 + index));
            return '<article class="variant-card' + (index === 0 ? ' is-best' : '') + '">' 
                + '<div class="variant-card__head"><span class="pill ' + toneList[index % toneList.length] + '">' + _esc(tag) + '</span><strong>' + (index === 0 ? '鎺ㄨ崘閲囩敤' : '鍊欓€夌増鏈?) + '</strong></div>'
                + '<p>' + _esc(item) + '</p>'
                + '<div class="detail-actions"><button class="ghost-button js-ai-regen" type="button">鍚屼富棰橀噸绠?/button><button class="secondary-button js-ai-apply-next" type="button">涓嬪彂鍒颁笅娓?/button></div>'
                + '<small>' + (index === 0 ? '褰撳墠缁撴灉宸叉寜鏈€鏂拌緭鍏ュ埛鏂般€? : '鍙敤浜庤ˉ鍏呮祴璇曚笌娓犻亾鍒嗗彂銆?) + '</small></article>';
        }).join('');
    }

    function _renderCompliance(selector, text) {
        var root = document.querySelector(selector);
        if (!root) return;
        var scoreCard = root.querySelector('.copy-score-card strong');
        var scoreNote = root.querySelector('.copy-score-card small');
        var riskStrong = root.querySelectorAll('.metric-kv .detail-item strong');
        var flagged = _detectRiskWords(text);
        var score = Math.max(48, 94 - flagged.length * 14);
        if (scoreCard) scoreCard.textContent = score;
        if (scoreNote) scoreNote.textContent = score >= 85 ? '浣庨闄? : score >= 70 ? '涓瓑椋庨櫓' : '楂橀闄?;
        if (riskStrong.length >= 2) {
            riskStrong[0].textContent = flagged.length;
            riskStrong[1].textContent = Math.max(0, Math.min(3, flagged.length + 1));
        }
        var list = root.querySelector('.workbench-side-list');
        if (list) {
            list.innerHTML = (flagged.length ? flagged : ['褰撳墠杈撳嚭鏈彂鐜版槑鏄鹃珮椋庨櫓璇?]).map(function (word) {
                return '<article class="workbench-sidecard"><strong>' + _esc(word === '褰撳墠杈撳嚭鏈彂鐜版槑鏄鹃珮椋庨櫓璇? ? word : ('椋庨櫓璇嶏細' + word)) + '</strong><div class="subtle">'
                    + (word === '褰撳墠杈撳嚭鏈彂鐜版槑鏄鹃珮椋庨櫓璇? ? '寤鸿缁х画浜哄伐澶嶆牳鍒╃泭鎵胯鍜岀粷瀵瑰寲琛ㄨ揪銆? : '寤鸿鏇挎崲涓烘洿绋冲Ε鐨勪腑鎬ц〃杈撅紝鍐嶈繘鍏ユ姇鏀俱€?)
                    + '</div></article>';
            }).join('');
        }
    }

    function _renderExtractorResult(text) {
        var host = document.querySelector('#mainHost .extractor-result-table');
        if (!host) return;
        var rows = _extractAiItems(text, 6);
        host.innerHTML = rows.map(function (row, index) {
            var match = row.match(/(\d{2}:\d{2}:\d{2})/);
            var ts = match ? match[1] : ('00:00:' + String(12 + index * 8).padStart(2, '0'));
            var cleaned = row.replace(/(\d{2}:\d{2}:\d{2})/, '').replace(/^[-*鈥d\.\)\s]+/, '').trim();
            return '<div class="extractor-result-row"><span>' + _esc(ts) + '</span><div><strong>' + (cleaned.indexOf('CTA') !== -1 ? '[CTA]' : cleaned.indexOf('闀滃ご') !== -1 ? '[瑙嗚鎻忚堪]' : '[鑴氭湰缁撴瀯]') + '</strong><p>' + _esc(cleaned) + '</p></div><em>' + (96 - index * 2) + '%</em></div>';
        }).join('');
    }

    function _extractAiItems(text, limit) {
        var cleaned = String(text || '')
            .split(/\n+/)
            .map(function (line) { return line.replace(/^[-*鈥d\.\)\s]+/, '').trim(); })
            .filter(function (line) { return line && line.length >= 6; });
        if (!cleaned.length) return [String(text || '').trim()];
        return cleaned.slice(0, limit || 3);
    }

    function _selectedModel() {
        var modelSelect = null;
        document.querySelectorAll('#mainHost select, #detailHost select').forEach(function (select) {
            if (!modelSelect && _fieldLabel(select).indexOf('妯″瀷') !== -1) modelSelect = select;
        });
        return modelSelect ? modelSelect.value : null;
    }

    function _fieldLabel(node) {
        var field = node.closest('.form-field, .config-field');
        var label = field ? field.querySelector('label, .config-field__label') : null;
        return label ? label.textContent.trim() : '';
    }

    function _calcTitleScore(text) {
        var value = String(text || '');
        var score = 6.8;
        if (value.indexOf('!') !== -1 || value.indexOf('锛?) !== -1) score += 0.6;
        if (/\d/.test(value)) score += 0.8;
        if (value.length >= 16 && value.length <= 28) score += 1.1;
        if (/涓轰粈涔坾鍙湁|鍒啀|绔嬪嵆|鎻|蹇呯湅/.test(value)) score += 0.5;
        return Math.min(9.8, Math.round(score * 10) / 10);
    }

    function _keywordChunks(text) {
        var parts = String(text || '').split(/[\s\-_/銆愩€慭[\]锛?銆俔+/).filter(Boolean);
        if (parts.length >= 3) return parts.slice(0, 3);
        return [String(text || '').slice(0, 4), String(text || '').slice(4, 8), String(text || '').slice(8, 12)].filter(Boolean);
    }

    function _keywordDensity(text, token) {
        if (!text || !token) return '0.0';
        var total = String(text).length || 1;
        var count = String(text).split(token).length - 1;
        return ((count * token.length / total) * 100).toFixed(1);
    }

    function _detectRiskWords(text) {
        var source = String(text || '');
        var patterns = ['鏈€寮?, '绗竴', '绋宠禋', '璧氶挶', '100%', '缁濆', '姘镐箙', '鍖呰繃'];
        return patterns.filter(function (word) { return source.indexOf(word) !== -1; });
    }

    function _formatElapsed(ms) {
        var n = parseInt(ms || 0, 10) || 0;
        if (n < 1000) return n + 'ms';
        return (n / 1000).toFixed(1) + 's';
    }

    function _updateAssetStats(assets, stats) {
        var cards = document.querySelectorAll('#mainHost .stat-grid .stat-card');
        var total = stats.total || assets.length;
        var byType = stats.byType || {};
        var reviewCount = (byType.text || 0) + (byType.template || 0);
        var reusable = total ? Math.round(((byType.video || 0) + (byType.image || 0)) / total * 100) : 0;
        if (cards.length >= 3) {
            cards[0].querySelector('.stat-card__value').textContent = _formatNum(total);
            cards[0].querySelector('.stat-card__delta .subtle').textContent = '鐪熷疄绱犳潗搴撳瓨鎬婚噺';
            cards[1].querySelector('.stat-card__value').textContent = reviewCount;
            cards[1].querySelector('.stat-card__delta .subtle').textContent = '鏂囨湰/妯℃澘绱犳潗寰呮暣鐞?;
            cards[2].querySelector('.stat-card__value').textContent = reusable + '%';
            cards[2].querySelector('.stat-card__delta .subtle').textContent = '鍥剧墖涓庤棰戠礌鏉愬崰姣?;
        }
    }

    function _renderAssetCategories(byType, total) {
        var labels = {
            all: '鍏ㄩ儴绱犳潗',
            video: '鐭棰戝彛鎾?,
            image: '灏侀潰鍥剧墖',
            audio: '闊抽 / 閰嶄箰',
            text: '瀛楀箷 / 鏂囨',
            template: '妯℃澘 / 宸ョ▼',
        };
        var order = ['all', 'video', 'image', 'audio', 'text', 'template'];
        var list = document.querySelector('#mainHost .asset-category-list');
        if (!list) return;
        list.innerHTML = order.map(function (key, index) {
            var count = key === 'all' ? total : (byType[key] || 0);
            return '<button class="asset-category-item' + (index === 0 ? ' is-active' : '') + '" data-asset-type="' + key + '"><strong>' + labels[key] + '</strong><span>' + count + '</span></button>';
        }).join('');
    }

    function _buildAssetThumb(asset, isSelected) {
        var type = (asset.asset_type || 'image').toLowerCase();
        var previewClass = type === 'video'
            ? 'source-thumb__preview--video'
            : type === 'audio'
                ? 'source-thumb__preview--audio'
                : type === 'text'
                    ? 'source-thumb__preview--subtitle'
                    : 'source-thumb__preview--image';
        var label = type === 'audio' ? '鈾? : type === 'video' ? '瑙嗛' : type === 'text' ? '鏂囩' : type === 'template' ? '妯℃澘' : '鍥剧墖';
        var tags = _assetTags(asset);
        return '<article class="source-thumb' + (isSelected ? ' is-selected' : '') + '" data-id="' + (asset.id || '') + '">'
            + '<div class="source-thumb__preview ' + previewClass + '">' + _esc(label) + (type === 'video' ? '<span class="source-thumb__dur">' + _humanFileSize(asset.file_size || 0) + '</span>' : '') + '</div>'
            + '<div class="source-thumb__name">' + _esc(asset.filename || '鏈懡鍚嶇礌鏉?) + '</div>'
            + '<div class="source-thumb__tag">' + tags.map(function (tag) { return '<span class="pill ' + tag.tone + '">' + _esc(tag.text) + '</span>'; }).join('') + '</div></article>';
    }

    function _assetTags(asset) {
        var type = (asset.asset_type || 'image').toLowerCase();
        var primaryTone = type === 'video' ? 'success' : type === 'audio' ? 'warning' : 'info';
        var tags = [{ text: type, tone: primaryTone }];
        if (asset.tags) {
            String(asset.tags).split(/[,锛宂/).slice(0, 1).forEach(function (tag) {
                if (tag.trim()) tags.push({ text: tag.trim(), tone: 'info' });
            });
        } else {
            tags.push({ text: '宸插叆搴?, tone: 'success' });
        }
        return tags;
    }

    function _bindAssetThumbs(assets) {
        document.querySelectorAll('#mainHost .source-thumb').forEach(function (thumb) {
            thumb.addEventListener('click', function () {
                document.querySelectorAll('#mainHost .source-thumb').forEach(function (item) {
                    item.classList.remove('is-selected');
                });
                thumb.classList.add('is-selected');
                var id = parseInt(thumb.dataset.id, 10);
                var asset = (assets || []).find(function (item) { return item.id === id || String(item.id) === String(id); });
                _renderAssetDetail(asset);
            });
        });
        _bindAssetActions(assets);
    }

    function _bindAssetActions(assets) {
        var actionHost = document.querySelector('#detailHost .workbench-side-list');
        if (!actionHost) return;
        var selectedThumb = document.querySelector('#mainHost .source-thumb.is-selected');
        if (!selectedThumb) return;
        var selectedId = parseInt(selectedThumb.dataset.id, 10);
        var asset = (assets || []).find(function (item) { return item.id === selectedId || String(item.id) === String(selectedId); });
        if (!asset) return;
        actionHost.innerHTML = '<article class="workbench-sidecard"><strong>绱犳潗鎿嶄綔</strong><div class="subtle"><button class="secondary-button js-edit-asset" data-id="' + _esc(asset.id || '') + '">缂栬緫绱犳潗</button> <button class="danger-button js-delete-asset" data-id="' + _esc(asset.id || '') + '">鍒犻櫎绱犳潗</button></div></article>';
        document.querySelectorAll('.js-edit-asset').forEach(function (btn) {
            btn.addEventListener('click', function () {
                openAssetForm(asset);
            });
        });
        document.querySelectorAll('.js-delete-asset').forEach(function (btn) {
            btn.addEventListener('click', function () {
                confirmModal({
                    title: '鍒犻櫎绱犳潗',
                    message: '纭畾鍒犻櫎璇ョ礌鏉愯褰曪紵姝ゆ搷浣滀笉鍙仮澶嶃€?,
                    confirmText: '鍒犻櫎',
                    tone: 'danger',
                }).then(function (ok) {
                    if (!ok) return;
                    api.assets.remove(asset.id).then(function () {
                        showToast('绱犳潗宸插垹闄?, 'success');
                        loaders['asset-center']();
                    });
                });
            });
        });
    }

    function _renderAssetDetail(asset) {
        if (!asset) return;
        var preview = document.querySelector('#detailHost .source-mini-preview');
        if (preview) {
            preview.innerHTML = '<div class="source-thumb__preview ' + ((asset.asset_type || '').toLowerCase() === 'video' ? 'source-thumb__preview--video' : (asset.asset_type || '').toLowerCase() === 'audio' ? 'source-thumb__preview--audio' : 'source-thumb__preview--image') + '">' + _esc((asset.asset_type || 'image').toUpperCase()) + '</div>'
                + '<div><strong>' + _esc(asset.filename || '鏈懡鍚嶇礌鏉?) + '</strong><div class="subtle">' + _esc(asset.file_path || '鏈褰曡矾寰?) + '</div></div>';
        }
        var items = document.querySelectorAll('#detailHost .detail-item strong');
        if (items.length >= 3) {
            items[0].textContent = (asset.asset_type || 'unknown') + ' / ' + _humanFileSize(asset.file_size || 0);
            items[1].textContent = asset.tags ? String(asset.tags) : '宸插叆搴?;
            items[2].textContent = asset.created_at || '-';
        }
    }

    function _humanFileSize(size) {
        var n = parseInt(size || 0, 10) || 0;
        if (n < 1024) return n + ' B';
        if (n < 1024 * 1024) return (n / 1024).toFixed(1) + ' KB';
        return (n / (1024 * 1024)).toFixed(1) + ' MB';
    }

    function _materializeSettingsControls(settings, theme) {
        document.querySelectorAll('#mainHost .config-field').forEach(function (field) {
            var labelNode = field.querySelector('.config-field__label');
            var control = field.querySelector('.config-field__control');
            if (!labelNode || !control) return;
            var label = labelNode.textContent.replace('*', '').trim();
            var meta = _settingsFieldMeta(label, settings, theme);
            if (!meta) return;
            if (meta.type === 'toggle') {
                control.innerHTML = '<label class="config-toggle ' + (meta.value ? 'is-on' : '') + '"><input type="checkbox" data-setting-key="' + _esc(meta.key) + '" ' + (meta.value ? 'checked' : '') + '><span class="config-toggle__track"></span><span class="config-toggle__label">' + (meta.value ? '寮€' : '鍏?) + '</span></label>';
                var checkbox = control.querySelector('input[type="checkbox"]');
                if (checkbox) {
                    checkbox.addEventListener('change', function () {
                        var toggle = checkbox.closest('.config-toggle');
                        if (toggle) toggle.classList.toggle('is-on', checkbox.checked);
                        var text = control.querySelector('.config-toggle__label');
                        if (text) text.textContent = checkbox.checked ? '寮€' : '鍏?;
                    });
                }
                return;
            }
            if (meta.type === 'select') {
                control.innerHTML = '<select class="config-native-select" data-setting-key="' + _esc(meta.key) + '">' + meta.options.map(function (option) {
                    return '<option' + (String(option) === String(meta.value) ? ' selected' : '') + '>' + _esc(option) + '</option>';
                }).join('') + '</select>';
                return;
            }
            control.innerHTML = '<input class="config-native-input" data-setting-key="' + _esc(meta.key) + '" value="' + _esc(meta.value || '') + '">';
        });
    }

    function _updateSettingsSummary(settings, theme, version) {
        var detailItems = document.querySelectorAll('#detailHost .detail-item strong');
        if (detailItems.length >= 3) {
            detailItems[0].textContent = '绯荤粺璁剧疆 / v' + (version.version || '-');
            detailItems[1].textContent = _countSettingsDrafts() + ' 椤瑰緟淇濆瓨';
            detailItems[2].textContent = settings.last_saved_at || '灏氭湭璁板綍';
        }
        var statusCards = document.querySelectorAll('#statusRight .status-chip, .status-meta .status-chip');
        if (statusCards.length) {
            statusCards[0].textContent = theme === 'dark' ? '娣辫壊涓婚' : '娴呰壊涓婚';
        }
        var sidebar = document.querySelector('#sidebarSummaryCopy, .sidebar-summary p');
        if (sidebar) {
            sidebar.textContent = '褰撳墠涓婚 ' + (theme === 'dark' ? '娣辫壊' : '娴呰壊') + '锛屽凡鎺ュ叆鐪熷疄閰嶇疆璇诲啓銆?;
        }
    }

    function _bindSystemSettingsActions(settings, theme) {
        _rewireElements('#mainHost .page-header .primary-button', function (btn) {
            btn.addEventListener('click', function () {
                _saveSystemSettings(btn, settings, theme);
            });
        });
        _rewireElements('#mainHost .page-header .secondary-button', function (btn) {
            btn.addEventListener('click', function () {
                var defaults = _recommendedSettings();
                _applySettingsToControls(defaults);
                showToast('宸叉仮澶嶆帹鑽愰厤缃紝鐐瑰嚮淇濆瓨鍚庣敓鏁?, 'info');
            });
        });
        document.querySelectorAll('#mainHost .config-nav-item').forEach(function (item, index) {
            item.addEventListener('click', function () {
                document.querySelectorAll('#mainHost .config-nav-item').forEach(function (node) { node.classList.remove('is-selected'); });
                item.classList.add('is-selected');
                document.querySelectorAll('#mainHost .config-form-group').forEach(function (group, groupIndex) {
                    group.style.display = groupIndex === index || index >= 4 ? '' : (groupIndex === index ? '' : 'none');
                });
            });
        });
    }

    function _saveSystemSettings(button, oldSettings, oldTheme) {
        var values = _collectSettingsValues();
        var promises = [];
        Object.keys(values).forEach(function (key) {
            if (key === 'theme') return;
            promises.push(api.settings.set(key, String(values[key])));
        });
        if (values.theme && values.theme !== oldTheme) {
            promises.push(api.theme.set(values.theme));
        }
        var originalText = button.textContent;
        button.disabled = true;
        button.textContent = '淇濆瓨涓€?;
        Promise.all(promises).then(function () {
            var now = _nowStamp();
            return api.settings.set('last_saved_at', now).then(function () { return now; });
        }).then(function (now) {
            showToast('绯荤粺璁剧疆宸蹭繚瀛?, 'success');
            var detailItems = document.querySelectorAll('#detailHost .detail-item strong');
            if (detailItems.length >= 3) {
                detailItems[1].textContent = '0 椤瑰緟淇濆瓨';
                detailItems[2].textContent = now;
            }
            applyTheme(values.theme || oldTheme);
        }).catch(function (err) {
            showToast('淇濆瓨璁剧疆澶辫触: ' + err.message, 'error');
        }).finally(function () {
            button.disabled = false;
            button.textContent = originalText;
        });
    }

    function _collectSettingsValues() {
        var data = {};
        document.querySelectorAll('#mainHost [data-setting-key]').forEach(function (control) {
            var key = control.dataset.settingKey;
            if (!key) return;
            if (control.type === 'checkbox') {
                data[key] = control.checked ? '1' : '0';
            } else {
                data[key] = control.value;
            }
        });
        return data;
    }

    function _applySettingsToControls(values) {
        document.querySelectorAll('#mainHost [data-setting-key]').forEach(function (control) {
            var key = control.dataset.settingKey;
            if (!(key in values)) return;
            if (control.type === 'checkbox') {
                control.checked = values[key] === '1' || values[key] === true;
                var toggle = control.closest('.config-toggle');
                if (toggle) toggle.classList.toggle('is-on', control.checked);
                var label = toggle ? toggle.querySelector('.config-toggle__label') : null;
                if (label) label.textContent = control.checked ? '寮€' : '鍏?;
            } else {
                control.value = values[key];
            }
        });
    }

    function _settingsFieldMeta(label, settings, theme) {
        var mapping = {
            '鐣岄潰璇█': { key: 'ui.language', type: 'select', value: settings['ui.language'] || '绠€浣撲腑鏂?, options: ['绠€浣撲腑鏂?, 'English'] },
            '鏃跺尯': { key: 'ui.timezone', type: 'select', value: settings['ui.timezone'] || 'UTC+8 (浜氭床/涓婃捣)', options: ['UTC+8 (浜氭床/涓婃捣)', 'UTC+0 (UTC)', 'UTC-5 (America/New_York)'] },
            '榛樿璐у竵': { key: 'business.currency', type: 'select', value: settings['business.currency'] || 'USD ($)', options: ['USD ($)', 'CNY (楼)', 'EUR (鈧?'] },
            '鍚姩鏃惰嚜鍔ㄦ鏌ユ洿鏂?: { key: 'update.auto_check', type: 'toggle', value: (settings['update.auto_check'] || '1') !== '0' },
            '涓婚': { key: 'theme', type: 'select', value: theme === 'dark' ? 'dark' : 'light', options: ['light', 'dark'] },
            '瀛楀彿': { key: 'ui.font_size', type: 'select', value: settings['ui.font_size'] || '鏍囧噯 (14px)', options: ['绱у噾 (13px)', '鏍囧噯 (14px)', '鑸掗€?(16px)'] },
            '绱у噾妯″紡': { key: 'ui.compact_mode', type: 'toggle', value: settings['ui.compact_mode'] === '1' },
            '浠ｇ悊鍦板潃': { key: 'network.proxy', type: 'input', value: settings['network.proxy'] || '' },
            '璇锋眰瓒呮椂': { key: 'network.timeout_sec', type: 'select', value: settings['network.timeout_sec'] || '30 绉?, options: ['15 绉?, '30 绉?, '60 绉?] },
            '鏈€澶у苟鍙?: { key: 'network.max_concurrency', type: 'select', value: settings['network.max_concurrency'] || '5', options: ['3', '5', '8', '10'] },
            '浠诲姟瀹屾垚閫氱煡': { key: 'notify.task_done', type: 'toggle', value: (settings['notify.task_done'] || '1') !== '0' },
            '寮傚父鍛婅': { key: 'notify.error_alert', type: 'toggle', value: (settings['notify.error_alert'] || '1') !== '0' },
            '闈欓粯鏃舵': { key: 'notify.quiet_hours', type: 'select', value: settings['notify.quiet_hours'] || '22:00 - 08:00', options: ['鍏抽棴', '22:00 - 08:00', '00:00 - 07:00'] },
        };
        return mapping[label] || null;
    }

    function _recommendedSettings() {
        return {
            'ui.language': '绠€浣撲腑鏂?,
            'ui.timezone': 'UTC+8 (浜氭床/涓婃捣)',
            'business.currency': 'USD ($)',
            'update.auto_check': '1',
            theme: 'light',
            'ui.font_size': '鏍囧噯 (14px)',
            'ui.compact_mode': '0',
            'network.proxy': '',
            'network.timeout_sec': '30 绉?,
            'network.max_concurrency': '5',
            'notify.task_done': '1',
            'notify.error_alert': '1',
            'notify.quiet_hours': '22:00 - 08:00',
        };
    }

    function _countSettingsDrafts() {
        var count = 0;
        document.querySelectorAll('#mainHost [data-setting-key]').forEach(function () {
            count += 1;
        });
        return count;
    }

    function _formatMoney(num) {
        var n = parseInt(num || 0, 10) || 0;
        if (n >= 10000) return (n / 10000).toFixed(1) + '涓?;
        return _formatNum(n);
    }

    function _safePercent(part, whole) {
        var numerator = parseInt(part || 0, 10) || 0;
        var denominator = parseInt(whole || 0, 10) || 0;
        if (!denominator) return '0%';
        return Math.max(0, Math.min(100, Math.round((numerator / denominator) * 100))) + '%';
    }

    function _buildTruthfulProfitRows(summary, conversion) {
        var regions = ((summary.accounts && summary.accounts.by_region) || {});
        var keys = Object.keys(regions);
        if (!keys.length) {
            return ['<tr><td colspan="5" style="text-align:center;padding:32px;">鏆傛棤鍒╂鼎鍒嗘瀽鍩虹鏁版嵁</td></tr>'];
        }
        var counts = (conversion && conversion.counts) || {};
        return keys.slice(0, 4).map(function (regionKey, index) {
            var accountCount = regions[regionKey] || 0;
            var completed = counts.completed_tasks || 0;
            var assets = counts.assets || 0;
            var statusClass = accountCount >= 2 ? 'success' : accountCount === 1 ? 'warning' : 'error';
            var readiness = assets >= completed ? '绱犳潗宸茶鐩? : '绱犳潗寰呰ˉ榻?;
            var action = accountCount >= 2 ? '缁х画楠岃瘉' : '浼樺厛琛ユ牱鏈?;
            return '<tr class="route-row" data-search="' + _esc(regionKey + ' ' + readiness + ' ' + action) + '"><td><strong>' + _esc(regionKey) + '</strong></td><td><span class="status-chip ' + statusClass + '">' + _formatNum(completed) + '</span></td><td>' + _formatNum(accountCount) + '</td><td>' + readiness + '</td><td>' + action + '</td></tr>';
        });
    }

    function _nowStamp() {
        var now = new Date();
        var month = String(now.getMonth() + 1).padStart(2, '0');
        var day = String(now.getDate()).padStart(2, '0');
        var hours = String(now.getHours()).padStart(2, '0');
        var minutes = String(now.getMinutes()).padStart(2, '0');
        return now.getFullYear() + '-' + month + '-' + day + ' ' + hours + ':' + minutes;
    }

    /* 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲
       鍏叡宸ュ叿
       鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲 */
    function _esc(str) {
        var d = document.createElement('div');
        d.textContent = str;
        return d.innerHTML;
    }

    function _formatNum(n) {
        return (n || 0).toLocaleString();
    }

    function _wireHeaderPrimary(handler, label) {
        var btn = document.querySelector('#mainHost .header-actions .primary-button');
        if (!btn) return;
        if (label) btn.textContent = label;
        var clone = btn.cloneNode(true);
        btn.parentNode.replaceChild(clone, btn);
        clone.addEventListener('click', handler);
    }

    /* 鈹€鈹€ 鎵归噺閫夋嫨 鈹€鈹€ */
    function _bindBatchBar(checkboxSelector, onBatchDelete) {
        var _bar = null;
        function _getCheckedIds() {
            var ids = [];
            document.querySelectorAll(checkboxSelector + ':checked').forEach(function (cb) {
                ids.push(parseInt(cb.dataset.id, 10));
            });
            return ids;
        }
        function _syncBar() {
            var ids = _getCheckedIds();
            if (ids.length === 0) {
                if (_bar) { _bar.remove(); _bar = null; }
                return;
            }
            if (!_bar) {
                _bar = document.createElement('div');
                _bar.className = 'batch-bar';
                _bar.innerHTML = '<span class="batch-bar__count"></span>'
                    + '<button class="danger-button js-batch-delete-btn">鎵归噺鍒犻櫎</button>'
                    + '<button class="ghost-button js-batch-cancel-btn">鍙栨秷閫夋嫨</button>';
                document.body.appendChild(_bar);
                _bar.querySelector('.js-batch-delete-btn').addEventListener('click', function () {
                    var ids2 = _getCheckedIds();
                    if (ids2.length === 0) return;
                    onBatchDelete(ids2);
                });
                _bar.querySelector('.js-batch-cancel-btn').addEventListener('click', function () {
                    document.querySelectorAll(checkboxSelector).forEach(function (cb) { cb.checked = false; });
                    _syncBar();
                });
            }
            _bar.querySelector('.batch-bar__count').textContent = '宸查€?' + ids.length + ' 椤?;
        }
        document.querySelectorAll(checkboxSelector).forEach(function (cb) {
            cb.addEventListener('change', _syncBar);
        });
    }

    function _batchDelete(ids, removeFn, entityName, loaderKey) {
        confirmModal({
            title: '鎵归噺鍒犻櫎' + entityName,
            message: '纭畾鍒犻櫎閫変腑鐨?' + ids.length + ' 涓? + entityName + '锛熸鎿嶄綔涓嶅彲鎭㈠銆?,
            confirmText: '鍏ㄩ儴鍒犻櫎',
            tone: 'danger',
        }).then(function (ok) {
            if (!ok) return;
            var promises = ids.map(function (id) { return removeFn(id); });
            Promise.all(promises).then(function () {
                showToast(ids.length + ' 涓? + entityName + '宸插垹闄?);
                if (loaders[loaderKey]) loaders[loaderKey]();
            }).catch(function (err) {
                showToast('閮ㄥ垎鍒犻櫎澶辫触: ' + err.message, 'error');
                if (loaders[loaderKey]) loaders[loaderKey]();
            });
        });
    }

    /* 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲
       Version Upgrade 椤甸潰
       鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲 */
    loaders['version-upgrade'] = function () {
        var _pollTimer = null;
        var _updateInfo = null;

        // DOM refs
        var elCurrent     = document.getElementById('verCurrent');
        var elLatest      = document.getElementById('verLatest');
        var elDelta       = document.getElementById('verDelta');
        var elStatus      = document.getElementById('verStatus');
        var elStatusNote  = document.getElementById('verStatusNote');
        var elBody        = document.getElementById('updateBody');
        var elSubtitle    = document.getElementById('updateSubtitle');
        var elActions     = document.getElementById('updateActions');
        var elDlWrap      = document.getElementById('downloadProgressWrap');
        var elDlFill      = document.getElementById('downloadFill');
        var elDlPercent   = document.getElementById('downloadPercent');
        var elDlSpeed     = document.getElementById('downloadSpeed');
        var elDlSize      = document.getElementById('downloadSize');
        var btnCheck      = document.getElementById('btnCheckUpdate');
        var btnDownload   = document.getElementById('btnDownload');
        var btnApply      = document.getElementById('btnApply');
        var btnRelease    = document.getElementById('btnReleasePage');
        var elEnvInfo     = document.getElementById('envInfo');

        // Show current version immediately
        api.version.current().then(function (d) {
            if (elCurrent) elCurrent.textContent = 'v' + (d.version || '鈥?);
            var detailCurrent = document.getElementById('detailVerCurrent');
            if (detailCurrent) detailCurrent.textContent = 'v' + (d.version || '鈥?);
            if (elEnvInfo) {
                elEnvInfo.innerHTML =
                    '<div class="detail-item"><span class="subtle">搴旂敤鐗堟湰</span><strong>v' + d.version + '</strong></div>' +
                    '<div class="detail-item"><span class="subtle">骞冲彴</span><strong>Windows</strong></div>' +
                    '<div class="detail-item"><span class="subtle">杩愯妯″紡</span><strong>Desktop</strong></div>';
            }
        });

        // Wire check button
        if (btnCheck) {
            var clone = btnCheck.cloneNode(true);
            btnCheck.parentNode.replaceChild(clone, btnCheck);
            btnCheck = clone;
            btnCheck.addEventListener('click', doCheck);
        }
        if (btnDownload) btnDownload.addEventListener('click', doDownload);
        if (btnApply) btnApply.addEventListener('click', doApply);

        function doCheck() {
            if (elStatus) elStatus.textContent = '妫€鏌ヤ腑鈥?;
            if (elDelta) elDelta.innerHTML = '<span>姝ｅ湪妫€鏌モ€?/span>';
            btnCheck.disabled = true;
            btnCheck.textContent = '妫€鏌ヤ腑鈥?;

            api.version.check().then(function (info) {
                _updateInfo = info;
                btnCheck.disabled = false;
                btnCheck.textContent = '妫€鏌ユ洿鏂?;

                if (elLatest) elLatest.textContent = info.hasUpdate ? 'v' + info.latest : 'v' + info.current;

                if (info.hasUpdate) {
                    if (elDelta) elDelta.innerHTML = '<span style="color:var(--status-warning);">鏈夋柊鐗堟湰鍙敤</span>';
                    if (elStatus) elStatus.textContent = '鍙洿鏂?;
                    var detailStatus = document.getElementById('detailVerStatus');
                    if (detailStatus) detailStatus.textContent = '鍙洿鏂?;
                    if (elStatusNote) elStatusNote.innerHTML = '<span style="color:var(--status-warning);">' + info.latest + ' 鍙敤</span>';
                    if (elSubtitle) elSubtitle.textContent = info.tag + ' 鏇存柊鏃ュ織';

                    // Render release notes (simple markdown鈫扝TML)
                    if (elBody) {
                        var notes = (info.releaseNotes || '鏆傛棤鏇存柊璇存槑').replace(/</g, '&lt;').replace(/>/g, '&gt;');
                        notes = notes.replace(/^### (.+)$/gm, '<h3>$1</h3>');
                        notes = notes.replace(/^## (.+)$/gm, '<h2>$1</h2>');
                        notes = notes.replace(/^# (.+)$/gm, '<h1>$1</h1>');
                        notes = notes.replace(/^\- (.+)$/gm, '<li>$1</li>');
                        notes = notes.replace(/`([^`]+)`/g, '<code>$1</code>');
                        notes = notes.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
                        notes = notes.replace(/\n/g, '<br>');
                        elBody.innerHTML = notes;
                    }

                    // Show actions
                    if (elActions) elActions.style.display = '';
                    if (info.downloadUrl && btnDownload) {
                        btnDownload.style.display = '';
                        var sizeStr = info.assetSize ? ' (' + _humanSize(info.assetSize) + ')' : '';
                        btnDownload.textContent = '涓嬭浇鏇存柊' + sizeStr;
                    }
                    if (info.htmlUrl && btnRelease) {
                        btnRelease.style.display = '';
                        btnRelease.href = info.htmlUrl;
                    }
                } else {
                    if (elDelta) elDelta.innerHTML = '<span style="color:var(--status-success);">宸叉槸鏈€鏂?/span>';
                    if (elStatus) elStatus.textContent = '宸叉槸鏈€鏂?;
                    var detailStatus2 = document.getElementById('detailVerStatus');
                    if (detailStatus2) detailStatus2.textContent = '宸叉槸鏈€鏂?;
                    if (elStatusNote) elStatusNote.innerHTML = '<span style="color:var(--status-success);">鏃犻渶鏇存柊</span>';
                    if (elBody) elBody.innerHTML = '<div class="update-placeholder"><span class="shell-icon">鉁?/span><p>褰撳墠宸叉槸鏈€鏂扮増鏈紝鏃犻渶鏇存柊銆?/p></div>';
                }
            }).catch(function (err) {
                btnCheck.disabled = false;
                btnCheck.textContent = '妫€鏌ユ洿鏂?;
                if (elStatus) elStatus.textContent = '妫€鏌ュけ璐?;
                var detailStatus3 = document.getElementById('detailVerStatus');
                if (detailStatus3) detailStatus3.textContent = '妫€鏌ュけ璐?;
                if (elDelta) elDelta.innerHTML = '<span style="color:var(--status-error);">妫€鏌ュけ璐?/span>';
                if (typeof showToast === 'function') showToast('鏇存柊妫€鏌ュけ璐? ' + err.message, 'error');
            });
        }

        function doDownload() {
            if (!_updateInfo || !_updateInfo.downloadUrl) return;
            btnDownload.disabled = true;
            btnDownload.textContent = '鍑嗗涓嬭浇鈥?;
            if (elDlWrap) elDlWrap.style.display = '';
            if (elStatus) elStatus.textContent = '涓嬭浇涓?;

            api.version.download(_updateInfo.downloadUrl).then(function () {
                _pollTimer = setInterval(pollProgress, 500);
            }).catch(function (err) {
                btnDownload.disabled = false;
                btnDownload.textContent = '閲嶈瘯涓嬭浇';
                if (typeof showToast === 'function') showToast('涓嬭浇鍚姩澶辫触: ' + err.message, 'error');
            });
        }

        function pollProgress() {
            api.version.progress().then(function (p) {
                if (elDlFill) elDlFill.style.width = p.percent + '%';
                if (elDlPercent) elDlPercent.textContent = p.percent + '%';
                if (elDlSpeed) elDlSpeed.textContent = p.speed || '';
                if (elDlSize) elDlSize.textContent = p.downloadedHuman + ' / ' + p.totalHuman;

                if (p.state === 'done') {
                    clearInterval(_pollTimer);
                    _pollTimer = null;
                    btnDownload.style.display = 'none';
                    if (btnApply) btnApply.style.display = '';
                    if (elStatus) elStatus.textContent = '涓嬭浇瀹屾垚';
                    if (elStatusNote) elStatusNote.innerHTML = '<span style="color:var(--status-success);">鍑嗗瀹夎</span>';
                    if (typeof showToast === 'function') showToast('涓嬭浇瀹屾垚锛屽彲浠ュ畨瑁呮洿鏂?);
                } else if (p.state === 'verifying') {
                    if (elDlPercent) elDlPercent.textContent = '鏍￠獙涓€?;
                } else if (p.state === 'error') {
                    clearInterval(_pollTimer);
                    _pollTimer = null;
                    btnDownload.disabled = false;
                    btnDownload.textContent = '閲嶈瘯涓嬭浇';
                    if (elStatus) elStatus.textContent = '涓嬭浇澶辫触';
                    if (typeof showToast === 'function') showToast('涓嬭浇澶辫触: ' + p.error, 'error');
                }
            });
        }

        function doApply() {
            if (typeof showConfirm === 'function') {
                showConfirm({
                    title: '瀹夎鏇存柊',
                    message: '灏嗗惎鍔ㄥ畨瑁呯▼搴忓苟鍏抽棴褰撳墠搴旂敤锛岀‘璁ょ户缁紵',
                    confirmText: '瀹夎骞堕噸鍚?,
                    tone: 'warning',
                }).then(function (ok) {
                    if (!ok) return;
                    _applyNow();
                });
            } else {
                _applyNow();
            }
        }

        function _applyNow() {
            api.version.apply().then(function (r) {
                if (typeof showToast === 'function') showToast('瀹夎绋嬪簭宸插惎鍔紝搴旂敤鍗冲皢鍏抽棴鈥?);
                setTimeout(function () { window.close(); }, 2000);
            }).catch(function (err) {
                if (typeof showToast === 'function') showToast('瀹夎澶辫触: ' + err.message, 'error');
            });
        }

        function _humanSize(n) {
            var units = ['B', 'KB', 'MB', 'GB'];
            for (var i = 0; i < units.length; i++) {
                if (Math.abs(n) < 1024) return n.toFixed(1) + ' ' + units[i];
                n /= 1024;
            }
            return n.toFixed(1) + ' TB';
        }
    };

    /* 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲
       缁熶竴璋冨害鍏ュ彛
       鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲 */
    function loadRouteData(routeKey) {
        var loader = loaders[routeKey];
        if (typeof loader === 'function') {
            loader();
        }
    }

    // 鈹€鈹€ dataChanged 浜嬩欢 鈫?鑷姩鍒锋柊褰撳墠椤?鈹€鈹€
    document.addEventListener('data:changed', function () {
        if (typeof currentRoute !== 'undefined' && loaders[currentRoute]) {
            loaders[currentRoute]();
        }
    });

    // 鈹€鈹€ 鏆撮湶鍏ㄥ眬 鈹€鈹€
    window.loadRouteData = loadRouteData;
    window._pageLoaders = loaders;
    window.__pageAudits = pageAudits;
    window.__runtimeSummaryHandlers = runtimeSummaryHandlers;
})();
