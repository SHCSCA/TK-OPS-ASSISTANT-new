/* ── ui-license.js ─ 激活页面 & Tier 门控 ─────────────
   全屏遮罩：未激活时阻止访问主功能。
   已激活时提供状态查看和吊销入口。
   Tier 缓存与路由级功能门控。
   ──────────────────────────────────────────────── */
(function () {
    'use strict';

    var _overlay = null;

    /* ── Tier 门控 ── */
    var _FREE_ROUTES = [
        'dashboard', 'account', 'setup-wizard', 'system-settings',
        'log-center', 'version-upgrade', 'network-diagnostics'
    ];
    var _ENTERPRISE_ONLY = ['license-issuer', 'permission-management'];

    var _cachedTier = null; // null = unknown, 'free'/'pro'/'enterprise'

    var _TIER_RANK = { free: 0, pro: 1, enterprise: 2 };

    function _tierRank(t) { return _TIER_RANK[t] || 0; }

    function setCachedTier(tier) {
        _cachedTier = tier || null;
        _applyNavTierBadges();
    }

    function getCachedTier() { return _cachedTier; }

    /**
     * Check if *routeKey* is accessible with the current tier.
     * Returns {allowed: bool, required_tier: str}
     */
    function canAccessRoute(routeKey) {
        if (_FREE_ROUTES.indexOf(routeKey) !== -1) {
            return { allowed: true, required_tier: 'free' };
        }
        var tier = _cachedTier || 'free';
        if (_ENTERPRISE_ONLY.indexOf(routeKey) !== -1) {
            return { allowed: tier === 'enterprise', required_tier: 'enterprise' };
        }
        return { allowed: _tierRank(tier) >= 1, required_tier: 'pro' };
    }

    /** Show a full-screen upgrade prompt when a route is blocked. */
    function showTierBlock(routeKey, requiredTier) {
        var mainHost = document.getElementById('mainHost');
        var tierLabel = { free: '免费版', pro: '专业版', enterprise: '企业版' };
        mainHost.innerHTML =
            '<div style=\"display:flex;flex-direction:column;align-items:center;justify-content:center;' +
            'min-height:60vh;gap:1.2rem;text-align:center;color:var(--text-secondary,#666)\">' +
                '<div style=\"font-size:3rem\">🔒</div>' +
                '<h2 style=\"margin:0;color:var(--text-primary,#222)\">功能受限</h2>' +
                '<p>此功能需要 <strong>' + (tierLabel[requiredTier] || requiredTier) + '</strong> 或更高许可证等级</p>' +
                '<p style=\"font-size:0.88rem\">当前等级：<code>' +
                    (tierLabel[_cachedTier] || _cachedTier || '未激活') + '</code></p>' +
                '<button class=\"btn-primary\" onclick=\"renderRoute(\\x27setup-wizard\\x27)\">前往激活 / 升级</button>' +
            '</div>';
        var detailHost = document.getElementById('detailHost');
        if (detailHost) detailHost.innerHTML = '';
    }

    /** Apply visual tier badges to sidebar nav items. */
    function _applyNavTierBadges() {
        document.querySelectorAll('.nav-link[data-route]').forEach(function (btn) {
            // Remove old badges
            var old = btn.querySelector('.tier-badge');
            if (old) old.remove();
            btn.classList.remove('tier-locked');

            var route = btn.dataset.route;
            var check = canAccessRoute(route);
            if (!check.allowed) {
                btn.classList.add('tier-locked');
                var badge = document.createElement('span');
                badge.className = 'tier-badge';
                badge.textContent = check.required_tier === 'enterprise' ? 'ENT' : 'PRO';
                btn.appendChild(badge);
            }
        });
    }

    /* ── Show the activation screen ── */
    function showActivationScreen(status) {
        hideActivationScreen();

        var overlay = document.createElement('div');
        overlay.id = 'licenseOverlay';
        overlay.className = 'license-overlay';

        var card = document.createElement('div');
        card.className = 'license-card';

        var shortId = status.machine_id_short || status.machineCodeShort || status.machine_code_short || '----';
        var fullId = status.machine_id || status.machineCode || status.machine_code || '';
        var errMsg  = status.error || '';

        card.innerHTML =
            '<div class="license-header">' +
                '<div class="license-logo">T</div>' +
                '<h2>TK-OPS \u8f6f\u4ef6\u6fc0\u6d3b</h2>' +
                '<p class="license-subtitle">\u8bf7\u8f93\u5165\u8bb8\u53ef\u8bc1\u5bc6\u94a5\u4ee5\u89e3\u9501\u5168\u90e8\u529f\u80fd</p>' +
            '</div>' +
            '<div class="license-machine">' +
                '<label>\u673a\u5668\u663e\u793a\u7801</label>' +
                '<div class="license-machine-id">' +
                    '<code id="licenseMachineId">' + _esc(shortId) + '</code>' +
                    '<button type="button" class="btn-sm" id="licenseCopyBtn">\u590d\u5236\u5b8c\u6574\u673a\u5668\u7801</button>' +
                '</div>' +
            '</div>' +
            '<div class="license-form">' +
                '<input type="text" id="licenseKeyInput" class="license-input" ' +
                    'placeholder="\u7c98\u8d34\u8bb8\u53ef\u8bc1\u5bc6\u94a5" spellcheck="false" autocomplete="off">' +
                '<div class="license-error" id="licenseError">' + _esc(errMsg) + '</div>' +
                '<button type="button" class="btn-primary license-submit" id="licenseSubmitBtn">\u6fc0\u6d3b</button>' +
            '</div>';

        overlay.appendChild(card);
        document.body.appendChild(overlay);
        _overlay = overlay;

        // Wire events
        document.getElementById('licenseCopyBtn').addEventListener('click', function () {
            _copyToClipboard(fullId || shortId);
        });
        document.getElementById('licenseSubmitBtn').addEventListener('click', _handleActivate);
        document.getElementById('licenseKeyInput').addEventListener('keydown', function (e) {
            if (e.key === 'Enter') _handleActivate();
        });
    }

    function _handleActivate() {
        var input  = document.getElementById('licenseKeyInput');
        var errEl  = document.getElementById('licenseError');
        var btn    = document.getElementById('licenseSubmitBtn');
        var key    = (input.value || '').trim();
        if (!key) { errEl.textContent = '\u8bf7\u8f93\u5165\u5bc6\u94a5'; return; }

        btn.disabled = true;
        btn.textContent = '\u9a8c\u8bc1\u4e2d\u2026';
        errEl.textContent = '';

        api.license.activate(key).then(function (info) {
            hideActivationScreen();
            var tier = (info && (info.tier || info.license_tier)) ? String(info.tier || info.license_tier) : 'unknown';
            setCachedTier(tier);
            if (typeof showToast === 'function') showToast('\u6fc0\u6d3b\u6210\u529f\uff01\u7b49\u7ea7\uff1a' + tier.toUpperCase(), 'success');
        }).catch(function (err) {
            errEl.textContent = err.message || '\u6fc0\u6d3b\u5931\u8d25';
            btn.disabled = false;
            btn.textContent = '\u6fc0\u6d3b';
        });
    }

    function hideActivationScreen() {
        if (_overlay) {
            _overlay.remove();
            _overlay = null;
        }
    }

    /* ── Show license info badge (in settings or about dialog) ── */
    function showLicenseInfo(status) {
        if (!status.activated) return;
        var tier = status.tier ? String(status.tier).toUpperCase() : 'UNKNOWN';
        var text = '\u8bb8\u53ef\u8bc1: ' + tier;
        if (status.is_permanent) {
            text += ' (\u6c38\u4e45)';
        } else if (status.days_remaining !== null) {
            text += ' (\u5269\u4f59 ' + status.days_remaining + ' \u5929)';
        }
        return text;
    }

    /* ── Check license at startup ── */
    function checkLicenseOnStartup() {
        api.license.status().then(function (status) {
            if (status.activated) {
                setCachedTier(status.tier);
            } else {
                setCachedTier(null);
                showActivationScreen(status);
            }
        }).catch(function () {
            // Backend not ready yet — retry once
            setTimeout(function () {
                api.license.status().then(function (s) {
                    if (s.activated) {
                        setCachedTier(s.tier);
                    } else {
                        setCachedTier(null);
                        showActivationScreen(s);
                    }
                }).catch(function () {});
            }, 1000);
        });
    }

    function _copyToClipboard(text) {
        if (!text) {
            if (typeof showToast === 'function') showToast('\u673a\u5668\u7801\u4e3a\u7a7a\uff0c\u65e0\u6cd5\u590d\u5236', 'error');
            return;
        }
        if (window.api && window.api.utils && window.api.utils.copyToClipboard) {
            window.api.utils.copyToClipboard(text).then(function() {
                if (typeof showToast === 'function') showToast('\u5df2\u590d\u5236\u5b8c\u6574\u673a\u5668\u7801', 'success');
            }).catch(function() {
                if (typeof showToast === 'function') showToast('\u590d\u5236\u5931\u8d25', 'error');
            });
            return;
        }
        
        // Fallback for browser without backend
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(function () {
                if (typeof showToast === 'function') showToast('\u5df2\u590d\u5236\u5b8c\u6574\u673a\u5668\u7801', 'success');
            }).catch(function () {
                _copyToClipboardFallback(text);
            });
        } else {
            _copyToClipboardFallback(text);
        }
    }

    function _copyToClipboardFallback(text) {
        var ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        ta.setSelectionRange(0, ta.value.length);
        var copied = false;
        try {
            copied = document.execCommand('copy');
        } catch (err) {
            copied = false;
        }
        ta.remove();
        if (typeof showToast === 'function') {
            showToast(copied ? '\u5df2\u590d\u5236\u5b8c\u6574\u673a\u5668\u7801' : '\u590d\u5236\u5931\u8d25\uff0c\u8bf7\u624b\u52a8\u590d\u5236\u4e0b\u65b9\u5b8c\u6574\u673a\u5668\u7801', copied ? 'success' : 'warning');
        }
    }

    function _esc(s) {
        var d = document.createElement('div');
        d.appendChild(document.createTextNode(s || ''));
        return d.innerHTML;
    }

    // ── Expose globals ──
    window.showActivationScreen = showActivationScreen;
    window.hideActivationScreen = hideActivationScreen;
    window.checkLicenseOnStartup = checkLicenseOnStartup;
    window.showLicenseInfo = showLicenseInfo;
    window.canAccessRoute = canAccessRoute;
    window.showTierBlock = showTierBlock;
    window.setCachedTier = setCachedTier;
    window.getCachedTier = getCachedTier;
})();
