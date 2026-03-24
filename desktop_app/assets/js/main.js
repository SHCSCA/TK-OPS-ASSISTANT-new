/* ═══════════════════════════════════════════════
   Global Error Boundary
   ═══════════════════════════════════════════════ */
const __frontendLogState = {
    lastSig: '',
    lastAt: 0,
};

function frontendLog(level, event, data) {
    const entry = {
        ts: new Date().toISOString(),
        level: level || 'info',
        event: event || 'frontend.event',
        route: typeof currentRoute !== 'undefined' ? currentRoute : '',
        data: data || {},
    };
    const sig = (entry.level || '') + '|' + (entry.event || '') + '|' + JSON.stringify(entry.data || {});
    const now = Date.now();
    if (sig === __frontendLogState.lastSig && (now - __frontendLogState.lastAt) < 800) {
        return;
    }
    __frontendLogState.lastSig = sig;
    __frontendLogState.lastAt = now;

    if (typeof window.onBackendReady === 'function') {
        window.onBackendReady(function (be) {
            if (be && typeof be.logFrontend === 'function') {
                try {
                    be.logFrontend(JSON.stringify(entry));
                } catch (_) {}
            }
        });
    }
}

window.appLog = frontendLog;

window.onerror = function (msg, source, line, col, err) {
    frontendLog('error', '全局异常', {
        错误信息: String(msg || ''),
        来源: String(source || ''),
        行号: line || 0,
        列号: col || 0,
        堆栈: err && err.stack ? String(err.stack) : '',
    });
    console.error('[GlobalError]', msg, source + ':' + line + ':' + col, err);
    if (typeof showToast === 'function') {
        showToast('\u7cfb\u7edf\u5f02\u5e38\uff0c\u8bf7\u67e5\u770b\u63a7\u5236\u53f0\u65e5\u5fd7', 'error');
    }
};

window.addEventListener('unhandledrejection', function (e) {
    frontendLog('error', '异步未处理拒绝', {
        原因: e && e.reason ? String(e.reason.message || e.reason) : '未知',
    });
    console.error('[UnhandledRejection]', e.reason);
    if (typeof showToast === 'function') {
        showToast('\u5f02\u6b65\u64cd\u4f5c\u5931\u8d25\uff0c\u8bf7\u91cd\u8bd5', 'error');
    }
});

function _escShellText(value) {
    var text = String(value == null ? '' : value);
    var doubleQuote = String.fromCharCode(34);
    var singleQuote = String.fromCharCode(39);
    var singleQuoteEntity = '&' + '#39;';
    text = text.split('&').join('&amp;');
    text = text.split('<').join('&lt;');
    text = text.split('>').join('&gt;');
    text = text.split(doubleQuote).join('&quot;');
    text = text.split(singleQuote).join(singleQuoteEntity);
    return text;
}

function setShellRouteSummary(summary) {
    uiState.shellRuntime.routeSummary = summary || null;
    renderShellRuntimeSummary();
}

function clearShellRouteSummary() {
    uiState.shellRuntime.routeSummary = null;
    renderShellRuntimeSummary();
}

function setShellSystemStatus(key, value) {
    if (!uiState.shellRuntime || !uiState.shellRuntime.systemStatus) return;
    uiState.shellRuntime.systemStatus[key] = value;
    uiState.shellRuntime[key] = value;
    renderShellRuntimeSummary();
}

function _routeStaticSummary(routeKey) {
    const route = routes[routeKey] || {};
    return {
        eyebrow: route.sidebarSummary && route.sidebarSummary.eyebrow ? route.sidebarSummary.eyebrow : '',
        title: route.sidebarSummary && route.sidebarSummary.title ? route.sidebarSummary.title : '',
        copy: route.sidebarSummary && route.sidebarSummary.copy ? route.sidebarSummary.copy : '',
        statusLeft: Array.isArray(route.statusLeft) ? route.statusLeft.slice() : [],
        statusRight: Array.isArray(route.statusRight) ? route.statusRight.slice() : [],
    };
}

