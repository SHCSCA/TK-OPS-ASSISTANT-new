/* ═══════════════════════════════════════════════
   PageAgent 集成模块
   alibaba/page-agent — 自然语言页面操作
   ═══════════════════════════════════════════════ */

(function () {
    let agentInstance = null;
    let agentReady = false;

    /** 初始化 PageAgent（延迟到用户首次打开命令面板时） */
    function initPageAgent(config) {
        if (agentInstance) return agentInstance;
        if (typeof PageAgent === 'undefined') {
            console.warn('[PageAgent] SDK 未加载，跳过初始化');
            return null;
        }
        try {
            agentInstance = new PageAgent({
                model: config.model || 'qwen-plus',
                baseURL: config.baseURL || '',
                apiKey: config.apiKey || '',
                language: config.language || 'zh-CN',
                maxSteps: config.maxSteps || 30,
            });
            agentReady = true;
        } catch (e) {
            console.error('[PageAgent] 初始化失败:', e.message);
        }
        return agentInstance;
    }

    /** 执行自然语言指令 */
    async function executeAgentCommand(command) {
        if (!agentInstance) {
            showToast('AI Agent 未初始化，请先配置 AI 供应商', 'warning');
            return null;
        }
        try {
            const result = await agentInstance.execute(command);
            showToast('Agent 指令执行完成', 'success');
            return result;
        } catch (e) {
            showToast('Agent 执行失败: ' + e.message, 'error');
            return null;
        }
    }

    /** 绑定 AI 命令面板交互 */
    function bindAgentPanel() {
        const overlay = document.getElementById('agentOverlay');
        const input = document.getElementById('agentInput');
        const runBtn = document.getElementById('agentRunBtn');
        const closeBtn = document.getElementById('agentCloseBtn');
        const logList = document.getElementById('agentLogList');
        if (!overlay || !input) return;

        function openPanel() {
            overlay.classList.remove('shell-hidden');
            input.value = '';
            input.focus();
        }

        function closePanel() {
            overlay.classList.add('shell-hidden');
        }

        function appendLog(text, tone) {
            const item = document.createElement('div');
            item.className = 'agent-log-item ' + (tone || '');
            item.textContent = text;
            logList.appendChild(item);
            logList.scrollTop = logList.scrollHeight;
        }

        async function runCommand() {
            const cmd = input.value.trim();
            if (!cmd) return;
            appendLog('▸ ' + cmd, 'user');
            input.value = '';

            if (!agentReady) {
                appendLog('⚠ Agent 未就绪，请先在 AI 供应商页面完成配置', 'warning');
                return;
            }
            appendLog('⏳ 执行中…', 'info');
            const result = await executeAgentCommand(cmd);
            if (result) {
                appendLog('✓ 完成', 'success');
            } else {
                appendLog('✗ 执行未成功', 'error');
            }
        }

        if (runBtn) runBtn.addEventListener('click', runCommand);
        if (closeBtn) closeBtn.addEventListener('click', closePanel);
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                runCommand();
            }
            if (e.key === 'Escape') closePanel();
        });

        // Ctrl+Shift+A 打开 Agent 面板
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'A') {
                e.preventDefault();
                if (overlay.classList.contains('shell-hidden')) {
                    openPanel();
                } else {
                    closePanel();
                }
            }
        });
    }

    // 暴露到全局
    window.initPageAgent = initPageAgent;
    window.executeAgentCommand = executeAgentCommand;
    window.bindAgentPanel = bindAgentPanel;
})();
