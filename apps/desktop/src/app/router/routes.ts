import type { RouteRecordRaw } from 'vue-router';

import AccountsPage from '../../pages/accounts/AccountsPage.vue';
import CopywriterPage from '../../pages/copywriter/CopywriterPage.vue';
import DashboardPage from '../../pages/dashboard/DashboardPage.vue';
import ProvidersPage from '../../pages/providers/ProvidersPage.vue';
import SchedulerPage from '../../pages/scheduler/SchedulerPage.vue';
import SettingsPage from '../../pages/settings/SettingsPage.vue';
import SetupWizardPage from '../../pages/setup/SetupWizardPage.vue';
import MigrationPlaceholderPage from '../../pages/shared/MigrationPlaceholderPage.vue';
import TasksPage from '../../pages/tasks/TasksPage.vue';
import { shellRouteManifest } from './routeManifest';

const pageComponents = {
  dashboard: DashboardPage,
  accounts: AccountsPage,
  tasks: TasksPage,
  scheduler: SchedulerPage,
  copywriter: CopywriterPage,
  providers: ProvidersPage,
  setup: SetupWizardPage,
  settings: SettingsPage,
  placeholder: MigrationPlaceholderPage,
} as const;

export const routes: RouteRecordRaw[] = shellRouteManifest.map((item) => {
  const route: RouteRecordRaw = {
    path: item.path,
    name: item.name,
    component: pageComponents[item.pageKind],
    meta: {
      title: item.title,
      eyebrow: item.eyebrow,
      summary: item.summary,
      navGroup: item.navGroup,
      navOrder: item.navOrder,
      legacyRouteKey: item.legacyRouteKey,
      migrationStatus: item.migrationStatus,
    },
  };

  if (item.aliases?.length) {
    route.alias = item.aliases;
  }

  return route;
});