function _buildShellDefaultSummary(snapshot) {
    const stats = snapshot && snapshot.dashboard ? snapshot.dashboard : {};
    const notifications = snapshot && snapshot.notifications ? snapshot.notifications : (uiState.shellRuntime.notifications || []);
    const license = snapshot && snapshot.license ? snapshot.license : null;
    const update = snapshot && snapshot.update ? snapshot.update : null;
    const onboarding = snapshot && snapshot.onboarding ? snapshot.onboarding : null;

    const accountTotal = stats.accounts ? (stats.accounts.total || 0) : 0;
    const taskTotal = stats.tasks ? (stats.tasks.total || 0) : 0;
    const deviceTotal = stats.devices ? (stats.devices.total || 0) : 0;
    const failedTasks = stats.tasks && stats.tasks.byStatus ? (stats.tasks.byStatus.failed || 0) : 0;
    const unread = Array.isArray(notifications) ? notifications.length : ((notifications && notifications.unread) || 0);

    let licenseText = '许可证未激活';
    let licenseTone = 'warning';
    if (license && license.activated) {
        const tier = String(license.tier || 'free').toUpperCase();
        licenseText = license.days_remaining != null ? ('许可证 ' + tier + ' · 剩余 ' + license.days_remaining + ' 天') : ('许可证 ' + tier);
        licenseTone = 'success';
    }

    let updateText = '版本检查中';
    let updateTone = 'warning';
    if (update && update.state === 'latest') {
        updateText = '已是最新版本';
        updateTone = 'success';
    } else if (update && update.state === 'available') {
        updateText = '发现新版本 v' + (update.latest || '');
        updateTone = 'info';
    } else if (update && update.state === 'error') {
        updateText = '更新检查失败';
        updateTone = 'warning';
    }

    const onboardingText = onboarding && onboarding.completed ? '初始化完成' : '待完成初始化';
    const onboardingTone = onboarding && onboarding.completed ? 'success' : 'warning';

    return {
        eyebrow: '系统状态',
        title: failedTasks > 0 ? ('当前有 ' + failedTasks + ' 个异常任务待处理') : '系统运行稳定',
        copy: '账号 ' + accountTotal + ' / 任务 ' + taskTotal + ' / 设备 ' + deviceTotal + ' / 通知 ' + unread,
        statusLeft: [
            '账号总量 ' + accountTotal,
            '任务总量 ' + taskTotal,
            '设备总量 ' + deviceTotal,
        ],
        statusRight: [
            { text: licenseText, tone: licenseTone },
            { text: onboardingText, tone: onboardingTone },
            { text: updateText, tone: updateTone },
            { text: unread > 0 ? ('通知未读 ' + unread) : '通知已读', tone: unread > 0 ? 'info' : 'success' },
        ],
    };
}

function _mergeShellSummary(defaultSummary, routeSummary, systemStatus) {
    const base = Object.assign({ eyebrow: '', title: '', copy: '', statusLeft: [], statusRight: [] }, defaultSummary || {});
    const route = routeSummary || null;
    const merged = {
        eyebrow: route && route.eyebrow ? route.eyebrow : base.eyebrow,
        title: route && route.title ? route.title : base.title,
        copy: route && route.copy ? route.copy : base.copy,
        statusLeft: route && Array.isArray(route.statusLeft) && route.statusLeft.length ? route.statusLeft.slice() : (Array.isArray(base.statusLeft) ? base.statusLeft.slice() : []),
        statusRight: route && Array.isArray(route.statusRight) && route.statusRight.length ? route.statusRight.slice() : (Array.isArray(base.statusRight) ? base.statusRight.slice() : []),
    };

    const globalRight = [];
    const license = systemStatus && systemStatus.license ? systemStatus.license : null;
    const onboarding = systemStatus && systemStatus.onboarding ? systemStatus.onboarding : null;
    const update = systemStatus && systemStatus.update ? systemStatus.update : null;
    const notifications = systemStatus && systemStatus.notifications ? systemStatus.notifications : null;

    if (license) {
        if (license.activated) {
            globalRight.push({ text: '许可证 ' + String(license.tier || 'free').toUpperCase(), tone: 'success' });
        } else {
            globalRight.push({ text: '许可证未激活', tone: 'warning' });
        }
    }
    if (onboarding) {
        globalRight.push({ text: onboarding.completed ? '初始化完成' : '待完成初始化', tone: onboarding.completed ? 'success' : 'warning' });
    }
    if (update) {
        if (update.state === 'available') globalRight.push({ text: '发现新版本', tone: 'info' });
        else if (update.state === 'latest') globalRight.push({ text: '已是最新版本', tone: 'success' });
        else if (update.state === 'error') globalRight.push({ text: '更新检查失败', tone: 'warning' });
    }
    if (notifications) {
        globalRight.push({ text: notifications.unread > 0 ? ('通知未读 ' + notifications.unread) : '通知已读', tone: notifications.unread > 0 ? 'info' : 'success' });
    }

    const seen = {};
    merged.statusRight = merged.statusRight.concat(globalRight).filter(function (item) {
        const key = String(item.text || '') + '|' + String(item.tone || '');
        if (seen[key]) return false;
        seen[key] = true;
        return true;
    }).slice(0, 5);

    return merged;
}

