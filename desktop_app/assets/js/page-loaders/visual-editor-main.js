/* ── page-loaders/visual-editor-main.js ─ 视觉编辑器页面加载器 ──
   从 page-loaders.js 主文件拆出，注册到全局 loaders 表。
   依赖：page-loaders.js（提供 loaders 对象与共享工具函数）
         page-loaders/editor-shared.js（buildAssetThumb / bindAssetThumbs）
   ──────────────────────────────────────────────────────── */
(function () {
    'use strict';

    if (typeof window._pageLoaders === 'undefined') {
        console.warn('[visual-editor-main] _pageLoaders not ready, deferring');
        return;
    }

    window._pageLoaders['visual-editor'] = function () {
        Promise.all([
            window.api.assets.list().catch(function () { return []; }),
            window.api.tasks.list().catch(function () { return []; }),
        ]).then(function (results) {
            var assets = results[0] || [];
            var tasks  = results[1] || [];

            var cards = document.querySelectorAll('#mainHost .stat-grid .stat-card');
            if (cards.length >= 3) {
                cards[0].querySelector('.stat-card__value').textContent = assets.length ? '1080\u00d71920' : '\u5f85\u914d\u7f6e';
                cards[1].querySelector('.stat-card__value').textContent = String(Math.max(1, assets.length));
                cards[2].querySelector('.stat-card__value').textContent = String(tasks.filter(function (t) { return (t.status || '').toLowerCase() === 'running'; }).length);
            }

            if (typeof _renderWorkbenchSideCards === 'function') _renderWorkbenchSideCards(tasks, '#mainHost .workbench-side-list');
            if (typeof _renderStripCards === 'function')         _renderStripCards(assets, '#mainHost .workbench-strip-grid', 'asset');

            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (e) {
            console.warn('[page-loaders] visual-editor load failed:', e);
        });
    };

}());
