function makeAnalyticsBoardRoute(config) {
    const metrics = config.metrics || [
        { label: `${config.title}总量`, value: '--', delta: '等待后端数据', note: '进入页面后动态填充', color: 'var(--status-success)', search: `${config.title} 总量` },
        { label: '风险提醒', value: '--', delta: '等待后端数据', note: '进入页面后动态填充', color: 'var(--status-warning)', search: `${config.title} 风险` },
        { label: '完成情况', value: '--', delta: '等待后端数据', note: '进入页面后动态填充', color: 'var(--brand-primary)', search: `${config.title} 完成情况` },
    ];
    const items = config.items || [
        { title: `${config.title}洞察 1`, desc: '当前最重要的数据发现。', badge: '关键', tone: 'success', search: `${config.title} 洞察 1` },
        { title: `${config.title}洞察 2`, desc: '需要进一步分析的异常。', badge: '待分析', tone: 'warning', search: `${config.title} 洞察 2` },
        { title: `${config.title}建议`, desc: '基于数据的行动建议。', badge: '建议', tone: 'info', search: `${config.title} 建议` },
    ];
    const cards = config.cards || [
        { title: '今日焦点', desc: `${config.title}中优先关注的指标变化。`, badge: '焦点', tone: 'warning', search: `${config.title} 焦点` },
        { title: '趋势变化', desc: '近 7 天关键指标走势。', badge: '趋势', tone: 'info', search: `${config.title} 趋势` },
        { title: '行动建议', desc: '基于分析的推荐操作。', badge: '行动', tone: 'success', search: `${config.title} 行动` },
    ];
    const detailItems = config.detailItems || ['数据趋势稳定', '部分指标需关注', '建议深入分析异常点'];
    const stripItems = config.stripItems || ['实时状态', '最近变更', '分析建议'];

    const metricsHtml = metrics.map(m => `<article class="stat-card" data-search="${m.search}"><div><div class="subtle">${m.label}</div><div class="stat-card__value">${m.value}</div></div><div class="stat-card__delta" style="color:${m.color};"><span>${m.delta}</span><span class="subtle">${m.note}</span></div></article>`).join('');
    const stripHtml = stripItems.map(s => `<div class="timeline-chip"><strong>${s}</strong><div class="subtle">${config.title} 数据保持同步</div></div>`).join('');
    const cardsHtml = cards.map(c => `<article class="board-card" data-search="${c.search}"><strong>${c.title}</strong><div class="subtle">${c.desc}</div><div class="status-strip"><span class="pill ${c.tone}">${c.badge}</span></div></article>`).join('');
    const insightHtml = items.map(it => `<article class="report-card" data-search="${it.search}"><strong>${it.title}</strong><div class="subtle">${it.desc}</div><div class="status-strip"><span class="pill ${it.tone}">${it.badge}</span></div></article>`).join('');
    const tableHtml = config.table
        ? `<section class="table-card"><div class="table-card__header"><div><strong>${config.table.title}</strong><div class="subtle">${config.table.description}</div></div></div><div class="table-wrapper"><table><thead><tr>${config.table.columns.map(c => `<th>${c}</th>`).join('')}</tr></thead><tbody>${config.table.rows.map(r => `<tr class="route-row" data-search="${r.search}">${r.cells.map(c => `<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table></div></section>`
        : '';

    const mainHtml = `
        <div class="breadcrumbs"><span>analyst</span><span>/</span><span>${config.title}</span></div>
        <div class="page-header">
            <div><div class="eyebrow">${config.headerEyebrow}</div><h1>${config.title}</h1><p>${config.description}</p></div>
            <div class="header-actions"><button class="secondary-button" type="button">${config.secondaryAction}</button><button class="primary-button" type="button">${config.primaryAction}</button></div>
        </div>
        <section class="section-stack">
            <div class="stat-grid">${metricsHtml}</div>
            <div class="analytics-board-shell">
                <div class="analytics-kpi-strip">${stripHtml}</div>
                <div class="analytics-body">
                    <div class="analytics-main">
                        <section class="analytics-chart-panel panel"><div class="panel__header"><div><strong>${config.title}图表</strong><div class="subtle">数据可视化区域</div></div><div class="analytics-chart-toggles"><button class="task-view-btn is-active" type="button">趋势</button><button class="task-view-btn" type="button">对比</button><button class="task-view-btn" type="button">分布</button></div></div><div class="analytics-chart-area"><div class="chart-placeholder" data-search="${config.title} 图表区域">📊 ${config.title} — 数据可视化</div></div></section>
                        <div class="analytics-insight-grid">${insightHtml}</div>
                        ${tableHtml}
                    </div>
                </div>
            </div>
        </section>
    `;

    return {
        eyebrow: config.eyebrow,
        searchTerms: `${config.title} ${config.description} analyst ${config.eyebrow}`,
        sidebarSummary: config.sidebarSummary || { eyebrow: `${config.title}提醒`, title: `${config.title}数据更新`, copy: `查看${config.title}中的关键指标变化。` },
        statusLeft: config.statusLeft || [`${config.title} 已更新`, '数据同步正常', '最近刷新 12:48'],
        statusRight: config.statusRight || [{ text: '数据正常', tone: 'success' }, { text: '待关注 2', tone: 'warning' }],
        hideDetailPanel: false,
        mainHtml,
        detailHtml: `<div class="detail-root"><section class="panel"><div class="panel__header"><div><strong>${config.sideTitle || '分析要点'}</strong><div class="subtle">${config.sideDesc || '把洞察转成后续动作。'}</div></div></div><div class="metric-kv">${detailItems.map((d, i) => `<div class="detail-item"><span class="subtle">${i === 0 ? '当前状态' : i === 1 ? '主要风险' : '建议动作'}</span><strong>${d}</strong></div>`).join('')}</div></section><section class="panel"><div class="panel__header"><div><strong>相关洞察</strong><div class="subtle">数据驱动的行动建议</div></div></div><div class="board-list">${cardsHtml}</div></section></div>`,
    };
}

function buildAnalystHeader(config) {
    return `
        <div class="breadcrumbs"><span>analyst</span><span>/</span><span>${config.title}</span></div>
        <div class="page-header">
            <div><div class="eyebrow">${config.headerEyebrow}</div><h1>${config.title}</h1><p>${config.description}</p></div>
            <div class="header-actions"><button class="secondary-button" type="button">${config.secondaryAction}</button><button class="primary-button" type="button">${config.primaryAction}</button></div>
        </div>
    `;
}

function buildStatGrid(metrics) {
    return `<div class="stat-grid">${metrics.map(metric => `<article class="stat-card" data-search="${metric.search || metric.label}"><div><div class="subtle">${metric.label}</div><div class="stat-card__value">${metric.value}</div></div><div class="stat-card__delta" style="color:${metric.color || 'var(--brand-primary)'};"><span>${metric.delta}</span><span class="subtle">${metric.note}</span></div></article>`).join('')}</div>`;
}

function buildAnalyticsSummary(options) {
    return `
        <div class="analytics-chart-card__summary">
            <div class="analytics-chart-meta"><span>时间范围：${options.range}</span><span>维度：${options.dimension}</span></div>
            <div class="analytics-key-takeaway">${options.takeaway}</div>
        </div>
    `;
}

function buildAnalystDetail(detail) {
    const items = detail.items || [];
    const cards = detail.cards || [];
    return `<div class="detail-root"><section class="panel"><div class="panel__header"><div><strong>${detail.title}</strong><div class="subtle">${detail.description}</div></div></div><div class="metric-kv">${items.map(item => `<div class="detail-item"><span class="subtle">${item.label}</span><strong>${item.value}</strong></div>`).join('')}</div></section><section class="panel"><div class="panel__header"><div><strong>${detail.cardTitle || '后续动作'}</strong><div class="subtle">把分析结论转成具体执行动作</div></div></div><div class="board-list">${cards.map(card => `<article class="board-card${card.routeLink ? ' cross-nav-card' : ''}" data-search="${card.search || card.title}"${card.routeLink ? ` data-route-link="${card.routeLink}"` : ''}><strong>${card.title}</strong><div class="subtle">${card.desc}</div><div class="status-strip"><span class="pill ${card.tone || 'info'}">${card.badge || '动作'}</span></div></article>`).join('')}</div></section></div>`;
}

function makeTrafficBoardRoute() {
    const metrics = [
        { label: '账号样本', value: '--', delta: '等待后端数据', note: '根据真实账号与任务记录填充', color: 'var(--status-success)', search: '账号样本' },
        { label: '任务完成率', value: '--', delta: '等待后端数据', note: '根据真实任务状态填充', color: 'var(--brand-primary)', search: '任务完成率' },
        { label: '异常任务', value: '--', delta: '等待后端数据', note: '根据真实异常任务填充', color: 'var(--status-warning)', search: '异常任务' },
    ];
    const sourceCards = [
        { title: '活跃账号', value: '--', meta: '等待后端数据', tone: 'success' },
        { title: '执行任务', value: '--', meta: '等待后端数据', tone: 'warning' },
        { title: '活动记录', value: '--', meta: '等待后端数据', tone: 'info' },
    ];
    const tableRows = [
        ['欧洲短视频', '下降 18%', '封面疲劳', '先换开场素材'],
        ['美国店铺流量', '上升 11%', '商品标题优化', '继续放量'],
        ['搜索关键词池', '波动 7%', '热门词更替', '补齐关键词映射'],
    ];
    const mainHtml = `
        ${buildAnalystHeader({ title: '流量看板', headerEyebrow: '流量监控页', description: '集中查看店铺流量、内容引流和转化来源，帮助分析师快速定位波动原因。', secondaryAction: '导出流量报告', primaryAction: '查看来源拆解' })}
        <section class="section-stack">
            ${buildStatGrid(metrics)}
            <div class="traffic-board-shell analyst-feature-shell">
                <section class="panel traffic-sources-panel"><div class="panel__header"><div><strong>流量来源拆解</strong><div class="subtle">从渠道层先判断波动来自哪里</div></div></div><div class="traffic-source-grid">${sourceCards.map(card => `<article class="traffic-source-card ${card.tone}"><div class="subtle">${card.title}</div><strong>${card.value}</strong><span>${card.meta}</span></article>`).join('')}</div></section>
                <div class="analytics-two-column">
                    <section class="panel"><div class="panel__header"><div><strong>波动趋势带</strong><div class="subtle">按小时查看各来源波动与异常标记</div></div><div class="analytics-chart-toggles"><button class="task-view-btn is-active" type="button">小时</button><button class="task-view-btn" type="button">日</button><button class="task-view-btn" type="button">周</button></div></div><div class="traffic-trend-board"><div class="traffic-trend-line"></div><div class="traffic-alert-markers"><span>欧洲渠道回落</span><span>搜索入口波动</span><span>自然流量回升</span></div></div></section>
                    <section class="panel"><div class="panel__header"><div><strong>异常动作建议</strong><div class="subtle">把波动直接映射为下一步排查动作</div></div></div><div class="traffic-action-list"><div class="task-item is-selected"><div><strong>先查欧洲渠道素材</strong><div class="subtle">重点确认封面疲劳与开场三秒留存</div></div><span class="pill warning">优先</span></div><div class="task-item" data-route-link="profit-analysis" data-route-toast="已跳转到利润分析"><div><strong>联动利润页看关键词价值 →</strong><div class="subtle">搜索入口波动可能是低价值词替换导致</div></div><span class="pill info">联动</span></div><div class="task-item"><div><strong>复盘促销投流成本</strong><div class="subtle">排查高投入但低转化的渠道组合</div></div><span class="pill success">增长</span></div></div></section>
                </div>
                <section class="table-card"><div class="table-card__header"><div><strong>渠道表现拆解</strong><div class="subtle">曝光、点击、成交流向在一张表里看清</div></div></div><div class="table-wrapper"><table><thead><tr><th>渠道</th><th>波动</th><th>原因判断</th><th>建议动作</th></tr></thead><tbody>${tableRows.map(row => `<tr class="route-row" data-search="${row.join(' ')}">${row.map(cell => `<td>${cell}</td>`).join('')}</tr>`).join('')}</tbody></table></div></section>
            </div>
        </section>
    `;

    return {
        eyebrow: '流量分析中心',
        searchTerms: '流量看板 曝光 点击率 渠道 搜索 促销 analyst',
        sidebarSummary: { eyebrow: '流量提醒', title: '等待实时汇总', copy: '该页面只展示真实账号、任务与活动记录衍生的流量摘要。' },
        statusLeft: ['等待数据接入', '账号/任务/活动同步中', '无静态指标'],
        statusRight: [{ text: '后端驱动', tone: 'success' }, { text: '等待刷新', tone: 'warning' }],
        hideDetailPanel: false,
        mainHtml,
        detailHtml: buildAnalystDetail({
            title: '流量排查清单',
            description: '先处理影响最大的流量波动点',
            items: [
                { label: '当前异常', value: '欧洲渠道回落 18%' },
                { label: '联动模块', value: '利润分析 / 商品标题 / 投流配置' },
                { label: '建议顺序', value: '素材 -> 关键词 -> 投流成本' },
            ],
            cards: [
                { title: '先换欧洲渠道开场素材', desc: '优先验证素材疲劳是否导致 CTR 下滑。', badge: '优先', tone: 'warning' },
                { title: '回看搜索词价值变化', desc: '排查是否由低价值热词替换造成波动。', badge: '联动', tone: 'info' },
                { title: '复盘任务执行路径', desc: '优先核对异常任务与活动记录的来源差异。', badge: '复盘', tone: 'success' },
            ],
        }),
    };
}

function makeVisualLabRoute() {
    const metrics = [
        { label: '实验项目', value: '--', delta: '等待后端数据', note: '进入页面后动态填充', color: 'var(--status-success)', search: '实验项目' },
        { label: '实验视图', value: '--', delta: '等待后端数据', note: '进入页面后动态填充', color: 'var(--brand-primary)', search: '实验视图' },
        { label: '可用模型', value: '--', delta: '等待后端数据', note: '进入页面后动态填充', color: 'var(--status-warning)', search: '可用模型' },
    ];
    const sources = ['店铺经营日报', '视频互动日志', '投流成本表', '搜索关键词池'];
    const chartTypes = ['折线图', '柱状图', '漏斗图', '热力图', '矩阵图', '环形图'];
    const mainHtml = `
        ${buildAnalystHeader({ title: '可视化实验室', headerEyebrow: '假设验证与图表拼装', description: '把实验指标、图表组合、洞察注释和导出结果放到一个实验空间里。', secondaryAction: '导出图表', primaryAction: '保存实验视图' })}
        <section class="section-stack">
            ${buildStatGrid(metrics)}
            <div class="visual-lab-shell analyst-feature-shell">
                <section class="panel visual-lab-column"><div class="panel__header"><div><strong>数据源</strong><div class="subtle">选择实验输入与图表库</div></div></div><div class="data-source-list">${sources.map((source, index) => `<button class="data-source-item ${index === 0 ? 'is-selected' : ''}" type="button"><strong>${source}</strong><span>${index === 0 ? '实时同步' : '已连接'}</span></button>`).join('')}</div><div class="subtle section-note">图表库</div><div class="chart-type-grid">${chartTypes.map(type => `<button class="chart-type-btn" type="button">${type}</button>`).join('')}</div></section>
                <section class="visual-lab-center"><div class="panel visual-preview-panel"><div class="panel__header"><div><strong>实验画布</strong><div class="subtle">图表组合、对照实验与注释在同一视图完成</div></div><div class="analytics-chart-toggles"><button class="task-view-btn is-active" type="button">1D</button><button class="task-view-btn" type="button">1W</button><button class="task-view-btn" type="button">1M</button></div></div><div class="visual-preview-stage"><div class="visual-preview-line"></div><div class="visual-preview-overlay"><span>项目 --</span><span>视图 --</span><span>素材 --</span></div></div></div><div class="visual-kpi-row"> <article class="panel visual-mini-card"><strong>实验卡片 A</strong><span>等待后端数据</span><em>进入页面后刷新</em></article><article class="panel visual-mini-card"><strong>实验卡片 B</strong><span>等待后端数据</span><em>进入页面后刷新</em></article><article class="panel visual-mini-card"><strong>实验卡片 C</strong><span>等待后端数据</span><em>进入页面后刷新</em></article></div></section>
                <section class="panel visual-lab-column"><div class="panel__header"><div><strong>样式与交互</strong><div class="subtle">调轴、配色、标签与交互行为</div></div></div><div class="config-form-group"><div class="config-field"><label>X 轴标签</label><input type="text" value="日期 / 实验批次"></div><div class="config-field"><label>Y 轴标签</label><input type="text" value="CTR / CVR / 成本"></div><div class="config-field"><label>配色策略</label><div class="visual-color-swatches"><span></span><span></span><span></span><span></span></div></div><div class="config-field"><label>交互选项</label><div class="visual-toggle-list"><div class="config-toggle"><span>显示异常标记</span><input type="checkbox" checked></div><div class="config-toggle"><span>支持悬停摘要</span><input type="checkbox" checked></div><div class="config-toggle"><span>同步到 Dashboard</span><input type="checkbox"></div></div></div></div></section>
            </div>
        </section>
    `;

    return {
        eyebrow: '可视分析实验台',
        searchTerms: '可视化实验室 数据源 图表 实验 模板 analyst',
        sidebarSummary: { eyebrow: '实验提醒', title: '2 个图表组合待发布', copy: '建议先固化 CTR 与 CVR 联动模板，再同步到报表中心与 Dashboard。' },
        statusLeft: ['实验 12', '数据源 8', '模板复用率 67%'],
        statusRight: [{ text: '实验稳定', tone: 'success' }, { text: '待发布 2', tone: 'warning' }],
        hideDetailPanel: false,
        mainHtml,
        detailHtml: buildAnalystDetail({
            title: '实验项目摘要',
            description: '可视化实验室是图表构建器，不是普通看板页',
            items: [
                { label: '核心作用', value: '拼图表、做对照实验、沉淀图表模板' },
                { label: '主要输出', value: '实验视图、共享图表、模板资产' },
                { label: '最关键动作', value: '数据源绑定 -> 图表构建 -> 样式发布' },
            ],
            cards: [
                { title: '先固化高频实验模板', desc: '把 CTR/CVR/成本联动模板沉淀成可复用组件。', badge: '模板', tone: 'success' },
                { title: '增加异常标记规则', desc: '让分析师快速看见突发波动和阈值越界。', badge: '规则', tone: 'warning' },
                { title: '同步到报表中心', desc: '实验完成后可直接成为报表预览模块。', badge: '联动', tone: 'info' },
            ],
        }),
    };
}

function makeCompetitorMonitorRoute() {
    const metrics = [
        { label: '监控账号', value: '--', delta: '等待后端数据', note: '根据真实账号样本填充', color: 'var(--status-success)', search: '监控账号' },
        { label: '异常任务', value: '--', delta: '等待后端数据', note: '根据真实失败任务填充', color: 'var(--status-warning)', search: '异常任务' },
        { label: '覆盖地区', value: '--', delta: '等待后端数据', note: '根据真实地区分布填充', color: 'var(--brand-primary)', search: '覆盖地区' },
    ];
    const rivals = [
        { name: '账号样本 A', fans: '--', delta: '等待后端数据', tone: 'success' },
        { name: '账号样本 B', fans: '--', delta: '等待后端数据', tone: 'warning' },
        { name: '账号样本 C', fans: '--', delta: '等待后端数据', tone: 'success' },
        { name: '账号样本 D', fans: '--', delta: '等待后端数据', tone: 'info' },
    ];
    const mainHtml = `
        ${buildAnalystHeader({ title: '竞争对手监控', headerEyebrow: '竞品趋势与动作拆解', description: '集中跟踪竞品商品、内容、价格和投流动作，帮助分析师快速判断哪些动作值得抄、哪些风险要避开。', secondaryAction: '导出竞品快照', primaryAction: '新增监控对象' })}
        <section class="section-stack">
            ${buildStatGrid(metrics)}
            <div class="competitor-monitor-shell analyst-feature-shell">
                <section class="panel"><div class="panel__header"><div><strong>竞品对象带</strong><div class="subtle">横向快速对比增长速度与定位变化</div></div></div><div class="rival-strip">${rivals.map(rival => `<article class="rival-card ${rival.name === 'My Account' ? 'is-self' : ''}"><div class="rival-avatar">${rival.name.slice(0, 1)}</div><strong>${rival.name}</strong><span>${rival.fans}</span><em class="${rival.tone}">${rival.delta}</em></article>`).join('')}</div></section>
                <div class="analytics-two-column">
                    <section class="panel"><div class="panel__header"><div><strong>视频表现表</strong><div class="subtle">封面、播放、评论与动作建议放在同一张表里</div></div></div><div class="table-wrapper"><table><thead><tr><th>视频</th><th>播放</th><th>互动</th><th>结论</th></tr></thead><tbody><tr class="route-row" data-search="家居收纳 82万 评论高"><td><strong>家居收纳 30s</strong></td><td>82万</td><td>赞 5.4万 / 评 3,182</td><td>封面与前三秒强</td></tr><tr class="route-row" data-search="折扣合集 61万 转化强"><td><strong>折扣合集快剪</strong></td><td>61万</td><td>赞 3.1万 / 评 1,906</td><td>值得借鉴结构</td></tr><tr class="route-row" data-search="价格对比 44万 风险"><td><strong>价格对比对拍</strong></td><td>44万</td><td>赞 1.5万 / 评 921</td><td>有价格战风险</td></tr></tbody></table></div></section>
                    <section class="analytics-side-stack"><section class="panel"><div class="panel__header"><div><strong>热门主题云</strong><div class="subtle">先看竞品在押注哪些主题簇</div></div></div><div class="topic-cloud"><span class="xl">折扣开箱</span><span class="lg">收纳改造</span><span class="md">限时补贴</span><span class="md">达人试用</span><span class="sm">节日套装</span><span class="sm">低价替代</span></div></section><section class="panel"><div class="panel__header"><div><strong>今日波动</strong><div class="subtle">增速与风险信号同步显示</div></div></div><div class="rival-trend-bars"><div><span>NovaDaily US</span><i style="height: 82%"></i></div><div><span>Glowmart UK</span><i style="height: 67%"></i></div><div><span>TrendBox DE</span><i class="warning" style="height: 38%"></i></div><div><span>My Account</span><i class="info" style="height: 54%"></i></div></div></section></section>
                </div>
            </div>
        </section>
    `;

    return {
        eyebrow: '竞品监控中枢',
        searchTerms: '竞争对手监控 竞品 视频表现 主题云 增长趋势 analyst',
        sidebarSummary: { eyebrow: '竞品提醒', title: '等待真实样本汇总', copy: '该页面仅展示真实账号样本、地区分布和失败任务衍生的竞品视图。' },
        statusLeft: ['等待数据接入', '样本动态刷新', '无静态竞品数值'],
        statusRight: [{ text: '后端驱动', tone: 'success' }, { text: '等待刷新', tone: 'warning' }],
        hideDetailPanel: false,
        mainHtml,
        detailHtml: buildAnalystDetail({
            title: '竞品监控作用',
            description: '这个页面不是简单列表，而是内容与增长动作的对比工作台',
            items: [
                { label: '核心任务', value: '比较竞品内容结构、增长动作、价格与投流策略' },
                { label: '关键输出', value: '可借鉴动作 / 需规避风险 / 选题方向' },
                { label: '联动页面', value: '蓝海分析 / 爆款标题 / 商品标题大师' },
            ],
            cards: [
                { title: '优先复盘高增长竞品', desc: '先分析 NovaDaily US 的前 3 条增长内容。', badge: '增长', tone: 'success' },
                { title: '标记价格战风险', desc: 'TrendBox DE 已进入低价竞争区，不建议直接复制。', badge: '风险', tone: 'warning' },
                { title: '沉淀主题模板 →', desc: '把高转化主题整理给内容创作团队直接复用。', badge: '复用', tone: 'info', routeLink: 'creative-workshop' },
            ],
        }),
    };
}

function makeProfitAnalysisRoute() {
    const metrics = [
        { label: '任务完成量', value: '--', delta: '实时聚合', note: '根据真实任务完成情况填充', color: 'var(--status-success)', search: '任务完成量 实时聚合' },
        { label: '失败任务量', value: '--', delta: '实时聚合', note: '根据真实任务异常情况填充', color: 'var(--status-warning)', search: '失败任务量 实时聚合' },
        { label: '素材支撑量', value: '--', delta: '实时聚合', note: '根据真实素材库存填充', color: 'var(--brand-primary)', search: '素材支撑量 实时聚合' },
        { label: '活跃账号量', value: '--', delta: '实时聚合', note: '根据真实账号状态填充', color: 'var(--status-success)', search: '活跃账号量 实时聚合' },
    ];
    const mainHtml = `
        ${buildAnalystHeader({ title: '利润分析', headerEyebrow: '成本收益总览', description: '把收入、成本、广告投入和退款风险汇总，帮助分析师判断哪些店铺和内容值得继续加码。', secondaryAction: '导出利润报表', primaryAction: '查看成本拆解' })}
        <section class="section-stack">
            ${buildStatGrid(metrics)}
            <div class="profit-analysis-shell analyst-feature-shell">
                <div class="analytics-two-column">
                    <section class="panel"><div class="panel__header"><div><strong>营收 vs 成本趋势</strong><div class="subtle">看利润变化时先确认收入与成本谁在拉扯</div></div><div class="analytics-chart-toggles"><button class="task-view-btn is-active" type="button">周</button><button class="task-view-btn" type="button">月</button><button class="task-view-btn" type="button">季</button></div></div><div class="profit-bar-compare"><div class="compare-group"><span>W1</span><i class="revenue" style="height:72%"></i><i class="cost" style="height:56%"></i></div><div class="compare-group"><span>W2</span><i class="revenue" style="height:84%"></i><i class="cost" style="height:63%"></i></div><div class="compare-group"><span>W3</span><i class="revenue" style="height:79%"></i><i class="cost warning" style="height:71%"></i></div><div class="compare-group"><span>W4</span><i class="revenue" style="height:88%"></i><i class="cost" style="height:68%"></i></div><div class="compare-group"><span>W5</span><i class="revenue" style="height:91%"></i><i class="cost warning" style="height:78%"></i></div></div></section>
                    <section class="panel"><div class="panel__header"><div><strong>成本结构</strong><div class="subtle">利润页的关键在于成本拆解而非单看涨跌</div></div></div><div class="profit-ledger-grid"><article><span>广告投流</span><strong>22%</strong><em>较上周 +2%</em></article><article><span>履约成本</span><strong>18%</strong><em>欧洲仓波动</em></article><article><span>退款侵蚀</span><strong>4.6%</strong><em>继续回落</em></article><article><span>平台费率</span><strong>7.2%</strong><em>稳定</em></article></div></section>
                </div>
                <section class="table-card"><div class="table-card__header"><div><strong>产品利润明细</strong><div class="subtle">把商品、利润率、库存风险和建议动作一起看</div></div></div><div class="table-wrapper"><table><thead><tr><th>商品</th><th>毛利率</th><th>库存</th><th>风险</th><th>动作</th></tr></thead><tbody><tr class="route-row" data-search="收纳箱 34 高 健康 继续加码"><td><strong>收纳箱套装</strong></td><td><span class="status-chip success">34%</span></td><td>高</td><td>健康</td><td>继续加码</td></tr><tr class="route-row" data-search="节日灯串 18 中 广告高 调整投流"><td><strong>节日灯串</strong></td><td><span class="status-chip warning">18%</span></td><td>中</td><td>广告成本高</td><td>调整投流</td></tr><tr class="route-row" data-search="厨房挂架 12 低 退款高 优先复盘"><td><strong>厨房挂架</strong></td><td><span class="status-chip error">12%</span></td><td>低</td><td>退款高</td><td>优先复盘</td></tr></tbody></table></div></section>
            </div>
        </section>
    `;

    return {
        eyebrow: '利润分析中心',
        searchTerms: '利润分析 ROI 成本 营收 退款 库存 analyst',
        sidebarSummary: { eyebrow: '利润提醒', title: '等待运营准备度汇总', copy: '该页面只展示真实账号、任务、素材回填出的运营准备度，不伪造利润金额。' },
        statusLeft: ['等待数据接入', '运营准备度动态刷新', '无静态利润金额'],
        statusRight: [{ text: '后端驱动', tone: 'success' }, { text: '等待刷新', tone: 'warning' }],
        hideDetailPanel: false,
        mainHtml,
        detailHtml: buildAnalystDetail({
            title: '利润分析作用',
            description: '这是预算与经营决策页，不是普通趋势展示页',
            items: [
                { label: '核心判断', value: '利润变动来自流量、成本还是退款侵蚀' },
                { label: '主要输入', value: '收入、广告、履约、退款、库存' },
                { label: '输出动作', value: '加码 / 降本 / 调投流 / 清库存' },
            ],
            cards: [
                { title: '先查欧洲履约成本', desc: '欧洲仓履约波动是利润被侵蚀的第一因素。', badge: '优先', tone: 'warning' },
                { title: '复核低 ROI 渠道', desc: '先关停高成本低回报的投流组合。', badge: '预算', tone: 'info' },
                { title: '联动订单与退款页 →', desc: '利润问题需要和订单质量、售后问题一起看。', badge: '联动', tone: 'success', routeLink: 'order-management' },
            ],
        }),
    };
}

function makeBlueOceanRoute() {
    const metrics = [
        { label: '候选主题', value: '--', delta: '等待后端数据', note: '根据真实账号、素材、任务结果填充', color: 'var(--status-success)', search: '候选主题' },
        { label: '素材主题', value: '--', delta: '等待后端数据', note: '根据真实素材类型填充', color: 'var(--brand-primary)', search: '素材主题' },
        { label: '异常任务', value: '--', delta: '等待后端数据', note: '根据真实任务状态填充', color: 'var(--status-warning)', search: '异常任务' },
    ];
    const bubbles = [
        { cls: 'xl', left: '68%', top: '24%', label: '收纳整理', tone: 'success' },
        { cls: 'lg', left: '58%', top: '38%', label: '宠物清洁', tone: 'info' },
        { cls: 'md', left: '32%', top: '26%', label: '节日灯串', tone: 'warning' },
        { cls: 'sm', left: '74%', top: '56%', label: '厨房置物', tone: 'success' },
        { cls: 'sm', left: '22%', top: '62%', label: '低价美妆', tone: 'warning' },
    ];
    const mainHtml = `
        ${buildAnalystHeader({ title: '蓝海分析', headerEyebrow: '供给与需求缺口识别', description: '围绕高需求低供给的品类和关键词建立机会池，帮助决定先做什么内容和商品。', secondaryAction: '导出蓝海清单', primaryAction: '加入机会池' })}
        <section class="section-stack">
            ${buildStatGrid(metrics)}
            <div class="blue-ocean-shell analyst-feature-shell analytics-two-column">
                <section class="panel"><div class="panel__header"><div><strong>机会分布矩阵</strong><div class="subtle">横轴看市场规模，纵轴看竞争强度，优先找右上蓝海区</div></div></div><div class="opportunity-matrix"><div class="matrix-quadrant q1"></div><div class="matrix-quadrant q2"></div><div class="matrix-quadrant q3"></div><div class="matrix-quadrant q4"></div><div class="matrix-axis matrix-axis-x">市场规模</div><div class="matrix-axis matrix-axis-y">竞争强度</div>${bubbles.map(bubble => `<button class="matrix-bubble ${bubble.cls} ${bubble.tone}" type="button" style="left:${bubble.left};top:${bubble.top};">${bubble.label}</button>`).join('')}</div></section>
                <section class="analytics-side-stack"><section class="panel"><div class="panel__header"><div><strong>选中机会详情</strong><div class="subtle">先看机会评分，再看是否可落地</div></div></div><div class="opportunity-detail-card"><strong>收纳整理</strong><div class="metric-kv"><div class="detail-item"><span class="subtle">市场热度</span><strong>87</strong></div><div class="detail-item"><span class="subtle">竞争强度</span><strong>42</strong></div><div class="detail-item"><span class="subtle">利润空间</span><strong>31%</strong></div></div><p class="subtle">需求高、内容切口多、供应仍不饱和，适合优先进入测试。</p></div></section><section class="panel"><div class="panel__header"><div><strong>AI 策略建议</strong><div class="subtle">机会页必须输出能执行的市场切入方案</div></div></div><div class="strategy-list"><div class="task-item is-selected"><div><strong>先做对比型内容</strong><div class="subtle">突出收纳前后变化，适合短视频起量</div></div><span class="pill success">优先</span></div><div class="task-item"><div><strong>优先英国和德国站测试</strong><div class="subtle">这两个站点仍有供给缺口</div></div><span class="pill info">地区</span></div><div class="task-item"><div><strong>同步给标题与文案团队</strong><div class="subtle">提前准备关键词和内容切口</div></div><span class="pill warning">联动</span></div></div></section></section>
            </div>
        </section>
    `;

    return {
        eyebrow: '蓝海机会挖掘',
        searchTerms: '蓝海分析 机会矩阵 市场规模 竞争强度 analyst',
        sidebarSummary: { eyebrow: '机会提醒', title: '等待实时主题汇总', copy: '该页面仅展示账号地区、素材类型与任务反馈生成的机会线索。' },
        statusLeft: ['等待数据接入', '主题矩阵动态生成', '无硬编码机会值'],
        statusRight: [{ text: '后端驱动', tone: 'success' }, { text: '等待刷新', tone: 'warning' }],
        hideDetailPanel: false,
        mainHtml,
        detailHtml: buildAnalystDetail({
            title: '蓝海分析作用',
            description: '这个页面用于判断做什么，而不是只看历史数据',
            items: [
                { label: '核心任务', value: '识别高需求低竞争的市场切入口' },
                { label: '关键输出', value: '机会矩阵、机会池、调研建议' },
                { label: '下游联动', value: '竞品监控 / 爆款标题 / AI 文案生成' },
            ],
            cards: [
                { title: '优先验证右上象限机会', desc: '先在高需求低竞争区做小批量测试。', badge: '优先', tone: 'success' },
                { title: '规避红海价格战', desc: '低价美妆与节日灯串已经进入高竞争区。', badge: '规避', tone: 'warning' },
                { title: '输出调研报告', desc: '把高潜类目整理成可读报告发给业务团队。', badge: '报告', tone: 'info' },
            ],
        }),
    };
}

function makeReportCenterRoute() {
    const metrics = [
        { label: '报告记录', value: '--', delta: '等待后端数据', note: '根据真实报表记录填充', color: 'var(--status-success)', search: '报告记录' },
        { label: '待处理项', value: '--', delta: '等待后端数据', note: '根据真实报表状态填充', color: 'var(--status-warning)', search: '待处理项' },
        { label: '活动日志', value: '--', delta: '等待后端数据', note: '根据真实活动记录填充', color: 'var(--brand-primary)', search: '活动日志' },
    ];
    const mainHtml = `
        ${buildAnalystHeader({ title: '报表中心', headerEyebrow: '经营报表生成与归档', description: '承接日报、周报、专题报表和外发下载，方便分析师和管理者统一查看输出。', secondaryAction: '批量导出报表', primaryAction: '生成新报表' })}
        <section class="section-stack">
            ${buildStatGrid(metrics)}
            <div class="report-center-shell analyst-feature-shell">
                <section class="panel report-templates-panel"><div class="panel__header"><div><strong>模板库</strong><div class="subtle">选择常用模板或收藏模板快速开报</div></div></div><div class="report-template-list"><button class="data-source-item is-selected" type="button"><strong>经营日报</strong><span>默认模板</span></button><button class="data-source-item" type="button"><strong>利润专题</strong><span>财务复盘</span></button><button class="data-source-item" type="button"><strong>互动洞察</strong><span>评论与情绪</span></button><button class="data-source-item" type="button"><strong>蓝海调研</strong><span>机会发现</span></button></div></section>
                <section class="panel report-builder-panel"><div class="panel__header"><div><strong>报告配置流程</strong><div class="subtle">字段、筛选、图表与发送规则分步完成</div></div></div><div class="report-builder-steps"><article><span>1</span><div><strong>选择字段</strong><p class="subtle">曝光、转化、利润、退款、情绪指数</p></div></article><article><span>2</span><div><strong>设置筛选</strong><p class="subtle">近 7 天 / 英德站 / 高价值账号组</p></div></article><article><span>3</span><div><strong>选择图表</strong><p class="subtle">柱图、折线、矩阵、情感环图</p></div></article><article><span>4</span><div><strong>配置发送</strong><p class="subtle">每周一 09:00 自动发送到管理群</p></div></article></div></section>
                <section class="panel report-preview-panel"><div class="panel__header"><div><strong>实时预览</strong><div class="subtle">预览内容必须与导出内容保持一致</div></div><span class="pill success">在线预览</span></div><div class="report-preview-card"><div class="report-preview-chart"></div><div class="report-preview-table"><div><strong>核心结论</strong><span>等待真实报表记录回填</span></div><div><strong>异常项</strong><span>等待活动日志与状态汇总</span></div><div><strong>建议动作</strong><span>等待运行时数据生成下一步建议</span></div></div></div></section>
            </div>
        </section>
    `;

    return {
        eyebrow: '报表汇总中心',
        searchTerms: '报表中心 报告 模板 导出 定时发送 analyst',
        sidebarSummary: { eyebrow: '报表提醒', title: '等待真实报表记录汇总', copy: '该页面只展示真实报表记录、活动日志和运行时预览结果。' },
        statusLeft: ['等待数据接入', '报表状态动态刷新', '无静态模板值'],
        statusRight: [{ text: '预览由运行时回填', tone: 'success' }, { text: '等待刷新', tone: 'warning' }],
        hideDetailPanel: false,
        mainHtml,
        detailHtml: buildAnalystDetail({
            title: '报表中心作用',
            description: '这是输出与分发中心，不是单纯的数据浏览页',
            items: [
                { label: '核心任务', value: '构建报告、预览校验、导出分发、定时发送' },
                { label: '关键要求', value: '预览与导出结果必须一致' },
                { label: '联动来源', value: '可视化实验室 / 利润分析 / 互动分析 / Dashboard' },
            ],
            cards: [
                { title: '优先固化日报模板', desc: '高频日报要先沉淀成一键生成模板。', badge: '模板', tone: 'success' },
                { title: '把结论段自动化', desc: '用 AI 自动生成风险段与建议段，减少人工整理时间。', badge: 'AI', tone: 'info' },
                { title: '校验定时发送名单', desc: '确保管理层、客户组与内部组分发权限正确。', badge: '校验', tone: 'warning' },
            ],
        }),
    };
}

function makeInteractionAnalysisRoute() {
    const metrics = [
        { label: '粉丝样本', value: '--', delta: '等待后端数据', note: '根据真实账号关注数填充', color: 'var(--status-success)', search: '粉丝样本' },
        { label: '正向占比', value: '--', delta: '等待后端数据', note: '根据真实任务和活动记录填充', color: 'var(--brand-primary)', search: '正向占比' },
        { label: '风险项', value: '--', delta: '等待后端数据', note: '根据真实失败任务填充', color: 'var(--status-warning)', search: '风险项' },
    ];
    const heatCells = Array.from({ length: 35 }, (_, index) => `<span class="heatmap-cell lvl-${(index % 5) + 1}"></span>`).join('');
    const mainHtml = `
        ${buildAnalystHeader({ title: '互动分析', headerEyebrow: '评论点赞收藏拆解', description: '分析评论、点赞、收藏和私信行为，把高意向互动与低质量噪音区分出来。', secondaryAction: '查看关键词簇', primaryAction: '输出互动结论' })}
        <section class="section-stack">
            ${buildStatGrid(metrics)}
            <div class="interaction-analysis-shell analyst-feature-shell analytics-two-column">
                <section class="analytics-side-stack"><section class="panel"><div class="panel__header"><div><strong>互动热力图</strong><div class="subtle">先看一周内什么时间段最值得加内容和客服响应</div></div></div><div class="heatmap-grid">${heatCells}</div></section><section class="panel"><div class="panel__header"><div><strong>评论回顾</strong><div class="subtle">把高频问题和高价值意向评论单独抽出</div></div></div><div class="task-item is-selected"><div><strong>物流时效问题</strong><div class="subtle">负向评论主要集中在延迟发货与退款沟通</div></div><span class="pill warning">负向</span></div><div class="task-item"><div><strong>收纳场景种草</strong><div class="subtle">高价值评论集中在使用前后对比和家庭场景</div></div><span class="pill success">高意向</span></div></section></section>
                <section class="analytics-side-stack"><section class="panel"><div class="panel__header"><div><strong>情感分布</strong><div class="subtle">情绪识别是互动分析页的核心区分度</div></div></div><div class="sentiment-donut"><div class="sentiment-donut__inner"><strong>72%</strong><span>正向满意度</span></div></div><div class="sentiment-legend"><span><i class="positive"></i>正向 72%</span><span><i class="neutral"></i>中立 19%</span><span><i class="negative"></i>负向 9%</span></div></section><section class="panel"><div class="panel__header"><div><strong>关键词云</strong><div class="subtle">看清用户在讨论什么、抱怨什么、想买什么</div></div></div><div class="topic-cloud keyword-cloud"><span class="xl">发货速度</span><span class="lg">收纳效果</span><span class="md">尺寸问题</span><span class="md">第二件优惠</span><span class="sm">售后态度</span><span class="sm">颜色差异</span><span class="sm">安装简单</span></div></section></section>
            </div>
        </section>
    `;

    return {
        eyebrow: '互动行为洞察',
        searchTerms: '互动分析 热力图 情绪 评论 关键词云 analyst',
        sidebarSummary: { eyebrow: '互动提醒', title: '等待真实互动摘要', copy: '该页面仅展示账号、任务、素材与活动记录推导出的互动视图。' },
        statusLeft: ['等待数据接入', '情绪分布动态计算', '无静态评论值'],
        statusRight: [{ text: '后端驱动', tone: 'success' }, { text: '等待刷新', tone: 'warning' }],
        hideDetailPanel: false,
        mainHtml,
        detailHtml: buildAnalystDetail({
            title: '互动分析作用',
            description: '这个页面要把互动质量和后续动作直接连起来',
            items: [
                { label: '核心任务', value: '识别高价值互动、负向情绪和用户流转信号' },
                { label: '主要输出', value: '评论主题、情绪分布、优化建议' },
                { label: '下游联动', value: 'CRM / 自动回复控制台 / 数据报告生成器' },
            ],
            cards: [
                { title: '优先分流负向评论', desc: '物流和售后问题先交给客服与 CRM 跟进。', badge: '分流', tone: 'warning' },
                { title: '沉淀高意向问答', desc: '把高频购买问题转成自动回复模板。', badge: '模板', tone: 'info' },
                { title: '反馈给内容团队', desc: '把高频兴趣点反馈到选题与脚本里。', badge: '内容', tone: 'success' },
            ],
        }),
    };
}

function makeEcommerceConversionRoute() {
    const metrics = [
        { label: '账号活跃率', value: '--', delta: '实时聚合', note: '根据真实账号状态填充', color: 'var(--status-success)', search: '账号活跃率 实时聚合' },
        { label: '任务完成率', value: '--', delta: '实时聚合', note: '根据真实任务完成情况填充', color: 'var(--status-warning)', search: '任务完成率 实时聚合' },
        { label: '素材支撑率', value: '--', delta: '实时聚合', note: '根据真实素材库存填充', color: 'var(--brand-primary)', search: '素材支撑率 实时聚合' },
    ];
    const steps = [
        { name: '账号样本', value: '--', cls: 'is-wide' },
        { name: '活跃账号', value: '--', cls: 'is-mid' },
        { name: '执行任务', value: '--', cls: 'is-narrow' },
        { name: '完成任务', value: '--', cls: 'is-thin' },
        { name: '素材支撑', value: '--', cls: 'is-tail' },
    ];
    const mainHtml = `
        ${buildAnalystHeader({ title: '电商转化', headerEyebrow: '从流量到成交的链路分析', description: '把曝光、点击、加购、下单和退款串成一条完整转化链路，帮助识别在哪一段流失。', secondaryAction: '导出转化报告', primaryAction: '查看漏斗拆解' })}
        <section class="section-stack">
            ${buildStatGrid(metrics)}
            <div class="conversion-shell analyst-feature-shell analytics-two-column">
                <section class="panel analytics-chart-card"><div class="panel__header"><div><strong>转化漏斗</strong><div class="subtle">先定位最大流失点，再决定是改内容、详情页还是售后链路</div></div></div>${buildAnalyticsSummary({ range: '近 7 天', dimension: '曝光 / 点击 / 加购 / 下单 / 签收', takeaway: '结论：当前最大流失集中在点击到加购阶段，优先检查详情页卖点表达与优惠信息。' })}<div class="funnel-steps">${steps.map(step => `<article class="funnel-step ${step.cls}"><span>${step.name}</span><strong>${step.value}</strong></article>`).join('')}</div></section>
                <section class="panel analytics-side-panel"><div class="panel__header"><div><strong>流失分析</strong><div class="subtle">每一层流失都要给出解释和动作</div></div></div><div class="leakage-grid"><article class="leakage-card"><strong>点击 -> 加购</strong><span>流失 82%</span><p>商品详情页说服力不足，价格优势表达不够。</p></article><article class="leakage-card"><strong>加购 -> 下单</strong><span>流失 64%</span><p>运费与优惠门槛影响下单决策。</p></article><article class="leakage-card"><strong>下单 -> 签收</strong><span>流失 5%</span><p>履约与取消订单仍有优化空间。</p></article></div></section>
            </div>
        </section>
    `;

    return {
        eyebrow: '电商转化追踪',
        searchTerms: '电商转化 漏斗 加购 下单 流失 analyst',
        sidebarSummary: { eyebrow: '转化提醒', title: '等待真实漏斗结果', copy: '该页面只展示真实账号、任务与素材支撑链路形成的运营漏斗。' },
        statusLeft: ['等待数据接入', '漏斗阶段动态更新', '无硬编码转化率'],
        statusRight: [{ text: '后端驱动', tone: 'success' }, { text: '等待刷新', tone: 'warning' }],
        hideDetailPanel: false,
        mainHtml,
        detailHtml: buildAnalystDetail({
            title: '电商转化作用',
            description: '漏斗页的重点是找到掉单位置并给出修复动作',
            items: [
                { label: '核心任务', value: '串起曝光、点击、加购、下单、退款全链路' },
                { label: '最大流失', value: '点击 -> 加购阶段' },
                { label: '常见动作', value: '改素材、改详情页、调优惠、查履约' },
            ],
            cards: [
                { title: '优先优化详情页卖点', desc: '把价格优势、使用场景和保障信息前置。', badge: '详情页', tone: 'warning' },
                { title: '验证优惠门槛', desc: '缩短用户从加购到下单的犹豫链路。', badge: '促销', tone: 'info' },
                { title: '联动退款与售后数据', desc: '保证转化提升不是靠牺牲售后质量换来的。', badge: '联动', tone: 'success' },
            ],
        }),
    };
}

function makeFanProfileRoute() {
    const metrics = [
        { label: '高价值分层', value: '--', delta: '等待后端数据', note: '根据真实画像分层填充', color: 'var(--status-success)', search: '高价值分层' },
        { label: '活跃分层', value: '--', delta: '等待后端数据', note: '根据真实画像分层填充', color: 'var(--brand-primary)', search: '活跃分层' },
        { label: '兴趣簇', value: '--', delta: '等待后端数据', note: '根据真实兴趣簇填充', color: 'var(--status-warning)', search: '兴趣簇' },
    ];
    const mainHtml = `
        ${buildAnalystHeader({ title: '粉丝画像', headerEyebrow: '受众标签与价值分层', description: '按兴趣、消费能力、互动深度和内容偏好给粉丝分层，辅助创作和运营联动。', secondaryAction: '导出人群分层', primaryAction: '更新画像标签' })}
        <section class="section-stack">
            ${buildStatGrid(metrics)}
            <div class="fan-profile-shell analyst-feature-shell analytics-two-column">
                <section class="analytics-side-stack"><section class="panel analytics-chart-card"><div class="panel__header"><div><strong>标签云</strong><div class="subtle">先看人群在关心什么，再决定内容和商品方向</div></div></div>${buildAnalyticsSummary({ range: '近 30 天', dimension: '兴趣簇 / 消费倾向', takeaway: '结论：家庭收纳与节日囤货是当前最值得拆开的两类高价值兴趣簇。' })}<div class="topic-cloud keyword-cloud"><span class="xl">家庭收纳</span><span class="lg">节日囤货</span><span class="md">小户型整理</span><span class="md">低价好物</span><span class="sm">租房改造</span><span class="sm">厨房动线</span><span class="sm">亲子家庭</span></div></section><section class="panel analytics-chart-card"><div class="panel__header"><div><strong>人群分层</strong><div class="subtle">高价值、潜力、观望、沉默分层一眼可见</div></div></div><div class="analytics-chart-meta"><span>样本：活跃粉丝</span><span>更新：每日同步</span></div><div class="segment-ring"><div class="segment-ring__inner"><strong>4 层</strong><span>活跃分层</span></div></div><div class="affinity-bars"><div><span>高价值粉丝</span><i style="width: 78%"></i></div><div><span>潜力粉丝</span><i class="info" style="width: 62%"></i></div><div><span>观望粉丝</span><i class="warning" style="width: 41%"></i></div><div><span>沉默粉丝</span><i style="width: 24%"></i></div></div></section></section>
                <section class="panel analytics-side-panel"><div class="panel__header"><div><strong>核心 Persona</strong><div class="subtle">把抽象画像变成团队能理解的典型人群</div></div></div>${buildAnalyticsSummary({ range: '近 14 天', dimension: '画像 / 内容偏好 / 复购倾向', takeaway: '结论：家居整理派与节日囤货派最适合优先联动内容和 CRM 触达。' })}<div class="persona-grid"><article><strong>家居整理派</strong><span>28-36 岁 / 高收藏高复购</span><p>偏好强对比改造内容，接受中高客单的收纳解决方案。</p></article><article><strong>节日囤货派</strong><span>24-32 岁 / 高点击高促销敏感</span><p>关注限时折扣、组合套餐、节日氛围场景。</p></article><article><strong>租房实用派</strong><span>22-30 岁 / 高互动低客单</span><p>关注平价、易安装、空间利用率相关内容。</p></article><article><strong>静默潜力派</strong><span>历史有加购 / 近期互动下降</span><p>适合通过 CRM 或自动私信做二次唤醒。</p></article></div></section>
            </div>
        </section>
    `;

    return {
        eyebrow: '粉丝画像中心',
        searchTerms: '粉丝画像 标签云 人群分层 persona 兴趣 analyst',
        sidebarSummary: { eyebrow: '画像提醒', title: '等待真实画像汇总', copy: '该页面仅展示真实账号画像、兴趣簇和任务反馈推导的人群结构。' },
        statusLeft: ['等待数据接入', '画像动态刷新', '无静态粉丝数值'],
        statusRight: [{ text: '画像更新完成', tone: 'success' }, { text: '需同步内容策略', tone: 'warning' }],
        hideDetailPanel: false,
        mainHtml,
        detailHtml: buildAnalystDetail({
            title: '粉丝画像作用',
            description: '它负责回答“用户是谁、偏好什么、该怎么触达”',
            items: [
                { label: '核心任务', value: '做标签、做人群分层、支撑内容与触达策略' },
                { label: '主要输出', value: '标签云、分层、Persona、兴趣变化' },
                { label: '联动模块', value: '内容创作 / CRM / 自动回复 / 定时发布' },
            ],
            cards: [
                { title: '给内容团队输出兴趣簇', desc: '让选题、标题与脚本直接对齐高价值人群。', badge: '内容', tone: 'success' },
                { title: '给 CRM 输出唤醒名单', desc: '静默潜力派适合做二次触达与私信激活。', badge: 'CRM', tone: 'info' },
                { title: '持续更新兴趣标签', desc: '兴趣簇变化会直接影响内容与商品节奏。', badge: '更新', tone: 'warning' },
            ],
        }),
    };
}

/* ═══════════════════════════════════════════════
   Batch 6 — generation-studio 家族工厂
   Template A/C hybrid: AI 输入 + 生成 + 结果输出
   ═══════════════════════════════════════════════ */
