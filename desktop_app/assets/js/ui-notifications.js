function addNotification(title, body, tone) {
    uiState.notificationId += 1;
    const notification = { id: uiState.notificationId, title, body, tone: tone || 'info', read: false, time: new Date() };
    uiState.notifications.unshift(notification);
    if (uiState.notifications.length > 50) uiState.notifications.length = 50;
    renderNotifications();
    updateNotificationBadge();
    return notification.id;
}

let __notificationSystemBound = false;

function setNotificationPanelOpen(panel, btn, open) {
    if (!panel || !btn) return;
    panel.classList.toggle('shell-hidden', !open);
    panel.classList.toggle('is-open', open);
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
}

function closeNotificationPanel() {
    const btn = document.getElementById('notificationToggle');
    const panel = document.getElementById('notificationPanel');
    if (!btn || !panel) return;
    setNotificationPanelOpen(panel, btn, false);
}

function renderNotifications() {
    const list = document.getElementById('notificationList');
    if (!list) return;
    if (!uiState.notifications.length) {
        list.innerHTML = '<div class="notification-empty">暂无通知</div>';
        return;
    }
    list.innerHTML = uiState.notifications.slice(0, 20).map((n) => `
        <div class="notification-item ${n.read ? '' : 'is-unread'}" data-notif-id="${n.id}">
            <div class="notification-item__dot ${n.tone}"></div>
            <div class="notification-item__body">
                <strong>${n.title}</strong>
                <div class="subtle">${n.body}</div>
                <div class="subtle">${formatTimeAgo(n.time)}</div>
            </div>
        </div>
    `).join('');
    list.querySelectorAll('.notification-item').forEach((item) => {
        item.addEventListener('click', () => {
            const id = Number(item.dataset.notifId);
            const notif = uiState.notifications.find((n) => n.id === id);
            if (notif) notif.read = true;
            item.classList.remove('is-unread');
            updateNotificationBadge();
        });
    });
}

function updateNotificationBadge() {
    const btn = document.getElementById('notificationToggle');
    if (!btn) return;
    const unread = uiState.notifications.filter((n) => !n.read).length;
    let badge = btn.querySelector('.notif-badge');
    if (unread > 0) {
        if (!badge) {
            badge = document.createElement('span');
            badge.className = 'notif-badge';
            btn.appendChild(badge);
        }
        badge.textContent = unread > 9 ? '9+' : unread;
    } else if (badge) {
        badge.remove();
    }
    if (uiState.shellRuntime && uiState.shellRuntime.systemStatus) {
        const existing = uiState.shellRuntime.systemStatus.notifications || {};
        uiState.shellRuntime.systemStatus.notifications = {
            total: existing.total || uiState.notifications.length,
            unread,
            hasUnread: unread > 0,
        };
    }
    if (typeof renderShellRuntimeSummary === 'function') {
        renderShellRuntimeSummary();
    }
}

function formatTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    if (seconds < 60) return '刚刚';
    if (seconds < 3600) return Math.floor(seconds / 60) + ' 分钟前';
    if (seconds < 86400) return Math.floor(seconds / 3600) + ' 小时前';
    return Math.floor(seconds / 86400) + ' 天前';
}

function syncNotifications(items) {
    const readMap = {};
    (uiState.notifications || []).forEach((item) => {
        readMap[String(item.id)] = Boolean(item.read);
    });

    uiState.notifications = (items || []).map((item, index) => ({
        id: item.id || ('notif-' + index),
        title: item.title || '系统通知',
        body: item.body || '暂无详细说明',
        tone: item.tone || 'info',
        read: readMap[String(item.id || ('notif-' + index))] || false,
        time: item.created_at ? new Date(item.created_at) : new Date(),
        source: item.source || 'backend',
    }));
    uiState.notificationId = uiState.notifications.length;
    if (uiState.shellRuntime && uiState.shellRuntime.systemStatus) {
        uiState.shellRuntime.systemStatus.notifications = {
            total: uiState.notifications.length,
            unread: uiState.notifications.filter((n) => !n.read).length,
            hasUnread: uiState.notifications.some((n) => !n.read),
        };
    }
    renderNotifications();
    updateNotificationBadge();
}

function loadNotifications() {
    if (!window.api || !window.api.notifications || typeof window.api.notifications.list !== 'function') {
        syncNotifications([]);
        return Promise.resolve([]);
    }
    return window.api.notifications.list()
        .then((items) => {
            syncNotifications(items || []);
            return items || [];
        })
        .catch(() => {
            syncNotifications([]);
            return [];
        });
}

function initNotificationSystem() {
    const btn = document.getElementById('notificationToggle');
    const panel = document.getElementById('notificationPanel');
    if (!btn || !panel) return;
    if (__notificationSystemBound) {
        updateNotificationBadge();
        return;
    }
    __notificationSystemBound = true;

    btn.setAttribute('aria-expanded', 'false');

    btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = panel.classList.contains('is-open');
        setNotificationPanelOpen(panel, btn, !isOpen);
    });

    document.addEventListener('click', (e) => {
        if (!e.target.closest('#notificationPanel') && !e.target.closest('#notificationToggle')) {
            setNotificationPanelOpen(panel, btn, false);
        }
    });

    window.addEventListener('resize', closeNotificationPanel);

    const clearBtn = document.getElementById('clearNotifications');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            uiState.notifications.forEach((n) => { n.read = true; });
            renderNotifications();
            updateNotificationBadge();
            showToast('所有通知已标为已读', 'success');
        });
    }

    loadNotifications();
    document.addEventListener('data:changed', function (event) {
        var detail = event && event.detail ? event.detail : {};
        if (detail.entity === 'activity_log' || detail.entity === 'task' || detail.entity === 'dev_seed') {
            loadNotifications();
        }
    });
}

/* ═══════════════════════════════════════════════
   右键菜单系统
   ═══════════════════════════════════════════════ */
