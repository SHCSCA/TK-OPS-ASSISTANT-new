function bindAnalyticsInteractions() {
    const mainHost = document.getElementById('mainHost');
    if (!mainHost) return;
    if (mainHost.dataset.analyticsBound === '1') return;
    mainHost.dataset.analyticsBound = '1';

    const seed = window.__tkopsAnalyticsSeed || {};

    function createAnalyticsTask(title, summary) {
        if (!window.api || !window.api.tasks || typeof window.api.tasks.create !== 'function') return Promise.resolve(null);
        return window.api.tasks.create({
            title,
            task_type: 'analytics_action',
            priority: 'medium',
            status: 'pending',
            result_summary: summary,
        }).catch(() => null);
    }

    function persistAnalyticsSetting(key, value) {
        if (!window.api || !window.api.settings || typeof window.api.settings.set !== 'function') return;
        window.api.settings.set(key, String(value)).catch(() => null);
    }

    function updateSideInsight(message) {
        const first = document.querySelector('#detailHost .panel .detail-item strong');
        if (first) first.textContent = message;
        const fallback = document.querySelector('#detailHost .panel .subtle');
        if (!first && fallback) fallback.textContent = message;
    }
    // — 通用：data-source-item / chart-type-btn 选中切换
    mainHost.querySelectorAll('.data-source-list, .report-template-list').forEach(list => {
        list.querySelectorAll('.data-source-item').forEach(item => {
            item.addEventListener('click', () => {
                list.querySelectorAll('.data-source-item').forEach(i => i.classList.remove('is-selected'));
                item.classList.add('is-selected');
                const name = item.querySelector('strong')?.textContent || '';
                const preview = mainHost.querySelector('.report-preview-table div span');
                if (preview) preview.textContent = '当前模板：' + name + '，可直接发起导出。';
                persistAnalyticsSetting('analytics.report_template', name);
                createAnalyticsTask('报表模板切换', '已切换到模板：' + name);
                if (typeof showToast === 'function') showToast('已切换: ' + name, 'info');
            });
        });
    });

    mainHost.querySelectorAll('.chart-type-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            mainHost.querySelectorAll('.chart-type-btn').forEach(b => b.classList.remove('is-selected'));
            btn.classList.add('is-selected');
            const mode = btn.textContent.trim();
            persistAnalyticsSetting('analytics.chart_type', mode);
            showToast('图表类型: ' + mode, 'info');
        });
    });

    // — 蓝海分析：气泡点击 → 更新右侧详情卡
    mainHost.querySelectorAll('.matrix-bubble').forEach(bubble => {
        bubble.addEventListener('click', () => {
            mainHost.querySelectorAll('.matrix-bubble').forEach(b => b.classList.remove('is-active'));
            bubble.classList.add('is-active');
            const name = bubble.textContent.trim();
            const row = (seed.blueOcean || []).find(x => x && x.label === name) || {};
            const heat = row.heat || 68;
            const comp = row.competition || 32;
            const margin = row.margin || 24;
            const detailCard = mainHost.querySelector('.opportunity-detail-card');
            if (detailCard) {
                detailCard.querySelector('strong').textContent = name;
                const items = detailCard.querySelectorAll('.detail-item strong');
                if (items[0]) items[0].textContent = heat;
                if (items[1]) items[1].textContent = comp;
                if (items[2]) items[2].textContent = margin + '%';
                const desc = detailCard.querySelector('p');
                if (desc) desc.textContent = heat > 70
                    ? '高热度品类，建议优先布局内容和选品测试。'
                    : comp > 40
                        ? '竞争偏强，需差异化切入或观望。'
                        : '潜力赛道，适合小批量验证后放量。';
            }
            createAnalyticsTask('蓝海主题聚焦', name + ' / 热度 ' + heat + ' / 利润率 ' + margin + '%');
            showToast('选中: ' + bubble.textContent.trim(), 'success');
        });
    });

    // — 竞品监控：竞品卡选中切换 + 趋势高亮
    mainHost.querySelectorAll('.rival-card').forEach(card => {
        card.addEventListener('click', () => {
            mainHost.querySelectorAll('.rival-card').forEach(c => c.classList.remove('is-active'));
            card.classList.add('is-active');
            const name = card.querySelector('strong')?.textContent || '竞品';
            const followers = card.querySelector('span')?.textContent || '-';
            updateSideInsight('竞品“' + name + '”已设为观察对象，当前规模 ' + followers + '。');
            persistAnalyticsSetting('analytics.rival_focus', name);
            createAnalyticsTask('竞品聚焦', '已聚焦竞品：' + name + ' / 规模 ' + followers);
            showToast('查看竞品: ' + name, 'info');
        });
    });

    // — 电商转化：漏斗步骤点击高亮 + 更新流失面板
    mainHost.querySelectorAll('.funnel-step').forEach(step => {
        step.addEventListener('click', () => {
            mainHost.querySelectorAll('.funnel-step').forEach(s => s.classList.remove('is-active'));
            step.classList.add('is-active');
            const stage = step.querySelector('span')?.textContent || '漏斗阶段';
            const value = step.querySelector('strong')?.textContent || '-';
            updateSideInsight('当前聚焦“' + stage + '”，样本量 ' + value + '。');
            persistAnalyticsSetting('analytics.funnel_stage', stage);
            createAnalyticsTask('漏斗阶段复盘', '聚焦阶段：' + stage + ' / 规模 ' + value);
            showToast('聚焦阶段: ' + stage, 'info');
        });
    });

    // — 互动分析：热力图格子高亮
    mainHost.querySelectorAll('.heatmap-cell').forEach(cell => {
        cell.addEventListener('click', () => {
            mainHost.querySelectorAll('.heatmap-cell').forEach(c => c.classList.remove('is-active'));
            cell.classList.add('is-active');
            const level = String(cell.className || '').match(/lvl-(\d)/);
            const v = level ? level[1] : '3';
            updateSideInsight('互动热力格已锁定，热度等级 L' + v + '。');
            persistAnalyticsSetting('analytics.heat_level', v);
            createAnalyticsTask('热力格复核', '互动热度等级 L' + v + ' 已标记复核');
        });
    });

    // — 粉丝画像：Persona 卡片选中
    mainHost.querySelectorAll('.persona-grid article').forEach(card => {
        card.addEventListener('click', () => {
            mainHost.querySelectorAll('.persona-grid article').forEach(c => c.classList.remove('is-active'));
            card.classList.add('is-active');
            const persona = card.querySelector('strong')?.textContent || '画像';
            updateSideInsight('画像“' + persona + '”已设为当前运营目标。');
            persistAnalyticsSetting('analytics.persona_focus', persona);
            createAnalyticsTask('粉丝画像聚焦', '已聚焦画像：' + persona);
            showToast('查看画像: ' + persona, 'info');
        });
    });

    // — 流量看板：来源卡片选中
    mainHost.querySelectorAll('.traffic-source-card').forEach(card => {
        card.addEventListener('click', () => {
            mainHost.querySelectorAll('.traffic-source-card').forEach(c => c.classList.remove('is-active'));
            card.classList.add('is-active');
            const src = card.querySelector('.subtle')?.textContent || '流量来源';
            updateSideInsight('流量来源已切换：' + src + '。');
            persistAnalyticsSetting('analytics.traffic_focus', src);
            createAnalyticsTask('流量来源复盘', '已聚焦来源：' + src);
            showToast('聚焦: ' + src, 'info');
        });
    });

    // — 报表中心：步骤卡片选中
    mainHost.querySelectorAll('.report-builder-steps article').forEach(step => {
        step.addEventListener('click', () => {
            mainHost.querySelectorAll('.report-builder-steps article').forEach(s => s.classList.remove('is-active'));
            step.classList.add('is-active');
            const stepName = step.querySelector('strong')?.textContent || step.textContent.trim() || '报表步骤';
            updateSideInsight('报表流程已进入：' + stepName + '。');
            persistAnalyticsSetting('analytics.report_step', stepName);
            createAnalyticsTask('报表流程推进', '当前步骤：' + stepName);
        });
    });

    // — 利润分析：成本结构卡片选中
    mainHost.querySelectorAll('.profit-ledger-grid article').forEach(card => {
        card.addEventListener('click', () => {
            mainHost.querySelectorAll('.profit-ledger-grid article').forEach(c => c.classList.remove('is-active'));
            card.classList.add('is-active');
            const costType = card.querySelector('span')?.textContent || '成本项';
            const ratio = card.querySelector('strong')?.textContent || '-';
            updateSideInsight('成本项“' + costType + '”占比 ' + ratio + '，已进入优化队列。');
            persistAnalyticsSetting('analytics.cost_focus', costType);
            createAnalyticsTask('成本结构优化', '聚焦成本项：' + costType + ' / 占比 ' + ratio);
            showToast('查看成本: ' + costType, 'info');
        });
    });
}

