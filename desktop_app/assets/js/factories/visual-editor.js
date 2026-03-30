const VISUAL_EDITOR_CONFIG = {
    eyebrow: '视觉模板工作台',
    headerEyebrow: '封面、图文卡片与模板排版',
    title: '视觉模板编辑器',
    description: '围绕封面、图文卡片和模板拼版进行编辑与导出，不再混入时间线剪辑器的布局。',
    primaryAction: '导出当前设计',
    secondaryAction: '切换模板',
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
        { title: '优先校正配色', desc: '当前主色偏暖，与品牌指南有偏差。', badge: '优先', tone: 'warning', search: '校正 配色' },
        { title: '多尺寸导出', desc: '确认后一次性导出 3 个尺寸。', badge: '动作', tone: 'info', search: '多尺寸 导出' },
    ],
    detailDesc: '确认配色和排版后批量导出。',
    detailGroups: [{ label: '设计稿', value: '竖版封面 v3' }, { label: '风险', value: '配色偏差' }],
    sidebarSummary: { eyebrow: '设计提醒', title: '3 张待审稿', copy: '先校正配色再批量导出。' },
    statusLeft: ['画布 1080×1920', '待审 3', '导出队列 5'],
    statusRight: [{ text: '编辑中', tone: 'success' }, { text: '配色待调', tone: 'warning' }],
};

function makeVisualEditorRoute() {
    return makeContentWorkbenchRoute(VISUAL_EDITOR_CONFIG);
}
