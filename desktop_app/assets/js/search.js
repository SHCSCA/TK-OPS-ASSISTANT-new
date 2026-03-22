function matchSearch(element, keyword) {
    if (!keyword) {
        return true;
    }
    return (element.dataset.search || element.textContent || '').toLowerCase().includes(keyword);
}

function highlightMatches(elements, keyword) {
    elements.forEach((element) => {
        const visible = !element.classList.contains('is-filtered-out');
        const matched = keyword && matchSearch(element, keyword);
        element.classList.toggle('search-hit', Boolean(keyword && matched && visible));
    });
}

function applyNavSearch(keyword) {
    const navButtons = [...document.querySelectorAll('.nav-link[data-route]')];
    navButtons.forEach((button) => {
        const matched = !keyword || button.textContent.toLowerCase().includes(keyword) || (routes[button.dataset.route]?.searchTerms || '').toLowerCase().includes(keyword);
        button.classList.toggle('is-filtered-out', !matched);
    });
    highlightMatches(navButtons, keyword);
    return navButtons.filter((button) => !button.classList.contains('is-filtered-out'));
}

function applyDashboardState(keyword) {
    const items = [...document.getElementById('mainHost').querySelectorAll('[data-search]')];
    items.forEach((item) => item.classList.toggle('is-filtered-out', !matchSearch(item, keyword)));
    highlightMatches(items, keyword);
}

function applyAccountState(keyword) {
    const state = uiState.account;
    const collection = document.querySelector('[data-collection="accounts"]');
    if (!collection) {
        return;
    }

    collection.classList.toggle('list-mode', state.view === 'list');
    if (state.sortMode === 'anomaly') {
        [...collection.children]
            .sort((left, right) => Number(left.dataset.order || 999) - Number(right.dataset.order || 999))
            .forEach((item) => collection.appendChild(item));
    }

    const cards = [...collection.querySelectorAll('.account-card')];
    let visibleCount = 0;
    let selectedVisible = false;
    cards.forEach((card) => {
        const statusMatched = state.statusFilter === 'all' || card.dataset.status === state.statusFilter;
        const searchMatched = matchSearch(card, keyword);
        const visible = statusMatched && searchMatched;
        card.classList.toggle('is-filtered-out', !visible);
        if (visible && card.classList.contains('is-selected')) {
            selectedVisible = true;
        }
        if (visible) {
            visibleCount += 1;
        }
    });
    if (!selectedVisible) {
        const firstVisible = cards.find((card) => !card.classList.contains('is-filtered-out'));
        if (firstVisible) {
            updateDetail(firstVisible.dataset.detailTarget, firstVisible);
        }
    }
    highlightMatches(cards, keyword);
    ensureEmptyState(collection, visibleCount, '没有匹配的账号，请调整筛选条件或搜索关键词。');
}

function applyTaskState(keyword) {
    const state = uiState['task-queue'];
    const collection = document.querySelector('[data-collection="tasks"]');
    if (!collection) {
        return;
    }

    const rows = [...collection.querySelectorAll('.route-row')];
    let visibleCount = 0;
    rows.forEach((row) => {
        const statusMatched = state.statusFilter === 'all' || row.dataset.status === state.statusFilter;
        const searchMatched = matchSearch(row, keyword);
        const visible = statusMatched && searchMatched;
        row.classList.toggle('is-filtered-out', !visible);
        if (visible) {
            visibleCount += 1;
        }
    });
    highlightMatches(rows, keyword);
    ensureEmptyState(collection, visibleCount, '没有匹配的任务，请调整筛选条件或搜索关键词。');
}

function applyProviderState(keyword) {
    const rows = [...document.getElementById('mainHost').querySelectorAll('.route-row')];
    rows.forEach((row) => row.classList.toggle('is-filtered-out', !matchSearch(row, keyword)));
    highlightMatches(rows, keyword);
}

function applyGroupManagementState(keyword) {
    const items = [...document.getElementById('mainHost').querySelectorAll('.workbench-list .task-item')];
    let visibleCount = 0;
    items.forEach((item) => {
        const visible = matchSearch(item, keyword);
        item.classList.toggle('is-filtered-out', !visible);
        if (visible) visibleCount += 1;
    });
    highlightMatches(items, keyword);
    const host = document.querySelector('#mainHost .workbench-list');
    if (host) ensureEmptyState(host, visibleCount, '没有匹配的分组，请调整搜索关键词。');
}

