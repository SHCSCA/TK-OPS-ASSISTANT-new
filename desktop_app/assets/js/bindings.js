function bindSegmentedButtons() {
    document.querySelectorAll('.segmented').forEach((group) => {
        group.querySelectorAll('button').forEach((btn) => {
            btn.addEventListener('click', () => {
                group.querySelectorAll('button').forEach((b) => b.classList.remove('is-active'));
                btn.classList.add('is-active');
            });
        });
    });
}

function bindFilters() {
    document.querySelectorAll('.filter-row select, .filter-row input, .filter-bar select, .filter-bar input').forEach((el) => {
        el.addEventListener('change', () => applyCurrentRouteState());
    });
}

function bindDetailTriggers() {
    document.querySelectorAll('[data-detail-target]').forEach((trigger) => {
        trigger.addEventListener('click', () => {
            const targetId = trigger.dataset.detailTarget;
            const template = document.getElementById('detail-' + targetId);
            if (template) {
                document.getElementById('detailHost').innerHTML = template.innerHTML;
            }
            document.querySelectorAll('[data-detail-target]').forEach((t) => t.classList.remove('is-selected'));
            trigger.classList.add('is-selected');
        });
    });
}

/* ─── 功能联动：提取元素内容生成右侧详情 ─── */
function buildDynamicDetail(title, subtitle, details, actions) {
    const detailItems = details.map((d) => `<div class="detail-item"><span class="subtle">${d.label}</span><strong>${d.value}</strong></div>`).join('');
    const actionItems = actions.map((a) => `<article class="workbench-sidecard"><strong>${a.title}</strong><div class="subtle">${a.desc}</div></article>`).join('');
    return `
        <div class="detail-root">
            <section class="panel">
                <div class="panel__header"><div><strong>${title}</strong><div class="subtle">${subtitle}</div></div></div>
                <div class="detail-list">${detailItems}</div>
            </section>
            ${actionItems ? `<section class="panel"><div class="panel__header"><div><strong>相关操作</strong><div class="subtle">针对当前选中项的推荐动作。</div></div></div><div class="workbench-side-list">${actionItems}</div></section>` : ''}
        </div>
    `;
}

function extractTextFromEl(el, selector) {
    const target = el.querySelector(selector);
    return target ? target.textContent.trim() : '';
}

/* ─── 功能联动：点击主区条目→更新右侧面板 ─── */
function bindMainItemClicks() {
    const mainHost = document.getElementById('mainHost');
    const detailHost = document.getElementById('detailHost');
    const route = routes[currentRoute];
    if (!route || route.hideDetailPanel === true) return;

    // 看板卡片点击
    mainHost.querySelectorAll('.board-card').forEach((card) => {
        card.style.cursor = 'pointer';
        card.addEventListener('click', () => {
            mainHost.querySelectorAll('.board-card').forEach((c) => c.classList.remove('is-selected'));
            card.classList.add('is-selected');
            const title = extractTextFromEl(card, 'strong') || '任务详情';
            const desc = extractTextFromEl(card, '.subtle') || '';
            const pills = [...card.querySelectorAll('.pill')].map((p) => p.textContent.trim());
            detailHost.innerHTML = buildDynamicDetail('任务详情', '点击查看的任务信息', [
                { label: '任务名称', value: title },
                { label: '描述', value: desc || '—' },
                { label: '标签', value: pills.join(' / ') || '—' },
            ], [
                { title: '编辑任务', desc: '修改任务参数或调整执行策略。' },
                { title: '查看日志', desc: '打开该任务最近的运行日志。' },
            ]);
            detailHost.classList.remove('shell-hidden');
        });
    });

    // 表格行点击
    mainHost.querySelectorAll('tbody .route-row').forEach((row) => {
        row.style.cursor = 'pointer';
        row.addEventListener('click', () => {
            mainHost.querySelectorAll('tbody .route-row').forEach((r) => r.classList.remove('is-selected'));
            row.classList.add('is-selected');
            const cells = [...row.querySelectorAll('td')];
            const details = cells.slice(0, 5).map((td, i) => ({
                label: document.querySelectorAll('thead th')[i]?.textContent.trim() || `列 ${i + 1}`,
                value: td.textContent.trim(),
            }));
            detailHost.innerHTML = buildDynamicDetail('行详情', '选中表格项的字段信息', details, []);
            detailHost.classList.remove('shell-hidden');
        });
    });

    // 任务项点击（列表视图）
    mainHost.querySelectorAll('.task-item').forEach((item) => {
        item.style.cursor = 'pointer';
        item.addEventListener('click', () => {
            mainHost.querySelectorAll('.task-item').forEach((t) => t.classList.remove('is-selected'));
            item.classList.add('is-selected');
            const title = extractTextFromEl(item, 'strong') || '任务';
            const desc = extractTextFromEl(item, '.subtle') || '';
            detailHost.innerHTML = buildDynamicDetail('任务信息', desc, [
                { label: '名称', value: title },
            ], [
                { title: '查看执行记录', desc: '查看该任务的历史执行情况。' },
            ]);
            detailHost.classList.remove('shell-hidden');
        });
    });

    // 洞察卡片点击（分析页）
    mainHost.querySelectorAll('.strip-card').forEach((card) => {
        card.style.cursor = 'pointer';
        card.addEventListener('click', () => {
            mainHost.querySelectorAll('.strip-card').forEach((c) => c.classList.remove('is-selected'));
            card.classList.add('is-selected');
            const title = extractTextFromEl(card, 'strong') || '洞察';
            const desc = extractTextFromEl(card, '.subtle') || '';
            detailHost.innerHTML = buildDynamicDetail('洞察详情', '深入查看选中的分析要点', [
                { label: '标题', value: title },
                { label: '摘要', value: desc || '—' },
            ], []);
            detailHost.classList.remove('shell-hidden');
        });
    });
}

