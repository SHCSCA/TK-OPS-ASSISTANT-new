/* ── factories/video-editor.js ─ 视频剪辑路由工厂 ──
   从 factories/content.js 拆出 video-editor 专属工厂逻辑。
   ──────────────────────────────────────────────── */
(function () {
    'use strict';

    window.makeVideoEditorRoute = function makeVideoEditorRoute() {
        return {
            eyebrow: '视频剪辑工作台',
            searchTerms: '视频剪辑 预览 精剪 字幕 导出',
            sidebarSummary: {
                eyebrow: '剪辑提醒',
                title: '正在加载当前工程摘要',
                copy: '稍后会根据当前项目、序列和导出校验同步真实状态。',
            },
            statusLeft: ['等待工程', '等待序列', '等待校验'],
            statusRight: [{ text: '正在同步', tone: 'info' }, { text: '等待导出校验', tone: 'warning' }],
            hideDetailPanel: false,
            mainHtml: '\
            <div class="breadcrumbs"><span>creator</span><span>/</span><span>视频剪辑</span></div>\
            <div class="page-header">\
                <div>\
                    <div class="eyebrow">轻量视频剪辑</div>\
                    <h1>视频剪辑</h1>\
                    <p class="js-video-project-copy">当前工程加载中，稍后会同步序列、时间轴与导出状态。</p>\
                    <div class="video-editor-project-meta js-video-project-meta"><span class="pill info">等待工程</span></div>\
                </div>\
                <div class="header-actions">\
                    <button class="secondary-button js-switch-video-sequence" type="button">切换剪辑序列</button>\
                    <button class="primary-button js-export-final" type="button">发起终版导出</button>\
                </div>\
            </div>\
            <section class="section-stack">\
                <div class="content-workbench-shell content-workbench-shell--main-only">\
                    <div class="section-stack">\
                        <section class="workbench-canvas workbench-canvas--video video-editing-studio">\
                            <div class="video-monitor-grid" data-search="视频剪辑 素材预览 节目监视器 播放器">\
                                <section class="source-browser-shell source-browser-shell--video-editor">\
                                    <div class="source-browser-head">\
                                        <div>\
                                            <strong>当前序列素材库</strong>\
                                            <div class="subtle">仅显示已导入当前序列的素材，拖到时间轴后才进入可编辑状态</div>\
                                        </div>\
                                        <div class="source-browser-head__actions">\
                                            <button class="secondary-button js-video-import-asset-center" type="button">导入素材中心素材</button>\
                                            <button class="secondary-button js-video-import-external-assets" type="button">导入其它素材</button>\
                                        </div>\
                                    </div>\
                                    <div class="source-browser-tabs">\
                                        <span class="is-selected" data-type="video">视频 <em>0</em></span>\
                                        <span data-type="image">图片 <em>0</em></span>\
                                        <span data-type="subtitle">字幕 <em>0</em></span>\
                                        <span data-type="audio">音频 <em>0</em></span>\
                                    </div>\
                                    <div class="source-thumb-grid source-thumb-grid--video-editor" data-search="素材缩略图 视频 图片 字幕 音频">\
                                        <div class="empty-state" style="padding:24px;text-align:center;grid-column:1/-1;"><p>当前素材库还是空的</p><p class="subtle">先从素材中心批量导入，或直接导入其它素材到当前序列。</p></div>\
                                    </div>\
                                </section>\
                                <section class="video-preview-shell video-preview-shell--editor">\
                                    <div class="video-preview-head">\
                                        <div>\
                                            <strong>节目监视器</strong>\
                                            <div class="subtle js-video-monitor-meta">等待选择素材或片段</div>\
                                        </div>\
                                        <div class="video-preview-tools"><span class="pill info">1080P</span><span class="pill success">自动保存</span></div>\
                                    </div>\
                                    <div class="canvas-stage canvas-stage--landscape video-preview-stage video-preview-stage--editor">\
                                        <div class="canvas-chip js-video-monitor-chip">等待选择</div>\
                                        <div class="video-surface video-surface--editor js-video-monitor-surface"><div class="play-button">等待选择</div></div>\
                                    </div>\
                                </section>\
                            </div>\
                        </section>\
                        <div class="timeline-board video-timeline-board js-video-timeline-board">\
                            <div class="timeline-empty-state"><strong>正在载入时间轴</strong><div class="subtle">当前序列加载完成后，这里会显示真实轨道、片段和字幕块。</div></div>\
                        </div>\
                    </div>\
                </div>\
            </section>',
            detailHtml: '<div class="detail-root"><section class="panel video-inspector-panel"><div class="panel__header"><div><strong>当前对象属性</strong><div class="subtle js-video-inspector-copy">等待选中时间轴片段、字幕块或素材</div></div></div><div class="video-inspector-tabs"><span class="is-selected" data-tab="properties">属性</span><span data-tab="subtitle">字幕</span><span data-tab="export">导出</span></div><div class="workbench-side-list js-video-inspector-content"><article class="workbench-sidecard"><div class="workbench-sidecard__head"><strong>等待序列数据</strong><span class="pill info">初始化</span></div><div class="subtle">当前项目、素材和时间线加载完成后，这里会联动刷新。</div></article></div></section></div>',
        };
    };

}());