function applyDeviceManagementState(keyword) {
    const state = uiState['device-management'];
    const cards = [...document.getElementById('mainHost').querySelectorAll('.device-env-grid .device-env-card')];
    let visibleCount = 0;
    cards.forEach((card) => {
        const status = card.dataset.status || 'all';
        const statusMatched = state.statusFilter === 'all' || status === state.statusFilter;
        const searchMatched = matchSearch(card, keyword);
        const visible = statusMatched && searchMatched;
        card.classList.toggle('is-filtered-out', !visible);
        if (visible) visibleCount += 1;
    });
    highlightMatches(cards, keyword);
    const host = document.querySelector('#mainHost .device-env-grid');
    if (host) ensureEmptyState(host, visibleCount, '没有匹配的设备，请调整筛选条件或搜索关键词。');
}

function applyAssetCenterState(keyword) {
    const items = [...document.getElementById('mainHost').querySelectorAll('.asset-source-grid .source-thumb')];
    let visibleCount = 0;
    items.forEach((item) => {
        const visible = matchSearch(item, keyword);
        item.classList.toggle('is-filtered-out', !visible);
        if (visible) visibleCount += 1;
    });
    highlightMatches(items, keyword);
    const host = document.querySelector('#mainHost .asset-source-grid');
    if (host) ensureEmptyState(host, visibleCount, '没有匹配的素材，请调整搜索关键词。');
}

function applyGenericState(keyword) {
    const items = [...document.getElementById('mainHost').querySelectorAll('[data-search]')];
    items.forEach((element) => element.classList.toggle('is-filtered-out', !matchSearch(element, keyword)));
    highlightMatches(items, keyword);
}

function applyCurrentRouteState() {
    const keyword = uiState.globalSearch.trim().toLowerCase();
    applyNavSearch(keyword);

    if (currentRoute === 'account') {
        applyAccountState(keyword);
    } else if (currentRoute === 'group-management') {
        applyGroupManagementState(keyword);
    } else if (currentRoute === 'device-management') {
        applyDeviceManagementState(keyword);
    } else if (currentRoute === 'task-queue') {
        applyTaskState(keyword);
    } else if (currentRoute === 'asset-center') {
        applyAssetCenterState(keyword);
    }
}

function renderRecentRoutes() {
    const host = document.getElementById('recentRoutes');
    if (!uiState.recentRoutes.length) {
        host.innerHTML = '<button class="search-result-item" type="button" disabled><strong>暂无最近访问</strong><span class="subtle">打开页面后会在这里记录。</span></button>';
        return;
    }

    host.innerHTML = uiState.recentRoutes
        .map((routeKey) => {
            const navButton = document.querySelector(`.nav-link[data-route="${routeKey}"]`);
            const title = navButton ? navButton.textContent.trim() : routeKey;
            const route = routes[routeKey];
            return `<button class="search-result-item" data-search-route="${routeKey}" type="button"><strong>${title}</strong><span class="subtle">${route.eyebrow}</span></button>`;
        })
        .join('');
}

function collectSearchResults(keyword) {
    const normalized = keyword.trim().toLowerCase();
    const results = [];
    const navButtons = [...document.querySelectorAll('.nav-link[data-route]')];
    navButtons.forEach((button) => {
        const routeKey = button.dataset.route;
        const route = routes[routeKey];
        const haystack = `${button.textContent} ${(route.searchTerms || '')}`.toLowerCase();
        if (!normalized || haystack.includes(normalized)) {
            results.push({ type: 'route', routeKey, title: button.textContent.trim(), subtitle: route.eyebrow });
        }
    });

    const pageHits = [...document.getElementById('mainHost').querySelectorAll('[data-search]')]
        .filter((element) => matchSearch(element, normalized))
        .slice(0, 4)
        .map((element) => ({
            type: 'detail',
            routeKey: currentRoute,
            title: element.querySelector('strong')?.textContent || element.textContent.trim().slice(0, 24),
            subtitle: '当前页面命中',
            detailTarget: element.dataset.detailTarget || '',
        }));

    return [...results.slice(0, 7), ...pageHits].slice(0, 8);
}

