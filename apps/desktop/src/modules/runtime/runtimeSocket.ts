import { getRuntimeToken, getRuntimeWebSocketUrl } from './config';

export interface RuntimeSocketHandle {
  connect(): void;
  disconnect(): void;
}

export function createRuntimeSocket(onMessage: (data: unknown) => void): RuntimeSocketHandle {
  let socket: WebSocket | null = null;

  return {
    connect() {
      if (socket) {
        return;
      }
      socket = new WebSocket(
        `${getRuntimeWebSocketUrl()}/ws/runtime-status?token=${encodeURIComponent(getRuntimeToken())}`,
      );
      socket.addEventListener('message', (event) => {
        onMessage(JSON.parse(event.data));
      });
      socket.addEventListener('close', () => {
        socket = null;
      });
    },
    disconnect() {
      socket?.close();
      socket = null;
    },
  };
}
