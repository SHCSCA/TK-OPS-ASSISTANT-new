function renderCharts() {
    const mainHost = document.getElementById('mainHost');
    mainHost.querySelectorAll('.chart-placeholder').forEach((placeholder) => {
        const canvas = document.createElement('canvas');
        const logicW = placeholder.clientWidth || 400;
        const logicH = placeholder.clientHeight || 200;
        const dpr = window.devicePixelRatio || 2;
        canvas.width = logicW * dpr;
        canvas.height = logicH * dpr;
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        placeholder.textContent = '';
        placeholder.appendChild(canvas);
        placeholder.style.fontSize = '0';

        const ctx = canvas.getContext('2d');
        ctx.scale(dpr, dpr);
        const parent = placeholder.closest('.analytics-chart-panel, .panel');
        const toggles = parent?.querySelectorAll('.analytics-chart-toggles button, .segmented button');
        const activeToggle = parent?.querySelector('.analytics-chart-toggles button.is-active, .segmented button.is-active');
        const mode = activeToggle?.textContent.trim() || '趋势';

        if (mode.includes('分布') || mode.includes('占比')) {
            drawPieChart(ctx, logicW, logicH);
        } else if (mode.includes('对比') || mode.includes('柱')) {
            drawBarChart(ctx, logicW, logicH);
        } else {
            drawTrendChart(ctx, logicW, logicH);
        }

        // 切换重绘
        if (toggles) {
            toggles.forEach((btn) => {
                btn.addEventListener('click', () => {
                    const m = btn.textContent.trim();
                    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
                    ctx.clearRect(0, 0, logicW, logicH);
                    if (m.includes('分布') || m.includes('占比')) drawPieChart(ctx, logicW, logicH);
                    else if (m.includes('对比') || m.includes('柱')) drawBarChart(ctx, logicW, logicH);
                    else drawTrendChart(ctx, logicW, logicH);
                });
            });
        }
    });
}

