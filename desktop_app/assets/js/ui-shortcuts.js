function bindKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        const isInput = ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName);

        // Ctrl+K → 搜索
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const search = document.getElementById('globalSearch');
            if (search) { search.focus(); search.select(); }
            return;
        }

        // Ctrl+\ → 切换右侧面板
        if ((e.ctrlKey || e.metaKey) && e.key === '\\') {
            e.preventDefault();
            document.getElementById('detailToggle')?.click();
            return;
        }

        // Ctrl+B → 切换侧边栏
        if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
            e.preventDefault();
            document.getElementById('menuToggle')?.click();
            return;
        }

        // Ctrl+D → 切换主题
        if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
            e.preventDefault();
            document.getElementById('themeToggle')?.click();
            return;
        }

        // Escape → 关闭弹层
        if (e.key === 'Escape') {
            document.getElementById('contextMenu')?.classList.add('shell-hidden');
            document.getElementById('notificationPanel')?.classList.add('shell-hidden');
            const overlay = document.getElementById('shortcutOverlay');
            if (overlay && !overlay.classList.contains('shell-hidden')) {
                overlay.classList.add('shell-hidden');
                return;
            }
            return;
        }

        // ? → 快捷键帮助
        if (!isInput && e.key === '?') {
            e.preventDefault();
            document.getElementById('shortcutOverlay')?.classList.toggle('shell-hidden');
            return;
        }
    });

    document.getElementById('closeShortcuts')?.addEventListener('click', () => {
        document.getElementById('shortcutOverlay')?.classList.add('shell-hidden');
    });
}
