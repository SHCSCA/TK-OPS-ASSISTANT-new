import { getRuntimeBaseUrl } from '../runtime/config';

export interface HostShellInfo {
  appVersion: string;
  runtimeEndpoint: string;
  runtimeStatus: string;
  runtimeLaunchMode: string;
  runtimeReachable: boolean;
  currentDir: string;
  currentExe: string;
  lastError: string | null;
  lastExitCode: number | null;
  bootAttempts: number;
}

export interface HostRuntimeRestartResult {
  action: string;
  status: string;
  runtimeStatus: string;
  runtimeEndpoint: string;
  lastError: string | null;
  lastExitCode: number | null;
  bootAttempts: number;
}

interface TauriInvokeShape {
  invoke?: (command: string, args?: Record<string, unknown>) => Promise<unknown>;
}

interface RuntimeHealthPayload {
  status?: string;
  endpoint?: string;
  launch_mode?: string;
  reachable?: boolean;
  last_error?: string | null;
  last_exit_code?: number | null;
  boot_attempts?: number;
}

interface AppPathsPayload {
  current_dir?: string;
  currentDir?: string;
  current_exe?: string;
  currentExe?: string;
}

interface RestartRuntimePayload {
  action?: string;
  status?: string;
  snapshot?: RuntimeHealthPayload;
}

function getTauriInvoker(): TauriInvokeShape['invoke'] {
  return (window as typeof window & { __TAURI_INTERNALS__?: TauriInvokeShape }).__TAURI_INTERNALS__?.invoke;
}

async function invokeCommand(command: string): Promise<unknown> {
  const invoke = getTauriInvoker();
  if (!invoke) {
    return null;
  }
  return invoke(command);
}

function parseJsonObject<T>(raw: unknown): T | null {
  if (typeof raw !== 'string') {
    return null;
  }
  try {
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

function parseRuntimeHealth(raw: unknown): RuntimeHealthPayload {
  return parseJsonObject<RuntimeHealthPayload>(raw) || {};
}

function parseAppPaths(raw: unknown): AppPathsPayload {
  return parseJsonObject<AppPathsPayload>(raw) || {};
}

function parseRestartRuntime(raw: unknown): RestartRuntimePayload {
  return parseJsonObject<RestartRuntimePayload>(raw) || {};
}

export async function loadHostShellInfo(): Promise<HostShellInfo> {
  const [appVersionRaw, runtimeHealthRaw, appPathsRaw] = await Promise.all([
    invokeCommand('get_app_version'),
    invokeCommand('runtime_health'),
    invokeCommand('get_app_paths'),
  ]);

  const runtimeHealth = parseRuntimeHealth(runtimeHealthRaw);
  const appPaths = parseAppPaths(appPathsRaw);

  return {
    appVersion: typeof appVersionRaw === 'string' && appVersionRaw ? appVersionRaw : 'web-dev',
    runtimeEndpoint: runtimeHealth.endpoint || getRuntimeBaseUrl(),
    runtimeStatus: runtimeHealth.status || 'browser-fallback',
    runtimeLaunchMode: runtimeHealth.launch_mode || 'browser',
    runtimeReachable: Boolean(runtimeHealth.reachable),
    currentDir: appPaths.current_dir || appPaths.currentDir || '',
    currentExe: appPaths.current_exe || appPaths.currentExe || '',
    lastError: typeof runtimeHealth.last_error === 'string' ? runtimeHealth.last_error : null,
    lastExitCode: typeof runtimeHealth.last_exit_code === 'number' ? runtimeHealth.last_exit_code : null,
    bootAttempts: runtimeHealth.boot_attempts || 0,
  };
}

export async function restartRuntimeFromHost(): Promise<HostRuntimeRestartResult> {
  const raw = await invokeCommand('restart_runtime');
  const result = parseRestartRuntime(raw);
  return {
    action: result.action || 'restart-runtime',
    status: result.status || 'browser-fallback',
    runtimeStatus: result.snapshot?.status || 'browser-fallback',
    runtimeEndpoint: result.snapshot?.endpoint || getRuntimeBaseUrl(),
    lastError: typeof result.snapshot?.last_error === 'string' ? result.snapshot.last_error : null,
    lastExitCode: typeof result.snapshot?.last_exit_code === 'number' ? result.snapshot.last_exit_code : null,
    bootAttempts: result.snapshot?.boot_attempts || 0,
  };
}