function renderShellRuntimeSummary() {
    if (!uiState.shellRuntime) return;
    const merged = _mergeShellSummary(
        uiState.shellRuntime.defaultSummary,
        uiState.shellRuntime.routeSummary,
        uiState.shellRuntime.systemStatus,
    );
    if (typeof renderSidebarSummary === 'function') {
        renderSidebarSummary({
            eyebrow: merged.eyebrow || '',
            title: merged.title || '',
            copy: merged.copy || '',
        });
    }
    const leftHost = document.getElementById('statusLeft');
    const rightHost = document.getElementById('statusRight');
    if (leftHost) {
        leftHost.innerHTML = (merged.statusLeft || []).map(function (text) {
            return '<span class="status-text">' + _escShellText(text) + '</span>';
        }).join('');
    }
    if (rightHost) {
        rightHost.innerHTML = (merged.statusRight || []).map(function (item) {
            return '<span class="status-chip ' + _escShellText(item.tone || 'info') + '">' + _escShellText(item.text || '') + '</span>';
        }).join('');
    }

    const panel = document.getElementById('statusSummaryPanel');
    if (panel) {
        const license = uiState.shellRuntime.systemStatus.license;
        const onboarding = uiState.shellRuntime.systemStatus.onboarding;
        const notifications = uiState.shellRuntime.systemStatus.notifications;
        panel.innerHTML = '<div class="notification-panel__header"><strong>运行状态</strong></div>'
            + '<div class="detail-list">'
            + '<div class="detail-item"><span class="subtle">当前环境</span><strong>桌面工作台</strong></div>'
            + '<div class="detail-item"><span class="subtle">License</span><strong>' + _escShellText(license && license.activated ? ('已激活 / ' + String(license.tier || 'free').toUpperCase()) : '未激活') + '</strong></div>'
            + '<div class="detail-item"><span class="subtle">初始化</span><strong>' + _escShellText(onboarding && onboarding.completed ? '已完成' : '待完成') + '</strong></div>'
            + '<div class="detail-item"><span class="subtle">通知</span><strong>' + _escShellText(notifications ? ('未读 ' + (notifications.unread || 0) + ' / 总计 ' + (notifications.total || 0)) : '等待加载') + '</strong></div>'
            + '</div>';
    }
}

