import type { RouteRecordRaw } from 'vue-router';

import AccountsPage from '../../pages/accounts/AccountsPage.vue';
import AssetCenterPage from '../../pages/assets/AssetCenterPage.vue';
import CopywriterPage from '../../pages/copywriter/CopywriterPage.vue';
import AiContentFactoryPage from '../../pages/content/AiContentFactoryPage.vue';
import DataCollectorPage from '../../pages/collector/DataCollectorPage.vue';
import CreativeWorkshopPage from '../../pages/content/CreativeWorkshopPage.vue';
import VideoEditorPage from '../../pages/content/VideoEditorPage.vue';
import DashboardPage from '../../pages/dashboard/DashboardPage.vue';
import DeviceManagementPage from '../../pages/devices/DeviceManagementPage.vue';
import ScheduledPublishPage from '../../pages/publish/ScheduledPublishPage.vue';
import ProvidersPage from '../../pages/providers/ProvidersPage.vue';
import SettingsPage from '../../pages/settings/SettingsPage.vue';
import SetupWizardPage from '../../pages/setup/SetupWizardPage.vue';
import MigrationPlaceholderPage from '../../pages/shared/MigrationPlaceholderPage.vue';
import TasksPage from '../../pages/tasks/TasksPage.vue';
import { shellRouteManifest } from './routeManifest';

const pageComponents = {
  dashboard: DashboardPage,
  accounts: AccountsPage,
  assetCenter: AssetCenterPage,
  deviceManagement: DeviceManagementPage,
  tasks: TasksPage,
  scheduledPublish: ScheduledPublishPage,
  dataCollector: DataCollectorPage,
  creativeWorkshop: CreativeWorkshopPage,
  aiContentFactory: AiContentFactoryPage,
  videoEditor: VideoEditorPage,
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
