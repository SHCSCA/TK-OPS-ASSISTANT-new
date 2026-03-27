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
            var byType = stats.byType || {};
            var reviewCount = (byType.text || 0) + (byType.template || 0);
            var reusable = total ? Math.round(((byType.video || 0) + (byType.image || 0)) / total * 100) : 0;
            _applyRuntimeSummary({
                eyebrow: '素材提醒',
                title: total ? ('素材库存 ' + total + ' 项') : '暂无素材库存',
                copy: '待整理 ' + reviewCount + ' / 图片视频占比 ' + reusable + '%',
                statusLeft: ['素材总量 ' + total, '待整理素材 ' + reviewCount, '图片/视频占比 ' + reusable + '%'],
                statusRight: [
                    { text: total ? '库存已加载' : '等待上传素材', tone: total ? 'success' : 'warning' },
                    { text: reviewCount ? ('待整理 ' + reviewCount) : '已整理', tone: reviewCount ? 'warning' : 'info' },
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
        if (s === 'active' || s === 'online' || s === '在线') return 'online';
        if (s === 'idle' || s === 'offline' || s === '离线') return 'offline';
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
        wireHeaderPrimary: _wireHeaderPrimary,
        bindBatchBar: _bindBatchBar,
        batchDelete: _batchDelete,
        buildAccountViewModel: _buildAccountViewModel,
        buildAccountSearchText: _buildAccountSearchText,
        buildAccountAdvice: _buildAccountAdvice,
        buildAccountDutySummary: _buildAccountDutySummary,
        findAccountViewModel: _findAccountViewModel,
        splitAccountTags: _splitAccountTags,
        mergeAccountTags: _mergeAccountTags,
        accountFilterStatus: _accountFilterStatus,
        accountSortOrder: _accountSortOrder,
        accountPlatformLabel: _accountPlatformLabel,
        accountRegionLabel: _accountRegionLabel,
        openAccountEnvironment: _openAccountEnvironment,
        openAccountProxyConfig: _openAccountProxyConfig,
        openAccountCookieModal: _openAccountCookieModal,
        runAccountConnectionTest: _runAccountConnectionTest,
        runAccountLoginValidation: _runAccountLoginValidation,
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
        }).catch(function (e) {
            window.__devicePageData = [];
            window.__devicePageAccounts = [];
            console.warn('[page-loaders] device-management load failed:', e);
        });
    };

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
            };
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

    function _runDeviceInspection(deviceIds) {
        var models = window.__devicePageData || [];
        var targets = Array.isArray(deviceIds) && deviceIds.length ? models.filter(function (item) { return deviceIds.indexOf(item.id) >= 0; }) : models;
        return Promise.all((targets || []).map(function (item) {
            return api.devices.inspect(item.id);
        })).then(function (results) {
            var abnormal = (results || []).filter(function (item) { return item && item.status === 'error'; }).length;
            var warnings = (results || []).filter(function (item) { return item && item.status === 'warning'; }).length;
            var idle = (results || []).filter(function (item) { return item && item.status === 'idle'; }).length;
            showToast('已完成 ' + results.length + ' 台设备巡检，异常 ' + abnormal + ' 台，告警 ' + warnings + ' 台，空闲 ' + idle + ' 台', abnormal || warnings ? 'warning' : 'success');
            if (uiState['device-management']) {
                var firstProblem = (results || []).find(function (item) { return item && (item.status === 'error' || item.status === 'warning'); });
                if (firstProblem) uiState['device-management'].selectedId = firstProblem.device_id;
            }
            loaders['device-management']();
            return results;
        }).catch(function (err) {
            showToast('设备巡检失败: ' + ((err && err.message) || '未知错误'), 'error');
            throw err;
        });
    }

    function _runDeviceRepair(deviceIds) {
        var models = window.__devicePageData || [];
        var targets = Array.isArray(deviceIds) && deviceIds.length ? models.filter(function (item) { return deviceIds.indexOf(item.id) >= 0; }) : models;
        return Promise.all((targets || []).map(function (item) {
            return api.devices.repair(item.id);
        })).then(function (results) {
            var manual = (results || []).filter(function (item) {
                var actions = (item && item.actions) || [];
                return actions.some(function (action) { return String(action).indexOf('人工') >= 0; });
            }).length;
            showToast('已执行 ' + results.length + ' 台设备修复：完成状态归一、隔离 profile 准备，并记录修复日志。仍有 ' + manual + ' 台需要人工处理。', manual ? 'warning' : 'success');
            loaders['device-management']();
            return results;
        });
    }

    function _openDeviceEnvironment(deviceId) {
        if (!deviceId) {
            showToast('请先选择设备', 'warning');
            return Promise.resolve(null);
        }
        return api.devices.openEnvironment(deviceId).then(function (result) {
            showToast('已启动外部浏览器隔离实例', 'success');
            return result;
        }).catch(function (err) {
            showToast('打开环境失败: ' + ((err && err.message) || '未知错误'), 'error');
            throw err;
        });
    }

    function _exportDeviceReport() {
        var models = window.__devicePageData || [];
        var lines = [];
        models.forEach(function (item) {
            lines.push('设备：' + item.name + ' / ' + item.deviceCode);
            lines.push('状态：' + item.statusMeta.label + ' / 代理 ' + item.proxyStatusLabel + ' / 指纹 ' + item.fingerprintLabel);
            lines.push('地区：' + item.regionLabel + ' / 代理地址：' + item.proxyLabel);
            lines.push('绑定账号：' + (item.boundAccounts.length ? item.boundAccounts.map(function (account) {
                var login = account.last_login_check_status || 'unknown';
                var isolation = _deviceBool(account.isolation_enabled) ? '已隔离' : '未隔离';
                return (account.username || ('账号#' + account.id)) + ' [' + isolation + ' / 登录态 ' + login + ']';
            }).join('；') : '无'));
            lines.push('隔离覆盖：' + item.coveragePercent + '% / 最近巡检：' + item.lastInspectionLabel);
            lines.push('巡检问题：' + (item.issues.length ? item.issues.map(function (issue) { return issue.title + ' - ' + issue.copy; }).join('；') : '无'));
            lines.push('');
        });
        return _exportThroughBackend('设备环境报告', lines, '设备报告已导出');
    }

    function _exportDeviceLog(deviceId, options) {
        var config = options || {};
        var models = window.__devicePageData || [];
        var target = models.find(function (item) { return String(item.id || '') === String(deviceId || ''); });
        if (!target) {
            showToast('未找到设备日志数据', 'warning');
            return Promise.resolve(null);
        }
        return api.devices.logs(target.id).then(function (logs) {
            target.logs = logs || [];
            _renderDeviceDetail(target, target.logs);
            if (!config.silent) showToast('已切换到当前设备的日志详情', 'info');
            return logs || [];
        }).catch(function (err) {
            showToast('加载设备日志失败: ' + ((err && err.message) || '未知错误'), 'error');
            throw err;
        });
    }

    /* ══════════════════════════════════════════════
       AI Generation 页面
       ══════════════════════════════════════════════ */
    loaders['viral-title'] = function () {
        Promise.all([
            api.providers.list().catch(function () { return []; }),
        ]).then(function (results) {
            runtimeSummaryHandlers['viral-title']({ providers: results[0] || [] });
        });
        _loadAiGenerationPage({
            routeKey: 'viral-title',
            preset: 'title-generator',
            actionText: '生成标题方案',
            inputSelector: '#mainHost .title-editor-textarea',
            triggerSelectors: ['#mainHost .page-header .primary-button', '#mainHost .title-editor-actions .primary-button'],
            beforeCall: function (input) {
                return '请基于以下主题生成 3 个适合 TikTok Shop 的爆款标题方案，并简要说明适用场景：\n' + input;
            },
            renderResult: function (result, input) {
                var variants = _extractAiItems(result.content, 3);
                _renderVariantList('#mainHost .variant-list', variants, '方案');
                var metricCards = document.querySelectorAll('#mainHost .title-metric-grid .mini-metric-card');
                if (metricCards.length >= 3) {
                    metricCards[0].querySelector('strong').textContent = _calcTitleScore(variants[0] || input) + ' / 10';
                    metricCards[0].querySelector('small').textContent = '基于当前输出长度与钩子密度估算';
                    metricCards[1].querySelector('strong').textContent = String(Math.min(98, 72 + Math.max(0, result.total_tokens || 0) / 8)).slice(0, 2) + '%';
                    metricCards[1].querySelector('small').textContent = '供应商：' + (result.provider || '-');
                    metricCards[2].querySelector('strong').textContent = Math.min(99, 78 + variants.length * 5) + '%';
                    metricCards[2].querySelector('small').textContent = '耗时 ' + _formatElapsed(result.elapsed_ms) + ' / ' + (result.model || '-');
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
                        textarea.value = templateName + '｜' + textarea.value;
                    });
                });
            },
        });
    };

    loaders['product-title'] = function () {
        Promise.all([
            api.providers.list().catch(function () { return []; }),
        ]).then(function (results) {
            runtimeSummaryHandlers['product-title']({ providers: results[0] || [] });
        });
        _loadAiGenerationPage({
            routeKey: 'product-title',
            preset: 'seo-optimizer',
            actionText: '优化商品标题',
            inputSelector: '#mainHost .product-input-row input',
            triggerSelectors: ['#mainHost .page-header .primary-button', '#mainHost .product-input-row .primary-button'],
            beforeCall: function (input) {
                return '请把以下商品标题优化为 2 个版本：高转化版和 SEO 版。要求保留核心品类词，并说明推荐场景。\n商品标题：' + input;
            },
            renderResult: function (result, input) {
                var variants = _extractAiItems(result.content, 2);
                _renderVariantList('#mainHost .product-result-board .variant-list', variants, ['高转化型', 'SEO 加强型']);
                var detailItems = document.querySelectorAll('#mainHost .product-insight-grid .detail-item strong');
                if (detailItems.length >= 3) {
                    var tokens = _keywordChunks(input);
                    detailItems[0].textContent = (tokens[0] || '核心词') + ' ' + _keywordDensity(input, tokens[0]) + '%';
                    detailItems[1].textContent = (tokens[1] || '属性词') + ' ' + _keywordDensity(input, tokens[1]) + '%';
                    detailItems[2].textContent = (tokens[2] || '修饰词') + ' ' + _keywordDensity(input, tokens[2]) + '%';
                }
            },
        });
    };

    loaders['ai-copywriter'] = function () {
        Promise.all([
            api.providers.list().catch(function () { return []; }),
        ]).then(function (results) {
            runtimeSummaryHandlers['ai-copywriter']({ providers: results[0] || [] });
        });
        _loadAiGenerationPage({
            routeKey: 'ai-copywriter',
            preset: 'copywriter',
            actionText: '生成营销文案',
            inputSelector: '#mainHost .copy-settings-column textarea',
            triggerSelectors: ['#mainHost .page-header .primary-button'],
            beforeCall: function (input) {
                var toneBtn = document.querySelector('#mainHost .copy-tone-list .is-active');
                var tone = toneBtn ? toneBtn.textContent.trim() : '专业严谨';
                return '请用“' + tone + '”语气，基于以下产品信息生成 3 个文案版本，并单独给出一条风险规避建议。\n' + input;
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
        Promise.all([
            api.providers.list().catch(function () { return []; }),
        ]).then(function (results) {
            runtimeSummaryHandlers['script-extractor']({ providers: results[0] || [] });
        });
        _loadAiGenerationPage({
            routeKey: 'script-extractor',
            preset: 'script-extractor',
            actionText: '提取脚本结构',
            inputSelector: '#mainHost .extractor-url-field input',
            triggerSelectors: ['#mainHost .page-header .primary-button'],
            beforeCall: function (input) {
                return '请基于以下视频链接或描述，输出脚本时间轴、结构标签和可复用结论。\n输入：' + input;
            },
            renderResult: function (result, input) {
                _renderExtractorResult(result.content);
                var progressText = document.querySelector('#mainHost .extractor-progress-row strong');
                if (progressText) progressText.textContent = '100%';
                var progressBar = document.querySelector('#mainHost .progress-bar span');
                if (progressBar) progressBar.style.width = '100%';
                var summary = document.querySelector('#mainHost .extractor-preview-column .panel p.subtle');
                if (summary) summary.textContent = '已完成结构提取：来源 ' + input + '，模型 ' + (result.model || '-') + '，总 tokens ' + (result.total_tokens || 0) + '。';
            },
        });
    };

    /* ══════════════════════════════════════════════
       Asset Center 页面
       ══════════════════════════════════════════════ */
    loaders['asset-center'] = function () {
        _wireHeaderPrimary(function () { openAssetForm(); }, '上传素材');
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
                    grid.innerHTML = '<div class="empty-state" style="padding:32px;text-align:center;grid-column:1/-1;"><p>暂无该分类素材</p><p class="subtle">当前分类下没有可展示的素材记录</p></div>';
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

    loaders['auto-reply'] = function () { _loadTaskOpsPage({ routeKey: 'auto-reply', title: '自动回复', tableMode: 'reply' }); };
    loaders['scheduled-publish'] = function () { _loadTaskOpsPage({ routeKey: 'scheduled-publish', title: '定时发布', tableMode: 'publish' }); };
    loaders['task-hall'] = function () { _loadTaskOpsPage({ routeKey: 'task-hall', title: '任务大厅', tableMode: 'generic' }); };
    loaders['data-collector'] = function () { _loadTaskOpsPage({ routeKey: 'data-collector', title: '数据采集助手', tableMode: 'collector' }); };
    loaders['auto-like'] = function () { _loadTaskOpsPage({ routeKey: 'auto-like', title: '自动点赞', tableMode: 'interaction' }); };
    loaders['auto-comment'] = function () { _loadTaskOpsPage({ routeKey: 'auto-comment', title: '自动评论', tableMode: 'interaction' }); };
    loaders['auto-message'] = function () { _loadTaskOpsPage({ routeKey: 'auto-message', title: '自动私信', tableMode: 'interaction' }); };
    loaders['task-scheduler'] = function () { _loadTaskOpsPage({ routeKey: 'task-scheduler', title: '任务调度', tableMode: 'calendar' }); };

    loaders['video-editor'] = function () {
        Promise.all([
            api.assets.list().catch(function () { return []; }),
            api.tasks.list().catch(function () { return []; }),
        ]).then(function (results) {
            var assets = results[0] || [];
            var tasks = results[1] || [];
            _renderWorkbenchSummary([
                { label: '当前序列', value: '素材 ' + assets.length + ' 条', note: '已接入真实素材库与时间线候选。' },
                { label: '未解决阻塞', value: String(tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'failed'; }).length) + ' 个', note: '异常任务会阻塞导出与批处理。' },
                { label: '导出队列', value: String(tasks.filter(function (task) { return _normalizeTaskStatus(task.status) === 'running'; }).length) + ' 个排队', note: '运行中任务已映射为导出或处理队列。' },
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

    loaders['visual-editor'] = function () {
        Promise.all([
            api.assets.list().catch(function () { return []; }),
            api.tasks.list().catch(function () { return []; }),
        ]).then(function (results) {
            var assets = results[0] || [];
            var tasks = results[1] || [];
            var cards = document.querySelectorAll('#mainHost .stat-grid .stat-card');
            if (cards.length >= 3) {
                cards[0].querySelector('.stat-card__value').textContent = assets.length ? '1080×1920' : '待配置';
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
            _bindAssetThumbs(assets);
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
                    showToast('当前没有可复制内容', 'warning');
                    return;
                }
                if (api.utils && typeof api.utils.copyToClipboard === 'function') {
                    api.utils.copyToClipboard(text).then(function () {
                        showToast('结果已复制', 'success');
                    }).catch(function () {
                        showToast('复制失败，请重试', 'error');
                    });
                    return;
                }
                showToast('复制能力不可用', 'warning');
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
                showToast('已应用该版本到编辑区', 'success');
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
                    showToast('当前版本内容为空', 'warning');
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
            showToast('请先填写生成内容', 'warning');
            return;
        }
        var originalText = btn.textContent;
        btn.disabled = true;
        btn.textContent = (options && options.diversify) ? '重算中…' : (config.actionText || '处理中…');
        var prompt = config.beforeCall ? config.beforeCall(source) : source;
        if (options && options.diversify) {
            prompt += '\n请基于同一主题输出全新角度，避免复用已有句式。';
        }
        api.ai.chat({
            preset: config.preset,
            model: _selectedModel(),
            messages: [{ role: 'user', content: prompt }],
            temperature: 0.7,
            max_tokens: 1200,
        }).then(function (result) {
            if (config.renderResult) config.renderResult(result || {}, source);
            showToast((options && options.diversify) ? '已生成同主题新版本' : '已生成最新结果', 'success');
            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (err) {
            showToast('生成失败: ' + err.message, 'error');
        }).finally(function () {
            btn.disabled = false;
            btn.textContent = originalText;
        });
    }

    function _applyAiResultToDownstream(config, text) {
        var map = {
            'viral-title': { route: 'creative-workshop', title: '标题方案下发', task_type: 'report' },
            'product-title': { route: 'creative-workshop', title: '商品标题下发', task_type: 'report' },
            'ai-copywriter': { route: 'ai-content-factory', title: '营销文案下发', task_type: 'publish' },
            'script-extractor': { route: 'video-editor', title: '脚本结构下发', task_type: 'publish' },
        };
        var target = map[config.routeKey] || { route: 'creative-workshop', title: 'AI 结果下发', task_type: 'report' };
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
            showToast('已下发到 ' + target.route + '，可继续处理', 'success');
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

    function ensurePagination(root, summaryText) {
        if (!root || root.querySelector('.pagination')) return;
        root.insertAdjacentHTML('beforeend', '<div class="list-footer"><div class="pagination"><div class="pagination__info">' + _esc(summaryText || '当前页 1 / 1') + '</div><div class="pagination__actions"><button class="secondary-button" type="button">上一页</button><button class="secondary-button" type="button">下一页</button></div></div></div>');
    }

    function _hydrateAiSelects(providers) {
        var list = providers || [];
        var active = list.find(function (provider) {
            return provider.is_active === true || provider.is_active === 'True';
        }) || list[0] || null;
        var providerNames = list.map(function (provider) { return provider.name || '未命名供应商'; });
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
            if (label.indexOf('供应商') !== -1) {
                select.innerHTML = providerNames.length
                    ? providerNames.map(function (name) {
                        return '<option' + (active && active.name === name ? ' selected' : '') + '>' + _esc(name) + '</option>';
                    }).join('')
                    : '<option selected>未配置供应商</option>';
            }
            if (label.indexOf('模型') !== -1) {
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
            detailItems[0].textContent = detailItems[0].textContent + ' / 今日 tokens ' + totalTokens;
        }
    }

    function _renderVariantList(selector, items, labels) {
        var host = document.querySelector(selector);
        if (!host) return;
        var toneList = ['success', 'info', 'warning'];
        var list = (items || []).filter(Boolean);
        if (!list.length) list = ['暂无可展示结果'];
        host.innerHTML = list.map(function (item, index) {
            var tag = Array.isArray(labels)
                ? (labels[index] || ('Variant ' + (index + 1)))
                : ((labels || 'Variant') + ' ' + String.fromCharCode(65 + index));
            return '<article class="variant-card' + (index === 0 ? ' is-best' : '') + '">' 
                + '<div class="variant-card__head"><span class="pill ' + toneList[index % toneList.length] + '">' + _esc(tag) + '</span><strong>' + (index === 0 ? '推荐采用' : '候选版本') + '</strong></div>'
                + '<p>' + _esc(item) + '</p>'
                + '<div class="detail-actions"><button class="ghost-button js-ai-regen" type="button">同主题重算</button><button class="secondary-button js-ai-apply-next" type="button">下发到下游</button></div>'
                + '<small>' + (index === 0 ? '当前结果已按最新输入刷新。' : '可用于补充测试与渠道分发。') + '</small></article>';
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
        if (scoreNote) scoreNote.textContent = score >= 85 ? '低风险' : score >= 70 ? '中等风险' : '高风险';
        if (riskStrong.length >= 2) {
            riskStrong[0].textContent = flagged.length;
            riskStrong[1].textContent = Math.max(0, Math.min(3, flagged.length + 1));
        }
        var list = root.querySelector('.workbench-side-list');
        if (list) {
            list.innerHTML = (flagged.length ? flagged : ['当前输出未发现明显高风险词']).map(function (word) {
                return '<article class="workbench-sidecard"><strong>' + _esc(word === '当前输出未发现明显高风险词' ? word : ('风险词：' + word)) + '</strong><div class="subtle">'
                    + (word === '当前输出未发现明显高风险词' ? '建议继续人工复核利益承诺和绝对化表达。' : '建议替换为更稳妥的中性表达，再进入投放。')
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
            var cleaned = row.replace(/(\d{2}:\d{2}:\d{2})/, '').replace(/^[-*•\d\.\)\s]+/, '').trim();
            return '<div class="extractor-result-row"><span>' + _esc(ts) + '</span><div><strong>' + (cleaned.indexOf('CTA') !== -1 ? '[CTA]' : cleaned.indexOf('镜头') !== -1 ? '[视觉描述]' : '[脚本结构]') + '</strong><p>' + _esc(cleaned) + '</p></div><em>' + (96 - index * 2) + '%</em></div>';
        }).join('');
    }

    function _extractAiItems(text, limit) {
        var cleaned = String(text || '')
            .split(/\n+/)
            .map(function (line) { return line.replace(/^[-*•\d\.\)\s]+/, '').trim(); })
            .filter(function (line) { return line && line.length >= 6; });
        if (!cleaned.length) return [String(text || '').trim()];
        return cleaned.slice(0, limit || 3);
    }

    function _selectedModel() {
        var modelSelect = null;
        document.querySelectorAll('#mainHost select, #detailHost select').forEach(function (select) {
            if (!modelSelect && _fieldLabel(select).indexOf('模型') !== -1) modelSelect = select;
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
        if (value.indexOf('!') !== -1 || value.indexOf('！') !== -1) score += 0.6;
        if (/\d/.test(value)) score += 0.8;
        if (value.length >= 16 && value.length <= 28) score += 1.1;
        if (/为什么|只有|别再|立即|揭秘|必看/.test(value)) score += 0.5;
        return Math.min(9.8, Math.round(score * 10) / 10);
    }

    function _keywordChunks(text) {
        var parts = String(text || '').split(/[\s\-_/【】\[\]，,。]+/).filter(Boolean);
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
        var patterns = ['最强', '第一', '稳赚', '赚钱', '100%', '绝对', '永久', '包过'];
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
            cards[0].querySelector('.stat-card__delta .subtle').textContent = '真实素材库存总量';
            cards[1].querySelector('.stat-card__value').textContent = reviewCount;
            cards[1].querySelector('.stat-card__delta .subtle').textContent = '文本/模板素材待整理';
            cards[2].querySelector('.stat-card__value').textContent = reusable + '%';
            cards[2].querySelector('.stat-card__delta .subtle').textContent = '图片与视频素材占比';
        }
    }

    function _renderAssetCategories(byType, total) {
        var labels = {
            all: '全部素材',
            video: '短视频口播',
            image: '封面图片',
            audio: '音频 / 配乐',
            text: '字幕 / 文案',
            template: '模板 / 工程',
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
        var label = type === 'audio' ? '♫' : type === 'video' ? '视频' : type === 'text' ? '文稿' : type === 'template' ? '模板' : '图片';
        var tags = _assetTags(asset);
        return '<article class="source-thumb' + (isSelected ? ' is-selected' : '') + '" data-id="' + (asset.id || '') + '">'
            + '<div class="source-thumb__preview ' + previewClass + '">' + _esc(label) + (type === 'video' ? '<span class="source-thumb__dur">' + _humanFileSize(asset.file_size || 0) + '</span>' : '') + '</div>'
            + '<div class="source-thumb__name">' + _esc(asset.filename || '未命名素材') + '</div>'
            + '<div class="source-thumb__tag">' + tags.map(function (tag) { return '<span class="pill ' + tag.tone + '">' + _esc(tag.text) + '</span>'; }).join('') + '</div></article>';
    }

    function _assetTags(asset) {
        var type = (asset.asset_type || 'image').toLowerCase();
        var primaryTone = type === 'video' ? 'success' : type === 'audio' ? 'warning' : 'info';
        var tags = [{ text: type, tone: primaryTone }];
        if (asset.tags) {
            String(asset.tags).split(/[,，]/).slice(0, 1).forEach(function (tag) {
                if (tag.trim()) tags.push({ text: tag.trim(), tone: 'info' });
            });
        } else {
            tags.push({ text: '已入库', tone: 'success' });
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
        actionHost.innerHTML = '<article class="workbench-sidecard"><strong>素材操作</strong><div class="subtle"><button class="secondary-button js-edit-asset" data-id="' + _esc(asset.id || '') + '">编辑素材</button> <button class="danger-button js-delete-asset" data-id="' + _esc(asset.id || '') + '">删除素材</button></div></article>';
        document.querySelectorAll('.js-edit-asset').forEach(function (btn) {
            btn.addEventListener('click', function () {
                openAssetForm(asset);
            });
        });
        document.querySelectorAll('.js-delete-asset').forEach(function (btn) {
            btn.addEventListener('click', function () {
                confirmModal({
                    title: '删除素材',
                    message: '确定删除该素材记录？此操作不可恢复。',
                    confirmText: '删除',
                    tone: 'danger',
                }).then(function (ok) {
                    if (!ok) return;
                    api.assets.remove(asset.id).then(function () {
                        showToast('素材已删除', 'success');
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
                + '<div><strong>' + _esc(asset.filename || '未命名素材') + '</strong><div class="subtle">' + _esc(asset.file_path || '未记录路径') + '</div></div>';
        }
        var items = document.querySelectorAll('#detailHost .detail-item strong');
        if (items.length >= 3) {
            items[0].textContent = (asset.asset_type || 'unknown') + ' / ' + _humanFileSize(asset.file_size || 0);
            items[1].textContent = asset.tags ? String(asset.tags) : '已入库';
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
