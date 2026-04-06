import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';

import { runtimeApi } from '../runtime/runtimeApi';
import { useAsyncResource } from '../runtime/useAsyncResource';
import type { AccountDetail, AccountItem, AccountListQuery, AccountUpsertPayload } from '../runtime/types';
import { useShellStore } from '../shell/useShellStore';

type AccountStatusFilter = 'all' | 'online' | 'offline' | 'exception';
type AccountViewMode = 'card' | 'list';
type Tone = 'info' | 'success' | 'warning' | 'error';
type DetailAction =
  | 'open-environment'
  | 'manage-cookies'
  | 'rebind-validate'
  | 'validate-login'
  | 'test-connection'
  | 'edit-account'
  | 'delete-account';

interface EditDialogDraft {
  accountId: number;
  username: string;
  platform: string;
  region: string;
  status: string;
  deviceId: string;
  tags: string;
  cookieStatus: string;
  cookieContent: string;
  followers: number;
  notes: string;
}

interface AdviceItem {
  title: string;
  copy: string;
  badge: string;
  tone: Tone;
}

interface AccountVM {
  id: number;
  username: string;
  subtitle: string;
  statusLabel: string;
  statusTone: Tone;
  filterStatus: AccountStatusFilter;
  sortOrder: number;
  platformLabel: string;
  regionLabel: string;
  followers: number;
  tags: string[];
  notes: string;
  proxyLabel: string;
  cookieStatus: string;
  cookieLabel: string;
  cookieTone: Tone;
  cookieContentSummary: string;
  cookieContentRaw: string;
  cookieUpdatedLabel: string;
  loginCheckStatus: string;
  loginCheckLabel: string;
  loginCheckTone: Tone;
  loginCheckMessage: string;
  isolationEnabled: boolean;
  isolationLabel: string;
  lastLoginLabel: string;
  connectionLabel: string;
  connectionTone: Tone;
  connectionMessage: string;
  connectionScopeLabel: string;
  lastConnectionStatus: string;
  createdAt: string | null;
  raw: AccountItem;
}

const ISOLATION_NOTICE_KEY = 'tkops.account.isolation.notice.dismissed';
const LIST_QUERY: AccountListQuery = { includeArchived: false };

function splitTags(raw: string | null | undefined): string[] {
  const seen = new Set<string>();
  return String(raw || '').split(/[，,]/).map((x) => x.trim()).filter((x) => {
    if (!x || seen.has(x)) return false;
    seen.add(x);
    return true;
  });
}

function mergeTags(existing: string[] | null | undefined, incoming: string[]): string {
  return splitTags(`${(existing || []).join(',')},${incoming.join(',')}`).join(', ');
}

function relTime(value: string | null | undefined): string {
  if (!value) return '未记录';
  const t = Date.parse(String(value).replace(' ', 'T'));
  if (Number.isNaN(t)) return String(value);
  const diff = Date.now() - t;
  const m = 60 * 1000;
  const h = 60 * m;
  const d = 24 * h;
  if (diff < m) return '刚刚';
  if (diff < h) return `${Math.max(1, Math.round(diff / m))} 分钟前`;
  if (diff < d) return `${Math.max(1, Math.round(diff / h))} 小时前`;
  return `${Math.max(1, Math.round(diff / d))} 天前`;
}

function statusFilter(status: string | null | undefined): AccountStatusFilter {
  const s = String(status || '').toLowerCase();
  if (['active', 'online', 'warming', 'warning'].includes(s)) return 'online';
  if (['idle', 'offline'].includes(s)) return 'offline';
  return 'exception';
}

function statusLabel(status: string | null | undefined): string {
  const s = String(status || '').toLowerCase();
  if (['active', 'online'].includes(s)) return '在线';
  if (['idle', 'offline'].includes(s)) return '离线';
  if (['warming', 'warning'].includes(s)) return '预热中';
  if (['suspended', 'error'].includes(s)) return '异常';
  return status || '未知';
}

function statusTone(status: string | null | undefined): Tone {
  const s = String(status || '').toLowerCase();
  if (['active', 'online'].includes(s)) return 'success';
  if (['idle', 'offline'].includes(s)) return 'info';
  if (['warming', 'warning'].includes(s)) return 'warning';
  return 'error';
}

function statusOrder(status: string | null | undefined): number {
  const s = String(status || '').toLowerCase();
  if (['error', 'suspended'].includes(s)) return 1;
  if (['warning', 'warming'].includes(s)) return 2;
  if (['offline', 'idle'].includes(s)) return 3;
  return 4;
}

