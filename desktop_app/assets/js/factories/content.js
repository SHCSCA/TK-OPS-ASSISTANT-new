const contentWorkbenchFactories = Object.create(null);

function registerContentWorkbenchFactory(workbenchType, factory) {
    if (!workbenchType || String(workbenchType).trim() === '') {
        return;
    }
    if (typeof factory !== 'function') {
        return;
    }
    contentWorkbenchFactories[workbenchType] = factory;
}

function makeContentWorkbenchRoute(config) {
    const registeredFactory = contentWorkbenchFactories[config.workbenchType];
    if (registeredFactory) {
        return registeredFactory(config);
    }

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

    if (config.workbenchType === 'creative-workshop') {
        centerHtml = `
            <section class="workbench-canvas workbench-canvas--creative">
                <div class="toolbar-strip">
                    <div class="toolbar-strip__group"><strong>鍒涙剰缁勫悎鐢绘澘</strong><span class="subtle">涓婚銆侀暅澶淬€佸彛鎾拰鍗栫偣鍦ㄤ竴鍧楁澘涓婂揩閫熺粍鍚?/span></div>
                    <div class="toolbar-strip__group"><button class="secondary-button" type="button">閿佸畾鐗堟湰</button><button class="secondary-button" type="button">鐢熸垚瀵规瘮</button></div>
                </div>
                <div class="focus-grid" data-search="鍒涙剰宸ュ潑 涓婚 闀滃ご 鍙ｆ挱 缁勫悎">
                    ${focusCardsHtml}
                </div>
            </section>
        `;
        sideHtml = `
            <section class="panel">
                <div class="panel__header"><div><strong>鏂规璇勫垎</strong><div class="subtle">鍙冲垪涓嶅啀鏄€氱敤鎽樿锛岃€屾槸鍒涙剰璇勫垎涓庣増鏈缓璁?/div></div></div>
                <div class="workbench-side-list">${sideCardsHtml}</div>
            </section>
        `;
        bottomHtml = `
            <section class="panel">
                <div class="panel__header"><div><strong>瀹為獙杞ㄨ抗</strong><div class="subtle">鎶婂凡璇曡繃鐨勫垱鎰忕粍鍚堝拰淇濈暀寤鸿娌夋穩涓嬫潵</div></div></div>
                <div class="workbench-strip-grid">${bottomCardsHtml}</div>
            </section>
        `;
    } else if (config.workbenchType === 'ai-content-factory') {
        centerHtml = `
            <section class="workbench-canvas workbench-canvas--factory">
                <div class="toolbar-strip">
                    <div class="toolbar-strip__group"><strong>鍐呭鐢熶骇宸ヤ綔娴?/strong><span class="subtle">鑺傜偣銆佹壒娆″拰浜у嚭鐘舵€侀泦涓樉绀猴紝涓嶅啀閫€鍖栦负鏅€?AI 鍗＄墖椤?/span></div>
                    <div class="toolbar-strip__group"><button class="secondary-button" type="button">淇濆瓨宸ヤ綔娴?/button><button class="secondary-button" type="button">杩愯鎵规</button></div>
                </div>
                <div class="workflow-board" data-search="AI 鍐呭宸ュ巶 宸ヤ綔娴?鑺傜偣 鐢熶骇绾?>
                    <div class="workflow-node is-active"><strong>杈撳叆绱犳潗</strong><div class="subtle">鏂囨湰銆侀摼鎺ャ€佸晢鍝佸簱</div></div>
                    <div class="workflow-connector"></div>
                    <div class="workflow-node"><strong>AI 鑴氭湰</strong><div class="subtle">閽╁瓙銆佺粨鏋勩€丆TA</div></div>
                    <div class="workflow-connector"></div>
                    <div class="workflow-node"><strong>璇煶涓庡瓧骞?/strong><div class="subtle">TTS + 瀛楀箷娓呮礂</div></div>
                    <div class="workflow-connector"></div>
                    <div class="workflow-node"><strong>鎵归噺鍓緫</strong><div class="subtle">灏侀潰銆佺墖娈点€佸鍑?/div></div>
                </div>
            </section>
        `;
        sideHtml = `
            <section class="panel">
                <div class="panel__header"><div><strong>鑺傜偣搴撲笌椤圭洰鍖?/strong><div class="subtle">鎶婇」鐩€佸父鐢ㄨ妭鐐瑰拰褰撳墠鎵规鐘舵€佺淮鎸佸湪涓诲唴瀹瑰彸鍒?/div></div></div>
                <div class="workbench-side-list">${sideCardsHtml}</div>
            </section>
        `;
        bottomHtml = `
            <section class="panel">
                <div class="panel__header"><div><strong>鎵规杩愯鐘舵€?/strong><div class="subtle">鎵归噺鐢熶骇瑕佷紭鍏堝睍绀轰换鍔￠€氳繃鐜囥€佸け璐ヨ妭鐐瑰拰鍙洖鏀炬壒娆?/div></div></div>
                <div class="workbench-strip-grid">${bottomCardsHtml}</div>
            </section>
        `;
    }

    const detailHtml = `
        <div class="detail-root">
            <section class="panel">
                <div class="panel__header"><div><strong>${config.title}鎽樿</strong><div class="subtle">${config.detailDesc}</div></div></div>
                <div class="detail-list">
                    ${detailGroups.map((group) => `<div class="detail-item"><span class="subtle">${group.label}</span><strong>${group.value}</strong></div>`).join('')}
                </div>
            </section>
            <section class="panel">
                <div class="panel__header"><div><strong>鍊肩彮鍔ㄤ綔</strong><div class="subtle">鍙充晶璇︽儏缁х画鎵胯浇褰撳墠鎵规鐨勫喅绛栨彁绀?/div></div></div>
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

/* 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
   Batch 3 鈥?task-ops 瀹舵棌宸ュ巶
   Template E: 椤堕儴鐘舵€佽繃婊?+ 浠诲姟鐪嬫澘/鍒楄〃/鏃ュ巻 + 鐘舵€佹爮
   鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?*/



