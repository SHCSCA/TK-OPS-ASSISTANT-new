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
    'device-management': makeDeviceManagementRoute(),
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
            { title: '下一步 →', desc: '锁定胜出主题后，交给视频剪辑页生成 15 秒与 30 秒双版本。', badge: '移交生产', tone: 'info', search: '创意 下一步 移交 生产', routeLink: 'video-editor' },
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
    'version-upgrade': {
        eyebrow: '版本升级中心',
        searchTerms: '版本升级 更新 update version upgrade 检查 下载 安装',
        sidebarSummary: { eyebrow: '系统版本', title: '版本检测与管理', copy: '检查最新版本、查看更新日志、下载与安装新版。' },
        statusLeft: ['版本检测中…'],
        statusRight: [{ text: '检测中', tone: 'warning' }],
        mainHtml: '\
<div class="breadcrumbs"><span>system</span><span>/</span><span>版本升级</span></div>\
<div class="page-header">\
  <div><div class="eyebrow">版本检测与升级管理</div><h1>版本升级</h1><p>检查最新版本、查看更新日志并一键升级。</p></div>\
  <div class="header-actions"><button class="primary-button" type="button" id="btnCheckUpdate">检查更新</button></div>\
</div>\
<section class="section-stack">\
  <div class="stat-grid">\
    <article class="stat-card"><div><div class="subtle">当前版本</div><div class="stat-card__value" id="verCurrent">—</div></div><div class="stat-card__delta" style="color:var(--brand-primary);"><span>运行中</span></div></article>\
    <article class="stat-card"><div><div class="subtle">最新版本</div><div class="stat-card__value" id="verLatest">—</div></div><div class="stat-card__delta" id="verDelta" style="color:var(--status-success);"><span>检查中…</span></div></article>\
    <article class="stat-card"><div><div class="subtle">更新状态</div><div class="stat-card__value" id="verStatus">待检查</div></div><div class="stat-card__delta" id="verStatusNote"><span>&nbsp;</span></div></article>\
  </div>\
  <div class="update-content-grid">\
    <section class="panel update-main-panel">\
      <div class="panel__header"><div><strong>更新信息</strong><div class="subtle" id="updateSubtitle">点击「检查更新」获取最新版本</div></div></div>\
      <div id="updateBody" class="update-body">\
        <div class="update-placeholder"><span class="shell-icon">↻</span><p>暂无更新信息</p></div>\
      </div>\
      <div id="updateActions" class="update-actions" style="display:none;">\
        <div id="downloadProgressWrap" class="download-progress-wrap" style="display:none;">\
          <div class="download-progress-bar"><div class="download-progress-fill" id="downloadFill"></div></div>\
          <div class="download-progress-text"><span id="downloadPercent">0%</span><span id="downloadSpeed"></span><span id="downloadSize"></span></div>\
        </div>\
        <div class="update-action-buttons">\
          <button class="primary-button" id="btnDownload" style="display:none;">下载更新</button>\
          <button class="primary-button" id="btnApply" style="display:none;">安装并重启</button>\
          <a id="btnReleasePage" href="#" target="_blank" class="secondary-button" style="display:none;">查看发布页</a>\
        </div>\
      </div>\
    </section>\
    <aside class="update-side-panel">\
      <section class="panel"><div class="panel__header"><div><strong>版本历史</strong><div class="subtle">近期发布记录</div></div></div>\
        <div id="versionHistory" class="board-list"><div class="subtle" style="padding:1rem;">检查更新后显示</div></div>\
      </section>\
      <section class="panel"><div class="panel__header"><div><strong>环境信息</strong><div class="subtle">运行时参数</div></div></div>\
        <div id="envInfo" class="detail-list"></div>\
      </section>\
    </aside>\
  </div>\
</section>',
        detailHtml: '<div class="detail-root"><section class="panel"><div class="panel__header"><div><strong>版本详情</strong><div class="subtle">当前运行版本信息</div></div></div><div class="detail-list"><div class="detail-item"><span class="subtle">当前版本</span><strong id="detailVerCurrent">—</strong></div><div class="detail-item"><span class="subtle">更新状态</span><strong id="detailVerStatus">待检查</strong></div></div></section></div>',
    },
    'visual-editor': makeContentWorkbenchRoute({
        breadcrumb: 'creator', eyebrow: '视觉编辑工作台', headerEyebrow: '图文排版与封面合成',
        title: '视觉编辑器', description: '封面、图文卡片和素材拼合的可视化编辑台，支持模板套用和多尺寸导出。',
        primaryAction: '导出当前设计', secondaryAction: '切换模板',
        workbenchType: 'visual-editor',
        summaryChips: [
            { label: '当前画布', value: '1080×1920 竖版封面', note: '基于高点击模板', search: '画布 竖版 封面' },
            { label: '待审稿', value: '3 张', note: '配色和字号需确认', search: '待审稿 3 张' },
            { label: '导出队列', value: '5 张排队', note: '批量导出完成约 2 分钟', search: '导出 队列 5' },
        ],
        railTools: [
            { icon: '画布', label: '画布', search: '视觉编辑器 画布' },
            { icon: '文字', label: '文字', search: '视觉编辑器 文字' },
            { icon: '贴纸', label: '贴纸', search: '视觉编辑器 贴纸' },
            { icon: '导出', label: '导出', search: '视觉编辑器 导出' },
        ],
        sideCards: [
            { title: '封面配色待调整', desc: '主色与品牌色偏差超过 15%，建议同步。', badge: '待调', tone: 'warning', search: '封面 配色 调整' },
            { title: '文字层级清晰', desc: '标题、副标题和行动号召层级合理。', badge: '已确认', tone: 'success', search: '文字 层级' },
        ],
        bottomCards: [
            { title: '模板草稿 A', desc: '极简风格，适合品牌向内容。', badge: '草稿', tone: 'info', search: '模板 草稿 A' },
            { title: '模板草稿 B', desc: '促销风格，适合大促场景。', badge: '草稿', tone: 'warning', search: '模板 草稿 B' },
        ],
        detailCards: [
            { title: '优先校正配色', desc: '当前主色偏暖，与品牌指南有差距。', badge: '优先', tone: 'warning', search: '校正 配色' },
            { title: '多尺寸导出', desc: '确认后一键导出 3 个尺寸。', badge: '动作', tone: 'info', search: '多尺寸 导出' },
        ],
        detailDesc: '确认配色和排版后批量导出。',
        detailGroups: [{ label: '设计稿', value: '竖版封面 v3' }, { label: '风险', value: '配色偏差' }],
        sidebarSummary: { eyebrow: '设计提醒', title: '3 张待审稿', copy: '先校正配色再批量导出。' },
        statusLeft: ['画布 1080×1920', '待审 3', '导出排队 5'],
        statusRight: [{ text: '编辑中', tone: 'success' }, { text: '配色待调', tone: 'warning' }],
    }),
    'license-issuer': makeLicenseIssuerRoute(),
    'permission-management': makeConfigCenterRoute({
        breadcrumb: 'system', eyebrow: '权限与角色管理', headerEyebrow: '访问控制与操作审计',
        title: '权限管理', description: '管理角色、功能权限和操作审计日志，确保多人协作时数据安全可控。',
        primaryAction: '新建角色', secondaryAction: '导出审计日志',
        configType: 'settings',
        navSections: [
            { label: '角色', icon: '👤', search: '角色 管理' },
            { label: '权限矩阵', icon: '🔐', search: '权限 矩阵 功能' },
            { label: '审计日志', icon: '📋', search: '审计 日志 操作' },
        ],
        formGroups: [
            { title: '角色列表', desc: '系统内置和自定义角色', fields: [
                { label: '管理员', value: '全部权限', hint: '不可编辑', search: '管理员 全部权限' },
                { label: '运营', value: '账号+任务+内容', hint: '默认角色', search: '运营 默认角色' },
                { label: '只读', value: '仅查看', hint: '适合外部协作', search: '只读 外部协作' },
            ]},
            { title: '功能权限', desc: '按模块配置读写权限', fields: [
                { label: '账号模块', type: 'select', value: '读写', search: '账号 读写' },
                { label: '任务模块', type: 'select', value: '读写', search: '任务 读写' },
                { label: 'AI 模块', type: 'select', value: '只读', search: 'AI 只读' },
                { label: '系统设置', type: 'select', value: '禁止', search: '系统 禁止' },
            ]},
        ],
        detailTitle: '权限说明', detailDesc: '当前角色的权限范围和变更记录',
        detailGroups: [{ label: '当前角色', value: '运营' }, { label: '最近变更', value: '今天 14:20' }],
        detailCards: [
            { title: '避免给外部角色写权限', desc: '只读角色不应有任何修改操作。', badge: '安全', tone: 'warning', search: '外部 只读 安全' },
            { title: '审计日志保留 90 天', desc: '超过 90 天的日志自动归档。', badge: '提示', tone: 'info', search: '审计 90 天' },
        ],
        sidebarSummary: { eyebrow: '权限状态', title: '3 个角色正常运行', copy: '建议定期复核外部协作角色权限。' },
        statusLeft: ['角色 3', '审计日志 1204 条', '最近变更 14:20'],
        statusRight: [{ text: '权限正常', tone: 'success' }],
    }),
    'operations-center': makeListManagementRoute({
        breadcrumb: 'ops', eyebrow: '运营排期中台', headerEyebrow: '资源协调与排期总览',
        title: '运营中心', description: '统一协调账号、素材、任务和人力资源，让运营排期有全局视角。',
        primaryAction: '新建排期', secondaryAction: '导出周报',
        listTitle: '本周重点排期', listDesc: '按优先级排序的运营事项。',
        sideTitle: '协调建议', sideDesc: '资源冲突与风险提示。',
        sideStats: ['排期 24 项', '冲突 3 项', '本周完成率 82%'],
        metrics: [
            { label: '排期总数', value: '24', delta: '+6', note: '本周新增 6 项', color: 'var(--status-success)', search: '排期 24' },
            { label: '资源冲突', value: '3', delta: '待协调', note: '账号和素材存在重叠使用', color: 'var(--status-warning)', search: '资源冲突 3' },
            { label: '完成率', value: '82%', delta: '+5%', note: '高于上周同期', color: 'var(--brand-primary)', search: '完成率 82' },
        ],
        items: [
            { title: '美国站大促排期', desc: '素材、账号、发布计划已就绪。', badge: '就绪', tone: 'success', search: '美国 大促 就绪' },
            { title: '日本站内容补量', desc: '缺 2 条视频素材，需协调创意工坊。', badge: '缺素材', tone: 'warning', search: '日本 内容 缺素材' },
            { title: '德国站账号修复', desc: '3 个异常账号阻塞发布计划。', badge: '阻塞', tone: 'error', search: '德国 账号 阻塞' },
        ],
        detailDesc: '运营排期的全局协调和风险管控。',
        detailItems: ['24 项排期运行中', '3 项资源冲突待协调', '先修复阻塞项再推进'],
        sidebarSummary: { eyebrow: '运营提醒', title: '3 项资源冲突', copy: '建议先处理德国站账号阻塞，再协调素材资源。' },
        statusLeft: ['排期 24', '冲突 3', '完成率 82%'],
        statusRight: [{ text: '大部分正常', tone: 'success' }, { text: '冲突 3', tone: 'warning' }],
    }),
    'order-management': makeListManagementRoute({
        breadcrumb: 'ops', eyebrow: '订单处理中心', headerEyebrow: '订单跟踪与异常排查',
        title: '订单管理', description: '统一查看订单状态、异常单详情和退款进度，快速定位问题订单。',
        primaryAction: '导出订单', secondaryAction: '筛选异常单',
        listTitle: '异常订单', listDesc: '优先处理超时和争议订单。',
        sideTitle: '处理建议', sideDesc: '异常订单的优先处理顺序。',
        sideStats: ['今日订单 328 笔', '异常 12 笔', '退款率 2.1%'],
        metrics: [
            { label: '今日订单', value: '328', delta: '+42', note: '较昨日增长', color: 'var(--status-success)', search: '今日 订单 328' },
            { label: '异常订单', value: '12', delta: '待处理', note: '超时和争议订单', color: 'var(--status-error)', search: '异常 订单 12' },
            { label: '退款率', value: '2.1%', delta: '-0.3%', note: '低于行业平均', color: 'var(--brand-primary)', search: '退款率 2.1' },
        ],
        items: [
            { title: '物流超时 #ORD-2847', desc: '已超出承诺时效 48 小时。', badge: '超时', tone: 'error', search: '物流 超时 ORD-2847' },
            { title: '买家争议 #ORD-2831', desc: '商品描述不符，待客服跟进。', badge: '争议', tone: 'warning', search: '买家 争议 ORD-2831' },
            { title: '退款审批 #ORD-2819', desc: '已通过自动审核，等待财务确认。', badge: '审批中', tone: 'info', search: '退款 审批 ORD-2819' },
        ],
        detailDesc: '快速定位和处理异常订单。',
        detailItems: ['328 笔订单正常流转', '12 笔异常待处理', '先处理超时订单'],
        sidebarSummary: { eyebrow: '订单提醒', title: '12 笔异常订单', copy: '优先处理物流超时单，再跟进买家争议。' },
        statusLeft: ['订单 328', '异常 12', '退款率 2.1%'],
        statusRight: [{ text: '大部分正常', tone: 'success' }, { text: '异常 12', tone: 'error' }],
    }),
    'service-center': makeListManagementRoute({
        breadcrumb: 'ops', eyebrow: '客服工单中心', headerEyebrow: '工单管理与规则联动',
        title: '客服中心', description: '统一管理客服工单、自动分配规则和响应时效，提升客户满意度。',
        primaryAction: '创建工单', secondaryAction: '查看 SLA 报告',
        listTitle: '待处理工单', listDesc: '按紧急程度排序的工单。',
        sideTitle: '响应建议', sideDesc: '改善响应时效的优化方向。',
        sideStats: ['活跃工单 45 个', '超时 7 个', '满意度 4.2/5'],
        metrics: [
            { label: '活跃工单', value: '45', delta: '+8', note: '今日新增 8 个', color: 'var(--status-success)', search: '活跃 工单 45' },
            { label: '超时工单', value: '7', delta: '需加速', note: '超出 SLA 响应时限', color: 'var(--status-error)', search: '超时 工单 7' },
            { label: '满意度', value: '4.2', delta: '+0.1', note: '近 7 天评分', color: 'var(--brand-primary)', search: '满意度 4.2' },
        ],
        items: [
            { title: '物流投诉 #CS-1024', desc: '买家已等待 72 小时，需优先处理。', badge: '紧急', tone: 'error', search: '物流 投诉 CS-1024' },
            { title: '退换货 #CS-1018', desc: '已生成退货标签，等待买家寄回。', badge: '跟进', tone: 'warning', search: '退换货 CS-1018' },
            { title: '咨询 #CS-1032', desc: '产品使用咨询，可自动回复处理。', badge: '低优', tone: 'info', search: '咨询 CS-1032' },
        ],
        detailDesc: '优先消化超时工单，提升整体SLA。',
        detailItems: ['45 个工单运行中', '7 个超时待加速', '满意度稳步提升'],
        sidebarSummary: { eyebrow: '客服提醒', title: '7 个超时工单', copy: '优先处理物流投诉类工单，防止升级。' },
        statusLeft: ['工单 45', '超时 7', '满意度 4.2'],
        statusRight: [{ text: '服务正常', tone: 'success' }, { text: '超时 7', tone: 'error' }],
    }),
    'refund-processing': makeListManagementRoute({
        breadcrumb: 'ops', eyebrow: '退款审批中心', headerEyebrow: '退款流程与财务对账',
        title: '退款处理', description: '集中管理退款申请、审批流程和财务对账，确保退款准确及时。',
        primaryAction: '批量审批', secondaryAction: '导出对账单',
        listTitle: '待审批退款', listDesc: '按金额和紧急度排序。',
        sideTitle: '审批建议', sideDesc: '大额退款需二次确认。',
        sideStats: ['待审批 18 笔', '今日已审 42 笔', '总金额 ¥12,480'],
        metrics: [
            { label: '待审批', value: '18', delta: '+5', note: '新增 5 笔待处理', color: 'var(--status-warning)', search: '待审批 18' },
            { label: '今日已审', value: '42', delta: '正常', note: '处理速度达标', color: 'var(--status-success)', search: '今日 已审 42' },
            { label: '退款总额', value: '¥12,480', delta: '-8%', note: '较上周下降', color: 'var(--brand-primary)', search: '退款 总额 12480' },
        ],
        items: [
            { title: '大额退款 #RF-0892', desc: '金额 ¥2,800，需主管二次审批。', badge: '大额', tone: 'error', search: '大额 退款 RF-0892' },
            { title: '批量退款 #RF-0888', desc: '促销活动集中退款 12 笔。', badge: '批量', tone: 'warning', search: '批量 退款 RF-0888' },
            { title: '常规退款 #RF-0895', desc: '已自动审核，等待打款。', badge: '自动', tone: 'success', search: '常规 退款 RF-0895' },
        ],
        detailDesc: '确保退款流程合规，大额退款需人工复核。',
        detailItems: ['18 笔待审批', '42 笔已完成', '大额退款需二次确认'],
        sidebarSummary: { eyebrow: '退款提醒', title: '18 笔待审批', copy: '优先处理大额退款，避免超时。' },
        statusLeft: ['待审 18', '已审 42', '总额 ¥12,480'],
        statusRight: [{ text: '大部分正常', tone: 'success' }, { text: '大额 1 笔', tone: 'error' }],
    }),
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

