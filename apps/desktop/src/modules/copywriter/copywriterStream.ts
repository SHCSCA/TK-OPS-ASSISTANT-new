import { getRuntimeToken, getRuntimeWebSocketUrl } from '../runtime/config';
import type { CopywriterStreamEvent, CopywriterStreamRequest } from '../runtime/types';

export function streamCopywriter(
  payload: CopywriterStreamRequest,
  onEvent: (event: CopywriterStreamEvent) => void,
): Promise<void> {
  return new Promise((resolve, reject) => {
    const socket = new WebSocket(
      `${getRuntimeWebSocketUrl()}/ws/copywriter-stream?token=${encodeURIComponent(getRuntimeToken())}`,
    );
    let settled = false;

    socket.addEventListener('open', () => {
      socket.send(JSON.stringify(payload));
    });

    socket.addEventListener('message', (event) => {
      const parsed = JSON.parse(event.data) as CopywriterStreamEvent;
      onEvent(parsed);
      if (parsed.type === 'ai.stream.done' || parsed.type === 'ai.stream.error') {
        settled = true;
        socket.close();
        if (parsed.type === 'ai.stream.error') {
          reject(new Error(parsed.payload.message));
          return;
        }
        resolve();
      }
    });

    socket.addEventListener('error', () => {
      if (!settled) {
        settled = true;
        reject(new Error('AI 文案流式连接失败'));
      }
    });

    socket.addEventListener('close', () => {
      if (!settled) {
        settled = true;
        resolve();
      }
    });
  });
}
