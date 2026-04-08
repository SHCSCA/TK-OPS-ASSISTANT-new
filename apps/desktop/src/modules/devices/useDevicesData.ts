import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';

import { runtimeApi } from '../runtime/runtimeApi';
import { useAsyncResource } from '../runtime/useAsyncResource';
import type { AccountItem, AccountUpsertPayload, DeviceItem, DeviceLogItem, DeviceUpsertPayload } from '../runtime/types';
import { useShellStore } from '../shell/useShellStore';

type Tone = 'info' | 'success' | 'warning' | 'error';
type DeviceStatusFilter = 'all' | 'healthy' | 'warning' | 'error' | 'idle';
type DeviceViewMode = 'card' | 'list';
type DeviceDetailAction = 'open-environment' | 'adjust-binding' | 'open-logs' | 'inspect-device' | 'edit-device' | 'delete-device' | 'toggle-logs';

interface DeviceDialogDraft {
  deviceId: number | null;
  deviceCode: string;
  name: string;
  proxyIp: string;
  region: string;
  status: string;
  proxyStatus: string;
  fingerprintStatus: string;
}

interface DeviceVM {
  id: number;
  deviceCode: string;
  name: string;
  status: string;
  statusLabel: string;
  statusTone: Tone;
  proxyStatus: string;
  proxyStatusLabel: string;
  proxyStatusTone: Tone;
  fingerprintStatus: string;
  fingerprintLabel: string;
  fingerprintTone: Tone;
  proxyLabel: string;
  regionLabel: string;
  boundCount: number;
  isolatedCount: number;
  coveragePercent: number;
  coverageLabel: string;
  lastInspectionLabel: string;
  sortOrder: number;
  boundAccounts: Array<{ id: number; username: string; isolationEnabled: boolean }>;
  issues: Array<{ title: string; copy: string; tone: Tone }>;
  raw: DeviceItem;
}

interface BindingDialogOption {
  accountId: number;
  username: string;
  regionLabel: string;
  tagsLabel: string;
  isolationLabel: string;
  selected: boolean;
}

const DEVICE_BANNER_DISMISS_KEY = 'tkops.device.notice.dismissed';

function relTime(value: string | null | undefined): string {
  if (!value) return '未记录';
  const t = Date.parse(String(value).replace(' ', 'T'));
  if (Number.isNaN(t)) return String(value);
  const diff = Date.now() - t;
  const minute = 60 * 1000;
  const hour = 60 * minute;
  const day = 24 * hour;
  if (diff < minute) return '刚刚';
  if (diff < hour) return `${Math.max(1, Math.round(diff / minute))} 分钟前`;
  if (diff < day) return `${Math.max(1, Math.round(diff / hour))} 小时前`;
  return `${Math.max(1, Math.round(diff / day))} 天前`;
}

function deviceStatusMeta(status: string | null | undefined): { label: string; tone: Tone; sortOrder: number; filter: DeviceStatusFilter } {
  const key = String(status || '').toLowerCase();
  if (key === 'healthy' || key === 'active') return { label: '正常', tone: 'success', sortOrder: 4, filter: 'healthy' };
  if (key === 'warning' || key === 'warming') return { label: '告警', tone: 'warning', sortOrder: 2, filter: 'warning' };
  if (key === 'idle' || key === 'offline') return { label: '空闲', tone: 'info', sortOrder: 3, filter: 'idle' };
  return { label: '异常', tone: 'error', sortOrder: 1, filter: 'error' };
}

function proxyStatusMeta(status: string | null | undefined): { label: string; tone: Tone } {
  const key = String(status || '').toLowerCase();
  if (['reachable', 'healthy', 'ready', 'ok'].includes(key)) return { label: '代理正常', tone: 'success' };
  if (['warning', 'degraded', 'slow'].includes(key)) return { label: '代理告警', tone: 'warning' };
  if (['idle', 'unknown', ''].includes(key)) return { label: '待检测', tone: 'info' };
  return { label: '代理异常', tone: 'error' };
}

