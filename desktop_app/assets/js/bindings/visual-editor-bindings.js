/* ── bindings/visual-editor-bindings.js ─ 视觉编辑器页交互绑定 ──
   负责 visual-editor 路由的画布工具、模板切换等交互。
   依赖：bindings.js（全局 bindRouteInteractions 注册机制）
   ──────────────────────────────────────────────────────── */
(function () {
    'use strict';

    window._visualEditorBindings = function () {
        // 工具栏工具切换
        document.querySelectorAll('#mainHost .workbench-tool').forEach(function (btn) {
            btn.addEventListener('click', function () {
                document.querySelectorAll('#mainHost .workbench-tool').forEach(function (b) {
                    b.classList.remove('is-selected');
                });
                btn.classList.add('is-selected');
            });
        });

        // 分段按钮组（如尺寸切换）
        document.querySelectorAll('#mainHost .segmented').forEach(function (group) {
            group.querySelectorAll('button').forEach(function (btn) {
                btn.addEventListener('click', function () {
                    group.querySelectorAll('button').forEach(function (b) { b.classList.remove('is-active'); });
                    btn.classList.add('is-active');
                });
            });
        });
    };

}());
