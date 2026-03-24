function animateRouteTransition(routeKey) {
    const mainHost = document.getElementById('mainHost');
    const detailHost = document.getElementById('detailHost');

    // 淡出当前内容
    mainHost.classList.add('route-exit');
    detailHost.classList.add('route-exit');

    setTimeout(() => {
        showSkeleton();
        mainHost.classList.remove('route-exit');
        mainHost.classList.add('route-enter');

        setTimeout(() => {
            // 实际渲染
            const route = routes[routeKey];
            if (!route) return;

            currentRoute = routeKey;
            uiState.detailPanelForced = null;
            const shell = document.getElementById('shellApp');
            shell.className = `app-shell route-${routeKey}`;
            document.getElementById('routeEyebrow').textContent = route.eyebrow;
            document.querySelectorAll('.nav-link[data-route]').forEach((button) => {
                button.classList.toggle('is-active', button.dataset.route === routeKey);
            });

            if (route.mainTemplate) {
                setTemplateContent('mainHost', route.mainTemplate);
            } else {
                setHostHtml('mainHost', route.mainHtml);
            }

            if (route.detailTemplate) {
                setTemplateContent('detailHost', route.detailTemplate);
            } else {
                setHostHtml('detailHost', route.detailHtml);
            }
            detailHost.classList.remove('route-exit');
            document.getElementById('detailHost').classList.toggle('shell-hidden', route.hideDetailPanel === true || window.innerWidth < 1180);

            if (typeof renderShellRuntimeSummary === 'function') {
                renderShellRuntimeSummary();
            } else {
                renderSidebarSummary(route.sidebarSummary);
            }
            applyTheme(currentTheme);
            if (!(typeof renderShellRuntimeSummary === 'function')) {
                renderStatus(route);
            }
            mainHost.classList.remove('route-enter', 'skeleton-active');
            mainHost.classList.add('route-enter-active');

            bindRouteInteractions();
            bindDragAndDrop();
            bindAIConfigInteractions();
            renderCharts();
            syncResponsiveState();
            pushRecentRoute(routeKey);

            // 拉取真实后端数据注入 DOM
            if (typeof loadRouteData === 'function') loadRouteData(routeKey);

            setTimeout(() => mainHost.classList.remove('route-enter-active'), 350);
        }, 180);
    }, 120);
}

/* ═══════════════════════════════════════════════
   快捷键系统
   ═══════════════════════════════════════════════ */
