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

    // ── 首次运行检测：未完成引导 → 自动跳 setup-wizard ──
    api.settings.get('onboarding.completed').then(function (val) {
        if (val === '1') {
            renderRoute(currentRoute);
        } else {
            frontendLog('info', '首次运行，跳转初始化向导');
            renderRoute('setup-wizard');
        }
    }).catch(function () {
        renderRoute(currentRoute);
    });

    checkLicenseOnStartup();
    checkUpdateOnStartup();
});

/* ═══════════════════════════════════════════════
   启动更新检查（静默后台检查，有更新才 Toast 通知）
   ═══════════════════════════════════════════════ */
function checkUpdateOnStartup() {
    // Delay 3s to not block startup
    setTimeout(function () {
        api.version.check().then(function (info) {
            if (info && info.hasUpdate) {
                frontendLog('info', '发现可用更新', {
                    当前版本: info.current,
                    最新版本: info.latest,
                    标签: info.tag,
                });
                if (typeof showToast === 'function') {
                    showToast('发现新版本 v' + info.latest + '，前往「版本升级」页面更新', 'info', 8000);
                }
            }
        }).catch(function (err) {
            frontendLog('warning', '更新检查失败', {
                错误信息: err && err.message ? err.message : '未知错误',
            });
            // Silent — don't bother user if check fails at startup
        });
    }, 3000);
}

/* ═══════════════════════════════════════════════
   Toast 反馈系统
   ═══════════════════════════════════════════════ */
