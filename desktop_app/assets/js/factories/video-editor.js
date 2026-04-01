function makeVideoEditorRoute() {
    const summaryChips = [
        { label: '当前序列', value: '混剪序列 #18', note: '主版本正在精修转场与结尾 CTA', search: '当前 序列 混剪 18' },
        { label: '未解决阻塞', value: '1 个授权素材', note: '节日 B-roll 未补齐前不能锁定终版', search: '阻塞项 授权 素材' },
        { label: '导出队列', value: '7 个排队', note: '建议完成校对后集中发起多版本导出', search: '导出 状态 7 个 排队' },
    ];

    const sideCards = [
        { title: '当前片段', desc: '主序列已完成粗剪，正在补两处转场并收紧结尾 CTA 时长。', badge: '精剪中', tone: 'success', search: '当前 片段 精剪中' },
        { title: '素材检查', desc: '节日 B-roll 仍待授权，授权后自动回填到 V2 补镜轨道。', badge: '待授权', tone: 'warning', search: '素材 检查 节日 B-roll 待授权' },
        { title: '字幕检查', desc: '两条口播字幕超出安全字数，需要压缩到 22 字以内。', badge: '待校对', tone: 'info', search: '字幕 检查 待校对' },
    ];

    const queueCards = [
        { title: '待导出批次 A', desc: '主版本、5 秒短版和字幕版准备合并导出。', badge: '待导出', tone: 'warning', search: '导出 批次 A' },
        { title: '字幕校对', desc: '两条核心口播字幕需要人工收短并校正断句。', badge: '校对', tone: 'info', search: '字幕 校对 2 条' },
        { title: '授权补齐', desc: '节日素材授权完成后回填至 V2 轨道再锁定终版。', badge: '待授权', tone: 'success', search: '授权 补齐 主时间轴' },
    ];

    const detailCards = [
        { title: '先处理字幕校对', desc: '两条口播超出安全字数，先压缩再锁轨。', badge: '优先', tone: 'warning', search: '先处理 字幕 校对' },
        { title: '跟进素材授权', desc: '节日 B-roll 是当前终版缺口，需要先补授权链路。', badge: '阻塞', tone: 'error', search: '跟进 素材 授权' },
        { title: '合并导出窗口', desc: '校对完成后集中发起多版本导出，避免队列碎片化。', badge: '动作', tone: 'info', search: '合并 导出 窗口' },
    ];

    const detailGroups = [
        { label: '当前批次', value: '视频混剪 #18' },
        { label: '重点风险', value: '节日素材授权未完成，可能阻塞终版导出' },
        { label: '建议动作', value: '先完成字幕校对，再集中发起多版本导出' },
    ];

    const summaryChipsHtml = summaryChips
        .map((chip) => `<article class="workbench-summary-chip" data-search="${chip.search || chip.label}"><span class="subtle">${chip.label}</span><strong>${chip.value}</strong><small>${chip.note}</small></article>`)
        .join('');

    const sideCardsHtml = sideCards
        .map((card) => `<article class="workbench-sidecard" data-search="${card.search || card.title}"><div class="workbench-sidecard__head"><strong>${card.title}</strong><span class="pill ${card.tone}">${card.badge}</span></div><div class="subtle">${card.desc}</div></article>`)
        .join('');

    const queueCardsHtml = queueCards
        .map((card) => `<article class="strip-card" data-search="${card.search || card.title}"><strong>${card.title}</strong><div class="subtle">${card.desc}</div><span class="pill ${card.tone}">${card.badge}</span></article>`)
        .join('');

    const detailCardsHtml = detailCards
        .map((card) => `<article class="workbench-sidecard" data-search="${card.search || card.title}"><div class="workbench-sidecard__head"><strong>${card.title}</strong><span class="pill ${card.tone}">${card.badge}</span></div><div class="subtle">${card.desc}</div></article>`)
        .join('');

    return {
        eyebrow: '视频剪辑工作台',
        searchTerms: '视频剪辑 预览 精剪 字幕 导出',
        sidebarSummary: {
            eyebrow: '剪辑提醒',
            title: '当前序列仍有 2 个未闭环问题',
            copy: '先补字幕校对和素材授权，再锁定终版并发起导出。',
        },
        statusLeft: ['当前序列 #18', '待导出 7', '未闭环问题 2'],
        statusRight: [{ text: '序列编辑中', tone: 'success' }, { text: '终版本未锁定', tone: 'warning' }],
        hideDetailPanel: false,
        mainHtml: `
            <div class="breadcrumbs"><span>creator</span><span>/</span><span>视频剪辑</span></div>
            <div class="page-header">
                <div>
                    <div class="eyebrow">序列剪辑与导出检查</div>
                    <h1>视频剪辑</h1>
                    <p>围绕当前剪辑序列进行预览、精剪、字幕校对和导出检查，主内容区保持剪辑器结构，方便后续 loader 继续接管。</p>
                </div>
                <div class="header-actions">
                    <button class="secondary-button" type="button">切换剪辑序列</button>
                    <button class="primary-button" type="button">发起终版导出</button>
                </div>
            </div>
            <section class="section-stack">
                <div class="workbench-summary-strip">${summaryChipsHtml}</div>
                <div class="content-workbench-shell">
                    <aside class="workbench-rail">
                        <button class="workbench-tool is-selected" type="button" data-search="视频剪辑 剪辑"><span>剪辑</span><small>剪辑</small></button>
                        <button class="workbench-tool" type="button" data-search="视频剪辑 字幕"><span>字幕</span><small>字幕</small></button>
                        <button class="workbench-tool" type="button" data-search="视频剪辑 音频"><span>音频</span><small>音频</small></button>
                        <button class="workbench-tool" type="button" data-search="视频剪辑 导出"><span>导出</span><small>导出</small></button>
                    </aside>
                    <div class="section-stack">
                        <section class="workbench-canvas workbench-canvas--video video-editing-studio">
                            <div class="video-studio-topbar">
                                <div>
                                    <strong>精剪工作区</strong>
                                    <div class="subtle">素材库、节目监视器、时间线和剪辑控制集中在此</div>
                                </div>
                                <div class="toolbar-strip__group">
                                    <button class="secondary-button" type="button">试看导出</button>
                                    <button class="secondary-button" type="button">添加批注</button>
                                </div>
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
                                        <div class="source-thumb is-selected" data-kind="video"><div class="source-thumb__preview source-thumb__preview--video"><span class="source-thumb__dur">00:18</span></div><div class="source-thumb__name">节日 B-roll_03</div><div class="source-thumb__tag"><span class="pill info">产品特写</span></div></div>
                                        <div class="source-thumb" data-kind="image"><div class="source-thumb__preview source-thumb__preview--image"></div><div class="source-thumb__name">春季封面 01</div><div class="source-thumb__tag"><span class="pill success">已授权</span></div></div>
                                        <div class="source-thumb" data-kind="subtitle"><div class="source-thumb__preview source-thumb__preview--subtitle"><span>SRT</span></div><div class="source-thumb__name">核心卖点字幕</div><div class="source-thumb__tag"><span class="pill warning">待校对</span></div></div>
                                        <div class="source-thumb" data-kind="audio"><div class="source-thumb__preview source-thumb__preview--audio"><span>♪</span></div><div class="source-thumb__name">背景音乐 轻快版</div><div class="source-thumb__tag"><span class="pill success">02:15</span></div></div>
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
                                        <div class="video-surface video-surface--editor"><div class="play-button">播放</div></div>
                                    </div>
                                </section>
                            </div>
                        </section>
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
                    </div>
                    <aside class="workbench-sidebar">
                        <section class="panel video-inspector-panel">
                            <div class="panel__header"><div><strong>检查器</strong><div class="subtle">剪辑现场需要处理的素材、字幕和导出事项</div></div></div>
                            <div class="video-inspector-tabs"><span class="is-selected">属性</span><span>字幕</span><span>导出</span></div>
                            <div class="workbench-side-list">${sideCardsHtml}</div>
                            <div class="video-queue-block">
                                <div class="video-queue-block__head"><strong>待办队列</strong><span class="subtle">从上到下按阻塞优先级处理</span></div>
                                <div class="video-queue-list">${queueCardsHtml}</div>
                            </div>
                        </section>
                    </aside>
                </div>
            </section>
        `,
        detailHtml: `
            <div class="detail-root">
                <section class="panel">
                    <div class="panel__header"><div><strong>视频剪辑摘要</strong><div class="subtle">优先处理字幕校对、素材授权与导出队列阻塞</div></div></div>
                    <div class="detail-list">
                        ${detailGroups.map((group) => `<div class="detail-item"><span class="subtle">${group.label}</span><strong>${group.value}</strong></div>`).join('')}
                    </div>
                </section>
                <section class="panel">
                    <div class="panel__header"><div><strong>值班动作</strong><div class="subtle">右侧详情继续承载当前批次的决策提醒</div></div></div>
                    <div class="workbench-side-list">${detailCardsHtml}</div>
                </section>
            </div>
        `,
    };
}

registerContentWorkbenchFactory('video-editor', makeVideoEditorRoute);