/* ═══════════════════════════════════════════════
   分析页 Canvas 图表渲染
   ═══════════════════════════════════════════════ */
function renderAnalyticsCanvases() {
    const isDark = document.body.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#94a3b8' : '#64748b';
    const brand = '#00f2ea';

    // — 流量趋势带
    renderTrendCanvas('.traffic-trend-board', '流量趋势', isDark, textColor, brand);

    // — 可视化实验室预览
    renderTrendCanvas('.visual-preview-stage', '实验数据', isDark, textColor, brand);

    // — 利润双柱画布
    renderProfitBars(isDark, textColor);

    // — 报表预览画布
    renderTrendCanvas('.report-preview-chart', '报表预览', isDark, textColor, brand);

    // — 竞品趋势柱
    renderRivalBars(isDark);

    // — 互动热力图颜色随机化（模拟真实数据）
    const seed = window.__tkopsAnalyticsSeed || {};

    // — 互动热力图使用 seed（无 seed 时保持稳定模式）
    document.querySelectorAll('.heatmap-cell').forEach((cell, idx) => {
        const list = seed.heatmap || [2, 3, 4, 3, 2];
        const lvl = Math.max(1, Math.min(5, list[idx % list.length] || 3));
        cell.className = 'heatmap-cell lvl-' + lvl;
    });

    // — 粉丝亲和力条动态化
    // — 粉丝亲和力条使用 seed
    document.querySelectorAll('.affinity-bars i').forEach((bar, idx) => {
        const list = seed.affinity || [78, 66, 44, 24];
        const pct = Math.max(12, Math.min(96, list[idx % list.length] || 30));
        bar.style.width = pct + '%';
    });

    // — 电商转化漏斗动态化
    // — 电商转化漏斗使用 seed
    document.querySelectorAll('.funnel-step strong').forEach((el, idx) => {
        const list = seed.funnel || [2840000, 136000, 24000, 8436, 7982];
        const value = list[idx] || 0;
        el.textContent = value >= 10000 ? (value / 10000).toFixed(1) + '万' : value.toLocaleString();
    });
}