function fingerprintMeta(status: string | null | undefined): { label: string; tone: Tone } {
  const key = String(status || '').toLowerCase();
  if (['ready', 'healthy', 'ok'].includes(key)) return { label: '指纹正常', tone: 'success' };
  if (['warning', 'changed'].includes(key)) return { label: '指纹待复核', tone: 'warning' };
  if (['idle', 'unknown', ''].includes(key)) return { label: '待确认', tone: 'info' };
  return { label: '指纹异常', tone: 'error' };
}

function regionLabel(value: string | null | undefined): string {
  const map: Record<string, string> = {
    US: '美国区',
    UK: '英国区',
    DE: '德国区',
    JP: '日本区',
    SG: '新加坡区',
    MY: '马来区',
    ID: '印尼区',
    TH: '泰国区',
    VN: '越南区',
    PH: '菲律宾区',
  };
  return map[String(value || '').toUpperCase()] || (value || '未知地区');
}

function parseAccountTags(raw: string | null | undefined): string[] {
  return String(raw || '').split(/[，,]/).map((item) => item.trim()).filter(Boolean);
}

function toAccountUpsertPayload(account: AccountItem, patch: Partial<AccountUpsertPayload> = {}): AccountUpsertPayload {
  const manualStatus = String(account.manualStatus || account.status || 'active');
  return {
    username: account.username,
    platform: account.platform || 'tiktok',
    region: account.region || 'US',
    status: manualStatus,
    manualStatus,
    riskStatus: String(account.riskStatus || 'unknown'),
    followers: Number.isFinite(Number(account.followers)) ? Math.max(0, Math.trunc(Number(account.followers))) : 0,
    groupId: account.groupId ?? null,
    groupName: account.groupName ?? null,
    deviceId: account.deviceId ?? null,
    cookieStatus: account.cookieStatus || 'unknown',
    cookieContent: account.cookieContent ?? null,
    isolationEnabled: Boolean(account.isolationEnabled),
    lastConnectionStatus: account.lastConnectionStatus || 'unknown',
    lastConnectionMessage: account.lastConnectionMessage ?? null,
    notes: account.notes ?? null,
    tags: account.tags ?? null,
    ...patch,
  };
}

function readBannerDismissed(): boolean {
  try {
    return window.sessionStorage.getItem(DEVICE_BANNER_DISMISS_KEY) === '1';
  } catch {
    return false;
  }
}

function writeBannerDismissed(value: boolean): void {
  try {
    window.sessionStorage.setItem(DEVICE_BANNER_DISMISS_KEY, value ? '1' : '0');
  } catch {
    // ignore
  }
}