/* ─── 功能联动：任务看板视图切换 ─── */
function bindTaskViewToggles() {
    const mainHost = document.getElementById('mainHost');
    const toggles = mainHost.querySelectorAll('.task-view-btn');
    if (!toggles.length) return;
    const kanban = mainHost.querySelector('.task-board');
    const list = mainHost.querySelector('.task-list-view, table');
    const calendar = mainHost.querySelector('.task-calendar');
    toggles.forEach((btn) => {
        btn.addEventListener('click', () => {
            toggles.forEach((b) => b.classList.remove('is-active'));
            btn.classList.add('is-active');
            const view = btn.textContent.trim();
            if (kanban) kanban.classList.toggle('shell-hidden', view !== '看板');
            if (list) list.classList.toggle('shell-hidden', view === '看板' || view === '日历');
            if (calendar) calendar.classList.toggle('shell-hidden', view !== '日历');
        });
    });
}

/* ─── 功能联动：任务状态筛选 ─── */
function bindTaskFilterTabs() {
    const mainHost = document.getElementById('mainHost');
    const tabs = mainHost.querySelectorAll('.task-filter-bar .task-filter-tab');
    if (!tabs.length) return;
    tabs.forEach((tab) => {
        tab.addEventListener('click', () => {
            const label = tab.textContent.replace(/\d+/g, '').trim();
            const cards = mainHost.querySelectorAll('.board-card, .task-item');
            cards.forEach((card) => {
                if (label === '全部') {
                    card.classList.remove('is-filtered-out');
                } else {
                    const pills = [...card.querySelectorAll('.pill')].map((p) => p.textContent.trim());
                    const text = card.textContent;
                    const match = pills.some((p) => p.includes(label)) || text.includes(label);
                    card.classList.toggle('is-filtered-out', !match);
                }
            });
        });
    });
}

/* ─── 功能联动：素材分类筛选 ─── */
function bindAssetCategoryFilter() {
    const mainHost = document.getElementById('mainHost');
    const cats = mainHost.querySelectorAll('.asset-category-item');
    if (!cats.length) return;
    cats.forEach((cat) => {
        cat.addEventListener('click', () => {
            cats.forEach((c) => c.classList.remove('is-active'));
            cat.classList.add('is-active');
            const label = extractTextFromEl(cat, 'strong');
            const thumbs = mainHost.querySelectorAll('.source-thumb');
            thumbs.forEach((thumb) => {
                if (label === '全部素材') {
                    thumb.classList.remove('is-filtered-out');
                } else {
                    const tags = [...thumb.querySelectorAll('.pill')].map((p) => p.textContent.trim());
                    const name = thumb.textContent;
                    const typeMap = { '短视频口播': '视频', '封面图片': '图片', 'B-roll 镜头': '视频', '音频 / 配乐': '音频', '字幕 / 文案': '字幕' };
                    const mapped = typeMap[label] || label;
                    const match = tags.some((t) => t.includes(mapped)) || name.includes(mapped);
                    thumb.classList.toggle('is-filtered-out', !match);
                }
            });
        });
    });
}

/* ─── 功能联动：素材点击更新右侧 ─── */
function bindAssetThumbDetail() {
    const mainHost = document.getElementById('mainHost');
    const detailHost = document.getElementById('detailHost');
    const thumbs = mainHost.querySelectorAll('.source-thumb');
    if (!thumbs.length) return;
    const route = routes[currentRoute];
    thumbs.forEach((thumb) => {
        thumb.addEventListener('click', () => {
            const name = extractTextFromEl(thumb, '.source-thumb__name') || '未命名素材';
            const tags = [...thumb.querySelectorAll('.pill')].map((p) => p.textContent.trim());
            const dur = extractTextFromEl(thumb, '.source-thumb__dur');

            // 选中态切换
            thumbs.forEach((t) => t.classList.remove('is-selected'));
            thumb.classList.add('is-selected');

            // hideDetailPanel 路由：更新内联 mini-preview 而非打开右侧面板
            if (route?.hideDetailPanel === true) {
                const preview = mainHost.querySelector('.source-mini-preview');
                if (preview) {
                    const nameEl = preview.querySelector('strong');
                    const infoEl = preview.querySelector('.subtle');
                    if (nameEl) nameEl.textContent = name;
                    if (infoEl) infoEl.textContent = [dur, tags.join(' · ')].filter(Boolean).join(' · ');
                }
                return;
            }

            detailHost.innerHTML = buildDynamicDetail('素材详情', '选中素材的属性信息', [
                { label: '素材名称', value: name },
                { label: '类型标签', value: tags.join(' / ') || '—' },
                { label: '时长', value: dur || '—' },
                { label: '状态', value: tags.find((t) => ['已授权', '待审', '已入库', '可复用', '需授权', '高转化'].includes(t)) || '—' },
            ], [
                { title: '编辑素材信息', desc: '修改名称、分类和授权状态。' },
                { title: '发送到创作链路', desc: '将素材推送到内容工厂或创意工坊。' },
            ]);
            detailHost.classList.remove('shell-hidden');
        });
    });
}

/* ─── 功能联动：分析图表切换 ─── */
function bindChartToggles() {
    const mainHost = document.getElementById('mainHost');
    const toggles = mainHost.querySelectorAll('.analytics-chart-toggles button');
    if (!toggles.length) return;
    toggles.forEach((btn) => {
        btn.addEventListener('click', () => {
            toggles.forEach((b) => b.classList.remove('is-active'));
            btn.classList.add('is-active');
            const chart = mainHost.querySelector('.chart-placeholder');
            if (chart) chart.textContent = `📊 ${btn.textContent.trim()} 视图`;
        });
    });
}

/* ─── 响应式：右侧面板手动切换 ─── */
function bindDetailPanelToggle() {
    const btn = document.getElementById('detailToggle');
    if (!btn) return;
    btn.addEventListener('click', () => {
        const detailHost = document.getElementById('detailHost');
        const route = routes[currentRoute];
        // 如果面板当前可见（被强制打开），允许关闭；否则 hideDetailPanel 路由不打开
        const isVisible = !detailHost.classList.contains('shell-hidden');
        if (route?.hideDetailPanel === true && !isVisible) return;
        uiState.detailPanelForced = isVisible ? 'hidden' : 'visible';
        detailHost.classList.toggle('shell-hidden');
        document.getElementById('shellApp').classList.toggle('detail-hidden', detailHost.classList.contains('shell-hidden'));
    });
}

