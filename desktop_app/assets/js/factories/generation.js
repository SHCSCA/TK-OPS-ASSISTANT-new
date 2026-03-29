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

function makeAssetCenterRoute(config = {}) {
    return {
        eyebrow: '素材资产库',
        searchTerms: '素材中心 素材分类 素材库 视频 图片 字幕 音频 标签 授权',
        audit: config.audit,
        sidebarSummary: { eyebrow: '素材提醒', title: '素材库存摘要', copy: '加载后根据真实素材库存、账号归属和标签覆盖情况自动更新。' },
        statusLeft: ['素材总量', '未绑定账号', '标签完善率'],
        statusRight: [{ text: '实时汇总', tone: 'info' }, { text: '等待加载', tone: 'warning' }],
        hideDetailPanel: false,
        mainHtml: `
            <div class="breadcrumbs"><span>creator</span><span>/</span><span>素材中心</span></div>
            <div class="page-header">
                <div><div class="eyebrow">内容素材中台</div><h1>素材中心</h1><p>统一查看素材库存、素材分类、授权状态和复用建议，主区直接展示素材，不再只剩说明卡片。</p></div>
            </div>
            <section class="section-stack asset-center-page">
                <div class="stat-grid">
                    <article class="stat-card"><div><div class="subtle">素材库存</div><div class="stat-card__value">2,148</div></div><div class="stat-card__delta" style="color:var(--status-success);"><span>+86</span><span class="subtle">近 7 天持续增长</span></div></article>
                    <article class="stat-card"><div><div class="subtle">未绑定账号</div><div class="stat-card__value">12</div></div><div class="stat-card__delta" style="color:var(--status-warning);"><span>需补充归属</span><span class="subtle">避免后续链路无法追溯</span></div></article>
                    <article class="stat-card"><div><div class="subtle">标签完善率</div><div class="stat-card__value">63%</div></div><div class="stat-card__delta" style="color:var(--brand-primary);"><span>已打标签素材</span><span class="subtle">便于快速检索与批量复用</span></div></article>
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
                                <div class="source-browser-head__actions">
                                    <button class="secondary-button" type="button">批量打标签</button>
                                    <button class="secondary-button" type="button">导入素材</button>
                                </div>
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
                    <article class="template-showcase-card is-highlight"><span class="pill success">待生成</span><strong>悬念钩子型</strong><div class="subtle">制造认知缺口，拉高停留与点击。</div></article>
                    <article class="template-showcase-card"><span class="pill info">待生成</span><strong>利益直给型</strong><div class="subtle">直接抛结果和收益，适合强转化场景。</div></article>
                    <article class="template-showcase-card"><span class="pill warning">待生成</span><strong>认知偏差型</strong><div class="subtle">强调反常识与对比，适合做第二组变体。</div></article>
                </div>
                <section class="panel title-creation-editor">
                    <div class="panel__header"><div><strong>标题编辑区</strong><div class="subtle">输入主标题、标签和钩子方向，避免把解释卡片挤进主操作区</div></div></div>
                    <div class="title-editor-tags"><span># 建议收藏</span><span># 震惊</span><span># 避坑指南</span><span># 深度好文</span></div>
                    <textarea class="title-editor-textarea" placeholder="在此输入或生成你的标题..."></textarea>
                    <div class="title-editor-actions"><span class="subtle">0 / 64 字</span><div class="header-actions"><button class="secondary-button" type="button">插入标签</button><button class="primary-button" type="button">生成新方案</button></div></div>
                </section>
                <div class="title-metric-grid">
                    <article class="mini-metric-card"><span class="subtle">互动率预测</span><strong>--</strong><small>生成后显示预测评分</small></article>
                    <article class="mini-metric-card"><span class="subtle">情感共鸣度</span><strong>--</strong><small>生成后显示共鸣度评估</small></article>
                    <article class="mini-metric-card"><span class="subtle">可读性评分</span><strong>--</strong><small>生成后显示可读性评分</small></article>
                </div>
                <section class="panel title-variant-board">
                    <div class="panel__header"><div><strong>A/B 方案对比</strong><div class="subtle">主区域只保留可比较的候选标题，不再塞入泛说明卡</div></div></div>
                    <div class="variant-list">
                        <article class="variant-card"><div class="variant-card__head"><span class="pill info">等待生成</span><strong>--</strong></div><p>输入内容后点击「生成新方案」获取标题候选。</p><small>生成结果将替换此区域。</small></article>
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
        sidebarSummary: { eyebrow: '提取提醒', title: '等待输入视频地址', copy: '输入视频 URL 后点击「开始提取」，结构结果实时输出到右侧面板。' },
        statusLeft: ['分析模式 混合', '处理进度 0%', '预计剩余 --:--'],
        statusRight: [{ text: '等待输入', tone: 'info' }, { text: '就绪', tone: 'warning' }],
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
                        <div class="form-field extractor-url-field"><label>视频源地址</label><input type="text" placeholder="输入视频 URL 或视频描述..."></div>
                        <div class="form-field"><label>分析模式</label><select><option>混合模式 (ASR + 视觉)</option></select></div>
                        <div class="form-field"><label>关键帧间隔</label><select><option>自动抽帧</option></select></div>
                        <div class="form-field"><label>AI 模型</label><select><option>GPT-4o</option></select></div>
                    </div>
                </section>
                <div class="extractor-workspace">
                    <aside class="extractor-preview-column">
                        <section class="panel extractor-preview-panel"><div class="panel__header"><div><strong>视频预览</strong><div class="subtle">左侧固定展示当前进度与视频摘要</div></div></div><div class="extractor-video-stage"><div class="play-button">播放</div></div><div class="extractor-progress-row"><span class="subtle">等待输入视频</span><strong>0%</strong></div><div class="progress-bar"><span style="width:0%"></span></div><div class="extractor-stat-grid"><article><span class="subtle">预计剩余</span><strong>--:--</strong></article><article><span class="subtle">已用时长</span><strong>--:--</strong></article></div></section>
                        <section class="panel"><div class="panel__header"><div><strong>AI 实时摘要</strong><div class="subtle">把阶段性结论收成一块短摘要</div></div></div><p class="subtle">输入视频地址后，AI 将自动输出阶段性结构摘要。</p></section>
                    </aside>
                    <div class="extractor-results-column">
                        <section class="panel"><div class="panel__header"><div><strong>提取结果</strong><div class="subtle">右侧主区只保留结果标签、时间轴和内容表格</div></div><div class="extractor-tabs"><span class="is-selected">脚本文案</span><span>视频关键帧</span><span>视觉分析</span></div></div><div class="extractor-result-table"><div class="extractor-result-row"><span>--:--:--</span><div><strong>[等待提取]</strong><p>输入视频地址后点击「开始提取」，结果将在此显示。</p></div><em>--%</em></div></div></section>
                        <section class="panel"><div class="panel__header"><div><strong>衍生能力</strong><div class="subtle">底部保留真正可继续执行的后续动作</div></div></div><div class="extractor-capability-grid"><article class="strip-card"><strong>结构摘要</strong><div class="subtle">自动输出钩子、转折、CTA 三段结构。</div><span class="pill info">提取后可用</span></article><article class="strip-card"><strong>镜头拆解</strong><div class="subtle">按关键帧分解镜头用途和节奏变化。</div><span class="pill info">提取后可用</span></article><article class="strip-card" data-route-link="ai-copywriter" data-route-toast="已跳转到 AI 文案生成"><strong>脚本回写</strong><div class="subtle">提取结果可直接回传到 AI 文案生成页继续改写。</div><span class="pill warning">下一步 →</span></article></div></section>
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
        sidebarSummary: { eyebrow: '优化提醒', title: '等待输入商品名称', copy: '输入商品名称后点击「立即优化」，生成兼顾 SEO 和点击率的标题方案。' },
        statusLeft: ['核心词 --', '当前行业 --', '生成方案 0'],
        statusRight: [{ text: '等待优化', tone: 'info' }, { text: '就绪', tone: 'warning' }],
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
                        <section class="panel product-saved-card"><div class="panel__header"><div><strong>优化历史</strong><div class="subtle">展示最近生成的标题记录</div></div></div><strong class="product-saved-value">--</strong><p class="subtle">输入商品名称后点击「立即优化」获取方案。</p></section>
                    </aside>
                    <div class="product-main-column">
                        <section class="panel product-input-panel"><div class="panel__header"><div><strong>输入原始商品名称</strong><div class="subtle">先锁定原始商品名、品类和卖点，再展开下游分析</div></div></div><div class="product-input-row"><input type="text" placeholder="输入商品名称..."><button class="primary-button" type="button">立即优化</button></div><div class="product-chip-row"><span>快速生成</span><span>高点击率</span><span>合规检测</span></div></section>
                        <div class="product-insight-grid">
                            <section class="panel"><div class="panel__header"><div><strong>关键词密度建议</strong><div class="subtle">当前最该看的不是大段解释，而是词层级分布</div></div></div><div class="metric-kv"><div class="detail-item"><span class="subtle">核心词</span><strong>--</strong></div><div class="detail-item"><span class="subtle">属性词</span><strong>--</strong></div><div class="detail-item"><span class="subtle">修饰词</span><strong>--</strong></div></div></section>
                            <section class="panel"><div class="panel__header"><div><strong>竞品 TOP 标题</strong><div class="subtle">看竞品结构，而不是堆更多提示卡</div></div></div><div class="workbench-side-list"><article class="workbench-sidecard"><strong>竞品 A</strong><div class="subtle">优化后自动显示竞品参考。</div></article><article class="workbench-sidecard"><strong>竞品 B</strong><div class="subtle">优化后自动显示竞品参考。</div></article></div></section>
                        </div>
                        <section class="panel"><div class="panel__header"><div><strong>行业专属模板</strong><div class="subtle">这里保留模板入口，避免混在顶部工具区</div></div></div><div class="product-template-grid"><article class="template-card is-active"><strong>服饰内衣</strong><small>当前激活</small></article><article class="template-card"><strong>数码家电</strong><small>切换模板</small></article><article class="template-card"><strong>美妆护肤</strong><small>切换模板</small></article><article class="template-card"><strong>食品饮料</strong><small>切换模板</small></article></div></section>
                        <section class="panel product-result-board"><div class="panel__header"><div><strong>AI 生成标题方案</strong><div class="subtle">主区只保留最终候选结果</div></div></div><div class="variant-list"><article class="variant-card"><div class="variant-card__head"><span class="pill info">等待优化</span><strong>--</strong></div><p>输入商品名称后点击「立即优化」获取高转化和 SEO 两类方案。</p><small>生成结果将替换此区域。</small></article></div></section>
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
        sidebarSummary: { eyebrow: '文案提醒', title: '等待生成文案', copy: '选择风格、填写产品信息后点击「立即生成」，右侧合规区实时显示风险评估。' },
        statusLeft: ['写作风格 专业严谨', '文案长度 300 字', '合规分 --'],
        statusRight: [{ text: '等待生成', tone: 'info' }, { text: '就绪', tone: 'warning' }],
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
                        <section class="panel"><div class="panel__header"><div><strong>生成参数设置</strong><div class="subtle">输入关键词、风格和长度</div></div></div><div class="form-field"><label>产品关键词</label><textarea placeholder="请输入产品名称、核心卖点或描述..."></textarea></div><div class="copy-tone-list"><button class="is-active">专业严谨</button><button>亲切随性</button><button>幽默风趣</button></div><div class="form-field"><label>文案长度</label><input type="range" min="100" max="1000" value="300"></div></section>
                    </aside>
                    <div class="copy-results-column">
                        <section class="panel"><div class="panel__header"><div><strong>输出版本</strong><div class="subtle">把标题推荐、文案脚本和热门话题放在同一结果容器内切换</div></div><div class="extractor-tabs"><span class="is-selected">标题推荐</span><span>文案脚本</span><span>热门话题</span></div></div><div class="variant-list"><article class="variant-card"><div class="variant-card__head"><span class="pill info">等待生成</span><strong>--</strong></div><p>填写产品信息后点击「立即生成文案」获取多版本输出。</p><small>生成结果将替换此区域。</small></article></div></section>
                        <section class="panel"><div class="panel__header"><div><strong>继续创作</strong><div class="subtle">把下一步动作放在底部而不是侧边重复说明</div></div></div><div class="copy-action-grid"><article class="strip-card"><strong>继续扩写</strong><div class="subtle">补正文案脚本和口播版本。</div><span class="pill info">生成后可用</span></article><article class="strip-card"><strong>切换渠道</strong><div class="subtle">改成商品详情页或短视频开场。</div><span class="pill info">生成后可用</span></article><article class="strip-card"><strong>生成话题</strong><div class="subtle">从当前版本延展热词与标签。</div><span class="pill info">生成后可用</span></article></div></section>
                    </div>
                    <aside class="copy-compliance-column">
                        <section class="panel"><div class="panel__header"><div><strong>合规自检报告</strong><div class="subtle">右列只承接风险分、风险词和改写建议</div></div></div><div class="copy-score-card"><strong>--</strong><small>等待生成</small></div><div class="metric-kv"><div class="detail-item"><span class="subtle">违规词</span><strong>--</strong></div><div class="detail-item"><span class="subtle">敏感词</span><strong>--</strong></div></div><div class="workbench-side-list"><article class="workbench-sidecard"><strong>风险词</strong><div class="subtle">生成后自动显示风险评估。</div></article></div><button class="secondary-button" type="button">导出合规报告</button></section>
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
                { label: '当前供应商', value: '等待接入' },
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
