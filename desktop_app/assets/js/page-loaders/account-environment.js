(function () {
    'use strict';

    function _pageLoaders() {
        return window._pageLoaders || {};
    }

    function _reloadAccountPage() {
        var loaders = _pageLoaders();
        if (loaders && typeof loaders['account'] === 'function') {
            loaders['account']();
        }
    }

    function _buildProxyMismatchGuidance(message, account) {
        var lines = [];
        var platformMessage = String(message || '').trim();
        if (platformMessage) {
            lines.push('平台反馈：' + platformMessage);
        }
        lines.push('当前现象：直连能识别账号，但当前代理下无法稳定验活。');
        lines.push('优先处理：用当前绑定设备重新登录，并导出该设备环境下的新 Cookie。');
        lines.push('检查代理：地区尽量与账号地区一致，协议与认证方式正确，出口 IP 保持稳定。');
        if (account && account.regionLabel) {
            lines.push('当前账号地区：' + account.regionLabel + '。优先选择同地区设备，不要频繁跨区切换。');
        }
        lines.push('如果暂时没有与 Cookie 适配的代理：不要强绑新代理继续验活；先切回原登录设备，或暂时解绑代理做直连复核，再重新登录获取新 Cookie。');
        return lines.join('\n');
    }

    function _selectedAccountProxyDevice(devices, deviceId) {
        return (devices || []).find(function (item) {
            return String(item.id || '') === String(deviceId || '');
        }) || null;
    }

    function _predictDeviceRuntimeState(proxyIp, fingerprintStatus) {
        var hasProxy = !!String(proxyIp || '').trim();
        var fingerprintKey = String(fingerprintStatus || 'normal').trim().toLowerCase();
        if (!hasProxy) {
            return { status: 'idle', label: '闲置', proxyStatus: 'offline', proxyLabel: '离线' };
        }
        if (fingerprintKey === 'missing') {
            return { status: 'error', label: '异常', proxyStatus: 'online', proxyLabel: '在线' };
        }
        if (fingerprintKey === 'drifted') {
            return { status: 'warning', label: '警告', proxyStatus: 'online', proxyLabel: '在线' };
        }
        return { status: 'healthy', label: '健康', proxyStatus: 'online', proxyLabel: '在线' };
    }

    function _readAccountProxyConfigForm(form) {
        return {
            device_id: form && form.elements.device_id ? form.elements.device_id.value : '',
            proxy_ip: form && form.elements.proxy_ip ? form.elements.proxy_ip.value : '',
            region: form && form.elements.region ? form.elements.region.value : 'US',
        };
    }

    function _buildRebindValidationMessage(loginResult, account) {
        var status = String(loginResult && loginResult.status ? loginResult.status : 'unknown').toLowerCase();
        if (status === 'proxy_mismatch') {
            return _buildProxyMismatchGuidance((loginResult && loginResult.message) || '', account);
        }
        if (status === 'invalid') {
            return '代理检测已通过，但平台没有确认当前 Cookie 处于已登录状态。请在当前绑定设备里重新登录，再导出新 Cookie。';
        }
        return (loginResult && loginResult.message) || '登录态校验没有得到明确结果，请检查代理与 Cookie 是否来自同一登录环境。';
    }

    function _saveAccountProxyBinding(account, data, options) {
        var settings = options || {};
        var deviceId = parseInt(data.device_id, 10);
        if (!deviceId) {
            throw new Error('请先选择设备');
        }

        var proxyIp = String(data.proxy_ip || '').trim();
        if (!proxyIp) {
            throw new Error('请填写代理 IP');
        }

        return api.accounts.update(account.id, { device_id: deviceId }).then(function () {
            return api.devices.update(deviceId, {
                proxy_ip: proxyIp,
                region: data.region,
            });
        }).then(function () {
            if (!settings.validateAfterSave) {
                showToast('代理配置已更新，设备状态已自动同步', 'success');
                _reloadAccountPage();
                return { saved: true };
            }
            if (!String(account.cookieContentRaw || '').trim()) {
                _reloadAccountPage();
                throw new Error('已完成重绑，但当前还没有 Cookie。请先在该设备环境中登录并导入 Cookie，再执行一键校验。');
            }
            return api.accounts.testConnection(account.id).then(function (connectionResult) {
                if (!connectionResult || !connectionResult.ok) {
                    _reloadAccountPage();
                    throw new Error((connectionResult && connectionResult.message) || '代理检测失败，请先修复代理连通性');
                }
                return api.accounts.validateLogin(account.id).then(function (loginResult) {
                    _reloadAccountPage();
                    if (!loginResult || String(loginResult.status || '').toLowerCase() !== 'valid') {
                        throw new Error(_buildRebindValidationMessage(loginResult, account));
                    }
                    var successMessage = '重绑完成，代理检测与登录态校验均通过';
                    if (loginResult.username) {
                        successMessage += ' / ' + loginResult.username;
                    }
                    showToast(successMessage, 'success');
                    return {
                        saved: true,
                        connection: connectionResult,
                        login: loginResult,
                    };
                });
            });
        });
    }

    function _unbindAccountProxyBinding(account) {
        return api.accounts.update(account.id, {
            device_id: null,
            last_connection_status: 'unknown',
            last_connection_checked_at: null,
            last_connection_message: '已解除代理绑定',
            last_login_check_status: 'unknown',
            last_login_check_at: null,
            last_login_check_message: '已解除代理绑定，请按当前环境重新校验登录态',
        }).then(function () {
            showToast('已解除代理绑定，账号当前不再绑定设备代理', 'success');
            _reloadAccountPage();
            return { unbound: true };
        });
    }

    function _parseCookieJson(raw) {
        try {
            var parsed = JSON.parse(raw);
            if (Array.isArray(parsed)) return parsed.filter(function (item) { return item && typeof item === 'object'; });
            if (parsed && Array.isArray(parsed.cookies)) return parsed.cookies.filter(function (item) { return item && typeof item === 'object'; });
        } catch (err) {
            return [];
        }
        return [];
    }

    function _parseCookieNetscape(raw) {
        var rows = raw.split(/\r?\n/).map(function (line) { return line.trim(); }).filter(Boolean);
        var cookies = [];
        rows.forEach(function (line) {
            if (!line || line.charAt(0) === '#') return;
            var parts = line.split(/\t+/);
            if (parts.length >= 7) {
                cookies.push({
                    domain: parts[0],
                    path: parts[2],
                    expires: parts[4],
                    name: parts[5],
                    value: parts[6],
                });
            }
        });
        return cookies;
    }

    function _parseCookieString(raw) {
        if (raw.indexOf('=') < 0) return [];
        return raw.split(';').map(function (part) {
            var pair = part.trim();
            if (!pair || pair.indexOf('=') < 0) return null;
            var eqIndex = pair.indexOf('=');
            return {
                name: pair.slice(0, eqIndex).trim(),
                value: pair.slice(eqIndex + 1).trim(),
            };
        }).filter(Boolean);
    }

    function _resolveCookieExpiry(cookie) {
        if (!cookie || typeof cookie !== 'object') return null;
        var keys = ['expirationDate', 'expires', 'expiry', 'expiration', 'expiresAt'];
        for (var i = 0; i < keys.length; i += 1) {
            var value = cookie[keys[i]];
            if (value === null || typeof value === 'undefined' || value === '') continue;
            var numeric = Number(value);
            if (!isNaN(numeric) && isFinite(numeric)) {
                return numeric < 100000000000 ? numeric * 1000 : numeric;
            }
            var parsed = Date.parse(String(value));
            if (!isNaN(parsed)) return parsed;
        }
        return null;
    }

    function _extractCookieFacts(value) {
        var raw = String(value || '').trim();
        var facts = {
            count: 0,
            validCount: 0,
            expiredCount: 0,
            nearestExpiryMs: null,
            hasExpiry: false,
        };
        if (!raw) return facts;

        var parsedCookies = _parseCookieJson(raw);
        if (!parsedCookies.length) {
            parsedCookies = _parseCookieNetscape(raw);
        }
        if (!parsedCookies.length) {
            parsedCookies = _parseCookieString(raw);
        }

        parsedCookies.forEach(function (cookie) {
            var expiresAt = _resolveCookieExpiry(cookie);
            facts.count += 1;
            if (expiresAt) {
                facts.hasExpiry = true;
                if (facts.nearestExpiryMs === null || expiresAt < facts.nearestExpiryMs) {
                    facts.nearestExpiryMs = expiresAt;
                }
                if (expiresAt <= Date.now()) facts.expiredCount += 1;
                else facts.validCount += 1;
            } else {
                facts.validCount += 1;
            }
        });
        return facts;
    }

    function _inferAccountCookieHealth(value) {
        var facts = _extractCookieFacts(value);
        var now = Date.now();
        var within48h = 48 * 60 * 60 * 1000;
        if (!facts.count) {
            return { status: 'missing', label: '缺失', tone: 'warning', reason: '未录入 Cookie 内容' };
        }
        if (facts.hasExpiry && facts.validCount === 0 && facts.expiredCount > 0) {
            return { status: 'invalid', label: '已失效', tone: 'error', reason: '检测到的 Cookie 已全部过期' };
        }
        if (facts.nearestExpiryMs && facts.nearestExpiryMs <= now) {
            return { status: 'invalid', label: '已失效', tone: 'error', reason: '最近到期时间已经过去' };
        }
        if (facts.nearestExpiryMs && (facts.nearestExpiryMs - now) <= within48h) {
            return { status: 'expiring', label: '48 小时内过期', tone: 'warning', reason: '最近到期时间在 48 小时内' };
        }
        return { status: 'valid', label: '有效', tone: 'success', reason: facts.hasExpiry ? '存在未过期 Cookie' : '已录入 Cookie 内容，未提供到期时间' };
    }

    function _readAccountCookieModalForm(form) {
        return {
            cookie_status: form && form.elements.cookie_status ? form.elements.cookie_status.value : 'auto',
            cookie_content: form && form.elements.cookie_content ? form.elements.cookie_content.value : '',
            notes: form && form.elements.notes ? form.elements.notes.value : '',
        };
    }

    function _persistAccountCookieDraft(account, data, options) {
        var cookieContent = (data.cookie_content || '').trim();
        var cookieChanged = cookieContent !== String(account.cookieContentRaw || '');
        var inferredStatus = _inferAccountCookieHealth(cookieContent);
        var resolvedStatus = data.cookie_status === 'auto' ? inferredStatus.status : data.cookie_status;
        if ((resolvedStatus === 'valid' || resolvedStatus === 'expiring') && !cookieContent) {
            throw new Error('状态为有效或即将过期时，需要同时录入真实 Cookie 内容');
        }

        var payload = {
            cookie_status: resolvedStatus,
            cookie_content: cookieContent || null,
            cookie_updated_at: cookieContent ? (cookieChanged ? new Date().toISOString() : (account.cookieUpdatedAt || null)) : null,
            notes: data.notes || null,
        };
        if (cookieChanged) {
            payload.last_login_check_status = 'unknown';
            payload.last_login_check_at = null;
            payload.last_login_check_message = cookieContent ? 'Cookie 已更新，请重新执行登录态校验' : null;
        }

        return api.accounts.update(account.id, payload).then(function () {
            if (!options || !options.skipToast) {
                showToast('Cookie 状态已更新：' + inferredStatus.label, 'success');
            }
            if (!options || !options.skipReload) {
                _reloadAccountPage();
            }
            return {
                cookieContent: cookieContent,
                cookieChanged: cookieChanged,
                inferredStatus: inferredStatus,
                resolvedStatus: resolvedStatus,
            };
        });
    }

    function _importCookieFileIntoModal(form, button) {
        if (!api.utils || typeof api.utils.importTextFile !== 'function') {
            showToast('当前环境暂不支持导入本地 Cookie 文件', 'warning');
            return;
        }
        var btn = button || null;
        var originalText = btn ? btn.textContent : '';
        if (btn) {
            btn.disabled = true;
            btn.textContent = '导入中...';
        }
        api.utils.importTextFile().then(function (result) {
            if (!result || !result.selected) return;
            if (form && form.elements.cookie_content) {
                form.elements.cookie_content.value = result.content || '';
            }
            showToast('已导入 Cookie 文件：' + (result.name || '未命名文件'), 'success');
        }).catch(function (err) {
            showToast('导入 Cookie 文件失败: ' + ((err && err.message) || '未知错误'), 'error');
        }).finally(function () {
            if (btn) {
                btn.disabled = false;
                btn.textContent = originalText || '导入 Cookie 文件';
            }
        });
    }

    function openAccountEnvironment(account) {
        if (!account) return;
        return api.accounts.openEnvironment(account.id).then(function (result) {
            if (currentRoute === 'account') {
                _reloadAccountPage();
            }
            var deviceId = result && result.device_id ? result.device_id : ((account.device && account.device.id) || account.device_id || 0);
            var deviceName = result && (result.name || result.device_code) ? (result.name || result.device_code) : (account.device && (account.device.name || account.device.device_code)) || (deviceId ? ('设备 #' + deviceId) : '未命名设备');
            var cookieCount = result && result.cookie_count ? ('，已注入 ' + result.cookie_count + ' 条 Cookie') : '';
            var extensionHint = result && result.extension_name ? ('，已自动加载扩展 ' + result.extension_name + '（无需手动安装）') : '';
            showToast('已为账号 ' + (account.username || ('#' + account.id)) + ' 启动隔离环境：' + deviceName + cookieCount + extensionHint, 'success');
            return result;
        }).catch(function (err) {
            showToast('打开环境失败: ' + ((err && err.message) || '未知错误'), 'error');
            throw err;
        });
    }

    function openAccountProxyConfig(account, options) {
        if (!account) return;
        var config = options || {};

        return api.devices.list().then(function (devices) {
            devices = devices || [];
            if (!devices.length) {
                showToast('当前还没有设备，请先新增设备后再配置代理', 'warning');
                return;
            }

            var deviceOptions = devices.map(function (device) {
                var label = (device.name || device.device_code || '未命名设备')
                    + ' / ' + (device.region || '-')
                    + ' / ' + (device.proxy_ip || '未配置代理');
                return { value: String(device.id), label: label };
            });
            var defaultDeviceId = String((account.device && account.device.id) || account.device_id || devices[0].id || '');

            openModal({
                title: (config.quickValidate ? '重绑并校验 / ' : '配置代理 / ') + (account.username || '账号'),
                width: 560,
                submitText: config.quickValidate ? '一键重绑并校验' : '保存代理配置',
                fields: [
                    {
                        key: 'device_id',
                        label: '选择设备',
                        type: 'select',
                        required: true,
                        value: defaultDeviceId,
                        options: deviceOptions,
                        hint: '代理与地区归属于设备。这里绑定账号到目标设备，并同步更新该设备的代理配置。',
                    },
                    {
                        key: 'proxy_ip',
                        label: '代理 IP',
                        required: true,
                        value: _selectedAccountProxyDevice(devices, defaultDeviceId) ? (_selectedAccountProxyDevice(devices, defaultDeviceId).proxy_ip || '') : '',
                        placeholder: '例如 23.88.14.10:8080 或 http://user:pass@23.88.14.10:8080',
                    },
                    {
                        key: 'region',
                        label: '地区',
                        type: 'select',
                        required: true,
                        value: _selectedAccountProxyDevice(devices, defaultDeviceId) ? (_selectedAccountProxyDevice(devices, defaultDeviceId).region || 'US') : 'US',
                        options: ['US', 'UK', 'DE', 'JP', 'MY', 'SG', 'ID', 'TH', 'VN', 'PH', 'BR', 'MX'],
                    },
                    {
                        key: 'status_preview',
                        label: '设备状态',
                        type: 'text',
                        value: '',
                        disabled: true,
                        hint: '',
                    },
                ],
                onSubmit: function (data) {
                    return _saveAccountProxyBinding(account, data, {
                        validateAfterSave: !!config.quickValidate,
                    });
                },
                onOpen: function (ctx) {
                    var deviceField = ctx.form.elements.device_id;
                    var proxyField = ctx.form.elements.proxy_ip;
                    var regionField = ctx.form.elements.region;
                    var previewField = ctx.form.elements.status_preview;
                    var previewHint = previewField && previewField.parentNode ? previewField.parentNode.querySelector('.form-hint') : null;

                    if (!config.quickValidate) {
                        var quickBtn = document.createElement('button');
                        quickBtn.type = 'button';
                        quickBtn.className = 'primary-button';
                        quickBtn.textContent = '一键重绑并校验';
                        ctx.submitButton.className = 'secondary-button modal-submit-btn';
                        ctx.footer.insertBefore(quickBtn, ctx.cancelButton);

                        if (account.device_id) {
                            var unbindBtn = document.createElement('button');
                            unbindBtn.type = 'button';
                            unbindBtn.className = 'ghost-button';
                            unbindBtn.textContent = '解除绑定代理';
                            ctx.footer.insertBefore(unbindBtn, ctx.cancelButton);

                            unbindBtn.addEventListener('click', function () {
                                confirmModal({
                                    title: '解除绑定代理',
                                    message: '确定解除当前账号与设备的代理绑定？设备上的代理配置会保留，但该账号将改为未绑定代理状态。',
                                    confirmText: '解除绑定',
                                    tone: 'warning',
                                }).then(function (ok) {
                                    if (!ok) return;
                                    var originalText = unbindBtn.textContent;
                                    unbindBtn.disabled = true;
                                    quickBtn.disabled = true;
                                    ctx.submitButton.disabled = true;
                                    unbindBtn.textContent = '解绑中...';
                                    _unbindAccountProxyBinding(account).then(function () {
                                        ctx.close();
                                    }).catch(function (err) {
                                        showToast((err && err.message) || '解除绑定失败', 'error');
                                    }).finally(function () {
                                        unbindBtn.disabled = false;
                                        quickBtn.disabled = false;
                                        ctx.submitButton.disabled = false;
                                        unbindBtn.textContent = originalText;
                                    });
                                });
                            });
                        }

                        quickBtn.addEventListener('click', function () {
                            var originalText = quickBtn.textContent;
                            quickBtn.disabled = true;
                            ctx.submitButton.disabled = true;
                            quickBtn.textContent = '校验中...';
                            _saveAccountProxyBinding(account, _readAccountProxyConfigForm(ctx.form), {
                                validateAfterSave: true,
                            }).then(function () {
                                ctx.close();
                            }).catch(function (err) {
                                showToast((err && err.message) || '重绑并校验失败', 'error');
                            }).finally(function () {
                                quickBtn.disabled = false;
                                ctx.submitButton.disabled = false;
                                quickBtn.textContent = originalText;
                            });
                        });
                    }

                    function syncDeviceDraft() {
                        var selected = _selectedAccountProxyDevice(devices, deviceField.value);
                        if (!selected) return;

                        if (!proxyField.value.trim() || String(selected.id) !== String(account.device_id || '')) {
                            proxyField.value = selected.proxy_ip || '';
                        }
                        regionField.value = selected.region || 'US';
                        var preview = _predictDeviceRuntimeState(proxyField.value, selected.fingerprint_status);
                        previewField.value = preview.label;
                        if (previewHint) {
                            previewHint.textContent = '代理状态将自动同步为 ' + preview.proxyLabel + '，设备健康将显示为 ' + preview.label + '。';
                        }
                    }

                    function syncProxyDraft() {
                        var selected = _selectedAccountProxyDevice(devices, deviceField.value);
                        var preview = _predictDeviceRuntimeState(proxyField.value, selected ? selected.fingerprint_status : 'normal');
                        previewField.value = preview.label;
                        if (previewHint) {
                            previewHint.textContent = '代理状态将自动同步为 ' + preview.proxyLabel + '，设备健康将显示为 ' + preview.label + '。';
                        }
                    }

                    deviceField.addEventListener('change', syncDeviceDraft);
                    proxyField.addEventListener('input', syncProxyDraft);
                    syncDeviceDraft();
                },
            });
        }).catch(function (err) {
            showToast('加载设备信息失败: ' + ((err && err.message) || '未知错误'), 'error');
        });
    }

    function openAccountCookieModal(account) {
        var inferred = _inferAccountCookieHealth(account.cookieContentRaw || '');
        openModal({
            title: 'Cookie 状态 / ' + (account.username || '账号'),
            submitText: '保存 Cookie',
            width: 680,
            fields: [
                {
                    key: 'cookie_status',
                    label: 'Cookie 状态（推荐选系统判断）',
                    type: 'select',
                    value: 'auto',
                    options: [
                        { value: 'auto', label: '系统判断（推荐）' },
                        { value: 'valid', label: '有效' },
                        { value: 'expiring', label: '即将过期' },
                        { value: 'invalid', label: '已失效' },
                        { value: 'missing', label: '缺失' },
                        { value: 'unknown', label: '待确认' },
                    ],
                    required: true,
                    hint: '当前系统建议：' + inferred.label + '。如果你不确定，就保持“系统判断”。',
                },
                {
                    key: 'cookie_content',
                    label: 'Cookie 内容',
                    type: 'textarea',
                    rows: 10,
                    mono: true,
                    spellcheck: false,
                    value: account.cookieContentRaw || '',
                    placeholder: '支持粘贴 Cookie 字符串、JSON 数组，或 Netscape cookies 文件内容。',
                    hint: '登录恢复扩展无需手动安装，系统会在“进入环境”时自动注入。只有你想手动导出浏览器 Cookie 回填到系统时，才建议安装 Cookie-Editor 或 EditThisCookie。操作顺序：1. 点“进入环境”登录账号；2. 如需回填，安装 Cookie-Editor / EditThisCookie 并导出当前站点 Cookie；3. 回到这里粘贴或导入文件；4. 点“校验登录态”确认平台仍识别该账号。',
                },
                {
                    key: 'notes',
                    label: '补充说明',
                    type: 'textarea',
                    value: account.notes || '',
                    placeholder: '例如：已完成续签，等待下一次人工确认。',
                },
            ],
            onSubmit: function (data) {
                return _persistAccountCookieDraft(account, data);
            },
            onOpen: function (ctx) {
                var actionBar = document.createElement('div');
                actionBar.className = 'detail-actions';
                actionBar.style.marginRight = 'auto';

                var importBtn = document.createElement('button');
                importBtn.type = 'button';
                importBtn.className = 'secondary-button';
                importBtn.textContent = '导入 Cookie 文件';
                importBtn.addEventListener('click', function () {
                    _importCookieFileIntoModal(ctx.form, importBtn);
                });
                actionBar.appendChild(importBtn);

                var validateBtn = document.createElement('button');
                validateBtn.type = 'button';
                validateBtn.className = 'secondary-button';
                validateBtn.textContent = '保存并校验登录态';
                validateBtn.addEventListener('click', function () {
                    var draft = _readAccountCookieModalForm(ctx.form);
                    _persistAccountCookieDraft(account, draft, { skipToast: true, skipReload: true }).then(function () {
                        return runAccountLoginValidation(account.id, validateBtn, { suppressReload: true });
                    }).then(function () {
                        ctx.close();
                        _reloadAccountPage();
                    }).catch(function (err) {
                        showToast((err && err.message) || '登录态校验失败', 'error');
                    });
                });
                actionBar.appendChild(validateBtn);

                ctx.footer.insertBefore(actionBar, ctx.cancelButton);
            },
        });
    }

    function runAccountConnectionTest(accountId, button) {
        var btn = button || null;
        var originalText = btn ? btn.textContent : '';
        if (btn) {
            btn.disabled = true;
            btn.textContent = '检测中...';
        }
        return api.accounts.testConnection(parseInt(accountId, 10)).then(function (result) {
            var tone = result && result.ok ? 'success' : 'error';
            var message = result && result.message ? result.message : '代理检测完成';
            if (result && result.ok && result.latency_ms) {
                message += ' / ' + result.latency_ms + 'ms';
            }
            if (result && result.target) {
                message += ' / ' + result.target;
            }
            if (result && result.scope_label) {
                message += ' / ' + result.scope_label;
            }
            showToast(message, tone);
            if (!uiState.account) uiState.account = { statusFilter: 'all', view: 'card', sortMode: 'default', batchMode: false };
            uiState.account.selectedId = parseInt(accountId, 10) || null;
            _reloadAccountPage();
            return result;
        }).catch(function (err) {
            showToast('代理检测失败: ' + ((err && err.message) || '未知错误'), 'error');
            throw err;
        }).finally(function () {
            if (btn) {
                btn.disabled = false;
                btn.textContent = originalText || '检测代理';
            }
        });
    }

    function runAccountLoginValidation(accountId, button, options) {
        var btn = button || null;
        var originalText = btn ? btn.textContent : '';
        if (btn) {
            btn.disabled = true;
            btn.textContent = '校验中...';
        }
        return api.accounts.validateLogin(parseInt(accountId, 10)).then(function (result) {
            var status = (result && result.status ? result.status : 'unknown').toLowerCase();
            var tone = status === 'valid' ? 'success' : (status === 'invalid' ? 'error' : 'warning');
            var message = result && result.message ? result.message : '登录态校验完成';
            if (result && result.target) {
                message += ' / ' + result.target;
            }
            showToast(message, tone);
            if (!options || !options.suppressReload) {
                if (!uiState.account) uiState.account = { statusFilter: 'all', view: 'card', sortMode: 'default', batchMode: false };
                uiState.account.selectedId = parseInt(accountId, 10) || null;
                _reloadAccountPage();
            }
            return result;
        }).catch(function (err) {
            showToast('登录态校验失败: ' + ((err && err.message) || '未知错误'), 'error');
            throw err;
        }).finally(function () {
            if (btn) {
                btn.disabled = false;
                btn.textContent = originalText || '校验登录态';
            }
        });
    }

    window.__accountEnvironmentHelpers = {
        openAccountEnvironment: openAccountEnvironment,
        openAccountProxyConfig: openAccountProxyConfig,
        openAccountCookieModal: openAccountCookieModal,
        runAccountConnectionTest: runAccountConnectionTest,
        runAccountLoginValidation: runAccountLoginValidation,
    };
})();