function _loadShellRuntimeSnapshot() {
    setShellSystemStatus('boot', { stage: 'loading', ready: false, error: '' });
    return Promise.all([
        api.dashboard.stats().catch(function () { return null; }),
        loadNotifications().catch(function () { return []; }),
        api.notifications.list().catch(function () { return []; }),
        api.license.status().catch(function () { return null; }),
        api.version.current().catch(function () { return null; }),
        api.version.check().catch(function () { return { state: 'error' }; }),
        api.settings.get('onboarding.completed').catch(function () { return '0'; }),
    ]).then(function (results) {
        const dashboard = results[0];
        const notifications = results[2] || results[1] || [];
        const license = results[3];
        const currentVersion = results[4];
        const updateInfo = results[5];
        const onboardingValue = results[6];

        const onboarding = { completed: onboardingValue === '1' };
        const update = updateInfo && updateInfo.hasUpdate
            ? { state: 'available', latest: updateInfo.latest || '', current: updateInfo.current || (currentVersion && currentVersion.version) || '' }
            : updateInfo && updateInfo.state === 'error'
                ? { state: 'error', current: (currentVersion && currentVersion.version) || '' }
                : { state: 'latest', current: (currentVersion && currentVersion.version) || '' };

        setShellSystemStatus('license', license);
        setShellSystemStatus('onboarding', onboarding);
        setShellSystemStatus('update', update);
        setShellSystemStatus('notifications', {
            total: Array.isArray(notifications) ? notifications.length : ((uiState.shellRuntime.systemStatus.notifications && uiState.shellRuntime.systemStatus.notifications.total) || 0),
            unread: (uiState.shellRuntime.systemStatus.notifications && uiState.shellRuntime.systemStatus.notifications.unread) || 0,
            hasUnread: (uiState.shellRuntime.systemStatus.notifications && uiState.shellRuntime.systemStatus.notifications.hasUnread) || false,
        });

        uiState.shellRuntime.defaultSummary = _buildShellDefaultSummary({
            dashboard: dashboard,
            notifications: uiState.shellRuntime.systemStatus.notifications,
            license: license,
            update: update,
            onboarding: onboarding,
        });
        setShellSystemStatus('boot', { stage: 'ready', ready: true, error: '' });
        renderShellRuntimeSummary();
        return {
            onboarding: onboarding,
            license: license,
            update: update,
        };
    }).catch(function (err) {
        setShellSystemStatus('boot', { stage: 'error', ready: false, error: err && err.message ? err.message : '启动状态加载失败' });
        uiState.shellRuntime.defaultSummary = _buildShellDefaultSummary({
            dashboard: null,
            notifications: [],
            license: uiState.shellRuntime.systemStatus.license,
            update: { state: 'error' },
            onboarding: uiState.shellRuntime.systemStatus.onboarding,
        });
        renderShellRuntimeSummary();
        return {
            onboarding: uiState.shellRuntime.systemStatus.onboarding || { completed: false },
        };
    });
}

function renderRoute(routeKey) {
    const route = routes[routeKey];
    if (!route) {
        frontendLog('warning', '路由不存在', { 路由键: routeKey });
        return;
    }
    // Tier 门控检查
    if (typeof canAccessRoute === 'function') {
        var access = canAccessRoute(routeKey);
        if (!access.allowed) {
            frontendLog('warning', '路由权限不足', { 路由键: routeKey, 所需等级: access.required_tier });
            currentRoute = routeKey;
            document.querySelectorAll('.nav-link[data-route]').forEach(function (b) {
                b.classList.toggle('is-active', b.dataset.route === routeKey);
            });
            if (typeof showTierBlock === 'function') showTierBlock(routeKey, access.required_tier);
            return;
        }
    }
    // 相同路由不重复渲染
    if (currentRoute === routeKey && document.getElementById('mainHost').innerHTML.length > 100) {
        frontendLog('debug', '路由重复渲染已跳过', { 路由键: routeKey });
        return;
    }
    frontendLog('info', '路由渲染', { 路由键: routeKey });
    clearShellRouteSummary();
    animateRouteTransition(routeKey);
}

function bindEvents() {
    document.getElementById('menuToggle').addEventListener('click', () => {
        document.getElementById('shellApp').classList.toggle('sidebar-collapsed');
    });

    document.getElementById('themeToggle').addEventListener('click', () => {
        applyTheme(currentTheme === 'dark' ? 'light' : 'dark');
    });

    document.querySelectorAll('.nav-link[data-route]').forEach((button) => {
        button.addEventListener('click', () => {
            frontendLog('info', '导航点击', {
                目标路由: button.dataset.route || '',
                文本: (button.textContent || '').trim(),
            });
            renderRoute(button.dataset.route);
        });
    });

    bindSearch();
    bindDetailPanelToggle();
    bindStatusSummaryToggle();
    window.addEventListener('resize', handleShellResize);

    /* ── 跨页导航：点击 [data-route-link] 元素跳转到目标路由 ── */
    document.addEventListener('click', (e) => {
        const link = e.target.closest('[data-route-link]');
        if (!link) return;
        e.preventDefault();
        const target = link.dataset.routeLink;
        if (target && routes[target]) {
            frontendLog('info', '跨页链接点击', {
                目标路由: target,
                文本: (link.textContent || '').trim(),
            });
            renderRoute(target);
            const toast = link.dataset.routeToast;
            if (toast && typeof showToast === 'function') showToast(toast);
        }
    });

    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.primary-button, .secondary-button, .chart-type-btn, .data-source-item');
        if (!btn) return;
        frontendLog('debug', '界面动作', {
            文本: (btn.textContent || '').trim().slice(0, 48),
            类名: (btn.className || '').toString().slice(0, 120),
        });
    });
}

