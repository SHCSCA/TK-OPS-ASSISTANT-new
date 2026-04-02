import { getRuntimeBaseUrl, getRuntimeToken } from './config';
import type { RuntimeEnvelope } from './types';

function buildUrl(path: string): string {
  return `${getRuntimeBaseUrl()}${path}`;
}

function extractRuntimeError(payload: unknown, fallback: string): string {
  if (!payload || typeof payload !== 'object') {
    return fallback;
  }

  const runtimeEnvelope = payload as RuntimeEnvelope<unknown>;
  const runtimeError = runtimeEnvelope.error;
  if (typeof runtimeError === 'string' && runtimeError.trim()) {
    return runtimeError;
  }
  if (runtimeError && typeof runtimeError === 'object' && 'message' in runtimeError) {
    const message = runtimeError.message;
    if (typeof message === 'string' && message.trim()) {
      return message;
    }
  }
  return fallback;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(buildUrl(path), {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      'X-TKOPS-Token': getRuntimeToken(),
      ...(init?.headers || {}),
    },
  });

  const payload = (await response.json().catch(() => null)) as RuntimeEnvelope<T> | null;
  if (!response.ok) {
    throw new Error(extractRuntimeError(payload, `Runtime 请求失败: ${response.status}`));
  }
  if (!payload?.ok) {
    throw new Error(extractRuntimeError(payload, 'Runtime 返回错误'));
  }
  return payload.data;
}

export const httpClient = {
  delete<T>(path: string): Promise<T> {
    return request(path, { method: 'DELETE' });
  },
  get<T>(path: string): Promise<T> {
    return request(path);
  },
  post<T>(path: string, body?: unknown): Promise<T> {
    return request(path, {
      method: 'POST',
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  },
  put<T>(path: string, body?: unknown): Promise<T> {
    return request(path, {
      method: 'PUT',
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  },
};
