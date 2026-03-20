/* ── data.js ─ 前后端数据层 ─────────────────────────
   封装所有 backend 调用：统一 JSON 信封解析、错误处理、
   简单内存缓存（TTL）、dataChanged 信号自动刷新。
   暴露 window.api 供页面使用。
   ──────────────────────────────────────────────── */
(function () {
    'use strict';

    // ── 缓存 ─────────────────────────────────────
    const _cache = {};
    const DEFAULT_TTL = 30000; // 30s

    function _cacheGet(key) {
        const entry = _cache[key];
        if (!entry) return null;
        if (Date.now() > entry.expires) { delete _cache[key]; return null; }
        return entry.data;
    }
    function _cacheSet(key, data, ttl) {
        _cache[key] = { data, expires: Date.now() + (ttl || DEFAULT_TTL) };
    }
    function _cacheInvalidate(prefix) {
        Object.keys(_cache).forEach(k => { if (k.startsWith(prefix)) delete _cache[k]; });
    }

    // ── 核心调用 ──────────────────────────────────
    /**
     * callBackend(methodName, ...args)
     * 返回 Promise<data>（已解包 envelope）。
     * 如果 backend 返回 {ok:false, error:...}，reject 该 error。
     */
    function callBackend(method) {
        var args = Array.prototype.slice.call(arguments, 1);
        return new Promise(function (resolve, reject) {
            window.onBackendReady(function (be) {
                if (typeof be[method] !== 'function') {
                    if (typeof window.appLog === 'function') {
                        window.appLog('error', '后端方法不存在', { 方法名: method });
                    }
                    reject(new Error('Backend method not found: ' + method));
                    return;
                }
                try {
                    var callbackFired = false;
                    var handleResult = function(raw) {
                        if (callbackFired) return;
                        callbackFired = true;
                        try {
                            var envelope = (typeof raw === 'string') ? JSON.parse(raw) : raw;
                            if (envelope && envelope.ok === false) {
                                if (typeof window.appLog === 'function') {
                                    window.appLog('warning', '后端调用失败', { 方法名: method, 错误: envelope.error || '未知后端错误' });
                                }
                                reject(new Error(envelope.error || 'Unknown backend error'));
                            } else if (envelope && envelope.ok === true) {
                                resolve(envelope.data);
                            } else {
                                // 兼容旧格式（直接返回数据）
                                resolve(envelope);
                            }
                        } catch (e) {
                            if (typeof window.appLog === 'function') {
                                window.appLog('error', '后端响应解析失败', { 方法名: method, 错误信息: e && e.message ? e.message : '解析异常' });
                            }
                            reject(e);
                        }
                    };

                    var callArgs = args.slice();
                    // QtWebChannel requires a callback as the last argument for async returns.
                    callArgs.push(handleResult);

                    var raw = be[method].apply(be, callArgs);
                    
                    // If it's the stub, it returns a string synchronously.
                    if (raw !== undefined) {
                        if (raw && typeof raw.then === 'function') {
                            raw.then(handleResult).catch(reject);
                        } else {
                            handleResult(raw);
                        }
                    }
                } catch (e) {
                    if (typeof window.appLog === 'function') {
                        window.appLog('error', '后端调用异常', { 方法名: method, 错误信息: e && e.message ? e.message : '调用异常' });
                    }
                    if (!callbackFired) reject(e);
                }
            });
        });
    }

    /**
     * callCached(cacheKey, ttl, method, ...args)
     * 带缓存的 callBackend。
     */
    function callCached(cacheKey, ttl, method) {
        var cached = _cacheGet(cacheKey);
        if (cached !== null) return Promise.resolve(cached);
        var args = Array.prototype.slice.call(arguments, 2);
        return callBackend.apply(null, args).then(function (data) {
            _cacheSet(cacheKey, data, ttl);
            return data;
        });
    }

    // ── 高层 API ─────────────────────────────────

    var api = {
        // -- Accounts --
        accounts: {
            list: function ()        { return callCached('accounts:list', DEFAULT_TTL, 'listAccounts'); },
            get:  function (id)      { return callBackend('getAccount', String(id)); },
            create: function (data)  { return callBackend('createAccount', JSON.stringify(data)); },
            update: function (id, d) { return callBackend('updateAccount', id, JSON.stringify(d)); },
            remove: function (id)    { return callBackend('deleteAccount', id); },
        },
        // -- Groups --
        groups: {
            list:   function ()      { return callCached('groups:list', DEFAULT_TTL, 'listGroups'); },
            create: function (data)  { return callBackend('createGroup', JSON.stringify(data)); },
            update: function (id, d) { return callBackend('updateGroup', id, JSON.stringify(d)); },
            remove: function (id)    { return callBackend('deleteGroup', id); },
        },
        // -- Devices --
        devices: {
            list:   function ()      { return callCached('devices:list', DEFAULT_TTL, 'listDevices'); },
            create: function (data)  { return callBackend('createDevice', JSON.stringify(data)); },
            update: function (id, d) { return callBackend('updateDevice', id, JSON.stringify(d)); },
            remove: function (id)    { return callBackend('deleteDevice', id); },
        },
        // -- Tasks --
        tasks: {
            list:     function ()      { return callCached('tasks:list', DEFAULT_TTL, 'listTasks'); },
            create:   function (data)  { return callBackend('createTask', JSON.stringify(data)); },
            update:   function (id, d) { return callBackend('updateTask', id, JSON.stringify(d)); },
            start:    function (id)    { return callBackend('startTask', id); },
            complete: function (id)    { return callBackend('completeTask', id); },
            fail:     function (id)    { return callBackend('failTask', id); },
            remove:   function (id)    { return callBackend('deleteTask', id); },
        },
        // -- AI Providers --
        providers: {
            list:      function ()      { return callCached('providers:list', DEFAULT_TTL, 'listProviders'); },
            create:    function (data)  { return callBackend('createProvider', JSON.stringify(data)); },
            update:    function (id, d) { return callBackend('updateProvider', id, JSON.stringify(d)); },
            activate:  function (id)    { return callBackend('setActiveProvider', id); },
            remove:    function (id)    { return callBackend('deleteProvider', id); },
        },
        // -- Dashboard --
        dashboard: {
            stats: function () { return callCached('dashboard:stats', 15000, 'getDashboardStats'); },
        },
        // -- Settings --
        settings: {
            get:    function (key)       { return callBackend('getSetting', key); },
            set:    function (key, val)  { return callBackend('setSetting', key, val); },
            setBatch: function (data)    { return callBackend('setSettingsBatch', JSON.stringify(data || {})); },
            all:    function ()          { return callBackend('getAllSettings'); },
        },
        // -- Theme --
        theme: {
            get: function ()       { return callBackend('getTheme'); },
            set: function (theme)  { return callBackend('setTheme', theme); },
        },
        // -- Version / Update --
        version: {
            current:  function ()    { return callBackend('getAppVersion'); },
            check:    function ()    { return callBackend('checkForUpdate'); },
            download: function (url) { return callBackend('startDownloadUpdate', url || ''); },
            progress: function ()    { return callBackend('getDownloadProgress'); },
            apply:    function ()    { return callBackend('applyUpdate'); },
        },
        // -- License --
        license: {
            status:     function () { return callBackend('getLicenseStatus'); },
            activate:   function (key) { return callBackend('activateLicense', key); },
            issue:      function (machineId, days, tier) { return callBackend('issueLicense', machineId, Number(days || 0), tier || 'pro'); },
            verify:     function (machineId, key) { return callBackend('verifyLicenseKey', machineId, key); },
            deactivate: function () { return callBackend('deactivateLicense'); },
            checkRoute: function (route) { return callBackend('checkRouteAccess', route); },
        },
        // -- Utils --
        utils: {
            copyToClipboard: function(text) { return callBackend('copyToClipboard', text); },
            pickFiles: function () { return callBackend('pickLocalFiles'); },
            exportTextFile: function (text) { return callBackend('exportTextFile', text || ''); },
        },
        diagnostics: {
            run: function () { return callBackend('runNetworkDiagnostics'); },
        },
        // -- Logs --
        logs: {
            recent: function () { return callBackend('getRecentLogs'); },
        },
        // -- AI Chat --
        ai: {
            chat:       function (payload) { return callBackend('chatSync', JSON.stringify(payload)); },
            startStream:function (payload) { return callBackend('startChatStream', JSON.stringify(payload)); },
            poll:       function ()        { return callBackend('pollChatStream'); },
            presets:    function ()        { return callCached('ai:presets', 60000, 'listAiPresets'); },
            preset:     function (key)     { return callBackend('getAiPreset', key); },
            testProvider: function (id)    { return callBackend('testAiProvider', id); },
            usage:      function ()        { return callBackend('getAiUsageStats'); },
            usageToday: function ()        { return callBackend('getAiUsageToday'); },
        },
        // -- Assets --
        assets: {
            list:     function ()          { return callCached('assets:list', DEFAULT_TTL, 'listAssets'); },
            byType:   function (type)      { return callBackend('listAssetsByType', type); },
            create:   function (data)      { return callBackend('createAsset', JSON.stringify(data)); },
            update:   function (id, d)     { return callBackend('updateAsset', id, JSON.stringify(d)); },
            remove:   function (id)        { return callBackend('deleteAsset', id); },
            stats:    function ()          { return callCached('assets:stats', DEFAULT_TTL, 'getAssetStats'); },
        },
        // -- Utilities --
        _call: callBackend,
        _callCached: callCached,
        _invalidate: _cacheInvalidate,
    };

    // ── dataChanged 信号监听 → 自动清缓存 ─────────
    window.onBackendReady(function (be) {
        if (be.dataChanged && typeof be.dataChanged.connect === 'function') {
            be.dataChanged.connect(function (payload) {
                try {
                    var ev = JSON.parse(payload);
                    var entity = ev.entity;
                    if (entity === 'account' || entity === 'group' || entity === 'device') {
                        _cacheInvalidate('accounts:');
                        _cacheInvalidate('groups:');
                        _cacheInvalidate('devices:');
                        _cacheInvalidate('dashboard:');
                    } else if (entity === 'task') {
                        _cacheInvalidate('tasks:');
                        _cacheInvalidate('dashboard:');
                    } else if (entity === 'provider') {
                        _cacheInvalidate('providers:');
                    }
                    // 触发自定义事件，页面可监听
                    document.dispatchEvent(new CustomEvent('data:changed', { detail: ev }));
                } catch (_) {}
            });
        }
    });

    // ── 暴露全局 ─────────────────────────────────
    window.api = api;
    window.callBackend = callBackend;
})();
