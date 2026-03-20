function addNotification(title, body, tone) {
    uiState.notificationId += 1;
    const notification = { id: uiState.notificationId, title, body, tone: tone || 'info', read: false, time: new Date() };
    uiState.notifications.unshift(notification);
    if (uiState.notifications.length > 50) uiState.notifications.length = 50;
    renderNotifications();
    updateNotificationBadge();
    return notification.id;
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
}

function formatTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    if (seconds < 60) return '刚刚';
    if (seconds < 3600) return Math.floor(seconds / 60) + ' 分钟前';
    if (seconds < 86400) return Math.floor(seconds / 3600) + ' 小时前';
    return Math.floor(seconds / 86400) + ' 天前';
}

function initNotificationSystem() {
    const btn = document.getElementById('notificationToggle');
    const panel = document.getElementById('notificationPanel');
    if (!btn || !panel) return;

    btn.addEventListener('click', (e) => {
        e.stopPropagation();
        panel.classList.toggle('shell-hidden');
    });

    document.addEventListener('click', (e) => {
        if (!e.target.closest('#notificationPanel') && !e.target.closest('#notificationToggle')) {
            panel.classList.add('shell-hidden');
        }
    });

    const clearBtn = document.getElementById('clearNotifications');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            uiState.notifications.forEach((n) => { n.read = true; });
            renderNotifications();
            updateNotificationBadge();
            showToast('所有通知已标为已读', 'success');
        });
    }

    // 模拟系统通知
    setTimeout(() => addNotification('系统提醒', '有 12 个素材等待版权审核，请及时处理。', 'warning'), 1500);
    setTimeout(() => addNotification('任务完成', '批量标题生成任务已完成，共生成 24 条标题。', 'success'), 3000);
    setTimeout(() => addNotification('AI 模型更新', 'GPT-4o 模型已同步至所有 AI 工作台。', 'info'), 5000);
    setTimeout(() => addNotification('性能告警', '数据采集任务 #0382 连续 3 次超时，建议检查代理配置。', 'error'), 8000);
}

/* ═══════════════════════════════════════════════
   右键菜单系统
   ═══════════════════════════════════════════════ */
