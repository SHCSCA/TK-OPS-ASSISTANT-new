(function () {
    'use strict';

    var shared = window.__pageLoaderShared;
    if (!shared) {
        throw new Error('page loader shared helpers not loaded');
    }

    var loaders = window._pageLoaders;
    var runtimeSummaryHandlers = window.__runtimeSummaryHandlers;
    if (!loaders || !runtimeSummaryHandlers) {
        throw new Error('page loader registries not loaded');
    }

    var _wireHeaderPrimary = shared.wireHeaderPrimary;
    var _esc = shared.esc;
    var _formatNum = shared.formatNum;

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

    function _humanFileSize(size) {
        var value = parseInt(size || 0, 10) || 0;
        if (value < 1024) return value + ' B';
        if (value < 1024 * 1024) return (value / 1024).toFixed(1) + ' KB';
        return (value / (1024 * 1024)).toFixed(1) + ' MB';
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
        }).catch(function (error) {
            console.warn('[page-loaders] asset-center load failed:', error);
        });
    };

    window.__assetCenterPageMain = {
        renderAssetDetail: _renderAssetDetail,
        buildAssetThumb: _buildAssetThumb,
    };
})();