function bindStatusSummaryToggle() {
    const btn = document.getElementById('statusSummaryToggle');
    const panel = document.getElementById('statusSummaryPanel');
    if (!btn || !panel || btn.dataset.boundStatusSummary === '1') return;
    btn.dataset.boundStatusSummary = '1';
    btn.setAttribute('aria-expanded', 'false');

    btn.addEventListener('click', (event) => {
        event.stopPropagation();
        const open = panel.classList.contains('shell-hidden');
        panel.classList.toggle('shell-hidden', !open);
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });

    document.addEventListener('click', (event) => {
        if (!event.target.closest('#statusSummaryToggle') && !event.target.closest('#statusSummaryPanel')) {
            panel.classList.add('shell-hidden');
            btn.setAttribute('aria-expanded', 'false');
        }
    });
}

let __shellResizeFrame = 0;

function handleShellResize() {
    if (__shellResizeFrame) {
        cancelAnimationFrame(__shellResizeFrame);
    }
    __shellResizeFrame = requestAnimationFrame(() => {
        __shellResizeFrame = 0;
        uiState.detailPanelForced = null;
        document.body.classList.remove('has-stale-overlay');
        document.querySelectorAll('.notification-panel.is-open').forEach((panel) => {
            panel.classList.remove('is-open');
            panel.classList.add('shell-hidden');
        });
        syncResponsiveState();
        if (typeof renderAnalyticsCanvases === 'function') {
            renderAnalyticsCanvases();
        }
    });
}

window.addEventListener('DOMContentLoaded', () => {
    frontendLog('info', '应用初始化完成', { 浏览器标识: navigator.userAgent });
    loadRecentRoutes();
    bindEvents();
    bindKeyboardShortcuts();
    bindContextMenu();
    initNotificationSystem();
    bindAgentPanel();
    initAiChat();

    uiState.shellRuntime.defaultSummary = _routeStaticSummary(currentRoute);
    renderShellRuntimeSummary();
    _loadShellRuntimeSnapshot().then(function (snapshot) {
        if (snapshot && snapshot.onboarding && snapshot.onboarding.completed) {
            renderRoute(currentRoute);
        } else {
            frontendLog('info', '首次运行，跳转初始化向导');
            renderRoute('setup-wizard');
        }
        checkLicenseOnStartup();
        checkUpdateOnStartup();
    });
});

/* ═══════════════════════════════════════════════
   启动更新检查（静默后台检查，有更新才 Toast 通知）
   ═══════════════════════════════════════════════ */
function checkUpdateOnStartup() {
    // Delay 3s to not block startup
    setTimeout(function () {
        api.version.check().then(function (info) {
            if (info && info.hasUpdate) {
                setShellSystemStatus('update', {
                    state: 'available',
                    latest: info.latest,
                    current: info.current,
                    tag: info.tag,
                });
                frontendLog('info', '发现可用更新', {
                    当前版本: info.current,
                    最新版本: info.latest,
                    标签: info.tag,
                });
                if (typeof showToast === 'function') {
                    showToast('发现新版本 v' + info.latest + '，前往「版本升级」页面更新', 'info', 8000);
                }
            }
            setShellSystemStatus('update', {
                state: info && info.current ? 'latest' : 'latest',
                current: info && info.current ? info.current : '',
            });
        }).catch(function (err) {
            setShellSystemStatus('update', { state: 'error', error: err && err.message ? err.message : '未知错误' });
            frontendLog('warning', '更新检查失败', {
                错误信息: err && err.message ? err.message : '未知错误',
            });
            // Silent — don't bother user if check fails at startup
        });
    }, 3000);
}

window.renderShellRuntimeSummary = renderShellRuntimeSummary;
window.setShellRouteSummary = setShellRouteSummary;
window.setShellSystemStatus = setShellSystemStatus;

/* ═══════════════════════════════════════════════
   Toast 反馈系统
   ═══════════════════════════════════════════════ */