function drawTrendChart(ctx, w, h) {
    const data = mockData.chartTrend();
    const padding = { top: 20, right: 20, bottom: 30, left: 40 };
    const chartW = w - padding.left - padding.right;
    const chartH = h - padding.top - padding.bottom;
    const max = Math.max(...data.map((d) => d.value));
    const isDark = document.body.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#94a3b8' : '#64748b';
    const gridColor = isDark ? 'rgba(148,163,184,0.1)' : 'rgba(0,0,0,0.06)';

    // 网格
    ctx.strokeStyle = gridColor;
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
        const y = padding.top + (chartH / 4) * i;
        ctx.beginPath(); ctx.moveTo(padding.left, y); ctx.lineTo(w - padding.right, y); ctx.stroke();
        ctx.fillStyle = textColor; ctx.font = '12px system-ui, sans-serif'; ctx.textAlign = 'right';
        ctx.fillText(Math.round(max - (max / 4) * i), padding.left - 6, y + 4);
    }

    // 面积
    const gradient = ctx.createLinearGradient(0, padding.top, 0, h - padding.bottom);
    gradient.addColorStop(0, 'rgba(0, 242, 234, 0.25)');
    gradient.addColorStop(1, 'rgba(0, 242, 234, 0.02)');
    ctx.beginPath();
    ctx.moveTo(padding.left, h - padding.bottom);
    data.forEach((d, i) => {
        const x = padding.left + (chartW / (data.length - 1)) * i;
        const y = padding.top + chartH * (1 - d.value / max);
        ctx.lineTo(x, y);
    });
    ctx.lineTo(padding.left + chartW, h - padding.bottom);
    ctx.closePath();
    ctx.fillStyle = gradient;
    ctx.fill();

    // 线条
    ctx.beginPath();
    ctx.strokeStyle = '#00f2ea';
    ctx.lineWidth = 2;
    data.forEach((d, i) => {
        const x = padding.left + (chartW / (data.length - 1)) * i;
        const y = padding.top + chartH * (1 - d.value / max);
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // 点
    data.forEach((d, i) => {
        const x = padding.left + (chartW / (data.length - 1)) * i;
        const y = padding.top + chartH * (1 - d.value / max);
        ctx.beginPath(); ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fillStyle = '#00f2ea'; ctx.fill();
        ctx.strokeStyle = isDark ? '#1e293b' : '#ffffff'; ctx.lineWidth = 2; ctx.stroke();
    });

    // X轴标签
    ctx.fillStyle = textColor; ctx.font = '12px system-ui, sans-serif'; ctx.textAlign = 'center';
    data.forEach((d, i) => {
        if (i % 2 === 0) {
            const x = padding.left + (chartW / (data.length - 1)) * i;
            ctx.fillText(`D${d.day}`, x, h - padding.bottom + 16);
        }
    });
}

function drawBarChart(ctx, w, h) {
    const data = mockData.chartBar();
    const padding = { top: 20, right: 20, bottom: 40, left: 40 };
    const chartW = w - padding.left - padding.right;
    const chartH = h - padding.top - padding.bottom;
    const max = Math.max(...data.map((d) => d.value));
    const barW = chartW / data.length * 0.6;
    const gap = chartW / data.length * 0.4;
    const isDark = document.body.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#94a3b8' : '#64748b';
    const colors = ['#00f2ea', '#ff6b6b', '#ffd93d', '#6bcb77', '#8b5cf6', '#f472b6'];

    data.forEach((d, i) => {
        const x = padding.left + (chartW / data.length) * i + gap / 2;
        const barH = (d.value / max) * chartH;
        const y = padding.top + chartH - barH;
        const grad = ctx.createLinearGradient(x, y, x, y + barH);
        grad.addColorStop(0, colors[i % colors.length]);
        grad.addColorStop(1, colors[i % colors.length] + '66');
        ctx.fillStyle = grad;
        ctx.beginPath();
        const r = 4;
        ctx.moveTo(x + r, y); ctx.lineTo(x + barW - r, y);
        ctx.quadraticCurveTo(x + barW, y, x + barW, y + r);
        ctx.lineTo(x + barW, y + barH); ctx.lineTo(x, y + barH);
        ctx.lineTo(x, y + r);
        ctx.quadraticCurveTo(x, y, x + r, y);
        ctx.fill();

        ctx.fillStyle = textColor; ctx.font = '12px system-ui, sans-serif'; ctx.textAlign = 'center';
        ctx.fillText(d.label, x + barW / 2, h - padding.bottom + 16);
        ctx.font = 'bold 12px system-ui, sans-serif';
        ctx.fillText(d.value, x + barW / 2, y - 6);
    });
}

function drawPieChart(ctx, w, h) {
    const data = mockData.chartPie();
    const cx = w / 2;
    const cy = h / 2;
    const r = Math.min(cx, cy) - 30;
    const isDark = document.body.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#e2e8f0' : '#334155';
    let startAngle = -Math.PI / 2;
    const total = data.reduce((sum, d) => sum + d.value, 0);

    data.forEach((d) => {
        const sliceAngle = (d.value / total) * Math.PI * 2;
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.arc(cx, cy, r, startAngle, startAngle + sliceAngle);
        ctx.closePath();
        ctx.fillStyle = d.color;
        ctx.fill();
        ctx.strokeStyle = isDark ? '#1e293b' : '#ffffff';
        ctx.lineWidth = 2;
        ctx.stroke();

        // 标签
        const mid = startAngle + sliceAngle / 2;
        const labelR = r * 0.7;
        const lx = cx + Math.cos(mid) * labelR;
        const ly = cy + Math.sin(mid) * labelR;
        ctx.fillStyle = textColor;
        ctx.font = 'bold 12px system-ui, sans-serif';
        ctx.textAlign = 'center';
        if (d.value > 5) {
            ctx.fillText(`${d.label}`, lx, ly - 4);
            ctx.font = '11px system-ui, sans-serif';
            ctx.fillText(`${d.value}%`, lx, ly + 10);
        }
        startAngle += sliceAngle;
    });

    // 中心空心
    ctx.beginPath();
    ctx.arc(cx, cy, r * 0.4, 0, Math.PI * 2);
    ctx.fillStyle = isDark ? '#1e293b' : '#ffffff';
    ctx.fill();
}

/* ═══════════════════════════════════════════════
   分析页交互绑定
   ═══════════════════════════════════════════════ */
