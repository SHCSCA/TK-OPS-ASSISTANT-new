const fallbackBaseUrl = 'http://127.0.0.1:8765';
const fallbackRuntimeToken = 'dev-token';

export function getRuntimeBaseUrl(): string {
  const value = import.meta.env.VITE_RUNTIME_URL?.trim();
  return value || fallbackBaseUrl;
}

export function getRuntimeToken(): string {
  const value = import.meta.env.VITE_RUNTIME_TOKEN?.trim();
  return value || fallbackRuntimeToken;
}

export function getRuntimeWebSocketUrl(): string {
  const baseUrl = new URL(getRuntimeBaseUrl());
  baseUrl.protocol = baseUrl.protocol === 'https:' ? 'wss:' : 'ws:';
  return baseUrl.toString().replace(/\/$/, '');
}
