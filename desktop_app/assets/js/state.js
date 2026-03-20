const RECENT_ROUTES_KEY = 'tkops.recentRoutes';

const uiState = {
    globalSearch: '',
    account: { statusFilter: 'all', view: 'card', sortMode: 'default' },
    'task-queue': { statusFilter: 'all' },
    searchPanel: { visible: false, activeIndex: 0, results: [] },
    recentRoutes: [],
    detailPanelForced: null,
    notifications: [],
    notificationId: 0,
};

