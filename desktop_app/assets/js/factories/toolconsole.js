function makeToolConsoleRoute(config) {
    const metrics = config.metrics || [
        { label: `${config.title}状态`, value: '正常', delta: '稳定', note: '无异常', color: 'var(--status-success)', search: `${config.title} 状态` },
        { label: '待处理', value: '3', delta: '需关注', note: '建议人工复核', color: 'var(--status-warning)', search: `${config.title} 待处理` },
        { label: '健康度', value: '98%', delta: '+2%', note: '近 7 天稳定', color: 'var(--brand-primary)', search: `${config.title} 健康度` },
    ];
    const items = config.items || [
        { title: `${config.title}主操作`, desc: '当前最需执行的操作。', badge: '执行', tone: 'success', search: `${config.title} 主操作` },
        { title: `${config.title}异常`, desc: '待修复的异常项。', badge: '告警', tone: 'warning', search: `${config.title} 异常` },
        { title: `${config.title}维护`, desc: '例行维护建议。', badge: '维护', tone: 'info', search: `${config.title} 维护` },
    ];
    const cards = config.cards || [
        { title: '运行状态', desc: `${config.title}各组件运行正常。`, badge: '正常', tone: 'success', search: `${config.title} 正常` },
        { title: '待处理项', desc: '有少量待确认事项。', badge: '待确认', tone: 'warning', search: `${config.title} 待确认` },
        { title: '维护建议', desc: '例行维护建议。', badge: '维护', tone: 'info', search: `${config.title} 维护` },
    ];
    const detailItems = config.detailItems || ['系统运行正常', '部分组件需关注', '建议执行例行维护'];
    const formFields = config.formFields || [
        { label: '策略名称', value: `${config.title}默认配置` },
        { label: '目标对象', value: '当前工作区' },
        { label: '执行模式', value: '自动' },
    ];
    const stripItems = config.stripItems || ['运行状态', '最近事件', '维护建议'];

    const metricsHtml = metrics.map(m => `<article class="stat-card" data-search="${m.search}"><div><div class="subtle">${m.label}</div><div class="stat-card__value">${m.value}</div></div><div class="stat-card__delta" style="color:${m.color};"><span>${m.delta}</span><span class="subtle">${m.note}</span></div></article>`).join('');
    const stripHtml = stripItems.map(s => `<div class="timeline-chip"><strong>${s}</strong><div class="subtle">${config.title} 保持同步</div></div>`).join('');
    const itemsHtml = items.map((it, i) => `<div class="task-item ${i === 0 ? 'is-selected' : ''}" data-search="${it.search}"><div><strong>${it.title}</strong><div class="subtle">${it.desc}</div></div><span class="pill ${it.tone}">${it.badge}</span></div>`).join('');
    const cardsHtml = cards.map(c => `<article class="board-card" data-search="${c.search}"><strong>${c.title}</strong><div class="subtle">${c.desc}</div><div class="status-strip"><span class="pill ${c.tone}">${c.badge}</span></div></article>`).join('');
    const formHtml = formFields.map(f => `<div class="form-field"><label>${f.label}</label><input type="text" value="${f.value}"></div>`).join('');
    const tableHtml = config.table
        ? `<section class="table-card"><div class="table-card__header"><div><strong>${config.table.title}</strong><div class="subtle">${config.table.description}</div></div></div><div class="table-wrapper"><table><thead><tr>${config.table.columns.map(c => `<th>${c}</th>`).join('')}</tr></thead><tbody>${config.table.rows.map(r => `<tr class="route-row" data-search="${r.search}">${r.cells.map(c => `<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table></div></section>`
        : '';

    const mainHtml = `
        <div class="breadcrumbs"><span>system</span><span>/</span><span>${config.title}</span></div>
        <div class="page-header">
            <div><div class="eyebrow">${config.headerEyebrow}</div><h1>${config.title}</h1><p>${config.description}</p></div>
            <div class="header-actions"><button class="secondary-button" type="button">${config.secondaryAction}</button><button class="primary-button" type="button">${config.primaryAction}</button></div>
        </div>
        <section class="section-stack">
            <div class="stat-grid">${metricsHtml}</div>
            <div class="tool-console-shell">
                <div class="tool-status-strip">${stripHtml}</div>
                <div class="tool-console-body">
                    <div class="tool-main-area">
                        <section class="panel"><div class="panel__header"><div><strong>${config.title}控制台</strong><div class="subtle">核心操作面板</div></div></div><div class="tool-operation-area"><div class="settings-grid">${formHtml}</div><div class="workbench-list">${itemsHtml}</div></div></section>
                        ${tableHtml}
                    </div>
                    <aside class="tool-side-panel">
                        <section class="panel"><div class="panel__header"><div><strong>状态面板</strong><div class="subtle">组件健康与运行指标</div></div></div><div class="board-list">${cardsHtml.replaceAll('board-card', 'settings-card')}</div></section>
                    </aside>
                </div>
            </div>
        </section>
    `;

    return {
        eyebrow: config.eyebrow,
        searchTerms: `${config.title} ${config.description} system ${config.eyebrow}`,
        sidebarSummary: config.sidebarSummary || { eyebrow: `${config.title}提醒`, title: `${config.title}运行正常`, copy: `${config.title}各组件状态稳定。` },
        statusLeft: config.statusLeft || [`${config.title} 正常`, '系统稳定', '最近检测 12:48'],
        statusRight: config.statusRight || [{ text: '运行正常', tone: 'success' }, { text: '待处理 1', tone: 'warning' }],
        mainHtml,
        detailHtml: `<div class="detail-root"><section class="panel"><div class="panel__header"><div><strong>${config.title}摘要</strong><div class="subtle">${config.detailDesc || '系统状态与维护概况。'}</div></div></div><div class="detail-list">${detailItems.map((d, i) => `<div class="detail-item"><span class="subtle">${i === 0 ? '当前状态' : i === 1 ? '待处理' : '建议'}</span><strong>${d}</strong></div>`).join('')}</div></section><section class="panel"><div class="panel__header"><div><strong>维护动作</strong><div class="subtle">推荐执行的维护操作</div></div></div><div class="board-list">${cardsHtml}</div></section></div>`,
    };
}