function platformLabel(v: string | null | undefined): string {
  const key = String(v || '').toLowerCase();
  if (key === 'tiktok_shop') return 'TikTok Shop';
  if (key === 'instagram') return 'Instagram';
  if (key === 'youtube') return 'YouTube';
  return 'TikTok';
}

function regionLabel(v: string | null | undefined): string {
  const m: Record<string, string> = { US: '美国区', UK: '英国区', DE: '德国区', SG: '新加坡区', MY: '马来区', JP: '日本区' };
  return m[String(v || '').toUpperCase()] || (v || '未知地区');
}

function cookieMeta(status: string | null | undefined): { status: string; label: string; tone: Tone } {
  const s = String(status || 'unknown').toLowerCase();
  if (s === 'valid') return { status: s, label: '有效', tone: 'success' };
  if (s === 'expiring') return { status: s, label: '48 小时内过期', tone: 'warning' };
  if (s === 'invalid') return { status: s, label: '已失效', tone: 'error' };
  if (s === 'missing') return { status: s, label: '缺失', tone: 'warning' };
  return { status: 'unknown', label: '待确认', tone: 'info' };
}

function loginMeta(account: AccountItem): { status: string; label: string; tone: Tone; message: string } {
  const s = String(account.lastLoginCheckStatus || 'unknown').toLowerCase();
  const at = account.lastLoginCheckAt;
  const msg = account.lastLoginCheckMessage || '';
  if (s === 'valid') return { status: s, label: at ? `已通过 / ${relTime(at)}` : '已通过', tone: 'success', message: msg || '最近一次真实登录态校验通过' };
  if (s === 'proxy_mismatch') return { status: s, label: at ? `代理冲突 / ${relTime(at)}` : '代理冲突', tone: 'warning', message: msg || '代理下登录态校验异常' };
  if (s === 'invalid') return { status: s, label: at ? `已失效 / ${relTime(at)}` : '已失效', tone: 'error', message: msg || '最近一次真实登录态校验失败' };
  return { status: 'unknown', label: at ? `未确认 / ${relTime(at)}` : '尚未校验', tone: at ? 'warning' : 'info', message: msg || '尚未执行真实登录态校验' };
}

function connMeta(account: AccountItem): { label: string; tone: Tone; message: string } {
  const s = String(account.lastConnectionStatus || 'unknown').toLowerCase();
  if (s === 'reachable') return { label: '代理最近可达', tone: 'success', message: account.lastConnectionMessage || '最近一次代理检测通过' };
  if (s === 'unreachable') return { label: account.lastConnectionCheckedAt ? `代理检测失败 / ${relTime(account.lastConnectionCheckedAt)}` : '代理检测失败', tone: 'error', message: account.lastConnectionMessage || '最近一次代理检测失败' };
  return { label: '尚未检测', tone: 'info', message: account.lastConnectionMessage || '尚未执行代理检测' };
}

function buildVM(account: AccountItem): AccountVM {
  const tags = splitTags(account.tags);
  const c = cookieMeta(account.cookieStatus);
  const l = loginMeta(account);
  const n = connMeta(account);
  return {
    id: account.id,
    username: account.username || '--',
    subtitle: `${regionLabel(account.region)} · ${tags.length ? tags.slice(0, 2).join(' · ') : (account.notes?.trim() || '待补充运营标签')}`,
    statusLabel: statusLabel(account.manualStatus || account.status),
    statusTone: statusTone(account.manualStatus || account.status),
    filterStatus: statusFilter(account.manualStatus || account.status),
    sortOrder: statusOrder(account.manualStatus || account.status),
    platformLabel: platformLabel(account.platform),
    regionLabel: regionLabel(account.region),
    followers: Number(account.followers || 0),
    tags,
    notes: account.notes?.trim() || '',
    proxyLabel: account.proxyIp?.trim() ? `${account.proxyIp} (${regionLabel(account.region).replace('区', '')})` : '未配置代理',
    cookieStatus: c.status,
    cookieLabel: c.label,
    cookieTone: c.tone,
    cookieContentSummary: String(account.cookieContent || '').trim() ? `已录入 ${String(account.cookieContent || '').trim().length} 字符` : '未录入',
    cookieContentRaw: String(account.cookieContent || ''),
    cookieUpdatedLabel: relTime(account.cookieUpdatedAt),
    loginCheckStatus: l.status,
    loginCheckLabel: l.label,
    loginCheckTone: l.tone,
    loginCheckMessage: l.message,
    isolationEnabled: Boolean(account.isolationEnabled),
    isolationLabel: account.isolationEnabled ? '已启用' : '未启用',
    lastLoginLabel: relTime(account.lastLoginAt),
    connectionLabel: n.label,
    connectionTone: n.tone,
    connectionMessage: n.message,
    connectionScopeLabel: account.proxyIp?.trim() ? '仅检测绑定代理是否可达，不校验平台登录态' : '当前仅支持检测已绑定代理的 TCP 可达性',
    lastConnectionStatus: String(account.lastConnectionStatus || 'unknown'),
    createdAt: account.createdAt,
    raw: account,
  };
}

