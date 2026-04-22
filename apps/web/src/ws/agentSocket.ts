import { useCallback, useEffect, useRef } from "react";

type Handler = (msg: unknown) => void;

export function useAgentSocket(projectId: string) {
  const wsRef = useRef<WebSocket | null>(null);
  const handlersRef = useRef<Set<Handler>>(new Set());

  useEffect(() => {
    const proto = location.protocol === "https:" ? "wss" : "ws";
    const url = `${proto}://${location.host}/api/v1/agent/ws/${projectId}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;
    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);
        handlersRef.current.forEach((h) => h(data));
      } catch {
        /* ignore */
      }
    };
    return () => ws.close();
  }, [projectId]);

  const send = useCallback((payload: unknown) => {
    wsRef.current?.send(JSON.stringify(payload));
  }, []);

  const subscribe = useCallback((handler: Handler) => {
    handlersRef.current.add(handler);
    return () => handlersRef.current.delete(handler);
  }, []);

  return { send, subscribe };
}
