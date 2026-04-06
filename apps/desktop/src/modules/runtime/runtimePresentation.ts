export type RuntimeTone = 'info' | 'success' | 'warning' | 'error';

export interface RuntimeStatusPresentation {
  label: string;
  tone: RuntimeTone;
}

const RUNTIME_STATUS_MAP: Record<string, RuntimeStatusPresentation> = {
  unknown: { label: '运行状态未知', tone: 'info' },
  ok: { label: '运行正常', tone: 'success' },
  ready: { label: '已就绪', tone: 'success' },
  healthy: { label: '状态健康', tone: 'success' },
  'browser-fallback': { label: '浏览器兼容模式', tone: 'warning' },
  'managed-idle': { label: '托管运行时待启动', tone: 'info' },
  'managed-starting': { label: '托管运行时启动中', tone: 'warning' },
  'managed-running': { label: '托管运行时运行中', tone: 'success' },
  'managed-timeout': { label: '托管运行时启动超时', tone: 'warning' },
  'managed-exited': { label: '托管运行时已退出', tone: 'warning' },
  'managed-crashed': { label: '托管运行时异常退出', tone: 'error' },
  'managed-restarting': { label: '托管运行时重启中', tone: 'warning' },
  'managed-recovery-failed': { label: '托管运行时恢复失败', tone: 'error' },
  'managed-already-running': { label: '托管运行时已在运行', tone: 'success' },
  'managed-runtime-detected': { label: '检测到托管运行时', tone: 'success' },
  'external-reachable': { label: '外部运行时可连接', tone: 'success' },
  'external-unreachable': { label: '外部运行时不可连接', tone: 'error' },
  'external-runtime-unchanged': { label: '外部运行时保持不变', tone: 'info' },
  'runtime-health-serialize-error': { label: '运行时状态序列化异常', tone: 'error' },
};

function inferRuntimeTone(normalized: string): RuntimeTone {
  if (!normalized) {
    return 'info';
  }
  if (normalized.includes('error') || normalized.includes('failed') || normalized.includes('crash') || normalized.includes('异常')) {
    return 'error';
  }
  if (normalized.includes('warn') || normalized.includes('timeout') || normalized.includes('fallback') || normalized.includes('starting')) {
    return 'warning';
  }
  if (normalized.includes('ok') || normalized.includes('ready') || normalized.includes('healthy') || normalized.includes('正常')) {
    return 'success';
  }
  return 'info';
}

function hasChinese(value: string): boolean {
  return /[\u4e00-\u9fa5]/.test(value);
}

export function mapRuntimeStatus(rawStatus: string | null | undefined): RuntimeStatusPresentation {
  const source = String(rawStatus || '').trim();
  const normalized = source.toLowerCase();
  if (!normalized) {
    return RUNTIME_STATUS_MAP.unknown;
  }

  const exact = RUNTIME_STATUS_MAP[normalized];
  if (exact) {
    return exact;
  }

  if (hasChinese(source)) {
    return {
      label: source,
      tone: inferRuntimeTone(normalized),
    };
  }

  if (normalized.includes('managed')) {
    return {
      label: '托管运行时状态待确认',
      tone: inferRuntimeTone(normalized),
    };
  }
  if (normalized.includes('external')) {
    return {
      label: '外部运行时状态待确认',
      tone: inferRuntimeTone(normalized),
    };
  }
  if (normalized.includes('browser')) {
    return {
      label: '浏览器模式',
      tone: inferRuntimeTone(normalized),
    };
  }

  return {
    label: '运行状态待确认',
    tone: inferRuntimeTone(normalized),
  };
}

export function mapRuntimeLaunchMode(rawMode: string | null | undefined): string {
  const source = String(rawMode || '').trim();
  const normalized = source.toLowerCase();
  if (!normalized) {
    return '未知模式';
  }
  if (normalized === 'managed') {
    return '托管模式';
  }
  if (normalized === 'external') {
    return '外部模式';
  }
  if (normalized === 'browser') {
    return '浏览器模式';
  }
  if (normalized.includes('managed')) {
    return '托管模式';
  }
  if (normalized.includes('external')) {
    return '外部模式';
  }
  if (normalized.includes('browser')) {
    return '浏览器模式';
  }
  if (hasChinese(source)) {
    return source;
  }
  return '未知模式';
}

export function mapThemeMode(rawTheme: string | null | undefined): string {
  const source = String(rawTheme || '').trim();
  const normalized = source.toLowerCase();
  if (normalized === 'light') {
    return '浅色';
  }
  if (normalized === 'dark') {
    return '深色';
  }
  if (normalized === 'system') {
    return '跟随系统';
  }
  if (hasChinese(source)) {
    return source;
  }
  return '跟随系统';
}
