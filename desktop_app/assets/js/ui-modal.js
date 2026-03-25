/* ── ui-modal.js ─ 通用模态框系统 ─────────────────
   提供 openModal / closeModal / confirmModal 三个全局方法。
   支持表单型 Modal 和确认对话框 (Confirm)。
   ──────────────────────────────────────────────── */
(function () {
    'use strict';

    var _overlay = null;   // 当前活跃的 overlay 元素
    var _onSubmit = null;  // 表单提交回调
    var _selectPortal = null;
    var _selectPortalCleanup = null;
    var _selectPortalTrigger = null;

    function _removeOverlayNode(overlay) {
        if (overlay && overlay.parentNode) {
            overlay.parentNode.removeChild(overlay);
        }
    }

    function _normalizeSelectOptions(options) {
        return (options || []).map(function (option) {
            if (typeof option === 'object') {
                return {
                    value: String(option.value == null ? '' : option.value),
                    label: String(option.label == null ? option.value : option.label),
                };
            }
            return {
                value: String(option == null ? '' : option),
                label: String(option == null ? '' : option),
            };
        });
    }

    function _closeSelectPortal() {
        if (typeof _selectPortalCleanup === 'function') {
            _selectPortalCleanup();
        }
        _selectPortal = null;
        _selectPortalCleanup = null;
        _selectPortalTrigger = null;
    }

    function _resolveSelectLabel(options, value, placeholder) {
        var current = (options || []).filter(function (option) {
            return String(option.value) === String(value == null ? '' : value);
        })[0];
        if (current) return current.label;
        return placeholder || '请选择';
    }

    function _positionSelectPortal(trigger, portal) {
        if (!trigger || !portal) return;
        var rect = trigger.getBoundingClientRect();
        var portalHeight = portal.offsetHeight || 0;
        var top = rect.bottom + 6;
        if ((top + portalHeight) > (window.innerHeight - 16)) {
            top = Math.max(16, rect.top - portalHeight - 6);
        }
        portal.style.left = Math.max(12, rect.left) + 'px';
        portal.style.top = top + 'px';
        portal.style.width = Math.max(rect.width, 220) + 'px';
    }

    function _openSelectPortal(trigger, hiddenInput, options, placeholder) {
        if (!trigger || !hiddenInput) return;
        if (_selectPortalTrigger === trigger) {
            _closeSelectPortal();
            return;
        }
        _closeSelectPortal();

        var portal = document.createElement('div');
        portal.className = 'modal-select-portal';
        portal.setAttribute('role', 'listbox');

        options.forEach(function (option) {
            var button = document.createElement('button');
            button.type = 'button';
            button.className = 'modal-select-option';
            if (String(option.value) === String(hiddenInput.value || '')) {
                button.classList.add('is-selected');
            }
            button.textContent = option.label;
            button.setAttribute('data-value', option.value);
            button.setAttribute('role', 'option');
            button.setAttribute('aria-selected', String(String(option.value) === String(hiddenInput.value || '')));
            button.addEventListener('mousedown', function (event) {
                event.preventDefault();
            });
            button.addEventListener('click', function (event) {
                event.preventDefault();
                event.stopPropagation();
                hiddenInput.value = option.value;
                trigger.querySelector('.modal-select-trigger__text').textContent = _resolveSelectLabel(options, option.value, placeholder);
                trigger.classList.toggle('is-empty', !option.value);
                hiddenInput.dispatchEvent(new Event('change', { bubbles: true }));
                _closeSelectPortal();
            });
            portal.appendChild(button);
        });

        document.body.appendChild(portal);
        _positionSelectPortal(trigger, portal);
        trigger.setAttribute('aria-expanded', 'true');

        function handleOutside(event) {
            if (!portal.contains(event.target) && !trigger.contains(event.target)) {
                _closeSelectPortal();
            }
        }

        function handleRelayout() {
            _positionSelectPortal(trigger, portal);
        }

        document.addEventListener('mousedown', handleOutside, true);
        window.addEventListener('resize', handleRelayout);
        window.addEventListener('scroll', handleRelayout, true);

        _selectPortal = portal;
        _selectPortalTrigger = trigger;
        _selectPortalCleanup = function () {
            document.removeEventListener('mousedown', handleOutside, true);
            window.removeEventListener('resize', handleRelayout);
            window.removeEventListener('scroll', handleRelayout, true);
            trigger.setAttribute('aria-expanded', 'false');
            if (portal.parentNode) portal.parentNode.removeChild(portal);
        };
    }

    function _createSelectField(field) {
        var wrapper = document.createElement('div');
        wrapper.className = 'modal-select';

        var hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = field.key;
        hiddenInput.value = field.value == null ? '' : String(field.value);
        wrapper.appendChild(hiddenInput);

        var trigger = document.createElement('button');
        trigger.type = 'button';
        trigger.className = 'form-input form-select-trigger';
        trigger.setAttribute('aria-haspopup', 'listbox');
        trigger.setAttribute('aria-expanded', 'false');
        if (field.disabled) trigger.disabled = true;

        var text = document.createElement('span');
        text.className = 'modal-select-trigger__text';
        var options = _normalizeSelectOptions(field.options);
        text.textContent = _resolveSelectLabel(options, hiddenInput.value, field.placeholder || '请选择');
        trigger.appendChild(text);

        var caret = document.createElement('span');
        caret.className = 'modal-select-trigger__caret';
        caret.innerHTML = '&#9662;';
        trigger.appendChild(caret);

        trigger.classList.toggle('is-empty', !hiddenInput.value);
        trigger.addEventListener('click', function (event) {
            event.preventDefault();
            event.stopPropagation();
            if (field.disabled) return;
            _openSelectPortal(trigger, hiddenInput, options, field.placeholder || '请选择');
        });

        wrapper.appendChild(trigger);
        return { wrapper: wrapper, input: hiddenInput, trigger: trigger };
    }

    /* ══════════════════════════════════════════════
       openModal(options)
       options:
         title       - 弹窗标题
         fields      - 表单字段数组 [{key, label, type, value, options, placeholder, required, hint}]
         submitText  - 提交按钮文字（默认 "确定"）
         cancelText  - 取消按钮文字（默认 "取消"）
         onSubmit    - function(formData) → Promise | void
         width       - 弹窗宽度（默认 480px）
       ══════════════════════════════════════════════ */
    function openModal(opts) {
        closeModal(); // 防止重叠

        var overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.setAttribute('role', 'dialog');
        overlay.setAttribute('aria-modal', 'true');

        var panel = document.createElement('div');
        panel.className = 'modal-panel';
        if (opts.width) panel.style.width = opts.width + 'px';

        // ── Header ──
        var header = document.createElement('div');
        header.className = 'modal-header';
        header.innerHTML = '<strong>' + _esc(opts.title || '操作') + '</strong>';
        var closeBtn = document.createElement('button');
        closeBtn.className = 'icon-button modal-close-btn';
        closeBtn.type = 'button';
        closeBtn.innerHTML = '<span class="shell-icon">✕</span>';
        closeBtn.addEventListener('click', function () { closeModal(); });
        header.appendChild(closeBtn);
        panel.appendChild(header);

        // ── Body (form) ──
        var body = document.createElement('div');
        body.className = 'modal-body';
        var form = document.createElement('form');
        form.className = 'modal-form';
        form.setAttribute('novalidate', '');

        (opts.fields || []).forEach(function (f) {
            var group = document.createElement('div');
            group.className = 'form-group';

            var label = document.createElement('label');
            label.className = 'form-label';
            label.textContent = f.label || f.key;
            if (f.required) {
                var req = document.createElement('span');
                req.className = 'form-required';
                req.textContent = ' *';
                label.appendChild(req);
            }
            group.appendChild(label);

            var input;
            if (f.type === 'select') {
                var selectField = _createSelectField(f);
                input = selectField.input;
                group.appendChild(selectField.wrapper);
            } else if (f.type === 'textarea') {
                input = document.createElement('textarea');
                input.className = 'form-input form-textarea';
                input.rows = f.rows || 3;
                input.value = f.value || '';
                if (f.spellcheck === false) input.spellcheck = false;
                if (f.mono) input.classList.add('mono');
            } else if (f.type === 'number') {
                input = document.createElement('input');
                input.className = 'form-input';
                input.type = 'number';
                input.value = f.value || '';
                if (f.min !== undefined) input.min = f.min;
                if (f.max !== undefined) input.max = f.max;
                if (f.step !== undefined) input.step = f.step;
            } else {
                input = document.createElement('input');
                input.className = 'form-input';
                input.type = f.type || 'text';
                input.value = f.value || '';
            }
            if (f.type !== 'select') {
                input.name = f.key;
                if (f.placeholder) input.placeholder = f.placeholder;
                if (f.required) input.required = true;
                if (f.disabled) input.disabled = true;
                group.appendChild(input);
            }

            if (f.hint) {
                var hint = document.createElement('div');
                hint.className = 'form-hint';
                hint.textContent = f.hint;
                group.appendChild(hint);
            }

            form.appendChild(group);
        });
        body.appendChild(form);
        panel.appendChild(body);

        // ── Footer ──
        var footer = document.createElement('div');
        footer.className = 'modal-footer';
        var cancelBtn = document.createElement('button');
        cancelBtn.className = 'secondary-button';
        cancelBtn.type = 'button';
        cancelBtn.textContent = opts.cancelText || '取消';
        cancelBtn.addEventListener('click', function () { closeModal(); });
        footer.appendChild(cancelBtn);

        var submitBtn = document.createElement('button');
        submitBtn.className = 'primary-button modal-submit-btn';
        submitBtn.type = 'button';
        submitBtn.textContent = opts.submitText || '确定';
        footer.appendChild(submitBtn);
        panel.appendChild(footer);

        overlay.appendChild(panel);
        document.body.appendChild(overlay);
        _overlay = overlay;
        _onSubmit = opts.onSubmit || null;

        if (typeof opts.onOpen === 'function') {
            opts.onOpen({
                overlay: overlay,
                panel: panel,
                form: form,
                footer: footer,
                submitButton: submitBtn,
                cancelButton: cancelBtn,
                close: function () { closeModal(overlay); },
            });
        }

        // Auto-focus first input
        requestAnimationFrame(function () {
            var first = form.querySelector('input:not([type="hidden"]), .form-select-trigger, textarea');
            if (first) first.focus();
        });

        // Click overlay to close
        overlay.addEventListener('click', function (e) {
            if (e.target === overlay) closeModal();
        });

        // Enter to submit
        form.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
                e.preventDefault();
                submitBtn.click();
            }
        });

        // Submit handler
        submitBtn.addEventListener('click', function () {
            // Gather form data
            var data = {};
            var valid = true;
            (opts.fields || []).forEach(function (f) {
                var el = form.elements[f.key];
                if (!el) return;
                var val = el.value;
                if (f.required && !val.trim()) {
                    el.classList.add('form-input--error');
                    valid = false;
                } else {
                    el.classList.remove('form-input--error');
                }
                if (f.type === 'number' && val !== '') {
                    data[f.key] = parseFloat(val);
                } else {
                    data[f.key] = val;
                }
            });
            if (!valid) {
                showToast('请填写必填字段', 'warning');
                return;
            }
            if (_onSubmit) {
                submitBtn.disabled = true;
                submitBtn.textContent = '提交中…';
                var result = _onSubmit(data);
                if (result && typeof result.then === 'function') {
                    result.then(function () {
                        closeModal();
                    }).catch(function (err) {
                        submitBtn.disabled = false;
                        submitBtn.textContent = opts.submitText || '确定';
                        showToast(err.message || '操作失败', 'error');
                    });
                } else {
                    closeModal();
                }
            } else {
                closeModal();
            }
        });
    }

    /* ══════════════════════════════════════════════
       closeModal()
       ══════════════════════════════════════════════ */
    function closeModal() {
        var candidate = arguments[0];
        var overlay = candidate && candidate.classList && candidate.classList.contains('modal-overlay') ? candidate : _overlay;
        if (!overlay || overlay.__closing || !overlay.classList) {
            return;
        }
        _closeSelectPortal();
        overlay.__closing = true;
        if (_overlay === overlay) {
            _overlay = null;
            _onSubmit = null;
        }
        _removeOverlayNode(overlay);
    }

    /* ══════════════════════════════════════════════
       confirmModal(options)
       options:
         title    - 标题
         message  - 正文描述
         tone     - 'danger' | 'warning' | 'info'（默认 info）
         confirmText - 确认按钮文字
         onConfirm   - function() → Promise | void
       ══════════════════════════════════════════════ */
    function confirmModal(opts) {
        closeModal();
        return new Promise(function (resolve) {
            var settled = false;
            function settle(value) {
                if (settled) return;
                settled = true;
                resolve(value);
            }

            var overlay = document.createElement('div');
            overlay.className = 'modal-overlay';
            overlay.setAttribute('role', 'alertdialog');

            var panel = document.createElement('div');
            panel.className = 'modal-panel modal-panel--confirm';

            var body = document.createElement('div');
            body.className = 'modal-body confirm-body';

            var icon = document.createElement('div');
            icon.className = 'confirm-icon confirm-icon--' + (opts.tone || 'info');
            icon.textContent = opts.tone === 'danger' ? '⚠' : opts.tone === 'warning' ? '△' : 'ℹ';
            body.appendChild(icon);

            var title = document.createElement('strong');
            title.className = 'confirm-title';
            title.textContent = opts.title || '确认操作';
            body.appendChild(title);

            if (opts.message) {
                var msg = document.createElement('p');
                msg.className = 'confirm-message';
                msg.textContent = opts.message;
                body.appendChild(msg);
            }
            panel.appendChild(body);

            var footer = document.createElement('div');
            footer.className = 'modal-footer';
            var cancelBtn = document.createElement('button');
            cancelBtn.className = 'secondary-button';
            cancelBtn.type = 'button';
            cancelBtn.textContent = '取消';
            footer.appendChild(cancelBtn);

            var confirmBtn = document.createElement('button');
            confirmBtn.className = (opts.tone === 'danger') ? 'danger-button' : 'primary-button';
            confirmBtn.type = 'button';
            confirmBtn.textContent = opts.confirmText || '确认';
            footer.appendChild(confirmBtn);
            panel.appendChild(footer);

            overlay.appendChild(panel);
            document.body.appendChild(overlay);
            _overlay = overlay;

            function dismiss() {
                settle(false);
                closeModal(overlay);
            }

            overlay.__handleDismiss = dismiss;

            cancelBtn.addEventListener('click', dismiss);
            overlay.addEventListener('click', function (e) {
                if (e.target === overlay) dismiss();
            });

            confirmBtn.addEventListener('click', function () {
                if (opts.onConfirm) {
                    confirmBtn.disabled = true;
                    var result = opts.onConfirm();
                    if (result && typeof result.then === 'function') {
                        result.then(function () {
                            settle(true);
                            closeModal(overlay);
                        }).catch(function (err) {
                            confirmBtn.disabled = false;
                            showToast((err && err.message) || '操作失败', 'error');
                        });
                        return;
                    }
                }
                settle(true);
                closeModal(overlay);
            });

            requestAnimationFrame(function () { confirmBtn.focus(); });
        });
    }

    // ── ESC 全局关闭 ──
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && _overlay) {
            if (typeof _overlay.__handleDismiss === 'function') {
                _overlay.__handleDismiss();
            } else {
                closeModal(_overlay);
            }
        }
    });

    function _esc(str) {
        var d = document.createElement('div');
        d.textContent = str;
        return d.innerHTML;
    }

    // ── 暴露全局 ──
    window.openModal = openModal;
    window.closeModal = closeModal;
    window.confirmModal = confirmModal;
    window.showConfirm = confirmModal;
})();