function _buttonText(btn) {
    return (btn && btn.textContent ? btn.textContent : '').replace(/\s+/g, ' ').trim();
}

function _downloadTextFile(filename, content, mimeType) {
    const blob = new Blob([content], { type: mimeType || 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = filename;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 0);
}

function _bindButtonAction(btn, binderKey, handler) {
    if (!btn || btn.dataset[binderKey] === '1') return;
    btn.dataset[binderKey] = '1';
    btn.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopPropagation();
        handler(btn, event);
    });
}

function _setExclusiveButtonState(btn) {
    const group = btn && btn.parentElement;
    if (!group) return;
    group.querySelectorAll('button').forEach((item) => {
        item.classList.remove('is-active', 'is-selected');
    });
    btn.classList.add('is-active');
    btn.classList.add('is-selected');
}

function _navigateToRoute(routeKey, toast, tone) {
    if (typeof renderRoute === 'function' && routeKey && routes && routes[routeKey]) {
        renderRoute(routeKey);
    }
    if (toast) showToast(toast, tone || 'info');
}

function _createQuickTask(title, taskType, summary, successText, extra) {
    if (!api || !api.tasks || typeof api.tasks.create !== 'function') {
        showToast('当前版本不支持创建任务', 'warning');
        return Promise.resolve(null);
    }
    const payload = Object.assign({
        title,
        task_type: taskType || 'maintenance',
        priority: 'medium',
        status: 'pending',
        result_summary: summary || ('来源页面：' + currentRoute),
    }, extra || {});
    return api.tasks.create(payload).then((result) => {
        showToast(successText || (title + ' 已加入队列'), 'success');
        return result;
    }).catch((err) => {
        showToast('创建失败: ' + ((err && err.message) || '未知错误'), 'error');
        return null;
    });
}

function _exportThroughBackend(title, lines, successText) {
    const text = [title, '时间: ' + new Date().toLocaleString()].concat(lines || []).join('\n');
    if (api && api.utils && typeof api.utils.exportTextFile === 'function') {
        return api.utils.exportTextFile(text).then((saved) => {
            showToast(saved && saved.saved ? (successText || (title + ' 导出成功')) : '已取消导出', saved && saved.saved ? 'success' : 'warning');
            return saved;
        }).catch((err) => {
            showToast('导出失败: ' + ((err && err.message) || '未知错误'), 'error');
            return null;
        });
    }
    _downloadTextFile((title || 'export').replace(/\s+/g, '-').toLowerCase() + '.txt', text, 'text/plain;charset=utf-8');
    showToast(successText || (title + ' 已导出'), 'success');
    return Promise.resolve(null);
}

function _guessAssetTypeByName(filename) {
    const lower = String(filename || '').toLowerCase();
    if (/\.(png|jpg|jpeg|gif|webp|bmp|svg)$/.test(lower)) return 'image';
    if (/\.(mp4|mov|avi|mkv|webm)$/.test(lower)) return 'video';
    if (/\.(mp3|wav|aac|flac|m4a)$/.test(lower)) return 'audio';
    if (/\.(txt|md|json|csv|srt|vtt)$/.test(lower)) return 'text';
    return 'template';
}

function _pickFilesAndImportAssets(routeKey) {
    if (!api || !api.utils || typeof api.utils.pickFiles !== 'function') {
        showToast('当前版本不支持文件选择', 'warning');
        return;
    }
    api.utils.pickFiles().then((files) => {
        const list = (files || []).filter(Boolean);
        if (!list.length) {
            showToast('未选择文件', 'warning');
            return;
        }
        const jobs = list.map((filePath) => {
            const parts = String(filePath).split(/[\\/]/);
            const filename = parts[parts.length - 1] || '未命名文件';
            return Promise.all([
                api.assets.create({
                    filename,
                    file_path: filePath,
                    asset_type: _guessAssetTypeByName(filename),
                    tags: '文件导入',
                }).catch(() => null),
                api.tasks.create({
                    title: '文件导入 · ' + filename,
                    task_type: 'maintenance',
                    priority: 'medium',
                    status: 'pending',
                    result_summary: '来源页面：' + routeKey + ' / 文件：' + filePath,
                }).catch(() => null),
            ]).then((results) => results[0] || results[1]);
        });
        return Promise.all(jobs).then((results) => {
            const successCount = results.filter(Boolean).length;
            showToast('已导入 ' + successCount + ' 个文件', successCount ? 'success' : 'warning');
        });
    }).catch((err) => {
        showToast('导入失败: ' + ((err && err.message) || '未知错误'), 'error');
    });
}

function _runDiagnostics(title) {
    if (!api || !api.diagnostics || typeof api.diagnostics.run !== 'function') {
        showToast('当前版本不支持网络诊断', 'warning');
        return;
    }
    api.diagnostics.run().then((result) => {
        window.__lastDiagnosticsResult = result || null;
        showToast((title || '网络诊断') + ' 已完成检测', 'success');
    }).catch((err) => {
        showToast('诊断失败: ' + ((err && err.message) || '未知错误'), 'error');
    });
}

function _createNamedTaskAction(actionKey, payload, successText) {
    if (!api || !api.taskActions || typeof api.taskActions.create !== 'function') {
        showToast('当前版本不支持任务动作创建', 'warning');
        return Promise.resolve(null);
    }
    const data = Object.assign({ action_key: actionKey }, payload || {});
    return api.taskActions.create(data).then((task) => {
        showToast(successText || ((data.title || actionKey) + ' 已加入任务队列'), 'success');
        return task;
    }).catch((err) => {
        showToast('创建任务失败: ' + ((err && err.message) || '未知错误'), 'error');
        return null;
    });
}

function _selectedAccountIds() {
    return [...document.querySelectorAll('.js-batch-account:checked')]
        .map((el) => parseInt(el.dataset.id || '0', 10))
        .filter(Boolean);
}

function _selectedTaskIds() {
    return [...document.querySelectorAll('.js-batch-task:checked')]
        .map((el) => parseInt(el.dataset.id || '0', 10))
        .filter(Boolean);
}

