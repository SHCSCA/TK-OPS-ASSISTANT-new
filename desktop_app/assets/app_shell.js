(function () {
    const RECENT_ROUTES_KEY = 'tkops.recentRoutes';

    const uiState = {
        globalSearch: '',
        account: { statusFilter: 'all', view: 'card', sortMode: 'default' },
        'task-queue': { statusFilter: 'all' },
        searchPanel: { visible: false, activeIndex: 0, results: [] },
        recentRoutes: [],
        detailPanelForced: null,
        notifications: [],
        notificationId: 0,
    };

    function makeSectionRoute(config) {
        const metrics = config.metrics || [
            { label: `${config.title}总量`, value: '24', delta: '+3', note: '本周期稳定推进', color: 'var(--status-success)', search: `${config.title} 总量 稳定` },
            { label: '风险提醒', value: '3', delta: '需关注', note: '高风险项需要人工复核', color: 'var(--status-warning)', search: `${config.title} 风险 告警` },
            { label: '完成率', value: '86%', delta: '+5%', note: '较上个周期改善', color: 'var(--brand-primary)', search: `${config.title} 完成率` },
        ];
        const items = config.items || [
            { title: `${config.title}主任务`, desc: '当前优先级最高的动作。', badge: '优先', tone: 'success', search: `${config.title} 主任务` },
            { title: `${config.title}异常项`, desc: '建议先处理高风险和阻塞节点。', badge: '告警', tone: 'warning', search: `${config.title} 异常项` },
            { title: `${config.title}后续建议`, desc: '完成当前动作后继续下钻复核。', badge: '建议', tone: 'info', search: `${config.title} 建议` },
        ];
        const cards = config.cards || [
            { title: '今日优先事项', desc: `围绕${config.title}先处理最高影响动作。`, badge: '立即跟进', tone: 'warning', search: `${config.title} 今日优先` },
            { title: '历史记录', desc: '查看过往执行记录，便于复用和迭代。', badge: '参考', tone: 'info', search: `${config.title} 历史` },
            { title: '结果沉淀', desc: '执行完成后沉淀结果，便于下一次继续复用。', badge: '复盘', tone: 'success', search: `${config.title} 复盘` },
        ];
        const navItems = config.navItems || ['总览', '主面板', '详情'];
        const formFields = config.formFields || [
            { label: '策略名称', value: `${config.title}主策略` },
            { label: '目标对象', value: '当前工作区 / 默认分组' },
            { label: '执行模式', value: '稳态推进' },
            { label: '优先级', value: '高' },
        ];
        const stripItems = config.stripItems || ['实时状态', '最近变更', '执行建议'];
        const results = config.results || cards;
        const detailItems = config.detailItems || ['当前状态稳定', '仍有少量风险待处理', '建议先处理高影响动作'];
        const resolvedLayout =
            config.layout
            || ({
                account: 'governance',
                creator: ['素材中心', '视频剪辑', '创意工坊'].includes(config.title) ? 'studio' : 'ai',
                analyst: 'analytics',
                automation: 'automation',
                system: 'system',
                crm: 'crm',
            }[config.breadcrumb] || 'default');

        const metricsHtml = metrics
            .map(
                (metric) => `<article class="stat-card" data-search="${metric.search}"><div><div class="subtle">${metric.label}</div><div class="stat-card__value">${metric.value}</div></div><div class="stat-card__delta" style="color: ${metric.color};"><span>${metric.delta}</span><span class="subtle">${metric.note}</span></div></article>`
            )
            .join('');

        const itemsHtml = items
            .map(
                (item, index) => `<div class="task-item ${index === 0 ? 'is-selected' : ''}" data-search="${item.search}"><div><strong>${item.title}</strong><div class="subtle">${item.desc}</div></div><span class="pill ${item.tone}">${item.badge}</span></div>`
            )
            .join('');

        const cardsHtml = cards
            .map(
                (item) => `<article class="board-card" data-search="${item.search}"><strong>${item.title}</strong><div class="subtle">${item.desc}</div><div class="status-strip"><span class="pill ${item.tone}">${item.badge}</span></div></article>`
            )
            .join('');

        const navHtml = navItems
            .map((item, index) => `<button class="studio-tool ${index === 0 ? 'is-selected' : ''}" type="button">${item}</button>`)
            .join('');

        const formHtml = formFields
            .map(
                (field) => `
                    <div class="form-field">
                        <label>${field.label}</label>
                        <input type="text" value="${field.value}">
                    </div>
                `
            )
            .join('');

        const stripHtml = stripItems.map((item) => `<div class="timeline-chip"><strong>${item}</strong><div class="subtle">${config.title} 当前保持同步</div></div>`).join('');

        const resultHtml = results
            .map(
                (item) => `<article class="report-card" data-search="${item.search}"><strong>${item.title}</strong><div class="subtle">${item.desc}</div><div class="status-strip"><span class="pill ${item.tone}">${item.badge}</span></div></article>`
            )
            .join('');

        const kanbanHtml = config.kanban
            ? `<div class="kanban-grid">${config.kanban
                .map(
                    (column) => `<section class="kanban-column"><div class="kanban-column__title">${column.title}</div><div class="kanban-list">${column.items.map((item) => `<article class="ticket-card" data-search="${item.search}"><strong>${item.title}</strong><div class="subtle">${item.desc}</div></article>`).join('')}</div></section>`
                )
                .join('')}</div>`
            : '';

        const calendarHtml = config.calendarDays
            ? `<div class="calendar-grid">${config.calendarDays
                .map(
                    (day) => `<section class="calendar-day"><strong>${day.title}</strong><div class="subtle">${day.subtle}</div>${day.slots.map((slot) => `<div class="calendar-slot" data-search="${slot.search}">${slot.title}</div>`).join('')}</section>`
                )
                .join('')}</div>`
            : '';

        const tableHtml = config.table
            ? `
                <section class="table-card">
                    <div class="table-card__header">
                        <div>
                            <strong>${config.table.title}</strong>
                            <div class="subtle">${config.table.description}</div>
                        </div>
                    </div>
                    <div class="table-wrapper">
                        <table>
                            <thead><tr>${config.table.columns.map((column) => `<th>${column}</th>`).join('')}</tr></thead>
                            <tbody>
                                ${config.table.rows
                                    .map(
                                        (row) => `
                                            <tr class="route-row" data-search="${row.search}">
                                                ${row.cells.map((cell) => `<td>${cell}</td>`).join('')}
                                            </tr>
                                        `
                                    )
                                    .join('')}
                            </tbody>
                        </table>
                    </div>
                </section>
            `
            : '';

        let mainHtml = '';
        if (resolvedLayout === 'governance') {
            mainHtml = `
                <div class="breadcrumbs"><span>${config.breadcrumb}</span><span>/</span><span>${config.title}</span></div>
                <div class="page-header">
                    <div>
                        <div class="eyebrow">${config.headerEyebrow}</div>
                        <h1>${config.title}</h1>
                        <p>${config.description}</p>
                    </div>
                    <div class="header-actions">
                        <button class="secondary-button" type="button">${config.secondaryAction}</button>
                        <button class="primary-button" type="button">${config.primaryAction}</button>
                    </div>
                </div>
                <section class="section-stack">
                    <div class="stat-grid">${metricsHtml}</div>
                    <div class="operations-grid">
                        ${tableHtml || `<section class="panel"><div class="panel__header"><div><strong>${config.title}清单</strong><div class="subtle">关键对象与当前状态</div></div></div><div class="board-list">${cardsHtml}</div></section>`}
                        <section class="panel">
                            <div class="panel__header"><div><strong>${config.listTitle || '待处理队列'}</strong><div class="subtle">${config.listDesc || '先处理高影响和高风险项。'}</div></div></div>
                            <div class="workbench-list">${itemsHtml}</div>
                        </section>
                        <section class="panel">
                            <div class="panel__header"><div><strong>${config.sideTitle || '协同提示'}</strong><div class="subtle">${config.sideDesc || '帮助用户减少跨页切换。'}</div></div></div>
                            <div class="board-list">${cardsHtml}</div>
                        </section>
                    </div>
                    ${kanbanHtml}
                </section>
            `;
        } else if (resolvedLayout === 'studio') {
            mainHtml = `
                <div class="breadcrumbs"><span>${config.breadcrumb}</span><span>/</span><span>${config.title}</span></div>
                <div class="page-header">
                    <div>
                        <div class="eyebrow">${config.headerEyebrow}</div>
                        <h1>${config.title}</h1>
                        <p>${config.description}</p>
                    </div>
                    <div class="header-actions">
                        <button class="secondary-button" type="button">${config.secondaryAction}</button>
                        <button class="primary-button" type="button">${config.primaryAction}</button>
                    </div>
                </div>
                <section class="section-stack">
                    <div class="stat-grid">${metricsHtml}</div>
                    <div class="studio-shell">
                        <aside class="studio-rail">${navHtml}</aside>
                        <div class="section-stack">
                            <section class="studio-stage">
                                <div class="toolbar-strip"><div class="toolbar-strip__group"><strong>${config.title}工作区</strong><span class="subtle">当前页面采用独立创作布局</span></div><div class="toolbar-strip__group"><button class="secondary-button" type="button">预览</button><button class="secondary-button" type="button">导出</button></div></div>
                                <div class="asset-grid">${resultHtml}</div>
                            </section>
                            <div class="frame-strip">${stripHtml}</div>
                        </div>
                        <aside class="inspector-panel">${cardsHtml}</aside>
                    </div>
                </section>
            `;
        } else if (resolvedLayout === 'analytics') {
            mainHtml = `
                <div class="breadcrumbs"><span>${config.breadcrumb}</span><span>/</span><span>${config.title}</span></div>
                <div class="page-header">
                    <div>
                        <div class="eyebrow">${config.headerEyebrow}</div>
                        <h1>${config.title}</h1>
                        <p>${config.description}</p>
                    </div>
                    <div class="header-actions">
                        <button class="secondary-button" type="button">${config.secondaryAction}</button>
                        <button class="primary-button" type="button">${config.primaryAction}</button>
                    </div>
                </div>
                <section class="section-stack">
                    <div class="summary-strip">${stripHtml}</div>
                    <div class="lab-shell">
                        <aside class="lab-sidebar">${cardsHtml}</aside>
                        <div class="section-stack">
                            <section class="lab-canvas">
                                <div class="report-grid">${resultHtml}</div>
                            </section>
                            ${tableHtml}
                        </div>
                        <aside class="inspector-panel"><section class="panel"><div class="panel__header"><div><strong>${config.sideTitle || '分析要点'}</strong><div class="subtle">${config.sideDesc || '把洞察转成后续动作。'}</div></div></div><div class="metric-kv">${detailItems.map((item, index) => `<div class="detail-item"><span class="subtle">${index === 0 ? '当前状态' : index === 1 ? '主要风险' : '建议动作'}</span><strong>${item}</strong></div>`).join('')}</div></section></aside>
                    </div>
                </section>
            `;
        } else if (resolvedLayout === 'automation') {
            mainHtml = `
                <div class="breadcrumbs"><span>${config.breadcrumb}</span><span>/</span><span>${config.title}</span></div>
                <div class="page-header">
                    <div>
                        <div class="eyebrow">${config.headerEyebrow}</div>
                        <h1>${config.title}</h1>
                        <p>${config.description}</p>
                    </div>
                    <div class="header-actions">
                        <button class="secondary-button" type="button">${config.secondaryAction}</button>
                        <button class="primary-button" type="button">${config.primaryAction}</button>
                    </div>
                </div>
                <section class="section-stack">
                    <div class="stat-grid">${metricsHtml}</div>
                    <div class="workflow-shell">
                        <aside class="workflow-sidebar">${cardsHtml}</aside>
                        <div class="section-stack">
                            <section class="workflow-canvas">
                                ${kanbanHtml || calendarHtml || `<div class="kanban-grid"><section class="kanban-column"><div class="kanban-column__title">待执行</div><div class="kanban-list">${itemsHtml}</div></section><section class="kanban-column"><div class="kanban-column__title">进行中</div><div class="kanban-list">${cardsHtml}</div></section><section class="kanban-column"><div class="kanban-column__title">已完成</div><div class="kanban-list">${resultHtml}</div></section></div>`}
                            </section>
                            ${tableHtml}
                        </div>
                        <aside class="workflow-properties"><section class="panel"><div class="panel__header"><div><strong>${config.sideTitle || '运行属性'}</strong><div class="subtle">${config.sideDesc || '当前自动化链路的配置摘要。'}</div></div></div><div class="detail-list">${detailItems.map((item, index) => `<div class="detail-item"><span class="subtle">${index === 0 ? '当前状态' : index === 1 ? '阻塞点' : '建议'}</span><strong>${item}</strong></div>`).join('')}</div></section></aside>
                    </div>
                </section>
            `;
        } else if (resolvedLayout === 'ai') {
            const providers = config.aiProviders || ['OpenAI', 'Anthropic', 'Google Gemini', '自定义接入'];
            const models = config.aiModels || ['GPT-4o', 'GPT-4o-mini', 'Claude 3.5 Sonnet', 'Gemini 1.5 Pro'];
            const agentRole = config.agentRole || `你是一个专业的 TK 电商${config.title}助手`;
            const providerOptions = providers.map((p, i) => `<option${i === 0 ? ' selected' : ''}>${p}</option>`).join('');
            const modelOptions = models.map((m, i) => `<option${i === 0 ? ' selected' : ''}>${m}</option>`).join('');
            mainHtml = `
                <div class="breadcrumbs"><span>${config.breadcrumb}</span><span>/</span><span>${config.title}</span></div>
                <div class="page-header">
                    <div>
                        <div class="eyebrow">${config.headerEyebrow}</div>
                        <h1>${config.title}</h1>
                        <p>${config.description}</p>
                    </div>
                    <div class="header-actions">
                        <button class="secondary-button" type="button">${config.secondaryAction}</button>
                        <button class="primary-button" type="button">${config.primaryAction}</button>
                    </div>
                </div>
                <section class="section-stack">
                    <div class="prompt-shell">
                        <div class="section-stack">
                            <section class="panel ai-config-panel">
                                <div class="panel__header"><div><strong>AI 模型配置</strong><div class="subtle">选择供应商、模型和生成参数</div></div></div>
                                <div class="ai-config-grid">
                                    <div class="form-field"><label>供应商</label><select>${providerOptions}</select></div>
                                    <div class="form-field"><label>模型</label><select>${modelOptions}</select></div>
                                    <div class="form-field"><label>温度</label><input type="range" min="0" max="100" value="70"><span class="subtle">0.7</span></div>
                                    <div class="form-field"><label>最大 Tokens</label><input type="number" value="2048" min="256" max="8192" step="256"></div>
                                </div>
                            </section>
                            <section class="panel">
                                <div class="panel__header"><div><strong>Agent 提示词</strong><div class="subtle">定义 AI 角色、目标和生成约束</div></div></div>
                                <div class="form-field"><label>角色定义</label><input type="text" value="${agentRole}"></div>
                                <div class="form-field"><label>系统提示</label><textarea>${config.promptText || `围绕${config.title}生成更贴近业务目标的结果。`}</textarea></div>
                            </section>
                            <section class="panel"><div class="panel__header"><div><strong>模板与动作</strong><div class="subtle">保留常用模版和一键动作</div></div></div><div class="template-grid">${cardsHtml.replaceAll('board-card', 'template-card')}</div></section>
                        </div>
                        <div class="section-stack">
                            <section class="report-preview"><div class="result-grid">${resultHtml}</div></section>
                            ${tableHtml}
                        </div>
                    </div>
                </section>
            `;
        } else if (resolvedLayout === 'system') {
            mainHtml = `
                <div class="breadcrumbs"><span>${config.breadcrumb}</span><span>/</span><span>${config.title}</span></div>
                <div class="page-header">
                    <div>
                        <div class="eyebrow">${config.headerEyebrow}</div>
                        <h1>${config.title}</h1>
                        <p>${config.description}</p>
                    </div>
                    <div class="header-actions">
                        <button class="secondary-button" type="button">${config.secondaryAction}</button>
                        <button class="primary-button" type="button">${config.primaryAction}</button>
                    </div>
                </div>
                <section class="section-stack">
                    <div class="status-strip">${stripHtml}</div>
                    <div class="system-shell">
                        <aside class="mini-panel-list">${cardsHtml.replaceAll('board-card', 'settings-card')}</aside>
                        <div class="section-stack">
                            <section class="panel"><div class="panel__header"><div><strong>${config.title}设置</strong><div class="subtle">系统页面采用配置面板与状态表的组合布局</div></div></div><div class="settings-grid">${formHtml}</div></section>
                            ${tableHtml}
                        </div>
                    </div>
                </section>
            `;
        } else if (resolvedLayout === 'crm') {
            mainHtml = `
                <div class="breadcrumbs"><span>${config.breadcrumb}</span><span>/</span><span>${config.title}</span></div>
                <div class="page-header">
                    <div>
                        <div class="eyebrow">${config.headerEyebrow}</div>
                        <h1>${config.title}</h1>
                        <p>${config.description}</p>
                    </div>
                    <div class="header-actions">
                        <button class="secondary-button" type="button">${config.secondaryAction}</button>
                        <button class="primary-button" type="button">${config.primaryAction}</button>
                    </div>
                </div>
                <section class="section-stack">
                    <div class="stat-grid">${metricsHtml}</div>
                    <div class="crm-grid">
                        <section class="panel"><div class="panel__header"><div><strong>客户分层</strong><div class="subtle">按客户价值和状态分组跟进</div></div></div><div class="board-list">${cardsHtml.replaceAll('board-card', 'crm-card')}</div></section>
                        <section class="panel"><div class="panel__header"><div><strong>跟进节奏</strong><div class="subtle">把动作和线索统一放进同一页</div></div></div>${kanbanHtml || `<div class="kanban-grid"><section class="kanban-column"><div class="kanban-column__title">待跟进</div><div class="kanban-list">${itemsHtml}</div></section><section class="kanban-column"><div class="kanban-column__title">沟通中</div><div class="kanban-list">${resultHtml.replaceAll('report-card', 'ticket-card')}</div></section><section class="kanban-column"><div class="kanban-column__title">已成交</div><div class="kanban-list">${cardsHtml.replaceAll('board-card', 'ticket-card')}</div></section></div>`}</section>
                    </div>
                    ${tableHtml}
                </section>
            `;
        } else {
            mainHtml = `
                <div class="breadcrumbs"><span>${config.breadcrumb}</span><span>/</span><span>${config.title}</span></div>
                <div class="page-header">
                    <div>
                        <div class="eyebrow">${config.headerEyebrow}</div>
                        <h1>${config.title}</h1>
                        <p>${config.description}</p>
                    </div>
                    <div class="header-actions">
                        <button class="secondary-button" type="button">${config.secondaryAction}</button>
                        <button class="primary-button" type="button">${config.primaryAction}</button>
                    </div>
                </div>
                <section class="section-stack">
                    <div class="stat-grid">${metricsHtml}</div>
                    <div class="content-grid shell-content-grid">
                        <section class="panel">
                            <div class="panel__header"><div><strong>${config.listTitle}</strong><div class="subtle">${config.listDesc}</div></div></div>
                            <div class="metric-list">${itemsHtml}</div>
                        </section>
                        <section class="panel">
                            <div class="panel__header"><div><strong>${config.sideTitle}</strong><div class="subtle">${config.sideDesc}</div></div></div>
                            <div class="detail-list">
                                <div class="detail-item"><span class="subtle">今日动作</span><strong>${config.sideStats?.[0] || detailItems[0]}</strong></div>
                                <div class="detail-item"><span class="subtle">风险提醒</span><strong>${config.sideStats?.[1] || detailItems[1]}</strong></div>
                                <div class="detail-item"><span class="subtle">推荐下一步</span><strong>${config.sideStats?.[2] || detailItems[2]}</strong></div>
                            </div>
                        </section>
                    </div>
                    ${tableHtml}
                </section>
            `;
        }

        return {
            eyebrow: config.eyebrow,
            searchTerms: `${config.title} ${config.description} ${config.breadcrumb} ${config.eyebrow}`,
            sidebarSummary: config.sidebarSummary || {
                eyebrow: `${config.title}提醒`,
                title: `${config.title}正在推进`,
                copy: `先处理${config.title}中的高影响动作，再继续下钻复核。`,
            },
            statusLeft: config.statusLeft || [`${config.title} 已接入`, '状态同步正常', '最近更新 12:48'],
            statusRight: config.statusRight || [{ text: '运行正常', tone: 'success' }, { text: '待复核 2', tone: 'warning' }],
            mainHtml,
            detailHtml: `
                <div class="detail-root">
                    <section class="panel">
                        <div class="panel__header"><div><strong>${config.title}摘要</strong><div class="subtle">${config.detailDesc}</div></div></div>
                        <div class="detail-list">
                            <div class="detail-item"><span class="subtle">当前状态</span><strong>${detailItems[0]}</strong></div>
                            <div class="detail-item"><span class="subtle">重点风险</span><strong>${detailItems[1]}</strong></div>
                            <div class="detail-item"><span class="subtle">建议</span><strong>${detailItems[2]}</strong></div>
                        </div>
                    </section>
                    <section class="panel">
                        <div class="panel__header"><div><strong>值班动作</strong><div class="subtle">右侧详情继续承载决策提示</div></div></div>
                        <div class="board-list">${cardsHtml}</div>
                    </section>
                </div>
            `,
        };
    }

    function makeStubRoute(config) {
        return makeSectionRoute({
            secondaryAction: config.secondaryAction || '查看详情',
            primaryAction: config.primaryAction || '立即处理',
            listTitle: config.listTitle || '当前清单',
            listDesc: config.listDesc || '把高影响动作和当前状态压缩到同一屏。',
            sideTitle: config.sideTitle || '操作建议',
            sideDesc: config.sideDesc || '减少来回切换，直接进入处理流程。',
            detailDesc: config.detailDesc || `${config.title} 页面的状态与建议摘要。`,
            ...config,
        });
    }

    function makeConfigCenterRoute(config) {
        const navSections = config.navSections || [];
        const formGroups = config.formGroups || [];
        const notices = config.notices || [];
        const detailGroups = config.detailGroups || [];
        const detailCards = config.detailCards || [];
        const configType = config.configType || 'settings';

        const navHtml = navSections
            .map((section, i) => `<button class="config-nav-item ${i === 0 ? 'is-selected' : ''}" type="button" data-search="${section.search || section.label}">${section.icon ? `<span class="config-nav-icon">${section.icon}</span>` : ''}<span>${section.label}</span>${section.badge ? `<span class="pill ${section.badgeTone || 'info'}">${section.badge}</span>` : ''}</button>`)
            .join('');

        const noticeHtml = notices
            .map((n) => `<section class="notice-banner ${n.tone ? 'notice-banner--' + n.tone : ''}"><div><strong>${n.title}</strong><div>${n.desc}</div></div></section>`)
            .join('');

        let centerContentHtml = '';

        if (configType === 'settings') {
            centerContentHtml = formGroups
                .map((group) => `
                    <section class="config-form-group">
                        <div class="config-form-group__header"><strong>${group.title}</strong><div class="subtle">${group.desc}</div></div>
                        <div class="config-form-fields">
                            ${group.fields
                                .map((f) => `
                                    <div class="config-field" data-search="${f.search || f.label}">
                                        <label class="config-field__label">${f.label}${f.required ? ' <span class="config-field__req">*</span>' : ''}</label>
                                        <div class="config-field__control">
                                            ${f.type === 'select'
                                                ? `<div class="config-select"><span>${f.value}</span><span class="config-select__arrow">▾</span></div>`
                                                : f.type === 'toggle'
                                                    ? `<div class="config-toggle ${f.value === true || f.value === '开' ? 'is-on' : ''}"><span class="config-toggle__track"></span><span class="config-toggle__label">${f.value === true || f.value === '开' ? '开' : '关'}</span></div>`
                                                    : `<div class="config-input">${f.value || ''}</div>`
                                            }
                                        </div>
                                        ${f.hint ? `<div class="config-field__hint subtle">${f.hint}</div>` : ''}
                                    </div>
                                `)
                                .join('')}
                        </div>
                    </section>
                `)
                .join('');
        } else if (configType === 'permissions') {
            const matrix = config.permissionMatrix || {};
            const roles = matrix.roles || [];
            const modules = matrix.modules || [];
            centerContentHtml = `
                <section class="config-form-group">
                    <div class="config-form-group__header"><strong>${matrix.title || '权限矩阵'}</strong><div class="subtle">${matrix.desc || '按角色和模块分配权限'}</div></div>
                    <div class="table-wrapper">
                        <table>
                            <thead><tr><th>模块</th>${roles.map((r) => `<th>${r}</th>`).join('')}</tr></thead>
                            <tbody>
                                ${modules
                                    .map((m) => `<tr data-search="${m.name} ${roles.join(' ')}"><td><strong>${m.name}</strong></td>${m.access.map((a) => `<td><span class="status-chip ${a === '完全' ? 'success' : a === '只读' ? 'info' : a === '禁止' ? 'error' : 'warning'}">${a}</span></td>`).join('')}</tr>`)
                                    .join('')}
                            </tbody>
                        </table>
                    </div>
                </section>
                ${config.memberList
                    ? `<section class="config-form-group">
                        <div class="config-form-group__header"><strong>成员列表</strong><div class="subtle">已注册用户与权限分配</div></div>
                        <div class="table-wrapper">
                            <table>
                                <thead><tr><th>成员</th><th>角色</th><th>最后活跃</th><th>状态</th></tr></thead>
                                <tbody>
                                    ${config.memberList.map((m) => `<tr data-search="${m.name} ${m.role}"><td><strong>${m.name}</strong></td><td>${m.role}</td><td class="subtle">${m.lastActive}</td><td><span class="status-chip ${m.statusTone}">${m.status}</span></td></tr>`).join('')}
                                </tbody>
                            </table>
                        </div>
                    </section>`
                    : ''}
            `;
        } else if (configType === 'wizard') {
            const steps = config.wizardSteps || [];
            centerContentHtml = `
                <div class="wizard-progress">
                    ${steps.map((s, i) => `<div class="wizard-step ${i === 0 ? 'is-active' : i < (config.currentStep || 0) ? 'is-done' : ''}" data-search="${s.search || s.title}"><span class="wizard-step__num">${i + 1}</span><div class="wizard-step__info"><strong>${s.title}</strong><div class="subtle">${s.desc}</div></div></div>`).join('<div class="wizard-step__connector"></div>')}
                </div>
                <section class="config-form-group wizard-active-step">
                    <div class="config-form-group__header"><strong>${steps[0]?.title || '当前步骤'}</strong><div class="subtle">${steps[0]?.desc || ''}</div></div>
                    <div class="config-form-fields">
                        ${(steps[0]?.fields || [])
                            .map((f) => `
                                <div class="config-field" data-search="${f.search || f.label}">
                                    <label class="config-field__label">${f.label}</label>
                                    <div class="config-field__control">
                                        ${f.type === 'select'
                                            ? `<div class="config-select"><span>${f.value}</span><span class="config-select__arrow">▾</span></div>`
                                            : `<div class="config-input">${f.value || ''}</div>`
                                        }
                                    </div>
                                    ${f.hint ? `<div class="config-field__hint subtle">${f.hint}</div>` : ''}
                                </div>
                            `)
                            .join('')}
                    </div>
                </section>
            `;
        }

        const detailGroupsHtml = detailGroups
            .map((g) => `<div class="detail-item"><span class="subtle">${g.label}</span><strong>${g.value}</strong></div>`)
            .join('');

        const detailCardsHtml = detailCards
            .map((card) => `<article class="strip-card" data-search="${card.search || card.title}"><strong>${card.title}</strong><div class="subtle">${card.desc}</div><span class="pill ${card.tone}">${card.badge}</span></article>`)
            .join('');

        return {
            eyebrow: config.eyebrow,
            searchTerms: `${config.title} ${config.description} ${config.headerEyebrow} ${config.breadcrumb}`,
            sidebarSummary: config.sidebarSummary,
            statusLeft: config.statusLeft,
            statusRight: config.statusRight,
            mainHtml: `
                <div class="breadcrumbs"><span>${config.breadcrumb}</span><span>/</span><span>${config.title}</span></div>
                <div class="page-header">
                    <div>
                        <div class="eyebrow">${config.headerEyebrow}</div>
                        <h1>${config.title}</h1>
                        <p>${config.description}</p>
                    </div>
                    <div class="header-actions">
                        <button class="secondary-button" type="button">${config.secondaryAction}</button>
                        <button class="primary-button" type="button">${config.primaryAction}</button>
                    </div>
                </div>
                <section class="config-center-shell">
                    <nav class="config-nav">${navHtml}</nav>
                    <div class="config-center-body section-stack">
                        ${noticeHtml}
                        ${centerContentHtml}
                    </div>
                </section>
                ${configType !== 'wizard' ? '' : `<div class="wizard-actions"><button class="secondary-button" type="button">上一步</button><button class="primary-button" type="button">下一步</button></div>`}
            `,
            detailHtml: `
                <div class="detail-root">
                    <section class="panel">
                        <div class="panel__header"><div><strong>${config.detailTitle || config.title + '说明'}</strong><div class="subtle">${config.detailDesc || '当前配置项的状态与建议'}</div></div></div>
                        <div class="detail-list">${detailGroupsHtml}</div>
                    </section>
                    ${detailCardsHtml ? `<section class="panel"><div class="panel__header"><div><strong>配置建议</strong><div class="subtle">根据当前状态给出的优化提示</div></div></div><div class="workbench-side-list">${detailCardsHtml}</div></section>` : ''}
                </div>
            `,
        };
    }

    function makeContentWorkbenchRoute(config) {
        const metrics = config.metrics || [];
        const summaryChips = config.summaryChips || [];
        const inlineSummary = config.inlineSummary === true;
        const hideWorkbenchSidebar = config.hideWorkbenchSidebar === true;
        const railTools = config.railTools || [];
        const focusCards = config.focusCards || [];
        const bottomCards = config.bottomCards || [];
        const sideCards = config.sideCards || [];
        const detailCards = config.detailCards || [];
        const detailGroups = config.detailGroups || [];

        const metricsHtml = metrics
            .map(
                (metric) => `<article class="stat-card" data-search="${metric.search || metric.label}"><div><div class="subtle">${metric.label}</div><div class="stat-card__value">${metric.value}</div></div><div class="stat-card__delta" style="color: ${metric.color};"><span>${metric.delta}</span><span class="subtle">${metric.note}</span></div></article>`
            )
            .join('');

        const railHtml = railTools
            .map(
                (tool, index) => `<button class="workbench-tool ${index === 0 ? 'is-selected' : ''}" type="button" data-search="${tool.search || tool.label}"><span>${tool.icon}</span><small>${tool.label}</small></button>`
            )
            .join('');

        const summaryChipsHtml = summaryChips
            .map(
                (chip) => `<article class="workbench-summary-chip" data-search="${chip.search || chip.label}"><span class="subtle">${chip.label}</span><strong>${chip.value}</strong><small>${chip.note}</small></article>`
            )
            .join('');

        const sideCardsHtml = sideCards
            .map(
                (card) => `<article class="workbench-sidecard" data-search="${card.search || card.title}"><div class="workbench-sidecard__head"><strong>${card.title}</strong><span class="pill ${card.tone}">${card.badge}</span></div><div class="subtle">${card.desc}</div></article>`
            )
            .join('');

        const detailCardsHtml = detailCards
            .map(
                (card) => `<article class="workbench-sidecard" data-search="${card.search || card.title}"><div class="workbench-sidecard__head"><strong>${card.title}</strong><span class="pill ${card.tone}">${card.badge}</span></div><div class="subtle">${card.desc}</div></article>`
            )
            .join('');

        const focusCardsHtml = focusCards
            .map(
                (card) => `<article class="focus-card ${card.size ? `focus-card--${card.size}` : ''}" data-search="${card.search || card.title}"><div class="focus-card__head"><strong>${card.title}</strong><span class="pill ${card.tone}">${card.badge}</span></div><div class="subtle">${card.desc}</div>${card.meta ? `<div class="focus-card__meta">${card.meta}</div>` : ''}</article>`
            )
            .join('');

        const bottomCardsHtml = bottomCards
            .map(
                (card) => `<article class="strip-card" data-search="${card.search || card.title}"><strong>${card.title}</strong><div class="subtle">${card.desc}</div><span class="pill ${card.tone}">${card.badge}</span></article>`
            )
            .join('');

        let centerHtml = '';
        let sideHtml = '';
        let bottomHtml = '';

        if (config.workbenchType === 'video-editor') {
            centerHtml = `
                <section class="workbench-canvas workbench-canvas--video video-editing-studio">
                    <div class="video-studio-topbar">
                        <div>
                            <strong>精剪工作区</strong>
                            <div class="subtle">素材库、节目监视器、时间线和剪辑控制集中在此</div>
                        </div>
                        <div class="toolbar-strip__group"><button class="secondary-button" type="button">试看导出</button><button class="secondary-button" type="button">添加批注</button></div>
                    </div>
                    <div class="video-monitor-grid" data-search="视频剪辑 素材预览 节目监视器 播放器">
                        <section class="source-browser-shell">
                            <div class="source-browser-head">
                                <div><strong>素材库</strong><div class="subtle">双击素材加入时间线，单击预览缩略图</div></div>
                                <button class="secondary-button" type="button">导入素材</button>
                            </div>
                            <div class="source-browser-tabs">
                                <span class="is-selected" data-type="video">视频 <em>6</em></span>
                                <span data-type="image">图片 <em>8</em></span>
                                <span data-type="subtitle">字幕 <em>3</em></span>
                                <span data-type="audio">音频 <em>2</em></span>
                            </div>
                            <div class="source-thumb-grid" data-search="素材缩略图 视频 图片 字幕 音频">
                                <div class="source-thumb is-selected" data-kind="video">
                                    <div class="source-thumb__preview source-thumb__preview--video"><span class="source-thumb__dur">00:18</span></div>
                                    <div class="source-thumb__name">节日 B-roll_03</div>
                                    <div class="source-thumb__tag"><span class="pill info">产品特写</span></div>
                                </div>
                                <div class="source-thumb" data-kind="video">
                                    <div class="source-thumb__preview source-thumb__preview--video"><span class="source-thumb__dur">00:32</span></div>
                                    <div class="source-thumb__name">开箱展示 A</div>
                                    <div class="source-thumb__tag"><span class="pill success">高转化</span></div>
                                </div>
                                <div class="source-thumb" data-kind="video">
                                    <div class="source-thumb__preview source-thumb__preview--video"><span class="source-thumb__dur">00:09</span></div>
                                    <div class="source-thumb__name">使用场景 02</div>
                                    <div class="source-thumb__tag"><span class="pill warning">待调色</span></div>
                                </div>
                                <div class="source-thumb" data-kind="video">
                                    <div class="source-thumb__preview source-thumb__preview--video"><span class="source-thumb__dur">00:14</span></div>
                                    <div class="source-thumb__name">仓库发货流程</div>
                                    <div class="source-thumb__tag"><span class="pill info">B-roll</span></div>
                                </div>
                                <div class="source-thumb" data-kind="image">
                                    <div class="source-thumb__preview source-thumb__preview--image"></div>
                                    <div class="source-thumb__name">春季封面 01</div>
                                    <div class="source-thumb__tag"><span class="pill success">已授权</span></div>
                                </div>
                                <div class="source-thumb" data-kind="image">
                                    <div class="source-thumb__preview source-thumb__preview--image"></div>
                                    <div class="source-thumb__name">产品白底图</div>
                                    <div class="source-thumb__tag"><span class="pill info">PNG</span></div>
                                </div>
                                <div class="source-thumb" data-kind="subtitle">
                                    <div class="source-thumb__preview source-thumb__preview--subtitle"><span>SRT</span></div>
                                    <div class="source-thumb__name">核心卖点字幕</div>
                                    <div class="source-thumb__tag"><span class="pill warning">待校对</span></div>
                                </div>
                                <div class="source-thumb" data-kind="audio">
                                    <div class="source-thumb__preview source-thumb__preview--audio"><span>♪</span></div>
                                    <div class="source-thumb__name">背景音乐 轻快版</div>
                                    <div class="source-thumb__tag"><span class="pill success">02:15</span></div>
                                </div>
                            </div>
                            <div class="source-mini-preview">
                                <div class="source-mini-preview__thumb source-mini-preview__thumb--video"></div>
                                <div class="source-mini-preview__info">
                                    <strong>节日 B-roll_03</strong>
                                    <div class="subtle">00:18 · 1080×1920 · 产品特写</div>
                                    <div class="source-mini-preview__meta">
                                        <span>入点 00:02</span><span>出点 00:11</span><span class="pill warning">待授权</span>
                                    </div>
                                </div>
                            </div>
                        </section>
                        <section class="video-preview-shell">
                            <div class="video-preview-head">
                                <div>
                                    <strong>节目监视器</strong>
                                    <div class="subtle">序列: 视频混剪 #18，当前定位第 2 段转场与结尾 CTA</div>
                                </div>
                                <div class="video-preview-tools"><span class="pill info">1080P</span><span class="pill success">自动保存</span></div>
                            </div>
                            <div class="canvas-stage canvas-stage--landscape video-preview-stage">
                                <div class="canvas-chip">00:15 / 01:30</div>
                                <div class="video-preview-markers"><span>片头钩子</span><span>卖点强化</span><span>结尾 CTA</span></div>
                                <div class="video-surface video-surface--editor">
                                    <div class="play-button">播放</div>
                                </div>
                            </div>
                        </section>
                    </div>
                    <div class="transport-bar">
                        <div class="transport-controls"><button class="secondary-button" type="button">回到开头</button><button class="secondary-button" type="button">逐帧</button><button class="secondary-button" type="button">设入点</button><button class="secondary-button" type="button">设出点</button></div>
                        <div class="transport-meta"><span>缩放 125%</span><span>吸附 开</span><span>波形 已展开</span></div>
                    </div>
                    <div class="timeline-board video-timeline-board">
                        <div class="timeline-ruler"><span>00:00</span><span>00:15</span><span>00:30</span><span>00:45</span><span>01:00</span><span>01:15</span><span>01:30</span></div>
                        <div class="timeline-track"><span>V1 主轨</span><div class="timeline-lane"><div class="timeline-block timeline-block--primary">开场钩子 00:00-00:12</div><div class="timeline-block">主片段 00:12-00:45</div><div class="timeline-block">结尾 CTA 01:05-01:30</div></div></div>
                        <div class="timeline-track"><span>V2 补镜</span><div class="timeline-lane"><div class="timeline-block">产品特写 00:18-00:28</div><div class="timeline-block">使用场景 00:46-01:05</div></div></div>
                        <div class="timeline-track"><span>T1 字幕</span><div class="timeline-lane"><div class="timeline-block timeline-block--accent">核心卖点字幕</div><div class="timeline-block timeline-block--accent">收尾 CTA</div></div></div>
                        <div class="timeline-track"><span>A1 音频</span><div class="timeline-lane"><div class="timeline-wave">背景音乐与口播波形预览</div></div></div>
                    </div>
                </section>
            `;
            sideHtml = `
                <section class="panel video-inspector-panel">
                    <div class="panel__header"><div><strong>检查器</strong><div class="subtle">剪辑现场需要处理的素材、字幕和导出事项</div></div></div>
                    <div class="video-inspector-tabs"><span class="is-selected">属性</span><span>字幕</span><span>导出</span></div>
                    <div class="workbench-side-list">${sideCardsHtml}</div>
                    <div class="video-queue-block">
                        <div class="video-queue-block__head"><strong>待办队列</strong><span class="subtle">从上到下按阻塞优先级处理</span></div>
                        <div class="video-queue-list">${bottomCardsHtml}</div>
                    </div>
                </section>
            `;
            bottomHtml = '';
        } else if (config.workbenchType === 'creative-workshop') {
            centerHtml = `
                <section class="workbench-canvas workbench-canvas--creative">
                    <div class="toolbar-strip">
                        <div class="toolbar-strip__group"><strong>创意组合画板</strong><span class="subtle">主题、镜头、口播和卖点在一块板上快速组合</span></div>
                        <div class="toolbar-strip__group"><button class="secondary-button" type="button">锁定版本</button><button class="secondary-button" type="button">生成对比</button></div>
                    </div>
                    <div class="focus-grid" data-search="创意工坊 主题 镜头 口播 组合">
                        ${focusCardsHtml}
                    </div>
                </section>
            `;
            sideHtml = `
                <section class="panel">
                    <div class="panel__header"><div><strong>方案评分</strong><div class="subtle">右列不再是通用摘要，而是创意评分与版本建议</div></div></div>
                    <div class="workbench-side-list">${sideCardsHtml}</div>
                </section>
            `;
            bottomHtml = `
                <section class="panel">
                    <div class="panel__header"><div><strong>实验轨迹</strong><div class="subtle">把已试过的创意组合和保留建议沉淀下来</div></div></div>
                    <div class="workbench-strip-grid">${bottomCardsHtml}</div>
                </section>
            `;
        } else if (config.workbenchType === 'ai-content-factory') {
            centerHtml = `
                <section class="workbench-canvas workbench-canvas--factory">
                    <div class="toolbar-strip">
                        <div class="toolbar-strip__group"><strong>内容生产工作流</strong><span class="subtle">节点、批次和产出状态集中显示，不再退化为普通 AI 卡片页</span></div>
                        <div class="toolbar-strip__group"><button class="secondary-button" type="button">保存工作流</button><button class="secondary-button" type="button">运行批次</button></div>
                    </div>
                    <div class="workflow-board" data-search="AI 内容工厂 工作流 节点 生产线">
                        <div class="workflow-node is-active"><strong>输入素材</strong><div class="subtle">文本、链接、商品库</div></div>
                        <div class="workflow-connector"></div>
                        <div class="workflow-node"><strong>AI 脚本</strong><div class="subtle">钩子、结构、CTA</div></div>
                        <div class="workflow-connector"></div>
                        <div class="workflow-node"><strong>语音与字幕</strong><div class="subtle">TTS + 字幕清洗</div></div>
                        <div class="workflow-connector"></div>
                        <div class="workflow-node"><strong>批量剪辑</strong><div class="subtle">封面、片段、导出</div></div>
                    </div>
                </section>
            `;
            sideHtml = `
                <section class="panel">
                    <div class="panel__header"><div><strong>节点库与项目区</strong><div class="subtle">把项目、常用节点和当前批次状态维持在主内容右列</div></div></div>
                    <div class="workbench-side-list">${sideCardsHtml}</div>
                </section>
            `;
            bottomHtml = `
                <section class="panel">
                    <div class="panel__header"><div><strong>批次运行状态</strong><div class="subtle">批量生产要优先展示任务通过率、失败节点和可回放批次</div></div></div>
                    <div class="workbench-strip-grid">${bottomCardsHtml}</div>
                </section>
            `;
        }

        const detailHtml = `
            <div class="detail-root">
                <section class="panel">
                    <div class="panel__header"><div><strong>${config.title}摘要</strong><div class="subtle">${config.detailDesc}</div></div></div>
                    <div class="detail-list">
                        ${detailGroups.map((group) => `<div class="detail-item"><span class="subtle">${group.label}</span><strong>${group.value}</strong></div>`).join('')}
                    </div>
                </section>
                <section class="panel">
                    <div class="panel__header"><div><strong>值班动作</strong><div class="subtle">右侧详情继续承载当前批次的决策提示</div></div></div>
                    <div class="workbench-side-list">${detailCardsHtml || sideCardsHtml}</div>
                </section>
            </div>
        `;

        return {
            eyebrow: config.eyebrow,
            searchTerms: `${config.title} ${config.description} ${config.headerEyebrow} ${config.breadcrumb}`,
            sidebarSummary: config.sidebarSummary,
            statusLeft: config.statusLeft,
            statusRight: config.statusRight,
            hideDetailPanel: config.hideDetailPanel !== false,
            mainHtml: `
                <div class="breadcrumbs"><span>${config.breadcrumb}</span><span>/</span><span>${config.title}</span></div>
                <div class="page-header">
                    <div>
                        <div class="eyebrow">${config.headerEyebrow}</div>
                        <h1>${config.title}</h1>
                        <p>${config.description}</p>
                    </div>
                    <div class="header-actions">
                        <button class="secondary-button" type="button">${config.secondaryAction}</button>
                        <button class="primary-button" type="button">${config.primaryAction}</button>
                    </div>
                </div>
                <section class="section-stack">
                    ${!inlineSummary && summaryChipsHtml ? `<div class="workbench-summary-strip">${summaryChipsHtml}</div>` : (metricsHtml ? `<div class="stat-grid">${metricsHtml}</div>` : '')}
                    <div class="content-workbench-shell ${hideWorkbenchSidebar ? 'content-workbench-shell--compact' : ''}">
                        <aside class="workbench-rail">${railHtml}</aside>
                        <div class="section-stack">${centerHtml}${bottomHtml}</div>
                        ${hideWorkbenchSidebar ? '' : `<aside class="workbench-sidebar">${sideHtml}</aside>`}
                    </div>
                </section>
            `,
            detailHtml,
        };
    }

    /* ═══════════════════════════════════════════════
       Batch 3 — task-ops 家族工厂
       Template E: 顶部状态过滤 + 任务看板/列表/日历 + 状态栏
       ═══════════════════════════════════════════════ */
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
            sidebarSummary: config.sidebarSummary || { eyebrow: `${config.title}提醒`, title: `${config.title}正在推进`, copy: `先处理${config.title}中的高影响项。` },
            statusLeft: config.statusLeft || [`${config.title} 已接入`, '状态正常', '最近更新 12:48'],
            statusRight: config.statusRight || [{ text: '运行正常', tone: 'success' }, { text: '待复核 2', tone: 'warning' }],
            hideDetailPanel: false,
            mainHtml,
            detailHtml: `<div class="detail-root"><section class="panel"><div class="panel__header"><div><strong>${config.sideTitle || '详情面板'}</strong><div class="subtle">${config.sideDesc || '选中条目的详细信息'}</div></div></div><div class="detail-list">${detailItems.map((d, i) => `<div class="detail-item"><span class="subtle">${i === 0 ? '当前状态' : i === 1 ? '风险提醒' : '推荐操作'}</span><strong>${d}</strong></div>`).join('')}</div></section><section class="panel"><div class="panel__header"><div><strong>操作建议</strong><div class="subtle">针对当前选中项的动作建议</div></div></div><div class="board-list">${cardsHtml}</div></section></div>`,
        };
    }

    /* ═══════════════════════════════════════════════
       Batch 5 — analytics-board 家族工厂
       Template A: KPI 卡片 + 图表/分析区 + 洞察面板
       ═══════════════════════════════════════════════ */
    function makeAnalyticsBoardRoute(config) {
        const metrics = config.metrics || [
            { label: `${config.title}总量`, value: '24', delta: '+3', note: '本周期稳定', color: 'var(--status-success)', search: `${config.title} 总量` },
            { label: '风险提醒', value: '3', delta: '需关注', note: '需人工复核', color: 'var(--status-warning)', search: `${config.title} 风险` },
            { label: '完成率', value: '86%', delta: '+5%', note: '较上周期改善', color: 'var(--brand-primary)', search: `${config.title} 完成率` },
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

    function buildAnalystDetail(detail) {
        const items = detail.items || [];
        const cards = detail.cards || [];
        return `<div class="detail-root"><section class="panel"><div class="panel__header"><div><strong>${detail.title}</strong><div class="subtle">${detail.description}</div></div></div><div class="metric-kv">${items.map(item => `<div class="detail-item"><span class="subtle">${item.label}</span><strong>${item.value}</strong></div>`).join('')}</div></section><section class="panel"><div class="panel__header"><div><strong>${detail.cardTitle || '后续动作'}</strong><div class="subtle">把分析结论转成具体执行动作</div></div></div><div class="board-list">${cards.map(card => `<article class="board-card" data-search="${card.search || card.title}"><strong>${card.title}</strong><div class="subtle">${card.desc}</div><div class="status-strip"><span class="pill ${card.tone || 'info'}">${card.badge || '动作'}</span></div></article>`).join('')}</div></section></div>`;
    }

    function makeTrafficBoardRoute() {
        const metrics = [
            { label: '总曝光', value: '284万', delta: '+13%', note: '短视频自然流量继续走高', color: 'var(--status-success)', search: '曝光 284万' },
            { label: '点击率', value: '4.8%', delta: '+0.6%', note: '封面与标题联动见效', color: 'var(--brand-primary)', search: '点击率 4.8' },
            { label: '异常来源', value: '4', delta: '待排查', note: '欧洲渠道与搜索入口波动', color: 'var(--status-warning)', search: '异常来源 4' },
        ];
        const sourceCards = [
            { title: '短视频自然', value: '126万', meta: 'CTR 5.2% / 转化强', tone: 'success' },
            { title: '促销渠道', value: '98万', meta: 'CTR 4.1% / 投流成本升高', tone: 'warning' },
            { title: '搜索入口', value: '60万', meta: 'CTR 3.8% / 需联动关键词分析', tone: 'info' },
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
                        <section class="panel"><div class="panel__header"><div><strong>异常动作建议</strong><div class="subtle">把波动直接映射为下一步排查动作</div></div></div><div class="traffic-action-list"><div class="task-item is-selected"><div><strong>先查欧洲渠道素材</strong><div class="subtle">重点确认封面疲劳与开场三秒留存</div></div><span class="pill warning">优先</span></div><div class="task-item"><div><strong>联动利润页看关键词价值</strong><div class="subtle">搜索入口波动可能是低价值词替换导致</div></div><span class="pill info">联动</span></div><div class="task-item"><div><strong>复盘促销投流成本</strong><div class="subtle">排查高投入但低转化的渠道组合</div></div><span class="pill success">增长</span></div></div></section>
                    </div>
                    <section class="table-card"><div class="table-card__header"><div><strong>渠道表现拆解</strong><div class="subtle">曝光、点击、成交流向在一张表里看清</div></div></div><div class="table-wrapper"><table><thead><tr><th>渠道</th><th>波动</th><th>原因判断</th><th>建议动作</th></tr></thead><tbody>${tableRows.map(row => `<tr class="route-row" data-search="${row.join(' ')}">${row.map(cell => `<td>${cell}</td>`).join('')}</tr>`).join('')}</tbody></table></div></section>
                </div>
            </section>
        `;

        return {
            eyebrow: '流量分析中心',
            searchTerms: '流量看板 曝光 点击率 渠道 搜索 促销 analyst',
            sidebarSummary: { eyebrow: '流量提醒', title: '4 个异常来源待分析', copy: '建议先查欧洲渠道回落，再联动利润页看关键词价值。' },
            statusLeft: ['曝光 284万', '异常来源 4', 'CTR 4.8%'],
            statusRight: [{ text: '自然流量增长', tone: 'success' }, { text: '异常来源 4', tone: 'warning' }],
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
                    { title: '复盘促销渠道预算结构', desc: '对高成本渠道先做 ROI 复核。', badge: '预算', tone: 'success' },
                ],
            }),
        };
    }

    function makeVisualLabRoute() {
        const metrics = [
            { label: '实验项目', value: '12', delta: '+3', note: '本周新增 3 个图表实验', color: 'var(--status-success)', search: '实验项目 12' },
            { label: '实时数据源', value: '8', delta: '在线', note: '可直接拖入实验画布', color: 'var(--brand-primary)', search: '数据源 8' },
            { label: '模板复用率', value: '67%', delta: '+9%', note: '图表模板开始沉淀', color: 'var(--status-warning)', search: '模板复用率 67' },
        ];
        const sources = ['店铺经营日报', '视频互动日志', '投流成本表', '搜索关键词池'];
        const chartTypes = ['折线图', '柱状图', '漏斗图', '热力图', '矩阵图', '环形图'];
        const mainHtml = `
            ${buildAnalystHeader({ title: '可视化实验室', headerEyebrow: '假设验证与图表拼装', description: '把实验指标、图表组合、洞察注释和导出结果放到一个实验空间里。', secondaryAction: '导出图表', primaryAction: '保存实验视图' })}
            <section class="section-stack">
                ${buildStatGrid(metrics)}
                <div class="visual-lab-shell analyst-feature-shell">
                    <section class="panel visual-lab-column"><div class="panel__header"><div><strong>数据源</strong><div class="subtle">选择实验输入与图表库</div></div></div><div class="data-source-list">${sources.map((source, index) => `<button class="data-source-item ${index === 0 ? 'is-selected' : ''}" type="button"><strong>${source}</strong><span>${index === 0 ? '实时同步' : '已连接'}</span></button>`).join('')}</div><div class="subtle section-note">图表库</div><div class="chart-type-grid">${chartTypes.map(type => `<button class="chart-type-btn" type="button">${type}</button>`).join('')}</div></section>
                    <section class="visual-lab-center"><div class="panel visual-preview-panel"><div class="panel__header"><div><strong>实验画布</strong><div class="subtle">图表组合、对照实验与注释在同一视图完成</div></div><div class="analytics-chart-toggles"><button class="task-view-btn is-active" type="button">1D</button><button class="task-view-btn" type="button">1W</button><button class="task-view-btn" type="button">1M</button></div></div><div class="visual-preview-stage"><div class="visual-preview-line"></div><div class="visual-preview-overlay"><span>CTR 4.8%</span><span>CVR 2.2%</span><span>成本 -6%</span></div></div></div><div class="visual-kpi-row"> <article class="panel visual-mini-card"><strong>封面 A</strong><span>点击率 4.8%</span><em>优于基线</em></article><article class="panel visual-mini-card"><strong>标题 B</strong><span>转化率 1.9%</span><em>待继续观察</em></article><article class="panel visual-mini-card"><strong>话题 C</strong><span>转化率 2.5%</span><em>建议扩大</em></article></div></section>
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
            { label: '监控竞品', value: '18', delta: '+2', note: '新增 2 个高增长对手', color: 'var(--status-success)', search: '竞品 18' },
            { label: '高风险动作', value: '5', delta: '需跟进', note: '集中在价格战和内容投流', color: 'var(--status-warning)', search: '高风险动作 5' },
            { label: '可借鉴主题', value: '9', delta: '+3', note: '本周出现新的高转化选题', color: 'var(--brand-primary)', search: '借鉴主题 9' },
        ];
        const rivals = [
            { name: 'Glowmart UK', fans: '32.4万', delta: '+8.4%', tone: 'success' },
            { name: 'TrendBox DE', fans: '18.7万', delta: '-2.1%', tone: 'warning' },
            { name: 'NovaDaily US', fans: '44.2万', delta: '+11.3%', tone: 'success' },
            { name: 'My Account', fans: '27.8万', delta: '+4.2%', tone: 'info' },
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
            sidebarSummary: { eyebrow: '竞品提醒', title: '5 个高风险动作待复盘', copy: '重点关注价格战、达人投流和爆款封面结构，避免直接复制高风险动作。' },
            statusLeft: ['竞品 18', '高风险动作 5', '可借鉴主题 9'],
            statusRight: [{ text: '监控在线', tone: 'success' }, { text: '风险 5', tone: 'warning' }],
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
                    { title: '沉淀主题模板', desc: '把高转化主题整理给内容创作团队直接复用。', badge: '复用', tone: 'info' },
                ],
            }),
        };
    }

    function makeProfitAnalysisRoute() {
        const metrics = [
            { label: '总销售额', value: '286.4万', delta: '+9%', note: '营收保持稳定增长', color: 'var(--status-success)', search: '总销售额 286.4万' },
            { label: '总成本', value: '200.0万', delta: '+12%', note: '广告与履约成本上升', color: 'var(--status-warning)', search: '总成本 200万' },
            { label: '净利润', value: '86.4万', delta: '+7%', note: '利润仍然向上但压力增大', color: 'var(--brand-primary)', search: '净利润 86.4万' },
            { label: 'ROI', value: '1.43', delta: '+0.05', note: '仍高于目标线', color: 'var(--status-success)', search: 'ROI 1.43' },
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
            sidebarSummary: { eyebrow: '利润提醒', title: '3 个店铺利润率下滑', copy: '建议先联动流量与订单页，确认是流量质量还是履约成本问题。' },
            statusLeft: ['利润 86.4万', '下滑店铺 3', '广告占比 22%'],
            statusRight: [{ text: '总体增长', tone: 'success' }, { text: '成本上升', tone: 'warning' }],
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
                    { title: '联动订单与退款页', desc: '利润问题需要和订单质量、售后问题一起看。', badge: '联动', tone: 'success' },
                ],
            }),
        };
    }

    function makeBlueOceanRoute() {
        const metrics = [
            { label: '机会池', value: '24', delta: '+6', note: '本周新识别 6 个机会点', color: 'var(--status-success)', search: '机会池 24' },
            { label: '高潜象限', value: '7', delta: '重点关注', note: '高需求低竞争区域', color: 'var(--brand-primary)', search: '高潜象限 7' },
            { label: '需规避赛道', value: '5', delta: '红海', note: '竞争强度已明显过高', color: 'var(--status-warning)', search: '红海 5' },
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
            sidebarSummary: { eyebrow: '机会提醒', title: '7 个高潜机会点待验证', copy: '优先验证收纳整理与厨房置物两条机会线，再同步给内容和选品团队。' },
            statusLeft: ['机会池 24', '高潜 7', '红海 5'],
            statusRight: [{ text: '高潜机会增加', tone: 'success' }, { text: '红海 5', tone: 'warning' }],
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
            { label: '报告模板', value: '18', delta: '+4', note: '新增 4 个专题模板', color: 'var(--status-success)', search: '报告模板 18' },
            { label: '待生成报告', value: '6', delta: '今日', note: '含日报与周报任务', color: 'var(--status-warning)', search: '待生成报告 6' },
            { label: '定时发送', value: '9', delta: '启用中', note: '客户与管理层分发已接入', color: 'var(--brand-primary)', search: '定时发送 9' },
        ];
        const mainHtml = `
            ${buildAnalystHeader({ title: '报表中心', headerEyebrow: '经营报表生成与归档', description: '承接日报、周报、专题报表和外发下载，方便分析师和管理者统一查看输出。', secondaryAction: '批量导出报表', primaryAction: '生成新报表' })}
            <section class="section-stack">
                ${buildStatGrid(metrics)}
                <div class="report-center-shell analyst-feature-shell">
                    <section class="panel report-templates-panel"><div class="panel__header"><div><strong>模板库</strong><div class="subtle">选择常用模板或收藏模板快速开报</div></div></div><div class="report-template-list"><button class="data-source-item is-selected" type="button"><strong>经营日报</strong><span>默认模板</span></button><button class="data-source-item" type="button"><strong>利润专题</strong><span>财务复盘</span></button><button class="data-source-item" type="button"><strong>互动洞察</strong><span>评论与情绪</span></button><button class="data-source-item" type="button"><strong>蓝海调研</strong><span>机会发现</span></button></div></section>
                    <section class="panel report-builder-panel"><div class="panel__header"><div><strong>报告配置流程</strong><div class="subtle">字段、筛选、图表与发送规则分步完成</div></div></div><div class="report-builder-steps"><article><span>1</span><div><strong>选择字段</strong><p class="subtle">曝光、转化、利润、退款、情绪指数</p></div></article><article><span>2</span><div><strong>设置筛选</strong><p class="subtle">近 7 天 / 英德站 / 高价值账号组</p></div></article><article><span>3</span><div><strong>选择图表</strong><p class="subtle">柱图、折线、矩阵、情感环图</p></div></article><article><span>4</span><div><strong>配置发送</strong><p class="subtle">每周一 09:00 自动发送到管理群</p></div></article></div></section>
                    <section class="panel report-preview-panel"><div class="panel__header"><div><strong>实时预览</strong><div class="subtle">预览内容必须与导出内容保持一致</div></div><span class="pill success">在线预览</span></div><div class="report-preview-card"><div class="report-preview-chart"></div><div class="report-preview-table"><div><strong>核心结论</strong><span>欧洲店铺利润下滑，需先优化履约成本</span></div><div><strong>异常项</strong><span>搜索入口波动 + 退款率偏高</span></div><div><strong>建议动作</strong><span>先修关键词池，再排查售后流程</span></div></div></div></section>
                </div>
            </section>
        `;

        return {
            eyebrow: '报表汇总中心',
            searchTerms: '报表中心 报告 模板 导出 定时发送 analyst',
            sidebarSummary: { eyebrow: '报表提醒', title: '6 份报告待生成', copy: '先处理管理层日报和利润专题，再安排客户汇报模板的定时发送。' },
            statusLeft: ['模板 18', '待生成 6', '定时发送 9'],
            statusRight: [{ text: '预览正常', tone: 'success' }, { text: '待生成 6', tone: 'warning' }],
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
            { label: '互动总量', value: '12.8万', delta: '+14%', note: '收藏与评论增长明显', color: 'var(--status-success)', search: '互动总量 12.8万' },
            { label: '正向情绪', value: '72%', delta: '+5%', note: '内容反馈更聚焦好评', color: 'var(--brand-primary)', search: '正向情绪 72' },
            { label: '负向评论', value: '218', delta: '需处理', note: '集中在物流与售后问题', color: 'var(--status-warning)', search: '负向评论 218' },
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
            sidebarSummary: { eyebrow: '互动提醒', title: '218 条负向评论待处理', copy: '建议先把物流和售后问题推给客服与 CRM，再把高价值评论沉淀成内容方向。' },
            statusLeft: ['互动 12.8万', '正向 72%', '负向 218'],
            statusRight: [{ text: '整体向好', tone: 'success' }, { text: '负向评论待处理', tone: 'warning' }],
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
            { label: '曝光到点击', value: '4.8%', delta: '+0.6%', note: '首屏素材继续改善', color: 'var(--status-success)', search: '曝光点击 4.8' },
            { label: '点击到加购', value: '18%', delta: '-1.4%', note: '详情页吸引力下降', color: 'var(--status-warning)', search: '点击加购 18' },
            { label: '下单转化', value: '6.2%', delta: '+0.3%', note: '最终成交仍稳定', color: 'var(--brand-primary)', search: '下单转化 6.2' },
        ];
        const steps = [
            { name: '曝光', value: '284万', cls: 'is-wide' },
            { name: '点击', value: '13.6万', cls: 'is-mid' },
            { name: '加购', value: '2.4万', cls: 'is-narrow' },
            { name: '下单', value: '8,436', cls: 'is-thin' },
            { name: '签收', value: '7,982', cls: 'is-tail' },
        ];
        const mainHtml = `
            ${buildAnalystHeader({ title: '电商转化', headerEyebrow: '从流量到成交的链路分析', description: '把曝光、点击、加购、下单和退款串成一条完整转化链路，帮助识别在哪一段流失。', secondaryAction: '导出转化报告', primaryAction: '查看漏斗拆解' })}
            <section class="section-stack">
                ${buildStatGrid(metrics)}
                <div class="conversion-shell analyst-feature-shell analytics-two-column">
                    <section class="panel"><div class="panel__header"><div><strong>转化漏斗</strong><div class="subtle">先定位最大流失点，再决定是改内容、详情页还是售后链路</div></div></div><div class="funnel-steps">${steps.map(step => `<article class="funnel-step ${step.cls}"><span>${step.name}</span><strong>${step.value}</strong></article>`).join('')}</div></section>
                    <section class="panel"><div class="panel__header"><div><strong>流失分析</strong><div class="subtle">每一层流失都要给出解释和动作</div></div></div><div class="leakage-grid"><article class="leakage-card"><strong>点击 -> 加购</strong><span>流失 82%</span><p>商品详情页说服力不足，价格优势表达不够。</p></article><article class="leakage-card"><strong>加购 -> 下单</strong><span>流失 64%</span><p>运费与优惠门槛影响下单决策。</p></article><article class="leakage-card"><strong>下单 -> 签收</strong><span>流失 5%</span><p>履约与取消订单仍有优化空间。</p></article></div></section>
                </div>
            </section>
        `;

        return {
            eyebrow: '电商转化追踪',
            searchTerms: '电商转化 漏斗 加购 下单 流失 analyst',
            sidebarSummary: { eyebrow: '转化提醒', title: '详情页说服力偏弱', copy: '当前最大流失发生在点击到加购阶段，优先优化详情页表达与优惠信息。' },
            statusLeft: ['CTR 4.8%', '加购率 18%', '下单转化 6.2%'],
            statusRight: [{ text: '最终成交稳定', tone: 'success' }, { text: '中段流失偏高', tone: 'warning' }],
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
            { label: '高价值粉丝', value: '8,420', delta: '+11%', note: '高互动高消费用户继续增长', color: 'var(--status-success)', search: '高价值粉丝 8420' },
            { label: '活跃分层', value: '4 层', delta: '稳定', note: '可直接联动内容和触达策略', color: 'var(--brand-primary)', search: '活跃分层 4层' },
            { label: '新增兴趣簇', value: '6', delta: '+2', note: '家庭收纳与节日囤货最强', color: 'var(--status-warning)', search: '兴趣簇 6' },
        ];
        const mainHtml = `
            ${buildAnalystHeader({ title: '粉丝画像', headerEyebrow: '受众标签与价值分层', description: '按兴趣、消费能力、互动深度和内容偏好给粉丝分层，辅助创作和运营联动。', secondaryAction: '导出人群分层', primaryAction: '更新画像标签' })}
            <section class="section-stack">
                ${buildStatGrid(metrics)}
                <div class="fan-profile-shell analyst-feature-shell analytics-two-column">
                    <section class="analytics-side-stack"><section class="panel"><div class="panel__header"><div><strong>标签云</strong><div class="subtle">先看人群在关心什么，再决定内容和商品方向</div></div></div><div class="topic-cloud keyword-cloud"><span class="xl">家庭收纳</span><span class="lg">节日囤货</span><span class="md">小户型整理</span><span class="md">低价好物</span><span class="sm">租房改造</span><span class="sm">厨房动线</span><span class="sm">亲子家庭</span></div></section><section class="panel"><div class="panel__header"><div><strong>人群分层</strong><div class="subtle">高价值、潜力、观望、沉默分层一眼可见</div></div></div><div class="segment-ring"><div class="segment-ring__inner"><strong>4 层</strong><span>活跃分层</span></div></div><div class="affinity-bars"><div><span>高价值粉丝</span><i style="width: 78%"></i></div><div><span>潜力粉丝</span><i class="info" style="width: 62%"></i></div><div><span>观望粉丝</span><i class="warning" style="width: 41%"></i></div><div><span>沉默粉丝</span><i style="width: 24%"></i></div></div></section></section>
                    <section class="panel"><div class="panel__header"><div><strong>核心 Persona</strong><div class="subtle">把抽象画像变成团队能理解的典型人群</div></div></div><div class="persona-grid"><article><strong>家居整理派</strong><span>28-36 岁 / 高收藏高复购</span><p>偏好强对比改造内容，接受中高客单的收纳解决方案。</p></article><article><strong>节日囤货派</strong><span>24-32 岁 / 高点击高促销敏感</span><p>关注限时折扣、组合套餐、节日氛围场景。</p></article><article><strong>租房实用派</strong><span>22-30 岁 / 高互动低客单</span><p>关注平价、易安装、空间利用率相关内容。</p></article><article><strong>静默潜力派</strong><span>历史有加购 / 近期互动下降</span><p>适合通过 CRM 或自动私信做二次唤醒。</p></article></div></section>
                </div>
            </section>
        `;

        return {
            eyebrow: '粉丝画像中心',
            searchTerms: '粉丝画像 标签云 人群分层 persona 兴趣 analyst',
            sidebarSummary: { eyebrow: '画像提醒', title: '高价值粉丝增长 11%', copy: '建议围绕家庭收纳与节日囤货两类兴趣簇，分别给内容和 CRM 团队输出分层策略。' },
            statusLeft: ['高价值 8420', '分层 4', '兴趣簇 6'],
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
    function makeGenerationStudioRoute(config) {
        const cards = config.cards || [
            { title: '生成结果 1', desc: '基于当前输入的最佳输出。', badge: '推荐', tone: 'success', search: `${config.title} 结果 1` },
            { title: '生成结果 2', desc: '候选变体，可用于 A/B 测试。', badge: '变体', tone: 'info', search: `${config.title} 结果 2` },
            { title: '生成结果 3', desc: '调整参数后的备选版本。', badge: '备选', tone: 'warning', search: `${config.title} 结果 3` },
        ];
        const detailItems = config.detailItems || ['当前生成质量稳定', '可尝试调整 prompt', '建议对比多版本后选用'];
        const providers = config.aiProviders || ['OpenAI', 'Anthropic', 'Google Gemini', '自定义接入'];
        const models = config.aiModels || ['GPT-4o', 'GPT-4o-mini', 'Claude 3.5 Sonnet', 'Gemini 1.5 Pro'];
        const agentRole = config.agentRole || `你是一个专业的 TK 电商${config.title}助手`;
        const providerOpts = providers.map((p, i) => `<option${i === 0 ? ' selected' : ''}>${p}</option>`).join('');
        const modelOpts = models.map((m, i) => `<option${i === 0 ? ' selected' : ''}>${m}</option>`).join('');
        const cardsHtml = cards.map(c => `<article class="board-card" data-search="${c.search}"><strong>${c.title}</strong><div class="subtle">${c.desc}</div><div class="status-strip"><span class="pill ${c.tone}">${c.badge}</span></div></article>`).join('');
        const resultHtml = cards.map(c => `<article class="report-card" data-search="${c.search}"><strong>${c.title}</strong><div class="subtle">${c.desc}</div><div class="status-strip"><span class="pill ${c.tone}">${c.badge}</span></div></article>`).join('');
        const tableHtml = config.table
            ? `<section class="table-card"><div class="table-card__header"><div><strong>${config.table.title}</strong><div class="subtle">${config.table.description}</div></div></div><div class="table-wrapper"><table><thead><tr>${config.table.columns.map(c => `<th>${c}</th>`).join('')}</tr></thead><tbody>${config.table.rows.map(r => `<tr class="route-row" data-search="${r.search}">${r.cells.map(c => `<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table></div></section>`
            : '';

        const mainHtml = `
            <div class="breadcrumbs"><span>creator</span><span>/</span><span>${config.title}</span></div>
            <div class="page-header">
                <div><div class="eyebrow">${config.headerEyebrow}</div><h1>${config.title}</h1><p>${config.description}</p></div>
                <div class="header-actions"><button class="secondary-button" type="button">${config.secondaryAction}</button><button class="primary-button" type="button">${config.primaryAction}</button></div>
            </div>
            <section class="section-stack">
                <div class="generation-studio-shell">
                    <div class="gen-input-panel">
                        <section class="panel ai-config-panel">
                            <div class="panel__header"><div><strong>AI 模型配置</strong><div class="subtle">选择供应商、模型和生成参数</div></div></div>
                            <div class="ai-config-grid">
                                <div class="form-field"><label>供应商</label><select>${providerOpts}</select></div>
                                <div class="form-field"><label>模型</label><select>${modelOpts}</select></div>
                                <div class="form-field"><label>温度</label><input type="range" min="0" max="100" value="70"><span class="subtle">0.7</span></div>
                                <div class="form-field"><label>最大 Tokens</label><input type="number" value="2048" min="256" max="8192" step="256"></div>
                            </div>
                        </section>
                        <section class="panel">
                            <div class="panel__header"><div><strong>Agent 提示词</strong><div class="subtle">定义 AI 角色与生成目标</div></div></div>
                            <div class="form-field"><label>角色定义</label><input type="text" value="${agentRole}"></div>
                            <div class="form-field"><label>系统提示</label><textarea>${config.promptText || `围绕${config.title}生成贴近业务目标的结果。`}</textarea></div>
                        </section>
                        <section class="panel"><div class="panel__header"><div><strong>模板与动作</strong><div class="subtle">快速选用常用模板</div></div></div><div class="template-grid">${cardsHtml.replaceAll('board-card', 'template-card')}</div></section>
                    </div>
                    <div class="gen-output-panel">
                        <section class="panel"><div class="panel__header"><div><strong>生成结果</strong><div class="subtle">AI 输出预览与版本管理</div></div><div class="gen-output-actions"><button class="secondary-button" type="button">重新生成</button><button class="primary-button" type="button">采用此版本</button></div></div><div class="result-grid">${resultHtml}</div></section>
                        ${tableHtml}
                    </div>
                </div>
            </section>
        `;

        return {
            eyebrow: config.eyebrow,
            searchTerms: `${config.title} ${config.description} creator ${config.eyebrow}`,
            sidebarSummary: config.sidebarSummary || { eyebrow: `${config.title}提醒`, title: `${config.title}就绪`, copy: `配置好模型和 prompt 后开始生成。` },
            statusLeft: config.statusLeft || [`${config.title} 已接入`, 'AI 服务正常', '最近生成 12:48'],
            statusRight: config.statusRight || [{ text: '模型就绪', tone: 'success' }, { text: '待生成', tone: 'warning' }],
            hideDetailPanel: config.hideDetailPanel !== false,
            mainHtml,
            detailHtml: `<div class="detail-root"><section class="panel"><div class="panel__header"><div><strong>${config.title}摘要</strong><div class="subtle">${config.detailDesc || '生成状态与版本概况。'}</div></div></div><div class="detail-list">${detailItems.map((d, i) => `<div class="detail-item"><span class="subtle">${i === 0 ? '当前状态' : i === 1 ? '优化方向' : '建议'}</span><strong>${d}</strong></div>`).join('')}</div></section><section class="panel"><div class="panel__header"><div><strong>生成动作</strong><div class="subtle">针对输出的后续建议</div></div></div><div class="board-list">${cardsHtml}</div></section></div>`,
        };
    }

    function makeAIConfigDetail(config) {
        const providers = config.aiProviders || ['OpenAI', 'Anthropic', 'Google Gemini', '自定义接入'];
        const models = config.aiModels || ['GPT-4o', 'GPT-4o-mini', 'Claude 3.5 Sonnet', 'Gemini 1.5 Pro'];
        const scopes = config.scopes || ['仅当前页面', '当前模块通用', '全局默认'];
        const providerOpts = providers.map((provider, index) => `<option${index === 0 ? ' selected' : ''}>${provider}</option>`).join('');
        const modelOpts = models.map((model, index) => `<option${index === 0 ? ' selected' : ''}>${model}</option>`).join('');
        const scopeOpts = scopes.map((scope, index) => `<option${index === 0 ? ' selected' : ''}>${scope}</option>`).join('');
        const notes = config.notes || [
            { label: '路由策略', value: '优先走默认供应商，失败后切换备用模型' },
            { label: '当前 Agent', value: config.agentRole || `你是专业的${config.title}助手` },
            { label: '生效范围', value: scopes[0] || '仅当前页面' },
        ];

        return `
            <div class="detail-root ai-side-config-root">
                <section class="panel">
                    <div class="panel__header"><div><strong>AI 运行配置</strong><div class="subtle">把供应商、模型和 Agent 提示词收进右侧，不再留白。</div></div></div>
                    <div class="ai-side-config-grid">
                        <div class="form-field"><label>供应商</label><select>${providerOpts}</select></div>
                        <div class="form-field"><label>模型</label><select>${modelOpts}</select></div>
                        <div class="form-field"><label>生效范围</label><select>${scopeOpts}</select></div>
                        <div class="form-field"><label>调用模式</label><select><option>主模型优先 + 失败回退</option><option>固定模型</option><option>按任务路由</option></select></div>
                    </div>
                </section>
                <section class="panel">
                    <div class="panel__header"><div><strong>Agent 提示词</strong><div class="subtle">在这里定义角色、目标和输出约束。</div></div></div>
                    <div class="form-field"><label>角色定义</label><input type="text" value="${config.agentRole || `你是专业的${config.title}助手`}"></div>
                    <div class="form-field"><label>系统提示</label><textarea>${config.promptText || `围绕${config.title}生成更贴近业务目标、可直接执行的结果。`}</textarea></div>
                    <div class="form-field"><label>输出约束</label><textarea>${config.outputConstraint || '输出需结构清晰、避免空泛表述，并优先给出可直接落地的版本。'}</textarea></div>
                </section>
                <section class="panel">
                    <div class="panel__header"><div><strong>当前策略摘要</strong><div class="subtle">右侧只保留配置相关内容。</div></div></div>
                    <div class="detail-list">${notes.map((item) => `<div class="detail-item"><span class="subtle">${item.label}</span><strong>${item.value}</strong></div>`).join('')}</div>
                    <div class="ai-side-config-actions"><button class="secondary-button" type="button">连接测试</button><button class="primary-button" type="button">保存并应用</button></div>
                </section>
            </div>
        `;
    }

    function makeAssetCenterRoute() {
        return {
            eyebrow: '素材资产库',
            searchTerms: '素材中心 素材分类 素材库 视频 图片 字幕 音频 标签 授权',
            sidebarSummary: { eyebrow: '素材提醒', title: '12 个素材待审核', copy: '先补版权审核，再把高价值素材批量标记到创作链路。' },
            statusLeft: ['素材 2148', '待审 12', '高转化 18'],
            statusRight: [{ text: '库存健康', tone: 'success' }, { text: '待审核 12', tone: 'warning' }],
            hideDetailPanel: false,
            mainHtml: `
                <div class="breadcrumbs"><span>creator</span><span>/</span><span>素材中心</span></div>
                <div class="page-header">
                    <div><div class="eyebrow">内容素材中台</div><h1>素材中心</h1><p>统一查看素材库存、素材分类、授权状态和复用建议，主区直接展示素材，不再只剩说明卡片。</p></div>
                    <div class="header-actions"><button class="secondary-button" type="button">批量打标签</button><button class="primary-button" type="button">上传素材</button></div>
                </div>
                <section class="section-stack asset-center-page">
                    <div class="stat-grid">
                        <article class="stat-card"><div><div class="subtle">素材库存</div><div class="stat-card__value">2,148</div></div><div class="stat-card__delta" style="color:var(--status-success);"><span>+86</span><span class="subtle">近 7 天持续增长</span></div></article>
                        <article class="stat-card"><div><div class="subtle">待审核</div><div class="stat-card__value">12</div></div><div class="stat-card__delta" style="color:var(--status-warning);"><span>需确认版权</span><span class="subtle">避免直接进入批量生成</span></div></article>
                        <article class="stat-card"><div><div class="subtle">复用率</div><div class="stat-card__value">63%</div></div><div class="stat-card__delta" style="color:var(--brand-primary);"><span>+4%</span><span class="subtle">高转化素材已形成库</span></div></article>
                    </div>
                    <div class="asset-center-shell">
                        <aside class="asset-category-column">
                            <section class="panel">
                                <div class="panel__header"><div><strong>素材分类</strong><div class="subtle">先按类型和场景找素材</div></div></div>
                                <div class="asset-category-list">
                                    <button class="asset-category-item is-active"><strong>全部素材</strong><span>2148</span></button>
                                    <button class="asset-category-item"><strong>短视频口播</strong><span>486</span></button>
                                    <button class="asset-category-item"><strong>封面图片</strong><span>322</span></button>
                                    <button class="asset-category-item"><strong>B-roll 镜头</strong><span>517</span></button>
                                    <button class="asset-category-item"><strong>音频 / 配乐</strong><span>209</span></button>
                                    <button class="asset-category-item"><strong>字幕 / 文案</strong><span>614</span></button>
                                </div>
                            </section>
                            <section class="panel">
                                <div class="panel__header"><div><strong>分类文件夹</strong><div class="subtle">保留常用素材分组入口</div></div></div>
                                <div class="workbench-side-list">
                                    <article class="workbench-sidecard"><strong>高价值素材</strong><div class="subtle">18 个高转化素材，适合优先复用。</div></article>
                                    <article class="workbench-sidecard"><strong>待授权复核</strong><div class="subtle">12 个素材待确认版权链路。</div></article>
                                    <article class="workbench-sidecard"><strong>节日营销库</strong><div class="subtle">下周促销活动优先使用的专题资产。</div></article>
                                </div>
                            </section>
                        </aside>
                        <div class="asset-library-column">
                            <section class="panel source-browser-shell asset-library-panel">
                                <div class="source-browser-head">
                                    <div><strong>素材浏览器</strong><div class="subtle">可以直接看到素材缩略图、类型和状态。</div></div>
                                    <button class="secondary-button" type="button">导入素材</button>
                                </div>
                                <div class="asset-library-toolbar">
                                    <div class="form-field asset-search-field"><label>搜索素材</label><input type="text" value="高转化 封面 / 节日 B-roll / 德语字幕"></div>
                                    <div class="asset-filter-row"><span class="is-active">全部</span><span>视频</span><span>图片</span><span>字幕</span><span>音频</span></div>
                                </div>
                                <div class="source-browser-tabs"><span class="is-selected">高价值 <em>18</em></span><span>待审核 <em>12</em></span><span>已授权 <em>1964</em></span><span>最近上传 <em>32</em></span></div>
                                <div class="source-thumb-grid asset-source-grid">
                                    <article class="source-thumb is-selected"><div class="source-thumb__preview source-thumb__preview--video">口播开场<span class="source-thumb__dur">00:18</span></div><div class="source-thumb__name">美区夏促口播开场 A</div><div class="source-thumb__tag"><span class="pill success">视频</span><span class="pill info">高转化</span></div></article>
                                    <article class="source-thumb"><div class="source-thumb__preview source-thumb__preview--image">封面图</div><div class="source-thumb__name">爆款封面模板 09</div><div class="source-thumb__tag"><span class="pill info">图片</span><span class="pill success">已授权</span></div></article>
                                    <article class="source-thumb"><div class="source-thumb__preview source-thumb__preview--subtitle">字幕包</div><div class="source-thumb__name">德国站字幕素材包</div><div class="source-thumb__tag"><span class="pill warning">待审</span><span class="pill info">字幕</span></div></article>
                                    <article class="source-thumb"><div class="source-thumb__preview source-thumb__preview--video">B-roll<span class="source-thumb__dur">00:12</span></div><div class="source-thumb__name">节日促销 B-roll 组</div><div class="source-thumb__tag"><span class="pill success">视频</span><span class="pill warning">需授权</span></div></article>
                                    <article class="source-thumb"><div class="source-thumb__preview source-thumb__preview--audio">♫</div><div class="source-thumb__name">Inspiring Tech Vibe</div><div class="source-thumb__tag"><span class="pill info">音频</span><span class="pill success">已入库</span></div></article>
                                    <article class="source-thumb"><div class="source-thumb__preview source-thumb__preview--image">商品图</div><div class="source-thumb__name">夏季新品白底图组</div><div class="source-thumb__tag"><span class="pill info">图片</span><span class="pill success">可复用</span></div></article>
                                </div>
                            </section>
                            <section class="panel">
                                <div class="panel__header"><div><strong>推荐编组</strong><div class="subtle">把常用素材组合成可直接投放的包。</div></div></div>
                                <div class="asset-pack-grid">
                                    <article class="strip-card"><strong>高转化封面包</strong><div class="subtle">适合商品标题页和爆款标题页直接调用。</div><span class="pill success">18 项</span></article>
                                    <article class="strip-card"><strong>节日营销镜头包</strong><div class="subtle">适合 AI 内容工厂批量剪辑节点使用。</div><span class="pill info">24 项</span></article>
                                    <article class="strip-card"><strong>德语字幕素材包</strong><div class="subtle">待版权复核完成后开放给欧洲项目。</div><span class="pill warning">待审</span></article>
                                </div>
                            </section>
                        </div>
                    </div>
                </section>
            `,
            detailHtml: `
                <div class="detail-root">
                    <section class="panel">
                        <div class="panel__header"><div><strong>当前选中素材</strong><div class="subtle">右侧只保留素材详情与操作。</div></div></div>
                        <div class="source-mini-preview"><div class="source-thumb__preview source-thumb__preview--video">Preview</div><div><strong>美区夏促口播开场 A</strong><div class="subtle">适合短视频开场 3 秒钩子，最近 7 天 CTR 4.9%。</div></div></div>
                        <div class="detail-list">
                            <div class="detail-item"><span class="subtle">素材类型</span><strong>视频 / 00:18</strong></div>
                            <div class="detail-item"><span class="subtle">授权状态</span><strong>已授权</strong></div>
                            <div class="detail-item"><span class="subtle">适配模块</span><strong>爆款标题 / AI 内容工厂</strong></div>
                        </div>
                    </section>
                    <section class="panel">
                        <div class="panel__header"><div><strong>待处理事项</strong><div class="subtle">优先清理阻塞批量创作的素材问题。</div></div></div>
                        <div class="workbench-side-list">
                            <article class="workbench-sidecard"><strong>版权待审 12 项</strong><div class="subtle">先复核德国字幕和节日 B-roll。</div></article>
                            <article class="workbench-sidecard"><strong>建议补分类</strong><div class="subtle">新增"商品细节图"和"达人口播"两个分类。</div></article>
                            <article class="workbench-sidecard"><strong>复用优先</strong><div class="subtle">优先把高价值素材同步到创意工坊与内容工厂。</div></article>
                        </div>
                    </section>
                </div>
            `,
        };
    }

    function makeViralTitleRoute() {
        return {
            eyebrow: '标题生成工作台',
            searchTerms: '爆款标题 标题 模板 A/B 测试 互动率 版本对比',
            sidebarSummary: { eyebrow: '标题提醒', title: '主版本已经收敛', copy: '先确认主钩子，再继续做 A/B 变体扩展。' },
            statusLeft: ['模板 12', '候选 6', '最新评分 8.4/10'],
            statusRight: [{ text: '标题就绪', tone: 'success' }, { text: '待复核 2', tone: 'warning' }],
            hideDetailPanel: false,
            mainHtml: `
                <div class="breadcrumbs"><span>creator</span><span>/</span><span>爆款标题</span></div>
                <div class="page-header">
                    <div><div class="eyebrow">爆款标题实验器</div><h1>爆款标题</h1><p>从热门模板、输入编辑、预测评分到 A/B 方案对比，保留真正有决策价值的内容。</p></div>
                    <div class="header-actions"><button class="secondary-button" type="button">保存标题库</button><button class="primary-button" type="button">AI 智能优化</button></div>
                </div>
                <section class="section-stack viral-title-page">
                    <div class="title-template-strip">
                        <article class="template-showcase-card is-highlight"><span class="pill success">92% 成功率</span><strong>悬念钩子型</strong><div class="subtle">适合先制造认知缺口，拉高停留与点击。</div></article>
                        <article class="template-showcase-card"><span class="pill info">88% 成功率</span><strong>利益直给型</strong><div class="subtle">直接抛结果和收益，适合强转化场景。</div></article>
                        <article class="template-showcase-card"><span class="pill warning">85% 成功率</span><strong>认知偏差型</strong><div class="subtle">强调反常识与对比，适合做第二组变体。</div></article>
                    </div>
                    <section class="panel title-creation-editor">
                        <div class="panel__header"><div><strong>标题编辑区</strong><div class="subtle">输入主标题、标签和钩子方向，避免把解释卡片挤进主操作区</div></div></div>
                        <div class="title-editor-tags"><span># 建议收藏</span><span># 震惊</span><span># 避坑指南</span><span># 深度好文</span></div>
                        <textarea class="title-editor-textarea" placeholder="在此输入或生成你的标题...">只有 1% 的人知道的理财秘籍，看完多赚一万！</textarea>
                        <div class="title-editor-actions"><span class="subtle">18 / 64 字</span><div class="header-actions"><button class="secondary-button" type="button">插入标签</button><button class="primary-button" type="button">生成新方案</button></div></div>
                    </section>
                    <div class="title-metric-grid">
                        <article class="mini-metric-card"><span class="subtle">互动率预测</span><strong>8.4 / 10</strong><small>击败 94% 同类标题</small></article>
                        <article class="mini-metric-card"><span class="subtle">情感共鸣度</span><strong>88%</strong><small>当前标题强于行业均值</small></article>
                        <article class="mini-metric-card"><span class="subtle">可读性评分</span><strong>92%</strong><small>结构完整，适合直接进入测试</small></article>
                    </div>
                    <section class="panel title-variant-board">
                        <div class="panel__header"><div><strong>A/B 方案对比</strong><div class="subtle">主区域只保留可比较的候选标题，不再塞入泛说明卡</div></div></div>
                        <div class="variant-list">
                            <article class="variant-card is-best"><div class="variant-card__head"><span class="pill success">A 方案</span><strong>预期 CTR 4.8%</strong></div><p>只有 1% 的人知道的理财秘籍，看完多赚一万！</p><small>当前最佳，建议作为首轮测试主版本。</small></article>
                            <article class="variant-card"><div class="variant-card__head"><span class="pill info">B 方案</span><strong>预期 CTR 3.2%</strong></div><p>别再盲目理财了！这 3 个坑你一定踩过。</p><small>风险更低，但情绪张力弱于主版本。</small></article>
                            <article class="variant-card"><div class="variant-card__head"><span class="pill warning">扩展方案</span><strong>预期 CTR 3.9%</strong></div><p>看完这套方法，你会重新理解“省钱”这件事。</p><small>适合做保守风格补位版本。</small></article>
                        </div>
                    </section>
                </section>
            `,
            detailHtml: makeAIConfigDetail({
                title: '爆款标题',
                aiProviders: ['OpenAI', 'Anthropic', 'Google Gemini', '自定义接入'],
                aiModels: ['GPT-4o', 'Claude 3.7 Sonnet', 'Gemini 2.0 Flash'],
                agentRole: '你是一个专门做短视频爆款标题策划的增长助手',
                promptText: '根据内容主题、目标受众和平台风格，生成高点击但不过度夸张的标题方案，并输出 A/B 测试方向。',
                outputConstraint: '标题要控制在平台适配长度内，避免绝对化违禁词，并明确标注适合测试的钩子方向。',
                notes: [
                    { label: '当前供应商', value: 'OpenAI / GPT-4o' },
                    { label: '当前 Agent', value: '爆款标题策划助手' },
                    { label: '应用范围', value: '仅爆款标题页' },
                ],
            }),
        };
    }

    function makeScriptExtractorRoute() {
        return {
            eyebrow: '脚本结构提取台',
            searchTerms: '脚本提取 工具 视频 结构 ASR OCR 关键帧',
            sidebarSummary: { eyebrow: '提取提醒', title: '当前任务正在处理中', copy: '先看预览和结构结果，再决定是否继续深度抽帧。' },
            statusLeft: ['分析模式 混合', '处理进度 45%', '预计剩余 02:45'],
            statusRight: [{ text: '提取中', tone: 'warning' }, { text: '结构已输出', tone: 'success' }],
            hideDetailPanel: false,
            mainHtml: `
                <div class="breadcrumbs"><span>creator</span><span>/</span><span>脚本提取工具</span></div>
                <div class="page-header">
                    <div><div class="eyebrow">拆解高表现脚本</div><h1>脚本提取工具</h1><p>顶部先配输入源和分析模式，中间看视频预览与提取结果，底部再放扩展能力，不再和标题页共用布局。</p></div>
                    <div class="header-actions"><button class="secondary-button" type="button">导入样本内容</button><button class="primary-button" type="button">开始提取</button></div>
                </div>
                <section class="section-stack script-extractor-page">
                    <section class="panel extractor-config-bar">
                        <div class="extractor-config-grid">
                            <div class="form-field extractor-url-field"><label>视频源地址</label><input type="text" value="https://example.com/video/viral-case"></div>
                            <div class="form-field"><label>分析模式</label><select><option>混合模式 (ASR + 视觉)</option></select></div>
                            <div class="form-field"><label>关键帧间隔</label><select><option>自动抽帧</option></select></div>
                            <div class="form-field"><label>AI 模型</label><select><option>GPT-4o</option></select></div>
                        </div>
                    </section>
                    <div class="extractor-workspace">
                        <aside class="extractor-preview-column">
                            <section class="panel extractor-preview-panel"><div class="panel__header"><div><strong>视频预览</strong><div class="subtle">左侧固定展示当前进度与视频摘要</div></div></div><div class="extractor-video-stage"><div class="play-button">播放</div></div><div class="extractor-progress-row"><span class="subtle">正在处理第 124 / 300 帧</span><strong>45%</strong></div><div class="progress-bar"><span style="width:45%"></span></div><div class="extractor-stat-grid"><article><span class="subtle">预计剩余</span><strong>02:45</strong></article><article><span class="subtle">已用时长</span><strong>01:12</strong></article></div></section>
                            <section class="panel"><div class="panel__header"><div><strong>AI 实时摘要</strong><div class="subtle">把阶段性结论收成一块短摘要</div></div></div><p class="subtle">该视频当前已拆到第 3 阶段，重点结构是“高密度开场钩子 + 番茄钟示例 + 方法总结”。</p></section>
                        </aside>
                        <div class="extractor-results-column">
                            <section class="panel"><div class="panel__header"><div><strong>提取结果</strong><div class="subtle">右侧主区只保留结果标签、时间轴和内容表格</div></div><div class="extractor-tabs"><span class="is-selected">脚本文案</span><span>视频关键帧</span><span>视觉分析</span></div></div><div class="extractor-result-table"><div class="extractor-result-row"><span>00:00:12</span><div><strong>[视觉描述]</strong><p>主讲人出现在镜头中央，背景为简约办公室风格，向观众挥手。</p></div><em>98%</em></div><div class="extractor-result-row"><span>00:00:15</span><div><strong>[ASR]</strong><p>大家好，欢迎来到本期高效生产力指南。今天我们聊如何掌控时间。</p></div><em>92%</em></div><div class="extractor-result-row"><span>00:00:28</span><div><strong>[视觉描述]</strong><p>画面切换到手机上的番茄钟应用，开始展示具体方法。</p></div><em>95%</em></div></div></section>
                            <section class="panel"><div class="panel__header"><div><strong>衍生能力</strong><div class="subtle">底部保留真正可继续执行的后续动作</div></div></div><div class="extractor-capability-grid"><article class="strip-card"><strong>结构摘要</strong><div class="subtle">自动输出钩子、转折、CTA 三段结构。</div><span class="pill success">可导出</span></article><article class="strip-card"><strong>镜头拆解</strong><div class="subtle">按关键帧分解镜头用途和节奏变化。</div><span class="pill info">可复用</span></article><article class="strip-card"><strong>脚本回写</strong><div class="subtle">提取结果可直接回传到脚本创作页继续改写。</div><span class="pill warning">下一步</span></article></div></section>
                        </div>
                    </div>
                </section>
            `,
            detailHtml: makeAIConfigDetail({
                title: '脚本提取工具',
                aiProviders: ['OpenAI', 'Google Gemini', 'Azure OpenAI', '自定义接入'],
                aiModels: ['GPT-4o', 'Gemini 2.0 Flash', 'gpt-4.1-mini'],
                agentRole: '你是一个负责脚本拆解、结构抽取和镜头识别的分析助手',
                promptText: '结合 ASR、OCR 和画面分析结果，抽取脚本结构、镜头节奏、CTA 位置和可复用表达。',
                outputConstraint: '输出必须包含时间轴、结构标签和可复用结论，不要只返回大段总结。',
                notes: [
                    { label: '当前供应商', value: 'Google Gemini / Gemini 2.0 Flash' },
                    { label: '分析模式', value: 'ASR + 视觉混合分析' },
                    { label: '应用范围', value: '当前提取任务' },
                ],
            }),
        };
    }

    function makeProductTitleRoute() {
        return {
            eyebrow: '商品标题生成器',
            searchTerms: '商品标题 标题优化 SEO 关键词 竞品 模板',
            sidebarSummary: { eyebrow: '优化提醒', title: '当前标题适合继续收敛', copy: '优先确认关键词密度和竞品差异，再选最终版本。' },
            statusLeft: ['核心词 3', '当前行业 服饰', '生成方案 2'],
            statusRight: [{ text: '优化中', tone: 'warning' }, { text: '主方案可用', tone: 'success' }],
            hideDetailPanel: false,
            mainHtml: `
                <div class="breadcrumbs"><span>creator</span><span>/</span><span>商品标题大师</span></div>
                <div class="page-header">
                    <div><div class="eyebrow">商品语义与卖点重写</div><h1>商品标题大师</h1><p>以商品输入、SEO 分析、行业模板和最终方案为四层结构组织，不再沿用标题页的同款骨架。</p></div>
                    <div class="header-actions"><button class="secondary-button" type="button">导入 SKU 列表</button><button class="primary-button" type="button">立即优化</button></div>
                </div>
                <section class="section-stack product-title-page">
                    <div class="product-title-shell">
                        <aside class="product-control-column">
                            <section class="panel"><div class="panel__header"><div><strong>控制台</strong><div class="subtle">左侧保留筛选、模板和行业入口</div></div></div><div class="product-nav-list"><button class="is-active">控制台</button><button>SEO 分析</button><button>分类模板</button><button>历史生成</button></div></section>
                            <section class="panel product-saved-card"><div class="panel__header"><div><strong>已节省时间</strong><div class="subtle">用来承接辅助信息，而不是再放摘要说明</div></div></div><strong class="product-saved-value">124 小时</strong><p class="subtle">通过 AI 优化，当前工作流效率提升 85%。</p></section>
                        </aside>
                        <div class="product-main-column">
                            <section class="panel product-input-panel"><div class="panel__header"><div><strong>输入原始商品名称</strong><div class="subtle">先锁定原始商品名、品类和卖点，再展开下游分析</div></div></div><div class="product-input-row"><input type="text" value="夏季新款纯棉短袖T恤男装韩版潮牌"><button class="primary-button" type="button">立即优化</button></div><div class="product-chip-row"><span>快速生成</span><span>高点击率</span><span>合规检测</span></div></section>
                            <div class="product-insight-grid">
                                <section class="panel"><div class="panel__header"><div><strong>关键词密度建议</strong><div class="subtle">当前最该看的不是大段解释，而是词层级分布</div></div></div><div class="metric-kv"><div class="detail-item"><span class="subtle">核心词</span><strong>纯棉T恤 2.4%</strong></div><div class="detail-item"><span class="subtle">属性词</span><strong>夏季新款 1.8%</strong></div><div class="detail-item"><span class="subtle">修饰词</span><strong>韩版潮流 0.5%</strong></div></div></section>
                                <section class="panel"><div class="panel__header"><div><strong>竞品 TOP 标题</strong><div class="subtle">看竞品结构，而不是堆更多提示卡</div></div></div><div class="workbench-side-list"><article class="workbench-sidecard"><strong>竞品 A</strong><div class="subtle">2024夏季新款国潮重磅纯棉短袖T恤男宽松百搭体恤...</div></article><article class="workbench-sidecard"><strong>竞品 B</strong><div class="subtle">简约基础款圆领纯棉短袖T恤大码男装内搭上衣男...</div></article></div></section>
                            </div>
                            <section class="panel"><div class="panel__header"><div><strong>行业专属模板</strong><div class="subtle">这里保留模板入口，避免混在顶部工具区</div></div></div><div class="product-template-grid"><article class="template-card is-active"><strong>服饰内衣</strong><small>当前激活</small></article><article class="template-card"><strong>数码家电</strong><small>切换模板</small></article><article class="template-card"><strong>美妆护肤</strong><small>切换模板</small></article><article class="template-card"><strong>食品饮料</strong><small>切换模板</small></article></div></section>
                            <section class="panel product-result-board"><div class="panel__header"><div><strong>AI 生成标题方案</strong><div class="subtle">主区只保留最终候选结果</div></div></div><div class="variant-list"><article class="variant-card is-best"><div class="variant-card__head"><span class="pill success">高转化型</span><strong>主推荐</strong></div><p>夏季新款【100%纯棉】重磅男士短袖T恤 2024潮牌宽松韩版百搭上衣</p><small>适合详情页广告投放。</small></article><article class="variant-card"><div class="variant-card__head"><span class="pill info">SEO 加强型</span><strong>备选方案</strong></div><p>【纯棉短袖T恤男】2024夏季新款男装韩版潮流 休闲宽松透气体恤衫</p><small>搜索权重更强，适合自然流量场景。</small></article></div></section>
                        </div>
                    </div>
                </section>
            `,
            detailHtml: makeAIConfigDetail({
                title: '商品标题大师',
                aiProviders: ['OpenAI', 'Anthropic', '阿里通义', '自定义接入'],
                aiModels: ['GPT-4o', 'Claude 3.5 Sonnet', 'qwen-max'],
                agentRole: '你是一个电商 SEO 与商品标题优化助手',
                promptText: '基于商品词、属性词、核心卖点和平台搜索习惯，生成兼顾搜索权重与点击率的商品标题。',
                outputConstraint: '标题必须包含核心品类词，避免堆砌修饰词，并区分自然流量版与高转化版。',
                notes: [
                    { label: '当前供应商', value: 'OpenAI / GPT-4o' },
                    { label: '当前 Agent', value: '商品 SEO 优化助手' },
                    { label: '应用范围', value: '商品标题模块通用' },
                ],
                scopes: ['商品标题模块通用', '仅当前页面', '全局默认'],
            }),
        };
    }

    function makeAICopywriterRoute() {
        return {
            eyebrow: '文案生成控制台',
            searchTerms: 'AI 文案生成 文案 合规 标题 变体 渠道',
            sidebarSummary: { eyebrow: '文案提醒', title: '需优先看合规结果', copy: '先改风险词，再决定是否采用当前版本。' },
            statusLeft: ['写作风格 专业严谨', '长度 300 字', '合规分 72'],
            statusRight: [{ text: '文案已生成', tone: 'success' }, { text: '中等风险', tone: 'warning' }],
            hideDetailPanel: false,
            mainHtml: `
                <div class="breadcrumbs"><span>creator</span><span>/</span><span>AI 文案生成</span></div>
                <div class="page-header">
                    <div><div class="eyebrow">渠道化文案生产</div><h1>AI 文案生成</h1><p>左侧只放生成参数，中间只放输出版本，右侧只放合规检查，三块职责分离。</p></div>
                    <div class="header-actions"><button class="secondary-button" type="button">选择投放渠道</button><button class="primary-button" type="button">立即生成文案</button></div>
                </div>
                <section class="section-stack ai-copy-page">
                    <div class="copywriter-shell">
                        <aside class="copy-settings-column">
                            <section class="panel"><div class="panel__header"><div><strong>生成参数设置</strong><div class="subtle">输入关键词、风格和长度</div></div></div><div class="form-field"><label>产品关键词</label><textarea>请输入产品名称、核心卖点或描述...</textarea></div><div class="copy-tone-list"><button class="is-active">专业严谨</button><button>亲切随性</button><button>幽默风趣</button></div><div class="form-field"><label>文案长度</label><input type="range" min="100" max="1000" value="300"></div></section>
                        </aside>
                        <div class="copy-results-column">
                            <section class="panel"><div class="panel__header"><div><strong>输出版本</strong><div class="subtle">把标题推荐、文案脚本和热门话题放在同一结果容器内切换</div></div><div class="extractor-tabs"><span class="is-selected">标题推荐</span><span>文案脚本</span><span>热门话题</span></div></div><div class="variant-list"><article class="variant-card is-best"><div class="variant-card__head"><span class="pill success">Variant 01</span><strong>推荐采用</strong></div><p>这款划时代的智能助手，让你的工作效率瞬间翻倍！</p><small>适合强利益点的首屏标题。</small></article><article class="variant-card"><div class="variant-card__head"><span class="pill info">Variant 02</span><strong>保守版本</strong></div><p>告别繁琐，极简主义者的生产力新选择：[产品名称]深度体验。</p><small>更适合内容种草与口碑表达。</small></article><article class="variant-card"><div class="variant-card__head"><span class="pill warning">Variant 03</span><strong>建议修改</strong></div><p>全网最强性能，首批用户体验报告正式出炉！</p><small>存在绝对化表达，需先做合规修改。</small></article></div></section>
                            <section class="panel"><div class="panel__header"><div><strong>继续创作</strong><div class="subtle">把下一步动作放在底部而不是侧边重复说明</div></div></div><div class="copy-action-grid"><article class="strip-card"><strong>继续扩写</strong><div class="subtle">补正文案脚本和口播版本。</div><span class="pill success">推荐</span></article><article class="strip-card"><strong>切换渠道</strong><div class="subtle">改成商品详情页或短视频开场。</div><span class="pill info">可切换</span></article><article class="strip-card"><strong>生成话题</strong><div class="subtle">从当前版本延展热词与标签。</div><span class="pill warning">下一步</span></article></div></section>
                        </div>
                        <aside class="copy-compliance-column">
                            <section class="panel"><div class="panel__header"><div><strong>合规自检报告</strong><div class="subtle">右列只承接风险分、风险词和改写建议</div></div></div><div class="copy-score-card"><strong>72</strong><small>中等风险</small></div><div class="metric-kv"><div class="detail-item"><span class="subtle">违规词</span><strong>1</strong></div><div class="detail-item"><span class="subtle">敏感词</span><strong>2</strong></div></div><div class="workbench-side-list"><article class="workbench-sidecard"><strong>风险词：最强</strong><div class="subtle">建议替换为“卓越性能”或“业界领先”。</div></article><article class="workbench-sidecard"><strong>风险词：赚钱</strong><div class="subtle">避免诱导性表达，改成“提升效率”更稳妥。</div></article></div><button class="secondary-button" type="button">导出合规报告</button></section>
                        </aside>
                    </div>
                </section>
            `,
            detailHtml: makeAIConfigDetail({
                title: 'AI 文案生成',
                aiProviders: ['OpenAI', 'Anthropic', 'Google Gemini', '自定义接入'],
                aiModels: ['GPT-4.1', 'Claude 3.7 Sonnet', 'Gemini 1.5 Pro'],
                agentRole: '你是一个懂投放场景和合规要求的营销文案助手',
                promptText: '根据产品卖点、投放渠道和目标受众生成多版本营销文案，并同步给出风险规避建议。',
                outputConstraint: '输出需要区分渠道语气，避免绝对化和收益承诺类表达，并优先给出可投放版本。',
                notes: [
                    { label: '当前供应商', value: 'Anthropic / Claude 3.7 Sonnet' },
                    { label: '当前 Agent', value: '营销文案与合规助手' },
                    { label: '应用范围', value: '当前文案页' },
                ],
            }),
        };
    }

    function makeAIContentFactoryRoute() {
        return {
            eyebrow: '内容批量生产中心',
            searchTerms: 'AI 内容工厂 工作流 节点 批次 生产线 画布',
            sidebarSummary: { eyebrow: '产线提醒', title: '当前批次仍有阻塞', copy: '优先处理语音节点配额和剪辑重试，再继续放量。' },
            statusLeft: ['当前批次 BATCH_0312_01', '通过率 81%', '阻塞节点 2'],
            statusRight: [{ text: '产线运行中', tone: 'success' }, { text: '待重试 2', tone: 'warning' }],
            hideDetailPanel: false,
            mainHtml: `
                <div class="breadcrumbs"><span>creator</span><span>/</span><span>AI 内容工厂</span></div>
                <div class="page-header">
                    <div><div class="eyebrow">多模板批量生成</div><h1>AI 内容工厂</h1><p>按照“左组件库 + 中工作流画布 + 右节点配置 + 底部批次状态”重建成真正的生产工作台。</p></div>
                    <div class="header-actions"><button class="secondary-button" type="button">选择模板集</button><button class="primary-button" type="button">启动批量生产</button></div>
                </div>
                <section class="section-stack aicf-page">
                    <div class="aicf-shell">
                        <aside class="aicf-library-column">
                            <section class="panel"><div class="panel__header"><div><strong>组件库</strong><div class="subtle">节点只放在左列，不再占据主画布上方</div></div></div><div class="aicf-node-palette"><button>输入源</button><button>AI 脚本</button><button>语音合成</button><button>批量剪辑</button><button>成品导出</button></div></section>
                            <section class="panel"><div class="panel__header"><div><strong>我的项目</strong><div class="subtle">最近项目快速切换</div></div></div><div class="workbench-side-list"><article class="workbench-sidecard"><strong>短视频自动化</strong><div class="subtle">当前激活项目</div></article><article class="workbench-sidecard"><strong>播客内容提取</strong><div class="subtle">历史工作流</div></article></div></section>
                        </aside>
                        <div class="aicf-canvas-column">
                            <section class="panel aicf-toolbar-panel"><div class="panel__header"><div><strong>工作流设计</strong><div class="subtle">中区只保留工具栏与节点画布</div></div><div class="gen-output-actions"><button class="secondary-button" type="button">保存</button><button class="primary-button" type="button">运行工作流</button></div></div><div class="aicf-toolbar-meta"><span>缩放 100%</span><span>GPU 加速 已开启</span><span>工作流 ID wf_20240523_001</span></div></section>
                            <section class="panel aicf-workflow-canvas"><div class="aicf-workflow-row"><article class="workflow-stage-card is-active"><strong>输入素材</strong><small>文本、链接、商品库</small></article><span class="workflow-arrow">→</span><article class="workflow-stage-card"><strong>AI 脚本</strong><small>钩子、结构、CTA</small></article><span class="workflow-arrow">→</span><article class="workflow-stage-card"><strong>语音与字幕</strong><small>TTS + 清洗</small></article><span class="workflow-arrow">→</span><article class="workflow-stage-card"><strong>批量剪辑</strong><small>封面、片段、导出</small></article><span class="workflow-arrow">→</span><article class="workflow-stage-card"><strong>导出成品</strong><small>MP4 / MOV</small></article></div></section>
                            <section class="panel"><div class="panel__header"><div><strong>批次运行状态</strong><div class="subtle">底部集中看通过率、失败节点和回放批次</div></div></div><div class="aicf-batch-grid"><article class="strip-card"><strong>BATCH_0312_01</strong><div class="subtle">标题 24 条，脚本 12 条，通过率 86%</div><span class="pill success">运行中</span></article><article class="strip-card"><strong>BATCH_0312_02</strong><div class="subtle">语音节点等待配额恢复，已自动排队。</div><span class="pill warning">排队</span></article><article class="strip-card"><strong>可回放批次</strong><div class="subtle">昨日有 3 个高通过率批次可直接复用。</div><span class="pill info">回放</span></article></div></section>
                        </div>
                        <aside class="aicf-config-column">
                            <section class="panel"><div class="panel__header"><div><strong>节点配置</strong><div class="subtle">右列只给当前选中节点的属性</div></div></div><div class="form-field"><label>当前节点</label><input type="text" value="批量剪辑"></div><div class="form-field"><label>生成比例</label><select><option>9:16</option></select></div><div class="form-field"><label>智能转场</label><select><option>淡入淡出</option></select></div><div class="form-field"><label>背景音乐</label><input type="text" value="Inspiring_Tech_Vibe.mp3"></div><div class="form-field"><label>字幕样式</label><input type="text" value="24px / 白字 / 阴影"></div></section>
                        </aside>
                    </div>
                </section>
            `,
            detailHtml: makeAIConfigDetail({
                title: 'AI 内容工厂',
                aiProviders: ['OpenAI', 'Azure OpenAI', 'Google Gemini', '自定义接入'],
                aiModels: ['GPT-4.1', 'GPT-4o-mini', 'Gemini 2.0 Flash'],
                agentRole: '你是一个负责批量内容生产调度与节点编排的工厂控制助手',
                promptText: '根据素材输入、模板策略和节点配置，生成脚本、语音和剪辑任务，并保证批量任务结构一致。',
                outputConstraint: '输出必须结构化，能够直接映射到工作流节点，不要返回无法落地的泛化建议。',
                notes: [
                    { label: '当前供应商', value: 'Azure OpenAI / GPT-4.1' },
                    { label: '当前 Agent', value: '内容工厂调度助手' },
                    { label: '应用范围', value: '内容工厂生产线' },
                ],
                scopes: ['内容工厂生产线', '当前模块通用', '全局默认'],
            }),
        };
    }

    /* ═══════════════════════════════════════════════
       Batch 7-8 — tool-console 家族工厂
       系统工具类: 状态面板 + 操作区 + 日志
       ═══════════════════════════════════════════════ */
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

    const routes = {
        dashboard: {
            eyebrow: '仪表盘工作台',
            searchTerms: '概览数据看板 dashboard KPI 任务 趋势 系统健康 活动流',
            mainTemplate: 'route-dashboard-main',
            detailTemplate: 'route-dashboard-detail-default',
            sidebarSummary: {
                eyebrow: '今日重点',
                title: 'AI 任务 452 条正在运行',
                copy: '优先处理 3 个异常集群，再回看导出队列和跨店铺同步失败告警。',
            },
            statusLeft: ['AI 服务健康度 98.7%', '最后同步 12:48', '连接状态 正常'],
            statusRight: [
                { text: '运行中 37', tone: 'success' },
                { text: '排队中 28', tone: 'warning' },
                { text: '异常 3', tone: 'error' },
            ],
        },
        account: {
            eyebrow: '账号运营工作台',
            searchTerms: '账号管理 account cookie 代理 登录 环境 隔离',
            mainTemplate: 'route-account-main',
            detailTemplate: 'route-account-detail-default',
            sidebarSummary: {
                eyebrow: '当前提醒',
                title: '4 个异常账号待处理',
                copy: '建议先处理代理异常和 Cookie 过期账号，再继续批量导入和自动回复任务。',
            },
            statusLeft: ['在线 12', '异常 4', '最后检测 12:46'],
            statusRight: [
                { text: 'Cookie 有效 18', tone: 'success' },
                { text: '即将过期 3', tone: 'warning' },
                { text: '隔离未启用 6', tone: 'error' },
            ],
        },
        'ai-provider': {
            eyebrow: 'AI 供应商配置中心',
            searchTerms: 'AI 供应商配置 provider 模型 key 路由 测试',
            mainTemplate: 'route-ai-provider-main',
            detailTemplate: 'route-ai-provider-detail-default',
            sidebarSummary: {
                eyebrow: '配置建议',
                title: '默认模型建议先测试再切换',
                copy: '先做连接验证和模型枚举，再把新路由推广到标题、脚本和工作流页面。',
            },
            statusLeft: ['启用 Provider 3', '默认路由 OpenAI', '最后验证 12:43'],
            statusRight: [
                { text: '连接正常', tone: 'success' },
                { text: '备用路由 1', tone: 'warning' },
            ],
        },
        'task-queue': {
            eyebrow: '任务调度中心',
            searchTerms: '任务队列 task queue 运行中 排队 异常 调度',
            mainTemplate: 'route-task-queue-main',
            detailTemplate: 'route-task-queue-detail-default',
            sidebarSummary: {
                eyebrow: '队列摘要',
                title: '运行中 37 条，排队 28 条',
                copy: '优先检查 9 条异常任务，再按业务价值调整内容生成和导出队列优先级。',
            },
            statusLeft: ['运行中 37', '排队中 28', '异常 9'],
            statusRight: [
                { text: '完成 54', tone: 'success' },
                { text: '需重试 4', tone: 'error' },
            ],
        },
        'group-management': makeListManagementRoute({
            breadcrumb: 'account',
            eyebrow: '账号组织编排',
            headerEyebrow: '组织结构工作台',
            title: '分组管理',
            description: '把店铺、地区、业务线和风险等级统一编组，方便后续批量检测、批量登录和批量任务投放。',
            primaryAction: '新建分组',
            secondaryAction: '导出分组结构',
            listTitle: '重点分组',
            listDesc: '优先关注高风险和高价值分组。',
            sideTitle: '操作建议',
            sideDesc: '面向运营负责人的分组调整建议。',
            sideStats: ['新增高价值组 2 个', '异常账号分散在 3 个组', '先补齐德国站和英国站规则'],
            metrics: [
                { label: '分组总数', value: '32', delta: '+4', note: '本周新增欧洲专项组', color: 'var(--status-success)', search: '分组总数 32 欧洲 专项' },
                { label: '高风险分组', value: '5', delta: '需复核', note: '集中在代理与 Cookie 问题', color: 'var(--status-warning)', search: '高风险分组 5 代理 cookie' },
                { label: '自动同步覆盖率', value: '86%', delta: '+8%', note: '分组标签与店铺数据已打通', color: 'var(--brand-primary)', search: '同步 覆盖率 86' },
            ],
            items: [
                { title: '欧洲站高价值组', desc: '包含 18 个内容账号，适合优先分配优质素材。', badge: '优先', tone: 'success', search: '欧洲站 高价值 内容账号 优先' },
                { title: 'Cookie 风险组', desc: '3 个账号将在 48 小时内过期，建议单独续签。', badge: '48h', tone: 'warning', search: 'cookie 风险 48 小时 续签' },
                { title: '代理异常组', desc: '德国、英国两组代理稳定性偏低，需要切换备用链路。', badge: '告警', tone: 'error', search: '代理 异常 德国 英国 告警' },
            ],
            detailDesc: '通过分组编排降低批量动作的出错概率。',
            detailItems: ['32 个分组运行正常', '5 个高风险分组需复核', '先修复代理异常组再做批量导入'],
            sidebarSummary: { eyebrow: '组织提醒', title: '5 个高风险分组待复核', copy: '建议先处理欧洲代理异常组，再同步 Cookie 风险组续签计划。' },
            statusLeft: ['分组 32', '高风险 5', '最近变更 12:21'],
            statusRight: [{ text: '同步正常', tone: 'success' }, { text: '需复核 5', tone: 'warning' }],
        }),
        'device-management': makeListManagementRoute({
            eyebrow: '设备与环境中心', breadcrumb: 'account', headerEyebrow: '隔离环境总览', title: '设备管理', description: '统一查看浏览器隔离环境、代理、指纹配置和异常设备占用情况。', secondaryAction: '导出设备报告', primaryAction: '新增设备环境', listTitle: '设备池摘要', listDesc: '把异常设备和空闲设备分开管理。', sideTitle: '维护建议', sideDesc: '避免设备与账号混绑带来风险。', sideStats: ['空闲设备 12 台', '环境异常 3 台', '优先修复德国站设备池'], metrics: [{ label: '设备总量', value: '64', delta: '+6', note: '本周新增 6 台环境', color: 'var(--status-success)', search: '设备 总量 64' }, { label: '隔离覆盖率', value: '91%', delta: '+3%', note: '大部分账号已进入独立环境', color: 'var(--brand-primary)', search: '隔离 覆盖率 91' }, { label: '异常环境', value: '3', delta: '待修复', note: '指纹漂移与代理丢失', color: 'var(--status-warning)', search: '异常 环境 3 指纹 代理' }], items: [{ title: '内容设备池 A', desc: '负载平稳，适合继续承接高频任务。', badge: '稳定', tone: 'success', search: '内容 设备池 稳定' }, { title: '英国短视频池', desc: '存在 1 台代理丢失设备，建议切换备用。', badge: '告警', tone: 'warning', search: '英国 短视频 代理 丢失' }, { title: '德国店铺池', desc: '2 台指纹漂移，需要重新生成环境。', badge: '修复', tone: 'error', search: '德国 指纹 漂移 修复' }], detailDesc: '让设备环境和账号风险在一个视图里闭环。', detailItems: ['64 台设备中 61 台可用', '3 台需修复', '先重建德国设备环境'], sidebarSummary: { eyebrow: '环境提醒', title: '3 台异常设备待处理', copy: '先处理代理丢失和指纹漂移，再恢复大批量登录任务。' }, statusLeft: ['设备可用率 95.3%', '异常 3', '最近巡检 12:18'], statusRight: [{ text: '环境正常', tone: 'success' }, { text: '告警 3', tone: 'warning' }] }),
        'asset-center': makeAssetCenterRoute(),
        'video-editor': makeContentWorkbenchRoute({
            breadcrumb: 'creator',
            eyebrow: '视频剪辑工作台',
            headerEyebrow: '序列编辑与导出检查',
            title: '视频剪辑',
            description: '围绕当前剪辑序列进行预览、精剪、字幕校对和导出检查，主内容区按剪辑器结构重做。',
            primaryAction: '发起终版导出',
            secondaryAction: '切换剪辑序列',
            workbenchType: 'video-editor',
            inlineSummary: true,
            hideWorkbenchSidebar: true,
            hideDetailPanel: true,
            summaryChips: [
                { label: '当前序列', value: '混剪序列 #18', note: '主版本正在精修转场与结尾 CTA', search: '当前 序列 混剪 18' },
                { label: '未解决阻塞', value: '1 个授权素材', note: '节日 B-roll 未补齐前不能锁定终版', search: '阻塞项 授权 素材' },
                { label: '导出队列', value: '7 个排队', note: '建议完成校对后集中发起多版本导出', search: '导出 状态 7 个 排队' },
            ],
            railTools: [
                { icon: '剪辑', label: '剪辑', search: '视频剪辑 剪辑' },
                { icon: '字幕', label: '字幕', search: '视频剪辑 字幕' },
                { icon: '音频', label: '音频', search: '视频剪辑 音频' },
                { icon: '导出', label: '导出', search: '视频剪辑 导出' },
            ],
            sideCards: [
                { title: '当前片段', desc: '主序列已完成粗剪，正在补两处转场并收紧结尾 CTA 时长。', badge: '精剪中', tone: 'success', search: '当前 片段 精剪中' },
                { title: '素材检查', desc: '节日 B-roll 仍待授权，授权后自动回填到 V2 补镜轨道。', badge: '待授权', tone: 'warning', search: '素材 检查 节日 B-roll 待授权' },
                { title: '字幕检查', desc: '两条口播字幕超出安全字数，需要压缩到 22 字以内。', badge: '待校对', tone: 'info', search: '字幕 检查 待校对' },
            ],
            bottomCards: [
                { title: '导出批次 A', desc: '主版本、15 秒短版和字幕版准备合并导出。', badge: '待导出', tone: 'warning', search: '导出 批次 A' },
                { title: '字幕校对', desc: '两条核心口播字幕需要人工收短并校正断句。', badge: '校对', tone: 'info', search: '字幕 校对 2 条' },
                { title: '授权补齐', desc: '节日素材授权完成后回填至 V2 轨道再锁定终版。', badge: '待授权', tone: 'success', search: '授权 补齐 主时间轴' },
            ],
            detailCards: [
                { title: '先处理字幕校对', desc: '两条口播超出安全字数，先压缩再锁轴。', badge: '优先', tone: 'warning', search: '先处理 字幕 校对' },
                { title: '跟进素材授权', desc: '节日 B-roll 是终版缺口，需先补授权链路。', badge: '阻塞', tone: 'error', search: '跟进 素材 授权' },
                { title: '合并导出窗口', desc: '校对完成后集中发起多版本导出，避免队列碎片化。', badge: '动作', tone: 'info', search: '合并 导出 窗口' },
            ],
            detailDesc: '优先处理导出阻塞、字幕校对和素材授权三类问题。',
            detailGroups: [
                { label: '当前批次', value: '视频混剪 #18' },
                { label: '重点风险', value: '促销素材授权未完成，可能阻塞最终导出' },
                { label: '建议动作', value: '先完成字幕校对，再集中发起多版本导出' },
            ],
            sidebarSummary: { eyebrow: '剪辑提醒', title: '当前序列仍有 2 个未闭环问题', copy: '先补字幕校对和素材授权，再锁定终版并发起多版本导出。' },
            statusLeft: ['当前序列 #18', '待导出 7', '未闭环问题 2'],
            statusRight: [{ text: '序列编辑中', tone: 'success' }, { text: '终版未锁定', tone: 'warning' }],
        }),
        'traffic-board': makeTrafficBoardRoute(),
        'profit-analysis': makeProfitAnalysisRoute(),
        'auto-reply': makeTaskOpsRoute({
            eyebrow: '自动回复工作台', breadcrumb: 'automation', headerEyebrow: '自动化客服控制台', title: '自动回复', description: '管理规则命中、风险词、人工接管阈值和灰度发布状态，让自动回复更稳地服务业务。', secondaryAction: '查看风险词', primaryAction: '新增回复规则', listTitle: '命中率摘要', listDesc: '先关注命中率低和风险高的规则。', sideTitle: '规则建议', sideDesc: '降低误答和投诉风险。', sideStats: ['活跃规则 48 条', '高风险词 6 个', '先灰度新模板'], metrics: [{ label: '规则总数', value: '48', delta: '+5', note: '本周新增 5 条', color: 'var(--status-success)', search: '规则 总数 48' }, { label: '命中率', value: '74%', delta: '+6%', note: '高频咨询处理更稳定', color: 'var(--brand-primary)', search: '命中率 74' }, { label: '风险词', value: '6', delta: '待复核', note: '建议人工审查', color: 'var(--status-warning)', search: '风险词 6' }], items: [{ title: '优惠券咨询模板', desc: '命中率高，适合继续放量。', badge: '高命中', tone: 'success', search: '优惠券 咨询 命中率高' }, { title: '赔付承诺模板', desc: '涉及售后承诺，需灰度验证。', badge: '灰度', tone: 'warning', search: '赔付 承诺 模板 灰度' }, { title: '多语言问候模板', desc: '覆盖日本和德国站，待人工润色。', badge: '润色', tone: 'info', search: '多语言 问候 日本 德国' }], table: { title: '规则灰度发布表', description: '把新旧规则、灰度范围和风险等级一起展示。', columns: ['规则', '灰度范围', '风险等级', '状态'], rows: [{ search: '赔付承诺模板 德国站 高 灰度中', cells: ['<strong>赔付承诺模板</strong>', '德国站 20%', '<span class="tag warning">高</span>', '<span class="status-chip warning">灰度中</span>'] }, { search: '优惠券咨询模板 全站 低 全量', cells: ['<strong>优惠券咨询模板</strong>', '全站', '<span class="tag success">低</span>', '<span class="status-chip success">全量</span>'] }, { search: '多语言问候模板 日本德国 中 待润色', cells: ['<strong>多语言问候模板</strong>', '日本 / 德国', '<span class="tag info">中</span>', '<span class="status-chip info">待润色</span>'] }] }, detailDesc: '自动回复页需要优先保护高风险场景。', detailItems: ['48 条规则在线', '6 个风险词待复核', '先灰度赔付承诺模板'], sidebarSummary: { eyebrow: '规则提醒', title: '6 个风险词待复核', copy: '建议先人工审查赔付、退款、物流超时相关回复，再扩大自动化范围。' }, statusLeft: ['规则 48', '风险词 6', '命中率 74%'], statusRight: [{ text: '自动回复稳定', tone: 'success' }, { text: '风险词 6', tone: 'warning' }] }),
        'scheduled-publish': makeTaskOpsRoute({
            eyebrow: '发布编排中心', breadcrumb: 'automation', headerEyebrow: '内容排程页', title: '定时发布', description: '统一管理发布计划、草稿、审核状态和异常中断，让排程更可控。', secondaryAction: '查看发布日历', primaryAction: '新建发布计划', listTitle: '待发布计划', listDesc: '先处理高风险和高价值计划。', sideTitle: '排程建议', sideDesc: '避免在异常环境下继续推送内容。', sideStats: ['今日计划 18 条', '待审核 8 条', '高风险计划 2 条'], metrics: [{ label: '今日计划', value: '18', delta: '+4', note: '下午场计划密集', color: 'var(--status-success)', search: '今日 计划 18' }, { label: '待审核', value: '8', delta: '需确认', note: '防止异常内容上线', color: 'var(--status-warning)', search: '待审核 8' }, { label: '中断计划', value: '2', delta: '需恢复', note: '受环境和代理影响', color: 'var(--status-error)', search: '中断 计划 2' }], items: [{ title: '美国新品预热', desc: '素材齐全，待审核通过后即可发布。', badge: '待审', tone: 'warning', search: '美国 新品 预热 待审核' }, { title: '日本私域促活', desc: '账号异常修复前不建议继续执行。', badge: '中断', tone: 'error', search: '日本 私域 促活 中断' }, { title: '英国短视频上新', desc: '可按计划发布，无需人工介入。', badge: '正常', tone: 'success', search: '英国 短视频 上新 正常' }], detailDesc: '排程页要先处理审核和环境异常。', detailItems: ['今日计划 18 条', '8 条待审核', '先恢复异常账号再发布'], sidebarSummary: { eyebrow: '排程提醒', title: '8 条计划待审核', copy: '建议先复核高风险计划，再修复日本私域账号异常。' }, statusLeft: ['计划 18', '待审核 8', '中断 2'], statusRight: [{ text: '大部分正常', tone: 'success' }, { text: '中断 2', tone: 'error' }] }),
        'visual-lab': makeVisualLabRoute(),
        'competitor-monitor': makeCompetitorMonitorRoute(),
        'blue-ocean': makeBlueOceanRoute(),
        'report-center': makeReportCenterRoute(),
        'interaction-analysis': makeInteractionAnalysisRoute(),
        'ecommerce-conversion': makeEcommerceConversionRoute(),
        'fan-profile': makeFanProfileRoute(),
        'task-hall': makeTaskOpsRoute({ breadcrumb: 'automation', eyebrow: '自动化任务大厅', headerEyebrow: '多任务编排总览', title: '任务大厅', description: '把采集、互动、发布和回放任务统一成一张调度看板，让自动化运营先看阻塞再决定动作。', primaryAction: '创建新任务', secondaryAction: '筛选高风险', kanban: [{ title: '待执行', items: [{ title: '晚高峰互动补量', desc: '18:00 自动进入执行窗口。', search: '晚高峰 互动 补量' }] }, { title: '运行中', items: [{ title: '内容评论分流', desc: '当前已处理 68%。', search: '内容 评论 分流' }] }, { title: '异常', items: [{ title: '达人池采集补偿', desc: '代理波动导致 2 个节点重试。', search: '达人池 采集 异常' }] }] }),
        'data-collector': makeTaskOpsRoute({ breadcrumb: 'automation', eyebrow: '采集工作流中心', headerEyebrow: '采集源与节点编排', title: '数据采集助手', description: '统一管理采集任务、数据源、代理池和补偿链路，不再只是一个简单任务列表。', primaryAction: '新建采集方案', secondaryAction: '查看代理池' }),
        'auto-like': makeTaskOpsRoute({ breadcrumb: 'automation', eyebrow: '互动增量控制台', headerEyebrow: '自动点赞编排', title: '自动点赞', description: '按账号池、时间窗和互动目标配置点赞任务，降低人工重复操作。', primaryAction: '创建点赞规则', secondaryAction: '查看白名单' }),
        'auto-comment': makeTaskOpsRoute({ breadcrumb: 'automation', eyebrow: '评论自动化控制台', headerEyebrow: '评论规则与风险控制', title: '自动评论', description: '统一管理评论模板、敏感词和账号节流规则，避免评论动作失控。', primaryAction: '新建评论规则', secondaryAction: '查看敏感词' }),
        'auto-message': makeTaskOpsRoute({ breadcrumb: 'automation', eyebrow: '私信触达控制台', headerEyebrow: '自动私信与节奏控制', title: '自动私信', description: '把私信触达、分层策略和频率限制集中展示，便于统一审计和调优。', primaryAction: '创建私信计划', secondaryAction: '查看发送限制' }),
        'viral-title': makeViralTitleRoute(),
        'script-extractor': makeScriptExtractorRoute(),
        'product-title': makeProductTitleRoute(),
        'creative-workshop': makeContentWorkbenchRoute({
            breadcrumb: 'creator',
            eyebrow: '创意组合实验区',
            headerEyebrow: '话题、镜头、文案联动',
            title: '创意工坊',
            description: '围绕主题、镜头、口播和素材组合做创意试验，主内容区改成方案拼版与版本对比工作台。',
            primaryAction: '保存创意方案',
            secondaryAction: '对比创意版本',
            workbenchType: 'creative-workshop',
            summaryChips: [
                { label: '当前实验', value: '达人实测 vs 低价钩子', note: '正在比对开场 3 秒信息密度与停留表现', search: '当前 实验 达人实测 低价 钩子' },
                { label: '待决策', value: '2 组冲突方案', note: '镜头强度与口播长度尚未收敛', search: '待决策 2 组 冲突 方案' },
                { label: '保留倾向', value: '达人实测领先', note: '短口播版本更适合进入下游生产', search: '保留 倾向 达人 实测 领先' },
            ],
            railTools: [
                { icon: '主题', label: '主题', search: '创意工坊 主题' },
                { icon: '镜头', label: '镜头', search: '创意工坊 镜头' },
                { icon: '口播', label: '口播', search: '创意工坊 口播' },
                { icon: '导出', label: '导出', search: '创意工坊 导出' },
            ],
            focusCards: [
                { title: '方案 A: 达人实测', desc: '开场先给真人反馈，再补产品局部和价格理由，强调真实信任感。', badge: 'A 方案', tone: 'success', size: 'wide', meta: '强项: 停留更稳；风险: 成本较高', search: '方案 A 达人 实测' },
                { title: '方案 B: 低价钩子', desc: '先给价格刺激与优惠倒计时，再补使用前后对比，强调快速点击。', badge: 'B 方案', tone: 'warning', meta: '强项: 点击更高；风险: 主题略分散', search: '方案 B 低价 钩子' },
                { title: '镜头组合', desc: '开场 3 秒对比镜头表现更好，中段建议插入使用场景而非空镜。', badge: '镜头', tone: 'info', meta: '保留快切，不建议超过 5 个镜头节点', search: '镜头 组合 对比' },
                { title: '口播变量', desc: '短口播版本更利于保留钩子，但需避免连续重复敏感词。', badge: '口播', tone: 'success', meta: '建议控制在 22 字以内，尾句保留 CTA', search: '口播 变量 22 字' },
            ],
            sideCards: [
                { title: '方案 A 判定', desc: '转化潜力高，建议作为基线方案继续压缩口播长度。', badge: '优先保留', tone: 'success', search: '方案 A 判定 优先保留' },
                { title: '方案 B 判定', desc: '点击刺激更强，但主题标签仍偏散，需要收束一条主线。', badge: '待收束', tone: 'warning', search: '方案 B 判定 待收束' },
                { title: '下一步', desc: '锁定胜出主题后，交给视频剪辑页生成 15 秒与 30 秒双版本。', badge: '移交生产', tone: 'info', search: '创意 下一步 移交 生产' },
            ],
            bottomCards: [
                { title: '昨日保留版', desc: '达人实测路线表现最好，建议作为基线版本。', badge: '保留', tone: 'success', search: '昨日 保留版 达人 实测' },
                { title: '待试验版', desc: '价格钩子更强，但镜头逻辑仍需精简。', badge: '待试', tone: 'warning', search: '待试验版 价格 钩子' },
                { title: '复盘记录', desc: '上周失败组合集中在口播过长和封面信息过载。', badge: '复盘', tone: 'info', search: '复盘 记录 口播 封面' },
            ],
            detailCards: [
                { title: '先裁短口播', desc: '把胜出方案控制在 22 字以内，确保开场节奏不塌。', badge: '优先', tone: 'warning', search: '先裁短 口播' },
                { title: '收束主题标签', desc: '低价钩子方案需减少并列卖点，避免信息分叉。', badge: '风险', tone: 'error', search: '收束 主题 标签' },
                { title: '输出双版本', desc: '确认胜出后同步下发 15 秒与 30 秒两套镜头脚本。', badge: '动作', tone: 'info', search: '输出 双版本 镜头 脚本' },
            ],
            detailDesc: '优先确认当前保留方案、主要冲突点和下一轮对比目标。',
            detailGroups: [
                { label: '当前保留方案', value: '达人实测 + 低价钩子' },
                { label: '重点风险', value: '口播过长会压缩开场节奏' },
                { label: '建议动作', value: '先产出 15 秒短版，再进入视频剪辑页批量对比' },
            ],
            sidebarSummary: { eyebrow: '创意提醒', title: '5 个方案待复核', copy: '建议先筛掉主题分散的组合，再保留高分创意进入生产链路。' },
            statusLeft: ['方案 18', '待复核 5', '最近评审 13:02'],
            statusRight: [{ text: '高分方案 3', tone: 'success' }, { text: '待试验 2', tone: 'warning' }],
        }),
        'ai-content-factory': makeAIContentFactoryRoute(),
        'ai-copywriter': makeAICopywriterRoute(),
        'setup-wizard': makeConfigCenterRoute({
            breadcrumb: 'system',
            eyebrow: '首次配置向导',
            headerEyebrow: '环境初始化引导',
            title: '初始化向导',
            description: '首次启动时完成供应商接入、模型选择和角色偏好设置，确保系统可正常运行。',
            primaryAction: '下一步',
            secondaryAction: '跳过并稍后设置',
            configType: 'wizard',
            navSections: [
                { label: '欢迎', icon: '👋', search: '欢迎 向导 开始' },
                { label: '许可证激活', icon: '🔑', search: '许可证 激活 一机一码' },
                { label: '供应商接入', icon: '🔌', search: '供应商 接入 API' },
                { label: '模型选择', icon: '🤖', search: '模型 选择 默认' },
                { label: '使用偏好', icon: '🎯', search: '偏好 市场 工作流' },
            ],
            wizardSteps: [
                {
                    title: '欢迎使用 TK-OPS',
                    desc: '只需几步即可完成环境初始化，开始高效运营。本软件为单机授权，一机一码绑定使用。',
                    search: '欢迎 初始化',
                    fields: [
                        { label: '机器码', value: 'MID-XXXX-XXXX-XXXX', hint: '自动生成，用于许可证绑定', search: '机器码 绑定' },
                    ],
                },
                {
                    title: '许可证激活',
                    desc: '输入购买时获得的许可证密钥，完成本机激活。每个许可证仅可绑定一台设备。',
                    search: '许可证 激活 绑定',
                    fields: [
                        { label: '许可证密钥', value: '', hint: '格式：TKOPS-XXXX-XXXX-XXXX-XXXX', search: '许可证 密钥' },
                        { label: '主要市场', type: 'select', value: '美国（US）', hint: '决定默认时区、货币和语言', search: '主要 市场' },
                    ],
                },
                {
                    title: '供应商接入',
                    desc: '配置至少一个 AI 供应商，系统才能启用标题、脚本和文案生成。',
                    search: '供应商 接入 配置',
                    fields: [
                        { label: '供应商', type: 'select', value: 'OpenAI', search: '供应商 选择' },
                        { label: 'API Key', value: 'sk-•••••••••••••', hint: '密钥加密存储，仅本机可用', search: 'API key 密钥' },
                    ],
                },
                {
                    title: '默认模型',
                    desc: '选择标题、脚本和内容生成使用的默认模型。',
                    search: '默认 模型 选择',
                    fields: [
                        { label: '默认模型', type: 'select', value: 'gpt-4.1-mini', search: '默认 模型' },
                    ],
                },
                {
                    title: '使用偏好',
                    desc: '选择您最常用的工作流方向，系统会优化导航和默认页面。',
                    search: '使用 偏好',
                    fields: [
                        { label: '常用工作流', type: 'select', value: '内容创作', search: '工作流 选择' },
                    ],
                },
            ],
            notices: [{ title: '首次配置建议', desc: '建议按顺序完成所有步骤。跳过的步骤可以稍后在系统设置中补充。', tone: 'info' }],
            detailTitle: '向导说明',
            detailDesc: '当前步骤的操作提示和注意事项',
            detailGroups: [
                { label: '当前步骤', value: '1 / 5 — 欢迎' },
                { label: '预计时间', value: '约 3 分钟' },
                { label: '授权模式', value: '一机一码，单机授权' },
            ],
            detailCards: [
                { title: '许可证绑定后不可转移', desc: '每个许可证仅可绑定一台设备，请确认后激活。', badge: '注意', tone: 'warning', search: '许可证 绑定 注意' },
                { title: '先完成供应商接入', desc: 'AI 功能依赖至少一个有效供应商。', badge: '必要', tone: 'warning', search: '供应商 必要' },
                { title: '市场选择影响默认配置', desc: '时区、货币和推荐模板会随市场变化。', badge: '提示', tone: 'info', search: '市场 影响' },
            ],
            sidebarSummary: { eyebrow: '向导进度', title: '步骤 1/5：欢迎', copy: '完成许可证激活后进入供应商接入步骤。' },
            statusLeft: ['步骤 1/5', '预计 3 分钟', '一机一码'],
            statusRight: [{ text: '向导进行中', tone: 'warning' }],
        }),
        'task-scheduler': makeTaskOpsRoute({ breadcrumb: 'automation', eyebrow: '计划任务调度中心', headerEyebrow: '时间窗与重复规则', title: '任务调度', description: '围绕时间窗、执行节点、补偿规则和依赖关系做调度管理，布局应更像排程台。', primaryAction: '新建调度计划', secondaryAction: '查看周历', calendarDays: [{ title: '周一', subtle: '03.10', slots: [{ title: '评论分流 09:30', search: '周一 评论分流' }] }, { title: '周二', subtle: '03.11', slots: [{ title: '内容生产 11:00', search: '周二 内容生产' }] }, { title: '周三', subtle: '03.12', slots: [{ title: '达人采集 18:00', search: '周三 达人采集' }] }, { title: '周四', subtle: '03.13', slots: [{ title: '自动私信 14:00', search: '周四 自动私信' }] }, { title: '周五', subtle: '03.14', slots: [{ title: '晚高峰点赞 19:00', search: '周五 点赞' }] }, { title: '周六', subtle: '03.15', slots: [{ title: '周报生成 10:00', search: '周六 周报生成' }] }, { title: '周日', subtle: '03.16', slots: [{ title: '备份巡检 22:00', search: '周日 备份巡检' }] }] }),
        'downloader': makeToolConsoleRoute({ breadcrumb: 'system', eyebrow: '下载链路控制台', headerEyebrow: '资源下载与队列管理', title: '下载器', description: '集中处理下载任务、代理链路、缓存目录和失败重试，便于快速定位下载侧异常。', primaryAction: '新建下载任务', secondaryAction: '查看失败记录' }),
        'lan-transfer': makeToolConsoleRoute({ breadcrumb: 'system', eyebrow: '局域网传输中枢', headerEyebrow: '本地设备与传输队列', title: '局域网传输', description: '把同网设备发现、文件传输、进度和连接状态聚合成一个局域网传输中心。', primaryAction: '选择文件发送', secondaryAction: '刷新设备列表' }),
        'network-diagnostics': makeToolConsoleRoute({ breadcrumb: 'system', eyebrow: '网络健康中心', headerEyebrow: '链路测试与诊断输出', title: '网络诊断', description: '统一查看代理、下载、DNS、接口与延迟测试结果，便于值班时快速定位网络异常。', primaryAction: '运行全部测试', secondaryAction: '导出诊断日志' }),
        'system-settings': makeConfigCenterRoute({
            breadcrumb: 'system',
            eyebrow: '系统参数中台',
            headerEyebrow: '主题、网络、通知统一配置',
            title: '系统设置',
            description: '集中管理应用主题、网络代理、通知策略、数据存储和高级运行参数。',
            primaryAction: '保存设置',
            secondaryAction: '恢复推荐配置',
            configType: 'settings',
            navSections: [
                { label: '通用', icon: '⚙', badge: '', search: '通用 设置 语言 时区' },
                { label: '外观', icon: '🎨', search: '外观 主题 字号 配色' },
                { label: '网络', icon: '🌐', badge: '1', badgeTone: 'warning', search: '网络 代理 超时' },
                { label: '通知', icon: '🔔', search: '通知 告警 静默' },
                { label: '存储', icon: '💾', search: '存储 缓存 路径' },
                { label: '高级', icon: '🔧', search: '高级 实验 调试' },
            ],
            notices: [{ title: '网络代理配置有变更未保存', desc: '当前代理地址已修改但尚未生效。保存后所有网络请求将走新路由。', tone: 'warning' }],
            formGroups: [
                {
                    title: '基础设置',
                    desc: '语言、时区和默认市场',
                    fields: [
                        { label: '界面语言', type: 'select', value: '简体中文', hint: '重启后生效', search: '界面 语言 中文' },
                        { label: '时区', type: 'select', value: 'UTC+8 (亚洲/上海)', search: '时区 UTC' },
                        { label: '默认货币', type: 'select', value: 'USD ($)', search: '货币 USD' },
                        { label: '启动时自动检查更新', type: 'toggle', value: '开', search: '自动 检查 更新' },
                    ],
                },
                {
                    title: '外观与主题',
                    desc: '配色方案、字号和紧凑模式',
                    fields: [
                        { label: '主题', type: 'select', value: '跟随系统', hint: '可选：浅色 / 深色 / 跟随系统', search: '主题 浅色 深色' },
                        { label: '字号', type: 'select', value: '标准 (14px)', search: '字号 大小' },
                        { label: '紧凑模式', type: 'toggle', value: '关', hint: '开启后减少间距，适合小屏', search: '紧凑 模式' },
                    ],
                },
                {
                    title: '网络设置',
                    desc: '代理、超时和并发限制',
                    fields: [
                        { label: '代理地址', value: 'http://127.0.0.1:7890', hint: '留空则直连', search: '代理 地址 proxy' },
                        { label: '请求超时', type: 'select', value: '30 秒', search: '请求 超时' },
                        { label: '最大并发', type: 'select', value: '5', hint: '同时进行的网络任务数上限', search: '最大 并发' },
                    ],
                },
                {
                    title: '通知策略',
                    desc: '任务完成、异常告警和静默时段',
                    fields: [
                        { label: '任务完成通知', type: 'toggle', value: '开', search: '任务 完成 通知' },
                        { label: '异常告警', type: 'toggle', value: '开', search: '异常 告警' },
                        { label: '静默时段', type: 'select', value: '22:00 - 08:00', hint: '此时段内不弹出通知', search: '静默 时段' },
                    ],
                },
            ],
            detailTitle: '配置说明',
            detailDesc: '当前选中配置项的解释和风险提示',
            detailGroups: [
                { label: '当前分区', value: '通用设置' },
                { label: '未保存变更', value: '1 项 (网络代理)' },
                { label: '上次保存', value: '今天 10:32' },
            ],
            detailCards: [
                { title: '代理变更需谨慎', desc: '错误的代理地址会导致所有网络请求失败，建议先测试。', badge: '注意', tone: 'warning', search: '代理 变更 注意' },
                { title: '主题切换立即生效', desc: '不需要重启应用，切换后所有页面自动刷新样式。', badge: '提示', tone: 'info', search: '主题 切换 提示' },
            ],
            sidebarSummary: { eyebrow: '设置状态', title: '1 项未保存变更', copy: '网络代理地址已修改，保存后生效。其余配置均为最新状态。' },
            statusLeft: ['语言 中文', '主题 跟随系统', '代理 127.0.0.1:7890'],
            statusRight: [{ text: '配置正常', tone: 'success' }, { text: '1 项未保存', tone: 'warning' }],
        }),
        'log-center': makeToolConsoleRoute({ breadcrumb: 'system', eyebrow: '日志观测中心', headerEyebrow: '运行日志与告警追踪', title: '日志中心', description: '统一查看系统日志、异常级别、模块分布和导出记录，便于问题排查。', primaryAction: '导出日志', secondaryAction: '刷新实时流' }),
        // version-upgrade: 使用 routes.js 中的自定义路由
    };

    let currentTheme = 'light';
    let currentRoute = 'dashboard';

    function loadRecentRoutes() {
        try {
            const parsed = JSON.parse(window.localStorage.getItem(RECENT_ROUTES_KEY) || '[]');
            uiState.recentRoutes = Array.isArray(parsed) ? parsed.filter((key) => routes[key]) : [];
        } catch {
            uiState.recentRoutes = [];
        }
    }

    function saveRecentRoutes() {
        try {
            window.localStorage.setItem(RECENT_ROUTES_KEY, JSON.stringify(uiState.recentRoutes.slice(0, 6)));
        } catch {
            // ignore storage failures in embedded mode
        }
    }

    function pushRecentRoute(routeKey) {
        uiState.recentRoutes = [routeKey, ...uiState.recentRoutes.filter((key) => key !== routeKey)].slice(0, 6);
        saveRecentRoutes();
        renderRecentRoutes();
    }

    function setTemplateContent(hostId, templateId) {
        const host = document.getElementById(hostId);
        const template = document.getElementById(templateId);
        host.innerHTML = template ? template.innerHTML : '';
    }

    function setHostHtml(hostId, html) {
        document.getElementById(hostId).innerHTML = html || '';
    }

    function renderSidebarSummary(summary) {
        document.getElementById('sidebarSummary').innerHTML = `
            <div class="eyebrow">${summary.eyebrow}</div>
            <strong>${summary.title}</strong>
            <p class="sidebar__footer-copy">${summary.copy}</p>
        `;
    }

    function renderStatus(route) {
        document.getElementById('statusLeft').innerHTML = route.statusLeft.map((text) => `<span class="status-text">${text}</span>`).join('');
        document.getElementById('statusRight').innerHTML = route.statusRight.map((item) => `<span class="status-chip ${item.tone}">${item.text}</span>`).join('');
    }

    function applyTheme(name) {
        currentTheme = name;
        document.body.setAttribute('data-theme', name === 'dark' ? 'dark' : 'light');
        document.getElementById('themeToggle').textContent = name === 'dark' ? '切换到浅色' : '切换到深色';
    }

    function updateDetail(templateId, sourceElement) {
        const detailTemplate = document.getElementById(`detail-${templateId}`);
        if (detailTemplate) {
            setTemplateContent('detailHost', `detail-${templateId}`);
        }
        document.getElementById('mainHost').querySelectorAll('.route-row, .detail-trigger, .account-card').forEach((element) => {
            element.classList.remove('is-selected');
        });
        if (sourceElement) {
            sourceElement.classList.add('is-selected');
        }
    }

    function ensureEmptyState(container, visibleCount, message) {
        let empty = container.parentElement.querySelector('.empty-state');
        if (!visibleCount) {
            if (!empty) {
                empty = document.createElement('div');
                empty.className = 'empty-state';
                container.parentElement.appendChild(empty);
            }
            empty.textContent = message;
        } else if (empty) {
            empty.remove();
        }
    }

    function matchSearch(element, keyword) {
        if (!keyword) {
            return true;
        }
        return (element.dataset.search || element.textContent || '').toLowerCase().includes(keyword);
    }

    function highlightMatches(elements, keyword) {
        elements.forEach((element) => {
            const visible = !element.classList.contains('is-filtered-out');
            const matched = keyword && matchSearch(element, keyword);
            element.classList.toggle('search-hit', Boolean(keyword && matched && visible));
        });
    }

    function applyNavSearch(keyword) {
        const navButtons = [...document.querySelectorAll('.nav-link[data-route]')];
        navButtons.forEach((button) => {
            const matched = !keyword || button.textContent.toLowerCase().includes(keyword) || (routes[button.dataset.route]?.searchTerms || '').toLowerCase().includes(keyword);
            button.classList.toggle('is-filtered-out', !matched);
        });
        highlightMatches(navButtons, keyword);
        return navButtons.filter((button) => !button.classList.contains('is-filtered-out'));
    }

    function applyDashboardState(keyword) {
        const items = [...document.getElementById('mainHost').querySelectorAll('[data-search]')];
        items.forEach((item) => item.classList.toggle('is-filtered-out', !matchSearch(item, keyword)));
        highlightMatches(items, keyword);
    }

    function applyAccountState(keyword) {
        const state = uiState.account;
        const collection = document.querySelector('[data-collection="accounts"]');
        if (!collection) {
            return;
        }

        collection.classList.toggle('list-mode', state.view === 'list');
        if (state.sortMode === 'anomaly') {
            [...collection.children]
                .sort((left, right) => Number(left.dataset.order || 999) - Number(right.dataset.order || 999))
                .forEach((item) => collection.appendChild(item));
        }

        const cards = [...collection.querySelectorAll('.account-card')];
        let visibleCount = 0;
        let selectedVisible = false;
        cards.forEach((card) => {
            const statusMatched = state.statusFilter === 'all' || card.dataset.status === state.statusFilter;
            const searchMatched = matchSearch(card, keyword);
            const visible = statusMatched && searchMatched;
            card.classList.toggle('is-filtered-out', !visible);
            if (visible && card.classList.contains('is-selected')) {
                selectedVisible = true;
            }
            if (visible) {
                visibleCount += 1;
            }
        });
        if (!selectedVisible) {
            const firstVisible = cards.find((card) => !card.classList.contains('is-filtered-out'));
            if (firstVisible) {
                updateDetail(firstVisible.dataset.detailTarget, firstVisible);
            }
        }
        highlightMatches(cards, keyword);
        ensureEmptyState(collection, visibleCount, '没有匹配的账号，请调整筛选条件或搜索关键词。');
    }

    function applyTaskState(keyword) {
        const state = uiState['task-queue'];
        const collection = document.querySelector('[data-collection="tasks"]');
        if (!collection) {
            return;
        }

        const rows = [...collection.querySelectorAll('.route-row')];
        let visibleCount = 0;
        rows.forEach((row) => {
            const statusMatched = state.statusFilter === 'all' || row.dataset.status === state.statusFilter;
            const searchMatched = matchSearch(row, keyword);
            const visible = statusMatched && searchMatched;
            row.classList.toggle('is-filtered-out', !visible);
            if (visible) {
                visibleCount += 1;
            }
        });
        highlightMatches(rows, keyword);
        ensureEmptyState(collection, visibleCount, '没有匹配的任务，请调整筛选条件或搜索关键词。');
    }

    function applyProviderState(keyword) {
        const rows = [...document.getElementById('mainHost').querySelectorAll('.route-row')];
        rows.forEach((row) => row.classList.toggle('is-filtered-out', !matchSearch(row, keyword)));
        highlightMatches(rows, keyword);
    }

    function applyGenericState(keyword) {
        const items = [...document.getElementById('mainHost').querySelectorAll('[data-search]')];
        items.forEach((element) => element.classList.toggle('is-filtered-out', !matchSearch(element, keyword)));
        highlightMatches(items, keyword);
    }

    function applyCurrentRouteState() {
        const keyword = uiState.globalSearch.trim().toLowerCase();
        applyNavSearch(keyword);

        if (currentRoute === 'account') {
            applyAccountState(keyword);
        } else if (currentRoute === 'task-queue') {
            applyTaskState(keyword);
        }
    }

    function renderRecentRoutes() {
        const host = document.getElementById('recentRoutes');
        if (!uiState.recentRoutes.length) {
            host.innerHTML = '<button class="search-result-item" type="button" disabled><strong>暂无最近访问</strong><span class="subtle">打开页面后会在这里记录。</span></button>';
            return;
        }

        host.innerHTML = uiState.recentRoutes
            .map((routeKey) => {
                const navButton = document.querySelector(`.nav-link[data-route="${routeKey}"]`);
                const title = navButton ? navButton.textContent.trim() : routeKey;
                const route = routes[routeKey];
                return `<button class="search-result-item" data-search-route="${routeKey}" type="button"><strong>${title}</strong><span class="subtle">${route.eyebrow}</span></button>`;
            })
            .join('');
    }

    function collectSearchResults(keyword) {
        const normalized = keyword.trim().toLowerCase();
        const results = [];
        const navButtons = [...document.querySelectorAll('.nav-link[data-route]')];
        navButtons.forEach((button) => {
            const routeKey = button.dataset.route;
            const route = routes[routeKey];
            const haystack = `${button.textContent} ${(route.searchTerms || '')}`.toLowerCase();
            if (!normalized || haystack.includes(normalized)) {
                results.push({ type: 'route', routeKey, title: button.textContent.trim(), subtitle: route.eyebrow });
            }
        });

        const pageHits = [...document.getElementById('mainHost').querySelectorAll('[data-search]')]
            .filter((element) => matchSearch(element, normalized))
            .slice(0, 4)
            .map((element) => ({
                type: 'detail',
                routeKey: currentRoute,
                title: element.querySelector('strong')?.textContent || element.textContent.trim().slice(0, 24),
                subtitle: '当前页面命中',
                detailTarget: element.dataset.detailTarget || '',
            }));

        return [...results.slice(0, 7), ...pageHits].slice(0, 8);
    }

    function highlightKeyword(text, keyword) {
        if (!keyword) {
            return text;
        }
        const escaped = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        return text.replace(new RegExp(escaped, 'ig'), (match) => `<span class="search-highlight-text">${match}</span>`);
    }

    function renderSearchPanel() {
        const panel = document.getElementById('searchPanel');
        const resultsHost = document.getElementById('searchResults');
        const keyword = uiState.globalSearch.trim().toLowerCase();
        uiState.searchPanel.results = collectSearchResults(keyword);
        uiState.searchPanel.activeIndex = Math.min(uiState.searchPanel.activeIndex, Math.max(uiState.searchPanel.results.length - 1, 0));

        if (!uiState.searchPanel.results.length) {
            resultsHost.innerHTML = '<button class="search-result-item" type="button" disabled><strong>未找到匹配项</strong><span class="subtle">可以尝试搜索页面名称、业务词或账号关键字。</span></button>';
        } else {
            resultsHost.innerHTML = uiState.searchPanel.results
                .map(
                    (result, index) => `
                        <button class="search-result-item ${index === uiState.searchPanel.activeIndex ? 'is-active' : ''}" data-search-route="${result.routeKey}" ${result.detailTarget ? `data-detail-target="${result.detailTarget}"` : ''} type="button">
                            <strong>${highlightKeyword(result.title, keyword)}</strong>
                            <span class="subtle">${highlightKeyword(result.subtitle, keyword)}</span>
                        </button>
                    `
                )
                .join('');
        }

        renderRecentRoutes();
        panel.classList.toggle('shell-hidden', !uiState.searchPanel.visible);

        panel.querySelectorAll('[data-search-route]').forEach((button) => {
            button.addEventListener('click', () => {
                const routeKey = button.dataset.searchRoute;
                const detailTarget = button.dataset.detailTarget;
                renderRoute(routeKey);
                uiState.searchPanel.visible = false;
                renderSearchPanel();
                if (detailTarget) {
                    const source = document.querySelector(`[data-detail-target="${detailTarget}"]`);
                    if (source) {
                        updateDetail(detailTarget, source);
                    }
                }
            });
        });
    }

    function handleSearchNavigation(event) {
        if (!uiState.searchPanel.visible || !uiState.searchPanel.results.length) {
            return false;
        }

        if (event.key === 'ArrowDown') {
            uiState.searchPanel.activeIndex = (uiState.searchPanel.activeIndex + 1) % uiState.searchPanel.results.length;
            renderSearchPanel();
            return true;
        }
        if (event.key === 'ArrowUp') {
            uiState.searchPanel.activeIndex = (uiState.searchPanel.activeIndex - 1 + uiState.searchPanel.results.length) % uiState.searchPanel.results.length;
            renderSearchPanel();
            return true;
        }
        if (event.key === 'Escape') {
            uiState.searchPanel.visible = false;
            renderSearchPanel();
            return true;
        }
        if (event.key === 'Enter') {
            const active = uiState.searchPanel.results[uiState.searchPanel.activeIndex];
            if (active) {
                renderRoute(active.routeKey);
                uiState.searchPanel.visible = false;
                renderSearchPanel();
                if (active.detailTarget) {
                    const source = document.querySelector(`[data-detail-target="${active.detailTarget}"]`);
                    if (source) {
                        updateDetail(active.detailTarget, source);
                    }
                }
            }
            return true;
        }
        return false;
    }

    function bindSearch() {
        const input = document.getElementById('globalSearch');
        input.addEventListener('focus', () => {
            uiState.searchPanel.visible = true;
            renderSearchPanel();
        });

        input.addEventListener('input', () => {
            uiState.globalSearch = input.value;
            uiState.searchPanel.visible = true;
            uiState.searchPanel.activeIndex = 0;
            applyCurrentRouteState();
            renderSearchPanel();
        });

        input.addEventListener('keydown', (event) => {
            if (handleSearchNavigation(event)) {
                event.preventDefault();
            }
        });

        document.addEventListener('click', (event) => {
            if (!event.target.closest('.shell-search-bar')) {
                uiState.searchPanel.visible = false;
                renderSearchPanel();
            }
        });
    }

    function bindSegmentedButtons() {
        document.querySelectorAll('.segmented').forEach((group) => {
            group.querySelectorAll('button').forEach((btn) => {
                btn.addEventListener('click', () => {
                    group.querySelectorAll('button').forEach((b) => b.classList.remove('is-active'));
                    btn.classList.add('is-active');
                });
            });
        });
    }

    function bindFilters() {
        document.querySelectorAll('.filter-row select, .filter-row input').forEach((el) => {
            el.addEventListener('change', () => applyCurrentRouteState());
        });
    }

    function bindDetailTriggers() {
        document.querySelectorAll('[data-detail-target]').forEach((trigger) => {
            trigger.addEventListener('click', () => {
                const targetId = trigger.dataset.detailTarget;
                const template = document.getElementById('detail-' + targetId);
                if (template) {
                    document.getElementById('detailHost').innerHTML = template.innerHTML;
                }
                document.querySelectorAll('[data-detail-target]').forEach((t) => t.classList.remove('is-selected'));
                trigger.classList.add('is-selected');
            });
        });
    }

    /* ─── 功能联动：提取元素内容生成右侧详情 ─── */
    function buildDynamicDetail(title, subtitle, details, actions) {
        const detailItems = details.map((d) => `<div class="detail-item"><span class="subtle">${d.label}</span><strong>${d.value}</strong></div>`).join('');
        const actionItems = actions.map((a) => `<article class="workbench-sidecard"><strong>${a.title}</strong><div class="subtle">${a.desc}</div></article>`).join('');
        return `
            <div class="detail-root">
                <section class="panel">
                    <div class="panel__header"><div><strong>${title}</strong><div class="subtle">${subtitle}</div></div></div>
                    <div class="detail-list">${detailItems}</div>
                </section>
                ${actionItems ? `<section class="panel"><div class="panel__header"><div><strong>相关操作</strong><div class="subtle">针对当前选中项的推荐动作。</div></div></div><div class="workbench-side-list">${actionItems}</div></section>` : ''}
            </div>
        `;
    }

    function extractTextFromEl(el, selector) {
        const target = el.querySelector(selector);
        return target ? target.textContent.trim() : '';
    }

    /* ─── 功能联动：点击主区条目→更新右侧面板 ─── */
    function bindMainItemClicks() {
        const mainHost = document.getElementById('mainHost');
        const detailHost = document.getElementById('detailHost');
        const route = routes[currentRoute];
        if (!route || route.hideDetailPanel === true) return;

        // 看板卡片点击
        mainHost.querySelectorAll('.board-card').forEach((card) => {
            card.style.cursor = 'pointer';
            card.addEventListener('click', () => {
                mainHost.querySelectorAll('.board-card').forEach((c) => c.classList.remove('is-selected'));
                card.classList.add('is-selected');
                const title = extractTextFromEl(card, 'strong') || '任务详情';
                const desc = extractTextFromEl(card, '.subtle') || '';
                const pills = [...card.querySelectorAll('.pill')].map((p) => p.textContent.trim());
                detailHost.innerHTML = buildDynamicDetail('任务详情', '点击查看的任务信息', [
                    { label: '任务名称', value: title },
                    { label: '描述', value: desc || '—' },
                    { label: '标签', value: pills.join(' / ') || '—' },
                ], [
                    { title: '编辑任务', desc: '修改任务参数或调整执行策略。' },
                    { title: '查看日志', desc: '打开该任务最近的运行日志。' },
                ]);
                detailHost.classList.remove('shell-hidden');
            });
        });

        // 表格行点击
        mainHost.querySelectorAll('tbody .route-row').forEach((row) => {
            row.style.cursor = 'pointer';
            row.addEventListener('click', () => {
                mainHost.querySelectorAll('tbody .route-row').forEach((r) => r.classList.remove('is-selected'));
                row.classList.add('is-selected');
                const cells = [...row.querySelectorAll('td')];
                const details = cells.slice(0, 5).map((td, i) => ({
                    label: document.querySelectorAll('thead th')[i]?.textContent.trim() || `列 ${i + 1}`,
                    value: td.textContent.trim(),
                }));
                detailHost.innerHTML = buildDynamicDetail('行详情', '选中表格项的字段信息', details, []);
                detailHost.classList.remove('shell-hidden');
            });
        });

        // 任务项点击（列表视图）
        mainHost.querySelectorAll('.task-item').forEach((item) => {
            item.style.cursor = 'pointer';
            item.addEventListener('click', () => {
                mainHost.querySelectorAll('.task-item').forEach((t) => t.classList.remove('is-selected'));
                item.classList.add('is-selected');
                const title = extractTextFromEl(item, 'strong') || '任务';
                const desc = extractTextFromEl(item, '.subtle') || '';
                detailHost.innerHTML = buildDynamicDetail('任务信息', desc, [
                    { label: '名称', value: title },
                ], [
                    { title: '查看执行记录', desc: '查看该任务的历史执行情况。' },
                ]);
                detailHost.classList.remove('shell-hidden');
            });
        });

        // 洞察卡片点击（分析页）
        mainHost.querySelectorAll('.strip-card').forEach((card) => {
            card.style.cursor = 'pointer';
            card.addEventListener('click', () => {
                mainHost.querySelectorAll('.strip-card').forEach((c) => c.classList.remove('is-selected'));
                card.classList.add('is-selected');
                const title = extractTextFromEl(card, 'strong') || '洞察';
                const desc = extractTextFromEl(card, '.subtle') || '';
                detailHost.innerHTML = buildDynamicDetail('洞察详情', '深入查看选中的分析要点', [
                    { label: '标题', value: title },
                    { label: '摘要', value: desc || '—' },
                ], []);
                detailHost.classList.remove('shell-hidden');
            });
        });
    }

    /* ─── 功能联动：任务看板视图切换 ─── */
    function bindTaskViewToggles() {
        const mainHost = document.getElementById('mainHost');
        const toggles = mainHost.querySelectorAll('.task-view-btn');
        if (!toggles.length) return;
        const kanban = mainHost.querySelector('.task-board');
        const list = mainHost.querySelector('.task-list-view, table');
        const calendar = mainHost.querySelector('.task-calendar');
        toggles.forEach((btn) => {
            btn.addEventListener('click', () => {
                toggles.forEach((b) => b.classList.remove('is-active'));
                btn.classList.add('is-active');
                const view = btn.textContent.trim();
                if (kanban) kanban.classList.toggle('shell-hidden', view !== '看板');
                if (list) list.classList.toggle('shell-hidden', view === '看板' || view === '日历');
                if (calendar) calendar.classList.toggle('shell-hidden', view !== '日历');
            });
        });
    }

    /* ─── 功能联动：任务状态筛选 ─── */
    function bindTaskFilterTabs() {
        const mainHost = document.getElementById('mainHost');
        const tabs = mainHost.querySelectorAll('.task-filter-bar .task-filter-tab');
        if (!tabs.length) return;
        tabs.forEach((tab) => {
            tab.addEventListener('click', () => {
                const label = tab.textContent.replace(/\d+/g, '').trim();
                const cards = mainHost.querySelectorAll('.board-card, .task-item');
                cards.forEach((card) => {
                    if (label === '全部') {
                        card.classList.remove('is-filtered-out');
                    } else {
                        const pills = [...card.querySelectorAll('.pill')].map((p) => p.textContent.trim());
                        const text = card.textContent;
                        const match = pills.some((p) => p.includes(label)) || text.includes(label);
                        card.classList.toggle('is-filtered-out', !match);
                    }
                });
            });
        });
    }

    /* ─── 功能联动：素材分类筛选 ─── */
    function bindAssetCategoryFilter() {
        const mainHost = document.getElementById('mainHost');
        const cats = mainHost.querySelectorAll('.asset-category-item');
        if (!cats.length) return;
        cats.forEach((cat) => {
            cat.addEventListener('click', () => {
                cats.forEach((c) => c.classList.remove('is-active'));
                cat.classList.add('is-active');
                const label = extractTextFromEl(cat, 'strong');
                const thumbs = mainHost.querySelectorAll('.source-thumb');
                thumbs.forEach((thumb) => {
                    if (label === '全部素材') {
                        thumb.classList.remove('is-filtered-out');
                    } else {
                        const tags = [...thumb.querySelectorAll('.pill')].map((p) => p.textContent.trim());
                        const name = thumb.textContent;
                        const typeMap = { '短视频口播': '视频', '封面图片': '图片', 'B-roll 镜头': '视频', '音频 / 配乐': '音频', '字幕 / 文案': '字幕' };
                        const mapped = typeMap[label] || label;
                        const match = tags.some((t) => t.includes(mapped)) || name.includes(mapped);
                        thumb.classList.toggle('is-filtered-out', !match);
                    }
                });
            });
        });
    }

    /* ─── 功能联动：素材点击更新右侧 ─── */
    function bindAssetThumbDetail() {
        const mainHost = document.getElementById('mainHost');
        const detailHost = document.getElementById('detailHost');
        const thumbs = mainHost.querySelectorAll('.source-thumb');
        if (!thumbs.length) return;
        thumbs.forEach((thumb) => {
            thumb.addEventListener('click', () => {
                const name = extractTextFromEl(thumb, '.source-thumb__name') || '未命名素材';
                const tags = [...thumb.querySelectorAll('.pill')].map((p) => p.textContent.trim());
                const dur = extractTextFromEl(thumb, '.source-thumb__dur');
                detailHost.innerHTML = buildDynamicDetail('素材详情', '选中素材的属性信息', [
                    { label: '素材名称', value: name },
                    { label: '类型标签', value: tags.join(' / ') || '—' },
                    { label: '时长', value: dur || '—' },
                    { label: '状态', value: tags.find((t) => ['已授权', '待审', '已入库', '可复用', '需授权', '高转化'].includes(t)) || '—' },
                ], [
                    { title: '编辑素材信息', desc: '修改名称、分类和授权状态。' },
                    { title: '发送到创作链路', desc: '将素材推送到内容工厂或创意工坊。' },
                ]);
                detailHost.classList.remove('shell-hidden');
            });
        });
    }

    /* ─── 功能联动：分析图表切换 ─── */
    function bindChartToggles() {
        const mainHost = document.getElementById('mainHost');
        const toggles = mainHost.querySelectorAll('.analytics-chart-toggles button');
        if (!toggles.length) return;
        toggles.forEach((btn) => {
            btn.addEventListener('click', () => {
                toggles.forEach((b) => b.classList.remove('is-active'));
                btn.classList.add('is-active');
                const chart = mainHost.querySelector('.chart-placeholder');
                if (chart) chart.textContent = `📊 ${btn.textContent.trim()} 视图`;
            });
        });
    }

    /* ─── 响应式：右侧面板手动切换 ─── */
    function bindDetailPanelToggle() {
        const btn = document.getElementById('detailToggle');
        if (!btn) return;
        btn.addEventListener('click', () => {
            const detailHost = document.getElementById('detailHost');
            const route = routes[currentRoute];
            if (route?.hideDetailPanel === true) return;
            uiState.detailPanelForced = !detailHost.classList.contains('shell-hidden') ? 'hidden' : 'visible';
            detailHost.classList.toggle('shell-hidden');
            document.getElementById('shellApp').classList.toggle('detail-hidden', detailHost.classList.contains('shell-hidden'));
        });
    }

    function bindRouteInteractions() {
        bindSegmentedButtons();
        bindFilters();
        bindDetailTriggers();
        bindConfigNavItems();
        bindSourceBrowserTabs();
        bindMainItemClicks();
        bindTaskViewToggles();
        bindTaskFilterTabs();
        bindAssetCategoryFilter();
        bindAssetThumbDetail();
        bindChartToggles();
        bindDragAndDrop();
        bindAIConfigInteractions();
        renderCharts();
        bindAnalyticsInteractions();
        renderAnalyticsCanvases();
        applyCurrentRouteState();
        renderSearchPanel();
    }

    function bindConfigNavItems() {
        document.querySelectorAll('.config-nav-item').forEach((item) => {
            item.addEventListener('click', () => {
                item.closest('.config-nav').querySelectorAll('.config-nav-item').forEach((i) => i.classList.remove('is-selected'));
                item.classList.add('is-selected');
                // 滚动到对应表单分组
                const index = [...item.closest('.config-nav').querySelectorAll('.config-nav-item')].indexOf(item);
                const groups = document.querySelectorAll('.config-form-group');
                if (groups[index]) groups[index].scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
        });
    }

    function bindSourceBrowserTabs() {
        document.querySelectorAll('.source-browser-tabs span').forEach((tab) => {
            tab.addEventListener('click', () => {
                tab.closest('.source-browser-tabs').querySelectorAll('span').forEach((t) => t.classList.remove('is-selected'));
                tab.classList.add('is-selected');
                // 实际筛选缩略图
                const label = tab.textContent.replace(/\d+/g, '').trim();
                const grid = tab.closest('.panel, .source-browser-shell')?.querySelector('.source-thumb-grid');
                if (grid) {
                    grid.querySelectorAll('.source-thumb').forEach((thumb) => {
                        if (!label || label === '全部') {
                            thumb.classList.remove('is-filtered-out');
                        } else {
                            const text = thumb.textContent + [...thumb.querySelectorAll('.pill')].map((p) => p.textContent).join(' ');
                            thumb.classList.toggle('is-filtered-out', !text.includes(label));
                        }
                    });
                }
            });
        });
        document.querySelectorAll('.source-thumb').forEach((thumb) => {
            thumb.addEventListener('click', () => {
                thumb.closest('.source-thumb-grid').querySelectorAll('.source-thumb').forEach((t) => t.classList.remove('is-selected'));
                thumb.classList.add('is-selected');
            });
        });
    }

    function syncResponsiveState() {
        const shell = document.getElementById('shellApp');
        const route = routes[currentRoute];
        const detailHost = document.getElementById('detailHost');
        const width = window.innerWidth;

        // 如果用户手动切换了面板，优先尊重用户选择
        if (uiState.detailPanelForced) {
            detailHost.classList.toggle('shell-hidden', uiState.detailPanelForced === 'hidden');
        } else {
            detailHost.classList.toggle('shell-hidden', route?.hideDetailPanel === true || width < 1180);
        }
        shell.classList.toggle('detail-hidden', detailHost.classList.contains('shell-hidden'));

        if (width < 960) {
            shell.classList.add('sidebar-collapsed');
            shell.classList.add('compact-mode');
        } else if (width < 1366) {
            shell.classList.add('sidebar-collapsed');
            shell.classList.remove('compact-mode');
        } else {
            shell.classList.remove('sidebar-collapsed');
            shell.classList.remove('compact-mode');
        }

        // 更新切换按钮状态
        const toggleBtn = document.getElementById('detailToggle');
        if (toggleBtn) {
            toggleBtn.classList.toggle('is-active', !detailHost.classList.contains('shell-hidden'));
        }
    }

    function renderRoute(routeKey) {
        const route = routes[routeKey];
        if (!route) {
            return;
        }
        // 相同路由不重复渲染
        if (currentRoute === routeKey && document.getElementById('mainHost').innerHTML.length > 100) {
            return;
        }
        animateRouteTransition(routeKey);
    }

    function bindEvents() {
        document.getElementById('menuToggle').addEventListener('click', () => {
            document.getElementById('shellApp').classList.toggle('sidebar-collapsed');
        });

        document.getElementById('themeToggle').addEventListener('click', () => {
            applyTheme(currentTheme === 'dark' ? 'light' : 'dark');
        });

        document.querySelectorAll('.nav-link[data-route]').forEach((button) => {
            button.addEventListener('click', () => {
                renderRoute(button.dataset.route);
            });
        });

        bindSearch();
        bindDetailPanelToggle();
        window.addEventListener('resize', () => {
            uiState.detailPanelForced = null;
            syncResponsiveState();
        });
    }

    window.addEventListener('DOMContentLoaded', () => {
        loadRecentRoutes();
        bindEvents();
        bindKeyboardShortcuts();
        bindContextMenu();
        initNotificationSystem();
        renderRoute(currentRoute);
    });

    /* ═══════════════════════════════════════════════
       Toast 反馈系统
       ═══════════════════════════════════════════════ */
    function showToast(message, tone) {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast-item toast-${tone || 'info'}`;
        toast.textContent = message;
        container.appendChild(toast);
        requestAnimationFrame(() => toast.classList.add('toast-visible'));
        setTimeout(() => {
            toast.classList.remove('toast-visible');
            toast.addEventListener('transitionend', () => toast.remove());
        }, 3000);
    }

    /* ═══════════════════════════════════════════════
       通知系统
       ═══════════════════════════════════════════════ */
    function addNotification(title, body, tone) {
        uiState.notificationId += 1;
        const notification = { id: uiState.notificationId, title, body, tone: tone || 'info', read: false, time: new Date() };
        uiState.notifications.unshift(notification);
        if (uiState.notifications.length > 50) uiState.notifications.length = 50;
        renderNotifications();
        updateNotificationBadge();
        return notification.id;
    }

    function renderNotifications() {
        const list = document.getElementById('notificationList');
        if (!list) return;
        if (!uiState.notifications.length) {
            list.innerHTML = '<div class="notification-empty">暂无通知</div>';
            return;
        }
        list.innerHTML = uiState.notifications.slice(0, 20).map((n) => `
            <div class="notification-item ${n.read ? '' : 'is-unread'}" data-notif-id="${n.id}">
                <div class="notification-item__dot ${n.tone}"></div>
                <div class="notification-item__body">
                    <strong>${n.title}</strong>
                    <div class="subtle">${n.body}</div>
                    <div class="subtle">${formatTimeAgo(n.time)}</div>
                </div>
            </div>
        `).join('');
        list.querySelectorAll('.notification-item').forEach((item) => {
            item.addEventListener('click', () => {
                const id = Number(item.dataset.notifId);
                const notif = uiState.notifications.find((n) => n.id === id);
                if (notif) notif.read = true;
                item.classList.remove('is-unread');
                updateNotificationBadge();
            });
        });
    }

    function updateNotificationBadge() {
        const btn = document.getElementById('notificationToggle');
        if (!btn) return;
        const unread = uiState.notifications.filter((n) => !n.read).length;
        let badge = btn.querySelector('.notif-badge');
        if (unread > 0) {
            if (!badge) {
                badge = document.createElement('span');
                badge.className = 'notif-badge';
                btn.appendChild(badge);
            }
            badge.textContent = unread > 9 ? '9+' : unread;
        } else if (badge) {
            badge.remove();
        }
    }

    function formatTimeAgo(date) {
        const seconds = Math.floor((new Date() - date) / 1000);
        if (seconds < 60) return '刚刚';
        if (seconds < 3600) return Math.floor(seconds / 60) + ' 分钟前';
        if (seconds < 86400) return Math.floor(seconds / 3600) + ' 小时前';
        return Math.floor(seconds / 86400) + ' 天前';
    }

    function initNotificationSystem() {
        const btn = document.getElementById('notificationToggle');
        const panel = document.getElementById('notificationPanel');
        if (!btn || !panel) return;

        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            panel.classList.toggle('shell-hidden');
        });

        document.addEventListener('click', (e) => {
            if (!e.target.closest('#notificationPanel') && !e.target.closest('#notificationToggle')) {
                panel.classList.add('shell-hidden');
            }
        });

        const clearBtn = document.getElementById('clearNotifications');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                uiState.notifications.forEach((n) => { n.read = true; });
                renderNotifications();
                updateNotificationBadge();
                showToast('所有通知已标为已读', 'success');
            });
        }

        // 模拟系统通知
        setTimeout(() => addNotification('系统提醒', '有 12 个素材等待版权审核，请及时处理。', 'warning'), 1500);
        setTimeout(() => addNotification('任务完成', '批量标题生成任务已完成，共生成 24 条标题。', 'success'), 3000);
        setTimeout(() => addNotification('AI 模型更新', 'GPT-4o 模型已同步至所有 AI 工作台。', 'info'), 5000);
        setTimeout(() => addNotification('性能告警', '数据采集任务 #0382 连续 3 次超时，建议检查代理配置。', 'error'), 8000);
    }

    /* ═══════════════════════════════════════════════
       右键菜单系统
       ═══════════════════════════════════════════════ */
    function showContextMenu(x, y, items) {
        const menu = document.getElementById('contextMenu');
        if (!menu) return;
        menu.innerHTML = items.map((item) => {
            if (item.separator) return '<div class="context-menu__separator"></div>';
            return `<button class="context-menu__item" data-action="${item.action}" type="button"><span class="shell-icon">${item.icon || ''}</span> ${item.label}</button>`;
        }).join('');
        menu.style.left = Math.min(x, window.innerWidth - 200) + 'px';
        menu.style.top = Math.min(y, window.innerHeight - menu.children.length * 36 - 16) + 'px';
        menu.classList.remove('shell-hidden');

        const handler = (e) => {
            const btn = e.target.closest('.context-menu__item');
            if (btn) {
                const action = btn.dataset.action;
                menu.classList.add('shell-hidden');
                handleContextAction(action);
            }
            if (!e.target.closest('.context-menu')) {
                menu.classList.add('shell-hidden');
            }
            document.removeEventListener('click', handler);
        };
        setTimeout(() => document.addEventListener('click', handler), 0);
    }

    let contextTarget = null;

    function handleContextAction(action) {
        const name = contextTarget ? (extractTextFromEl(contextTarget, 'strong') || contextTarget.textContent.trim().slice(0, 20)) : '项目';
        switch (action) {
            case 'edit': showToast(`正在编辑: ${name}`, 'info'); break;
            case 'delete': showToast(`已删除: ${name}`, 'warning'); addNotification('删除操作', `"${name}" 已移入回收站。`, 'warning'); break;
            case 'copy': showToast(`已复制: ${name}`, 'success'); break;
            case 'export': showToast(`已导出: ${name}`, 'success'); break;
            case 'pin': showToast(`已置顶: ${name}`, 'info'); break;
            case 'archive': showToast(`已归档: ${name}`, 'info'); break;
            default: showToast(`操作: ${action}`, 'info');
        }
    }

    function bindContextMenu() {
        document.addEventListener('contextmenu', (e) => {
            const card = e.target.closest('.board-card, .strip-card, .task-item, .source-thumb, .workbench-sidecard, tbody .route-row');
            if (!card) return;
            e.preventDefault();
            contextTarget = card;

            const isThumb = card.classList.contains('source-thumb');
            const isRow = card.tagName === 'TR';
            const items = isThumb ? [
                { icon: '✏', label: '编辑素材信息', action: 'edit' },
                { icon: '📋', label: '复制素材链接', action: 'copy' },
                { separator: true },
                { icon: '📤', label: '导出素材', action: 'export' },
                { icon: '📌', label: '标记为高价值', action: 'pin' },
                { separator: true },
                { icon: '🗑', label: '删除', action: 'delete' },
            ] : isRow ? [
                { icon: '👁', label: '查看详情', action: 'edit' },
                { icon: '📋', label: '复制行数据', action: 'copy' },
                { icon: '📤', label: '导出为 CSV', action: 'export' },
                { separator: true },
                { icon: '🗑', label: '删除', action: 'delete' },
            ] : [
                { icon: '✏', label: '编辑', action: 'edit' },
                { icon: '📋', label: '复制', action: 'copy' },
                { icon: '📌', label: '置顶', action: 'pin' },
                { icon: '🗃', label: '归档', action: 'archive' },
                { separator: true },
                { icon: '🗑', label: '删除', action: 'delete' },
            ];
            showContextMenu(e.clientX, e.clientY, items);
        });
    }

    /* ═══════════════════════════════════════════════
       拖拽排序（看板列内/列间）
       ═══════════════════════════════════════════════ */
    function bindDragAndDrop() {
        const mainHost = document.getElementById('mainHost');
        const draggables = mainHost.querySelectorAll('.board-card, .task-item');
        if (!draggables.length) return;

        draggables.forEach((card) => {
            card.setAttribute('draggable', 'true');
            card.addEventListener('dragstart', (e) => {
                card.classList.add('is-dragging');
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/plain', '');
            });
            card.addEventListener('dragend', () => {
                card.classList.remove('is-dragging');
                mainHost.querySelectorAll('.drag-over').forEach((el) => el.classList.remove('drag-over'));
            });
        });

        const columns = mainHost.querySelectorAll('.board-column, .kanban-column');
        columns.forEach((col) => {
            col.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
                col.classList.add('drag-over');
                const dragging = mainHost.querySelector('.is-dragging');
                if (!dragging) return;
                const container = col.querySelector('.board-column__cards') || col;
                const afterElement = getDragAfterElement(container, e.clientY);
                if (afterElement) {
                    container.insertBefore(dragging, afterElement);
                } else {
                    container.appendChild(dragging);
                }
            });
            col.addEventListener('dragleave', (e) => {
                if (!col.contains(e.relatedTarget)) col.classList.remove('drag-over');
            });
            col.addEventListener('drop', (e) => {
                e.preventDefault();
                col.classList.remove('drag-over');
                const dragging = mainHost.querySelector('.is-dragging');
                if (dragging) {
                    showToast('卡片已移动', 'success');
                    addNotification('看板操作', `"${extractTextFromEl(dragging, 'strong') || '卡片'}" 已移至新列。`, 'info');
                }
            });
        });
    }

    function getDragAfterElement(container, y) {
        const elements = [...container.querySelectorAll('.board-card:not(.is-dragging), .task-item:not(.is-dragging)')];
        return elements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            if (offset < 0 && offset > closest.offset) {
                return { offset, element: child };
            }
            return closest;
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }

    /* ═══════════════════════════════════════════════
       AI 配置联动
       ═══════════════════════════════════════════════ */
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
    function renderCharts() {
        const mainHost = document.getElementById('mainHost');
        mainHost.querySelectorAll('.chart-placeholder').forEach((placeholder) => {
            const canvas = document.createElement('canvas');
            canvas.width = placeholder.clientWidth || 400;
            canvas.height = placeholder.clientHeight || 200;
            canvas.style.width = '100%';
            canvas.style.height = '100%';
            placeholder.textContent = '';
            placeholder.appendChild(canvas);
            placeholder.style.fontSize = '0';

            const ctx = canvas.getContext('2d');
            const parent = placeholder.closest('.analytics-chart-panel, .panel');
            const toggles = parent?.querySelectorAll('.analytics-chart-toggles button, .segmented button');
            const activeToggle = parent?.querySelector('.analytics-chart-toggles button.is-active, .segmented button.is-active');
            const mode = activeToggle?.textContent.trim() || '趋势';

            if (mode.includes('分布') || mode.includes('占比')) {
                drawPieChart(ctx, canvas.width, canvas.height);
            } else if (mode.includes('对比') || mode.includes('柱')) {
                drawBarChart(ctx, canvas.width, canvas.height);
            } else {
                drawTrendChart(ctx, canvas.width, canvas.height);
            }

            // 切换重绘
            if (toggles) {
                toggles.forEach((btn) => {
                    btn.addEventListener('click', () => {
                        const m = btn.textContent.trim();
                        ctx.clearRect(0, 0, canvas.width, canvas.height);
                        if (m.includes('分布') || m.includes('占比')) drawPieChart(ctx, canvas.width, canvas.height);
                        else if (m.includes('对比') || m.includes('柱')) drawBarChart(ctx, canvas.width, canvas.height);
                        else drawTrendChart(ctx, canvas.width, canvas.height);
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
            ctx.fillStyle = textColor; ctx.font = '11px sans-serif'; ctx.textAlign = 'right';
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
            ctx.beginPath(); ctx.arc(x, y, 3, 0, Math.PI * 2);
            ctx.fillStyle = '#00f2ea'; ctx.fill();
            ctx.strokeStyle = isDark ? '#1e293b' : '#ffffff'; ctx.lineWidth = 2; ctx.stroke();
        });

        // X轴标签
        ctx.fillStyle = textColor; ctx.font = '10px sans-serif'; ctx.textAlign = 'center';
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

            ctx.fillStyle = textColor; ctx.font = '10px sans-serif'; ctx.textAlign = 'center';
            ctx.fillText(d.label, x + barW / 2, h - padding.bottom + 16);
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
            ctx.font = 'bold 11px sans-serif';
            ctx.textAlign = 'center';
            if (d.value > 5) {
                ctx.fillText(`${d.label}`, lx, ly - 4);
                ctx.font = '10px sans-serif';
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
    function bindAnalyticsInteractions() {
        const mainHost = document.getElementById('mainHost');

        // — 通用：data-source-item / chart-type-btn 选中切换
        mainHost.querySelectorAll('.data-source-list, .report-template-list').forEach(list => {
            list.querySelectorAll('.data-source-item').forEach(item => {
                item.addEventListener('click', () => {
                    list.querySelectorAll('.data-source-item').forEach(i => i.classList.remove('is-selected'));
                    item.classList.add('is-selected');
                    if (typeof showToast === 'function') showToast('已切换: ' + (item.querySelector('strong')?.textContent || ''), 'info');
                });
            });
        });

        mainHost.querySelectorAll('.chart-type-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                mainHost.querySelectorAll('.chart-type-btn').forEach(b => b.classList.remove('is-selected'));
                btn.classList.add('is-selected');
                showToast('图表类型: ' + btn.textContent.trim(), 'info');
            });
        });

        // — 蓝海分析：气泡点击 → 更新右侧详情卡
        mainHost.querySelectorAll('.matrix-bubble').forEach(bubble => {
            bubble.addEventListener('click', () => {
                mainHost.querySelectorAll('.matrix-bubble').forEach(b => b.classList.remove('is-active'));
                bubble.classList.add('is-active');
                const detailCard = mainHost.querySelector('.opportunity-detail-card');
                if (detailCard) {
                    const name = bubble.textContent.trim();
                    const heat = 40 + Math.floor(Math.random() * 55);
                    const comp = 15 + Math.floor(Math.random() * 50);
                    const margin = 14 + Math.floor(Math.random() * 28);
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
                showToast('选中: ' + bubble.textContent.trim(), 'success');
            });
        });

        // — 竞品监控：竞品卡选中切换 + 趋势高亮
        mainHost.querySelectorAll('.rival-card').forEach(card => {
            card.addEventListener('click', () => {
                mainHost.querySelectorAll('.rival-card').forEach(c => c.classList.remove('is-active'));
                card.classList.add('is-active');
                showToast('查看竞品: ' + card.querySelector('strong')?.textContent, 'info');
            });
        });

        // — 电商转化：漏斗步骤点击高亮 + 更新流失面板
        mainHost.querySelectorAll('.funnel-step').forEach(step => {
            step.addEventListener('click', () => {
                mainHost.querySelectorAll('.funnel-step').forEach(s => s.classList.remove('is-active'));
                step.classList.add('is-active');
                showToast('聚焦阶段: ' + step.querySelector('span')?.textContent, 'info');
            });
        });

        // — 互动分析：热力图格子高亮
        mainHost.querySelectorAll('.heatmap-cell').forEach(cell => {
            cell.addEventListener('click', () => {
                mainHost.querySelectorAll('.heatmap-cell').forEach(c => c.classList.remove('is-active'));
                cell.classList.add('is-active');
            });
        });

        // — 粉丝画像：Persona 卡片选中
        mainHost.querySelectorAll('.persona-grid article').forEach(card => {
            card.addEventListener('click', () => {
                mainHost.querySelectorAll('.persona-grid article').forEach(c => c.classList.remove('is-active'));
                card.classList.add('is-active');
                showToast('查看画像: ' + card.querySelector('strong')?.textContent, 'info');
            });
        });

        // — 流量看板：来源卡片选中
        mainHost.querySelectorAll('.traffic-source-card').forEach(card => {
            card.addEventListener('click', () => {
                mainHost.querySelectorAll('.traffic-source-card').forEach(c => c.classList.remove('is-active'));
                card.classList.add('is-active');
                showToast('聚焦: ' + card.querySelector('.subtle')?.textContent, 'info');
            });
        });

        // — 报表中心：步骤卡片选中
        mainHost.querySelectorAll('.report-builder-steps article').forEach(step => {
            step.addEventListener('click', () => {
                mainHost.querySelectorAll('.report-builder-steps article').forEach(s => s.classList.remove('is-active'));
                step.classList.add('is-active');
            });
        });

        // — 利润分析：成本结构卡片选中
        mainHost.querySelectorAll('.profit-ledger-grid article').forEach(card => {
            card.addEventListener('click', () => {
                mainHost.querySelectorAll('.profit-ledger-grid article').forEach(c => c.classList.remove('is-active'));
                card.classList.add('is-active');
                showToast('查看成本: ' + card.querySelector('span')?.textContent, 'info');
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
        document.querySelectorAll('.heatmap-cell').forEach(cell => {
            const lvl = 1 + Math.floor(Math.random() * 5);
            cell.className = 'heatmap-cell lvl-' + lvl;
        });

        // — 粉丝亲和力条动态化
        document.querySelectorAll('.affinity-bars i').forEach(bar => {
            const pct = 18 + Math.floor(Math.random() * 64);
            bar.style.width = pct + '%';
        });

        // — 电商转化漏斗动态化
        document.querySelectorAll('.funnel-step strong').forEach((el, idx) => {
            const bases = [2840000, 136000, 24000, 8436, 7982];
            const jitter = Math.floor(bases[idx] * (0.93 + Math.random() * 0.14));
            el.textContent = jitter >= 10000 ? (jitter / 10000).toFixed(1) + '万' : jitter.toLocaleString();
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

        // 生成数据并绘线
        const pts = 14;
        const data = Array.from({length: pts}, () => 20 + Math.random() * (h - 80));
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
        const groups = container.querySelectorAll('.compare-group');
        groups.forEach(group => {
            const bars = group.querySelectorAll('i');
            bars.forEach(bar => {
                const pct = 40 + Math.floor(Math.random() * 52);
                bar.style.height = pct + '%';
            });
        });
    }

    function renderRivalBars(isDark) {
        const container = document.querySelector('.rival-trend-bars');
        if (!container) return;
        container.querySelectorAll('i').forEach(bar => {
            const pct = 28 + Math.floor(Math.random() * 62);
            bar.style.height = pct + '%';
        });
    }

    /* ═══════════════════════════════════════════════
       骨架屏 & 路由过渡动画
       ═══════════════════════════════════════════════ */
    function showSkeleton() {
        const mainHost = document.getElementById('mainHost');
        mainHost.innerHTML = `
            <div class="skeleton-screen">
                <div class="skeleton-line skeleton-title"></div>
                <div class="skeleton-line skeleton-subtitle"></div>
                <div class="skeleton-stat-row">
                    <div class="skeleton-stat"></div>
                    <div class="skeleton-stat"></div>
                    <div class="skeleton-stat"></div>
                </div>
                <div class="skeleton-block"></div>
                <div class="skeleton-grid">
                    <div class="skeleton-card"></div>
                    <div class="skeleton-card"></div>
                    <div class="skeleton-card"></div>
                    <div class="skeleton-card"></div>
                    <div class="skeleton-card"></div>
                    <div class="skeleton-card"></div>
                </div>
            </div>
        `;
        mainHost.classList.add('skeleton-active');
    }

    function animateRouteTransition(routeKey) {
        const mainHost = document.getElementById('mainHost');
        const detailHost = document.getElementById('detailHost');

        // 淡出当前内容
        mainHost.classList.add('route-exit');
        detailHost.classList.add('route-exit');

        setTimeout(() => {
            showSkeleton();
            mainHost.classList.remove('route-exit');
            mainHost.classList.add('route-enter');

            setTimeout(() => {
                // 实际渲染
                const route = routes[routeKey];
                if (!route) return;

                currentRoute = routeKey;
                uiState.detailPanelForced = null;
                const shell = document.getElementById('shellApp');
                shell.className = `app-shell route-${routeKey}`;
                document.getElementById('routeEyebrow').textContent = route.eyebrow;
                document.querySelectorAll('.nav-link[data-route]').forEach((button) => {
                    button.classList.toggle('is-active', button.dataset.route === routeKey);
                });

                if (route.mainTemplate) {
                    setTemplateContent('mainHost', route.mainTemplate);
                } else {
                    setHostHtml('mainHost', route.mainHtml);
                }

                if (route.detailTemplate) {
                    setTemplateContent('detailHost', route.detailTemplate);
                } else {
                    setHostHtml('detailHost', route.detailHtml);
                }
                detailHost.classList.remove('route-exit');
                document.getElementById('detailHost').classList.toggle('shell-hidden', route.hideDetailPanel === true || window.innerWidth < 1180);

                renderSidebarSummary(route.sidebarSummary);
                applyTheme(currentTheme);
                renderStatus(route);
                mainHost.classList.remove('route-enter', 'skeleton-active');
                mainHost.classList.add('route-enter-active');

                bindRouteInteractions();
                bindDragAndDrop();
                bindAIConfigInteractions();
                renderCharts();
                syncResponsiveState();
                pushRecentRoute(routeKey);

                setTimeout(() => mainHost.classList.remove('route-enter-active'), 350);
            }, 180);
        }, 120);
    }

    /* ═══════════════════════════════════════════════
       快捷键系统
       ═══════════════════════════════════════════════ */
    function bindKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            const isInput = ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName);

            // Ctrl+K → 搜索
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const search = document.getElementById('globalSearch');
                if (search) { search.focus(); search.select(); }
                return;
            }

            // Ctrl+\ → 切换右侧面板
            if ((e.ctrlKey || e.metaKey) && e.key === '\\') {
                e.preventDefault();
                document.getElementById('detailToggle')?.click();
                return;
            }

            // Ctrl+B → 切换侧边栏
            if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
                e.preventDefault();
                document.getElementById('menuToggle')?.click();
                return;
            }

            // Ctrl+D → 切换主题
            if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
                e.preventDefault();
                document.getElementById('themeToggle')?.click();
                return;
            }

            // Escape → 关闭弹层
            if (e.key === 'Escape') {
                document.getElementById('contextMenu')?.classList.add('shell-hidden');
                document.getElementById('notificationPanel')?.classList.add('shell-hidden');
                const overlay = document.getElementById('shortcutOverlay');
                if (overlay && !overlay.classList.contains('shell-hidden')) {
                    overlay.classList.add('shell-hidden');
                    return;
                }
                return;
            }

            // ? → 快捷键帮助
            if (!isInput && e.key === '?') {
                e.preventDefault();
                document.getElementById('shortcutOverlay')?.classList.toggle('shell-hidden');
                return;
            }
        });

        document.getElementById('closeShortcuts')?.addEventListener('click', () => {
            document.getElementById('shortcutOverlay')?.classList.add('shell-hidden');
        });
    }
})();
