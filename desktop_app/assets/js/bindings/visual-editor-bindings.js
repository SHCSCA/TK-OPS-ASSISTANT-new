(function () {
    'use strict';

    if (typeof window.registerBindingModule !== 'function') {
        throw new Error('binding module registry not loaded');
    }

    function _activateTool(btn, label) {
        _setExclusiveButtonState(btn);
        showToast('已切换到' + label + '工具', 'info');
    }

    window.registerBindingModule('visual-editor', function () {
        return {
            '导出当前设计': function () {
                return _createQuickTask('设计稿导出', 'publish', '来源页面：视觉编辑器', '设计导出任务已加入队列');
            },
            '切换模板': function () {
                showToast('模板切换面板已打开', 'info');
            },
            '画布': function (btn) { _activateTool(btn, '画布'); },
            '文字': function (btn) { _activateTool(btn, '文字'); },
            '贴纸': function (btn) { _activateTool(btn, '贴纸'); },
            '导出': function (btn) { _activateTool(btn, '导出'); },
        };
    });
})();
