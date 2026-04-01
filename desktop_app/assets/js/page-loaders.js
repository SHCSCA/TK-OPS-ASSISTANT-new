/* ── page-loaders.js ─ 页面级数据加载器 ───────────────
   每个路由渲染完静态模板后，对应的 loader 拉取真实数据
   并注入 DOM。由 loadRouteData(routeKey) 统一调度。
   ──────────────────────────────────────────────── */
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
                eyebrow: '今日重点',
                title: '系统实时运行摘要',
                copy: '账号 ' + (stats.accounts ? stats.accounts.total || 0 : 0)
                    + ' / 任务 ' + (stats.tasks ? stats.tasks.total || 0 : 0)
                    + ' / 设备 ' + (stats.devices ? stats.devices.total || 0 : 0)
                    + ' / 供应商 ' + (stats.providers || 0)
                    + ' / 素材 ' + (stats.assets || 0),
                statusLeft: [
                    '账号 ' + (accountStatuses.active || 0) + ' 活跃 / ' + ((stats.accounts && stats.accounts.total) || 0) + ' 总量',
                    '任务运行中 ' + (taskStatuses.running || 0) + ' / 排队 ' + (taskStatuses.pending || 0),
                    '设备健康 ' + (deviceStatuses.healthy || 0) + ' / 异常 ' + (deviceStatuses.error || 0),
                ],
                statusRight: [
                    { text: (taskStatuses.failed || 0) > 0 ? ('任务异常 ' + (taskStatuses.failed || 0)) : '任务稳定', tone: (taskStatuses.failed || 0) > 0 ? 'error' : 'success' },
                    { text: (stats.providers || 0) > 0 ? ('已接入供应商 ' + (stats.providers || 0)) : '未配置供应商', tone: (stats.providers || 0) > 0 ? 'info' : 'warning' },
                ],
            });
        },
        'account': function (payload) {
            payload = payload || {};
            var accounts = payload.accounts || [];
            var counts = { total: accounts.length, online: 0, offline: 0, error: 0 };
            accounts.forEach(function (a) {
                var s = (a.status || '').toLowerCase();
                if (s === 'online' || s === '在线' || s === 'active') counts.online++;
                else if (s === 'offline' || s === '离线' || s === 'idle') counts.offline++;
                else if (s === 'error' || s === 'warning' || s === '异常' || s === 'suspended' || s === 'warming') counts.error++;
            });
            _applyRuntimeSummary({
                eyebrow: '当前提醒',
                title: counts.error > 0 ? (counts.error + ' 个异常账号待处理') : '账号状态稳定',
                copy: '在线 ' + counts.online + ' / 离线 ' + counts.offline + ' / 异常 ' + counts.error + ' / 总量 ' + counts.total,
                statusLeft: [
                    '账号总量 ' + counts.total,
                    '在线账号 ' + counts.online,
                    '异常账号 ' + counts.error,
                ],
                statusRight: [
                    { text: counts.online > 0 ? ('在线 ' + counts.online) : '暂无在线账号', tone: counts.online > 0 ? 'success' : 'warning' },
                    { text: counts.error > 0 ? ('异常 ' + counts.error) : '无异常', tone: counts.error > 0 ? 'error' : 'info' },
                ],
            });
        },
        'group-management': function (payload) {
            payload = payload || {};
            var groups = payload.groups || [];
            var described = groups.filter(function (g) { return !!(g.description || '').trim(); }).length;
            var colored = groups.filter(function (g) { return !!(g.color || '').trim(); }).length;
            _applyRuntimeSummary({
                eyebrow: '组织提醒',
                title: groups.length ? ('分组结构已加载 ' + groups.length + ' 项') : '暂无分组结构',
                copy: '已描述 ' + described + ' / 已配色 ' + colored + ' / 总量 ' + groups.length,
                statusLeft: ['分组总量 ' + groups.length, '已描述分组 ' + described, '已配色分组 ' + colored],
                statusRight: [
                    { text: groups.length ? '分组已接线' : '等待创建分组', tone: groups.length ? 'success' : 'warning' },
                    { text: '实时汇总', tone: 'info' },
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
                eyebrow: '环境提醒',
                title: error > 0 ? (error + ' 台异常设备待处理') : '设备环境状态稳定',
                copy: '健康 ' + healthy + ' / 告警 ' + warning + ' / 异常 ' + error + ' / 总量 ' + devices.length,
                statusLeft: ['设备总量 ' + devices.length, '健康覆盖率 ' + rate + '%', '异常设备 ' + error],
                statusRight: [
                    { text: error > 0 ? ('异常 ' + error) : '环境正常', tone: error > 0 ? 'error' : 'success' },
                    { text: warning > 0 ? ('告警 ' + warning) : '无告警', tone: warning > 0 ? 'warning' : 'info' },
                ],
            });
        },
        'ai-provider': function (payload) {
            payload = payload || {};
            var providers = payload.providers || [];
            var active = providers.filter(function (p) { return p.is_active === true || p.is_active === 'True'; });
            var primary = active[0] || providers[0] || null;
            _applyRuntimeSummary({
                eyebrow: '配置建议',
                title: providers.length ? ('已接入 ' + providers.length + ' 个供应商') : '尚未配置供应商',
                copy: primary ? ('当前默认模型 ' + (primary.default_model || '-') + ' / 供应商 ' + (primary.name || '-')) : '请先添加供应商并完成连接测试。',
                statusLeft: ['供应商总量 ' + providers.length, '启用供应商 ' + active.length, '默认模型 ' + (primary ? (primary.default_model || '-') : '-')],
                statusRight: [
                    { text: active.length ? ('启用中 ' + active.length) : '未启用', tone: active.length ? 'success' : 'warning' },
                    { text: primary ? (primary.name || '已配置') : '等待加载', tone: primary ? 'info' : 'warning' },
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
                eyebrow: '队列摘要',
                title: tasks.length ? ('运行中 ' + counts.running + ' 条，排队 ' + counts.pending + ' 条') : '暂无任务队列数据',
                copy: '已完成 ' + counts.completed + ' / 异常 ' + counts.failed + ' / 总量 ' + counts.total,
                statusLeft: ['任务总量 ' + counts.total, '运行中任务 ' + counts.running, '排队任务 ' + counts.pending],
                statusRight: [
                    { text: counts.completed ? ('已完成 ' + counts.completed) : '待完成任务', tone: counts.completed ? 'success' : 'info' },
                    { text: counts.failed ? ('需重试 ' + counts.failed) : '无异常', tone: counts.failed ? 'error' : 'info' },
                ],
            });
        },
        'asset-center': function (payload) {
            payload = payload || {};
            var assets = payload.assets || [];
            var stats = payload.stats || { total: assets.length, byType: {} };
            var total = stats.total || assets.length;
            var unboundCount = assets.filter(function (asset) { return !String((asset && asset.account_id) || '').trim(); }).length;
            var taggedCount = assets.filter(function (asset) {
                var tags = String((asset && asset.tags) || '').split(/[，,、/\s]+/).filter(Boolean);
                return tags.length > 0;
            }).length;
            var taggedRate = total ? Math.round((taggedCount / total) * 100) : 0;
            _applyRuntimeSummary({
                eyebrow: '素材提醒',
                title: total ? ('素材库存 ' + total + ' 项') : '暂无素材库存',
                copy: '未绑定账号 ' + unboundCount + ' / 标签完善率 ' + taggedRate + '%',
                statusLeft: ['素材总量 ' + total, '未绑定账号 ' + unboundCount, '标签完善率 ' + taggedRate + '%'],
                statusRight: [
                    { text: total ? '库存已加载' : '等待上传素材', tone: total ? 'success' : 'warning' },
                    { text: taggedCount ? ('已打标签 ' + taggedCount) : '暂无标签', tone: taggedCount ? 'info' : 'warning' },
                ],
            });
        },
        'visual-lab': function (payload) {
            payload = payload || {};
            var projects = payload.projects || [];
            var views = payload.views || [];
            var summary = payload.summary || {};
            var providerCount = (summary.providers && summary.providers.total) || 0;
            _applyRuntimeSummary({
                eyebrow: '实验提醒',
                title: projects.length ? ('实验项目 ' + projects.length + ' 个已接入') : '暂无实验项目',
                copy: '实验视图 ' + views.length + ' / 供应商 ' + providerCount + ' / 素材 ' + ((summary.assets && summary.assets.total) || 0),
                statusLeft: ['实验项目 ' + projects.length, '实验视图 ' + views.length, '素材总量 ' + ((summary.assets && summary.assets.total) || 0)],
                statusRight: [
                    { text: projects.length ? '持久化已接入' : '等待创建项目', tone: projects.length ? 'success' : 'warning' },
                    { text: providerCount ? ('模型池 ' + providerCount) : '等待模型配置', tone: providerCount ? 'info' : 'warning' },
                ],
            });
        },
        'profit-analysis': function (payload) {
            payload = payload || {};
            var summary = payload.summary || {};
            var conversion = payload.conversion || {};
            var counts = conversion.counts || {};
            var activeAccounts = (summary.accounts && summary.accounts.active) || 0;
            var totalAccounts = (summary.accounts && summary.accounts.total) || 0;
            var assetsTotal = (summary.assets && summary.assets.total) || 0;
            var completedTasks = counts.completed_tasks || (summary.tasks && summary.tasks.completed) || 0;
            var failedTasks = (summary.tasks && summary.tasks.failed) || 0;
            _applyRuntimeSummary({
                eyebrow: '经营提醒',
                title: totalAccounts ? ('活跃账号 ' + activeAccounts + ' / 完成任务 ' + completedTasks) : '暂无利润页基础样本',
                copy: '失败任务 ' + failedTasks + ' / 素材支撑 ' + assetsTotal + ' / 该页只展示当前系统可支撑的运营准备度。',
                statusLeft: ['账号样本 ' + totalAccounts, '完成任务 ' + completedTasks, '失败任务 ' + failedTasks],
                statusRight: [
                    { text: assetsTotal ? ('素材 ' + assetsTotal) : '素材待补齐', tone: assetsTotal ? 'success' : 'warning' },
                    { text: failedTasks ? ('需排查 ' + failedTasks) : '无异常', tone: failedTasks ? 'error' : 'info' },
                ],
            });
        },
        'report-center': function (payload) {
            payload = payload || {};
            var reports = payload.reports || [];
            var activity = payload.activity || [];
            var pending = reports.filter(function (report) {
                return String(report.status || '').toLowerCase() !== 'completed';
            }).length;
            _applyRuntimeSummary({
                eyebrow: '报表提醒',
                title: reports.length ? ('报告记录 ' + reports.length + ' 份') : '暂无报表记录',
                copy: '待处理 ' + pending + ' / 活动日志 ' + activity.length + ' / 预览内容由真实记录回填。',
                statusLeft: ['报告记录 ' + reports.length, '待处理 ' + pending, '活动日志 ' + activity.length],
                statusRight: [
                    { text: reports.length ? '报表已接线' : '等待生成报表', tone: reports.length ? 'success' : 'warning' },
                    { text: pending ? ('待跟进 ' + pending) : '状态稳定', tone: pending ? 'warning' : 'info' },
                ],
            });
        },
        'creative-workshop': function (payload) {
            payload = payload || {};
            var projects = payload.projects || [];
            var tasks = payload.tasks || [];
            var assets = payload.assets || [];
            var failed = tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'failed'; }).length;
            _applyRuntimeSummary({
                eyebrow: '创意提醒',
                title: projects.length ? ('创意实验 ' + projects.length + ' 个已接入') : '暂无创意实验项目',
                copy: '素材 ' + assets.length + ' / 任务 ' + tasks.length + ' / 该页优先展示真实实验、素材和任务反馈。',
                statusLeft: ['实验项目 ' + projects.length, '素材样本 ' + assets.length, '任务反馈 ' + tasks.length],
                statusRight: [
                    { text: assets.length ? ('素材充足 ' + assets.length) : '素材待补齐', tone: assets.length ? 'success' : 'warning' },
                    { text: failed ? ('待排查 ' + failed) : '无阻塞', tone: failed ? 'error' : 'info' },
                ],
            });
        },
        'viral-title': function (payload) {
            payload = payload || {};
            var providers = payload.providers || [];
            var active = providers.filter(function (p) { return p.is_active === true || p.is_active === 'True'; });
            var total = providers.length;
            _applyRuntimeSummary({
                eyebrow: '标题提醒',
                title: total ? ('已接入 ' + total + ' 个供应商') : '尚未配置供应商',
                copy: 'AI 生成标题依赖供应商配置，生成结果存于当前会话。',
                statusLeft: ['供应商 ' + total, '启用中 ' + active.length, '标题生成就绪'],
                statusRight: [
                    { text: total ? '已配置' : '等待接入', tone: total ? 'success' : 'warning' },
                    { text: '等待生成', tone: 'info' },
                ],
            });
        },
        'script-extractor': function (payload) {
            payload = payload || {};
            var providers = payload.providers || [];
            var total = providers.length;
            _applyRuntimeSummary({
                eyebrow: '提取提醒',
                title: total ? ('已接入 ' + total + ' 个供应商') : '尚未配置供应商',
                copy: '视频 URL 输入后点击「开始提取」，结构结果实时输出到右侧面板。',
                statusLeft: ['供应商 ' + total, '分析模式 混合', '等待输入视频'],
                statusRight: [
                    { text: total ? '已配置' : '等待接入', tone: total ? 'success' : 'warning' },
                    { text: '等待提取', tone: 'info' },
                ],
            });
        },
        'product-title': function (payload) {
            payload = payload || {};
            var providers = payload.providers || [];
            var active = providers.filter(function (p) { return p.is_active === true || p.is_active === 'True'; });
            var total = providers.length;
            _applyRuntimeSummary({
                eyebrow: '优化提醒',
                title: total ? ('已接入 ' + total + ' 个供应商') : '尚未配置供应商',
                copy: '输入商品名称后点击「立即优化」，生成兼顾 SEO 和点击率的标题方案。',
                statusLeft: ['供应商 ' + total, '启用中 ' + active.length, 'SEO 优化就绪'],
                statusRight: [
                    { text: total ? '已配置' : '等待接入', tone: total ? 'success' : 'warning' },
                    { text: '等待优化', tone: 'info' },
                ],
            });
        },
        'ai-copywriter': function (payload) {
            payload = payload || {};
            var providers = payload.providers || [];
            var total = providers.length;
            _applyRuntimeSummary({
                eyebrow: '文案提醒',
                title: total ? ('已接入 ' + total + ' 个供应商') : '尚未配置供应商',
                copy: '选择风格、填写产品信息后点击「立即生成」，右侧合规区实时显示风险评估。',
                statusLeft: ['供应商 ' + total, '合规自检 就绪', '多版本输出'],
                statusRight: [
                    { text: total ? '已配置' : '等待接入', tone: total ? 'success' : 'warning' },
                    { text: '等待生成', tone: 'info' },
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
        'visual-lab': {
            dataSources: ['getAnalyticsSummary', 'listExperimentProjects', 'listExperimentViews'],
            interactions: ['create', 'detail', 'compare', 'persist'],
        },
        'profit-analysis': {
            dataSources: ['getAnalyticsSummary', 'getConversionAnalysis'],
            interactions: ['detail', 'filter', 'export'],
        },
        'report-center': {
            dataSources: ['listReportRuns', 'getAnalyticsSummary', 'listActivityLogs'],
            interactions: ['create', 'detail', 'preview', 'export'],
        },
        'creative-workshop': {
            dataSources: ['listAccounts', 'listAssets', 'listTasks', 'listExperimentProjects'],
            interactions: ['persist', 'compare', 'detail', 'handoff'],
        },
        'viral-title': {
            dataSources: ['listProviders', 'getAiUsageToday'],
            interactions: ['generate', 'compare', 'select', 'copy'],
        },
        'script-extractor': {
            dataSources: ['listProviders', 'getAiUsageToday'],
            interactions: ['input', 'extract', 'preview', 'export'],
        },
        'product-title': {
            dataSources: ['listProviders', 'getAiUsageToday'],
            interactions: ['input', 'optimize', 'compare', 'select'],
        },
        'ai-copywriter': {
            dataSources: ['listProviders', 'getAiUsageToday'],
            interactions: ['configure', 'generate', 'evaluate', 'select'],
        },
    };

    function _applyRuntimeSummary(summary) {
        if (!summary) return;
        if (typeof setShellRouteSummary === 'function') {
            setShellRouteSummary({
                eyebrow: summary.eyebrow || '',
                title: summary.title || '',
                copy: summary.copy || '',
                statusLeft: Array.isArray(summary.statusLeft) ? summary.statusLeft.slice() : [],
                statusRight: Array.isArray(summary.statusRight) ? summary.statusRight.slice() : [],
            });
            return;
        }
    }

    /* ══════════════════════════════════════════════
       Account 页面
       ══════════════════════════════════════════════ */
    // Account 主渲染与交互已拆分至 page-loaders/account-main.js。

    function _buildAccountViewModel(account, device) {
        var tags = _splitAccountTags(account.tags);
        var cookieMeta = _accountCookieMeta(account.cookie_status);
        var loginCheckMeta = _accountLoginCheckMeta(account.last_login_check_status, account.last_login_check_message, account.last_login_check_at);
        var lastConnectionMeta = _accountConnectionMeta(account.last_connection_status, account.last_connection_message, account.last_connection_checked_at);
        return {
            id: account.id,
            username: account.username || '',
            platform: account.platform || '',
            platformLabel: _accountPlatformLabel(account.platform),
            region: account.region || '',
            regionLabel: _accountRegionLabel(account.region),
            status: account.status || '',
            statusLabel: _accountStatusLabel(account.status),
            statusTone: _accountStatusTone(account.status),
            filterStatus: _accountFilterStatus(account.status),
            sortOrder: _accountSortOrder(account.status),
            followers: parseInt(account.followers || 0, 10) || 0,
            notes: account.notes || '',
            created_at: account.created_at || '',
            device_id: account.device_id || null,
            device: device,
            tags: tags,
            cookieStatus: cookieMeta.value,
            cookieLabel: cookieMeta.label,
            cookieTone: cookieMeta.tone,
            cookieContentRaw: account.cookie_content || '',
            cookieContentSummary: _accountCookieContentSummary(account.cookie_content),
            cookieUpdatedAt: account.cookie_updated_at || '',
            cookieUpdatedLabel: _formatRelativeDate(account.cookie_updated_at),
            loginCheckStatus: loginCheckMeta.value,
            loginCheckStatusRaw: account.last_login_check_status || 'unknown',
            loginCheckLabel: loginCheckMeta.label,
            loginCheckTone: loginCheckMeta.tone,
            loginCheckMessage: loginCheckMeta.message,
            loginCheckAt: account.last_login_check_at || '',
            loginCheckCheckedLabel: _formatRelativeDate(account.last_login_check_at),
            isolationEnabled: _isTruthy(account.isolation_enabled),
            isolationLabel: _isTruthy(account.isolation_enabled) ? '已启用' : '未启用',
            isolationTone: _isTruthy(account.isolation_enabled) ? 'success' : 'warning',
            lastLoginLabel: _formatRelativeDate(account.last_login_at),
            lastLoginAt: account.last_login_at || '',
            proxyLabel: _accountProxyLabel(device),
            subtitle: _accountRegionLabel(account.region) + ' · ' + _accountSummaryLine(account, tags),
            connectionLabel: lastConnectionMeta.label,
            connectionTone: lastConnectionMeta.tone,
            connectionMessage: lastConnectionMeta.message,
            connectionScopeLabel: _accountConnectionScopeLabel(device),
            lastConnectionStatus: account.last_connection_status || 'unknown',
            detailTarget: 'account-' + String(account.id || ''),
            searchText: _buildAccountSearchText(account, device, tags, cookieMeta, lastConnectionMeta),
            raw: account,
        };
    }

    function _renderAccountGrid(accounts) {
        var grid = document.querySelector('#mainHost .account-grid');
        if (!grid) return;
        if (!accounts.length) {
            grid.innerHTML = '<div class="empty-state" style="padding:48px;text-align:center;"><p>暂无账号数据</p><p class="subtle">点击右上角「新建账号」添加第一个账号</p></div>';
            return;
        }

        grid.innerHTML = accounts.map(function (a) {
            var tagMarkup = a.tags.slice(0, 3).map(function (tag) {
                return '<span class="pill info">' + _esc(tag) + '</span>';
            }).join('');
            return '<article class="account-card detail-trigger" data-id="' + (a.id || '') + '" data-detail-target="' + _esc(a.detailTarget) + '" data-status="' + _esc(_accountFilterStatus(a.status)) + '" data-order="' + _esc(_accountSortOrder(a.status)) + '" data-search="' + _esc(_buildAccountSearchText(a.raw, a.device, a.tags, { label: a.cookieLabel }, { label: a.connectionLabel })) + '">'
                + '<input type="checkbox" class="batch-check js-batch-account" data-id="' + (a.id || '') + '" aria-label="选择账号 ' + _esc(a.username || '') + '">'
                + '<div class="account-card__head"><div><strong>' + _esc(a.username || '') + '</strong><div class="subtle">' + _esc(a.subtitle || '') + '</div></div><span class="status-chip ' + a.statusTone + '">' + _esc(a.statusLabel) + '</span></div>'
                + '<div class="account-card__meta">'
                + '<div class="list-row"><span class="subtle">账号 ID</span><strong class="mono">' + (a.id || '-') + '</strong></div>'
                + '<div class="list-row"><span class="subtle">代理 IP</span><strong class="mono">' + _esc(a.proxyLabel) + '</strong></div>'
                + '<div class="list-row"><span class="subtle">上次登录</span><strong>' + _esc(a.lastLoginLabel) + '</strong></div>'
                + '<div class="list-row"><span class="subtle">Cookie 状态</span><span class="tag ' + a.cookieTone + '">' + _esc(a.cookieLabel) + '</span></div>'
                + '<div class="list-row"><span class="subtle">登录态校验</span><span class="tag ' + a.loginCheckTone + '">' + _esc(a.loginCheckLabel) + '</span></div>'
                + '<div class="list-row"><span class="subtle">标签</span><div class="account-card__tags">' + (tagMarkup || '<span class="subtle">未打标签</span>') + '</div></div>'
                + '</div>'
                + '<div class="detail-actions account-card__actions">'
                + '<button class="primary-button js-account-open-environment" data-id="' + (a.id || '') + '" type="button">进入环境</button>'
                + '<button class="secondary-button js-account-manage-cookies" data-id="' + (a.id || '') + '" type="button">Cookie 状态</button>'
                + '<button class="secondary-button js-account-rebind-validate" data-id="' + (a.id || '') + '" type="button">重绑并校验</button>'
                + '<button class="ghost-button js-view-account" data-id="' + (a.id || '') + '" type="button">查看详情与更多操作</button>'
                + '</div></article>';
        }).join('');
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

    function _renderEmptyAccountDetail() {
        var detailHost = document.getElementById('detailHost');
        var template = document.getElementById('route-account-detail-default');
        if (!detailHost || !template) return;
        detailHost.innerHTML = template.innerHTML;
    }

    function _findAccountViewModel(accounts, accountId) {
        return (accounts || []).find(function (item) {
            return String(item.id || '') === String(accountId || '');
        }) || null;
    }

    function _getAccountEnvironmentHelpers() {
        var helpers = window.__accountEnvironmentHelpers;
        if (helpers) return helpers;
        showToast('账号环境模块加载失败，请刷新应用后重试', 'error');
        throw new Error('account environment helpers not loaded');
    }

    function _openAccountEnvironment(account) {
        return _getAccountEnvironmentHelpers().openAccountEnvironment(account);
    }

    function _openAccountProxyConfig(account, options) {
        return _getAccountEnvironmentHelpers().openAccountProxyConfig(account, options);
    }

    function _openAccountCookieModal(account) {
        return _getAccountEnvironmentHelpers().openAccountCookieModal(account);
    }

    function _runAccountConnectionTest(accountId, button) {
        return _getAccountEnvironmentHelpers().runAccountConnectionTest(accountId, button);
    }

    function _runAccountLoginValidation(accountId, button, options) {
        return _getAccountEnvironmentHelpers().runAccountLoginValidation(accountId, button, options);
    }

    function _accountFilterStatus(status) {
        var s = (status || '').toLowerCase();
        if (s === 'active' || s === 'online' || s === '???') return 'online';
        if (s === 'warming' || s === 'warning' || s === '?????') return 'online';
        if (s === 'idle' || s === 'offline' || s === '???') return 'offline';
        return 'exception';
    }

    function _accountStatusLabel(status) {
        var s = (status || '').toLowerCase();
        if (s === 'active' || s === 'online') return '在线';
        if (s === 'idle' || s === 'offline') return '离线';
        if (s === 'warming' || s === 'warning') return '预热中';
        if (s === 'suspended' || s === 'error') return '异常';
        return status || '未知';
    }

    function _accountStatusTone(status) {
        if (!status) return 'info';
        var s = status.toLowerCase();
        if (s === 'online' || s === '在线' || s === 'active') return 'success';
        if (s === 'offline' || s === '离线' || s === 'idle') return 'info';
        if (s === 'warning' || s === '警告' || s === 'warming') return 'warning';
        return 'error';
    }

    function _accountSortOrder(status) {
        var s = (status || '').toLowerCase();
        if (s === 'error' || s === '异常' || s === 'suspended') return '1';
        if (s === 'warning' || s === 'warming') return '2';
        if (s === 'offline' || s === '离线' || s === 'idle') return '3';
        return '4';
    }

    function _accountPlatformLabel(platform) {
        var key = (platform || '').toLowerCase();
        if (key === 'tiktok_shop') return 'TikTok Shop';
        if (key === 'instagram') return 'Instagram';
        if (key === 'youtube') return 'YouTube';
        return 'TikTok';
    }

    function _accountRegionLabel(region) {
        var labels = {
            US: '美国区',
            UK: '英国区',
            DE: '德国区',
            SG: '新加坡区',
            MY: '马来区',
            JP: '日本区',
            ID: '印尼区',
            TH: '泰国区',
            VN: '越南区',
            PH: '菲律宾区',
            BR: '巴西区',
            MX: '墨西哥区',
        };
        return labels[String(region || '').toUpperCase()] || (region || '未知地区');
    }

    function _accountSummaryLine(account, tags) {
        if (tags && tags.length) return tags.slice(0, 2).join(' · ');
        if (account.notes) return String(account.notes).slice(0, 18);
        return '待补充运营标签';
    }

    function _accountProxyLabel(device) {
        if (!device || !device.proxy_ip) return '未配置代理';
        var region = device.region ? ' (' + _accountRegionLabel(device.region).replace('区', '') + ')' : '';
        return String(device.proxy_ip) + region;
    }

    function _accountCookieMeta(status) {
        var key = String(status || 'unknown').toLowerCase();
        if (key === 'valid') return { value: 'valid', label: '有效', tone: 'success' };
        if (key === 'expiring') return { value: 'expiring', label: '48 小时内过期', tone: 'warning' };
        if (key === 'invalid') return { value: 'invalid', label: '已失效', tone: 'error' };
        if (key === 'missing') return { value: 'missing', label: '缺失', tone: 'warning' };
        return { value: 'unknown', label: '待确认', tone: 'info' };
    }

    function _accountLoginCheckMeta(status, message, checkedAt) {
        var key = String(status || 'unknown').toLowerCase();
        if (key === 'valid') {
            return {
                value: 'valid',
                label: checkedAt ? ('已通过 / ' + _formatRelativeDate(checkedAt)) : '已通过',
                tone: 'success',
                message: message || '最近一次真实登录态校验通过',
            };
        }
        if (key === 'proxy_mismatch') {
            return {
                value: 'proxy_mismatch',
                label: checkedAt ? ('代理冲突 / ' + _formatRelativeDate(checkedAt)) : '代理冲突',
                tone: 'warning',
                message: _buildProxyMismatchGuidance(message, null),
            };
        }
        if (key === 'invalid') {
            return {
                value: 'invalid',
                label: checkedAt ? ('已失效 / ' + _formatRelativeDate(checkedAt)) : '已失效',
                tone: 'error',
                message: message || '最近一次真实登录态校验失败',
            };
        }
        if (checkedAt) {
            return {
                value: 'unknown',
                label: '未确认 / ' + _formatRelativeDate(checkedAt),
                tone: 'warning',
                message: message || '最近一次真实登录态校验未得到明确结论',
            };
        }
        return { value: 'unknown', label: '尚未校验', tone: 'info', message: message || '尚未执行真实登录态校验' };
    }

    function _accountCookieContentSummary(value) {
        var content = String(value || '').trim();
        if (!content) return '未录入';
        return '已录入 ' + _formatNum(content.length) + ' 字符';
    }

    function _accountConnectionMeta(status, message, checkedAt) {
        var key = String(status || 'unknown').toLowerCase();
        if (key === 'reachable') {
            return { label: '代理最近可达', tone: 'success', message: message || '最近一次代理检测通过' };
        }
        if (key === 'unreachable') {
            return {
                label: checkedAt ? ('代理检测失败 / ' + _formatRelativeDate(checkedAt)) : '代理检测失败',
                tone: 'error',
                message: message || '最近一次代理检测失败',
            };
        }
        return { label: '尚未检测', tone: 'info', message: message || '尚未执行代理检测' };
    }

    function _accountConnectionScopeLabel(device) {
        if (!device || !device.proxy_ip) return '当前仅支持检测已绑定代理的 TCP 可达性';
        return '仅检测绑定代理是否可达，不校验平台登录态';
    }

    function _splitAccountTags(value) {
        var seen = {};
        return String(value || '')
            .split(/[，,]/)
            .map(function (item) { return item.trim(); })
            .filter(function (item) {
                if (!item || seen[item]) return false;
                seen[item] = true;
                return true;
            });
    }

    function _mergeAccountTags(existing, incoming) {
        return _splitAccountTags((existing || []).concat(incoming || []).join(','))
            .join(', ');
    }

    function _buildAccountSearchText(account, device, tags, cookieMeta, connectionMeta) {
        return [
            account.username || '',
            account.platform || '',
            account.region || '',
            account.status || '',
            account.notes || '',
            account.tags || '',
            (tags || []).join(' '),
            device && device.proxy_ip ? device.proxy_ip : '',
            cookieMeta && cookieMeta.label ? cookieMeta.label : '',
            connectionMeta && connectionMeta.label ? connectionMeta.label : '',
            account.last_login_check_message || '',
            account.last_login_check_status || '',
        ].join(' ');
    }

    function _buildAccountAdvice(account) {
        var items = [];
        if (!account.isolationEnabled) {
            items.push({ title: '隔离环境尚未启用', copy: '建议先进入环境，切到独立浏览器后再继续操作。', badge: '优先处理', tone: 'warning' });
        }
        if (account.cookieStatus === 'invalid' || account.cookieStatus === 'missing') {
            items.push({ title: 'Cookie 状态需要处理', copy: '当前状态会直接影响登录和自动化执行，建议先在右侧面板更新 Cookie。', badge: account.cookieLabel, tone: account.cookieTone });
        } else if (account.cookieStatus === 'expiring') {
            items.push({ title: 'Cookie 即将过期', copy: '可以继续短时操作，但建议在下一个任务前完成续签，避免中途掉线。', badge: account.cookieLabel, tone: account.cookieTone });
        }
        if (account.loginCheckStatus === 'invalid') {
            items.push({ title: '真实登录态校验失败', copy: account.loginCheckMessage || '平台没有确认当前 Cookie 仍处于已登录状态，建议重新登录并重新导入 Cookie。', badge: '需重新登录', tone: 'error' });
        } else if (account.loginCheckStatus === 'proxy_mismatch') {
            items.push({ title: '代理下登录态校验异常', copy: _buildProxyMismatchGuidance(account.loginCheckMessage, account), badge: '代理冲突', tone: 'warning' });
        } else if (account.loginCheckStatus === 'unknown' && account.cookieContentRaw) {
            items.push({ title: '还没有做真实登录态校验', copy: '当前只有 Cookie 内容和过期时间推断，建议更新 Cookie 后立刻点“校验登录态”，确认平台接口还能识别账号。', badge: '建议补做', tone: 'warning' });
        } else if (account.loginCheckStatus === 'valid') {
            items.push({ title: '真实登录态最近已通过', copy: account.loginCheckMessage || '平台最近一次已确认当前 Cookie 仍可识别账号，可继续值班处理。', badge: '已验活', tone: 'success' });
        }
        if (!account.cookieContentRaw) {
            items.push({ title: '还没有录入 Cookie 内容', copy: '登录恢复扩展会在“进入环境”时自动加载，不需要手装。只有想把浏览器里的 Cookie 回填到系统时，才需要安装 Cookie-Editor 或 EditThisCookie：先登录账号，再导出当前站点 Cookie，最后回到“Cookie 状态”里粘贴。', badge: '新手指引', tone: 'info' });
        }
        if (account.lastConnectionStatus === 'unreachable') {
            items.push({ title: '最近一次代理检测失败', copy: account.connectionMessage || '请优先检查代理地址、网络和设备状态。', badge: '检测失败', tone: 'error' });
        } else if (account.lastConnectionStatus === 'reachable') {
            items.push({ title: '代理链路最近可达', copy: '代理线路最近一次检测通过，可继续做环境登录或后续人工验活。', badge: '代理正常', tone: 'success' });
        }
        if (!items.length) {
            items.push({ title: '当前账号可继续处理', copy: '隔离环境、Cookie 与连接检测暂无明显阻塞，可继续执行登录或批量任务。', badge: '已就绪', tone: 'success' });
        }
        items.push({ title: '粉丝与标签复核', copy: '当前粉丝 ' + _formatNum(account.followers) + '，标签为 ' + (account.tags.length ? account.tags.join(' / ') : '未配置') + '。', badge: '运营复核', tone: 'info' });
        return items.slice(0, 3);
    }

    function _buildProxyMismatchGuidance(message, account) {
        var lines = [];
        var platformMessage = String(message || '').trim();
        if (platformMessage) {
            lines.push('平台反馈：' + platformMessage);
        }
        lines.push('当前现象：直连能识别账号，但当前代理下无法稳定验活。');
        lines.push('优先处理：用当前绑定设备重新登录，并导出该设备环境下的新 Cookie。');
        lines.push('检查代理：地区尽量与账号地区一致，协议与认证方式正确，出口 IP 保持稳定。');
        if (account && account.regionLabel) {
            lines.push('当前账号地区：' + account.regionLabel + '。优先选择同地区设备，不要频繁跨区切换。');
        }
        lines.push('如果暂时没有与 Cookie 适配的代理：不要强绑新代理继续验活；先切回原登录设备，或暂时解绑代理做直连复核，再重新登录获取新 Cookie。');
        return lines.join('\n');
    }

    function _buildAccountDutySummary(account, items) {
        var risk = 0;
        var blockers = [];
        if (!account.isolationEnabled) {
            risk += 2;
            blockers.push('先进入隔离环境');
        }
        if (account.cookieStatus === 'invalid' || account.cookieStatus === 'missing') {
            risk += 3;
            blockers.push('Cookie 需要修复');
        } else if (account.cookieStatus === 'expiring') {
            risk += 1;
            blockers.push('Cookie 临近过期');
        }
        if (account.loginCheckStatus === 'invalid') {
            risk += 3;
            blockers.push('登录态校验失败');
        } else if (account.loginCheckStatus === 'proxy_mismatch') {
            risk += 2;
            blockers.push('代理下登录态异常');
        } else if (account.loginCheckStatus !== 'valid' && account.cookieContentRaw) {
            risk += 1;
            blockers.push('尚未做真实登录态校验');
        }
        if (account.lastConnectionStatus === 'unreachable') {
            risk += 3;
            blockers.push('代理检测失败');
        }
        if (account.filterStatus === 'exception') {
            risk += 2;
            blockers.push('账号处于异常状态');
        }
        if (risk >= 6) {
            return {
                title: '当前不建议直接值班操作',
                copy: blockers.join('，') + '。建议先排障，再继续登录、导入或发布。',
                badge: '高风险',
                tone: 'error',
            };
        }
        if (risk >= 3) {
            return {
                title: '建议先补齐环境条件',
                copy: blockers.join('，') + '。完成这些准备后再继续主流程更稳妥。',
                badge: '待处理',
                tone: 'warning',
            };
        }
        return {
            title: '当前账号可继续值班处理',
            copy: (items && items.length ? items[0].copy : '关键环境条件已满足，可继续进入账号操作流程。'),
            badge: '可执行',
            tone: 'success',
        };
    }

    function _formatRelativeDate(value) {
        if (!value) return '未记录';
        var normalized = String(value).replace(' ', 'T');
        var date = new Date(normalized);
        if (isNaN(date.getTime())) return String(value);
        var diff = Date.now() - date.getTime();
        var minute = 60 * 1000;
        var hour = 60 * minute;
        var day = 24 * hour;
        if (diff < minute) return '刚刚';
        if (diff < hour) return Math.max(1, Math.round(diff / minute)) + ' 分钟前';
        if (diff < day) return Math.max(1, Math.round(diff / hour)) + ' 小时前';
        return Math.max(1, Math.round(diff / day)) + ' 天前';
    }

    function _isTruthy(value) {
        if (value === true || value === false) return value;
        return ['1', 'true', 'yes', 'on', 'enabled'].indexOf(String(value || '').toLowerCase()) >= 0;
    }

    window.__pageLoaderShared = {
        // Shell and batch helpers consumed across split page modules.
        wireHeaderPrimary: _wireHeaderPrimary,
        bindBatchBar: _bindBatchBar,
        batchDelete: _batchDelete,

        // Account page view-model, search, and environment helpers.
        buildAccountViewModel: _buildAccountViewModel,
        buildAccountSearchText: _buildAccountSearchText,
        buildAccountAdvice: _buildAccountAdvice,
        buildAccountDutySummary: _buildAccountDutySummary,
        findAccountViewModel: _findAccountViewModel,
        splitAccountTags: _splitAccountTags,
        mergeAccountTags: _mergeAccountTags,
        accountFilterStatus: _accountFilterStatus,
        accountSortOrder: _accountSortOrder,
        openAccountEnvironment: _openAccountEnvironment,
        openAccountProxyConfig: _openAccountProxyConfig,
        openAccountCookieModal: _openAccountCookieModal,
        runAccountConnectionTest: _runAccountConnectionTest,
        runAccountLoginValidation: _runAccountLoginValidation,

        // Device page helpers retained in the root aggregator for now.
        buildDeviceViewModel: _buildDeviceViewModel,
        deviceBool: _deviceBool,
        safePercent: _safePercent,

        // Task operation helpers shared across task ops and workbench pages.
        normalizeTaskStatus: _normalizeTaskStatus,
        taskStatusLabel: _taskStatusLabel,
        taskStatusTone: _taskStatusTone,
        taskTypeLabel: _taskTypeLabel,
        taskTime: _taskTime,

        // Shared labels and formatting helpers.
        accountPlatformLabel: _accountPlatformLabel,
        accountRegionLabel: _accountRegionLabel,
        esc: _esc,
        formatNum: _formatNum,
        formatRelativeDate: _formatRelativeDate,
        isTruthy: _isTruthy,
    };

    /* ══════════════════════════════════════════════
       Dashboard 页面
       ══════════════════════════════════════════════ */
    loaders['dashboard'] = function () {
        _wireHeaderPrimary(function () { openTaskForm(); });
        _loadDashboardOverview(uiState.dashboard && uiState.dashboard.dashboardRange ? uiState.dashboard.dashboardRange : 'today');
    };

    function _loadDashboardOverview(rangeKey) {
        if (!uiState.dashboard) uiState.dashboard = { dashboardRange: 'today', selectedSystemKey: null };
        uiState.dashboard.dashboardRange = rangeKey || 'today';
        api.dashboard.overview(uiState.dashboard.dashboardRange).then(function (overview) {
            overview = overview || {};
            var trend = Array.isArray(overview.trend) ? overview.trend : [];
            if (!trend.length) {
                trend = _buildDashboardFallbackTrend(overview.stats || {}, uiState.dashboard.dashboardRange);
            }
            runtimeSummaryHandlers['dashboard']({ stats: overview.stats || {} });
            _renderDashboardStats(overview.stats || {});
            _renderDashboardTrend(trend, uiState.dashboard.dashboardRange, overview.stats || {});
            _renderDashboardActivity(overview.activity || []);
            _renderDashboardSystems(overview.systems || []);
            _syncDashboardRangeButtons(uiState.dashboard.dashboardRange);
        }).catch(function (e) {
            console.warn('[page-loaders] dashboard overview load failed:', e);
        });
    }

    function _buildDashboardFallbackTrend(stats, rangeKey) {
        var total = stats && stats.tasks ? (stats.tasks.total || 0) : 0;
        var byStatus = stats && stats.tasks && stats.tasks.byStatus ? stats.tasks.byStatus : {};
        var completed = byStatus.completed || 0;
        var failed = byStatus.failed || 0;
        var pending = byStatus.pending || 0;
        var running = byStatus.running || 0;
        var label = rangeKey === 'today' ? '当前' : '今日';
        return [{
            label: label,
            created: total,
            completed: completed + running,
            failed: failed + pending,
        }];
    }

    function _renderDashboardStats(stats) {
        var routeMap = {
            accounts: { route: 'account', toast: '正在打开账号管理' },
            tasks: { route: 'task-queue', toast: '正在打开任务队列' },
            failed: { route: 'task-queue', toast: '正在打开异常任务列表', filter: 'failed' },
            providers: { route: 'ai-provider', toast: '正在打开 AI 供应商配置' },
        };
        var statMap = {
            accounts: _formatNum(stats.accounts ? stats.accounts.total : 0),
            tasks: _formatNum(stats.tasks ? stats.tasks.total : 0),
            failed: _formatNum(stats.tasks && stats.tasks.byStatus ? (stats.tasks.byStatus.failed || 0) : 0),
            providers: _formatNum(stats.providers || 0),
        };
        Object.keys(statMap).forEach(function (key) {
            var card = document.querySelector('#mainHost [data-dashboard-stat="' + key + '"]');
            if (!card) return;
            var routeMeta = routeMap[key];
            if (routeMeta) {
                card.classList.add('dashboard-stat-link');
                if (routeMeta.filter) {
                    card.removeAttribute('data-route-link');
                    card.removeAttribute('data-route-toast');
                    card.dataset.dashboardTaskFilter = routeMeta.filter;
                    _bindDashboardTaskFilterTrigger(card, routeMeta.filter, routeMeta.toast);
                } else {
                    delete card.dataset.dashboardTaskFilter;
                    card.setAttribute('data-route-link', routeMeta.route);
                    card.setAttribute('data-route-toast', routeMeta.toast);
                    card.onclick = null;
                }
            }
            var node = card.querySelector('.stat-card__value');
            if (node) node.textContent = statMap[key];
        });
    }

    function _renderDashboardTrend(trend, rangeKey, stats) {
        var host = document.querySelector('#mainHost [data-dashboard-chart]');
        if (!host) return;
        var summary = _summarizeDashboardTrend(trend, rangeKey, stats);
        if (!summary) {
            host.innerHTML = '<div class="subtle">当前时间范围暂无趋势数据</div>';
            return;
        }
        var maxValue = Math.max(1, summary.created || 0, summary.completed || 0, summary.failed || 0);
        var rows = '<div class="dashboard-trend-group dashboard-trend-group--summary">'
            + '<div class="dashboard-trend-group__label">' + _esc(summary.label || '--') + '</div>'
            + '<div class="dashboard-trend-group__metrics">'
            + _renderDashboardTrendMetric('新增', 'created', summary.created || 0, maxValue)
            + _renderDashboardTrendMetric('完成', 'completed', summary.completed || 0, maxValue)
            + _renderDashboardTrendMetric('异常', 'failed', summary.failed || 0, maxValue)
            + '</div></div>';
        host.innerHTML = '<div class="dashboard-axis-note">当前展示的是所选时间范围内的汇总结果，不再按小时或日期拆分。</div>'
            + '<div class="dashboard-trend-chart dashboard-trend-chart--summary">' + rows + '</div>';
    }

    function _summarizeDashboardTrend(trend, rangeKey, stats) {
        var items = Array.isArray(trend) ? trend : [];
        if (!items.length) {
            var byStatus = stats && stats.tasks && stats.tasks.byStatus ? stats.tasks.byStatus : {};
            var total = stats && stats.tasks ? (stats.tasks.total || 0) : 0;
            if (!total && !(byStatus.completed || byStatus.failed || byStatus.pending || byStatus.running)) {
                return null;
            }
            return {
                label: _dashboardSummaryLabel(rangeKey),
                created: total,
                completed: (byStatus.completed || 0) + (byStatus.running || 0),
                failed: (byStatus.failed || 0) + (byStatus.pending || 0),
            };
        }
        return items.reduce(function (acc, item) {
            acc.created += Number(item.created || 0);
            acc.completed += Number(item.completed || 0);
            acc.failed += Number(item.failed || 0);
            return acc;
        }, {
            label: _dashboardSummaryLabel(rangeKey),
            created: 0,
            completed: 0,
            failed: 0,
        });
    }

    function _dashboardSummaryLabel(rangeKey) {
        if (rangeKey === '30d') return '近 30 天汇总';
        if (rangeKey === '7d') return '近 7 天汇总';
        return '今日汇总';
    }

    function _renderDashboardTrendMetric(label, tone, value, maxValue) {
        var numericValue = Number(value || 0);
        var width = numericValue <= 0 ? 0 : Math.max(10, Math.round((numericValue / Math.max(1, maxValue)) * 100));
        return '<div class="dashboard-trend-metric">'
            + '<span class="dashboard-trend-metric__name">' + _esc(label) + '</span>'
            + '<span class="dashboard-trend-track"><span class="dashboard-trend-fill is-' + _esc(tone) + '" style="width:' + width + '%"></span></span>'
            + '<strong class="dashboard-trend-metric__value">' + _esc(String(numericValue)) + '</strong>'
            + '</div>';
    }

    function _renderDashboardActivity(activity) {
        var tbody = document.querySelector('#mainHost [data-dashboard-activity]');
        if (!tbody) return;
        if (!activity.length) {
            tbody.innerHTML = '<tr><td colspan="5" class="subtle">暂无活动数据</td></tr>';
            return;
        }
        tbody.innerHTML = activity.map(function (item, index) {
                var entityLabel = _dashboardActivityEntityLabel(item.entity);
                var categoryLabel = _dashboardActivityCategoryLabel(item.category);
            return '<tr class="route-row' + (index === 0 ? ' is-selected' : '') + '" data-dashboard-activity-row="1">'
                + '<td><strong>' + _esc(item.title || '未命名动作') + '</strong></td>'
                    + '<td>' + _esc(entityLabel) + '</td>'
                    + '<td>' + _esc(categoryLabel) + '</td>'
                + '<td><span class="status-chip info">' + _esc(item.status || '--') + '</span></td>'
                + '<td class="subtle">' + _esc(_formatDashboardTime(item.time)) + '</td>'
                + '</tr>';
        }).join('');
        _bindDashboardActivityRows(activity);
        _bindDashboardViewAllButton();
    }

        function _dashboardActivityEntityLabel(value) {
            var key = String(value || '').trim().toLowerCase();
            var labels = {
                activity: '活动日志',
                seed: '种子数据',
                task: '任务',
                report_run: '报告运行',
                workflow_run: '工作流运行',
                workflow_definition: '工作流定义',
                experiment_project: '实验项目',
                experiment_view: '实验视图',
                analysis_snapshot: '分析快照',
                provider: 'AI 服务商',
                account: '账号',
                group: '分组',
                device: '设备',
                asset: '素材'
            };
            return labels[key] || value || '--';
        }

        function _dashboardActivityCategoryLabel(value) {
            var key = String(value || '').trim().toLowerCase();
            var labels = {
                seed: '数据初始化',
                task: '任务',
                warning: '预警',
                report: '报告',
                workflow: '工作流',
                experiment: '实验',
                maintenance: '维护',
                publish: '发布',
                interact: '互动',
                scrape: '采集'
            };
            return labels[key] || value || '--';
        }

    function _bindDashboardTaskFilterTrigger(card, statusFilter, toast) {
        if (!card) return;
        card.onclick = function (event) {
            if (event) {
                event.preventDefault();
                event.stopPropagation();
            }
            _openTaskQueueWithFilter(statusFilter, toast);
        };
    }

    function _bindDashboardViewAllButton() {
        var button = document.querySelector('#mainHost .table-card__header .ghost-button');
        if (!button || button.dataset.dashboardViewAllBound === '1') return;
        button.dataset.dashboardViewAllBound = '1';
        button.addEventListener('click', function (event) {
            event.preventDefault();
            event.stopPropagation();
            if (typeof renderRoute === 'function') renderRoute('report-center');
            if (typeof showToast === 'function') showToast('正在打开完整活动日志', 'info');
        });
    }

    function _openTaskQueueWithFilter(statusFilter, toast) {
        uiState['task-queue'] = uiState['task-queue'] || { statusFilter: 'all' };
        uiState['task-queue'].statusFilter = statusFilter || 'all';
        if (currentRoute === 'task-queue') {
            _syncTaskQueueFilterTabs(uiState['task-queue'].statusFilter);
            if (typeof applyCurrentRouteState === 'function') applyCurrentRouteState();
        } else if (typeof renderRoute === 'function') {
            renderRoute('task-queue');
        }
        if (toast && typeof showToast === 'function') showToast(toast, 'info');
    }

    function _bindDashboardActivityRows(activity) {
        var rows = document.querySelectorAll('#mainHost [data-dashboard-activity-row]');
        if (!rows.length) return;
        rows.forEach(function (row, index) {
            row.addEventListener('click', function () {
                rows.forEach(function (node) { node.classList.remove('is-selected'); });
                row.classList.add('is-selected');
                var item = activity[index] || {};
                var entityLabel = _dashboardActivityEntityLabel(item.entity);
                var categoryLabel = _dashboardActivityCategoryLabel(item.category);
                var detailHost = document.getElementById('detailHost');
                if (!detailHost) return;
                detailHost.innerHTML = '<div class="detail-root"><section class="panel"><div class="panel__header"><div><strong>'
                    + _esc(item.title || '活动详情') + '</strong><div class="subtle">来自活动流选中项</div></div><span class="status-chip info">'
                    + _esc(item.status || '--') + '</span></div><div class="detail-list">'
                    + '<div class="detail-item"><span class="subtle">关联对象</span><strong>' + _esc(entityLabel) + '</strong></div>'
                    + '<div class="detail-item"><span class="subtle">分类</span><strong>' + _esc(categoryLabel) + '</strong></div>'
                    + '<div class="detail-item"><span class="subtle">时间</span><strong>' + _esc(_formatDashboardTime(item.time)) + '</strong></div>'
                    + '</div></section></div>';
                detailHost.classList.remove('shell-hidden');
            });
        });
    }

    function _renderDashboardSystems(systems) {
        var host = document.querySelector('#mainHost [data-dashboard-systems]');
        var statusChip = document.querySelector('#mainHost [data-dashboard-systems-status]');
        if (!host) return;
        if (!systems.length) {
            host.innerHTML = '<div class="task-item"><div><strong>暂无系统状态</strong><div class="subtle">等待后端返回摘要</div></div><span class="pill warning">空</span></div>';
            if (statusChip) {
                statusChip.textContent = '暂无数据';
                statusChip.className = 'status-chip warning';
            }
            return;
        }
        var hasError = systems.some(function (item) { return item.tone === 'error'; });
        var hasWarning = systems.some(function (item) { return item.tone === 'warning'; });
        if (statusChip) {
            statusChip.textContent = hasError ? '存在异常' : (hasWarning ? '需要关注' : '运行稳定');
            statusChip.className = 'status-chip ' + (hasError ? 'error' : (hasWarning ? 'warning' : 'success'));
        }
        host.classList.add('dashboard-systems-grid');
        host.innerHTML = systems.map(function (item, index) {
            return '<button class="dashboard-system-card' + ((uiState.dashboard.selectedSystemKey ? uiState.dashboard.selectedSystemKey === item.key : index === 0) ? ' is-selected' : '') + '" data-dashboard-system-key="' + _esc(item.key || '') + '" type="button">'
                + '<div class="dashboard-system-card__head">'
                + '<strong>' + _esc(item.title || '--') + '</strong>'
                + '<span class="pill ' + _esc(item.tone || 'info') + '">' + _esc(item.status || '--') + '</span>'
                + '</div>'
                + '<div class="dashboard-system-card__summary">' + _esc(item.summary || '--') + '</div>'
                + '</button>';
        }).join('');
        _bindDashboardSystemItems(systems);
    }

    function _bindDashboardSystemItems(systems) {
        var items = document.querySelectorAll('#mainHost [data-dashboard-system-key]');
        if (!items.length) return;
        items.forEach(function (item) {
            item.addEventListener('click', function () {
                var key = item.getAttribute('data-dashboard-system-key');
                uiState.dashboard.selectedSystemKey = key;
                items.forEach(function (node) { node.classList.remove('is-selected'); });
                item.classList.add('is-selected');
                var current = systems.filter(function (entry) { return entry.key === key; })[0] || null;
                if (current) {
                    var detailHost = document.getElementById('detailHost');
                    if (detailHost) {
                        detailHost.innerHTML = '<div class="detail-root"><section class="panel"><div class="panel__header"><div><strong>'
                            + _esc(current.title || '系统状态') + '</strong><div class="subtle">实时状态摘要</div></div><span class="pill ' + _esc(current.tone || 'info') + '">' + _esc(current.status || '--') + '</span></div>'
                            + '<div class="detail-list"><div class="detail-item"><span class="subtle">摘要</span><strong>' + _esc(current.summary || '--') + '</strong></div><div class="detail-item"><span class="subtle">来源</span><strong>dashboard 运行时聚合</strong></div></div></section></div>';
                        detailHost.classList.remove('shell-hidden');
                    }
                }
            });
        });
    }

    function _syncDashboardRangeButtons(rangeKey) {
        document.querySelectorAll('#mainHost [data-dashboard-range] button').forEach(function (btn) {
            btn.classList.toggle('is-active', btn.getAttribute('data-range') === rangeKey);
        });
    }

    function _formatDashboardTime(value) {
        if (!value) return '--';
        var text = String(value);
        if (text.indexOf('T') !== -1) {
            return text.replace('T', ' ').slice(5, 16);
        }
        return text;
    }

    function _esc(value) {
        return String(value == null ? '' : value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    /* ══════════════════════════════════════════════
       Task Queue 页面
       ══════════════════════════════════════════════ */
    // Task Queue 主渲染与交互已拆分至 page-loaders/task-queue-main.js。

    /* ══════════════════════════════════════════════
       AI Provider 页面
       ══════════════════════════════════════════════ */
    loaders['ai-provider'] = function () {
        _wireHeaderPrimary(function () { openProviderForm(); }, '添加供应商');

        api.providers.list().then(function (providers) {
            providers = providers || [];
            runtimeSummaryHandlers['ai-provider']({ providers: providers });
            // 尝试渲染到表格
            var tbody = document.querySelector('#mainHost .table-wrapper tbody');
            if (tbody) {
                if (providers.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:32px;">暂无 AI 供应商，点击「添加供应商」开始配置</td></tr>';
                    return;
                }
                tbody.innerHTML = providers.map(function (p) {
                    var active = p.is_active === 'True' || p.is_active === true;
                    return '<tr data-id="' + (p.id || '') + '">'
                        + '<td><strong>' + _esc(p.name || '') + '</strong></td>'
                        + '<td>' + _esc(p.provider_type || '') + '</td>'
                        + '<td class="mono">' + _esc(p.default_model || '-') + '</td>'
                        + '<td><span class="status-chip ' + (active ? 'success' : 'info') + '">' + (active ? '启用中' : '未启用') + '</span></td>'
                        + '<td>'
                        + '<button class="ghost-button js-edit-provider" data-id="' + (p.id || '') + '">编辑</button>'
                        + (active ? '' : '<button class="ghost-button js-activate-provider" data-id="' + (p.id || '') + '">启用</button>')
                        + '<button class="ghost-button js-delete-provider" data-id="' + (p.id || '') + '" style="color:var(--status-error);">删除</button>'
                        + '</td></tr>';
                }).join('');
                _bindProviderActions(providers);
                return;
            }
            // 回退：渲染到列表容器
            var list = document.querySelector('#mainHost .metric-list, #mainHost .detail-list');
            if (!list) return;
            if (providers.length === 0) {
                list.innerHTML = '<div class="task-item"><div><strong>暂无 AI 供应商</strong><div class="subtle">请点击「添加供应商」开始配置</div></div></div>';
                return;
            }
            list.innerHTML = providers.map(function (p) {
                var active = p.is_active === 'True' || p.is_active === true;
                return '<div class="task-item" data-id="' + (p.id || '') + '">'
                    + '<div><strong>' + _esc(p.name || '') + '</strong>'
                    + '<div class="subtle">' + _esc(p.provider_type || '') + ' · ' + _esc(p.api_base || '') + '</div></div>'
                    + '<div style="display:flex;gap:6px;align-items:center;">'
                    + '<button class="ghost-button js-edit-provider" data-id="' + (p.id || '') + '">编辑</button>'
                    + '<span class="pill ' + (active ? 'success' : 'info') + '">' + (active ? '活跃' : '未启用') + '</span>'
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
                    showToast('供应商已启用', 'success');
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
                    title: '删除供应商',
                    message: '删除后所有使用此供应商的任务将受到影响。确定继续？',
                    confirmText: '删除',
                    tone: 'danger',
                }).then(function (ok) {
                    if (!ok) return;
                    api.providers.remove(id).then(function () {
                        showToast('供应商已删除');
                        loaders['ai-provider']();
                    });
                });
            });
        });
    }

    /* ══════════════════════════════════════════════
       Group Management 页面
       ══════════════════════════════════════════════ */
    loaders['group-management'] = function () {
        _wireHeaderPrimary(function () { openGroupForm(); });

        api.groups.list().then(function (groups) {
            groups = groups || [];
            runtimeSummaryHandlers['group-management']({ groups: groups });
            // 更新指标卡
            var statCards = document.querySelectorAll('#mainHost .stat-card');
            if (statCards.length >= 3) {
                var v0 = statCards[0].querySelector('.stat-card__value');
                if (v0) v0.textContent = groups.length;
                var v1 = statCards[1].querySelector('.stat-card__value');
                if (v1) v1.textContent = '0';
                var v2 = statCards[2].querySelector('.stat-card__value');
                if (v2) v2.textContent = groups.length > 0 ? '100%' : '0%';
            }
            // 渲染分组列表
            var list = document.querySelector('#mainHost .workbench-list');
            if (!list) return;
            if (groups.length === 0) {
                list.innerHTML = '<div class="empty-state" style="padding:32px;text-align:center;"><p>暂无分组</p><p class="subtle">点击「新建分组」开始组织账号</p></div>';
                return;
            }
            list.innerHTML = groups.map(function (g) {
                var color = g.color || '#6366f1';
                return '<div class="task-item" data-id="' + (g.id || '') + '" data-search="' + _esc((g.name || '') + ' ' + (g.description || '') + ' ' + (g.color || '')) + '" style="border-left:3px solid ' + _esc(color) + ';">'
                    + '<div><strong>' + _esc(g.name || '') + '</strong>'
                    + '<div class="subtle">' + _esc(g.description || '暂无描述') + '</div></div>'
                    + '<div style="display:flex;gap:6px;align-items:center;">'
                    + '<button class="ghost-button js-edit-group" data-id="' + (g.id || '') + '">编辑</button>'
                    + '<button class="ghost-button js-delete-group" data-id="' + (g.id || '') + '" style="color:var(--status-error);">删除</button>'
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
                    title: '删除分组',
                    message: '删除分组不会删除组内账号，但会解除绑定关系。确定继续？',
                    confirmText: '删除',
                    tone: 'danger',
                }).then(function (ok) {
                    if (!ok) return;
                    api.groups.remove(id).then(function () {
                        showToast('分组已删除');
                        loaders['group-management']();
                    }).catch(function (err) {
                        showToast('删除失败: ' + err.message, 'error');
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
        detailHost.innerHTML = '<div class="detail-root"><section class="panel"><div class="panel__header"><div><strong>' + _esc(provider.name || '供应商详情') + '</strong><div class="subtle">' + _esc(provider.provider_type || '-') + '</div></div><span class="status-chip ' + (active ? 'success' : 'info') + '">' + (active ? '启用中' : '未启用') + '</span></div><div class="detail-list"><div class="detail-item"><span class="subtle">默认模型</span><strong>' + _esc(provider.default_model || '-') + '</strong></div><div class="detail-item"><span class="subtle">API 地址</span><strong>' + _esc(provider.api_base || '-') + '</strong></div><div class="detail-item"><span class="subtle">最大 Token</span><strong>' + _esc(provider.max_tokens || '-') + '</strong></div></div></section></div>';
    }

    function _renderGroupDetail(group) {
        if (!group) return;
        var detailHost = document.getElementById('detailHost');
        if (!detailHost) return;
        detailHost.innerHTML = '<div class="detail-root"><section class="panel"><div class="panel__header"><div><strong>' + _esc(group.name || '分组详情') + '</strong><div class="subtle">组织编排详情</div></div><span class="status-chip info">已加载</span></div><div class="detail-list"><div class="detail-item"><span class="subtle">描述</span><strong>' + _esc(group.description || '无') + '</strong></div><div class="detail-item"><span class="subtle">颜色</span><strong>' + _esc(group.color || '-') + '</strong></div><div class="detail-item"><span class="subtle">分组 ID</span><strong>' + _esc(group.id || '-') + '</strong></div></div></section></div>';
    }

    /* ══════════════════════════════════════════════
       Device Management 页面
       ══════════════════════════════════════════════ */
    // Device Management 主渲染与交互已拆分至 page-loaders/device-management-main.js。

    function _deviceStatusMap(status) {
        var map = {
            healthy: { label: '正常', tone: 'success' },
            warning: { label: '告警', tone: 'warning' },
            error: { label: '异常', tone: 'error' },
            idle: { label: '空闲', tone: 'info' },
        };
        return map[String(status || '').toLowerCase()] || { label: status || '未知', tone: 'info' };
    }

    function _normalizeDeviceStatus(status) {
        var key = String(status || '').toLowerCase();
        return ['healthy', 'warning', 'error', 'idle'].indexOf(key) >= 0 ? key : 'idle';
    }

    function _normalizeDeviceProxyStatus(status) {
        var key = String(status || '').toLowerCase();
        return ['online', 'lost', 'offline'].indexOf(key) >= 0 ? key : 'offline';
    }

    function _deviceBool(value) {
        return value === true || String(value || '').toLowerCase() === 'true' || String(value || '') === '1';
    }

    function _deviceSortOrder(status) {
        var key = String(status || '').toLowerCase();
        if (key === 'error') return 1;
        if (key === 'warning') return 2;
        if (key === 'idle') return 3;
        return 4;
    }

    function _deviceInspectionTimestamp(device, boundAccounts) {
        var values = [device.updated_at, device.created_at];
        (boundAccounts || []).forEach(function (account) {
            values.push(account.last_connection_checked_at);
            values.push(account.last_login_check_at);
            values.push(account.cookie_updated_at);
        });
        var latest = null;
        values.forEach(function (value) {
            if (!value) return;
            var date = new Date(value);
            if (isNaN(date.getTime())) return;
            if (!latest || date > latest) latest = date;
        });
        return latest;
    }

    function _deviceProxyMeta(device, boundAccounts) {
        var hasProxy = !!String(device.proxy_ip || '').trim();
        var rawStatus = String(device.proxy_status || '').toLowerCase();
        var hasUnreachable = (boundAccounts || []).some(function (account) {
            return String(account.last_connection_status || '').toLowerCase() === 'unreachable';
        });
        if (!hasProxy) {
            return { value: 'offline', label: '离线', tone: 'error' };
        }
        if (rawStatus === 'offline') {
            return { value: 'offline', label: '离线', tone: 'error' };
        }
        if (rawStatus === 'lost' || hasUnreachable) {
            return { value: 'lost', label: '丢失', tone: 'warning' };
        }
        return { value: 'online', label: '在线', tone: 'success' };
    }

    function _deriveDeviceHealth(device, boundAccounts) {
        var hasProxy = !!String(device.proxy_ip || '').trim();
        var proxyMeta = _deviceProxyMeta(device, boundAccounts);
        var fingerprint = String(device.fingerprint_status || 'normal').toLowerCase();
        if (!hasProxy || !(boundAccounts || []).length) {
            return { status: 'idle', proxyStatus: proxyMeta.value };
        }
        if (proxyMeta.value === 'offline') {
            return { status: 'error', proxyStatus: proxyMeta.value };
        }
        if (proxyMeta.value === 'lost') {
            return { status: 'warning', proxyStatus: proxyMeta.value };
        }
        if (fingerprint === 'missing') {
            return { status: 'error', proxyStatus: proxyMeta.value };
        }
        if (fingerprint === 'drifted') {
            return { status: 'warning', proxyStatus: proxyMeta.value };
        }
        var hasCriticalAccount = (boundAccounts || []).some(function (account) {
            var loginStatus = String(account.last_login_check_status || '').toLowerCase();
            var connStatus = String(account.last_connection_status || '').toLowerCase();
            return loginStatus === 'invalid' || connStatus === 'unreachable';
        });
        if (hasCriticalAccount) {
            return { status: 'warning', proxyStatus: proxyMeta.value };
        }
        return { status: 'healthy', proxyStatus: proxyMeta.value };
    }

    function _summarizeAccountMessages(accounts, messageKey) {
        return (accounts || []).slice(0, 2).map(function (account) {
            var username = account.username || ('账号#' + account.id);
            var message = String(account[messageKey] || '').trim();
            return message ? (username + '：' + message) : username;
        }).join('；');
    }

    function _buildDeviceIssues(device, boundAccounts) {
        var issues = [];
        var hasProxy = !!String(device.proxy_ip || '').trim();
        var fingerprint = String(device.fingerprint_status || 'normal').toLowerCase();
        var proxyMeta = _deviceProxyMeta(device, boundAccounts);
        if (!hasProxy) {
            issues.push({ tone: 'warning', title: '未配置代理', copy: '当前设备没有可用代理地址，无法承担稳定隔离环境。' });
        } else if (proxyMeta.value === 'offline') {
            issues.push({ tone: 'error', title: '代理离线', copy: '设备代理状态为离线，当前环境不可用于账号操作。' });
        } else if (proxyMeta.value === 'lost') {
            issues.push({ tone: 'warning', title: '代理链路丢失', copy: _summarizeAccountMessages(boundAccounts.filter(function (account) {
                return String(account.last_connection_status || '').toLowerCase() === 'unreachable';
            }), 'last_connection_message') || '已检测到代理链路异常，请先复核连接状态。' });
        }
        if (fingerprint === 'missing') {
            issues.push({ tone: 'error', title: '指纹缺失', copy: '当前设备缺少指纹信息，建议先修复环境再使用。' });
        } else if (fingerprint === 'drifted') {
            issues.push({ tone: 'warning', title: '指纹漂移', copy: '当前设备指纹状态为漂移，继续批量操作有较高风险，需要先修复环境后再使用。' });
        }
        if (!(boundAccounts || []).length) {
            issues.push({ tone: 'info', title: '当前无绑定账号', copy: '该设备处于空闲状态，可分配给新账号或回收。' });
        }
        var loginRiskAccounts = (boundAccounts || []).filter(function (account) {
            return ['invalid', 'proxy_mismatch'].indexOf(String(account.last_login_check_status || '').toLowerCase()) >= 0;
        });
        if (loginRiskAccounts.length) {
            issues.push({ tone: 'warning', title: '绑定账号存在登录态风险', copy: _summarizeAccountMessages(loginRiskAccounts, 'last_login_check_message') || ('风险账号：' + loginRiskAccounts.slice(0, 3).map(function (item) { return item.username || ('账号#' + item.id); }).join('、') + '。') });
        }
        var unreachableAccounts = (boundAccounts || []).filter(function (account) {
            return String(account.last_connection_status || '').toLowerCase() === 'unreachable';
        });
        if (unreachableAccounts.length) {
            issues.push({ tone: 'error', title: '代理检测失败', copy: _summarizeAccountMessages(unreachableAccounts, 'last_connection_message') || ('检测失败账号：' + unreachableAccounts.slice(0, 3).map(function (item) { return item.username || ('账号#' + item.id); }).join('、') + '。') });
        }
        return issues;
    }

    function _buildDeviceViewModel(device, accounts) {
        var boundAccounts = (accounts || []).filter(function (account) {
            return String(account.device_id || '') === String(device.id || '');
        });
        var derived = _deriveDeviceHealth(device, boundAccounts);
        var displayStatus = _normalizeDeviceStatus(device.status || derived.status);
        var displayProxyStatus = _normalizeDeviceProxyStatus(device.proxy_status || derived.proxyStatus);
        var issues = _buildDeviceIssues(device, boundAccounts);
        var isolatedCount = boundAccounts.filter(function (account) { return _deviceBool(account.isolation_enabled); }).length;
        var lastInspection = _deviceInspectionTimestamp(device, boundAccounts);
        return {
            id: device.id,
            raw: device,
            name: device.name || device.device_code || '未命名设备',
            deviceCode: device.device_code || '-',
            proxyIp: device.proxy_ip || '',
            proxyLabel: device.proxy_ip ? (String(device.proxy_ip) + (device.region ? ' (' + _accountRegionLabel(device.region).replace('区', '') + ')' : '')) : '未配置代理',
            regionLabel: _accountRegionLabel(device.region || ''),
            fingerprintLabel: String(device.fingerprint_status || 'normal').toLowerCase() === 'drifted' ? '漂移' : (String(device.fingerprint_status || 'normal').toLowerCase() === 'missing' ? '缺失' : '正常'),
            status: displayStatus,
            statusMeta: _deviceStatusMap(displayStatus),
            proxyStatus: displayProxyStatus,
            proxyStatusLabel: displayProxyStatus === 'offline' ? '离线' : (displayProxyStatus === 'lost' ? '丢失' : '在线'),
            inspectedStatus: derived.status,
            inspectedProxyStatus: derived.proxyStatus,
            boundAccounts: boundAccounts,
            boundCount: boundAccounts.length,
            isolatedCount: isolatedCount,
            coveragePercent: boundAccounts.length ? Math.round((isolatedCount / boundAccounts.length) * 100) : 0,
            unisolatedCount: Math.max(0, boundAccounts.length - isolatedCount),
            issues: issues,
            issueCount: issues.length,
            searchText: [device.name || '', device.device_code || '', device.proxy_ip || '', device.region || '', displayStatus, issues.map(function (issue) { return issue.title + ' ' + issue.copy; }).join(' '), boundAccounts.map(function (account) { return account.username || ''; }).join(' ')].join(' '),
            lastInspectionAt: lastInspection,
            lastInspectionLabel: lastInspection ? _formatRelativeDate(lastInspection.toISOString()) : '未巡检',
            sortOrder: _deviceSortOrder(displayStatus),
        };
    }

    function _renderDeviceDetail(deviceModel, logs) {
        var page = window.__deviceManagementPageMain;
        if (page && typeof page.renderDeviceDetail === 'function') {
            return page.renderDeviceDetail(deviceModel, logs);
        }
    }

    function _selectDeviceCard(deviceId, models) {
        var page = window.__deviceManagementPageMain;
        if (page && typeof page.selectDeviceCard === 'function') {
            return page.selectDeviceCard(deviceId, models);
        }
    }

    function _getDeviceEnvironmentHelpers() {
        var helpers = window.__deviceEnvironmentHelpers;
        if (!helpers) {
            throw new Error('device environment helpers not loaded');
        }
        return helpers;
    }

    // Device Environment 动作链已拆分至 page-loaders/device-environment.js。
    function _runDeviceInspection(deviceIds) {
        return _getDeviceEnvironmentHelpers().runDeviceInspection(deviceIds);
    }

    function _runDeviceRepair(deviceIds) {
        return _getDeviceEnvironmentHelpers().runDeviceRepair(deviceIds);
    }

    function _openDeviceEnvironment(deviceId) {
        return _getDeviceEnvironmentHelpers().openDeviceEnvironment(deviceId);
    }

    function _exportDeviceReport() {
        return _getDeviceEnvironmentHelpers().exportDeviceReport();
    }

    function _exportDeviceLog(deviceId, options) {
        return _getDeviceEnvironmentHelpers().exportDeviceLog(deviceId, options);
    }

        // AI generation loaders moved to page-loaders/ai-generation-main.js.

/* ══════════════════════════════════════════════
       Asset Center 页面
       ══════════════════════════════════════════════ */
    // Asset Center 主渲染与交互已拆分至 page-loaders/asset-center-main.js。

    /* ══════════════════════════════════════════════
       System Settings 页面
       ══════════════════════════════════════════════ */
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

    /* ══════════════════════════════════════════════
       Analytics 页面
       ══════════════════════════════════════════════ */
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
                cards[2].querySelector('.stat-card__value').textContent = ((summary.providers && summary.providers.models) || []).length + ' 个';
            }
            var sourceList = document.querySelector('#mainHost .data-source-list');
            if (sourceList) {
                sourceList.innerHTML = [
                    { title: '实验项目', meta: '项目 ' + projects.length + ' / 持久化同步' },
                    { title: '实验视图', meta: '视图 ' + views.length + ' / 可用于对照' },
                    { title: '素材资产库', meta: '素材 ' + (assetStats.total || 0) + ' / 已连接' },
                    { title: 'AI 模型池', meta: '模型 ' + (((summary.providers && summary.providers.models) || []).length) + ' / 可用' },
                ].map(function (item, index) {
                    return '<button class="data-source-item ' + (index === 0 ? 'is-selected' : '') + '" type="button"><strong>' + _esc(item.title) + '</strong><span>' + _esc(item.meta) + '</span></button>';
                }).join('');
            }
            var overlay = document.querySelectorAll('#mainHost .visual-preview-overlay span');
            if (overlay.length >= 3) {
                overlay[0].textContent = '项目 ' + projects.length;
                overlay[1].textContent = '视图 ' + views.length;
                overlay[2].textContent = '素材 ' + (assetStats.total || 0);
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
            runtimeSummaryHandlers['visual-lab']({ summary: summary, projects: projects, views: views });
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
            runtimeSummaryHandlers['profit-analysis']({ summary: summary, conversion: conversion });
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
                    var name = item.name || ('账号 ' + (index + 1));
                    return '<article class="rival-card ' + (index === 0 ? 'is-self' : '') + '"><div class="rival-avatar">' + _esc(name.slice(0, 1).toUpperCase()) + '</div><strong>' + _esc(name) + '</strong><span>' + _formatNum(item.followers || 0) + '</span><em class="' + _esc(item.tone || 'info') + '">' + _esc(item.delta || '持续跟踪') + '</em></article>';
                }).join('');
            }
            var tbody = document.querySelector('#mainHost .table-wrapper tbody');
            if (tbody) {
                tbody.innerHTML = (analysis.rows || []).slice(0, 4).map(function (row) {
                    return '<tr class="route-row" data-search="' + _esc((row.title || '') + ' ' + (row.meta || '')) + '"><td><strong>' + _esc(row.title || '账号') + '</strong></td><td>' + _formatNum(row.value || 0) + '</td><td>' + _esc(row.meta || '等待数据') + '</td><td>' + _esc(row.conclusion || '继续观察') + '</td></tr>';
                }).join('');
                ensurePagination(tbody.closest('.table-card, .panel'), '当前展示 ' + Math.min(accounts.length, 3) + ' / ' + accounts.length + ' 个竞品样本');
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
                    _setTrafficSourceCard(sourceCards[index], item.value || 0, item.meta || '等待数据');
                });
            }
            var tbody = document.querySelector('#mainHost .table-wrapper tbody');
            if (tbody) {
                tbody.innerHTML = (analysis.rows || []).slice(0, 4).map(function (row) {
                    return '<tr class="route-row" data-search="' + _esc((row.label || '') + ' ' + (row.reason || '')) + '"><td><strong>' + _esc(row.label || '区域') + '</strong></td><td>' + _esc(row.delta || '等待数据') + '</td><td>' + _esc(row.reason || '等待数据') + '</td><td>' + _esc(row.action || '继续观察') + '</td></tr>';
                }).join('');
                ensurePagination(tbody.closest('.table-card, .panel'), '当前展示 ' + Math.min(accounts.length, 3) + ' / ' + accounts.length + ' 个流量区域');
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
                if (title) title.textContent = lead.title || bubbleLabels[0] || '内容机会';
                if (statsList.length >= 3) {
                    statsList[0].textContent = String(lead.heat || 0);
                    statsList[1].textContent = String(lead.competition || 0);
                    statsList[2].textContent = String(lead.coverage || 0) + '%';
                }
                if (desc) desc.textContent = lead.description || '机会判断已根据账号、素材与任务反馈自动刷新。';
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
                    title.textContent = report ? (report.title || ('报告 ' + (index + 1))) : (['经营日报', '利润专题', '互动洞察', '蓝海调研'][index] || ('模板 ' + (index + 1)));
                    meta.textContent = report ? ('状态 ' + (report.status || 'pending')) : '等待生成';
                }
            });
            var previewRows = document.querySelectorAll('#mainHost .report-preview-table div span');
            if (previewRows.length >= 3) {
                previewRows[0].textContent = '当前已沉淀 ' + reports.length + ' 份报告记录';
                previewRows[1].textContent = '最近活动日志 ' + activity.length + ' 条，可追踪报告动作';
                previewRows[2].textContent = '账号总量 ' + ((summary.accounts && summary.accounts.total) || 0) + ' / 素材总量 ' + ((summary.assets && summary.assets.total) || 0);
            }
            _setAnalyticsSeed({
                reportTrend: [reports.length, activity.length, ((summary.accounts && summary.accounts.total) || 0), ((summary.assets && summary.assets.total) || 0)],
            });
            runtimeSummaryHandlers['report-center']({ reports: reports, activity: activity, summary: summary });
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
                legends[0].lastChild.textContent = '正向 ' + String(sentiment.positive || 0) + '%';
                legends[1].lastChild.textContent = '中立 ' + String(sentiment.neutral || 0) + '%';
                legends[2].lastChild.textContent = '负向 ' + String(sentiment.negative || 0) + '%';
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
                    _setAffinityBar(affinityBars[index], Math.max(18, Math.min(96, 22 + (segment.count || 0) * 14)), segment.label || segment.key || ('分层 ' + (index + 1)));
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

    // Task ops route loaders moved to page-loaders/task-ops-main.js.

    // video-editor loader 已移至 page-loaders/video-editor-main.js

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
                { label: '当前实验', value: projects[0] ? (projects[0].name || '实验已保存') : (accounts.length ? (accounts[0].region || '多地区实验') : '实验待启动'), note: '账号与地域结构已同步进创意对比。'},
                { label: '待决策', value: String(Math.max(2, tasks.length)) + ' 组', note: '来自真实任务池的执行反馈已回写。'},
                { label: '保留倾向', value: assets.length > 3 ? '素材充分' : '素材偏少', note: '优先选择有足够素材支撑的方案。'},
            ]);
            _renderCreativeFocusCards(accounts, assets, tasks);
            _renderWorkbenchSideCards(tasks, '#mainHost .workbench-side-list');
            _renderStripCards(assets, '#mainHost .workbench-strip-grid', 'asset');
            _renderCreativeWorkshopDetail(projects, tasks, assets);
            runtimeSummaryHandlers['creative-workshop']({ projects: projects, tasks: tasks, assets: assets });
            _applyAiHandoffHint('creative-workshop', '#mainHost .workbench-strip-grid');
            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (e) {
            console.warn('[page-loaders] creative-workshop load failed:', e);
        });
    };

    // visual-editor loader 已移至 page-loaders/visual-editor-main.js


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
            _renderLicenseIssuer({ error: e && e.message ? e.message : '许可证状态获取失败' });
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
        _loadToolConsolePage({ routeKey: 'downloader', title: '下载器', mode: 'downloader' });
    };

    loaders['lan-transfer'] = function () {
        _loadToolConsolePage({ routeKey: 'lan-transfer', title: '局域网传输', mode: 'transfer' });
    };

    loaders['network-diagnostics'] = function () {
        _loadToolConsolePage({ routeKey: 'network-diagnostics', title: '网络诊断', mode: 'diagnostics' });
    };

    loaders['log-center'] = function () {
        _loadToolConsolePage({ routeKey: 'log-center', title: '日志中心', mode: 'log' });
    };

    loaders['operations-center'] = function () {
        _loadListManagementPage({ routeKey: 'operations-center', title: '运营中心', mode: 'operations' });
    };

    loaders['order-management'] = function () {
        _loadListManagementPage({ routeKey: 'order-management', title: '订单管理', mode: 'orders' });
    };

    loaders['service-center'] = function () {
        _loadListManagementPage({ routeKey: 'service-center', title: '客服中心', mode: 'service' });
    };

    loaders['refund-processing'] = function () {
        _loadListManagementPage({ routeKey: 'refund-processing', title: '退款处理', mode: 'refund' });
    };

    // Task ops route-specific helpers moved to page-loaders/task-ops-main.js.

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
            ['视频', counts.video],
            ['图片', counts.image],
            ['字幕', counts.subtitle],
            ['音频', counts.audio],
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
            // _bindAssetThumbs 已移至 editor-shared.js，由 video-editor-main.js 调用
        }
        if (assets[0]) _renderAssetDetail(assets[0]);
    }

    function _renderWorkbenchSideCards(items, selector) {
        var host = document.querySelector(selector);
        if (!host) return;
        host.innerHTML = (items || []).slice(0, 3).map(function (item, index) {
            var title = item.title || item.filename || ('项目 ' + (index + 1));
            var desc = item.result_summary || item.file_path || (_taskTypeLabel(item.task_type) + ' / ' + _taskStatusLabel(item.status));
            var tone = item.status ? _taskStatusTone(item.status) : 'info';
            var badge = item.status ? _taskStatusLabel(item.status) : (item.asset_type || '素材');
            return '<article class="workbench-sidecard"><div class="workbench-sidecard__head"><strong>' + _esc(title) + '</strong><span class="pill ' + tone + '">' + _esc(badge) + '</span></div><div class="subtle">' + _esc(desc) + '</div></article>';
        }).join('');
    }

    function _renderStripCards(items, selector, mode) {
        var host = document.querySelector(selector);
        if (!host) return;
        host.innerHTML = (items || []).slice(0, 3).map(function (item, index) {
            var title = item.title || item.filename || ('条目 ' + (index + 1));
            var desc = mode === 'asset' ? (item.file_path || '已进入素材编组') : (item.result_summary || _taskStatusLabel(item.status));
            var badge = mode === 'asset' ? (item.asset_type || '素材') : _taskStatusLabel(item.status || 'pending');
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
        if (strong) strong.textContent = 'AI 下发内容';
        if (subtle) subtle.textContent = String(handoff.text || '').slice(0, 72);
        if (pill) {
            pill.textContent = '已下发';
            pill.className = 'pill success';
        }
    }

    function _renderCreativeFocusCards(accounts, assets, tasks) {
        var host = document.querySelector('#mainHost .focus-grid');
        if (!host) return;
        var base = [
            { title: '账号地域组合', badge: 'A 方案', tone: 'success', desc: (accounts[0] ? ((accounts[0].region || '核心地区') + ' 表现更稳') : '暂无账号地域数据'), meta: '优先保留高体量地区内容验证' },
            { title: '素材覆盖率', badge: 'B 方案', tone: 'warning', desc: '当前已接入 ' + assets.length + ' 条素材，可支持多版本创意试验', meta: '素材充足时可推进双版本并行' },
            { title: '执行反馈', badge: '镜头', tone: 'info', desc: '任务池中有 ' + tasks.length + ' 个相关动作结果可回看', meta: '优先选完成率更高的创意路线' },
            { title: '输出建议', badge: '口播', tone: 'success', desc: '建议先产出短口播版本，再进入剪辑页验证', meta: '口播长度与素材数量已联动评估' },
        ];
        host.innerHTML = base.map(function (card, index) {
            return '<article class="focus-card ' + (index === 0 ? 'focus-card--wide' : '') + '"><div class="focus-card__head"><strong>' + _esc(card.title) + '</strong><span class="pill ' + card.tone + '">' + _esc(card.badge) + '</span></div><div class="subtle">' + _esc(card.desc) + '</div><div class="focus-card__meta">' + _esc(card.meta) + '</div></article>';
        }).join('');
    }

    function _renderCreativeWorkshopDetail(projects, tasks, assets) {
        var detailItems = document.querySelectorAll('#detailHost .detail-item strong');
        if (detailItems.length >= 3) {
            detailItems[0].textContent = projects[0] ? (projects[0].name || '已接入实验项目') : '暂无实验项目';
            detailItems[1].textContent = tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'failed'; }).length ? '存在失败任务待排查' : '当前无失败任务阻塞';
            detailItems[2].textContent = assets.length ? ('优先基于 ' + assets.length + ' 条素材进入下一轮验证') : '建议先补充素材后再继续实验';
        }
        var sideHost = document.querySelector('#detailHost .workbench-side-list');
        if (!sideHost) return;
        sideHost.innerHTML = (tasks || []).slice(0, 3).map(function (task) {
            return '<article class="workbench-sidecard"><div class="workbench-sidecard__head"><strong>' + _esc(task.title || '创意反馈') + '</strong><span class="pill ' + _taskStatusTone(task.status) + '">' + _esc(_taskStatusLabel(task.status)) + '</span></div><div class="subtle">' + _esc(task.result_summary || '已同步任务反馈') + '</div></article>';
        }).join('');
    }

    function _renderWorkflowNodes(assets, tasks, providers, definitions, runs) {
        var nodes = document.querySelectorAll('#mainHost .workflow-node');
        if (!nodes.length) return;
        var summaries = [
            '素材 ' + assets.length + ' 条',
            '工作流 ' + ((definitions || []).length || tasks.length) + ' 个',
            '供应商 ' + providers.length + ' 个',
            '运行中 ' + ((runs || []).filter(function (run) { return _normalizeTaskStatus(run.status) === 'running'; }).length || tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'running'; }).length) + ' 个',
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
                        showToast('日志路径已复制', 'success');
                    });
                    return;
                }
                showToast(config.title + ' 已同步真实数据', 'info');
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
                showToast('已刷新 ' + config.title + ' 数据', 'success');
            });
        });
        _bindToolQueueActions(config, tasks);
    }

    function _bindToolQueueActions(config, tasks) {
        _rewireElements('#mainHost .js-tool-queue-start', function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                api.tasks.start(id).then(function () {
                    showToast('队列任务已启动', 'success');
                    if (loaders[config.routeKey]) loaders[config.routeKey]();
                }).catch(function (err) {
                    showToast('启动失败: ' + err.message, 'error');
                });
            });
        });
        _rewireElements('#mainHost .js-tool-queue-pause', function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                api.tasks.update(id, { status: 'paused' }).then(function () {
                    showToast('队列任务已暂停', 'warning');
                    if (loaders[config.routeKey]) loaders[config.routeKey]();
                }).catch(function (err) {
                    showToast('暂停失败: ' + err.message, 'error');
                });
            });
        });
        _rewireElements('#mainHost .js-tool-queue-cancel', function (btn) {
            btn.addEventListener('click', function () {
                var id = parseInt(btn.dataset.id, 10);
                api.tasks.remove(id).then(function () {
                    showToast('队列任务已取消', 'success');
                    if (loaders[config.routeKey]) loaders[config.routeKey]();
                }).catch(function (err) {
                    showToast('取消失败: ' + err.message, 'error');
                });
            });
        });
    }

    function _pickFilesAndImportAsAssets(routeKey) {
        if (!api.utils || typeof api.utils.pickFiles !== 'function') {
            showToast('当前版本不支持文件选择', 'warning');
            return;
        }
        api.utils.pickFiles().then(function (files) {
            var list = (files || []).filter(Boolean);
            if (!list.length) {
                showToast('未选择文件', 'warning');
                return;
            }
            var jobs = list.map(function (filePath) {
                var parts = String(filePath).split(/[\\/]/);
                var filename = parts[parts.length - 1] || '未命名文件';
                return Promise.all([
                    api.assets.create({
                        filename: filename,
                        file_path: filePath,
                        asset_type: _guessAssetTypeByName(filename),
                        tags: '文件导入',
                    }).catch(function () { return null; }),
                    api.tasks.create({
                        title: '下载入库 · ' + filename,
                        task_type: 'maintenance',
                        priority: 'medium',
                        status: 'pending',
                        result_summary: '来源页面：下载器 / 文件：' + filePath,
                    }).catch(function () { return null; }),
                ]).then(function (pair) {
                    return pair[0] || pair[1];
                });
            });
            return Promise.all(jobs).then(function (results) {
                var successCount = results.filter(Boolean).length;
                showToast('已导入 ' + successCount + ' 个文件', successCount ? 'success' : 'warning');
                if (loaders[routeKey]) loaders[routeKey]();
            });
        }).catch(function (err) {
            showToast('导入失败: ' + err.message, 'error');
        });
    }

    function _pickFilesAndCreateTransferTasks(routeKey, accounts) {
        if (!api.utils || typeof api.utils.pickFiles !== 'function') {
            showToast('当前版本不支持文件选择', 'warning');
            return;
        }
        api.utils.pickFiles().then(function (files) {
            var list = (files || []).filter(Boolean);
            if (!list.length) {
                showToast('未选择发送文件', 'warning');
                return;
            }
            var targetId = accounts[0] ? accounts[0].id : '';
            var jobs = list.map(function (filePath) {
                var parts = String(filePath).split(/[\\/]/);
                var filename = parts[parts.length - 1] || '文件';
                return api.tasks.create({
                    title: '局域网传输 · ' + filename,
                    task_type: 'maintenance',
                    priority: 'medium',
                    status: 'pending',
                    account_id: targetId,
                    result_summary: '待发送文件：' + filePath,
                }).catch(function () { return null; });
            });
            return Promise.all(jobs).then(function (results) {
                var successCount = results.filter(Boolean).length;
                showToast('已加入 ' + successCount + ' 条传输任务', successCount ? 'success' : 'warning');
                if (loaders[routeKey]) loaders[routeKey]();
            });
        }).catch(function (err) {
            showToast('创建传输任务失败: ' + err.message, 'error');
        });
    }

    function _runNetworkDiagnosticsAndRender(routeKey, title) {
        if (!api.diagnostics || typeof api.diagnostics.run !== 'function') {
            showToast('当前版本不支持网络诊断', 'warning');
            return;
        }
        api.diagnostics.run().then(function (result) {
            window.__lastDiagnosticsResult = result || null;
            _saveDiagnosticsResult(result || null);
            _applyDiagnosticsResult(result || {});
            showToast(title + ' 已完成检测', 'success');
        }).catch(function (err) {
            showToast('诊断失败: ' + err.message, 'error');
            if (loaders[routeKey]) loaders[routeKey]();
        });
    }

    function _exportDiagnosticsReport(title) {
        var result = window.__lastDiagnosticsResult || null;
        if (!result || !result.reportText) {
            showToast('请先运行网络测试', 'warning');
            return;
        }
        if (!api.utils || typeof api.utils.exportTextFile !== 'function') {
            showToast('当前版本不支持导出', 'warning');
            return;
        }
        api.utils.exportTextFile(result.reportText).then(function (saved) {
            if (saved && saved.saved) {
                showToast(title + ' 导出成功', 'success');
                return;
            }
            showToast('已取消导出', 'warning');
        }).catch(function (err) {
            showToast('导出失败: ' + err.message, 'error');
        });
    }

    function _exportLogReport(logs) {
        var text = ((logs && logs.lines) || []).join('\n');
        if (!text) {
            showToast('当前没有可导出的日志', 'warning');
            return;
        }
        if (!api.utils || typeof api.utils.exportTextFile !== 'function') {
            showToast('当前版本不支持导出', 'warning');
            return;
        }
        api.utils.exportTextFile(text).then(function (saved) {
            if (saved && saved.saved) {
                showToast('日志导出成功', 'success');
                return;
            }
            showToast('已取消导出', 'warning');
        }).catch(function (err) {
            showToast('导出失败: ' + err.message, 'error');
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
            strip[0].textContent = '检测项 ' + checks.length;
            strip[1].textContent = '告警 ' + String(result.warningCount || 0);
            strip[2].textContent = '评分 ' + String(result.score || 0) + '%';
        }

        var list = document.querySelector('#mainHost .workbench-list');
        if (list) {
            list.innerHTML = (checks.length ? checks : [{ name: '无检测项', status: 'warning', detail: '请检查诊断配置' }]).map(function (item, index) {
                var tone = item.status === 'ok' ? 'success' : item.status === 'warning' ? 'warning' : 'error';
                var badge = item.status === 'ok' ? '通过' : item.status === 'warning' ? '警告' : '失败';
                return '<div class="task-item ' + (index === 0 ? 'is-selected' : '') + '"><div><strong>' + _esc(item.name || ('检测项 ' + (index + 1))) + '</strong><div class="subtle">' + _esc(item.detail || '') + '</div></div><span class="pill ' + tone + '">' + badge + '</span></div>';
            }).join('');
        }

        var detailItems = document.querySelectorAll('#detailHost .detail-item strong');
        if (detailItems.length >= 3) {
            detailItems[0].textContent = '检查项 ' + checks.length;
            detailItems[1].textContent = '错误 ' + String(result.errorCount || 0) + ' / 警告 ' + String(result.warningCount || 0);
            detailItems[2].textContent = '生成时间 ' + (result.generatedAt || '-');
        }

        var boardList = document.querySelector('#detailHost .board-list');
        if (boardList) {
            boardList.innerHTML = checks.slice(0, 3).map(function (item) {
                var tone = item.status === 'ok' ? 'success' : item.status === 'warning' ? 'warning' : 'error';
                var badge = item.status === 'ok' ? '通过' : item.status === 'warning' ? '警告' : '失败';
                return '<article class="board-card"><strong>' + _esc(item.name || '检测项') + '</strong><div class="subtle">' + _esc(item.detail || '') + '</div><div class="status-strip"><span class="pill ' + tone + '">' + badge + '</span></div></article>';
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
                showToast(config.title + ' 已接入真实数据草稿', 'info');
            });
        });
        _rewireElements('#mainHost .page-header .secondary-button', function (btn) {
            btn.addEventListener('click', function () {
                if (loaders[config.routeKey]) loaders[config.routeKey]();
                showToast('已刷新 ' + config.title + ' 数据', 'success');
            });
        });
    }

    function _listManagementDraft(config, accounts, assets, providers) {
        var drafts = {
            operations: {
                title: '运营排期协调',
                task_type: 'maintenance',
                priority: 'high',
                result_summary: '来源页面：运营中心 / 协调账号、素材与排期冲突',
            },
            orders: {
                title: '订单异常复核',
                task_type: 'report',
                priority: 'high',
                result_summary: '来源页面：订单管理 / 聚焦超时、争议与履约异常',
            },
            service: {
                title: '客服工单跟进',
                task_type: 'interact',
                priority: 'high',
                result_summary: '来源页面：客服中心 / 跟进超时工单与高风险投诉',
            },
            refund: {
                title: '退款审批处理',
                task_type: 'maintenance',
                priority: 'high',
                result_summary: '来源页面：退款处理 / 审批高金额与批量退款记录',
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
                    title: (account.region || '默认区域') + ' 运营排期',
                    desc: (account.username || '未绑定负责人') + ' / 素材 ' + (asset.filename || '待补齐') + ' / ' + _taskTypeLabel(task.task_type),
                    badge: task.status ? _taskStatusLabel(task.status) : '待协调',
                    tone: task.status ? _taskStatusTone(task.status) : 'warning',
                };
            });
        }
        if (config.mode === 'orders') {
            return tasks.slice(0, 4).map(function (task, index) {
                var account = accounts[index] || {};
                return {
                    title: 'ORD-' + String(2800 + index + 1),
                    desc: (account.username || account.region || '默认店铺') + ' / ' + (task.title || _taskTypeLabel(task.task_type)),
                    badge: _normalizeTaskStatus(task.status) === 'failed' ? '异常' : (_normalizeTaskStatus(task.status) === 'completed' ? '已完成' : '处理中'),
                    tone: _normalizeTaskStatus(task.status) === 'failed' ? 'error' : (_normalizeTaskStatus(task.status) === 'completed' ? 'success' : 'warning'),
                };
            });
        }
        if (config.mode === 'service') {
            return accounts.slice(0, 4).map(function (account, index) {
                var task = tasks[index] || {};
                return {
                    title: 'CS-' + String(1000 + index + 1),
                    desc: (account.username || '客户请求') + ' / ' + (task.result_summary || task.title || '待跟进工单'),
                    badge: _normalizeTaskStatus(task.status) === 'failed' ? '超时' : '跟进中',
                    tone: _normalizeTaskStatus(task.status) === 'failed' ? 'error' : 'warning',
                };
            });
        }
        return tasks.slice(0, 4).map(function (task, index) {
            var provider = providers[index] || {};
            return {
                title: 'RF-' + String(890 + index + 1),
                desc: (task.title || '退款申请') + ' / ' + (provider.name || '默认审批流'),
                badge: _normalizeTaskStatus(task.status) === 'completed' ? '已审核' : '待审批',
                tone: _normalizeTaskStatus(task.status) === 'completed' ? 'success' : 'warning',
            };
        });
    }

    function _renderSetupWizard(license, providers, settings, theme) {
        var machineCode = license.machine_id_short || license.machineCodeShort || license.machine_code_short || license.machine_id || license.machine_code || license.machineCode || license.device_id || license.deviceId || 'MID-UNBOUND';
        var hasLicense = !!(license.activated || license.active || license.is_activated || license.valid || String(license.status || '').toLowerCase() === 'active');
        var licenseTier = license.tier || license.license_tier || (hasLicense ? 'pro' : '未激活');
        var activeProvider = (providers || []).find(function (provider) {
            return provider.is_active || provider.active;
        }) || providers[0] || {};
        var market = settings.primary_market || settings.market || '美国（US）';
        var model = settings.default_model || settings.ai_model || settings.defaultModel || 'gpt-4.1-mini';
        var workflow = settings.default_workflow || settings.home_route || settings.workflow || '内容创作';
        var activeStep = !hasLicense ? 1 : !providers.length ? 2 : !model ? 3 : 4;
        var steps = document.querySelectorAll('#mainHost .wizard-step');
        steps.forEach(function (step, index) {
            step.classList.toggle('is-done', index < activeStep - 1);
            step.classList.toggle('is-active', index === activeStep - 1);
            var subtle = step.querySelector('.subtle');
            if (subtle) {
                subtle.textContent = index === 0
                    ? (hasLicense ? '设备已识别，可继续激活' : '等待许可证激活')
                    : index === 1
                        ? (hasLicense ? '许可证状态正常' : '请先完成本机激活')
                        : index === 2
                            ? (providers.length ? '已发现 ' + providers.length + ' 个供应商' : '至少接入 1 个供应商')
                            : index === 3
                                ? ('当前默认模型：' + model)
                                : ('当前工作流：' + workflow);
            }
        });

        var activeHost = document.querySelector('#mainHost .wizard-active-step');
        if (activeHost) {
            var headerTitle = activeStep === 1 ? '许可证激活' : activeStep === 2 ? '供应商接入' : activeStep === 3 ? '默认模型' : '使用偏好';
            var headerDesc = activeStep === 1
                ? '当前设备已识别，完成授权后才能解锁后续功能。'
                : activeStep === 2
                    ? '选择一个可用供应商，系统才能启用 AI 生成能力。'
                    : activeStep === 3
                        ? '确认默认模型，避免后续不同工作流配置分散。'
                        : '最后确认常用市场和默认工作流。';
            var fields = activeStep === 1
                ? [
                    { label: '机器显示码', value: machineCode, hint: '短码用于人工核对，完整机器码可在激活页复制' },
                    { label: '许可证状态', value: hasLicense ? ('已激活 / ' + String(licenseTier).toUpperCase()) : '待激活', hint: hasLicense ? '许可证已绑定当前设备' : '请输入有效许可证密钥' },
                ]
                : activeStep === 2
                    ? [
                        { label: '当前供应商', value: activeProvider.name || '未配置', hint: providers.length ? '已检测到 ' + providers.length + ' 个供应商配置' : '请至少配置一个 AI 供应商' },
                        { label: '推荐动作', value: providers.length ? '验证 API Key' : '新建供应商', hint: '完成连通性验证后再进入模型配置' },
                    ]
                    : activeStep === 3
                        ? [
                            { label: '默认模型', value: model, hint: '当前用于标题、脚本和文案生成' },
                            { label: '主题', value: theme === 'dark' ? '深色' : '浅色', hint: '主题已同步到当前桌面壳层' },
                        ]
                        : [
                            { label: '主要市场', value: market, hint: '影响默认货币、语言与时区' },
                            { label: '常用工作流', value: workflow, hint: '完成后将优先展示对应页面' },
                        ];
            activeHost.innerHTML = '<div class="config-form-group__header"><strong>' + _esc(headerTitle) + '</strong><div class="subtle">' + _esc(headerDesc) + '</div></div><div class="config-form-fields">' + fields.map(function (field) {
                return '<div class="config-field"><label class="config-field__label">' + _esc(field.label) + '</label><div class="config-field__control"><div class="config-input">' + _esc(field.value) + '</div></div><div class="config-field__hint subtle">' + _esc(field.hint) + '</div></div>';
            }).join('') + '</div>';
        }

        var notice = document.querySelector('#mainHost .notice-banner');
        if (notice) {
            var strong = notice.querySelector('strong');
            var desc = notice.querySelector('div div');
            if (strong) strong.textContent = hasLicense ? '初始化已进入可用阶段' : '当前还未完成许可证激活';
            if (desc) desc.textContent = hasLicense
                ? '下一步建议确认供应商与默认模型，避免后续 AI 页面不可用。'
                : '当前设备码已生成，请先完成许可证绑定，再继续后续供应商与模型配置。';
        }

        var detailItems = document.querySelectorAll('#detailHost .detail-item strong');
        if (detailItems.length >= 3) {
            detailItems[0].textContent = activeStep + ' / 5';
            detailItems[1].textContent = providers.length ? '约 1 分钟' : '约 2 分钟';
            detailItems[2].textContent = hasLicense ? '已绑定当前设备' : '待绑定';
        }
        var tips = document.querySelector('#detailHost .workbench-side-list');
        if (tips) {
            tips.innerHTML = [
                { title: '许可证状态', desc: hasLicense ? '当前许可证已激活，可继续初始化。' : '授权未完成前，AI 与同步功能不可用。', badge: hasLicense ? '正常' : '阻塞', tone: hasLicense ? 'success' : 'warning' },
                { title: '供应商接入', desc: providers.length ? '已检测到 ' + providers.length + ' 个供应商配置。' : '尚未检测到 AI 供应商。', badge: providers.length ? '已接入' : '待接入', tone: providers.length ? 'success' : 'warning' },
                { title: '默认工作流', desc: '当前推荐以“' + workflow + '”作为进入路径。', badge: market, tone: 'info' },
            ].map(function (card) {
                return '<article class="strip-card"><strong>' + _esc(card.title) + '</strong><div class="subtle">' + _esc(card.desc) + '</div><span class="pill ' + card.tone + '">' + _esc(card.badge) + '</span></article>';
            }).join('');
        }
    }

    function _renderLicenseIssuer(status) {
        var shortId = status.machine_id_short || status.machineCodeShort || status.machine_code_short || '----';
        var fullId = status.machine_id || status.machineCode || status.machine_code || '';
        var activated = !!status.activated;
        var tier = status.tier ? String(status.tier).toUpperCase() : '未激活';
        var shortStat = document.getElementById('licenseIssuerShort');
        var shortEcho = document.getElementById('licenseIssuerShortEcho');
        var statusEcho = document.getElementById('licenseIssuerStatus');
        var machineInput = document.getElementById('licenseIssuerMachineId');
        var meta = document.getElementById('licenseIssuerMeta');
        if (shortStat) shortStat.textContent = shortId;
        if (shortEcho) shortEcho.textContent = shortId;
        if (statusEcho) statusEcho.textContent = activated ? ('已激活 / ' + tier) : '未激活';
        if (machineInput && !machineInput.value) machineInput.value = fullId;
        if (meta && status.error) meta.textContent = '状态提示：' + status.error;

        _rewireElements('#licenseIssuerUseLocal', function (btn) {
            btn.addEventListener('click', function () {
                if (machineInput) machineInput.value = fullId;
                if (typeof showToast === 'function') showToast('已填入本机完整机器码', 'success');
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
                    if (infoMeta) infoMeta.textContent = '请先输入完整机器码';
                    return;
                }
                btn.disabled = true;
                btn.textContent = '签发中…';
                api.license.issue(machineId, days, issueTier).then(function (result) {
                    if (output) output.value = result.license_key || '';
                    if (infoMeta) {
                        infoMeta.textContent = '签发完成：' + String(result.tier || issueTier).toUpperCase() + ' / ' + (result.expiry || '永久') + ' / 机器码 ' + (result.machine_id || machineId).slice(0, 16).toUpperCase();
                    }
                    if (typeof showToast === 'function') showToast('许可证已生成', 'success');
                }).catch(function (err) {
                    if (infoMeta) infoMeta.textContent = err.message || '许可证生成失败';
                    if (typeof showToast === 'function') showToast(err.message || '许可证生成失败', 'error');
                }).finally(function () {
                    btn.disabled = false;
                    btn.textContent = '生成许可证';
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
                    if (infoMeta) infoMeta.textContent = '请先提供机器码并生成或粘贴许可证';
                    return;
                }
                api.license.verify(machineId, key).then(function (info) {
                    if (infoMeta) infoMeta.textContent = '校验通过：' + String(info.tier || '').toUpperCase() + ' / ' + (info.expiry || '永久');
                    if (typeof showToast === 'function') showToast('许可证校验通过', 'success');
                }).catch(function (err) {
                    if (infoMeta) infoMeta.textContent = err.message || '许可证校验失败';
                    if (typeof showToast === 'function') showToast(err.message || '许可证校验失败', 'error');
                });
            });
        });
    }

    function _copyLicenseIssuerText(text) {
        if (!text) {
            if (typeof showToast === 'function') showToast('没有可复制的内容', 'warning');
            return;
        }
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(function () {
                if (typeof showToast === 'function') showToast('已复制到剪贴板', 'success');
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
        if (typeof showToast === 'function') showToast(copied ? '已复制到剪贴板' : '复制失败，请手动复制', copied ? 'success' : 'warning');
    }

    function _renderPermissionManagement(accounts, providers, tasks) {
        var groups = document.querySelectorAll('#mainHost .config-form-group');
        var admins = accounts.slice(0, 1);
        var operators = accounts.slice(1, Math.min(4, accounts.length));
        var readonlyCount = Math.max(0, accounts.length - admins.length - operators.length);
        if (groups[0]) {
            var fields = groups[0].querySelectorAll('.config-field');
            var roleValues = [
                { value: admins.length ? admins[0].username || '系统管理员' : '待分配', hint: '当前拥有系统最高权限' },
                { value: operators.length ? operators.length + ' 个活跃账号' : '待分配', hint: '覆盖任务、账号与内容相关操作' },
                { value: readonlyCount + ' 个观察位', hint: '适合外部协作和审阅场景' },
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
                providers.length ? '读写' : '只读',
                tasks.length > 0 ? '读写' : '只读',
                providers.length > 1 ? '读写' : '只读',
                readonlyCount > 0 ? '只读' : '禁止',
            ];
            groups[1].querySelectorAll('.config-field').forEach(function (field, index) {
                var value = field.querySelector('.config-select span, .config-input');
                if (value && perms[index]) value.textContent = perms[index];
            });
        }
        var detailItems = document.querySelectorAll('#detailHost .detail-item strong');
        if (detailItems.length >= 2) {
            detailItems[0].textContent = operators.length ? '运营角色已覆盖主要流程' : '角色分配待完善';
            detailItems[1].textContent = tasks.length ? '最近变更 ' + _taskTime(tasks[0], 0) : '暂无变更记录';
        }
        var sideCards = document.querySelector('#detailHost .workbench-side-list');
        if (sideCards) {
            sideCards.innerHTML = [
                { title: '角色规模', desc: '当前共接入 ' + accounts.length + ' 个账号对象，可映射为多角色协作。', badge: '账号 ' + accounts.length, tone: 'info' },
                { title: '权限矩阵', desc: providers.length ? 'AI 模块已有可用供应商，可开放高级能力。' : 'AI 模块暂缺供应商，建议保持只读。', badge: providers.length ? '可放开' : '受限', tone: providers.length ? 'success' : 'warning' },
                { title: '审计热度', desc: '当前任务池共 ' + tasks.length + ' 条记录，可作为操作审计参考。', badge: tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'failed'; }).length + ' 异常', tone: 'warning' },
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
                showToast('请先完成许可证激活', 'warning');
                return;
            }
            if (!providers.length) {
                if (typeof renderRoute === 'function') renderRoute('ai-provider');
                showToast('请先接入至少 1 个 AI 供应商', 'warning');
                return;
            }

            var payload = {
                'theme': theme,
                'onboarding.completed': '1',
                'onboarding.completed_at': _nowStamp(),
                'onboarding.default_provider': providers[0].name || 'default',
                'onboarding.default_model': providers[0].default_model || 'gpt-4.1-mini',
                'onboarding.primary_market': settings.primary_market || settings.market || '美国（US）',
                'onboarding.workflow': settings.default_workflow || settings.home_route || '内容创作',
            };
            var save = (api.settings && typeof api.settings.setBatch === 'function')
                ? api.settings.setBatch(payload)
                : Promise.all(Object.keys(payload).map(function (key) { return api.settings.set(key, payload[key]); }));
            save.then(function () {
                return api.tasks.create({
                    title: '初始化完成确认',
                    task_type: 'onboarding_finalize',
                    priority: 'high',
                    status: 'pending',
                    result_summary: '向导已完成，默认供应商：' + (payload['onboarding.default_provider'] || '-'),
                }).catch(function () { return null; });
            }).finally(function () {
                if (typeof renderRoute === 'function') renderRoute('ai-content-factory');
                showToast('初始化已保存并进入 AI 内容工厂', 'success');
            });
        }

        function skipAction() {
            api.settings.set('onboarding.skipped_at', _nowStamp()).catch(function () { return null; }).finally(function () {
                api.tasks.create({
                    title: '补全初始化配置',
                    task_type: 'onboarding_followup',
                    priority: 'medium',
                    status: 'pending',
                    result_summary: '用户选择稍后完成 setup-wizard。',
                }).catch(function () { return null; });
                if (typeof renderRoute === 'function') renderRoute('dashboard');
                showToast('已跳过，稍后可在设置中继续', 'info');
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
                    title: '新建角色草稿',
                    task_type: 'permission_role',
                    priority: 'medium',
                    status: 'pending',
                    result_summary: '角色草稿已创建：账号 ' + accounts.length + ' / 供应商 ' + providers.length,
                }).then(function () {
                    showToast('已创建角色草稿任务', 'success');
                }).catch(function (err) {
                    showToast('创建角色草稿失败: ' + err.message, 'error');
                });
            });
        });

        _rewireElements('#mainHost .page-header .secondary-button', function (btn) {
            btn.addEventListener('click', function () {
                var text = [
                    '权限审计导出 ' + _nowStamp(),
                    '账号总数: ' + accounts.length,
                    '供应商总数: ' + providers.length,
                    '任务总数: ' + tasks.length,
                    '失败任务: ' + tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'failed'; }).length,
                ].join('\n');
                if (!api.utils || typeof api.utils.exportTextFile !== 'function') {
                    showToast('当前版本不支持导出', 'warning');
                    return;
                }
                api.utils.exportTextFile(text).then(function (saved) {
                    showToast(saved && saved.saved ? '审计日志导出成功' : '已取消导出', saved && saved.saved ? 'success' : 'warning');
                }).catch(function (err) {
                    showToast('导出失败: ' + err.message, 'error');
                });
            });
        });
    }

    function _bindAnalyticsHeaderActions(routeKey, context) {
        var routeMap = {
            'visual-lab': '可视化实验室',
            'profit-analysis': '利润分析',
            'competitor-monitor': '竞品监控',
            'traffic-board': '流量看板',
            'blue-ocean': '蓝海分析',
            'report-center': '数据报告中心',
            'interaction-analysis': '互动分析',
            'ecommerce-conversion': '电商转化',
            'fan-profile': '粉丝画像',
        };
        var routeTitle = routeMap[routeKey] || routeKey;

        function summary() {
            var accounts = (context && context.accounts) || [];
            var tasks = (context && context.tasks) || [];
            var assets = (context && context.assets) || [];
            var failed = tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'failed'; }).length;
            return routeTitle + ' / 账号 ' + accounts.length + ' / 任务 ' + tasks.length + ' / 素材 ' + (assets.length || assets.total || 0) + ' / 异常 ' + failed;
        }

        _rewireElements('#mainHost .page-header .primary-button', function (btn) {
            btn.addEventListener('click', function () {
                api.tasks.create({
                    title: routeTitle + '执行任务',
                    task_type: 'analytics_workflow',
                    priority: 'high',
                    status: 'pending',
                    result_summary: summary(),
                }).then(function () {
                    showToast(routeTitle + '任务已创建', 'success');
                }).catch(function (err) {
                    showToast('创建失败: ' + err.message, 'error');
                });
            });
        });

        _rewireElements('#mainHost .page-header .secondary-button', function (btn) {
            btn.addEventListener('click', function () {
                if (!api.utils || typeof api.utils.exportTextFile !== 'function') {
                    showToast('当前版本不支持导出', 'warning');
                    return;
                }
                var text = [
                    routeTitle + ' 导出报告',
                    '时间: ' + _nowStamp(),
                    summary(),
                ].join('\n');
                api.utils.exportTextFile(text).then(function (saved) {
                    showToast(saved && saved.saved ? (routeTitle + '导出成功') : '已取消导出', saved && saved.saved ? 'success' : 'warning');
                }).catch(function (err) {
                    showToast('导出失败: ' + err.message, 'error');
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
            ? ['素材池 ' + assets.length + ' 条', '失败重试 ' + assets.filter(function (asset) { return !asset.file_path; }).length, '缓存目录已同步']
            : config.mode === 'transfer'
                ? ['在线节点 ' + accounts.length, '待发送文件 ' + assets.length, '接收端准备完成']
                : config.mode === 'diagnostics'
                    ? ['供应商链路 ' + providers.length, '异常任务 ' + tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'failed'; }).length, '诊断报告可导出']
                    : config.mode === 'log'
                        ? ['日志文件 ' + ((logs && logs.lineCount) || 0) + ' 行', '错误 ' + ((logs && logs.errorCount) || 0), '路径已接入']
                    : ['今日日志 ' + tasks.length, '告警 ' + tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'failed'; }).length, '系统状态可追踪'];
        chips.forEach(function (chip, index) {
            var strong = chip.querySelector('strong');
            var subtle = chip.querySelector('.subtle');
            if (strong && lines[index]) strong.textContent = lines[index];
            if (subtle) subtle.textContent = config.title + ' 已同步真实运行数据';
        });
    }

    function _renderToolConsoleForm(tasks, assets, accounts, providers, logs, config) {
        var fields = document.querySelectorAll('#mainHost .settings-grid .form-field');
        var rows = config.mode === 'downloader'
            ? [
                { label: '缓存目录', value: assets[0] && assets[0].file_path ? assets[0].file_path.split('\\').slice(0, -1).join('\\') || assets[0].file_path : 'workspace/assets' },
                { label: '目标对象', value: assets[0] ? (assets[0].filename || '默认素材集') : '默认下载队列' },
                { label: '执行模式', value: '自动重试' },
            ]
            : config.mode === 'transfer'
                ? [
                    { label: '策略名称', value: '局域网快速分发' },
                    { label: '目标对象', value: accounts[0] ? (accounts[0].username || '发现设备 1') : '等待发现设备' },
                    { label: '执行模式', value: assets.length ? '批量发送' : '待命' },
                ]
                : config.mode === 'diagnostics'
                    ? [
                        { label: '策略名称', value: '全链路巡检' },
                        { label: '目标对象', value: providers[0] ? (providers[0].name || '主供应商') : '默认网络栈' },
                        { label: '执行模式', value: '自动诊断' },
                    ]
                    : config.mode === 'log'
                        ? [
                            { label: '日志文件', value: (logs && logs.path) || '日志文件不存在' },
                            { label: '最近错误数', value: String((logs && logs.errorCount) || 0) },
                            { label: '读取窗口', value: '最近 200 行' },
                        ]
                    : [
                        { label: '策略名称', value: '日志归档策略' },
                        { label: '目标对象', value: tasks[0] ? (tasks[0].title || '最新任务') : '全局日志流' },
                        { label: '执行模式', value: '滚动留存' },
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
                            title: provider.name || ('链路 ' + (index + 1)),
                            desc: provider.base_url || provider.model || '已接入诊断巡检列表',
                            badge: provider.is_active || provider.active ? '在线' : '待验证',
                            tone: provider.is_active || provider.active ? 'success' : 'warning',
                        };
                    })
                    : config.mode === 'log'
                        ? ((logs && logs.lines) || []).slice(-6).reverse().map(function (line, index) {
                            return _buildLogConsoleItem(line, index);
                        })
                    : tasks.slice(0, 3).map(function (task, index) {
                        return {
                            title: task.title || ('日志流 ' + (index + 1)),
                            desc: task.result_summary || (_taskTypeLabel(task.task_type) + ' / ' + _taskTime(task, index)),
                            badge: _taskStatusLabel(task.status),
                            tone: _taskStatusTone(task.status),
                        };
                    });
        host.innerHTML = (items.length ? items : [{ title: config.title + '暂无数据', desc: '等待后端数据接入', badge: '待命', tone: 'info' }]).map(function (item, index) {
            var actionHtml = item.actions || '';
            return '<div class="task-item ' + (index === 0 ? 'is-selected' : '') + '"><div><strong>' + _esc(item.title) + '</strong><div class="subtle">' + _esc(item.desc) + '</div>' + actionHtml + '</div><span class="pill ' + item.tone + '">' + _esc(item.badge) + '</span></div>';
        }).join('');
    }

    function _filterToolQueueTasks(tasks, mode) {
        var prefix = mode === 'transfer' ? '局域网传输 · ' : '下载入库 · ';
        return (tasks || []).filter(function (task) {
            return String(task.title || '').indexOf(prefix) === 0;
        });
    }

    function _buildToolQueueItem(task, index, mode) {
        var status = _normalizeTaskStatus(task.status);
        var progress = status === 'completed' ? 100 : status === 'running' ? 62 : status === 'paused' ? 45 : status === 'failed' ? 33 : 18;
        var actions = [];
        if (status === 'pending' || status === 'paused' || status === 'failed') {
            actions.push('<button class="ghost-button js-tool-queue-start" data-id="' + (task.id || '') + '">重试</button>');
        }
        if (status === 'running') {
            actions.push('<button class="ghost-button js-tool-queue-pause" data-id="' + (task.id || '') + '">暂停</button>');
        }
        actions.push('<button class="danger-button js-tool-queue-cancel" data-id="' + (task.id || '') + '">取消</button>');
        return {
            title: task.title || ((mode === 'transfer' ? '传输任务 ' : '下载任务 ') + (index + 1)),
            desc: '进度 ' + progress + '% · ' + (task.result_summary || '等待执行'),
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
            { title: '当前总览', desc: config.mode === 'downloader' ? ('素材文件 ' + assets.length + ' 条') : config.mode === 'transfer' ? ('可达节点 ' + accounts.length + ' 个') : config.mode === 'diagnostics' ? ('供应商端点 ' + providers.length + ' 个') : config.mode === 'log' ? ('日志文件最近 ' + ((logs && logs.lineCount) || 0) + ' 行') : ('日志来源 ' + tasks.length + ' 条'), badge: '已同步', tone: 'success' },
            { title: '待处理项', desc: config.mode === 'log' ? ('检测到 ' + ((logs && logs.errorCount) || 0) + ' 条错误日志') : failedCount ? ('发现 ' + failedCount + ' 个异常任务待排查') : '当前未发现阻塞项', badge: config.mode === 'log' ? (((logs && logs.errorCount) || 0) ? '需排查' : '正常') : failedCount ? '需复核' : '正常', tone: config.mode === 'log' ? (((logs && logs.errorCount) || 0) ? 'warning' : 'success') : failedCount ? 'warning' : 'success' },
            { title: '维护建议', desc: config.mode === 'diagnostics' ? '建议导出本次链路检测结果并留档。' : config.mode === 'log' ? '建议优先排查最新 ERROR 和 WARNING，必要时导出日志文件。' : '建议保留最近一次处理结果用于回溯。', badge: '建议', tone: 'info' },
        ];
        host.innerHTML = cards.map(function (card) {
            return '<article class="settings-card"><strong>' + _esc(card.title) + '</strong><div class="subtle">' + _esc(card.desc) + '</div><div class="status-strip"><span class="pill ' + card.tone + '">' + _esc(card.badge) + '</span></div></article>';
        }).join('');
    }

    function _renderToolConsoleDetail(tasks, assets, accounts, providers, logs, config) {
        var items = document.querySelectorAll('#detailHost .detail-item strong');
        if (items.length >= 3) {
            items[0].textContent = config.mode === 'downloader' ? ('素材 ' + assets.length + ' 条') : config.mode === 'transfer' ? ('设备 ' + accounts.length + ' 个') : config.mode === 'diagnostics' ? ('链路 ' + providers.length + ' 条') : config.mode === 'log' ? ('路径 ' + (((logs && logs.path) || '').split('\\').pop() || 'app.log')) : ('日志 ' + tasks.length + ' 条');
            items[1].textContent = config.mode === 'log' ? (((logs && logs.errorCount) || 0) + ' 条错误 / ' + (((logs && logs.warningCount) || 0)) + ' 条警告') : tasks.filter(function (task) { return _normalizeTaskStatus(task.status) !== 'completed'; }).length + ' 条待处理';
            items[2].textContent = config.title + ' 已切换为真实数据视图';
        }
        var boardList = document.querySelector('#detailHost .board-list');
        if (boardList) {
            var pool = config.mode === 'downloader' ? assets : config.mode === 'diagnostics' ? providers : config.mode === 'log' ? (((logs && logs.lines) || []).slice(-3).reverse()) : tasks;
            boardList.innerHTML = (pool || []).slice(0, 3).map(function (item, index) {
                var title = config.mode === 'log' ? _logLineTitle(item, index) : (item.filename || item.name || item.title || (config.title + '记录 ' + (index + 1)));
                var desc = config.mode === 'log' ? _logLineDesc(item) : (item.file_path || item.base_url || item.result_summary || _taskTypeLabel(item.task_type));
                var badge = config.mode === 'log' ? _logLineBadge(item) : (item.status ? _taskStatusLabel(item.status) : (item.is_active || item.active ? '在线' : '同步'));
                var tone = config.mode === 'log' ? _logLineTone(item) : (item.status ? _taskStatusTone(item.status) : ((item.is_active || item.active) ? 'success' : 'info'));
                return '<article class="board-card"><strong>' + _esc(title) + '</strong><div class="subtle">' + _esc(desc || '运行数据已接入') + '</div><div class="status-strip"><span class="pill ' + tone + '">' + _esc(badge) + '</span></div></article>';
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
        if (match) return match[2] + ' · ' + match[1];
        return '日志记录 ' + (index + 1);
    }

    function _logLineDesc(line) {
        return String(line || '').replace(/^\[[^\]]+\]\s+[A-Z]+\s+[^\s]+\s+/, '').trim();
    }

    function _logLineBadge(line) {
        var upper = String(line || '').toUpperCase();
        if (upper.indexOf('ERROR') !== -1 || upper.indexOf('CRITICAL') !== -1) return '错误';
        if (upper.indexOf('WARNING') !== -1) return '警告';
        return '信息';
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
                    : [String(tasks.filter(function (task) { return _normalizeTaskStatus(task.status) !== 'completed'; }).length), String(tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'completed'; }).length), '¥' + _formatNum((assets.length * 320) + (providers.length * 1200))];
        cards.forEach(function (card, index) {
            var value = card.querySelector('.stat-card__value');
            if (value && values[index] !== undefined) value.textContent = values[index];
        });
    }

    function _renderListManagementItems(tasks, accounts, assets, providers, config) {
        var host = document.querySelector('#mainHost .workbench-list');
        if (!host) return;
        var items = _listManagementRecords(tasks, accounts, assets, providers, config);
        host.innerHTML = (items.length ? items : [{ title: config.title + '暂无数据', desc: '等待后端数据写入', badge: '待命', tone: 'info' }]).map(function (item, index) {
            return '<div class="task-item ' + (index === 0 ? 'is-selected' : '') + '"><div><strong>' + _esc(item.title) + '</strong><div class="subtle">' + _esc(item.desc) + '</div></div><span class="pill ' + item.tone + '">' + _esc(item.badge) + '</span></div>';
        }).join('');
    }

    function _renderListManagementDetail(tasks, accounts, assets, providers, config) {
        var detailItems = document.querySelectorAll('#detailHost .detail-item strong');
        if (detailItems.length >= 3) {
            detailItems[0].textContent = config.mode === 'operations' ? (tasks.length + ' 项排期运行中') : config.mode === 'orders' ? ((tasks.length + accounts.length) + ' 笔订单进入视图') : config.mode === 'service' ? (tasks.length + ' 个工单来源已同步') : (tasks.length + ' 笔退款记录已接入');
            detailItems[1].textContent = tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'failed'; }).length + ' 项需关注';
            detailItems[2].textContent = '账号 ' + accounts.length + ' / 素材 ' + assets.length + ' / 供应商 ' + providers.length;
        }
        var boardList = document.querySelector('#detailHost .board-list');
        if (boardList) {
            boardList.innerHTML = _listManagementRecords(tasks, accounts, assets, providers, config).slice(0, 3).map(function (record, index) {
                var label = config.mode === 'orders' ? ('订单建议 ' + (index + 1)) : config.mode === 'service' ? ('响应建议 ' + (index + 1)) : config.mode === 'refund' ? ('审批建议 ' + (index + 1)) : ('协调建议 ' + (index + 1));
                return '<article class="board-card"><strong>' + _esc(label) + '</strong><div class="subtle">' + _esc(record.desc || record.title) + '</div><div class="status-strip"><span class="pill ' + record.tone + '">' + _esc(record.badge) + '</span></div></article>';
            }).join('');
        }
    }

    function _taskStatusLabel(status) {
        return {
            pending: '待执行',
            running: '运行中',
            paused: '已暂停',
            completed: '已完成',
            failed: '任务失败',
        }[_normalizeTaskStatus(status)] || '待执行';
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
            publish: '内容发布',
            interact: '互动运营',
            scrape: '数据采集',
            report: '报表生成',
            maintenance: '运维监控',
        }[String(type || '').toLowerCase()] || '综合任务';
    }

    function _normalizeTaskStatus(status) {
        var value = String(status || '').toLowerCase();
        if (value === 'running' || value === '进行中') return 'running';
        if (value === 'paused' || value === '已暂停') return 'paused';
        if (value === 'completed' || value === '已完成' || value === 'done') return 'completed';
        if (value === 'failed' || value === '异常' || value === 'task_failed') return 'failed';
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
        if (regions.length) topics.push(regions[0] + ' 收纳');
        if ((assetStats.byType || {}).video) topics.push('短视频对比');
        if ((assetStats.byType || {}).image) topics.push('封面优化');
        if ((assetStats.byType || {}).text) topics.push('高意图文案');
        topics.push('低竞争切口');
        return topics.slice(0, 5);
    }

    function _setAffinityBar(row, width, label) {
        var span = row.querySelector('span');
        var bar = row.querySelector('i');
        if (span) span.textContent = label;
        if (bar) bar.style.width = width + '%';
    }

    // AI generation helpers moved to page-loaders/ai-generation-main.js.

    function ensurePagination(root, summaryText) {
        if (!root || root.querySelector('.pagination')) return;
        root.insertAdjacentHTML('beforeend', '<div class="list-footer"><div class="pagination"><div class="pagination__info">' + _esc(summaryText || '当前页 1 / 1') + '</div><div class="pagination__actions"><button class="secondary-button" type="button">上一页</button><button class="secondary-button" type="button">下一页</button></div></div></div>');
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
                control.innerHTML = '<label class="config-toggle ' + (meta.value ? 'is-on' : '') + '"><input type="checkbox" data-setting-key="' + _esc(meta.key) + '" ' + (meta.value ? 'checked' : '') + '><span class="config-toggle__track"></span><span class="config-toggle__label">' + (meta.value ? '开' : '关') + '</span></label>';
                var checkbox = control.querySelector('input[type="checkbox"]');
                if (checkbox) {
                    checkbox.addEventListener('change', function () {
                        var toggle = checkbox.closest('.config-toggle');
                        if (toggle) toggle.classList.toggle('is-on', checkbox.checked);
                        var text = control.querySelector('.config-toggle__label');
                        if (text) text.textContent = checkbox.checked ? '开' : '关';
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
        document.querySelectorAll('#mainHost .config-form-group').forEach(function (group, index) {
            if (group.querySelector('.config-section__footer')) return;
            group.insertAdjacentHTML('beforeend', '<div class="config-section__footer"><span class="subtle">当前分组 ' + (index + 1) + ' / ' + document.querySelectorAll('#mainHost .config-form-group').length + '</span><div class="pagination__actions"><button class="secondary-button" type="button">上一组</button><button class="secondary-button" type="button">下一组</button></div></div>');
        });
    }

    function _updateSettingsSummary(settings, theme, version) {
        var detailItems = document.querySelectorAll('#detailHost .detail-item strong');
        if (detailItems.length >= 3) {
            detailItems[0].textContent = '系统设置 / v' + (version.version || '-');
            detailItems[1].textContent = _countSettingsDrafts() + ' 项待保存';
            detailItems[2].textContent = settings.last_saved_at || '尚未记录';
        }
        var statusCards = document.querySelectorAll('#statusRight .status-chip, .status-meta .status-chip');
        if (statusCards.length) {
            statusCards[0].textContent = theme === 'dark' ? '深色主题' : '浅色主题';
        }
        var sidebar = document.querySelector('#sidebarSummaryCopy, .sidebar-summary p');
        if (sidebar) {
            sidebar.textContent = '当前主题 ' + (theme === 'dark' ? '深色' : '浅色') + '，已接入真实配置读写。';
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
                showToast('已恢复推荐配置，点击保存后生效', 'info');
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
        button.textContent = '保存中…';
        Promise.all(promises).then(function () {
            var now = _nowStamp();
            return api.settings.set('last_saved_at', now).then(function () { return now; });
        }).then(function (now) {
            showToast('系统设置已保存', 'success');
            var detailItems = document.querySelectorAll('#detailHost .detail-item strong');
            if (detailItems.length >= 3) {
                detailItems[1].textContent = '0 项待保存';
                detailItems[2].textContent = now;
            }
            applyTheme(values.theme || oldTheme);
        }).catch(function (err) {
            showToast('保存设置失败: ' + err.message, 'error');
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
                if (label) label.textContent = control.checked ? '开' : '关';
            } else {
                control.value = values[key];
            }
        });
    }

    function _settingsFieldMeta(label, settings, theme) {
        var mapping = {
            '界面语言': { key: 'ui.language', type: 'select', value: settings['ui.language'] || '简体中文', options: ['简体中文', 'English'] },
            '时区': { key: 'ui.timezone', type: 'select', value: settings['ui.timezone'] || 'UTC+8 (亚洲/上海)', options: ['UTC+8 (亚洲/上海)', 'UTC+0 (UTC)', 'UTC-5 (America/New_York)'] },
            '默认货币': { key: 'business.currency', type: 'select', value: settings['business.currency'] || 'USD ($)', options: ['USD ($)', 'CNY (¥)', 'EUR (€)'] },
            '启动时自动检查更新': { key: 'update.auto_check', type: 'toggle', value: (settings['update.auto_check'] || '1') !== '0' },
            '主题': { key: 'theme', type: 'select', value: theme === 'dark' ? 'dark' : 'light', options: ['light', 'dark'] },
            '字号': { key: 'ui.font_size', type: 'select', value: settings['ui.font_size'] || '标准 (14px)', options: ['紧凑 (13px)', '标准 (14px)', '舒适 (16px)'] },
            '紧凑模式': { key: 'ui.compact_mode', type: 'toggle', value: settings['ui.compact_mode'] === '1' },
            '代理地址': { key: 'network.proxy', type: 'input', value: settings['network.proxy'] || '' },
            '请求超时': { key: 'network.timeout_sec', type: 'select', value: settings['network.timeout_sec'] || '30 秒', options: ['15 秒', '30 秒', '60 秒'] },
            '最大并发': { key: 'network.max_concurrency', type: 'select', value: settings['network.max_concurrency'] || '5', options: ['3', '5', '8', '10'] },
            '任务完成通知': { key: 'notify.task_done', type: 'toggle', value: (settings['notify.task_done'] || '1') !== '0' },
            '异常告警': { key: 'notify.error_alert', type: 'toggle', value: (settings['notify.error_alert'] || '1') !== '0' },
            '静默时段': { key: 'notify.quiet_hours', type: 'select', value: settings['notify.quiet_hours'] || '22:00 - 08:00', options: ['关闭', '22:00 - 08:00', '00:00 - 07:00'] },
        };
        return mapping[label] || null;
    }

    function _recommendedSettings() {
        return {
            'ui.language': '简体中文',
            'ui.timezone': 'UTC+8 (亚洲/上海)',
            'business.currency': 'USD ($)',
            'update.auto_check': '1',
            theme: 'light',
            'ui.font_size': '标准 (14px)',
            'ui.compact_mode': '0',
            'network.proxy': '',
            'network.timeout_sec': '30 秒',
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
        if (n >= 10000) return (n / 10000).toFixed(1) + '万';
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
            return ['<tr><td colspan="5" style="text-align:center;padding:32px;">暂无利润分析基础数据</td></tr>'];
        }
        var counts = (conversion && conversion.counts) || {};
        return keys.slice(0, 4).map(function (regionKey, index) {
            var accountCount = regions[regionKey] || 0;
            var completed = counts.completed_tasks || 0;
            var assets = counts.assets || 0;
            var statusClass = accountCount >= 2 ? 'success' : accountCount === 1 ? 'warning' : 'error';
            var readiness = assets >= completed ? '素材已覆盖' : '素材待补齐';
            var action = accountCount >= 2 ? '继续验证' : '优先补样本';
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

    /* ══════════════════════════════════════════════
       公共工具
       ══════════════════════════════════════════════ */
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
        clone.dataset.tkopsPresetBound = '1';
        clone.dataset.tkopsFallbackBound = '1';
        clone.addEventListener('click', function (event) {
            event.preventDefault();
            event.stopPropagation();
            handler(event);
        });
    }

    /* ── 批量选择 ── */
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
                    + '<button class="danger-button js-batch-delete-btn">批量删除</button>'
                    + '<button class="ghost-button js-batch-cancel-btn">取消选择</button>';
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
            _bar.querySelector('.batch-bar__count').textContent = '已选 ' + ids.length + ' 项';
        }
        document.querySelectorAll(checkboxSelector).forEach(function (cb) {
            cb.addEventListener('change', _syncBar);
        });
    }

    function _batchDelete(ids, removeFn, entityName, loaderKey) {
        confirmModal({
            title: '批量删除' + entityName,
            message: '确定删除选中的 ' + ids.length + ' 个' + entityName + '？此操作不可恢复。',
            confirmText: '全部删除',
            tone: 'danger',
        }).then(function (ok) {
            if (!ok) return;
            var promises = ids.map(function (id) { return removeFn(id); });
            Promise.all(promises).then(function () {
                showToast(ids.length + ' 个' + entityName + '已删除');
                if (loaders[loaderKey]) loaders[loaderKey]();
            }).catch(function (err) {
                showToast('部分删除失败: ' + err.message, 'error');
                if (loaders[loaderKey]) loaders[loaderKey]();
            });
        });
    }

    /* ══════════════════════════════════════════════
       Version Upgrade 页面
       ══════════════════════════════════════════════ */
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
            if (elCurrent) elCurrent.textContent = 'v' + (d.version || '—');
            var detailCurrent = document.getElementById('detailVerCurrent');
            if (detailCurrent) detailCurrent.textContent = 'v' + (d.version || '—');
            if (elEnvInfo) {
                elEnvInfo.innerHTML =
                    '<div class="detail-item"><span class="subtle">应用版本</span><strong>v' + d.version + '</strong></div>' +
                    '<div class="detail-item"><span class="subtle">平台</span><strong>Windows</strong></div>' +
                    '<div class="detail-item"><span class="subtle">运行模式</span><strong>Desktop</strong></div>';
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
            if (elStatus) elStatus.textContent = '检查中…';
            if (elDelta) elDelta.innerHTML = '<span>正在检查…</span>';
            btnCheck.disabled = true;
            btnCheck.textContent = '检查中…';

            api.version.check().then(function (info) {
                _updateInfo = info;
                btnCheck.disabled = false;
                btnCheck.textContent = '检查更新';

                if (elLatest) elLatest.textContent = info.hasUpdate ? 'v' + info.latest : 'v' + info.current;

                if (info.hasUpdate) {
                    if (elDelta) elDelta.innerHTML = '<span style="color:var(--status-warning);">有新版本可用</span>';
                    if (elStatus) elStatus.textContent = '可更新';
                    var detailStatus = document.getElementById('detailVerStatus');
                    if (detailStatus) detailStatus.textContent = '可更新';
                    if (elStatusNote) elStatusNote.innerHTML = '<span style="color:var(--status-warning);">' + info.latest + ' 可用</span>';
                    if (elSubtitle) elSubtitle.textContent = info.tag + ' 更新日志';

                    // Render release notes (simple markdown→HTML)
                    if (elBody) {
                        var notes = (info.releaseNotes || '暂无更新说明').replace(/</g, '&lt;').replace(/>/g, '&gt;');
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
                        btnDownload.textContent = '下载更新' + sizeStr;
                    }
                    if (info.htmlUrl && btnRelease) {
                        btnRelease.style.display = '';
                        btnRelease.href = info.htmlUrl;
                    }
                } else {
                    if (elDelta) elDelta.innerHTML = '<span style="color:var(--status-success);">已是最新</span>';
                    if (elStatus) elStatus.textContent = '已是最新';
                    var detailStatus2 = document.getElementById('detailVerStatus');
                    if (detailStatus2) detailStatus2.textContent = '已是最新';
                    if (elStatusNote) elStatusNote.innerHTML = '<span style="color:var(--status-success);">无需更新</span>';
                    if (elBody) elBody.innerHTML = '<div class="update-placeholder"><span class="shell-icon">✓</span><p>当前已是最新版本，无需更新。</p></div>';
                }
            }).catch(function (err) {
                btnCheck.disabled = false;
                btnCheck.textContent = '检查更新';
                if (elStatus) elStatus.textContent = '检查失败';
                var detailStatus3 = document.getElementById('detailVerStatus');
                if (detailStatus3) detailStatus3.textContent = '检查失败';
                if (elDelta) elDelta.innerHTML = '<span style="color:var(--status-error);">检查失败</span>';
                if (typeof showToast === 'function') showToast('更新检查失败: ' + err.message, 'error');
            });
        }

        function doDownload() {
            if (!_updateInfo || !_updateInfo.downloadUrl) return;
            btnDownload.disabled = true;
            btnDownload.textContent = '准备下载…';
            if (elDlWrap) elDlWrap.style.display = '';
            if (elStatus) elStatus.textContent = '下载中';

            api.version.download(_updateInfo.downloadUrl).then(function () {
                _pollTimer = setInterval(pollProgress, 500);
            }).catch(function (err) {
                btnDownload.disabled = false;
                btnDownload.textContent = '重试下载';
                if (typeof showToast === 'function') showToast('下载启动失败: ' + err.message, 'error');
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
                    if (elStatus) elStatus.textContent = '下载完成';
                    if (elStatusNote) elStatusNote.innerHTML = '<span style="color:var(--status-success);">准备安装</span>';
                    if (typeof showToast === 'function') showToast('下载完成，可以安装更新');
                } else if (p.state === 'verifying') {
                    if (elDlPercent) elDlPercent.textContent = '校验中…';
                } else if (p.state === 'error') {
                    clearInterval(_pollTimer);
                    _pollTimer = null;
                    btnDownload.disabled = false;
                    btnDownload.textContent = '重试下载';
                    if (elStatus) elStatus.textContent = '下载失败';
                    if (typeof showToast === 'function') showToast('下载失败: ' + p.error, 'error');
                }
            });
        }

        function doApply() {
            if (typeof showConfirm === 'function') {
                showConfirm({
                    title: '安装更新',
                    message: '将启动安装程序并关闭当前应用，确认继续？',
                    confirmText: '安装并重启',
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
                if (typeof showToast === 'function') showToast('安装程序已启动，应用即将关闭…');
                setTimeout(function () { window.close(); }, 2000);
            }).catch(function (err) {
                if (typeof showToast === 'function') showToast('安装失败: ' + err.message, 'error');
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

    /* ══════════════════════════════════════════════
       统一调度入口
       ══════════════════════════════════════════════ */
    function loadRouteData(routeKey) {
        var loader = loaders[routeKey];
        if (typeof loader === 'function') {
            loader();
        }
    }

    // ── dataChanged 事件 → 自动刷新当前页 ──
    document.addEventListener('data:changed', function () {
        if (typeof currentRoute !== 'undefined' && loaders[currentRoute]) {
            loaders[currentRoute]();
        }
    });

    // ── 暴露全局 ──
    window.loadRouteData = loadRouteData;
    window._pageLoaders = loaders;
    window.__loadDashboardOverview = _loadDashboardOverview;
    window.__exportDeviceReport = _exportDeviceReport;
    window.__inspectDevices = _runDeviceInspection;
    window.__repairDevices = _runDeviceRepair;
    window.__openDeviceEnvironment = _openDeviceEnvironment;
    window.__focusDeviceDetail = function (deviceId) {
        _selectDeviceCard(deviceId, window.__devicePageData || []);
    };
    window.__exportDeviceLog = _exportDeviceLog;
    window.__pageAudits = pageAudits;
    window.__runtimeSummaryHandlers = runtimeSummaryHandlers;
})();
