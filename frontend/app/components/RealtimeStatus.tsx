"use client";

import { CircleDot } from "lucide-react";

type Props = {
  connected: boolean;
};

/**
 * ✅ Realtime status indicator avec:
 * - Animated pulse
 * - Color coded status
 * - Clear labels
 */
export default function RealtimeStatus({
  connected,
}: Props) {
  return (
    <div
      className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-black transition ${
        connected
          ? "bg-emerald-500/20 border border-emerald-500/40 text-emerald-300"
          : "bg-red-500/20 border border-red-500/40 text-red-300"
      }`}
    >
      <CircleDot
        size={12}
        className={`${
          connected
            ? "fill-emerald-400 text-emerald-400 animate-pulse"
            : "fill-red-400 text-red-400"
        }`}
      />
      <span>
        {connected ? "🟢 LIVE" : "🔴 OFFLINE"}
      </span>
    </div>
  );
}