function toUpsertPayload(account: AccountItem, patch: Partial<AccountUpsertPayload> = {}): AccountUpsertPayload {
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

function inferCookieStatus(current: string | null | undefined, content: string): string {
  if (!content.trim()) return 'missing';
  const normalized = String(current || '').toLowerCase();
  if (['valid', 'expiring', 'invalid'].includes(normalized)) return normalized;
  return 'valid';
}

function readDismissed(): boolean {
  try {
    return window.localStorage.getItem(ISOLATION_NOTICE_KEY) === '1';
  } catch {
    return false;
  }
}

function writeDismissed(value: boolean): void {
  try {
    window.localStorage.setItem(ISOLATION_NOTICE_KEY, value ? '1' : '0');
  } catch {
    // ignore
  }
}

function buildAdvice(vm: AccountVM): AdviceItem[] {
  const items: AdviceItem[] = [];
  if (!vm.isolationEnabled) items.push({ title: '隔离环境尚未启用', copy: '建议先进入环境，切到独立浏览器后再继续操作。', badge: '优先处理', tone: 'warning' });
  if (vm.cookieStatus === 'invalid' || vm.cookieStatus === 'missing') items.push({ title: 'Cookie 状态需要处理', copy: '当前状态会直接影响登录和自动化执行，建议先更新 Cookie。', badge: vm.cookieLabel, tone: vm.cookieTone });
  if (vm.loginCheckStatus === 'proxy_mismatch') items.push({ title: '代理下登录态校验异常', copy: vm.loginCheckMessage || '建议先重绑并校验。', badge: '代理冲突', tone: 'warning' });
  if (vm.lastConnectionStatus === 'unreachable') items.push({ title: '最近一次代理检测失败', copy: vm.connectionMessage || '请优先检查代理地址、网络和设备状态。', badge: '检测失败', tone: 'error' });
  if (!items.length) items.push({ title: '当前账号可继续处理', copy: '隔离环境、Cookie 与连接检测暂无明显阻塞。', badge: '已就绪', tone: 'success' });
  items.push({ title: '粉丝与标签复核', copy: `当前粉丝 ${vm.followers || 0}，标签为 ${vm.tags.length ? vm.tags.join(' / ') : '未配置'}。`, badge: '运营复核', tone: 'info' });
  return items.slice(0, 3);
}

function buildDutySummary(vm: AccountVM): { title: string; copy: string; badge: string; tone: Tone } {
  let risk = 0;
  const blockers: string[] = [];
  if (!vm.isolationEnabled) {
    risk += 2;
    blockers.push('先进入隔离环境');
  }
  if (vm.cookieStatus === 'invalid' || vm.cookieStatus === 'missing') {
    risk += 3;
    blockers.push('Cookie 需要修复');
  } else if (vm.cookieStatus === 'expiring') {
    risk += 1;
    blockers.push('Cookie 临近过期');
  }
  if (vm.loginCheckStatus === 'invalid') {
    risk += 3;
    blockers.push('登录态校验失败');
  } else if (vm.loginCheckStatus === 'proxy_mismatch') {
    risk += 2;
    blockers.push('代理下登录态异常');
  } else if (vm.loginCheckStatus !== 'valid' && vm.cookieContentRaw) {
    risk += 1;
    blockers.push('尚未做真实登录态校验');
  }
  if (vm.lastConnectionStatus === 'unreachable') {
    risk += 3;
    blockers.push('代理检测失败');
  }
  if (vm.filterStatus === 'exception') {
    risk += 2;
    blockers.push('账号处于异常状态');
  }
  if (risk >= 6) {
    return {
      title: '当前不建议直接值班操作',
      copy: `${blockers.join('，')}。建议先排障，再继续登录、导入或发布。`,
      badge: '高风险',
      tone: 'error',
    };
  }
  if (risk >= 3) {
    return {
      title: '建议先补齐环境条件',
      copy: `${blockers.join('，')}。完成这些准备后再继续主流程更稳妥。`,
      badge: '待处理',
      tone: 'warning',
    };
  }
  return {
    title: '当前账号可继续值班处理',
    copy: '关键环境条件已满足，可继续进入账号操作流程。',
    badge: '可执行',
    tone: 'success',
  };
}

export function useAccountsData() {
  const shell = useShellStore();
  const router = useRouter();
  const resource = useAsyncResource(() => runtimeApi.listAccounts(LIST_QUERY));

  const actionError = ref('');
  const actionMessage = ref('');
  const detailLoading = ref(false);
  const detailError = ref('');
  const statusFilterRef = ref<AccountStatusFilter>('all');
  const viewMode = ref<AccountViewMode>('card');
  const batchMode = ref(false);
  const selectedAccountId = ref<number | null>(null);
  const selectedAccountIds = ref<number[]>([]);
  const selectedDetail = ref<AccountDetail | null>(null);
  const selectedActivityCount = ref(0);
  const workingAction = ref('');
  const isolationNoticeDismissed = ref(readDismissed());
  const editDialogVisible = ref(false);
  const editDialogSaving = ref(false);
  const editDialogError = ref('');
  const editDialogDraft = ref<EditDialogDraft | null>(null);
  const editDialogDeviceOptions = ref<Array<{ id: number; label: string }>>([]);
  const deleteDialogVisible = ref(false);
  const deleteDialogWorking = ref(false);
  const deleteDialogError = ref('');
  const deleteDialogTarget = ref<{ id: number; username: string } | null>(null);
  let detailToken = 0;

  const rawAccounts = computed<AccountItem[]>(() => resource.data.value?.items || []);
  const allAccounts = computed<AccountVM[]>(() => rawAccounts.value.map(buildVM).sort((a, b) => {
    const ac = Date.parse(a.createdAt || '') || 0;
    const bc = Date.parse(b.createdAt || '') || 0;
    if (ac !== bc) return bc - ac;
    if (a.id !== b.id) return b.id - a.id;
    return a.sortOrder - b.sortOrder;
  }));
  const accountStatusCounts = computed(() => {
    const counts = { all: allAccounts.value.length, online: 0, offline: 0, exception: 0 };
    allAccounts.value.forEach((x) => { counts[x.filterStatus] += 1; });
    return counts;
  });
  const accounts = computed(() => statusFilterRef.value === 'all' ? allAccounts.value : allAccounts.value.filter((x) => x.filterStatus === statusFilterRef.value));
  const selectedCount = computed(() => selectedAccountIds.value.length);
  const batchTagButtonText = computed(() => batchMode.value ? '为已选账号打标签' : '批量打标签');
  const isolationPendingCount = computed(() => allAccounts.value.filter((x) => !x.isolationEnabled).length);
  const isolationBannerVisible = computed(() => !isolationNoticeDismissed.value && isolationPendingCount.value > 0);
  const isolationBannerCopy = computed(() => isolationPendingCount.value > 0
    ? `当前仍有 ${isolationPendingCount.value} 个账号未启用隔离环境，建议先完成浏览器隔离配置，再继续登录和导入。`
    : '当前账号已经全部启用隔离环境，可以继续执行批量登录和导入。');

  function clearFeedback() { actionError.value = ''; actionMessage.value = ''; }
  function setError(msg: string) { actionError.value = msg; actionMessage.value = ''; }
  function setMessage(msg: string) { actionMessage.value = msg; actionError.value = ''; }
  function byId(id: number): AccountItem | null { return rawAccounts.value.find((x) => x.id === id) || null; }

  function syncDetailState(): void {
    const selectedId = selectedAccountId.value;
    const selected = typeof selectedId === 'number' ? allAccounts.value.find((x) => x.id === selectedId) || null : null;
    if (!selected) {
      shell.resetAccountDetailState();
      return;
    }
    const source = selectedDetail.value && selectedDetail.value.id === selected.id ? buildVM(selectedDetail.value) : selected;
    const advice = buildAdvice(source);
    const dutySummary = buildDutySummary(source);
    shell.setAccountDetailState({
      kind: dutySummary.tone === 'success' ? 'selected' : 'advice',
      accountId: source.id,
      title: source.username,
      subtitle: `ID ${source.id} · ${source.subtitle}`,
      statusLabel: source.statusLabel,
      statusTone: source.statusTone,
      dataPoints: [
        { label: 'Cookie 状态', value: source.cookieLabel },
        { label: '登录态校验', value: source.loginCheckLabel },
        { label: '隔离环境', value: source.isolationLabel },
        { label: 'Cookie 更新', value: source.cookieUpdatedLabel },
        { label: '最近登录', value: source.lastLoginLabel },
        { label: '代理检测', value: source.connectionLabel },
      ],
      detailItems: [
        { label: '平台 / 区域', value: `${source.platformLabel} / ${source.regionLabel}` },
        { label: '代理地址', value: source.proxyLabel, stacked: true },
        { label: '检测范围', value: source.connectionScopeLabel, stacked: true },
        { label: 'Cookie 内容', value: source.cookieContentSummary },
        { label: '登录态说明', value: source.loginCheckMessage, stacked: true },
        { label: '标签', value: source.tags.length ? source.tags.join(' / ') : '未打标签', stacked: true },
        { label: '备注', value: source.notes || '暂无备注' },
        { label: '近期活动', value: selectedActivityCount.value > 0 ? `${selectedActivityCount.value} 条` : '暂无数据' },
      ],
      dutySummary,
      adviceItems: advice,
    });
  }

  async function loadAccountDetail(accountId: number): Promise<void> {
    detailLoading.value = true;
    detailError.value = '';
    const token = ++detailToken;
    try {
      const [detail, activity] = await Promise.all([
        runtimeApi.getAccountDetail(accountId),
        runtimeApi.getAccountActivity(accountId, { limit: 20 }),
      ]);
      if (token !== detailToken) return;
      selectedDetail.value = detail;
      selectedActivityCount.value = Number(activity.total || 0);
      syncDetailState();
    } catch (cause) {
      if (token !== detailToken) return;
      selectedDetail.value = null;
      selectedActivityCount.value = 0;
      detailError.value = cause instanceof Error ? cause.message : '加载账号详情失败';
      syncDetailState();
    } finally {
      if (token === detailToken) detailLoading.value = false;
    }
  }

  async function selectAccount(accountId: number): Promise<void> {
    if (selectedAccountId.value === accountId && selectedDetail.value?.id === accountId) return;
    selectedAccountId.value = accountId;
    await loadAccountDetail(accountId);
  }

  async function refreshAccounts(): Promise<void> {
    await resource.load();
    if (typeof selectedAccountId.value === 'number') await loadAccountDetail(selectedAccountId.value);
    else syncDetailState();
  }

  function setStatusFilter(value: AccountStatusFilter): void { statusFilterRef.value = value; }
  function setView(next: AccountViewMode): void { viewMode.value = next; }
  function toggleAccountSelection(accountId: number, checked: boolean): void {
    const set = new Set(selectedAccountIds.value);
    if (checked) set.add(accountId); else set.delete(accountId);
    selectedAccountIds.value = Array.from(set);
  }
  function isAccountChecked(accountId: number): boolean { return selectedAccountIds.value.includes(accountId); }

  async function openAccountEnvironment(accountId: number): Promise<void> {
    clearFeedback(); workingAction.value = 'open-environment';
    try {
      const result = await runtimeApi.openAccountEnvironment(accountId);
      const pid = result.pid > 0 ? `，PID ${result.pid}` : '';
      setMessage(`隔离环境已启动：${result.accountUsername}${pid}`);
      await refreshAccounts();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : '启动隔离环境失败');
    } finally { workingAction.value = ''; }
  }

  async function manageAccountCookies(accountId: number): Promise<void> {
    clearFeedback(); workingAction.value = 'manage-cookies';
    try {
      if (typeof window.prompt !== 'function') throw new Error('当前环境不支持 Cookie 编辑');
      const detail = selectedDetail.value && selectedDetail.value.id === accountId ? selectedDetail.value : await runtimeApi.getAccountDetail(accountId);
      const nextRaw = window.prompt('编辑 Cookie 内容（留空表示清空）', String(detail.cookieContent || ''));
      if (nextRaw === null) return;
      const next = nextRaw.trim();
      await runtimeApi.updateAccount(accountId, toUpsertPayload(detail, { cookieContent: next ? next : null, cookieStatus: inferCookieStatus(detail.cookieStatus, next) }));
      if (next && typeof window.confirm === 'function' && window.confirm('Cookie 已保存，是否立即执行登录态校验？')) {
        const validation = await runtimeApi.validateAccountLogin(accountId);
        setMessage(`Cookie 状态已更新 / ${validation.label}`);
      } else {
        setMessage('Cookie 状态已更新');
      }
      await refreshAccounts();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : '更新 Cookie 失败');
    } finally { workingAction.value = ''; }
  }

  async function rebindAndValidateAccount(accountId: number): Promise<void> {
    clearFeedback(); workingAction.value = 'rebind-validate';
    try {
      if (typeof window.prompt !== 'function') throw new Error('当前环境不支持交互式重绑');
      const snapshot = await runtimeApi.getAccountProxyBinding(accountId);
      if (!snapshot.availableDevices.length) throw new Error('当前没有可用设备，无法执行重绑');
      const defaultDeviceId = snapshot.boundDeviceId ?? snapshot.availableDevices[0].id;
      const options = snapshot.availableDevices.map((x) => `${x.id}: ${x.name || '--'} (${x.region || '--'} / ${x.proxyIp || '未配置代理'})`).join('\n');
      const idRaw = window.prompt(`输入目标设备 ID：\n${options}`, String(defaultDeviceId));
      if (idRaw === null) return;
      const deviceId = Number(idRaw.trim());
      if (!Number.isFinite(deviceId) || deviceId <= 0) throw new Error('设备 ID 无效');
      const selected = snapshot.availableDevices.find((x) => x.id === Math.trunc(deviceId)) || null;
      const proxyIp = window.prompt('代理 IP（留空表示不修改）', selected?.proxyIp || snapshot.proxyIp || '');
      if (proxyIp === null) return;
      const region = window.prompt('代理地区（留空表示不修改）', selected?.region || snapshot.region || '');
      if (region === null) return;

      const result = await runtimeApi.updateAccountProxyBinding(accountId, {
        deviceId: Math.trunc(deviceId),
        proxyIp: proxyIp.trim() || null,
        region: region.trim() || null,
        validateAfterSave: true,
      });
      const validationLabel = result.validation?.label || '已执行校验';
      setMessage(`重绑并校验完成：${snapshot.accountUsername} / ${validationLabel}`);
      await refreshAccounts();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : '重绑并校验失败');
    } finally { workingAction.value = ''; }
  }

  async function testAccountConnection(accountId: number): Promise<void> {
    clearFeedback(); workingAction.value = 'test-connection';
    try {
      const result = await runtimeApi.testAccountConnection(accountId);
      const latency = typeof result.latencyMs === 'number' ? `，延迟 ${result.latencyMs}ms` : '';
      setMessage(`代理检测完成：${result.status || 'unknown'}${latency}`);
      await refreshAccounts();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : '代理检测失败');
    } finally { workingAction.value = ''; }
  }

  async function validateAccountLogin(accountId: number): Promise<void> {
    clearFeedback(); workingAction.value = 'validate-login';
    try {
      const result = await runtimeApi.validateAccountLogin(accountId);
      setMessage(`登录态校验完成：${result.label}${result.message ? `，${result.message}` : ''}`);
      await refreshAccounts();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : '登录态校验失败');
    } finally { workingAction.value = ''; }
  }

  async function openEditDialog(accountId: number): Promise<void> {
    clearFeedback();
    editDialogError.value = '';
    const source = byId(accountId);
    if (!source) {
      setError('账号不存在，无法编辑');
      return;
    }
    try {
      const binding = await runtimeApi.getAccountProxyBinding(accountId);
      editDialogDeviceOptions.value = binding.availableDevices.map((device) => ({
        id: device.id,
        label: `${device.name || '--'} / ${device.region || '--'} / ${device.proxyIp || '未配置代理'}`,
      }));
      editDialogDraft.value = {
        accountId,
        username: source.username || '',
        platform: source.platform || 'tiktok',
        region: source.region || 'US',
        status: source.manualStatus || source.status || 'active',
        deviceId: binding.boundDeviceId !== null && binding.boundDeviceId !== undefined ? String(binding.boundDeviceId) : '',
        tags: source.tags || '',
        cookieStatus: source.cookieStatus || 'unknown',
        cookieContent: source.cookieContent || '',
        followers: Number(source.followers || 0),
        notes: source.notes || '',
      };
      editDialogVisible.value = true;
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : '加载编辑信息失败');
    }
  }

  function closeEditDialog(): void {
    editDialogVisible.value = false;
    editDialogSaving.value = false;
    editDialogError.value = '';
    editDialogDraft.value = null;
    editDialogDeviceOptions.value = [];
  }

  async function submitEditDialog(): Promise<void> {
    if (!editDialogDraft.value || editDialogSaving.value) {
      return;
    }
    const draft = editDialogDraft.value;
    if (!draft.username.trim()) {
      editDialogError.value = '用户名不能为空';
      return;
    }
    editDialogSaving.value = true;
    editDialogError.value = '';
    try {
      const source = byId(draft.accountId) || selectedDetail.value;
      if (!source) {
        throw new Error('账号不存在，无法保存');
      }
      await runtimeApi.updateAccount(
        draft.accountId,
        toUpsertPayload(source, {
          username: draft.username.trim(),
          platform: draft.platform.trim() || 'tiktok',
          region: draft.region.trim() || 'US',
          status: draft.status.trim() || 'active',
          manualStatus: draft.status.trim() || 'active',
          deviceId: draft.deviceId.trim() ? Number(draft.deviceId.trim()) : null,
          tags: draft.tags.trim() || null,
          cookieStatus: draft.cookieStatus.trim() || 'unknown',
          cookieContent: draft.cookieContent.trim() || null,
          followers: Number.isFinite(Number(draft.followers)) ? Math.max(0, Math.trunc(Number(draft.followers))) : 0,
          notes: draft.notes.trim() || null,
        }),
      );
      closeEditDialog();
      setMessage(`账号已更新：${draft.username.trim()}`);
      await refreshAccounts();
    } catch (cause) {
      editDialogError.value = cause instanceof Error ? cause.message : '保存账号失败';
    } finally {
      editDialogSaving.value = false;
    }
  }

  function openDeleteDialog(accountId: number): void {
    clearFeedback();
    deleteDialogError.value = '';
    const source = byId(accountId);
    if (!source) {
      setError('账号不存在，无法删除');
      return;
    }
    deleteDialogTarget.value = { id: source.id, username: source.username || '--' };
    deleteDialogVisible.value = true;
  }

  function closeDeleteDialog(): void {
    deleteDialogVisible.value = false;
    deleteDialogWorking.value = false;
    deleteDialogError.value = '';
    deleteDialogTarget.value = null;
  }

  async function confirmDeleteDialog(): Promise<void> {
    if (!deleteDialogTarget.value || deleteDialogWorking.value) {
      return;
    }
    deleteDialogWorking.value = true;
    deleteDialogError.value = '';
    const target = deleteDialogTarget.value;
    try {
      await runtimeApi.deleteAccount(target.id);
      closeDeleteDialog();
      setMessage(`账号已删除：${target.username}`);
      selectedAccountIds.value = selectedAccountIds.value.filter((id) => id !== target.id);
      if (selectedAccountId.value === target.id) {
        selectedAccountId.value = null;
        selectedDetail.value = null;
        selectedActivityCount.value = 0;
      }
      await refreshAccounts();
    } catch (cause) {
      deleteDialogError.value = cause instanceof Error ? cause.message : '删除账号失败';
    } finally {
      deleteDialogWorking.value = false;
    }
  }

  async function runBulkDetectEnvironment(): Promise<void> {
    clearFeedback();
    const ids = batchMode.value && selectedAccountIds.value.length > 0 ? selectedAccountIds.value.slice() : accounts.value.map((x) => x.id);
    if (!ids.length) { setError('当前没有可检测的账号'); return; }
    workingAction.value = 'bulk-detect';
    try {
      await runtimeApi.bulkUpdateAccounts({ action: 'test', accountIds: ids });
      setMessage(`已发起 ${ids.length} 个账号的批量环境检测`);
      await refreshAccounts();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : '批量检测环境失败');
    } finally { workingAction.value = ''; }
  }

  async function createAccount(): Promise<void> {
    clearFeedback();
    if (typeof window.prompt !== 'function') { setError('当前环境不支持快捷创建账号'); return; }
    const usernameInput = window.prompt('请输入新账号用户名');
    if (usernameInput === null) return;
    const username = usernameInput.trim();
    if (!username) { setError('用户名不能为空'); return; }
    const platform = window.prompt('平台（默认 tiktok）', 'tiktok');
    if (platform === null) return;
    const region = window.prompt('地区（默认 US）', 'US');
    if (region === null) return;
    workingAction.value = 'create';
    try {
      const created = await runtimeApi.createAccount({
        username,
        platform: platform.trim() || 'tiktok',
        region: region.trim() || 'US',
        status: 'active',
        manualStatus: 'active',
        riskStatus: 'unknown',
        followers: 0,
        cookieStatus: 'unknown',
      });
      await refreshAccounts();
      selectedAccountId.value = created.id;
      await loadAccountDetail(created.id);
      setMessage(`已创建账号：${created.username}`);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : '创建账号失败');
    } finally { workingAction.value = ''; }
  }

  async function runBatchTagAction(): Promise<void> {
    if (!batchMode.value) {
      batchMode.value = true;
      setMessage('已进入批量模式，请勾选账号后继续打标签');
      return;
    }
    if (!selectedAccountIds.value.length) { setError('请先勾选需要打标签的账号'); return; }
    if (typeof window.prompt !== 'function') { setError('当前环境不支持批量标签输入'); return; }
    const input = window.prompt('输入标签（用逗号分隔）');
    if (input === null) return;
    const incoming = splitTags(input);
    if (!incoming.length) { setError('请至少填写一个标签'); return; }
    workingAction.value = 'batch-tag'; clearFeedback();
    try {
      await Promise.all(selectedAccountIds.value.map(async (accountId) => {
        const source = byId(accountId);
        if (!source) return;
        await runtimeApi.updateAccount(accountId, toUpsertPayload(source, { tags: mergeTags(splitTags(source.tags), incoming) }));
      }));
      setMessage(`已为 ${selectedAccountIds.value.length} 个账号补充标签`);
      batchMode.value = false;
      selectedAccountIds.value = [];
      await refreshAccounts();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : '批量打标签失败');
    } finally { workingAction.value = ''; }
  }

  function cancelBatchMode(): void {
    batchMode.value = false;
    selectedAccountIds.value = [];
    setMessage('已退出批量模式');
  }

  function exportAccountList(): void {
    clearFeedback();
    if (!accounts.value.length) { setError('当前没有可导出的账号'); return; }
    const header = ['账号ID', '用户名', '平台', '地区', '状态', 'Cookie', '登录态校验', '代理', '标签'];
    const rows = accounts.value.map((x) => [x.id, x.username, x.platformLabel, x.regionLabel, x.statusLabel, x.cookieLabel, x.loginCheckLabel, x.proxyLabel, x.tags.join(' | ')]);
    const csv = `\ufeff${[header, ...rows].map((row) => row.map((f) => `"${String(f).replaceAll('"', '""')}"`).join(',')).join('\n')}`;
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `accounts-${Date.now()}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setMessage('账号清单导出完成');
  }

  function dismissIsolationReminder(): void {
    isolationNoticeDismissed.value = true;
    writeDismissed(true);
    setMessage('本轮已隐藏隔离提醒');
  }

  async function openIsolationSettings(): Promise<void> {
    await router.push({ name: 'device-management' });
  }

  function onDetailAction(event: Event): void {
    const detail = (event as CustomEvent<{ action?: DetailAction; accountId?: number }>).detail;
    if (!detail || typeof detail.accountId !== 'number') return;
    if (detail.action === 'open-environment') { void openAccountEnvironment(detail.accountId); return; }
    if (detail.action === 'manage-cookies') { void manageAccountCookies(detail.accountId); return; }
    if (detail.action === 'rebind-validate') { void rebindAndValidateAccount(detail.accountId); return; }
    if (detail.action === 'validate-login') { void validateAccountLogin(detail.accountId); return; }
    if (detail.action === 'edit-account') { void openEditDialog(detail.accountId); return; }
    if (detail.action === 'delete-account') { openDeleteDialog(detail.accountId); return; }
    if (detail.action === 'test-connection') { void testAccountConnection(detail.accountId); }
  }

  watch(allAccounts, (items) => {
    const ids = new Set(items.map((x) => x.id));
    selectedAccountIds.value = selectedAccountIds.value.filter((id) => ids.has(id));
  }, { immediate: true });

  watch(accounts, (items) => {
    if (!items.length) {
      selectedAccountId.value = null;
      selectedDetail.value = null;
      selectedActivityCount.value = 0;
      shell.resetAccountDetailState();
      return;
    }
    if (typeof selectedAccountId.value === 'number' && items.some((x) => x.id === selectedAccountId.value)) {
      syncDetailState();
      return;
    }
    void selectAccount(items[0].id);
  }, { immediate: true });

  watch([selectedAccountId, selectedDetail, selectedActivityCount], () => syncDetailState());

  onMounted(() => {
    window.addEventListener('tkops:account-detail-action', onDetailAction as EventListener);
  });
  onBeforeUnmount(() => {
    window.removeEventListener('tkops:account-detail-action', onDetailAction as EventListener);
    shell.resetAccountDetailState();
  });

  return {
    accounts,
    loading: resource.loading,
    error: resource.error,
    actionError,
    actionMessage,
    detailError,
    detailLoading,
    workingAction,
    editDialogVisible,
    editDialogSaving,
    editDialogError,
    editDialogDraft,
    editDialogDeviceOptions,
    deleteDialogVisible,
    deleteDialogWorking,
    deleteDialogError,
    deleteDialogTarget,
    statusFilter: statusFilterRef,
    viewMode,
    batchMode,
    selectedAccountId,
    selectedAccountIds,
    selectedCount,
    batchTagButtonText,
    accountStatusCounts,
    isolationBannerVisible,
    isolationBannerCopy,
    refreshAccounts,
    setStatusFilter,
    setViewMode: setView,
    selectAccount,
    toggleAccountSelection,
    runBatchTagAction,
    cancelBatchMode,
    isAccountChecked,
    dismissIsolationReminder,
    openIsolationSettings,
    openAccountEnvironment,
    manageAccountCookies,
    rebindAndValidateAccount,
    validateAccountLogin,
    testAccountConnection,
    openEditDialog,
    closeEditDialog,
    submitEditDialog,
    openDeleteDialog,
    closeDeleteDialog,
    confirmDeleteDialog,
    runBulkDetectEnvironment,
    createAccount,
    exportAccountList,
  };
}
