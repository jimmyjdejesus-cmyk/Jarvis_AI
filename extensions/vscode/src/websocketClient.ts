import WebSocket from 'ws';

export class JarvisClient {
  private socket?: WebSocket;
  private pending = new Map<string, (data: any) => void>();

  constructor(private url: string) {}

  async connect(): Promise<void> {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      return;
    }
    this.socket = new WebSocket(this.url);
    this.socket.on('message', (data: WebSocket.RawData) => {
      try {
        const msg = JSON.parse(data.toString());
        const id = msg.id;
        if (id && this.pending.has(id)) {
          const resolve = this.pending.get(id)!;
          this.pending.delete(id);
          resolve(msg);
        }
      } catch {
        // ignore parse errors
      }
    });
    await new Promise<void>((resolve, reject) => {
      this.socket?.once('open', () => resolve());
      this.socket?.once('error', (err: any) => reject(err));
    });
  }

  sendRequest(payload: any): Promise<any> {
    const id = Date.now().toString() + Math.random().toString();
    payload.id = id;
    const promise = new Promise<any>(resolve => {
      this.pending.set(id, resolve);
    });
    this.socket?.send(JSON.stringify(payload));
    return promise;
  }

      this.socket?.once('close', () => reject(new Error('WebSocket closed before connection established')));
    });
  }

  sendRequest(payload: any): Promise<any> {
    const id = Date.now().toString() + Math.random().toString();
    payload.id = id;
    const TIMEOUT_MS = 10000;
    const promise = new Promise<any>((resolve, reject) => {
      const timeout = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error('Request timed out'));
      }, TIMEOUT_MS);
      this.pending.set(id, {resolve, reject, timeout});
    });
    this.socket?.send(JSON.stringify(payload));
    return promise;
  }

  dispose() {
    // Reject all pending promises on dispose
    for (const [id, pendingObj] of this.pending.entries()) {
      clearTimeout(pendingObj.timeout);
      pendingObj.reject(new Error('Client disposed'));
    }
    this.pending.clear();
    this.socket?.close();
  }
}