function buildDeviceVM(device: DeviceItem, accounts: AccountItem[]): DeviceVM {
  const statusMeta = deviceStatusMeta(device.status);
  const proxyMeta = proxyStatusMeta(device.proxyStatus);
  const fingerprint = fingerprintMeta(device.fingerprintStatus);
  const boundAccounts = accounts
    .filter((account) => account.deviceId === device.id)
    .map((account) => ({
      id: account.id,
      username: account.username || `账号#${account.id}`,
      isolationEnabled: Boolean(account.isolationEnabled),
    }));
  const isolatedCount = boundAccounts.filter((item) => item.isolationEnabled).length;
  const coveragePercent = boundAccounts.length > 0 ? Math.round((isolatedCount / boundAccounts.length) * 100) : 0;
  const issues: Array<{ title: string; copy: string; tone: Tone }> = [];
  if (statusMeta.tone === 'error') {
    issues.push({ title: '设备状态异常', copy: '建议优先执行巡检或修复，确认代理和浏览器环境可正常打开。', tone: 'error' });
  }
  if (proxyMeta.tone !== 'success') {
    issues.push({ title: '代理状态待处理', copy: `当前代理状态为「${proxyMeta.label}」，建议复核代理链路与出口 IP。`, tone: proxyMeta.tone });
  }
  if (fingerprint.tone !== 'success') {
    issues.push({ title: '指纹状态待复核', copy: `当前指纹状态为「${fingerprint.label}」，建议确认环境指纹是否发生漂移。`, tone: fingerprint.tone });
  }
  if (boundAccounts.length > 0 && coveragePercent < 100) {
    issues.push({ title: '隔离覆盖率不足', copy: `当前仅覆盖 ${coveragePercent}% 的绑定账号，建议检查未隔离账号。`, tone: coveragePercent >= 60 ? 'warning' : 'error' });
  }

  return {
    id: device.id,
    deviceCode: device.deviceCode,
    name: device.name || '--',
    status: statusMeta.filter,
    statusLabel: statusMeta.label,
    statusTone: statusMeta.tone,
    proxyStatus: device.proxyStatus,
    proxyStatusLabel: proxyMeta.label,
    proxyStatusTone: proxyMeta.tone,
    fingerprintStatus: device.fingerprintStatus,
    fingerprintLabel: fingerprint.label,
    fingerprintTone: fingerprint.tone,
    proxyLabel: device.proxyIp?.trim() ? device.proxyIp : '未配置代理',
    regionLabel: regionLabel(device.region),
    boundCount: boundAccounts.length,
    isolatedCount,
    coveragePercent,
    coverageLabel: `${coveragePercent}% / 已隔离 ${isolatedCount} 个`,
    lastInspectionLabel: relTime(device.updatedAt || device.createdAt),
    sortOrder: statusMeta.sortOrder,
    boundAccounts,
    issues,
    raw: device,
  };
}

