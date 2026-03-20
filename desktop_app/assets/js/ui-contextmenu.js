function showContextMenu(x, y, items) {
    const menu = document.getElementById('contextMenu');
    if (!menu) return;
    menu.innerHTML = items.map((item) => {
        if (item.separator) return '<div class="context-menu__separator"></div>';
        return `<button class="context-menu__item" data-action="${item.action}" type="button"><span class="shell-icon">${item.icon || ''}</span> ${item.label}</button>`;
    }).join('');
    menu.style.left = Math.min(x, window.innerWidth - 200) + 'px';
    menu.style.top = Math.min(y, window.innerHeight - menu.children.length * 36 - 16) + 'px';
    menu.classList.remove('shell-hidden');

    const handler = (e) => {
        const btn = e.target.closest('.context-menu__item');
        if (btn) {
            const action = btn.dataset.action;
            menu.classList.add('shell-hidden');
            handleContextAction(action);
        }
        if (!e.target.closest('.context-menu')) {
            menu.classList.add('shell-hidden');
        }
        document.removeEventListener('click', handler);
    };
    setTimeout(() => document.addEventListener('click', handler), 0);
}

let contextTarget = null;

function handleContextAction(action) {
    const name = contextTarget ? (extractTextFromEl(contextTarget, 'strong') || contextTarget.textContent.trim().slice(0, 20)) : '项目';
    switch (action) {
        case 'edit': showToast(`正在编辑: ${name}`, 'info'); break;
        case 'delete': showToast(`已删除: ${name}`, 'warning'); addNotification('删除操作', `"${name}" 已移入回收站。`, 'warning'); break;
        case 'copy': showToast(`已复制: ${name}`, 'success'); break;
        case 'export': showToast(`已导出: ${name}`, 'success'); break;
        case 'pin': showToast(`已置顶: ${name}`, 'info'); break;
        case 'archive': showToast(`已归档: ${name}`, 'info'); break;
        default: showToast(`操作: ${action}`, 'info');
    }
}

function bindContextMenu() {
    document.addEventListener('contextmenu', (e) => {
        const card = e.target.closest('.board-card, .strip-card, .task-item, .source-thumb, .workbench-sidecard, tbody .route-row');
        if (!card) return;
        e.preventDefault();
        contextTarget = card;

        const isThumb = card.classList.contains('source-thumb');
        const isRow = card.tagName === 'TR';
        const items = isThumb ? [
            { icon: '✏', label: '编辑素材信息', action: 'edit' },
            { icon: '📋', label: '复制素材链接', action: 'copy' },
            { separator: true },
            { icon: '📤', label: '导出素材', action: 'export' },
            { icon: '📌', label: '标记为高价值', action: 'pin' },
            { separator: true },
            { icon: '🗑', label: '删除', action: 'delete' },
        ] : isRow ? [
            { icon: '👁', label: '查看详情', action: 'edit' },
            { icon: '📋', label: '复制行数据', action: 'copy' },
            { icon: '📤', label: '导出为 CSV', action: 'export' },
            { separator: true },
            { icon: '🗑', label: '删除', action: 'delete' },
        ] : [
            { icon: '✏', label: '编辑', action: 'edit' },
            { icon: '📋', label: '复制', action: 'copy' },
            { icon: '📌', label: '置顶', action: 'pin' },
            { icon: '🗃', label: '归档', action: 'archive' },
            { separator: true },
            { icon: '🗑', label: '删除', action: 'delete' },
        ];
        showContextMenu(e.clientX, e.clientY, items);
    });
}

/* ═══════════════════════════════════════════════
   拖拽排序（看板列内/列间）
   ═══════════════════════════════════════════════ */