function _selectedProviderId() {
    const selected = document.querySelector('#mainHost .table-wrapper tbody tr.is-selected[data-id], #mainHost .metric-list .task-item.is-selected[data-id]');
    return selected ? parseInt(selected.dataset.id || '0', 10) || null : null;
}

function _selectedDeviceId(btn) {
    const host = btn && btn.closest('[data-id]');
    if (host && host.dataset.id) return parseInt(host.dataset.id || '0', 10) || null;
    const selected = document.querySelector('#mainHost .device-env-card.is-selected[data-id]');
    return selected ? parseInt(selected.dataset.id || '0', 10) || null : null;
}

function _selectedDeviceIdFromButton(btn) {
    return _selectedDeviceId(btn);
}

function _openBatchGroupAssignmentModal() {
    const selectedIds = _selectedAccountIds();
    if (!selectedIds.length) {
        showToast('请先勾选需要归组的账号', 'warning');
        return;
    }
    api.groups.list().then((groups) => {
        const options = [{ value: '', label: '请选择目标分组' }].concat((groups || []).map((group) => ({
            value: String(group.id),
            label: group.name || ('分组 #' + group.id),
        })));
        openModal({
            title: '批量归组',
            submitText: '确认归组',
            fields: [
                { key: 'group_id', label: '目标分组', type: 'select', options, required: true },
            ],
            onSubmit: function (data) {
                const groupId = parseInt(data.group_id || '0', 10);
                if (!groupId) {
                    throw new Error('请选择目标分组');
                }
                const jobs = selectedIds.map((accountId) => api.accounts.update(accountId, { group_id: groupId }));
                return Promise.all(jobs).then(() => {
                    showToast('已完成 ' + selectedIds.length + ' 个账号归组', 'success');
                    if (typeof loadRouteData === 'function') loadRouteData('account');
                });
            },
        });
    }).catch((err) => {
        showToast('加载分组失败: ' + ((err && err.message) || '未知错误'), 'error');
    });
}

function _batchStartSelectedTasks() {
    const selectedIds = _selectedTaskIds();
    if (!selectedIds.length) {
        showToast('请先勾选需要启动的任务', 'warning');
        return;
    }
    Promise.all(selectedIds.map((taskId) => api.tasks.start(taskId))).then(() => {
        showToast('已启动 ' + selectedIds.length + ' 个任务', 'success');
        if (typeof loadRouteData === 'function') loadRouteData('task-queue');
    }).catch((err) => {
        showToast('批量启动失败: ' + ((err && err.message) || '未知错误'), 'error');
    });
}

function _resetSelectedProviderDefaults() {
    const providerId = _selectedProviderId();
    if (!providerId) {
        showToast('请先选择需要恢复的供应商', 'warning');
        return;
    }
    api.providers.update(providerId, {
        api_base: 'https://api.openai.com/v1',
        default_model: 'gpt-4o-mini',
        temperature: 0.7,
        max_tokens: 2048,
    }).then(() => {
        showToast('供应商默认配置已恢复', 'success');
        if (typeof loadRouteData === 'function') loadRouteData('ai-provider');
    }).catch((err) => {
        showToast('恢复默认失败: ' + ((err && err.message) || '未知错误'), 'error');
    });
}

function _openSelectedProviderEditModal() {
    const providerId = _selectedProviderId();
    if (!providerId) {
        showToast('请先选择需要保存的供应商', 'warning');
        return;
    }
    api.providers.list().then((providers) => {
        const provider = (providers || []).find((item) => Number(item.id) === Number(providerId));
        if (!provider) {
            showToast('未找到选中的供应商', 'warning');
            return;
        }
        if (typeof openProviderForm === 'function') {
            openProviderForm(provider);
        }
    }).catch((err) => {
        showToast('加载供应商失败: ' + ((err && err.message) || '未知错误'), 'error');
    });
}

function _openDeviceBindingModal(btn) {
    const deviceId = _selectedDeviceId(btn);
    if (!deviceId) {
        showToast('请先选择设备', 'warning');
        return;
    }
    api.accounts.list().then((accounts) => {
        const accountOptions = [{ value: '', label: '解除绑定' }].concat((accounts || []).map((account) => ({
            value: String(account.id),
            label: (account.username || ('账号 #' + account.id)) + ' / ' + (account.region || '-'),
        })));
        openModal({
            title: '调整设备绑定',
            submitText: '保存绑定',
            fields: [
                { key: 'account_id', label: '账号', type: 'select', options: accountOptions, required: true },
            ],
            onSubmit: function (data) {
                const accountId = parseInt(data.account_id || '0', 10);
                if (!accountId) {
                    return _createNamedTaskAction('device_unbind_account', {
                        title: '调整设备绑定',
                        summary: '来源页面：设备环境管理 / 调整绑定',
                        metadata: { device_id: deviceId, mode: 'unbind' },
                    }, '解除绑定任务已加入队列');
                }
                return api.accounts.update(accountId, { device_id: deviceId }).then(() => {
                    showToast('设备绑定已更新', 'success');
                    if (typeof loadRouteData === 'function') loadRouteData('device-management');
                });
            },
        });
    }).catch((err) => {
        showToast('加载账号列表失败: ' + ((err && err.message) || '未知错误'), 'error');
    });
}

function _openAssetTagBatchModal() {
    const thumbs = [...document.querySelectorAll('#mainHost .source-thumb.is-selected[data-id]')];
    const selectedIds = thumbs.map((thumb) => parseInt(thumb.dataset.id || '0', 10)).filter(Boolean);
    if (!selectedIds.length) {
        showToast('请先选择需要打标签的素材', 'warning');
        return;
    }
    openModal({
        title: '批量打标签',
        submitText: '应用标签',
        fields: [
            { key: 'tags', label: '标签', placeholder: '例如 春促, 高转化', required: true },
        ],
        onSubmit: function (data) {
            const tags = String(data.tags || '').trim();
            const jobs = selectedIds.map((assetId) => api.assets.update(assetId, { tags }));
            return Promise.all(jobs).then(() => {
                showToast('已更新 ' + selectedIds.length + ' 个素材标签', 'success');
                if (typeof loadRouteData === 'function') loadRouteData('asset-center');
            });
        },
    });
}

