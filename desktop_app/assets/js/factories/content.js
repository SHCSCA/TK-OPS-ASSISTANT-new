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
            (card) => `<article class="workbench-sidecard${card.routeLink ? ' cross-nav-card' : ''}" data-search="${card.search || card.title}"${card.routeLink ? ` data-route-link="${card.routeLink}"` : ''}><div class="workbench-sidecard__head"><strong>${card.title}</strong><span class="pill ${card.tone}">${card.badge}</span></div><div class="subtle">${card.desc}</div></article>`
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
    let outerBottomHtml = '';

    // video-editor workbenchType 分支已移至 factories/video-editor.js
if (config.workbenchType === 'creative-workshop') {
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
                ${outerBottomHtml}
            </section>
        `,
        detailHtml,
    };
}

/* ═══════════════════════════════════════════════
   Batch 3 — task-ops 家族工厂
   Template E: 顶部状态过滤 + 任务看板/列表/日历 + 状态栏
   ═══════════════════════════════════════════════ */
