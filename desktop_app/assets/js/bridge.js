/* ── backend bridge ────────────────────────────────
   Connects to Python QWebChannel bridge ("backend").
   Exposes window.backend after channel is ready.
   ─────────────────────────────────────────────── */
(function () {
    'use strict';

    let _backend = null;
    const _readyCallbacks = [];

    function onBackendReady(cb) {
        if (_backend) { cb(_backend); return; }
        _readyCallbacks.push(cb);
    }

    function _initChannel() {
        if (typeof QWebChannel === 'undefined') {
            // Running outside PySide6 (e.g. plain browser preview) – provide a stub
            _backend = _createStub();
            window.backend = _backend;
            _readyCallbacks.forEach(cb => cb(_backend));
            _readyCallbacks.length = 0;
            return;
        }
        new QWebChannel(qt.webChannelTransport, function (channel) {
            _backend = channel.objects.backend;
            window.backend = _backend;
            _readyCallbacks.forEach(cb => cb(_backend));
            _readyCallbacks.length = 0;
            console.log('[bridge] QWebChannel connected');
        });
    }

    /* Stub for browser-only preview – returns envelope format */
    function _createStub() {
        const ok = (data) => JSON.stringify({ ok: true, data: data });
        const noop = () => ok([]);
        const noopObj = () => ok({});
        return {
            // Accounts
            listAccounts: noop, getAccount: noopObj,
            createAccount: noopObj, updateAccount: noopObj, deleteAccount: noopObj,
            testAccountConnection: () => ok({ ok: false, message: '浏览器预览模式不支持连接测试', latency_ms: null, target: '' }),
            validateAccountLogin: () => ok({ status: 'unknown', label: '预览模式', message: '浏览器预览模式不支持真实登录态校验' }),
            openAccountEnvironment: () => ok({ account_id: 0, account_username: 'preview', device_id: 0, browser_path: '', profile_dir: '', extension_dir: '', extension_name: 'TKOPS Account Session', extension_ready: true, extension_install_required: false, extension_install_hint: '无需手动安装，系统会在启动隔离浏览器时自动生成并加载登录扩展。', proxy_server: '127.0.0.1:0', browser_proxy: '127.0.0.1:0', upstream_proxy: 'http://127.0.0.1:0', validation: { ok: true, message: '', detail: '' }, pid: 0, url: '', cookie_count: 0, preview: true }),
            // Groups / Devices
            listGroups: noop, createGroup: noopObj, updateGroup: noopObj, deleteGroup: noopObj,
            listDevices: noop, createDevice: noopObj, updateDevice: noopObj, deleteDevice: noopObj,
            inspectDevice: () => ok({ device_id: 0, status: 'idle', proxy_status: 'offline', message: '浏览器预览模式不支持真实设备巡检' }),
            repairDeviceEnvironment: () => ok({ device_id: 0, status: 'idle', proxy_status: 'offline', actions: ['浏览器预览模式不支持真实环境修复'] }),
            openDeviceEnvironment: () => ok({ device_id: 0, browser_path: '', profile_dir: '', proxy_server: '127.0.0.1:0', browser_proxy: '127.0.0.1:0', upstream_proxy: 'http://127.0.0.1:0', validation: { ok: true, message: '', detail: '' }, pid: 0, url: '', preview: true }),
            getDeviceLogs: noop,
            // Tasks
            listTasks: noop, createTask: noopObj, updateTask: noopObj,
            startTask: noopObj, completeTask: noopObj, failTask: noopObj, deleteTask: noopObj,
            createTaskAction: noopObj,
            // AI Providers
            listProviders: noop, createProvider: noopObj,
            updateProvider: noopObj, setActiveProvider: noopObj, deleteProvider: noopObj,
            // Assets
            listAssets: noop, listAssetsByType: noop, createAsset: noopObj, updateAsset: noopObj, deleteAsset: noopObj,
            getAssetStats: () => ok({ total: 0, byType: {} }),
            getAssetVideoPoster: () => ok({ poster_path: '', reason: 'stub' }),
            getAssetTextPreview: () => ok({ preview: '', encoding: '', reason: 'stub' }),
            // Dashboard
            getDashboardStats: () => ok({
                accounts: { total: 0, byStatus: {} },
                tasks:    { total: 0, byStatus: {} },
                devices:  { total: 0, byStatus: {} },
                groups: 0, assets: 0, providers: 0,
            }),
            getDashboardOverview: () => ok({
                range: 'today',
                stats: {
                    accounts: { total: 0, byStatus: {} },
                    tasks: { total: 0, byStatus: {} },
                    devices: { total: 0, byStatus: {} },
                    groups: 0,
                    assets: 0,
                    providers: 0,
                },
                trend: [],
                activity: [],
                systems: [],
            }),
            getAnalyticsSummary: () => ok({
                accounts: { total: 0, active: 0, by_region: {}, followers_total: 0 },
                tasks: { total: 0, completed: 0, running: 0, failed: 0 },
                assets: { total: 0, by_type: {} },
                providers: { total: 0, active: 0, models: [] },
                experiments: { projects: 0, views: 0 },
            }),
            getConversionAnalysis: () => ok({
                counts: { accounts: 0, active_accounts: 0, tasks: 0, completed_tasks: 0, assets: 0 },
                funnel: [],
            }),
            getPersonaAnalysis: () => ok({ segments: [], regions: [], interest_clusters: [] }),
            getTrafficAnalysis: () => ok({ metrics: {}, sources: [], rows: [], trend: [] }),
            getCompetitorAnalysis: () => ok({ metrics: {}, rivals: [], rows: [], bars: [] }),
            getBlueOceanAnalysis: () => ok({ metrics: {}, topics: [], lead: {}, matrix: [] }),
            getInteractionAnalysis: () => ok({ metrics: {}, sentiment: {}, keywords: [], heatmap: [], affinity: [] }),
            // Analytics / Reports / Workflows / Experiments
            listAnalysisSnapshots: noop,
            createAnalysisSnapshot: noopObj,
            listReportRuns: noop,
            createReportRun: noopObj,
            listWorkflowDefinitions: noop,
            createWorkflowDefinition: noopObj,
            listWorkflowRuns: noop,
            startWorkflowRun: noopObj,
            listExperimentProjects: noop,
            createExperimentProject: noopObj,
            listExperimentViews: noop,
            createExperimentView: noopObj,
            listNotifications: noop,
            listActivityLogs: noop,
            createActivityLog: noopObj,
            runDevSeed: () => ok({ created: 0, counts: {} }),
            // AI chat
            chatSync: () => ok({ content: '未配置 AI 供应商，请先在「AI 供应商配置」页面添加。', model: '', provider: '', prompt_tokens: 0, completion_tokens: 0, total_tokens: 0, elapsed_ms: 0 }),
            startChatStream: () => ok({ started: true }),
            pollChatStream: () => ok({ chunks: [], finished: true }),
            listAiPresets: noop,
            getAiPreset: noopObj,
            testAiProvider: noopObj,
            getAiUsageStats: () => ok({ total: { prompt: 0, completion: 0, requests: 0 }, daily: {}, by_provider: {}, by_model: {} }),
            getAiUsageToday: () => ok({ prompt: 0, completion: 0, requests: 0 }),
            // Settings
            getSetting: () => ok(''), setSetting: noopObj, setSettingsBatch: noopObj, getAllSettings: () => ok({}),
            // Theme
            setTheme: noopObj, getTheme: () => ok('light'),
            // Version
            getAppVersion: () => ok({ version: '1.2.2' }),
            checkForUpdate: () => ok({ hasUpdate: false, current: '1.2.2' }),
            startDownloadUpdate: () => ok(true),
            getDownloadProgress: () => ok({ state: 'idle', percent: 0, downloaded: 0, total: 0, speed: '', filePath: '', error: '' }),
            applyUpdate: () => ok({ ok: true, action: 'stub' }),
            // License
            getLicenseStatus: () => ok({ activated: false, machine_id: 'stub', machine_id_short: 'STUB-0000-0000-0000', compound_id: '', tier: null, expiry: null, days_remaining: null, is_permanent: false, error: '未激活' }),
            activateLicense: noopObj,
            deactivateLicense: noopObj,
            checkRouteAccess: (route) => ok({ allowed: true, required_tier: 'free', current_tier: 'pro' }),
            // Utils
            copyToClipboard: () => ok({ copied: true }),
            pickLocalFiles: () => ok([]),
            importTextFile: () => ok({ selected: false, path: '', name: '', content: '' }),
            exportTextFile: () => ok({ saved: false, path: '' }),
            exportNamedTextFile: () => ok({ saved: false, path: '' }),
            getRecentLogs: () => ok({ path: 'C:/TK-OPS-ASSISTANT/logs/app.log', lines: ['[2026-03-19 10:30:00] INFO     desktop_app.app  Application started'], lineCount: 1, errorCount: 0, warningCount: 0, size: 128 }),
            runNetworkDiagnostics: () => ok({ score: 100, checks: [], errorCount: 0, warningCount: 0, generatedAt: '', reportText: '' }),
            // Logging
            logFrontend: () => {},
            // Signals
            dataChanged: { connect: () => {} },
        };
    }

    // Expose globals
    window.onBackendReady = onBackendReady;
    window._initBridgeChannel = _initChannel;

    // Auto-init when DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', _initChannel);
    } else {
        _initChannel();
    }
})();
