const RECENT_ROUTES_KEY = 'tkops.recentRoutes';

const uiState = {
    globalSearch: '',
    account: { statusFilter: 'all', view: 'card', sortMode: 'default' },
    'group-management': { keyword: '', selectedId: null },
    'device-management': { statusFilter: 'all', view: 'card', selectedId: null },
    'task-queue': { statusFilter: 'all' },
    'asset-center': { category: 'all', keyword: '', selectedId: null },
    searchPanel: { visible: false, activeIndex: 0, results: [] },
    recentRoutes: [],
    detailPanelForced: null,
    notifications: [],
    notificationId: 0,
    shellRuntime: {
        defaultSummary: null,
        routeSummary: null,
        license: null,
        notifications: null,
        update: null,
        onboarding: null,
        boot: { stage: 'idle', ready: false, error: '' },
        systemStatus: {
            license: null,
            notifications: null,
            update: null,
            onboarding: null,
            boot: { stage: 'idle', ready: false, error: '' },
        },
    },
};

uiState['group-management'] = uiState['group-management'] || { keyword: '', selectedId: null };
uiState['device-management'] = uiState['device-management'] || { statusFilter: 'all', view: 'card', selectedId: null };
uiState['task-queue'] = uiState['task-queue'] || { statusFilter: 'all' };
uiState['asset-center'] = uiState['asset-center'] || { category: 'all', keyword: '', selectedId: null };

