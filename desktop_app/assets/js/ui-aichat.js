/* ═══════════════════════════════════════════════
   AI Chat Panel — 浮动对话面板
   ═══════════════════════════════════════════════ */
(function () {
    'use strict';

    var _messages = [];   // {role, content}
    var _streaming = false;
    var _pollTimer = null;
    var _currentContent = '';

    /* ── 初始化 ── */
    function initAiChat() {
        var overlay = document.getElementById('aiChatOverlay');
        var toggleBtn = document.getElementById('aiChatToggle');
        var closeBtn = document.getElementById('aiChatCloseBtn');
        var sendBtn = document.getElementById('aiChatSendBtn');
        var input = document.getElementById('aiChatInput');

        if (!overlay) return;

        toggleBtn.addEventListener('click', function () {
            overlay.classList.toggle('shell-hidden');
            if (!overlay.classList.contains('shell-hidden')) {
                input.focus();
                loadPresets();
            }
        });

        closeBtn.addEventListener('click', function () {
            overlay.classList.add('shell-hidden');
        });

        sendBtn.addEventListener('click', function () { sendMessage(); });

        input.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Ctrl+Shift+C toggle
        document.addEventListener('keydown', function (e) {
            if (e.ctrlKey && e.shiftKey && e.key === 'C') {
                e.preventDefault();
                toggleBtn.click();
            }
        });
    }

    /* ── 加载预设列表 ── */
    function loadPresets() {
        var select = document.getElementById('aiPresetSelect');
        if (!select || select.children.length > 1) return;
        api.ai.presets().then(function (presets) {
            select.innerHTML = '';
            presets.forEach(function (p) {
                var opt = document.createElement('option');
                opt.value = p.key;
                opt.textContent = p.name;
                select.appendChild(opt);
            });
        }).catch(function () {});
    }

    /* ── 发送消息 ── */
    function sendMessage() {
        if (_streaming) return;
        var input = document.getElementById('aiChatInput');
        var text = (input.value || '').trim();
        if (!text) return;

        _messages.push({ role: 'user', content: text });
        appendBubble('user', text);
        input.value = '';

        var preset = document.getElementById('aiPresetSelect').value || 'default';
        var payload = { messages: _messages, preset: preset };

        _streaming = true;
        _currentContent = '';
        setStatus('正在思考…');
        appendBubble('assistant', '');
        var bubbles = document.getElementById('aiChatMessages');
        var lastBubble = bubbles.lastElementChild;
        var contentEl = lastBubble.querySelector('.ai-chat-bubble__content');

        api.ai.startStream(payload).then(function () {
            _pollTimer = setInterval(function () { pollStream(contentEl); }, 100);
        }).catch(function (err) {
            _streaming = false;
            contentEl.textContent = '请求失败: ' + err.message;
            setStatus('');
        });
    }

    /* ── 轮询流式响应 ── */
    function pollStream(contentEl) {
        api.ai.poll().then(function (data) {
            var chunks = data.chunks || [];
            chunks.forEach(function (c) {
                if (c.error) {
                    contentEl.textContent = '错误: ' + c.error;
                    stopStream();
                    return;
                }
                if (c.delta) {
                    _currentContent += c.delta;
                    contentEl.textContent = _currentContent;
                    scrollToBottom();
                }
                if (c.done) {
                    stopStream();
                    if (c.model) {
                        setStatus(c.provider + ' / ' + c.model + '  ·  ' + (c.elapsed_ms || 0) + 'ms');
                    }
                }
            });
            if (data.finished) {
                stopStream();
            }
        }).catch(function () {
            stopStream();
        });
    }

    function stopStream() {
        _streaming = false;
        if (_pollTimer) { clearInterval(_pollTimer); _pollTimer = null; }
        if (_currentContent) {
            _messages.push({ role: 'assistant', content: _currentContent });
        }
    }

    /* ── DOM 操作 ── */
    function appendBubble(role, text) {
        var container = document.getElementById('aiChatMessages');
        var div = document.createElement('div');
        div.className = 'ai-chat-bubble ai-chat-bubble--' + role;
        div.innerHTML = '<div class="ai-chat-bubble__role">' + (role === 'user' ? '你' : 'AI') + '</div>' +
                        '<div class="ai-chat-bubble__content">' + escapeHtml(text) + '</div>';
        container.appendChild(div);
        scrollToBottom();
    }

    function scrollToBottom() {
        var el = document.getElementById('aiChatMessages');
        el.scrollTop = el.scrollHeight;
    }

    function setStatus(text) {
        var el = document.getElementById('aiChatStatus');
        if (el) el.textContent = text || '';
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    /* ── 暴露 ── */
    window.initAiChat = initAiChat;
})();
