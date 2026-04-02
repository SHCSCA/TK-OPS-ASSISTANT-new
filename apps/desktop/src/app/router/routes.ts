import AccountsPage from '../../pages/accounts/AccountsPage.vue';
import CopywriterPage from '../../pages/copywriter/CopywriterPage.vue';
import DashboardPage from '../../pages/dashboard/DashboardPage.vue';
import ProvidersPage from '../../pages/providers/ProvidersPage.vue';
import SchedulerPage from '../../pages/scheduler/SchedulerPage.vue';
import SettingsPage from '../../pages/settings/SettingsPage.vue';
import SetupWizardPage from '../../pages/setup/SetupWizardPage.vue';
import TasksPage from '../../pages/tasks/TasksPage.vue';

export const routes = [
  {
    path: '/',
    name: 'dashboard',
    component: DashboardPage,
    meta: {
      title: '概览看板',
      eyebrow: '总览工作台',
      shellGroup: 'overview',
      summary: '集中查看系统健康、核心指标、任务状态与最近动态。',
    },
  },
  {
    path: '/accounts',
    name: 'account-management',
    component: AccountsPage,
    meta: {
      title: '账号管理',
      eyebrow: '账号治理',
      shellGroup: 'ops',
      summary: '管理账号主数据、人工状态、系统状态、风险状态与批量动作。',
    },
  },
  {
    path: '/ai-copywriter',
    name: 'ai-copywriter',
    component: CopywriterPage,
    meta: {
      title: 'AI 文案生成',
      eyebrow: '内容创作',
      shellGroup: 'ai',
      summary: '通过真实 runtime 链路生成文案与流式结果。',
    },
  },
  {
    path: '/providers',
    name: 'ai-provider',
    component: ProvidersPage,
    meta: {
      title: 'AI 提供商',
      eyebrow: '系统配置',
      shellGroup: 'ai',
      summary: '统一维护模型提供商、连通性与默认模型配置。',
    },
  },
  {
    path: '/tasks',
    name: 'task-queue',
    component: TasksPage,
    meta: {
      title: '任务队列',
      eyebrow: '自动化运营',
      shellGroup: 'ops',
      summary: '查看任务运行、排队、失败与手动控制。',
    },
  },
  {
    path: '/scheduler',
    name: 'scheduler',
    component: SchedulerPage,
    meta: {
      title: '任务调度',
      eyebrow: '自动化运营',
      shellGroup: 'ops',
      summary: '管理计划任务、静默时段、启停切换与调度摘要。',
    },
  },
  {
    path: '/settings',
    name: 'settings',
    component: SettingsPage,
    meta: {
      title: '系统设置',
      eyebrow: '系统与工具',
      shellGroup: 'system',
      summary: '统一维护主题、系统参数与运行环境设置。',
    },
  },
  {
    path: '/setup-wizard',
    name: 'setup-wizard',
    component: SetupWizardPage,
    meta: {
      title: '初始化向导',
      eyebrow: '系统与工具',
      shellGroup: 'system',
      summary: '引导完成许可、提供商与基础环境初始化。',
    },
  },
];
