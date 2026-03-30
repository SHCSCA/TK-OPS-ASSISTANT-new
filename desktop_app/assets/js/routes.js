const routes = {
    dashboard: {
        eyebrow: '仪表盘工作台',
        searchTerms: '概览数据看板 dashboard KPI 任务 趋势 系统健康 活动流',
        mainTemplate: 'route-dashboard-main',
        detailTemplate: 'route-dashboard-detail-default',
        audit: {
            scope: 'dashboard',
            interactions: ['create', 'detail', 'filter', 'navigate'],
        },
        sidebarSummary: {
            eyebrow: '今日重点',
            title: '实时运行摘要',
            copy: '加载后根据账号、任务、设备、素材和供应商状态自动更新。',
        },
        statusLeft: ['账号状态', '任务状态', '设备状态'],
        statusRight: [
            { text: '实时汇总', tone: 'info' },
            { text: '等待加载', tone: 'warning' },
        ],
    },
    account: {
        eyebrow: '账号运营工作台',
        searchTerms: '账号管理 account cookie 代理 登录 环境 隔离',
        mainTemplate: 'route-account-main',
        detailTemplate: 'route-account-detail-default',
        audit: {
            scope: 'account',
            interactions: ['create', 'edit', 'delete', 'detail', 'filter', 'batch', 'task'],
        },
        sidebarSummary: {
            eyebrow: '当前提醒',
            title: '账号状态摘要',
            copy: '加载后根据真实账号列表与状态统计自动更新。',
        },
        statusLeft: ['账号总量', '在线账号', '异常账号'],
        statusRight: [
            { text: '实时汇总', tone: 'info' },
            { text: '等待加载', tone: 'warning' },
        ],
    },
    'ai-provider': {
        eyebrow: 'AI 供应商配置中心',
        searchTerms: 'AI 供应商配置 provider 模型 key 路由 测试',
        mainTemplate: 'route-ai-provider-main',
        detailTemplate: 'route-ai-provider-detail-default',
        audit: {
            scope: 'ai-provider',
            interactions: ['create', 'edit', 'activate', 'delete', 'detail'],
        },
        sidebarSummary: {
            eyebrow: '配置建议',
            title: '供应商配置摘要',
            copy: '加载后根据真实供应商配置、启用状态和默认模型自动更新。',
        },
        statusLeft: ['供应商总量', '启用供应商', '默认模型'],
        statusRight: [
            { text: '实时汇总', tone: 'info' },
            { text: '等待加载', tone: 'warning' },
        ],
    },
    'task-queue': {
        eyebrow: '任务调度中心',
        searchTerms: '任务队列 task queue 运行中 排队 异常 调度',
        mainTemplate: 'route-task-queue-main',
        detailTemplate: 'route-task-queue-detail-default',
        audit: {
            scope: 'task-queue',
            interactions: ['create', 'edit', 'start', 'complete', 'delete', 'filter', 'batch', 'detail'],
        },
        sidebarSummary: {
            eyebrow: '队列摘要',
            title: '任务队列摘要',
            copy: '加载后根据真实任务状态与队列分布自动更新。',
        },
        statusLeft: ['任务总量', '运行中任务', '排队任务'],
        statusRight: [
            { text: '实时汇总', tone: 'info' },
            { text: '等待加载', tone: 'warning' },
        ],
    },
    'device-management': makeDeviceManagementRoute({
        audit: {
            scope: 'device-management',
            interactions: ['create', 'edit', 'delete', 'filter', 'detail', 'batch'],
        },
    }),
    'asset-center': makeAssetCenterRoute({
        audit: {
            scope: 'asset-center',
            interactions: ['create', 'edit', 'delete', 'filter', 'detail'],
        },
    }),
    'video-editor': makeVideoEditorRoute(),
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
            { label: '当前实验', value: '等待实验项目回填', note: '加载后根据真实实验项目名称与状态自动更新', search: '当前 实验 等待 回填' },
            { label: '待决策', value: '等待任务反馈汇总', note: '加载后根据真实任务与活动记录自动更新', search: '待决策 任务 反馈 汇总' },
            { label: '保留倾向', value: '等待素材与结果判断', note: '优先显示真实素材覆盖度与实验状态', search: '保留 倾向 素材 结果' },
        ],
        railTools: [
            { icon: '主题', label: '主题', search: '创意工坊 主题' },
            { icon: '镜头', label: '镜头', search: '创意工坊 镜头' },
            { icon: '口播', label: '口播', search: '创意工坊 口播' },
            { icon: '导出', label: '导出', search: '创意工坊 导出' },
        ],
        focusCards: [
            { title: '实验主视角', desc: '加载后根据真实实验项目、账号地区和任务反馈回填当前主视角。', badge: '实验', tone: 'success', size: 'wide', meta: '不再固定写死示例方案名', search: '实验 主视角 回填' },
            { title: '素材覆盖', desc: '加载后根据真实素材数量、类型和可复用情况评估可执行性。', badge: '素材', tone: 'warning', meta: '优先基于真实素材库存决定下一步', search: '素材 覆盖 评估' },
            { title: '任务反馈', desc: '加载后根据真实任务完成、失败和待处理状态显示当前反馈。', badge: '任务', tone: 'info', meta: '优先观察失败任务是否阻塞创意推进', search: '任务 反馈 状态' },
            { title: '执行建议', desc: '加载后根据真实任务与素材状态决定是否继续对比或下发。', badge: '建议', tone: 'success', meta: '建议动作由运行时数据决定', search: '执行 建议 运行时' },
        ],
        sideCards: [
            { title: '实验判定', desc: '加载后根据真实项目与任务结果回填当前判定。', badge: '等待回填', tone: 'success', search: '实验 判定 回填' },
            { title: '风险检查', desc: '加载后根据失败任务与素材缺口显示真实阻塞点。', badge: '待检查', tone: 'warning', search: '风险 检查 阻塞' },
            { title: '下一步 →', desc: '锁定胜出方向后，再交给视频剪辑页继续加工和导出。', badge: '移交生产', tone: 'info', search: '创意 下一步 移交 生产', routeLink: 'video-editor' },
        ],
        bottomCards: [
            { title: '已保存实验', desc: '加载后显示真实已保存实验或实验视图记录。', badge: '实验', tone: 'success', search: '已保存 实验 记录' },
            { title: '待验证项', desc: '加载后显示真实待处理任务或素材缺口。', badge: '待试', tone: 'warning', search: '待验证 任务 素材' },
            { title: '复盘记录', desc: '加载后显示真实活动日志中的创意复盘记录。', badge: '复盘', tone: 'info', search: '复盘 活动 日志' },
        ],
        detailCards: [
            { title: '先看失败任务', desc: '优先确认是否存在失败任务阻塞当前实验推进。', badge: '优先', tone: 'warning', search: '先看 失败 任务' },
            { title: '核对素材缺口', desc: '优先确认素材覆盖是否足够支撑下一轮实验。', badge: '风险', tone: 'error', search: '核对 素材 缺口' },
            { title: '输出下一步', desc: '确认无阻塞后再下发到剪辑页或后续工作流。', badge: '动作', tone: 'info', search: '输出 下一步 工作流' },
        ],
        detailDesc: '优先确认当前保留方案、主要冲突点和下一轮对比目标。',
        detailGroups: [
            { label: '当前实验状态', value: '等待真实项目与任务回填' },
            { label: '重点风险', value: '加载后根据失败任务和素材缺口自动更新' },
            { label: '建议动作', value: '加载后根据真实结果决定是否进入视频剪辑页' },
        ],
        sidebarSummary: { eyebrow: '创意提醒', title: '等待真实创意实验汇总', copy: '该页面只展示真实实验项目、素材和任务反馈，不再写死示例方案。' },
        statusLeft: ['等待数据接入', '创意状态动态刷新', '无静态方案名'],
        statusRight: [{ text: '后端驱动', tone: 'success' }, { text: '等待刷新', tone: 'warning' }],
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
    'visual-editor': makeVisualEditorRoute(),
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
    const state = summary || { eyebrow: '', title: '', copy: '' };
    document.getElementById('sidebarSummary').innerHTML = `
        <div class="eyebrow">${state.eyebrow || ''}</div>
        <strong id="sidebarSummaryTitle">${state.title || ''}</strong>
        <p class="sidebar__footer-copy" id="sidebarSummaryCopy">${state.copy || ''}</p>
    `;
}

function renderStatus(route) {
    const left = (route && route.statusLeft) || [];
    const right = (route && route.statusRight) || [];
    document.getElementById('statusLeft').innerHTML = left.map((text) => `<span class="status-text">${text}</span>`).join('');
    document.getElementById('statusRight').innerHTML = right.map((item) => `<span class="status-chip ${item.tone}">${item.text}</span>`).join('');
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