export function useDevicesData() {
  const shell = useShellStore();
  const resource = useAsyncResource(async () => {
    const [devices, accounts] = await Promise.all([
      runtimeApi.listDevices(),
      runtimeApi.listAccounts({ includeArchived: false }),
    ]);
    return { devices: devices.items, accounts: accounts.items };
  });

  const actionError = ref('');
  const actionMessage = ref('');
  const detailError = ref('');
  const workingAction = ref('');
  const statusFilterRef = ref<DeviceStatusFilter>('all');
  const viewMode = ref<DeviceViewMode>('card');
  const selectedDeviceId = ref<number | null>(null);
  const selectedDeviceIds = ref<number[]>([]);
  const batchMode = ref(false);
  const bannerDismissed = ref(readBannerDismissed());
  const deviceLogs = ref<Record<number, DeviceLogItem[]>>({});
  const logsCollapsed = ref(true);
  const dialogVisible = ref(false);
  const dialogSaving = ref(false);
  const dialogError = ref('');
  const dialogDraft = ref<DeviceDialogDraft | null>(null);
  const bindingDialogVisible = ref(false);
  const bindingDialogSaving = ref(false);
  const bindingDialogError = ref('');
  const bindingDialogTarget = ref<{ id: number; name: string } | null>(null);
  const bindingDialogOptions = ref<BindingDialogOption[]>([]);
  const deleteDialogVisible = ref(false);
  const deleteDialogWorking = ref(false);
  const deleteDialogError = ref('');
  const deleteDialogTarget = ref<{ id: number; name: string } | null>(null);

  const rawDevices = computed<DeviceItem[]>(() => resource.data.value?.devices || []);
  const rawAccounts = computed<AccountItem[]>(() => resource.data.value?.accounts || []);
  const allDevices = computed<DeviceVM[]>(() => rawDevices.value
    .map((device) => buildDeviceVM(device, rawAccounts.value))
    .sort((left, right) => {
      if (left.sortOrder !== right.sortOrder) return left.sortOrder - right.sortOrder;
      return left.name.localeCompare(right.name, 'zh-CN');
    }));

  const deviceStatusCounts = computed(() => {
    const counts = { all: allDevices.value.length, healthy: 0, warning: 0, error: 0, idle: 0 };
    allDevices.value.forEach((item) => {
      if (item.status === 'healthy' || item.status === 'warning' || item.status === 'error' || item.status === 'idle') {
        counts[item.status] += 1;
      }
    });
    return counts;
  });

  const devices = computed(() => statusFilterRef.value === 'all'
    ? allDevices.value
    : allDevices.value.filter((item) => item.status === statusFilterRef.value));

  const selectedDevice = computed(() => {
    if (typeof selectedDeviceId.value !== 'number') return null;
    return allDevices.value.find((item) => item.id === selectedDeviceId.value) || null;
  });

  const abnormalCount = computed(() => allDevices.value.filter((item) => item.status === 'error' || item.status === 'warning').length);
  const idleCount = computed(() => allDevices.value.filter((item) => item.status === 'idle').length);
  const totalAccountCount = computed(() => rawAccounts.value.length);
  const isolatedAccountCount = computed(() => rawAccounts.value.filter((account) => Boolean(account.isolationEnabled) && typeof account.deviceId === 'number').length);
  const uncoveredAccounts = computed(() => rawAccounts.value.filter((account) => !account.deviceId || !account.isolationEnabled));
  const isolationCoveragePercent = computed(() => totalAccountCount.value > 0 ? Math.round((isolatedAccountCount.value / totalAccountCount.value) * 100) : 0);
  const batchButtonText = computed(() => batchMode.value ? '删除已选设备' : '批量删除');
  const batchInspectButtonText = computed(() => batchMode.value ? '巡检已选设备' : '批量巡检');
  const bindingDialogSelectedCount = computed(() => bindingDialogOptions.value.filter((item) => item.selected).length);
  const bannerSummary = computed(() => {
    if (abnormalCount.value > 0) return `当前有 ${abnormalCount.value} 台设备待处理`;
    if (idleCount.value > 0) return `当前有 ${idleCount.value} 台空闲设备可调度`;
    return '当前设备环境整体稳定';
  });
  const bannerDetail = computed(() => {
    const examples = allDevices.value.filter((item) => item.status === 'error' || item.status === 'warning').slice(0, 2).map((item) => item.name);
    if (examples.length) return `优先处理：${examples.join('、')}。巡检结果和环境日志会同步到右侧详情区。`;
    return '设备列表已按真实代理、指纹和绑定关系归类，可直接进入环境调度。';
  });

  function clearFeedback(): void {
    actionError.value = '';
    actionMessage.value = '';
  }

  function setError(message: string): void {
    actionError.value = message;
    actionMessage.value = '';
  }

  function setMessage(message: string): void {
    actionMessage.value = message;
    actionError.value = '';
  }

  function byDeviceId(deviceId: number): DeviceItem | null {
    return rawDevices.value.find((item) => item.id === deviceId) || null;
  }

  function toggleDeviceSelection(deviceId: number, checked: boolean): void {
    const next = new Set(selectedDeviceIds.value);
    if (checked) next.add(deviceId);
    else next.delete(deviceId);
    selectedDeviceIds.value = Array.from(next);
  }

  function isDeviceChecked(deviceId: number): boolean {
    return selectedDeviceIds.value.includes(deviceId);
  }

  function syncDetailState(): void {
    const current = selectedDevice.value;
    if (!current) {
      shell.resetDeviceDetailState();
      return;
    }
    const logs = deviceLogs.value[current.id] || [];
    shell.setDeviceDetailState({
      kind: 'selected',
      deviceId: current.id,
      title: current.name,
      subtitle: `编码 ${current.deviceCode} · ${current.regionLabel}`,
      statusLabel: current.statusLabel,
      statusTone: current.statusTone,
      dataPoints: [
        { label: '代理状态', value: current.proxyStatusLabel },
        { label: '指纹状态', value: current.fingerprintLabel },
        { label: '绑定账号', value: `${current.boundCount} 个` },
        { label: '隔离覆盖', value: `${current.coveragePercent}%` },
        { label: '最近巡检', value: current.lastInspectionLabel },
        { label: '地区', value: current.regionLabel },
      ],
      issues: current.issues,
      logs: logs.map((item) => ({
        id: item.id,
        title: item.title || '设备日志',
        message: item.message || '系统记录已同步',
        category: item.category || 'log',
        createdAt: relTime(item.createdAt),
      })),
      logsCollapsed: logsCollapsed.value,
    });
  }

  async function loadDeviceLogs(deviceId: number, silent = false): Promise<void> {
    if (!silent) {
      detailError.value = '';
    }
    try {
      const response = await runtimeApi.getDeviceLogs(deviceId, 20);
      deviceLogs.value = {
        ...deviceLogs.value,
        [deviceId]: response.items,
      };
      syncDetailState();
    } catch (cause) {
      detailError.value = cause instanceof Error ? cause.message : '加载设备日志失败';
    }
  }

  async function selectDevice(deviceId: number): Promise<void> {
    if (selectedDeviceId.value === deviceId) {
      syncDetailState();
      return;
    }
    selectedDeviceId.value = deviceId;
    logsCollapsed.value = true;
    syncDetailState();
    await loadDeviceLogs(deviceId, true);
  }

  async function refreshDevices(): Promise<void> {
    await resource.load();
    if (typeof selectedDeviceId.value === 'number') {
      syncDetailState();
      await loadDeviceLogs(selectedDeviceId.value, true);
      return;
    }
    syncDetailState();
  }

  function setStatusFilter(value: DeviceStatusFilter): void {
    statusFilterRef.value = value;
  }

  function setViewMode(value: DeviceViewMode): void {
    viewMode.value = value;
  }

  function dismissBanner(): void {
    bannerDismissed.value = true;
    writeBannerDismissed(true);
    setMessage('本轮已隐藏设备提醒');
  }

  async function openDeviceEnvironment(deviceId: number): Promise<void> {
    clearFeedback();
    workingAction.value = 'open-environment';
    try {
      const result = await runtimeApi.openDeviceEnvironment(deviceId);
      const pid = result.pid > 0 ? `，PID ${result.pid}` : '';
      setMessage(`设备环境已启动：${result.name}${pid}`);
      await loadDeviceLogs(deviceId, true);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : '打开设备环境失败');
    } finally {
      workingAction.value = '';
    }
  }

  async function inspectDevice(deviceId: number): Promise<void> {
    clearFeedback();
    workingAction.value = 'inspect-device';
    try {
      const result = await runtimeApi.inspectDevice(deviceId);
      setMessage(`设备巡检完成：${result.ok ? '通过' : '存在问题'}${result.message ? `，${result.message}` : ''}`);
      await refreshDevices();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : '设备巡检失败');
    } finally {
      workingAction.value = '';
    }
  }

  async function repairDevice(deviceId: number): Promise<void> {
    clearFeedback();
    workingAction.value = 'repair-device';
    try {
      const result = await runtimeApi.repairDevice(deviceId);
      setMessage(`设备修复完成：${result.actions.length ? result.actions.join(' / ') : '已完成环境修复'}`);
      await refreshDevices();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : '设备修复失败');
    } finally {
      workingAction.value = '';
    }
  }

  function openBindingDialog(deviceId: number): void {
    clearFeedback();
    bindingDialogError.value = '';
    const target = allDevices.value.find((item) => item.id === deviceId);
    if (!target) {
      setError('设备不存在，无法调整绑定');
      return;
    }
    bindingDialogTarget.value = { id: target.id, name: target.name };
    bindingDialogOptions.value = rawAccounts.value
      .map((account) => ({
        accountId: account.id,
        username: account.username || `账号#${account.id}`,
        regionLabel: regionLabel(account.region),
        tagsLabel: parseAccountTags(account.tags).slice(0, 3).join(' / ') || '未打标签',
        isolationLabel: account.isolationEnabled ? '已隔离' : '未隔离',
        selected: account.deviceId === deviceId,
      }))
      .sort((left, right) => Number(right.selected) - Number(left.selected) || left.username.localeCompare(right.username, 'zh-CN'));
    bindingDialogVisible.value = true;
  }

  function closeBindingDialog(): void {
    bindingDialogVisible.value = false;
    bindingDialogSaving.value = false;
    bindingDialogError.value = '';
    bindingDialogTarget.value = null;
    bindingDialogOptions.value = [];
  }

  function toggleBindingAccount(accountId: number, checked: boolean): void {
    bindingDialogOptions.value = bindingDialogOptions.value.map((item) => item.accountId === accountId ? { ...item, selected: checked } : item);
  }

  function setAllBindingAccounts(checked: boolean): void {
    bindingDialogOptions.value = bindingDialogOptions.value.map((item) => ({ ...item, selected: checked }));
  }

  async function submitBindingDialog(): Promise<void> {
    if (!bindingDialogTarget.value || bindingDialogSaving.value) {
      return;
    }
    const targetName = bindingDialogTarget.value.name;
    bindingDialogSaving.value = true;
    bindingDialogError.value = '';
    workingAction.value = 'adjust-binding';
    try {
      const deviceId = bindingDialogTarget.value.id;
      const nextIds = new Set(bindingDialogOptions.value.filter((item) => item.selected).map((item) => item.accountId));
      const tasks: Promise<unknown>[] = [];

      rawAccounts.value.forEach((account) => {
        if (account.deviceId === deviceId && !nextIds.has(account.id)) {
          tasks.push(runtimeApi.updateAccount(account.id, toAccountUpsertPayload(account, { deviceId: null })));
          return;
        }
        if (nextIds.has(account.id) && account.deviceId !== deviceId) {
          tasks.push(runtimeApi.updateAccount(account.id, toAccountUpsertPayload(account, { deviceId })));
        }
      });

      await Promise.all(tasks);
      closeBindingDialog();
      window.dispatchEvent(new CustomEvent('tkops:accounts-refresh-requested'));
      setMessage(`设备绑定已更新：${targetName}`);
      await refreshDevices();
    } catch (cause) {
      bindingDialogError.value = cause instanceof Error ? cause.message : '保存绑定关系失败';
    } finally {
      bindingDialogSaving.value = false;
      workingAction.value = '';
    }
  }

  async function adjustBinding(deviceId: number): Promise<void> {
    openBindingDialog(deviceId);
  }

  function openCreateDialog(): void {
    clearFeedback();
    dialogError.value = '';
    dialogDraft.value = {
      deviceId: null,
      deviceCode: '',
      name: '',
      proxyIp: '',
      region: 'US',
      status: 'healthy',
      proxyStatus: 'unknown',
      fingerprintStatus: 'unknown',
    };
    dialogVisible.value = true;
  }

  function openEditDialog(deviceId: number): void {
    clearFeedback();
    dialogError.value = '';
    const source = byDeviceId(deviceId);
    if (!source) {
      setError('设备不存在，无法编辑');
      return;
    }
    dialogDraft.value = {
      deviceId: source.id,
      deviceCode: source.deviceCode,
      name: source.name || '',
      proxyIp: source.proxyIp || '',
      region: source.region || 'US',
      status: source.status || 'healthy',
      proxyStatus: source.proxyStatus || 'unknown',
      fingerprintStatus: source.fingerprintStatus || 'unknown',
    };
    dialogVisible.value = true;
  }

  function closeDialog(): void {
    dialogVisible.value = false;
    dialogSaving.value = false;
    dialogError.value = '';
    dialogDraft.value = null;
  }

  async function submitDialog(): Promise<void> {
    if (!dialogDraft.value || dialogSaving.value) return;
    const draft = dialogDraft.value;
    if (!draft.deviceCode.trim()) {
      dialogError.value = '设备编码不能为空';
      return;
    }
    if (!draft.name.trim()) {
      dialogError.value = '设备名称不能为空';
      return;
    }
    dialogSaving.value = true;
    dialogError.value = '';
    const payload: DeviceUpsertPayload = {
      deviceCode: draft.deviceCode.trim(),
      name: draft.name.trim(),
      proxyIp: draft.proxyIp.trim() || null,
      region: draft.region.trim() || 'US',
      status: draft.status.trim() || 'healthy',
      proxyStatus: draft.proxyStatus.trim() || 'unknown',
      fingerprintStatus: draft.fingerprintStatus.trim() || 'unknown',
    };
    try {
      if (typeof draft.deviceId === 'number') {
        await runtimeApi.updateDevice(draft.deviceId, payload);
        setMessage(`设备已更新：${draft.name.trim()}`);
      } else {
        await runtimeApi.createDevice(payload);
        setMessage(`已新增设备：${draft.name.trim()}`);
      }
      closeDialog();
      await refreshDevices();
    } catch (cause) {
      dialogError.value = cause instanceof Error ? cause.message : '保存设备失败';
    } finally {
      dialogSaving.value = false;
    }
  }

  function openDeleteDialog(deviceId: number): void {
    clearFeedback();
    deleteDialogError.value = '';
    const target = allDevices.value.find((item) => item.id === deviceId);
    if (!target) {
      setError('设备不存在，无法删除');
      return;
    }
    deleteDialogTarget.value = { id: target.id, name: target.name };
    deleteDialogVisible.value = true;
  }

  function closeDeleteDialog(): void {
    deleteDialogVisible.value = false;
    deleteDialogWorking.value = false;
    deleteDialogError.value = '';
    deleteDialogTarget.value = null;
  }

  async function confirmDeleteDialog(): Promise<void> {
    if (!deleteDialogTarget.value || deleteDialogWorking.value) return;
    deleteDialogWorking.value = true;
    deleteDialogError.value = '';
    try {
      await runtimeApi.deleteDevice(deleteDialogTarget.value.id);
      setMessage(`设备已删除：${deleteDialogTarget.value.name}`);
      window.dispatchEvent(new CustomEvent('tkops:accounts-refresh-requested'));
      closeDeleteDialog();
      if (selectedDeviceId.value === deleteDialogTarget.value.id) {
        selectedDeviceId.value = null;
      }
      await refreshDevices();
    } catch (cause) {
      deleteDialogError.value = cause instanceof Error ? cause.message : '删除设备失败';
    } finally {
      deleteDialogWorking.value = false;
    }
  }

  async function runBatchDelete(): Promise<void> {
    if (!batchMode.value) {
      batchMode.value = true;
      setMessage('已进入多选模式，请勾选设备后继续删除');
      return;
    }
    if (!selectedDeviceIds.value.length) {
      setError('请先勾选需要删除的设备');
      return;
    }
    workingAction.value = 'batch-delete';
    clearFeedback();
    try {
      await Promise.all(selectedDeviceIds.value.map((deviceId) => runtimeApi.deleteDevice(deviceId)));
      selectedDeviceIds.value = [];
      batchMode.value = false;
      setMessage('已删除选中的设备');
      window.dispatchEvent(new CustomEvent('tkops:accounts-refresh-requested'));
      await refreshDevices();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : '批量删除设备失败');
    } finally {
      workingAction.value = '';
    }
  }

  async function runBatchInspect(): Promise<void> {
    const ids = batchMode.value && selectedDeviceIds.value.length > 0 ? selectedDeviceIds.value.slice() : devices.value.map((item) => item.id);
    if (!ids.length) {
      setError('当前没有可巡检的设备');
      return;
    }
    clearFeedback();
    workingAction.value = 'batch-inspect';
    try {
      await Promise.all(ids.map((deviceId) => runtimeApi.inspectDevice(deviceId)));
      setMessage(`已完成 ${ids.length} 台设备的批量巡检`);
      await refreshDevices();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : '批量巡检设备失败');
    } finally {
      workingAction.value = '';
    }
  }

  function cancelBatchMode(): void {
    batchMode.value = false;
    selectedDeviceIds.value = [];
    setMessage('已退出多选模式');
  }

  function exportDeviceReport(): void {
    clearFeedback();
    if (!devices.value.length) {
      setError('当前没有可导出的设备');
      return;
    }
    const header = ['设备编码', '设备名称', '状态', '代理状态', '指纹状态', '地区', '绑定账号', '隔离覆盖'];
    const rows = devices.value.map((item) => [item.deviceCode, item.name, item.statusLabel, item.proxyStatusLabel, item.fingerprintLabel, item.regionLabel, `${item.boundCount}`, `${item.coveragePercent}%`]);
    const csv = `\ufeff${[header, ...rows].map((row) => row.map((field) => `"${String(field).replaceAll('"', '""')}"`).join(',')).join('\n')}`;
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `devices-${Date.now()}.csv`;
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);
    URL.revokeObjectURL(url);
    setMessage('设备报告导出完成');
  }

  function onDetailAction(event: Event): void {
    const detail = (event as CustomEvent<{ action?: DeviceDetailAction; deviceId?: number }>).detail;
    if (!detail || typeof detail.deviceId !== 'number') return;
    if (detail.action === 'open-environment') { void openDeviceEnvironment(detail.deviceId); return; }
    if (detail.action === 'adjust-binding') { openBindingDialog(detail.deviceId); return; }
    if (detail.action === 'open-logs') { void loadDeviceLogs(detail.deviceId); return; }
    if (detail.action === 'inspect-device') { void inspectDevice(detail.deviceId); return; }
    if (detail.action === 'edit-device') { openEditDialog(detail.deviceId); return; }
    if (detail.action === 'delete-device') { openDeleteDialog(detail.deviceId); return; }
    if (detail.action === 'toggle-logs') {
      logsCollapsed.value = !logsCollapsed.value;
      syncDetailState();
    }
  }

  watch(allDevices, (items) => {
    const ids = new Set(items.map((item) => item.id));
    selectedDeviceIds.value = selectedDeviceIds.value.filter((id) => ids.has(id));
  }, { immediate: true });

  watch(devices, (items) => {
    if (!items.length) {
      selectedDeviceId.value = null;
      shell.resetDeviceDetailState();
      return;
    }
    if (typeof selectedDeviceId.value === 'number' && items.some((item) => item.id === selectedDeviceId.value)) {
      syncDetailState();
      return;
    }
    void selectDevice(items[0].id);
  }, { immediate: true });

  watch([selectedDeviceId, allDevices], () => syncDetailState());

  onMounted(() => {
    window.addEventListener('tkops:device-detail-action', onDetailAction as EventListener);
  });

  onBeforeUnmount(() => {
    window.removeEventListener('tkops:device-detail-action', onDetailAction as EventListener);
    shell.resetDeviceDetailState();
  });

  return {
    devices,
    loading: resource.loading,
    error: resource.error,
    actionError,
    actionMessage,
    detailError,
    workingAction,
    statusFilter: statusFilterRef,
    viewMode,
    selectedDeviceId,
    selectedDeviceIds,
    batchMode,
    bannerDismissed,
    bannerSummary,
    bannerDetail,
    deviceStatusCounts,
    abnormalCount,
    idleCount,
    totalAccountCount,
    isolationCoveragePercent,
    uncoveredAccounts,
    batchButtonText,
    dialogVisible,
    dialogSaving,
    dialogError,
    dialogDraft,
    bindingDialogVisible,
    bindingDialogSaving,
    bindingDialogError,
    bindingDialogTarget,
    bindingDialogOptions,
    bindingDialogSelectedCount,
    deleteDialogVisible,
    deleteDialogWorking,
    deleteDialogError,
    deleteDialogTarget,
    refreshDevices,
    setStatusFilter,
    setViewMode,
    selectDevice,
    toggleDeviceSelection,
    isDeviceChecked,
    dismissBanner,
    openDeviceEnvironment,
    inspectDevice,
    repairDevice,
    adjustBinding,
    openBindingDialog,
    closeBindingDialog,
    toggleBindingAccount,
    setAllBindingAccounts,
    submitBindingDialog,
    openCreateDialog,
    openEditDialog,
    closeDialog,
    submitDialog,
    openDeleteDialog,
    closeDeleteDialog,
    confirmDeleteDialog,
    runBatchDelete,
    runBatchInspect,
    cancelBatchMode,
    exportDeviceReport,
    batchInspectButtonText,
  };
}