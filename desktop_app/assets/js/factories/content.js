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
                    <section class="source-browser-shell">`

        // Keep the source browser, preview, mini-preview all the same
        // but move transport + timeline out to bottomHtml
        centerHtml += `
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
            </section>
        `;
        bottomHtml = '';
        outerBottomHtml = `
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
