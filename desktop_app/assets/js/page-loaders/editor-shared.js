/* ── page-loaders/editor-shared.js ─ 编辑器页面共享工具函数 ──
   视频剪辑与视觉编辑器共用的渲染辅助，由各自 main.js 调用。
   ──────────────────────────────────────────────────────── */
(function () {
    'use strict';

    window._editorShared = window._editorShared || {};

    function _esc(value) {
        return String(value == null ? '' : value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function _normalizeAssetType(asset) {
        var type = String((asset && asset.asset_type) || '').toLowerCase();
        if (type === 'text') return 'subtitle';
        if (type === 'template') return 'image';
        if (type === 'video' || type === 'image' || type === 'audio' || type === 'subtitle') return type;
        return 'image';
    }

    function _parseTags(asset) {
        return String((asset && asset.tags) || '')
            .split(/[，,、/\s]+/)
            .map(function (item) { return item.trim(); })
            .filter(Boolean);
    }

    function _typeLabel(type) {
        if (type === 'video') return '视频';
        if (type === 'image') return '图片';
        if (type === 'subtitle') return '字幕';
        if (type === 'audio') return '音频';
        return '素材';
    }

    function _fileUrl(filePath) {
        var raw = String(filePath || '').trim();
        if (!raw) return '';
        if (/^https?:\/\//i.test(raw) || /^file:\/\//i.test(raw)) return raw;
        var normalized = raw.replace(/\\/g, '/');
        if (/^[a-zA-Z]:\//.test(normalized)) return 'file:///' + encodeURI(normalized);
        if (normalized.charAt(0) === '/') return 'file://' + encodeURI(normalized);
        return encodeURI(normalized);
    }

    function _videoFallbackDataUri(filename) {
        var label = String(filename || 'VIDEO').slice(0, 20).replace(/[<>&"']/g, '');
        var svg = ''
            + '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 360">'
            + '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
            + '<stop offset="0%" stop-color="#30445d"/><stop offset="100%" stop-color="#1d2a3a"/>'
            + '</linearGradient></defs>'
            + '<rect width="640" height="360" fill="url(#g)"/>'
            + '<circle cx="320" cy="180" r="62" fill="rgba(255,255,255,0.16)"/>'
            + '<polygon points="300,146 300,214 358,180" fill="#ffffff"/>'
            + '<text x="24" y="332" font-family="Segoe UI,Arial" font-size="24" fill="#dfe8f2">' + label + '</text>'
            + '</svg>';
        return 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(svg);
    }

    function _fetchTextPreview(filePath) {
        var api = window.api;
        var key = String(filePath || '').trim();
        if (!key || !api || !api.assets || typeof api.assets.previewText !== 'function') {
            return Promise.resolve('');
        }
        return api.assets.previewText(key, 220).then(function (result) {
            return String((result && result.preview) || '').trim();
        }).catch(function () {
            return '';
        });
    }

    function _buildCardPreview(asset, mode) {
        var type = _normalizeAssetType(asset);
        var fileUrl = _fileUrl(asset && asset.file_path);
        var posterUrl = _fileUrl(asset && asset.poster_path);
        if (type === 'image' && fileUrl) {
            return '<img class="source-thumb__media js-asset-media" src="' + _esc(fileUrl) + '" alt="' + _esc(asset.filename || '图片素材') + '" loading="lazy">';
        }
        if (type === 'video' && fileUrl) {
            return '<img class="source-thumb__media js-asset-media" src="' + _esc(posterUrl || _videoFallbackDataUri(asset.filename)) + '" alt="' + _esc(asset.filename || '视频素材') + '" loading="lazy">';
        }
        if (type === 'subtitle' && fileUrl) {
            return '<div class="source-thumb__text js-asset-text-preview" data-file-path="' + _esc(fileUrl) + '" data-fallback="文稿预览不可用">加载文稿预览...</div>';
        }
        if (type === 'audio') {
            return '<span class="source-thumb__preview-label">音频</span>';
        }
        return '';
    }

    function _bindMediaFallbacks(scopeRoot) {
        var root = scopeRoot || document;
        root.querySelectorAll('.js-asset-media').forEach(function (media) {
            if (media.dataset.fallbackBound === '1') return;
            media.dataset.fallbackBound = '1';
            media.addEventListener('error', function () {
                var host = media.closest('.source-thumb__preview, .video-monitor-surface__frame');
                if (host) host.classList.add('is-media-missing');
                if (host && host.classList.contains('video-monitor-surface__frame') && !host.querySelector('.video-monitor-surface__fallback')) {
                    var fallback = document.createElement('span');
                    fallback.className = 'video-monitor-surface__fallback';
                    fallback.textContent = '预览不可用';
                    host.appendChild(fallback);
                }
                media.remove();
            });
        });
    }

    function _buildStageMedia(asset) {
        var type = _normalizeAssetType(asset);
        var fileUrl = _fileUrl(asset && asset.file_path);
        var posterUrl = _fileUrl(asset && asset.poster_path);
        if (type === 'video') {
            return ''
                + '<div class="video-monitor-surface__frame video-monitor-surface__frame--video">'
                + '<img class="video-monitor-surface__native-frame js-asset-media js-video-monitor-frame" src="' + _esc(posterUrl || _videoFallbackDataUri(asset.filename)) + '" alt="' + _esc(asset.filename || '视频素材') + '" loading="lazy">'
                + '<button class="video-monitor-surface__overlay js-video-monitor-toggle-playback" type="button">播放</button>'
                + '<span class="video-monitor-surface__status js-video-monitor-status">准备预览</span>'
                + '</div>';
        }
        if (type === 'image' && fileUrl) {
            return ''
                + '<div class="video-monitor-surface__frame video-monitor-surface__frame--image">'
                + '<img class="video-monitor-surface__image js-asset-media" src="' + _esc(fileUrl) + '" alt="' + _esc(asset.filename || '图片素材') + '" loading="lazy">'
                + '</div>';
        }
        if (type === 'subtitle' && fileUrl) {
            return ''
                + '<div class="video-monitor-surface__frame video-monitor-surface__frame--subtitle">'
                + '<div class="video-monitor-surface__subtitle js-asset-text-preview" data-file-path="' + _esc(fileUrl) + '" data-fallback="文稿预览不可用">加载文稿预览...</div>'
                + '</div>';
        }
        if (type === 'audio') {
            return ''
                + '<div class="video-monitor-surface__frame video-monitor-surface__frame--audio">'
                + '<div class="video-monitor-surface__audio">'
                + '<span>♪</span>'
                + '<strong>' + _esc(asset.filename || '音频素材') + '</strong>'
                + '</div>'
                + (fileUrl ? '<audio class="video-monitor-surface__audio-player js-asset-media" src="' + _esc(fileUrl) + '" controls preload="metadata"></audio>' : '<span class="video-monitor-surface__fallback">未找到可播放文件</span>')
                + '</div>';
        }
        return ''
            + '<div class="video-monitor-surface__frame video-monitor-surface__frame--image is-media-missing">'
            + '<span class="video-monitor-surface__fallback">预览不可用</span>'
            + '</div>';
    }

    function _hydrateTextPreviews(scopeRoot) {
        var root = scopeRoot || document;
        root.querySelectorAll('.js-asset-text-preview').forEach(function (node) {
            if (node.dataset.bound === '1') return;
            node.dataset.bound = '1';
            var fallback = String(node.dataset.fallback || '文稿预览不可用');
            _fetchTextPreview(node.dataset.filePath).then(function (text) {
                if (!node.isConnected) return;
                node.textContent = text || fallback;
                node.classList.toggle('is-empty', !text);
            });
        });
    }

    function _previewClass(type) {
        if (type === 'subtitle') return 'source-thumb__preview--subtitle';
        if (type === 'audio') return 'source-thumb__preview--audio';
        if (type === 'video') return 'source-thumb__preview--video';
        return 'source-thumb__preview--image';
    }

    /**
     * 构建素材缩略图 HTML 字符串。
     * @param {Object} asset  - 素材对象 {id, asset_type, filename, file_size, tags}
     * @param {boolean} selected - 是否默认选中
     */
    window._editorShared.buildAssetThumb = function (asset, selected, options) {
        var kind = _normalizeAssetType(asset);
        var tags = _parseTags(asset);
        var config = options || {};
        var compact = !!config.compact;
        var cardClass = compact ? ' source-thumb--compact' : '';
        var metaText = compact
            ? _typeLabel(kind)
            : (asset.file_path || _typeLabel(kind));
        var tag = (!compact && tags.length) ? ('<span class="pill info">' + _esc(tags[0]) + '</span>') : '';
        return (
            '<div class="source-thumb' + cardClass + (selected ? ' is-selected' : '') + '" data-asset-id="' + _esc(asset.id || '') + '" data-kind="' + kind + '">' +
            '<div class="source-thumb__preview ' + _previewClass(kind) + '">' +
            _buildCardPreview(asset, 'card') +
            '<span class="source-thumb__preview-label">' + _esc(_typeLabel(kind)) + '</span>' +
            '</div>' +
            '<div class="source-thumb__name">' + _esc(asset.filename || '\u672a\u547d\u540d') + '</div>' +
            '<div class="source-thumb__meta">' + _esc(metaText) + '</div>' +
            (tag ? '<div class="source-thumb__tag">' + tag + '</div>' : '') +
            '</div>'
        );
    };

    window._editorShared.buildMiniPreview = function (asset) {
        var kind = _normalizeAssetType(asset);
        var tags = _parseTags(asset);
        return ''
            + '<div class="source-mini-preview__thumb source-thumb__preview ' + _previewClass(kind) + '">'
            + _buildCardPreview(asset, 'detail')
            + '<span class="source-thumb__preview-label">' + _esc(_typeLabel(kind)) + '</span>'
            + '</div>'
            + '<div class="source-mini-preview__info">'
            + '<strong>' + _esc(asset.filename || '未命名素材') + '</strong>'
            + '<div class="subtle">' + _esc(_typeLabel(kind) + ' · ' + (asset.file_path || '未记录路径')) + '</div>'
            + '<div class="source-mini-preview__meta">'
            + '<span>ID ' + _esc(asset.id || '-') + '</span>'
            + '<span>' + _esc(tags[0] || '未打标签') + '</span>'
            + '<span>' + _esc(asset.created_at || '已导入当前序列') + '</span>'
            + '</div>'
            + '</div>';
    };

    window._editorShared.buildStagePreview = function (asset, meta) {
        var kind = _normalizeAssetType(asset);
        var secondaryText = meta && meta.secondaryText ? meta.secondaryText : (asset.file_path || '未记录路径');
        var durationText = meta && meta.durationText ? meta.durationText : '';
        var markerText = meta && meta.markerText ? meta.markerText : _typeLabel(kind);
        return ''
            + '<div class="video-monitor-stage video-monitor-stage--' + _esc(kind) + '">'
            + '<div class="video-monitor-stage__viewport">'
            + _buildStageMedia(asset)
            + '</div>'
            + '<div class="video-monitor-stage__hud">'
            + '<div class="video-monitor-stage__title">'
            + '<strong>' + _esc(asset.filename || '未命名素材') + '</strong>'
            + '<span>' + _esc(markerText) + '</span>'
            + '</div>'
            + '<div class="video-monitor-stage__meta">'
            + '<span>' + _esc(secondaryText) + '</span>'
            + (durationText ? '<span>' + _esc(durationText) + '</span>' : '')
            + '</div>'
            + '</div>'
            + '</div>';
    };

    window._editorShared.hydrateRuntimePreviews = function (scopeRoot) {
        _bindMediaFallbacks(scopeRoot || document);
        _hydrateTextPreviews(scopeRoot || document);
    };

    /**
     * 绑定素材缩略图点击事件（选中高亮）。
     * @param {Array} assets
     */
    window._editorShared.bindAssetThumbs = function (assets) {
        var grid = document.querySelector('#mainHost .source-thumb-grid');
        if (!grid) return;
        grid.querySelectorAll('.source-thumb').forEach(function (thumb) {
            thumb.addEventListener('click', function () {
                grid.querySelectorAll('.source-thumb').forEach(function (t) { t.classList.remove('is-selected'); });
                thumb.classList.add('is-selected');
                var idx = parseInt(thumb.dataset.assetId, 10);
                var asset = assets.find(function (a) { return a.id === idx; });
                if (asset && typeof _renderAssetDetail === 'function') _renderAssetDetail(asset);
            });
        });
    };

}());
