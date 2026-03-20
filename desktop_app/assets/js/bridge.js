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
            // Groups / Devices
            listGroups: noop, createGroup: noopObj, updateGroup: noopObj, deleteGroup: noopObj,
            listDevices: noop, createDevice: noopObj, updateDevice: noopObj, deleteDevice: noopObj,
            // Tasks
            listTasks: noop, createTask: noopObj, updateTask: noopObj,
            startTask: noopObj, completeTask: noopObj, failTask: noopObj, deleteTask: noopObj,
            // AI Providers
            listProviders: noop, createProvider: noopObj,
            updateProvider: noopObj, setActiveProvider: noopObj, deleteProvider: noopObj,
            // Dashboard
            getDashboardStats: () => ok({
                accounts: { total: 0, byStatus: {} },
                tasks:    { total: 0, byStatus: {} },
                devices:  { total: 0, byStatus: {} },
                groups: 0, assets: 0, providers: 0,
            }),
            // Settings
            getSetting: () => ok(''), setSetting: noopObj, setSettingsBatch: noopObj, getAllSettings: () => ok({}),
            // Theme
            setTheme: noopObj, getTheme: () => ok('light'),
            // Version
            getAppVersion: () => ok({ version: '0.0.0' }),
            checkForUpdate: () => ok({ hasUpdate: false, current: '0.0.0' }),
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
            getRecentLogs: () => ok({ path: 'C:/TK-OPS-ASSISTANT/logs/app.log', lines: ['[2026-03-19 10:30:00] INFO     desktop_app.app  Application started'], lineCount: 1, errorCount: 0, warningCount: 0, size: 128 }),
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