function _refreshCurrentRoute() {
    if (typeof loadRouteData === 'function' && currentRoute) {
        loadRouteData(currentRoute);
    }
}

function _createExperimentProjectFromRoute(routeKey) {
    const targetRoute = routeKey || currentRoute;
    const titleMap = {
        'visual-lab': '保存实验视图',
        'creative-workshop': '保存创意方案',
    };
    openModal({
        title: titleMap[targetRoute] || '保存实验项目',
        submitText: '保存',
        fields: [
            { key: 'name', label: '项目名称', value: (targetRoute === 'visual-lab' ? '可视化实验' : '创意方案') + ' ' + new Date().toLocaleDateString(), required: true },
            { key: 'goal', label: '目标说明', type: 'textarea', placeholder: '填写当前实验或创意方案的目标' },
        ],
        onSubmit: function (data) {
            const payload = {
                name: String(data.name || '').trim(),
                goal: String(data.goal || '').trim(),
                status: 'active',
                config_json: JSON.stringify({ route: targetRoute, saved_at: new Date().toISOString() }),
            };
            return api.experiments.createProject(payload).then(function (project) {
                return api.experiments.createView({
                    experiment_project_id: project.id,
                    name: payload.name + ' / 默认视图',
                    layout_json: JSON.stringify({ route: targetRoute, project_id: project.id, mode: 'default' }),
                }).then(function () { return project; });
            }).then(function (project) {
                if (api.activity && typeof api.activity.create === 'function') {
                    return api.activity.create({
                        category: 'experiment',
                        title: payload.name + ' 已保存',
                        payload_json: JSON.stringify({ route: targetRoute }),
                        related_entity_type: 'experiment_project',
                        related_entity_id: project.id,
                    }).catch(function () { return null; }).then(function () { return project; });
                }
                return project;
            }).then(function () {
                showToast((titleMap[targetRoute] || '实验项目已保存') + '成功', 'success');
                _refreshCurrentRoute();
            });
        },
    });
}

function _createReportRunFromRoute() {
    openModal({
        title: '生成新报表',
        submitText: '创建报表',
        fields: [
            { key: 'title', label: '报表标题', value: '经营分析报告 ' + new Date().toLocaleDateString(), required: true },
            { key: 'report_type', label: '报表类型', type: 'select', value: 'general', options: [{ value: 'daily', label: '日报' }, { value: 'weekly', label: '周报' }, { value: 'general', label: '专题' }] },
        ],
        onSubmit: function (data) {
            const payload = {
                title: String(data.title || '').trim(),
                report_type: data.report_type || 'general',
                status: 'pending',
                filters_json: JSON.stringify({ route: currentRoute, created_at: new Date().toISOString() }),
            };
            return api.reports.create(payload).then(function (report) {
                if (api.activity && typeof api.activity.create === 'function') {
                    return api.activity.create({
                        category: 'report',
                        title: payload.title + ' 已创建',
                        payload_json: JSON.stringify({ route: currentRoute, report_type: payload.report_type }),
                        related_entity_type: 'report_run',
                        related_entity_id: report.id,
                    }).catch(function () { return null; }).then(function () { return report; });
                }
                return report;
            }).then(function () {
                showToast('报表任务已创建', 'success');
                _refreshCurrentRoute();
            });
        },
    });
}

function _createWorkflowDefinitionFromRoute() {
    openModal({
        title: '保存工作流',
        submitText: '保存工作流',
        fields: [
            { key: 'name', label: '工作流名称', value: '工作流 ' + new Date().toLocaleDateString(), required: true },
            { key: 'description', label: '说明', type: 'textarea', placeholder: '描述当前工作流的目标和用途' },
        ],
        onSubmit: function (data) {
            const payload = {
                name: String(data.name || '').trim(),
                description: String(data.description || '').trim(),
                status: 'active',
                config_json: JSON.stringify({ route: currentRoute, saved_at: new Date().toISOString() }),
            };
            return api.workflows.createDefinition(payload).then(function (definition) {
                if (api.activity && typeof api.activity.create === 'function') {
                    return api.activity.create({
                        category: 'workflow',
                        title: payload.name + ' 已保存',
                        payload_json: JSON.stringify({ route: currentRoute }),
                        related_entity_type: 'workflow_definition',
                        related_entity_id: definition.id,
                    }).catch(function () { return null; }).then(function () { return definition; });
                }
                return definition;
            }).then(function () {
                showToast('工作流已保存', 'success');
                _refreshCurrentRoute();
            });
        },
    });
}

function _createWorkflowRunFromRoute() {
    api.workflows.definitions().then(function (definitions) {
        definitions = definitions || [];
        if (!definitions.length) {
            showToast('请先保存工作流，再执行运行', 'warning');
            _createWorkflowDefinitionFromRoute();
            return;
        }
        openModal({
            title: '运行工作流',
            submitText: '启动运行',
            fields: [
                {
                    key: 'workflow_definition_id',
                    label: '选择工作流',
                    type: 'select',
                    value: String(definitions[0].id || ''),
                    options: definitions.map(function (definition) {
                        return { value: String(definition.id), label: definition.name || ('工作流 #' + definition.id) };
                    }),
                    required: true,
                },
                { key: 'note', label: '运行说明', type: 'textarea', placeholder: '可选：说明本次运行目标' },
            ],
            onSubmit: function (data) {
                const workflowDefinitionId = parseInt(data.workflow_definition_id || '0', 10);
                if (!workflowDefinitionId) {
                    throw new Error('请选择需要运行的工作流');
                }
                return api.workflows.start({
                    workflow_definition_id: workflowDefinitionId,
                    status: 'running',
                    input_json: JSON.stringify({ route: currentRoute, note: String(data.note || '').trim() }),
                }).then(function (run) {
                    if (api.activity && typeof api.activity.create === 'function') {
                        return api.activity.create({
                            category: 'workflow',
                            title: '工作流运行已启动',
                            payload_json: JSON.stringify({ route: currentRoute, workflow_definition_id: workflowDefinitionId }),
                            related_entity_type: 'workflow_run',
                            related_entity_id: run.id,
                        }).catch(function () { return null; }).then(function () { return run; });
                    }
                    return run;
                }).then(function () {
                    showToast('工作流运行已启动', 'success');
                    _refreshCurrentRoute();
                });
            },
        });
    }).catch(function (err) {
        showToast('加载工作流失败: ' + ((err && err.message) || '未知错误'), 'error');
    });
}

