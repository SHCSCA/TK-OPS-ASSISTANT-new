function makeTaskOpsRoute(config) {
    const metrics = config.metrics || [
        { label: `${config.title}总量`, value: '24', delta: '+3', note: '本周期推进稳定', color: 'var(--status-success)', search: `${config.title} 总量` },
        { label: '异常项', value: '3', delta: '需关注', note: '高风险需人工复核', color: 'var(--status-warning)', search: `${config.title} 异常` },
        { label: '执行率', value: '86%', delta: '+5%', note: '较上周期改善', color: 'var(--brand-primary)', search: `${config.title} 执行率` },
    ];
    const items = config.items || [
        { title: `${config.title}主任务`, desc: '当前优先级最高的动作。', badge: '优先', tone: 'success', search: `${config.title} 主任务` },
        { title: `${config.title}异常项`, desc: '建议先处理高风险节点。', badge: '告警', tone: 'warning', search: `${config.title} 异常项` },
        { title: `${config.title}后续建议`, desc: '完成当前动作后继续下钻。', badge: '建议', tone: 'info', search: `${config.title} 建议` },
    ];
    const cards = config.cards || [
        { title: '今日优先', desc: `围绕${config.title}处理最高影响动作。`, badge: '跟进', tone: 'warning', search: `${config.title} 今日` },
        { title: '历史记录', desc: '查看过往执行记录。', badge: '参考', tone: 'info', search: `${config.title} 历史` },
        { title: '结果沉淀', desc: '执行完成后沉淀结果。', badge: '复盘', tone: 'success', search: `${config.title} 复盘` },
    ];
    const detailItems = config.detailItems || ['当前状态稳定', '仍有风险待处理', '建议先处理高影响动作'];
    const filterTabs = config.filterTabs || ['全部', '运行中', '暂停', '失败', '已完成'];

    const metricsHtml = metrics.map(m => `<article class="stat-card" data-search="${m.search}"><div><div class="subtle">${m.label}</div><div class="stat-card__value">${m.value}</div></div><div class="stat-card__delta" style="color:${m.color};"><span>${m.delta}</span><span class="subtle">${m.note}</span></div></article>`).join('');
    const itemsHtml = items.map((it, i) => `<div class="task-item ${i === 0 ? 'is-selected' : ''}" data-search="${it.search}"><div><strong>${it.title}</strong><div class="subtle">${it.desc}</div></div><span class="pill ${it.tone}">${it.badge}</span></div>`).join('');
    const cardsHtml = cards.map(c => `<article class="board-card" data-search="${c.search}"><strong>${c.title}</strong><div class="subtle">${c.desc}</div><div class="status-strip"><span class="pill ${c.tone}">${c.badge}</span></div></article>`).join('');
    const filterHtml = filterTabs.map((t, i) => `<button class="task-filter-tab ${i === 0 ? 'is-active' : ''}" type="button">${t}</button>`).join('');

    const kanbanHtml = config.kanban
        ? `<div class="kanban-grid">${config.kanban.map(col => `<section class="kanban-column"><div class="kanban-column__title">${col.title}</div><div class="kanban-list">${col.items.map(it => `<article class="ticket-card" data-search="${it.search}"><strong>${it.title}</strong><div class="subtle">${it.desc}</div></article>`).join('')}</div></section>`).join('')}</div>`
        : '';
    const calendarHtml = config.calendarDays
        ? `<div class="calendar-grid">${config.calendarDays.map(day => `<section class="calendar-day"><strong>${day.title}</strong><div class="subtle">${day.subtle}</div>${day.slots.map(s => `<div class="calendar-slot" data-search="${s.search}">${s.title}</div>`).join('')}</section>`).join('')}</div>`
        : '';
    const tableHtml = config.table
        ? `<section class="table-card"><div class="table-card__header"><div><strong>${config.table.title}</strong><div class="subtle">${config.table.description}</div></div></div><div class="table-wrapper"><table><thead><tr>${config.table.columns.map(c => `<th>${c}</th>`).join('')}</tr></thead><tbody>${config.table.rows.map(r => `<tr class="route-row" data-search="${r.search}">${r.cells.map(c => `<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table></div></section>`
        : '';

    const centerContent = kanbanHtml || calendarHtml || `<div class="kanban-grid"><section class="kanban-column"><div class="kanban-column__title">待执行</div><div class="kanban-list">${itemsHtml}</div></section><section class="kanban-column"><div class="kanban-column__title">进行中</div><div class="kanban-list">${cardsHtml}</div></section><section class="kanban-column"><div class="kanban-column__title">已完成</div><div class="kanban-list">${cardsHtml.replaceAll('board-card', 'ticket-card')}</div></section></div>`;

    const mainHtml = `
        <div class="breadcrumbs"><span>automation</span><span>/</span><span>${config.title}</span></div>
        <div class="page-header">
            <div><div class="eyebrow">${config.headerEyebrow}</div><h1>${config.title}</h1><p>${config.description}</p></div>
            <div class="header-actions"><button class="secondary-button" type="button">${config.secondaryAction}</button><button class="primary-button" type="button">${config.primaryAction}</button></div>
        </div>
        <section class="section-stack">
            <div class="stat-grid">${metricsHtml}</div>
            <div class="task-ops-shell">
                <div class="task-filter-bar">${filterHtml}<div class="task-view-toggles"><button class="task-view-btn is-active" type="button">看板</button><button class="task-view-btn" type="button">列表</button><button class="task-view-btn" type="button">日历</button></div></div>
                <div class="task-ops-body">
                    <div class="task-ops-main">
                        <section class="task-ops-canvas">${centerContent}</section>
                        ${tableHtml}
                    </div>
                </div>
            </div>
        </section>
    `;

    return {
        eyebrow: config.eyebrow,
        searchTerms: `${config.title} ${config.description} automation ${config.eyebrow}`,
        sidebarSummary: config.sidebarSummary || { eyebrow: `${config.title}提醒`, title: `${config.title}正在推进`, copy: `先处理${config.title}中的高影响动作。` },
        statusLeft: config.statusLeft || [`${config.title} 已接入`, '状态同步正常', '最近更新 12:48'],
        statusRight: config.statusRight || [{ text: '运行正常', tone: 'success' }, { text: '待复核 2', tone: 'warning' }],
        hideDetailPanel: false,
        mainHtml,
        detailHtml: `<div class="detail-root"><section class="panel"><div class="panel__header"><div><strong>${config.sideTitle || '运行属性'}</strong><div class="subtle">${config.sideDesc || '当前自动化链路的配置摘要。'}</div></div></div><div class="detail-list">${detailItems.map((d, i) => `<div class="detail-item"><span class="subtle">${i === 0 ? '当前状态' : i === 1 ? '阻塞点' : '建议'}</span><strong>${d}</strong></div>`).join('')}</div></section><section class="panel"><div class="panel__header"><div><strong>规则与配置</strong><div class="subtle">快速查看当前生效配置</div></div></div><div class="board-list">${cardsHtml}</div></section></div>`,
    };
}

/* ═══════════════════════════════════════════════
   Batch 4 — list-management 家族工厂
   Template B: 筛选条 + 主表格/列表 + 右侧详情
   ═══════════════════════════════════════════════ */
function makeListManagementRoute(config) {
    const metrics = config.metrics || [
        { label: `${config.title}总量`, value: '24', delta: '+3', note: '本周期稳定', color: 'var(--status-success)', search: `${config.title} 总量` },
        { label: '异常项', value: '3', delta: '需关注', note: '需人工复核', color: 'var(--status-warning)', search: `${config.title} 异常` },
        { label: '覆盖率', value: '86%', delta: '+5%', note: '较上周期改善', color: 'var(--brand-primary)', search: `${config.title} 覆盖率` },
    ];
    const items = config.items || [
        { title: `${config.title}主项`, desc: '当前优先处理对象。', badge: '优先', tone: 'success', search: `${config.title} 主项` },
        { title: `${config.title}异常项`, desc: '建议先处理高风险。', badge: '告警', tone: 'warning', search: `${config.title} 异常项` },
        { title: `${config.title}待跟进`, desc: '完成后继续下钻。', badge: '跟进', tone: 'info', search: `${config.title} 跟进` },
    ];
    const cards = config.cards || [
        { title: '今日优先', desc: `优先处理${config.title}高影响项。`, badge: '跟进', tone: 'warning', search: `${config.title} 今日` },
        { title: '历史记录', desc: '查看过往操作记录。', badge: '参考', tone: 'info', search: `${config.title} 历史` },
        { title: '结果沉淀', desc: '操作完成后沉淀为规范。', badge: '复盘', tone: 'success', search: `${config.title} 复盘` },
    ];
    const detailItems = config.detailItems || ['当前状态稳定', '部分项需复核', '建议先处理高优先级项'];
    const filterFields = config.filterFields || ['状态', '分类', '优先级'];

    const metricsHtml = metrics.map(m => `<article class="stat-card" data-search="${m.search}"><div><div class="subtle">${m.label}</div><div class="stat-card__value">${m.value}</div></div><div class="stat-card__delta" style="color:${m.color};"><span>${m.delta}</span><span class="subtle">${m.note}</span></div></article>`).join('');
    const itemsHtml = items.map((it, i) => `<div class="task-item ${i === 0 ? 'is-selected' : ''}" data-search="${it.search}"><div><strong>${it.title}</strong><div class="subtle">${it.desc}</div></div><span class="pill ${it.tone}">${it.badge}</span></div>`).join('');
    const cardsHtml = cards.map(c => `<article class="board-card" data-search="${c.search}"><strong>${c.title}</strong><div class="subtle">${c.desc}</div><div class="status-strip"><span class="pill ${c.tone}">${c.badge}</span></div></article>`).join('');
    const filterHtml = filterFields.map(f => `<select class="list-filter-select"><option>${f}: 全部</option></select>`).join('');

    const tableHtml = config.table
        ? `<section class="table-card"><div class="table-card__header"><div><strong>${config.table.title}</strong><div class="subtle">${config.table.description}</div></div></div><div class="table-wrapper"><table><thead><tr>${config.table.columns.map(c => `<th>${c}</th>`).join('')}</tr></thead><tbody>${config.table.rows.map(r => `<tr class="route-row" data-search="${r.search}">${r.cells.map(c => `<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table></div></section>`
        : '';

    const kanbanHtml = config.kanban
        ? `<div class="kanban-grid">${config.kanban.map(col => `<section class="kanban-column"><div class="kanban-column__title">${col.title}</div><div class="kanban-list">${col.items.map(it => `<article class="ticket-card" data-search="${it.search}"><strong>${it.title}</strong><div class="subtle">${it.desc}</div></article>`).join('')}</div></section>`).join('')}</div>`
        : '';

    const mainHtml = `
        <div class="breadcrumbs"><span>${config.breadcrumb}</span><span>/</span><span>${config.title}</span></div>
        <div class="page-header">
            <div><div class="eyebrow">${config.headerEyebrow}</div><h1>${config.title}</h1><p>${config.description}</p></div>
            <div class="header-actions"><button class="secondary-button" type="button">${config.secondaryAction}</button><button class="primary-button" type="button">${config.primaryAction}</button></div>
        </div>
        <section class="section-stack">
            <div class="stat-grid">${metricsHtml}</div>
            <div class="list-management-shell">
                <div class="list-toolbar"><div class="list-toolbar__search"><input type="text" placeholder="搜索${config.title}…" class="list-search-input"></div><div class="list-toolbar__filters">${filterHtml}</div></div>
                <div class="list-body">
                    <div class="list-main-area">
                        ${tableHtml || `<section class="panel"><div class="panel__header"><div><strong>${config.listTitle || config.title + '清单'}</strong><div class="subtle">${config.listDesc || '关键对象与状态一览'}</div></div></div><div class="workbench-list">${itemsHtml}</div></section>`}
                        ${kanbanHtml}
                    </div>
                </div>
            </div>
        </section>
    `;

    return {
        eyebrow: config.eyebrow,
        searchTerms: `${config.title} ${config.description} ${config.breadcrumb} ${config.eyebrow}`,
        audit: config.audit,
        sidebarSummary: config.sidebarSummary || { eyebrow: `${config.title}提醒`, title: `${config.title}正在推进`, copy: `先处理${config.title}中的高影响项。` },
        statusLeft: config.statusLeft || [`${config.title} 已接入`, '状态正常', '最近更新 12:48'],
        statusRight: config.statusRight || [{ text: '运行正常', tone: 'success' }, { text: '待复核 2', tone: 'warning' }],
        hideDetailPanel: false,
        mainHtml,
        detailHtml: `<div class="detail-root"><section class="panel"><div class="panel__header"><div><strong>${config.sideTitle || '详情面板'}</strong><div class="subtle">${config.sideDesc || '选中条目的详细信息'}</div></div></div><div class="detail-list">${detailItems.map((d, i) => `<div class="detail-item"><span class="subtle">${i === 0 ? '当前状态' : i === 1 ? '风险提醒' : '推荐操作'}</span><strong>${d}</strong></div>`).join('')}</div></section><section class="panel"><div class="panel__header"><div><strong>操作建议</strong><div class="subtle">针对当前选中项的动作建议</div></div></div><div class="board-list">${cardsHtml}</div></section></div>`,
    };
}

/* ═══════════════════════════════════════════════
   设备管理专用页面工厂
   独立于 makeListManagementRoute，有环境卡片、指纹/代理状态、
   设备-账号绑定关系、隔离覆盖率和批量操作面板
   ═══════════════════════════════════════════════ */
function makeDeviceManagementRoute(config = {}) {
    const metrics = [
        { label: '设备总量', value: '64', delta: '+6', note: '本周新增 6 台环境', color: 'var(--status-success)', search: '设备 总量 64' },
        { label: '隔离覆盖率', value: '91%', delta: '+3%', note: '大部分账号已进入独立环境', color: 'var(--brand-primary)', search: '隔离 覆盖率 91' },
        { label: '异常环境', value: '3', delta: '待修复', note: '指纹漂移与代理丢失', color: 'var(--status-warning)', search: '异常 环境 3 指纹 代理' },
        { label: '空闲设备', value: '12', delta: '可分配', note: '建议优先分配给高价值账号', color: 'var(--text-secondary)', search: '空闲 设备 12' },
    ];

    const devices = [
        { id: 'DEV-US-01', name: '美国直播池 A1', ip: '192.168.1.101 (US)', fingerprint: '正常', proxy: '在线', accounts: 4, status: 'healthy', search: '美国 直播池 A1 正常' },
        { id: 'DEV-US-02', name: '美国内容池 A2', ip: '192.168.1.102 (US)', fingerprint: '正常', proxy: '在线', accounts: 3, status: 'healthy', search: '美国 内容池 A2 正常' },
        { id: 'DEV-UK-01', name: '英国短视频池', ip: '154.22.81.44 (UK)', fingerprint: '正常', proxy: '丢失', accounts: 2, status: 'warning', search: '英国 短视频池 代理丢失' },
        { id: 'DEV-DE-01', name: '德国店铺池 B1', ip: '—', fingerprint: '漂移', proxy: '离线', accounts: 3, status: 'error', search: '德国 店铺池 指纹漂移 离线' },
        { id: 'DEV-DE-02', name: '德国店铺池 B2', ip: '—', fingerprint: '漂移', proxy: '离线', accounts: 2, status: 'error', search: '德国 店铺池 B2 指纹漂移' },
        { id: 'DEV-JP-01', name: '日本客服池', ip: '103.44.22.8 (JP)', fingerprint: '正常', proxy: '在线', accounts: 1, status: 'idle', search: '日本 客服池 空闲' },
    ];

    const statusMap = { healthy: { label: '正常', tone: 'success' }, warning: { label: '告警', tone: 'warning' }, error: { label: '异常', tone: 'error' }, idle: { label: '空闲', tone: 'info' } };

    const metricsHtml = metrics.map(m => `<article class="stat-card" data-search="${m.search}"><div><div class="subtle">${m.label}</div><div class="stat-card__value">${m.value}</div></div><div class="stat-card__delta" style="color:${m.color};"><span>${m.delta}</span><span class="subtle">${m.note}</span></div></article>`).join('');

    const envCardsHtml = devices.map((d, i) => {
        const st = statusMap[d.status];
        return `<article class="device-env-card device-env-card--${d.status} ${i === 0 ? 'is-selected' : ''}" data-search="${d.search}">
            <div class="device-env-card__head"><strong>${d.name}</strong><span class="status-chip ${st.tone}">${st.label}</span></div>
            <div class="device-env-card__meta">
                <div class="list-row"><span class="subtle">设备 ID</span><strong class="mono">${d.id}</strong></div>
                <div class="list-row"><span class="subtle">代理 IP</span><strong class="mono">${d.ip}</strong></div>
                <div class="list-row"><span class="subtle">指纹状态</span><span class="tag ${d.fingerprint === '正常' ? 'success' : 'error'}">${d.fingerprint}</span></div>
                <div class="list-row"><span class="subtle">代理状态</span><span class="tag ${d.proxy === '在线' ? 'success' : d.proxy === '丢失' ? 'warning' : 'error'}">${d.proxy}</span></div>
                <div class="list-row"><span class="subtle">绑定账号</span><strong>${d.accounts} 个</strong></div>
            </div>
            <div class="detail-actions">
                <button class="secondary-button" type="button">${d.status === 'error' ? '修复环境' : d.status === 'idle' ? '分配账号' : '查看详情'}</button>
                <button class="ghost-button" type="button">环境日志</button>
            </div>
        </article>`;
    }).join('');

    const bindingRows = [
        { device: 'DEV-US-01', accounts: ['TK_User_US_01', 'TK_User_US_02', 'TK_Live_US_03', 'TK_Shop_US_04'], status: '正常' },
        { device: 'DEV-UK-01', accounts: ['TK_Creator_UK_02', 'TK_Shop_UK_05'], status: '代理丢失' },
        { device: 'DEV-DE-01', accounts: ['Shop_Manager_03', 'TK_DE_Growth_06', 'TK_DE_Live_07'], status: '指纹漂移' },
    ];

    const mainHtml = `
        <div class="breadcrumbs"><span>account</span><span>/</span><span>设备管理</span></div>
        <div class="page-header">
            <div><div class="eyebrow">隔离环境总览</div><h1>设备管理</h1><p>统一查看浏览器隔离环境、代理、指纹和设备-账号绑定关系，让环境治理可视化。</p></div>
            <div class="header-actions">
                <button class="secondary-button" type="button">导出设备报告</button>
                <button class="secondary-button" type="button">批量巡检</button>
                <button class="primary-button" type="button">新增设备环境</button>
            </div>
        </div>
        <section class="section-stack">
            <div class="stat-grid">${metricsHtml}</div>
            <div class="notice-banner"><div><strong>3 台设备环境异常</strong><div>德国站 2 台指纹漂移，英国站 1 台代理丢失。建议先修复后再恢复批量登录任务。</div></div><div class="toolbar__group"><button class="primary-button" type="button">批量修复</button><button class="ghost-button" type="button">查看详情</button></div></div>
            <div class="device-management-shell">
                <div class="device-filter-bar">
                    <div class="local-tabs" data-filter-group="device-status">
                        <button class="local-tab is-active" data-filter-value="all" type="button">全部 (${devices.length})</button>
                        <button class="local-tab" data-filter-value="healthy" type="button">正常 (2)</button>
                        <button class="local-tab" data-filter-value="warning" type="button">告警 (1)</button>
                        <button class="local-tab" data-filter-value="error" type="button">异常 (2)</button>
                        <button class="local-tab" data-filter-value="idle" type="button">空闲 (1)</button>
                    </div>
                    <div class="segmented" data-segmented data-view-toggle="devices">
                        <button class="is-active" data-view="card" type="button">卡片</button>
                        <button data-view="list" type="button">列表</button>
                    </div>
                </div>
                <div class="device-env-grid">${envCardsHtml}</div>
            </div>
            <div class="analytics-two-column">
                <section class="table-card"><div class="table-card__header"><div><strong>设备-账号绑定表</strong><div class="subtle">快速查看每台设备绑定了哪些账号及隔离状态</div></div></div><div class="table-wrapper"><table><thead><tr><th>设备 ID</th><th>绑定账号</th><th>状态</th><th>操作</th></tr></thead><tbody>${bindingRows.map(r => `<tr class="route-row" data-search="${r.device} ${r.accounts.join(' ')} ${r.status}"><td class="mono"><strong>${r.device}</strong></td><td>${r.accounts.map(a => `<span class="tag">${a}</span>`).join(' ')}</td><td><span class="status-chip ${r.status === '正常' ? 'success' : r.status === '代理丢失' ? 'warning' : 'error'}">${r.status}</span></td><td><button class="ghost-button" type="button">调整绑定</button></td></tr>`).join('')}</tbody></table></div></section>
                <section class="panel"><div class="panel__header"><div><strong>隔离覆盖率</strong><div class="subtle">环境覆盖率越高，批量操作越安全</div></div></div><div class="device-coverage-bar"><div class="coverage-track"><span class="coverage-fill" style="width: 91%;"></span></div><div class="coverage-labels"><span>已隔离 58 台</span><span>未隔离 6 台</span></div></div><div class="device-pool-summary"><div class="task-item is-selected"><div><strong>高价值账号未覆盖</strong><div class="subtle">VIP 客服号与德国站主号仍在默认环境</div></div><span class="pill warning">优先</span></div><div class="task-item"><div><strong>空闲设备可回收</strong><div class="subtle">12 台空闲设备建议分配给新增账号</div></div><span class="pill info">调度</span></div></div></section>
            </div>
        </section>
    `;

    return {
        eyebrow: '设备与环境中心',
        searchTerms: '设备管理 浏览器隔离 代理 指纹 环境 device proxy fingerprint 设备池',
        audit: config.audit,
        sidebarSummary: { eyebrow: '环境提醒', title: '设备环境摘要', copy: '加载后根据真实设备状态、覆盖率与异常情况自动更新。' },
        statusLeft: ['设备总量', '健康覆盖率', '异常设备'],
        statusRight: [{ text: '实时汇总', tone: 'info' }, { text: '等待加载', tone: 'warning' }],
        hideDetailPanel: false,
        mainHtml,
        detailHtml: `<div class="detail-root"><section class="panel"><div class="panel__header"><div><strong>设备详情</strong><div class="subtle">选中设备的环境参数与绑定信息</div></div><span class="status-chip success">正常</span></div><div class="detail-stack"><div><strong>美国直播池 A1</strong><div class="subtle mono">DEV-US-01</div></div><div class="detail-list"><div class="detail-item"><span class="subtle">代理 IP</span><strong class="mono">192.168.1.101 (US)</strong></div><div class="detail-item"><span class="subtle">指纹状态</span><strong>正常</strong></div><div class="detail-item"><span class="subtle">绑定账号</span><strong>4 个</strong></div><div class="detail-item"><span class="subtle">最近巡检</span><strong>12:18</strong></div></div><div class="detail-actions"><button class="primary-button" type="button">打开环境</button><button class="secondary-button" type="button">修改绑定</button></div></div></section><section class="panel"><div class="panel__header"><div><strong>维护建议</strong><div class="subtle">避免设备与账号混绑带来风险</div></div></div><div class="audit-list"><div class="audit-item"><div><strong>优先修复德国设备池</strong><div class="subtle">指纹漂移会影响 5 个账号的登录环境</div></div><span class="pill warning">优先</span></div><div class="audit-item"><div><strong>英国代理恢复后再操作</strong><div class="subtle">当前代理丢失，不宜继续投流</div></div><span class="pill error">阻塞</span></div><div class="audit-item"><div><strong>空闲设备调度</strong><div class="subtle">12 台空闲可分配给新增高价值账号</div></div><span class="pill info">调度</span></div></div></section></div>`,
    };
}
/* Template A: KPI 卡片 + 图表/分析区 + 洞察面板
   ═══════════════════════════════════════════════ */
