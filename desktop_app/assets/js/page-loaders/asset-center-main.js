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

    var _esc = shared.esc;
    var _formatNum = shared.formatNum;

    var TYPE_LABELS = {
        image: '图片',
        video: '视频',
        audio: '音频',
        text: '字幕',
        template: '模板',
    };

    var CATEGORY_LABELS = {
        all: '全部素材',
        video: '短视频口播',
        image: '封面图片',
        audio: '音频 / 配乐',
        text: '字幕 / 文案',
        template: '模板 / 工程',
    };

    var _assetCenterState = {
        assets: [],
        stats: { total: 0, byType: {} },
        category: 'all',
        tab: 'all',
        keyword: '',
        groupTag: '',
        packKey: '',
        selectedId: null,
    };
    var _textPreviewCache = Object.create(null);
    var _videoPosterCache = Object.create(null);

    function _toNumber(value) {
        var number = parseInt(value || 0, 10);
        return Number.isFinite(number) ? number : 0;
    }

    function _normalizeType(value) {
        var type = String(value || '').toLowerCase();
        return TYPE_LABELS[type] ? type : 'image';
    }

    function _parseTags(raw) {
        return String(raw || '')
            .split(/[，,、/\s]+/)
            .map(function (item) { return item.trim(); })
            .filter(Boolean);
    }

    function _normalizePreviewText(value, limit) {
        var text = String(value || '').replace(/\r\n/g, '\n').replace(/\r/g, '\n').trim();
        if (!text) return '';
        var maxChars = _toNumber(limit) || 180;
        if (text.length > maxChars) text = text.slice(0, maxChars) + '…';
        return text;
    }

    function _toDate(value) {
        if (!value) return null;
        var date = new Date(value);
        return Number.isNaN(date.getTime()) ? null : date;
    }

    function _formatDate(value) {
        var date = _toDate(value);
        if (!date) return '-';
        var yyyy = String(date.getFullYear());
        var mm = String(date.getMonth() + 1).padStart(2, '0');
        var dd = String(date.getDate()).padStart(2, '0');
        var hh = String(date.getHours()).padStart(2, '0');
        var min = String(date.getMinutes()).padStart(2, '0');
        return yyyy + '-' + mm + '-' + dd + ' ' + hh + ':' + min;
    }

    function _isRecentUpload(asset) {
        var date = _toDate(asset.created_at);
        if (!date) return false;
        var days7 = 7 * 24 * 60 * 60 * 1000;
        return (Date.now() - date.getTime()) <= days7;
    }

    function _isNeedsReview(asset) {
        if (asset.asset_type === 'text' || asset.asset_type === 'template') return true;
        return asset.tagList.some(function (tag) {
            return /待审|待审核|需授权|未授权|review|pending/i.test(tag);
        });
    }

    function _normalizeAssets(rows) {
        return (rows || []).map(function (row) {
            var tags = _parseTags(row.tags);
            var fileSize = _toNumber(row.file_size);
            return {
                id: String(row.id || ''),
                filename: row.filename || '未命名素材',
                asset_type: _normalizeType(row.asset_type),
                file_path: row.file_path || '',
                file_size: fileSize,
                tags: row.tags || '',
                tagList: tags,
                created_at: row.created_at || '',
                account_id: row.account_id || '',
            };
        });
    }

    function _resolveTypeCounts(assets, stats) {
        var byType = {
            image: 0,
            video: 0,
            audio: 0,
            text: 0,
            template: 0,
        };
        assets.forEach(function (asset) {
            byType[asset.asset_type] = (byType[asset.asset_type] || 0) + 1;
        });
        var backendByType = (stats && stats.byType) || {};
        Object.keys(byType).forEach(function (key) {
            var backendCount = _toNumber(backendByType[key]);
            if (backendCount > 0 || byType[key] === 0) {
                byType[key] = backendCount > 0 ? backendCount : byType[key];
            }
        });
        return byType;
    }

    function _humanFileSize(size) {
        var value = _toNumber(size);
        if (value < 1024) return value + ' B';
        if (value < 1024 * 1024) return (value / 1024).toFixed(1) + ' KB';
        return (value / (1024 * 1024)).toFixed(1) + ' MB';
    }

    function _assetTags(asset) {
        var typeText = TYPE_LABELS[asset.asset_type] || '图片';
        var primaryTone = asset.asset_type === 'video' ? 'success' : asset.asset_type === 'audio' ? 'warning' : 'info';
        var tags = [{ text: typeText, tone: primaryTone }];
        if (asset.tagList.length) {
            asset.tagList.slice(0, 2).forEach(function (tag) {
                tags.push({ text: tag, tone: 'info' });
            });
        } else {
            tags.push({ text: '未打标签', tone: 'warning' });
        }
        return tags;
    }

    function _assetPreviewClass(type) {
        if (type === 'video') return 'source-thumb__preview--video';
        if (type === 'audio') return 'source-thumb__preview--audio';
        if (type === 'text') return 'source-thumb__preview--subtitle';
        return 'source-thumb__preview--image';
    }

    function _assetPreviewLabel(type) {
        if (type === 'audio') return '♫';
        if (type === 'video') return '视频';
        if (type === 'text') return '文稿';
        if (type === 'template') return '模板';
        return '图片';
    }

    function _fileUrl(filePath) {
        var raw = String(filePath || '').trim();
        if (!raw) return '';
        if (/^https?:\/\//i.test(raw) || /^file:\/\//i.test(raw)) return raw;
        var normalized = raw.replace(/\\/g, '/');
        if (/^[a-zA-Z]:\//.test(normalized)) {
            return 'file:///' + encodeURI(normalized);
        }
        if (normalized.charAt(0) === '/') {
            return 'file://' + encodeURI(normalized);
        }
        return encodeURI(normalized);
    }

    function _buildCardPreview(asset, mode) {
        mode = mode || 'card';
        var fileUrl = _fileUrl(asset.file_path);
        if (asset.asset_type === 'image' && fileUrl) {
            return '<img class="source-thumb__media js-asset-media" src="' + _esc(fileUrl) + '" alt="' + _esc(asset.filename) + '" loading="lazy">';
        }
        if (asset.asset_type === 'video' && fileUrl) {
            if (mode === 'detail') {
                return '<video class="source-thumb__media js-asset-media js-asset-video" src="' + _esc(fileUrl) + '" preload="metadata" controls muted playsinline data-preview-mode="detail" data-video-path="' + _esc(asset.file_path || '') + '"></video>';
            }
            return '<video class="source-thumb__media js-asset-media js-asset-video" src="' + _esc(fileUrl) + '" preload="auto" autoplay loop muted playsinline data-preview-mode="card" data-video-path="' + _esc(asset.file_path || '') + '"></video>';
        }
        if ((asset.asset_type === 'text' || asset.asset_type === 'template') && asset.file_path) {
            return '<div class="source-thumb__text js-asset-text-preview" data-file-path="' + _esc(asset.file_path) + '" data-fallback="文稿预览不可用">加载文稿预览...</div>';
        }
        return '';
    }

    function _fetchVideoPoster(filePath) {
        var key = String(filePath || '').trim();
        if (!key) return Promise.resolve('');
        if (_videoPosterCache[key]) return Promise.resolve(_videoPosterCache[key]);
        if (!api || !api.assets || typeof api.assets.videoPoster !== 'function') {
            return Promise.resolve('');
        }
        return api.assets.videoPoster(key).then(function (result) {
            var posterPath = String(result && result.poster_path || '').trim();
            var posterUrl = posterPath ? _fileUrl(posterPath) : '';
            _videoPosterCache[key] = posterUrl;
            return posterUrl;
        }).catch(function () {
            _videoPosterCache[key] = '';
            return '';
        });
    }

    function _hydrateVideoPosters(scopeRoot) {
        var root = scopeRoot || document;
        root.querySelectorAll('.js-asset-video').forEach(function (video) {
            if (video.dataset.posterBound === '1') return;
            video.dataset.posterBound = '1';
            var filePath = String(video.dataset.videoPath || '').trim();
            _fetchVideoPoster(filePath).then(function (posterUrl) {
                if (!posterUrl || !video.isConnected || !root.contains(video)) return;
                video.poster = posterUrl;
                video.dataset.posterUrl = posterUrl;
                var mode = String(video.dataset.previewMode || 'card');
                if (mode === 'card') {
                    try { video.currentTime = 0.001; } catch (_) {}
                    var playPromise = video.play();
                    if (playPromise && typeof playPromise.catch === 'function') {
                        playPromise.catch(function () {});
                    }
                }
            });
        });
    }

    function _fetchTextPreview(filePath) {
        var key = String(filePath || '').trim();
        if (!key) return Promise.resolve('');
        if (_textPreviewCache[key]) return Promise.resolve(_textPreviewCache[key]);
        if (!api || !api.assets || typeof api.assets.previewText !== 'function') {
            return Promise.resolve('');
        }
        return api.assets.previewText(key, 220).then(function (result) {
            var previewText = _normalizePreviewText(result && result.preview, 220);
            _textPreviewCache[key] = previewText || '';
            return _textPreviewCache[key];
        }).catch(function () {
            _textPreviewCache[key] = '';
            return '';
        });
    }

    function _hydrateTextPreviews(scopeRoot) {
        var root = scopeRoot || document;
        root.querySelectorAll('.js-asset-text-preview').forEach(function (node) {
            if (node.dataset.bound === '1') return;
            node.dataset.bound = '1';
            var filePath = String(node.dataset.filePath || '').trim();
            var fallback = String(node.dataset.fallback || '文稿预览不可用');
            _fetchTextPreview(filePath).then(function (text) {
                if (!node.isConnected || !root.contains(node)) return;
                node.textContent = text || fallback;
                node.classList.toggle('is-empty', !text);
            });
        });
    }

    function _bindMediaFallbacks(scopeRoot) {
        var root = scopeRoot || document;
        root.querySelectorAll('.js-asset-media').forEach(function (media) {
            if (media.dataset.fallbackBound === '1') return;
            media.dataset.fallbackBound = '1';
            var markMissing = function () {
                var host = media.closest('.source-thumb__preview');
                var posterUrl = String(media.dataset.posterUrl || media.poster || '').trim();
                if (posterUrl) {
                    var image = document.createElement('img');
                    image.className = media.className.replace('js-asset-video', '').trim();
                    image.src = posterUrl;
                    image.alt = '视频首帧预览';
                    image.loading = 'lazy';
                    media.replaceWith(image);
                    return;
                }
                if (host) host.classList.add('is-media-missing');
                media.remove();
            };
            media.addEventListener('error', markMissing);
            if (media.tagName === 'VIDEO') {
                var mode = String(media.dataset.previewMode || 'card');
                if (mode === 'card') {
                    media.addEventListener('loadedmetadata', function () {
                        try { media.currentTime = 0.001; } catch (_) {}
                    });
                    var playPromise = media.play();
                    if (playPromise && typeof playPromise.catch === 'function') {
                        playPromise.catch(function () {});
                    }
                }
            }
        });
    }

    function _updateAssetStats(assets, stats) {
        var cards = document.querySelectorAll('#mainHost .stat-grid .stat-card');
        var total = _toNumber(stats.total) || assets.length;
        var unboundCount = assets.filter(function (asset) { return !String(asset.account_id || '').trim(); }).length;
        var taggedCount = assets.filter(function (asset) { return asset.tagList.length > 0; }).length;
        var taggedRate = total ? Math.round(taggedCount / total * 100) : 0;
        var recentCount = assets.filter(_isRecentUpload).length;

        if (cards.length < 3) return;

        cards[0].querySelector('div:first-child .subtle').textContent = '素材库存';
        cards[0].querySelector('.stat-card__value').textContent = _formatNum(total);
        cards[0].querySelector('.stat-card__delta span').textContent = '最近上传 ' + _formatNum(recentCount);
        cards[0].querySelector('.stat-card__delta .subtle').textContent = '真实素材库存总量';

        cards[1].querySelector('div:first-child .subtle').textContent = '未绑定账号';
        cards[1].querySelector('.stat-card__value').textContent = _formatNum(unboundCount);
        cards[1].querySelector('.stat-card__delta span').textContent = '需要补充归属';
        cards[1].querySelector('.stat-card__delta .subtle').textContent = '未关联账号素材';

        cards[2].querySelector('div:first-child .subtle').textContent = '标签完善率';
        cards[2].querySelector('.stat-card__value').textContent = taggedRate + '%';
        cards[2].querySelector('.stat-card__delta span').textContent = '已打标签 ' + _formatNum(taggedCount);
        cards[2].querySelector('.stat-card__delta .subtle').textContent = '标签可检索覆盖率';
    }

    function _renderAssetCategories(byType, total, activeCategory) {
        var order = ['all', 'video', 'image', 'audio', 'text', 'template'];
        var list = document.querySelector('#mainHost .asset-category-list');
        if (!list) return;
        list.innerHTML = order.map(function (key) {
            var count = key === 'all' ? total : (byType[key] || 0);
            return '<button class="asset-category-item' + (key === activeCategory ? ' is-active' : '') + '" data-asset-type="' + key + '"><strong>' + CATEGORY_LABELS[key] + '</strong><span>' + _formatNum(count) + '</span></button>';
        }).join('');
    }

    function _renderTypeFilters(byType, total, activeCategory) {
        var order = ['all', 'video', 'image', 'text', 'audio', 'template'];
        var labels = {
            all: '全部',
            video: '视频',
            image: '图片',
            text: '字幕',
            audio: '音频',
            template: '模板',
        };
        var row = document.querySelector('#mainHost .asset-filter-row');
        if (!row) return;
        row.innerHTML = order.map(function (type) {
            var count = type === 'all' ? total : (byType[type] || 0);
            return '<span class="' + (type === activeCategory ? 'is-active' : '') + '" data-asset-type="' + type + '">' + labels[type] + ' ' + _formatNum(count) + '</span>';
        }).join('');
    }

    function _buildTabs(assets) {
        var list = [
            { key: 'all', label: '全部素材', match: function () { return true; } },
            { key: 'recent', label: '最近上传', match: _isRecentUpload },
            { key: 'review', label: '待整理', match: _isNeedsReview },
            { key: 'tagged', label: '已打标签', match: function (asset) { return asset.tagList.length > 0; } },
        ];
        list.forEach(function (item) {
            item.count = assets.filter(item.match).length;
        });
        return list;
    }

    function _renderSourceTabs(assets, activeTab) {
        var host = document.querySelector('#mainHost .source-browser-tabs');
        if (!host) return;
        var tabs = _buildTabs(assets);
        host.innerHTML = tabs.map(function (tab) {
            return '<span class="' + (tab.key === activeTab ? 'is-selected' : '') + '" data-asset-tab="' + tab.key + '">' + tab.label + ' <em>' + _formatNum(tab.count) + '</em></span>';
        }).join('');
    }

    function _renderCategoryFolders(state, typeCounts) {
        var host = document.querySelector('#mainHost .asset-category-column .workbench-side-list');
        if (!host) return;

        var tagCounter = {};
        state.assets.forEach(function (asset) {
            asset.tagList.forEach(function (tag) {
                tagCounter[tag] = (tagCounter[tag] || 0) + 1;
            });
        });

        var topTags = Object.keys(tagCounter)
            .map(function (tag) { return { key: tag, count: tagCounter[tag] }; })
            .sort(function (a, b) { return b.count - a.count; })
            .slice(0, 3);

        var cards = [{ key: '', title: '常用分组 · 全部', desc: '清空标签分组筛选，展示当前分类内素材。', tone: 'info' }];
        if (topTags.length) {
            cards = cards.concat(topTags.map(function (entry) {
                return {
                    key: entry.key,
                    title: '标签分组 · ' + entry.key,
                    desc: '共 ' + _formatNum(entry.count) + ' 个素材，可快速聚合复用。',
                    tone: entry.count >= 3 ? 'success' : 'info',
                };
            }));
        } else {
            cards = cards.concat([
                { key: '图片', title: '图片素材池', desc: '当前共 ' + _formatNum(typeCounts.image || 0) + ' 个图片素材。', tone: 'info' },
                { key: '视频', title: '视频素材池', desc: '当前共 ' + _formatNum(typeCounts.video || 0) + ' 个视频素材。', tone: 'success' },
                { key: '模板', title: '文本与模板', desc: '当前共 ' + _formatNum((typeCounts.text || 0) + (typeCounts.template || 0)) + ' 个待整理素材。', tone: 'warning' },
            ]);
        }

        host.innerHTML = cards.map(function (card) {
            return '<article class="workbench-sidecard js-asset-tag-group' + (state.groupTag === card.key ? ' is-selected' : '') + '" data-tag-group="' + _esc(card.key) + '"><strong>' + _esc(card.title) + '</strong><div class="subtle">' + _esc(card.desc) + '</div><span class="pill ' + card.tone + '">' + _esc(card.key ? '筛选' : '默认') + '</span></article>';
        }).join('');
    }

    function _renderPackRecommendations(state) {
        var host = document.querySelector('#mainHost .asset-pack-grid');
        if (!host) return;
        var assets = state.assets || [];
        var cards = [
            { key: 'recent', title: '最近上传素材包', desc: '近 7 天上传素材，便于快速回看新资源。', count: assets.filter(_isRecentUpload).length, tone: 'info' },
            { key: 'large', title: '大文件素材包', desc: '文件 >= 5MB，建议优先做压缩与转码。', count: assets.filter(function (asset) { return _toNumber(asset.file_size) >= 5 * 1024 * 1024; }).length, tone: 'warning' },
            { key: 'unbound', title: '待关联账号素材', desc: '未绑定账号素材，避免后续链路无法追溯。', count: assets.filter(function (asset) { return !String(asset.account_id || '').trim(); }).length, tone: 'error' },
            { key: 'tagged', title: '已打标签素材', desc: '标签齐全的素材更适合批量检索复用。', count: assets.filter(function (asset) { return asset.tagList.length > 0; }).length, tone: 'success' },
        ]
            .sort(function (a, b) { return b.count - a.count; })
            .slice(0, 3)
            .concat([{ key: '', title: '清空推荐筛选', desc: '恢复当前分类与标签页筛选结果。', count: 0, tone: 'info' }]);

        host.innerHTML = cards.map(function (card) {
            var active = state.packKey === card.key;
            return '<article class="strip-card js-asset-pack' + (active ? ' is-selected' : '') + '" data-pack-key="' + _esc(card.key) + '"><strong>' + _esc(card.title) + '</strong><div class="subtle">' + _esc(card.desc) + '</div><span class="pill ' + card.tone + '">' + _formatNum(card.count) + ' 项</span></article>';
        }).join('');
    }

    function _matchPack(asset, packKey) {
        if (!packKey) return true;
        if (packKey === 'recent') return _isRecentUpload(asset);
        if (packKey === 'large') return _toNumber(asset.file_size) >= 5 * 1024 * 1024;
        if (packKey === 'unbound') return !String(asset.account_id || '').trim();
        if (packKey === 'tagged') return asset.tagList.length > 0;
        return true;
    }

    function _buildAssetThumb(asset, isSelected) {
        var tags = _assetTags(asset);
        var searchText = [
            asset.filename,
            asset.file_path,
            asset.asset_type,
            asset.tags,
        ].join(' ');
        return '<article class="source-thumb' + (isSelected ? ' is-selected' : '') + '" data-id="' + _esc(asset.id) + '" data-search="' + _esc(searchText) + '">'
            + '<div class="source-thumb__preview ' + _assetPreviewClass(asset.asset_type) + '">'
            + _buildCardPreview(asset, 'card')
            + '<span class="source-thumb__preview-label">' + _esc(_assetPreviewLabel(asset.asset_type)) + '</span>'
            + (asset.asset_type === 'video' ? '<span class="source-thumb__dur">' + _humanFileSize(asset.file_size) + '</span>' : '')
            + '</div>'
            + '<div class="source-thumb__name">' + _esc(asset.filename) + '</div>'
            + '<div class="subtle">' + _esc(asset.file_path || '未记录路径') + '</div>'
            + '<div class="source-thumb__tag">' + tags.map(function (tag) { return '<span class="pill ' + tag.tone + '">' + _esc(tag.text) + '</span>'; }).join('') + '</div></article>';
    }

    function _renderAssetDetail(asset) {
        var preview = document.querySelector('#detailHost .source-mini-preview');
        var detailLabels = document.querySelectorAll('#detailHost .detail-item .subtle');
        var detailValues = document.querySelectorAll('#detailHost .detail-item strong');

        if (detailLabels.length >= 3) {
            detailLabels[0].textContent = '素材类型';
            detailLabels[1].textContent = '素材标签';
            detailLabels[2].textContent = '入库时间';
        }

        if (!asset) {
            if (preview) {
                preview.innerHTML = '<div class="source-thumb__preview source-thumb__preview--image">无</div><div><strong>暂无素材</strong><div class="subtle">当前筛选条件下没有可展示素材。</div></div>';
            }
            if (detailValues.length >= 3) {
                detailValues[0].textContent = '-';
                detailValues[1].textContent = '-';
                detailValues[2].textContent = '-';
            }
            return;
        }

        if (preview) {
            preview.innerHTML = '<div class="source-thumb__preview ' + _assetPreviewClass(asset.asset_type) + '">'
                + _buildCardPreview(asset, 'detail')
                + '<span class="source-thumb__preview-label">' + _esc(_assetPreviewLabel(asset.asset_type)) + '</span>'
                + '</div>'
                + '<div><strong>' + _esc(asset.filename) + '</strong><div class="subtle">' + _esc(asset.file_path || '未记录路径') + '</div></div>';
            _hydrateVideoPosters(preview);
            _bindMediaFallbacks(preview);
            _hydrateTextPreviews(preview);
        }

        if (detailValues.length >= 3) {
            detailValues[0].textContent = (TYPE_LABELS[asset.asset_type] || asset.asset_type) + ' / ' + _humanFileSize(asset.file_size);
            detailValues[1].textContent = asset.tagList.length ? asset.tagList.join(' / ') : '未打标签';
            detailValues[2].textContent = _formatDate(asset.created_at);
        }
    }

    function _renderAssetActions(asset) {
        var actionHost = document.querySelector('#detailHost .workbench-side-list');
        if (!actionHost) return;

        if (!asset) {
            actionHost.innerHTML = '<article class="workbench-sidecard"><strong>素材操作</strong><div class="subtle">请先在左侧选择一个素材。</div></article>';
            return;
        }

        var tagText = asset.tagList.length ? asset.tagList.join(' / ') : '未打标签';
        actionHost.innerHTML = ''
            + '<article class="workbench-sidecard"><strong>素材操作</strong><div class="subtle">选中素材后可直接编辑、删除与标签维护。</div>'
            + '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:8px;">'
            + '<button class="secondary-button js-edit-asset" data-id="' + _esc(asset.id) + '">编辑素材信息</button>'
            + '<button class="danger-button js-delete-asset" data-id="' + _esc(asset.id) + '">删除素材</button>'
            + '</div></article>'
            + '<article class="workbench-sidecard asset-current-summary"><strong>当前素材摘要</strong>'
            + '<div class="asset-summary-grid">'
            + '<div class="asset-summary-item"><span>类型</span><strong>' + _esc(TYPE_LABELS[asset.asset_type] || asset.asset_type) + '</strong></div>'
            + '<div class="asset-summary-item"><span>大小</span><strong>' + _esc(_humanFileSize(asset.file_size)) + '</strong></div>'
            + '<div class="asset-summary-item"><span>标签</span><strong>' + _esc(tagText) + '</strong></div>'
            + '<div class="asset-summary-item"><span>入库时间</span><strong>' + _esc(_formatDate(asset.created_at)) + '</strong></div>'
            + '</div></article>';

        actionHost.querySelectorAll('.js-edit-asset').forEach(function (btn) {
            btn.addEventListener('click', function () {
                if (typeof openAssetForm === 'function') {
                    openAssetForm(asset);
                }
            });
        });

        actionHost.querySelectorAll('.js-delete-asset').forEach(function (btn) {
            btn.addEventListener('click', function () {
                confirmModal({
                    title: '删除素材',
                    message: '确定删除该素材记录？此操作不可恢复。',
                    confirmText: '删除',
                    tone: 'danger',
                }).then(function (ok) {
                    if (!ok) return;
                    api.assets.remove(asset.id).then(function () {
                        if (typeof showToast === 'function') showToast('素材已删除', 'success');
                        loaders['asset-center']();
                    }).catch(function (err) {
                        if (typeof showToast === 'function') showToast('删除失败: ' + ((err && err.message) || '未知错误'), 'error');
                    });
                });
            });
        });
    }

    function _matchKeyword(asset, keyword) {
        if (!keyword) return true;
        var text = [
            asset.filename,
            asset.file_path,
            TYPE_LABELS[asset.asset_type] || asset.asset_type,
            asset.tags,
        ].join(' ').toLowerCase();
        return text.indexOf(keyword) !== -1;
    }

    function _matchTab(asset, tabKey) {
        if (tabKey === 'recent') return _isRecentUpload(asset);
        if (tabKey === 'review') return _isNeedsReview(asset);
        if (tabKey === 'tagged') return asset.tagList.length > 0;
        return true;
    }

    function _filteredAssets(state) {
        return state.assets.filter(function (asset) {
            var passCategory = state.category === 'all' || asset.asset_type === state.category;
            var passTab = _matchTab(asset, state.tab);
            var passKeyword = _matchKeyword(asset, state.keyword);
            var passGroupTag = !state.groupTag || asset.tagList.indexOf(state.groupTag) !== -1;
            var passPack = _matchPack(asset, state.packKey);
            return passCategory && passTab && passKeyword && passGroupTag && passPack;
        });
    }

    function _currentBatchCandidates() {
        return _filteredAssets(_assetCenterState).map(function (asset) {
            return {
                id: asset.id,
                filename: asset.filename,
                asset_type: asset.asset_type,
                tags: asset.tags,
            };
        });
    }

    function _persistRouteState(state) {
        if (typeof uiState === 'undefined' || !uiState['asset-center']) return;
        uiState['asset-center'].category = state.category;
        uiState['asset-center'].tab = state.tab;
        uiState['asset-center'].keyword = state.keyword;
        uiState['asset-center'].groupTag = state.groupTag;
        uiState['asset-center'].packKey = state.packKey;
        uiState['asset-center'].selectedId = state.selectedId;
    }

    function _renderGrid(state) {
        var grid = document.querySelector('#mainHost .asset-source-grid');
        if (!grid) return;
        var filtered = _filteredAssets(state);
        if (!filtered.length) {
            grid.innerHTML = '<div class="empty-state" style="padding:32px;text-align:center;grid-column:1/-1;"><p>没有匹配素材</p><p class="subtle">请调整分类、标签页或搜索关键词。</p></div>';
            _renderAssetDetail(null);
            _renderAssetActions(null);
            return;
        }

        var selectedId = state.selectedId;
        if (!selectedId || !filtered.some(function (item) { return item.id === selectedId; })) {
            selectedId = filtered[0].id;
            state.selectedId = selectedId;
            _persistRouteState(state);
        }

        grid.innerHTML = filtered.slice(0, 24).map(function (asset) {
            return _buildAssetThumb(asset, asset.id === selectedId);
        }).join('');
        _hydrateVideoPosters(grid);
        _bindMediaFallbacks(grid);
        _hydrateTextPreviews(grid);

        var selected = filtered.find(function (item) { return item.id === selectedId; }) || filtered[0];
        _renderAssetDetail(selected);
        _renderAssetActions(selected);

        grid.querySelectorAll('.source-thumb').forEach(function (thumb) {
            thumb.addEventListener('click', function () {
                var id = String(thumb.dataset.id || '');
                state.selectedId = id;
                _persistRouteState(state);
                _renderGrid(state);
            });
        });
    }

    function _bindFilterInteractions(state) {
        document.querySelectorAll('#mainHost .asset-category-item').forEach(function (btn) {
            btn.addEventListener('click', function () {
                state.category = btn.dataset.assetType || 'all';
                state.packKey = '';
                _persistRouteState(state);
                _render(state);
            });
        });

        document.querySelectorAll('#mainHost .asset-filter-row [data-asset-type]').forEach(function (chip) {
            chip.addEventListener('click', function () {
                state.category = chip.dataset.assetType || 'all';
                state.packKey = '';
                _persistRouteState(state);
                _render(state);
            });
        });

        document.querySelectorAll('#mainHost .source-browser-tabs [data-asset-tab]').forEach(function (tab) {
            tab.addEventListener('click', function () {
                state.tab = tab.dataset.assetTab || 'all';
                _persistRouteState(state);
                _render(state);
            });
        });

        document.querySelectorAll('#mainHost .js-asset-tag-group[data-tag-group]').forEach(function (card) {
            card.addEventListener('click', function () {
                state.groupTag = card.dataset.tagGroup || '';
                _persistRouteState(state);
                _render(state);
            });
        });

        document.querySelectorAll('#mainHost .js-asset-pack[data-pack-key]').forEach(function (card) {
            card.addEventListener('click', function () {
                state.packKey = card.dataset.packKey || '';
                _persistRouteState(state);
                _render(state);
            });
        });

        var searchInput = document.querySelector('#mainHost .asset-search-field input');
        if (searchInput) {
            searchInput.placeholder = '输入文件名 / 标签 / 路径关键词';
            searchInput.value = state.keyword || '';
            if (searchInput.dataset.assetSearchBound !== '1') {
                searchInput.dataset.assetSearchBound = '1';
                searchInput.addEventListener('input', function () {
                    _assetCenterState.keyword = String(searchInput.value || '').trim().toLowerCase();
                    _persistRouteState(_assetCenterState);
                    _renderGrid(_assetCenterState);
                    if (typeof applyCurrentRouteState === 'function') applyCurrentRouteState();
                });
            }
        }
    }

    function _render(state) {
        var byType = _resolveTypeCounts(state.assets, state.stats);
        var total = _toNumber(state.stats.total) || state.assets.length;

        _updateAssetStats(state.assets, state.stats);
        _renderAssetCategories(byType, total, state.category);
        _renderTypeFilters(byType, total, state.category);
        _renderSourceTabs(state.assets, state.tab);
        _renderCategoryFolders(state, byType);
        _renderPackRecommendations(state);
        _renderGrid(state);
        _bindFilterInteractions(state);
    }

    loaders['asset-center'] = function () {
        Promise.all([
            api.assets.list().catch(function () { return []; }),
            api.assets.stats().catch(function () { return { total: 0, byType: {} }; }),
        ]).then(function (results) {
            var routeState = (typeof uiState !== 'undefined' && uiState['asset-center']) ? uiState['asset-center'] : {};
            var assets = _normalizeAssets(results[0] || []);
            var stats = results[1] || { total: 0, byType: {} };

            _assetCenterState = {
                assets: assets,
                stats: stats,
                category: routeState.category || 'all',
                tab: routeState.tab || _assetCenterState.tab || 'all',
                keyword: routeState.keyword || '',
                groupTag: routeState.groupTag || '',
                packKey: routeState.packKey || '',
                selectedId: routeState.selectedId ? String(routeState.selectedId) : null,
            };

            runtimeSummaryHandlers['asset-center']({ assets: assets, stats: stats });
            _render(_assetCenterState);

            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (error) {
            console.warn('[page-loaders] asset-center load failed:', error);
            var grid = document.querySelector('#mainHost .asset-source-grid');
            if (grid) {
                grid.innerHTML = '<div class="empty-state" style="padding:32px;text-align:center;grid-column:1/-1;"><p>素材加载失败</p><p class="subtle">请稍后重试，或检查后端连接状态。</p></div>';
            }
        });
    };

    window.__assetCenterPageMain = {
        renderAssetDetail: _renderAssetDetail,
        buildAssetThumb: _buildAssetThumb,
        getBatchCandidates: _currentBatchCandidates,
    };
})();
