"use client";

import {
  useEffect,
  useRef,
  useState,
} from "react";

/**
 * ✅ WebSocket hook avec:
 * - Auto-reconnection avec exponential backoff
 * - Message queuing
 * - Proper error logging
 */
export function useWebSocket(url: string) {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const messageQueueRef = useRef<string[]>([]);

  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<string>("");

  const MAX_RECONNECT_ATTEMPTS = 5;
  const RECONNECT_DELAY = 3000; // 3s

  // ===== CONNECT =====
  const connect = () => {
    try {
      if (!url) {
        console.warn("⚠️ WebSocket URL is empty");
        return;
      }

      console.log(`🔌 Connecting to ${url}`);

      const ws = new WebSocket(url);

      ws.onopen = () => {
        console.log("✅ WebSocket connected");
        setConnected(true);
        reconnectAttemptsRef.current = 0;

        // ✅ Flush queued messages
        while (messageQueueRef.current.length > 0) {
          const msg = messageQueueRef.current.shift();
          if (msg && ws.readyState === WebSocket.OPEN) {
            try {
              ws.send(msg);
            } catch (e) {
              console.error("Failed to send queued message:", e);
            }
          }
        }
      };

      ws.onmessage = (event: MessageEvent<string>) => {
        try {
          if (event.data) {
            setLastMessage(event.data);
          }
        } catch (err) {
          console.error("❌ Message parse error:", err instanceof Error ? err.message : String(err));
        }
      };

      // ✅ FIXED: Extract error info from Event object
      ws.onerror = (event: Event) => {
        // Event object doesn't have a message, log it differently
        if (event instanceof Event) {
          console.error("❌ WebSocket error - Connection failed");
          console.debug("Event type:", event.type);
        } else {
          console.error("❌ WebSocket error:", String(event));
        }
        setConnected(false);
      };

      ws.onclose = (event: CloseEvent) => {
        console.log(`❌ WebSocket closed (code: ${event.code}, reason: ${event.reason || 'unknown'})`);
        setConnected(false);

        // ✅ Auto-reconnect with exponential backoff
        if (reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
          const delay = RECONNECT_DELAY * (2 ** reconnectAttemptsRef.current);
          console.log(
            `🔄 Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current + 1}/${MAX_RECONNECT_ATTEMPTS})`
          );

          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++;
            connect();
          }, delay);
        } else {
          console.error(
            `❌ Max reconnect attempts reached (${MAX_RECONNECT_ATTEMPTS})`
          );
        }
      };

      wsRef.current = ws;

    } catch (err) {
      console.error(
        "❌ WebSocket connection error:",
        err instanceof Error ? err.message : String(err)
      );
      setConnected(false);
    }
  };

  // ===== SEND MESSAGE =====
  const sendMessage = (message: string) => {
    if (!message) return;

    if (
      wsRef.current &&
      wsRef.current.readyState === WebSocket.OPEN
    ) {
      try {
        wsRef.current.send(message);
        console.log("📤 Message sent");
      } catch (err) {
        console.error(
          "❌ Send error:",
          err instanceof Error ? err.message : String(err)
        );
        messageQueueRef.current.push(message);
      }
    } else {
      console.warn("⚠️ WebSocket not ready, queuing message");
      messageQueueRef.current.push(message);
    }
  };

  // ===== EFFECT: Connect on mount =====
  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }

      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [url]);

  return {
    connected,
    lastMessage,
    sendMessage,
  };
}