function renderTrendCanvas(containerSelector, label, isDark, textColor, brand) {
    const container = document.querySelector(containerSelector);
    if (!container) return;
    // 如果容器里已经有 canvas 就先删除
    const existing = container.querySelector('canvas');
    if (existing) existing.remove();

    const canvas = document.createElement('canvas');
    const w = container.clientWidth || 420;
    const h = container.clientHeight || 260;
    canvas.width = w * 2;
    canvas.height = h * 2;
    canvas.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;pointer-events:none;';
    container.style.position = 'relative';
    container.appendChild(canvas);
    const ctx = canvas.getContext('2d');
    ctx.scale(2, 2);

    // 绘制网格
    ctx.strokeStyle = isDark ? 'rgba(148,163,184,0.08)' : 'rgba(0,0,0,0.04)';
    ctx.lineWidth = 1;
    for (let i = 0; i < 6; i++) {
        const y = 20 + (h - 60) * i / 5;
        ctx.beginPath(); ctx.moveTo(30, y); ctx.lineTo(w - 10, y); ctx.stroke();
    }

    const seed = window.__tkopsAnalyticsSeed || {};
    const seedMap = {
        '.traffic-trend-board': seed.trafficTrend,
        '.visual-preview-stage': seed.visualTrend,
        '.report-preview-chart': seed.reportTrend,
    };

    // 生成数据并绘线
    const pts = 14;
    const source = seedMap[containerSelector] || [];
    const data = Array.from({length: pts}, (_, i) => {
        const v = source[i % Math.max(1, source.length)] || (22 + i * 2);
        return Math.max(20, Math.min(h - 80, Number(v) || 20));
    });
    const stepX = (w - 50) / (pts - 1);

    // 渐变区域
    const grad = ctx.createLinearGradient(0, 20, 0, h - 30);
    grad.addColorStop(0, isDark ? 'rgba(0,242,234,0.22)' : 'rgba(0,242,234,0.18)');
    grad.addColorStop(1, 'transparent');
    ctx.beginPath();
    ctx.moveTo(35, h - 30 - data[0]);
    for (let i = 1; i < pts; i++) ctx.lineTo(35 + i * stepX, h - 30 - data[i]);
    ctx.lineTo(35 + (pts - 1) * stepX, h - 30);
    ctx.lineTo(35, h - 30);
    ctx.closePath();
    ctx.fillStyle = grad;
    ctx.fill();

    // 折线
    ctx.beginPath();
    ctx.moveTo(35, h - 30 - data[0]);
    for (let i = 1; i < pts; i++) ctx.lineTo(35 + i * stepX, h - 30 - data[i]);
    ctx.strokeStyle = brand;
    ctx.lineWidth = 2.5;
    ctx.lineJoin = 'round';
    ctx.stroke();

    // 数据点
    data.forEach((d, i) => {
        ctx.beginPath();
        ctx.arc(35 + i * stepX, h - 30 - d, 3.5, 0, Math.PI * 2);
        ctx.fillStyle = brand;
        ctx.fill();
        ctx.beginPath();
        ctx.arc(35 + i * stepX, h - 30 - d, 1.8, 0, Math.PI * 2);
        ctx.fillStyle = isDark ? '#1e293b' : '#ffffff';
        ctx.fill();
    });

    // 标签
    ctx.font = '11px system-ui, sans-serif';
    ctx.fillStyle = textColor;
    ctx.textAlign = 'center';
    for (let i = 0; i < pts; i += 2) {
        ctx.fillText('D' + (i + 1), 35 + i * stepX, h - 10);
    }
}

function renderProfitBars(isDark, textColor) {
    const container = document.querySelector('.profit-bar-compare');
    if (!container) return;
    const seed = window.__tkopsAnalyticsSeed || {};
    const list = seed.profitBars || [52, 74];
    const groups = container.querySelectorAll('.compare-group');
    groups.forEach((group, groupIdx) => {
        const bars = group.querySelectorAll('i');
        bars.forEach((bar, idx) => {
            const base = list[(groupIdx + idx) % list.length] || 58;
            const pct = Math.max(24, Math.min(92, Number(base)));
            bar.style.height = pct + '%';
        });
    });
}

function renderRivalBars(isDark) {
    const container = document.querySelector('.rival-trend-bars');
    if (!container) return;
    const seed = window.__tkopsAnalyticsSeed || {};
    const list = seed.rivalBars || [36, 48, 62, 72, 58, 44];
    container.querySelectorAll('i').forEach((bar, idx) => {
        const pct = Math.max(22, Math.min(96, list[idx % list.length] || 40));
        bar.style.height = pct + '%';
    });
}

/* ═══════════════════════════════════════════════
   骨架屏 & 路由过渡动画
   ═══════════════════════════════════════════════ */