function _bindSelectableButtonGroups() {
    const mainHost = document.getElementById('mainHost');
    if (!mainHost) return;
    const selectors = [
        '.mini-list button',
        '.product-nav-list button',
        '.copy-tone-list button',
        '.chart-type-grid button',
        '.data-source-list button',
        '.aicf-node-palette button',
    ];
    selectors.forEach((selector) => {
        mainHost.querySelectorAll(selector).forEach((btn) => {
            if (btn.dataset.tkopsPresetBound === '1') return;
            _bindButtonAction(btn, 'tkopsSelectableBound', () => {
                _setExclusiveButtonState(btn);
                showToast('已切换到 ' + _buttonText(btn), 'info');
            });
        });
    });
}

function _bindRouteButtonPresets() {
    const mainHost = document.getElementById('mainHost');
    if (!mainHost) return;

        const contentRoutes = ['creative-workshop', 'video-editor', 'visual-editor'];
    const generationRoutes = ['viral-title', 'product-title', 'script-extractor', 'ai-copywriter', 'ai-content-factory'];
    const analyticsRoutes = ['visual-lab', 'profit-analysis', 'competitor-monitor', 'traffic-board', 'blue-ocean', 'report-center', 'interaction-analysis', 'ecommerce-conversion', 'fan-profile'];

    const groupHandlers = {};

    if (contentRoutes.includes(currentRoute)) {
        Object.assign(groupHandlers, {
            '保存创意方案': () => _createExperimentProjectFromRoute('creative-workshop'),
            '对比创意版本': () => showToast('已切换到创意版本对比视图', 'info'),
            '导出当前设计': () => _createQuickTask('设计稿导出', 'publish', '来源页面：视觉编辑器', '设计导出任务已加入队列'),
            '切换模板': () => showToast('模板切换面板已打开', 'info'),
            '试看导出': () => _createQuickTask('试看导出', 'publish', '来源页面：' + currentRoute, '试看导出任务已创建'),
            '添加批注': () => showToast('批注模式已开启', 'info'),
            '导入素材': () => _pickFilesAndImportAssets(currentRoute),
            '发起终版导出': () => _createQuickTask('终版导出', 'publish', '来源页面：视频剪辑', '终版导出任务已创建'),
            '切换剪辑序列': () => showToast('已切换到剪辑序列选择模式', 'info'),
            '画布': (btn) => {
                _setExclusiveButtonState(btn);
                showToast('已切换到画布工具', 'info');
            },
            '文字': (btn) => {
                _setExclusiveButtonState(btn);
                showToast('已切换到文字工具', 'info');
            },
            '贴纸': (btn) => {
                _setExclusiveButtonState(btn);
                showToast('已切换到贴纸工具', 'info');
            },
            '导出': (btn) => {
                _setExclusiveButtonState(btn);
                showToast('已切换到导出工具', 'info');
            },
            '回到开头': () => showToast('播放头已回到开头', 'info'),
            '逐帧': () => showToast('已切换到逐帧预览', 'info'),
            '设入点': () => showToast('已设置入点', 'success'),
            '设出点': () => showToast('已设置出点', 'success'),
            '锁定版本': () => showToast('当前版本已锁定', 'success'),
            '生成对比': () => showToast('已生成版本对比草稿', 'info'),
            '保存工作流': () => _createWorkflowDefinitionFromRoute(),
            '运行批次': () => _createQuickTask('工作流批次', 'publish', '来源页面：' + currentRoute, '运行批次已加入队列'),
        });
    }

    if (generationRoutes.includes(currentRoute)) {
        Object.assign(groupHandlers, {
            '连接测试': () => showToast('连接测试已发起', 'info'),
            '保存并应用': () => showToast('配置已保存并应用', 'success'),
            '批量打标签': () => showToast('批量标签工具已就绪', 'info'),
            '上传素材': () => _pickFilesAndImportAssets(currentRoute),
            '保存标题库': () => _createQuickTask('标题库保存', 'report', '来源页面：' + currentRoute, '标题库保存任务已创建'),
            'AI 智能优化': () => _createQuickTask('AI 标题优化', 'report', '来源页面：' + currentRoute, '标题优化任务已加入队列'),
            '插入标签': () => showToast('标签面板已切换到可插入状态', 'info'),
            '生成新方案': () => _createQuickTask('生成新方案', 'report', '来源页面：' + currentRoute, '新方案生成任务已创建'),
            '导入样本内容': () => _pickFilesAndImportAssets(currentRoute),
            '开始提取': () => _createQuickTask('脚本提取', 'report', '来源页面：脚本提取器', '脚本提取任务已创建'),
            '导入 SKU 列表': () => _pickFilesAndImportAssets(currentRoute),
            '立即优化': () => _createQuickTask('优化任务', 'report', '来源页面：' + currentRoute, '优化任务已加入队列'),
            '选择投放渠道': () => showToast('已打开投放渠道选择器', 'info'),
            '立即生成文案': () => _createQuickTask('文案生成', 'report', '来源页面：AI 文案生成', '文案生成任务已创建'),
            '导出合规报告': () => _exportThroughBackend('合规报告', ['来源页面: ' + currentRoute, '状态: 手动导出'], '合规报告已导出'),
            '选择模板集': () => showToast('模板集选择器已打开', 'info'),
            '启动批量生产': () => _createQuickTask('批量生产', 'publish', '来源页面：AI 内容工厂', '批量生产任务已加入队列'),
            '保存': () => currentRoute === 'ai-content-factory' ? _createWorkflowDefinitionFromRoute() : showToast('已保存当前内容', 'success'),
            '运行工作流': () => _createWorkflowRunFromRoute(),
        });
    }

    if (analyticsRoutes.includes(currentRoute)) {
        Object.assign(groupHandlers, {
            '保存实验视图': () => _createExperimentProjectFromRoute('visual-lab'),
            '生成新报表': () => _createReportRunFromRoute(),
            '趋势': () => showToast('已切换到趋势视图', 'info'),
            '对比': () => showToast('已切换到对比视图', 'info'),
            '分布': () => showToast('已切换到分布视图', 'info'),
            '小时': () => showToast('已切换到小时维度', 'info'),
            '日': () => showToast('已切换到日维度', 'info'),
            '周': () => showToast('已切换到周维度', 'info'),
            '月': () => showToast('已切换到月维度', 'info'),
            '季': () => showToast('已切换到季度维度', 'info'),
            '1D': () => showToast('已切换到 1D 视图', 'info'),
            '1W': () => showToast('已切换到 1W 视图', 'info'),
            '1M': () => showToast('已切换到 1M 视图', 'info'),
        });
    }

    const routeHandlers = {
        account: {
            '导出账号清单': () => {
                api.accounts.list().then((accounts) => {
                    const rows = [['ID', '用户名', '平台', '地区', '状态', '粉丝数']]
                        .concat((accounts || []).map((item) => [
                            item.id || '',
                            item.username || '',
                            item.platform || '',
                            item.region || '',
                            item.status || '',
                            item.followers || 0,
                        ]));
                    const csv = rows.map((row) => row.map((cell) => {
                        const value = String(cell == null ? '' : cell).replace(/"/g, '""');
                        return '"' + value + '"';
                    }).join(',')).join('\r\n');
                    _downloadTextFile('accounts-export.csv', '\uFEFF' + csv, 'text/csv;charset=utf-8');
                    showToast('账号清单已导出', 'success');
                }).catch((err) => {
                    showToast('导出失败: ' + ((err && err.message) || '未知错误'), 'error');
                });
            },
        },
        'ai-provider': {
            'Reset to Default': () => _resetSelectedProviderDefaults(),
            '恢复默认': () => _resetSelectedProviderDefaults(),
            '保存变更': () => _openSelectedProviderEditModal(),
            'Save Changes': () => _openSelectedProviderEditModal(),
            '基础设置': (btn) => {
                _setExclusiveButtonState(btn);
                showToast('已切换到基础设置', 'info');
            },
            'AI 配置': (btn) => {
                _setExclusiveButtonState(btn);
                showToast('已切换到 AI 配置', 'info');
            },
            'TTS 服务': (btn) => {
                _setExclusiveButtonState(btn);
                showToast('已切换到 TTS 服务', 'info');
            },
            '浏览器隔离': (btn) => {
                _setExclusiveButtonState(btn);
                showToast('已切换到浏览器隔离', 'info');
            },
            'General': (btn) => {
                _setExclusiveButtonState(btn);
                showToast('已切换到 General', 'info');
            },
            'AI Configuration': (btn) => {
                _setExclusiveButtonState(btn);
                showToast('已切换到 AI Configuration', 'info');
            },
            'TTS Services': (btn) => {
                _setExclusiveButtonState(btn);
                showToast('已切换到 TTS Services', 'info');
            },
            'Browser Isolation': (btn) => {
                _setExclusiveButtonState(btn);
                showToast('已切换到 Browser Isolation', 'info');
            },
        },
        'task-queue': {
            '批量开始': () => _batchStartSelectedTasks(),
        },
        'group-management': {
            '导出分组结构': () => {
                api.groups.list().then((groups) => {
                    const rows = (groups || []).map((item) => [item.id || '', item.name || '', item.description || '', item.color || '']);
                    return _exportThroughBackend('分组结构导出', rows.map((row) => row.join(' | ')), '分组结构已导出');
                }).catch((err) => showToast('导出失败: ' + ((err && err.message) || '未知错误'), 'error'));
            },
        },
        'device-management': {
            '导出设备报告': () => {
                api.devices.list().then((devices) => {
                    const lines = (devices || []).map((item) => [item.device_code || '', item.name || '', item.region || '', item.status || ''].join(' | '));
                    return _exportThroughBackend('设备环境报告', lines, '设备报告已导出');
                }).catch((err) => showToast('导出失败: ' + ((err && err.message) || '未知错误'), 'error'));
            },
            '批量巡检': () => _runDiagnostics('设备巡检'),
            '批量修复': () => _createQuickTask('设备批量修复', 'maintenance', '来源页面：设备环境管理', '批量修复任务已创建'),
            '修复环境': () => _createQuickTask('环境修复', 'maintenance', '来源页面：设备环境管理', '环境修复任务已创建'),
            '环境日志': () => {
                api.logs.recent().then((logs) => {
                    const lines = (logs && logs.lines) || [];
                    return _exportThroughBackend('设备环境日志', lines, '环境日志已导出');
                }).catch((err) => showToast('导出失败: ' + ((err && err.message) || '未知错误'), 'error'));
            },
            '调整绑定': (btn) => _openDeviceBindingModal(btn),
            '修改绑定': (btn) => _openDeviceBindingModal(btn),
            '打开环境': () => _createNamedTaskAction('device_open_environment', {
                title: '打开设备环境',
                summary: '来源页面：设备环境管理 / 打开环境',
                metadata: { route: 'device-management', device_id: _selectedDeviceId() },
            }, '设备环境启动任务已创建'),
            '查看详情': () => showToast('详情已同步到右侧面板', 'info'),
        },
        'asset-center': {
            '上传素材': () => _pickFilesAndImportAssets(currentRoute),
            '导入素材': () => _pickFilesAndImportAssets(currentRoute),
            '新建素材': () => typeof openAssetForm === 'function' ? openAssetForm() : null,
            '批量打标签': () => _openAssetTagBatchModal(),
        },
        dashboard: {
            '查看历史': () => {
                uiState['task-queue'] = uiState['task-queue'] || { statusFilter: 'all' };
                uiState['task-queue'].statusFilter = 'all';
                return typeof renderRoute === 'function' ? renderRoute('task-queue') : null;
            },
            'View History': () => {
                uiState['task-queue'] = uiState['task-queue'] || { statusFilter: 'all' };
                uiState['task-queue'].statusFilter = 'all';
                return typeof renderRoute === 'function' ? renderRoute('task-queue') : null;
            },
            '查看全部': () => typeof renderRoute === 'function' ? renderRoute('report-center') : null,
            '新建任务': () => typeof openTaskForm === 'function' ? openTaskForm() : null,
            'Launch New Task': () => typeof openTaskForm === 'function' ? openTaskForm() : null,
            '今日': () => typeof window.__loadDashboardOverview === 'function' ? window.__loadDashboardOverview('today') : null,
            '近 7 天': () => typeof window.__loadDashboardOverview === 'function' ? window.__loadDashboardOverview('7d') : null,
            '近 30 天': () => typeof window.__loadDashboardOverview === 'function' ? window.__loadDashboardOverview('30d') : null,
            '处理账号异常': () => typeof renderRoute === 'function' ? renderRoute('account') : null,
            '启动内容批量生成': () => typeof renderRoute === 'function' ? renderRoute('ai-content-factory') : null,
            '网络诊断': () => typeof renderRoute === 'function' ? renderRoute('device-management') : null,
            '审核定时发布': () => typeof renderRoute === 'function' ? renderRoute('task-queue') : null,
        },
    };

    const handlers = Object.assign({}, groupHandlers, routeHandlers[currentRoute] || {});
    if (!Object.keys(handlers).length) return;

    mainHost.querySelectorAll('button').forEach((btn) => {
        const text = _buttonText(btn);
        const handler = handlers[text];
        if (!handler) return;
        if (btn.id || /(^|\s)js-/.test(btn.className || '')) return;
        _bindButtonAction(btn, 'tkopsPresetBound', () => handler(btn));
    });
}

function _bindFallbackActionButtons() {
    const mainHost = document.getElementById('mainHost');
    if (!mainHost) return;
    const selectors = [
        '.toolbar-strip__group button',
        '.transport-controls button',
        '.gen-output-actions button',
        '.title-editor-actions .header-actions button',
        '.ai-side-config-actions button',
        '.detail-actions .ghost-button',
        '.detail-actions .secondary-button',
        '.detail-actions .danger-button',
    ];
    selectors.forEach((selector) => {
        mainHost.querySelectorAll(selector).forEach((btn) => {
            if (btn.id || /(^|\s)js-/.test(btn.className || '')) return;
            if (btn.dataset.tkopsPresetBound === '1') return;
            _bindButtonAction(btn, 'tkopsFallbackBound', () => {
                const text = _buttonText(btn);
                showToast(text ? (text + ' 已响应，详细流程正在接入') : '操作已响应', 'info');
            });
        });
    });
}

function bindRouteInteractions() {
    bindSegmentedButtons();
    bindFilters();
    bindDetailTriggers();
    bindConfigNavItems();
    bindSourceBrowserTabs();
    bindMainItemClicks();
    bindTaskViewToggles();
    bindTaskFilterTabs();
    bindAssetCategoryFilter();
    bindAssetThumbDetail();
    bindChartToggles();
    bindDragAndDrop();
    bindAIConfigInteractions();
    renderCharts();
    bindAnalyticsInteractions();
    renderAnalyticsCanvases();
    _bindRouteButtonPresets();
    _bindSelectableButtonGroups();
    _bindFallbackActionButtons();
    applyCurrentRouteState();
    renderSearchPanel();
}

function bindConfigNavItems() {
    document.querySelectorAll('.config-nav-item').forEach((item) => {
        item.addEventListener('click', () => {
            item.closest('.config-nav').querySelectorAll('.config-nav-item').forEach((i) => i.classList.remove('is-selected'));
            item.classList.add('is-selected');
            // 滚动到对应表单分组
            const index = [...item.closest('.config-nav').querySelectorAll('.config-nav-item')].indexOf(item);
            const groups = document.querySelectorAll('.config-form-group');
            if (groups[index]) groups[index].scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    });
}

function bindSourceBrowserTabs() {
    document.querySelectorAll('.source-browser-tabs span').forEach((tab) => {
        tab.addEventListener('click', () => {
            tab.closest('.source-browser-tabs').querySelectorAll('span').forEach((t) => t.classList.remove('is-selected'));
            tab.classList.add('is-selected');
            // 实际筛选缩略图
            const label = tab.textContent.replace(/\d+/g, '').trim();
            const grid = tab.closest('.panel, .source-browser-shell')?.querySelector('.source-thumb-grid');
            if (grid) {
                grid.querySelectorAll('.source-thumb').forEach((thumb) => {
                    if (!label || label === '全部') {
                        thumb.classList.remove('is-filtered-out');
                    } else {
                        const text = thumb.textContent + [...thumb.querySelectorAll('.pill')].map((p) => p.textContent).join(' ');
                        thumb.classList.toggle('is-filtered-out', !text.includes(label));
                    }
                });
            }
        });
    });
    document.querySelectorAll('.source-thumb').forEach((thumb) => {
        thumb.addEventListener('click', () => {
            thumb.closest('.source-thumb-grid').querySelectorAll('.source-thumb').forEach((t) => t.classList.remove('is-selected'));
            thumb.classList.add('is-selected');
        });
    });
}

function syncResponsiveState() {
    const shell = document.getElementById('shellApp');
    const route = routes[currentRoute];
    const detailHost = document.getElementById('detailHost');
    const width = window.innerWidth;

    // 如果用户手动切换了面板，优先尊重用户选择
    if (uiState.detailPanelForced) {
        detailHost.classList.toggle('shell-hidden', uiState.detailPanelForced === 'hidden');
    } else {
        detailHost.classList.toggle('shell-hidden', route?.hideDetailPanel === true || width < 1180);
    }
    shell.classList.toggle('detail-hidden', detailHost.classList.contains('shell-hidden'));

    if (width < 960) {
        shell.classList.add('sidebar-collapsed');
        shell.classList.add('compact-mode');
    } else if (width < 1366) {
        shell.classList.add('sidebar-collapsed');
        shell.classList.remove('compact-mode');
    } else {
        shell.classList.remove('sidebar-collapsed');
        shell.classList.remove('compact-mode');
    }

    // 更新切换按钮状态
    const toggleBtn = document.getElementById('detailToggle');
    if (toggleBtn) {
        toggleBtn.classList.toggle('is-active', !detailHost.classList.contains('shell-hidden'));
    }
}

