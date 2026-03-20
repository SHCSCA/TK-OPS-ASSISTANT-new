function bindAIConfigInteractions() {
    const detailHost = document.getElementById('detailHost');
    if (!detailHost) return;
    const configRoot = detailHost.querySelector('.ai-side-config-root');
    if (!configRoot) return;

    // 供应商→模型级联
    const providerSelect = configRoot.querySelector('select');
    const modelSelect = configRoot.querySelectorAll('select')[1];
    if (providerSelect && modelSelect) {
        const modelMap = {
            'OpenAI': ['GPT-4o', 'GPT-4o-mini', 'GPT-4-Turbo', 'o1-preview'],
            '文心一言': ['ERNIE-4.0-Turbo', 'ERNIE-4.0', 'ERNIE-3.5-SE'],
            '通义千问': ['Qwen-Max', 'Qwen-Plus', 'Qwen-Turbo', 'Qwen-Long'],
            'Claude': ['Claude-Opus-4', 'Claude-Sonnet-4', 'Claude-Haiku'],
            'DeepSeek': ['DeepSeek-V3', 'DeepSeek-R1', 'DeepSeek-Chat'],
        };
        providerSelect.addEventListener('change', () => {
            const provider = providerSelect.options[providerSelect.selectedIndex]?.text || '';
            const models = modelMap[provider] || ['默认模型'];
            modelSelect.innerHTML = models.map((m) => `<option>${m}</option>`).join('');
            showToast(`已切换至 ${provider}`, 'info');
        });
    }

    // 提示词字数统计
    configRoot.querySelectorAll('textarea').forEach((ta) => {
        const counter = document.createElement('div');
        counter.className = 'subtle textarea-counter';
        counter.textContent = `${ta.value.length} 字`;
        ta.parentElement.appendChild(counter);
        ta.addEventListener('input', () => {
            counter.textContent = `${ta.value.length} 字`;
        });
    });

    // 保存按钮
    const saveBtn = configRoot.querySelector('.primary-button');
    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            showToast('AI 配置已保存并应用', 'success');
            addNotification('配置更新', 'AI 运行配置已更新，新参数将在下次生成时生效。', 'success');
        });
    }

    // 连接测试按钮
    const testBtn = configRoot.querySelector('.secondary-button');
    if (testBtn) {
        testBtn.addEventListener('click', () => {
            testBtn.disabled = true;
            testBtn.textContent = '测试中…';
            setTimeout(() => {
                testBtn.disabled = false;
                testBtn.textContent = '连接测试';
                showToast('连接测试通过 ✓  延迟 128ms', 'success');
            }, 1200);
        });
    }
}

/* ═══════════════════════════════════════════════
   Mock 数据引擎
   ═══════════════════════════════════════════════ */
const mockData = {
    chartTrend: () => Array.from({ length: 14 }, (_, i) => ({ day: i + 1, value: 40 + Math.floor(Math.random() * 60) })),
    chartBar: () => ['口播', '封面', 'B-roll', '字幕', '音频', '商品图'].map((label) => ({ label, value: 10 + Math.floor(Math.random() * 90) })),
    chartPie: () => {
        const slices = [
            { label: '视频', color: '#00f2ea' },
            { label: '图片', color: '#ff6b6b' },
            { label: '字幕', color: '#ffd93d' },
            { label: '音频', color: '#6bcb77' },
            { label: '其他', color: '#8b5cf6' },
        ];
        let remaining = 100;
        return slices.map((s, i) => {
            const val = i === slices.length - 1 ? remaining : Math.min(remaining, 10 + Math.floor(Math.random() * 30));
            remaining -= val;
            return { ...s, value: val };
        });
    },
};

/* ═══════════════════════════════════════════════
   Canvas 图表渲染
   ═══════════════════════════════════════════════ */