function highlightKeyword(text, keyword) {
    if (!keyword) {
        return text;
    }
    const escaped = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    return text.replace(new RegExp(escaped, 'ig'), (match) => `<span class="search-highlight-text">${match}</span>`);
}

function renderSearchPanel() {
    const panel = document.getElementById('searchPanel');
    const resultsHost = document.getElementById('searchResults');
    const keyword = uiState.globalSearch.trim().toLowerCase();
    uiState.searchPanel.results = collectSearchResults(keyword);
    uiState.searchPanel.activeIndex = Math.min(uiState.searchPanel.activeIndex, Math.max(uiState.searchPanel.results.length - 1, 0));

    if (!uiState.searchPanel.results.length) {
        resultsHost.innerHTML = '<button class="search-result-item" type="button" disabled><strong>未找到匹配项</strong><span class="subtle">可以尝试搜索页面名称、业务词或账号关键字。</span></button>';
    } else {
        resultsHost.innerHTML = uiState.searchPanel.results
            .map(
                (result, index) => `
                    <button class="search-result-item ${index === uiState.searchPanel.activeIndex ? 'is-active' : ''}" data-search-route="${result.routeKey}" ${result.detailTarget ? `data-detail-target="${result.detailTarget}"` : ''} type="button">
                        <strong>${highlightKeyword(result.title, keyword)}</strong>
                        <span class="subtle">${highlightKeyword(result.subtitle, keyword)}</span>
                    </button>
                `
            )
            .join('');
    }

    renderRecentRoutes();
    panel.classList.toggle('shell-hidden', !uiState.searchPanel.visible);

    panel.querySelectorAll('[data-search-route]').forEach((button) => {
        button.addEventListener('click', () => {
            const routeKey = button.dataset.searchRoute;
            const detailTarget = button.dataset.detailTarget;
            renderRoute(routeKey);
            uiState.searchPanel.visible = false;
            renderSearchPanel();
            if (detailTarget) {
                const source = document.querySelector(`[data-detail-target="${detailTarget}"]`);
                if (source) {
                    updateDetail(detailTarget, source);
                }
            }
        });
    });
}

function handleSearchNavigation(event) {
    if (!uiState.searchPanel.visible || !uiState.searchPanel.results.length) {
        return false;
    }

    if (event.key === 'ArrowDown') {
        uiState.searchPanel.activeIndex = (uiState.searchPanel.activeIndex + 1) % uiState.searchPanel.results.length;
        renderSearchPanel();
        return true;
    }
    if (event.key === 'ArrowUp') {
        uiState.searchPanel.activeIndex = (uiState.searchPanel.activeIndex - 1 + uiState.searchPanel.results.length) % uiState.searchPanel.results.length;
        renderSearchPanel();
        return true;
    }
    if (event.key === 'Escape') {
        uiState.searchPanel.visible = false;
        renderSearchPanel();
        return true;
    }
    if (event.key === 'Enter') {
        const active = uiState.searchPanel.results[uiState.searchPanel.activeIndex];
        if (active) {
            renderRoute(active.routeKey);
            uiState.searchPanel.visible = false;
            renderSearchPanel();
            if (active.detailTarget) {
                const source = document.querySelector(`[data-detail-target="${active.detailTarget}"]`);
                if (source) {
                    updateDetail(active.detailTarget, source);
                }
            }
        }
        return true;
    }
    return false;
}

function bindSearch() {
    const input = document.getElementById('globalSearch');
    input.addEventListener('focus', () => {
        uiState.searchPanel.visible = true;
        renderSearchPanel();
    });

    input.addEventListener('input', () => {
        uiState.globalSearch = input.value;
        uiState.searchPanel.visible = true;
        uiState.searchPanel.activeIndex = 0;
        applyCurrentRouteState();
        renderSearchPanel();
    });

    input.addEventListener('keydown', (event) => {
        if (handleSearchNavigation(event)) {
            event.preventDefault();
        }
    });

    document.addEventListener('click', (event) => {
        if (!event.target.closest('.shell-search-bar')) {
            uiState.searchPanel.visible = false;
            renderSearchPanel();
        }
    });
}

