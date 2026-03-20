function bindDragAndDrop() {
    const mainHost = document.getElementById('mainHost');
    const draggables = mainHost.querySelectorAll('.board-card, .task-item');
    if (!draggables.length) return;

    draggables.forEach((card) => {
        card.setAttribute('draggable', 'true');
        card.addEventListener('dragstart', (e) => {
            card.classList.add('is-dragging');
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', '');
        });
        card.addEventListener('dragend', () => {
            card.classList.remove('is-dragging');
            mainHost.querySelectorAll('.drag-over').forEach((el) => el.classList.remove('drag-over'));
        });
    });

    const columns = mainHost.querySelectorAll('.board-column, .kanban-column');
    columns.forEach((col) => {
        col.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            col.classList.add('drag-over');
            const dragging = mainHost.querySelector('.is-dragging');
            if (!dragging) return;
            const container = col.querySelector('.board-column__cards') || col;
            const afterElement = getDragAfterElement(container, e.clientY);
            if (afterElement) {
                container.insertBefore(dragging, afterElement);
            } else {
                container.appendChild(dragging);
            }
        });
        col.addEventListener('dragleave', (e) => {
            if (!col.contains(e.relatedTarget)) col.classList.remove('drag-over');
        });
        col.addEventListener('drop', (e) => {
            e.preventDefault();
            col.classList.remove('drag-over');
            const dragging = mainHost.querySelector('.is-dragging');
            if (dragging) {
                showToast('卡片已移动', 'success');
                addNotification('看板操作', `"${extractTextFromEl(dragging, 'strong') || '卡片'}" 已移至新列。`, 'info');
            }
        });
    });
}

function getDragAfterElement(container, y) {
    const elements = [...container.querySelectorAll('.board-card:not(.is-dragging), .task-item:not(.is-dragging)')];
    return elements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        if (offset < 0 && offset > closest.offset) {
            return { offset, element: child };
        }
        return closest;
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

/* ═══════════════════════════════════════════════
   AI 配置联动
   ═══════════════════════════════════════════════ */
