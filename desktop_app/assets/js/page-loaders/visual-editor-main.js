(function () {
    'use strict';

    var shared = window.__pageLoaderShared;
    var loaders = window._pageLoaders;
    if (!shared || !loaders) {
        throw new Error('visual editor page loader dependencies not loaded');
    }

    var _renderWorkbenchSummary = shared.renderWorkbenchSummary;
    var _renderWorkbenchSideCards = shared.renderWorkbenchSideCards;
    var _renderStripCards = shared.renderStripCards;

    function _designCanvasLabel(assets) {
        var cover = (assets || []).find(function (asset) {
            var type = String(asset.asset_type || '').toLowerCase();
            return type === 'image' || type === 'template';
        });
        if (!cover) return '待配置画布';
        if (cover.width && cover.height) return String(cover.width) + '×' + String(cover.height);
        return '1080×1920';
    }

    loaders['visual-editor'] = function () {
        Promise.all([
            api.assets.list().catch(function () { return []; }),
            api.tasks.list().catch(function () { return []; }),
        ]).then(function (results) {
            var assets = results[0] || [];
            var tasks = results[1] || [];
            document.querySelectorAll('#mainHost .workbench-summary-chip');
            var reviewCount = assets.filter(function (asset) {
                return String(asset.tags || '').indexOf('审核') >= 0;
            }).length;
            var exporting = tasks.filter(function (task) {
                return String(task.status || '').toLowerCase() === 'running';
            }).length;
            _renderWorkbenchSummary([
                { label: '当前画布', value: _designCanvasLabel(assets), note: assets.length ? '已根据真实素材画布回填' : '导入封面素材后自动更新' },
                { label: '待审稿', value: String(reviewCount || Math.max(0, assets.length - 1)) + ' 张', note: '优先检查配色、字号与模板一致性' },
                { label: '导出队列', value: String(exporting) + ' 个', note: '正在使用真实任务状态回填导出排队' },
            ]);
            _renderWorkbenchSideCards(tasks, '#mainHost .workbench-side-list');
            _renderStripCards(assets, '#mainHost .workbench-strip-grid', 'asset');
            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (error) {
            console.warn('[page-loaders] visual-editor load failed:', error);
            if (typeof showToast === 'function') {
                showToast('视觉编辑页加载失败: ' + ((error && error.message) || '未知错误'), 'error');
            }
        });
    };
})();
