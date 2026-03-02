/**
 * ═══════════════════════════════════════════════════════════════════════════
 * ARCHIVED CODE - OLD DASHBOARD AND TELEMETRY COMPONENTS
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * This file contains the original Dashboard and Telemetry components
 * that were used before consolidating everything into a single page.
 *
 * Kept here for reference in case you need to restore the multi-tab/page
 * version or need to see how individual components worked.
 *
 * To use these again, you'd need to:
 * 1. Restore routing in App.tsx (see comments at bottom of App.tsx)
 * 2. Restore AppLayout.tsx and Sidebar.tsx
 * 3. Import and use these components in the routing
 *
 * ═══════════════════════════════════════════════════════════════════════════
 */

/*
// ═══════════════════════════════════════════════════════════════════════════
// DASHBOARD.TSX - ORIGINAL VERSION
// ═══════════════════════════════════════════════════════════════════════════
// This page shows the main dashboard grid (3 columns) and pulls live telemetry via WebSocket.

// Import React hooks (needed for live state + side effects)
import { useEffect, useState } from "react";

// Import the reusable Card component
import Card from "../Components/Card";

// TypeScript "shape" for the JSON we expect from the Python server.
// Everything is optional (with ?) so the UI doesn't crash if a field is missing.
type TelemetryPacket = {
  power?: {
    battery_voltage?: number;
    solar_current?: number;
    battery_temp_c?: number;
  };
  orientation?: {
    roll_deg?: number;
    pitch_deg?: number;
    yaw_deg?: number;
  };
  radio?: {
    frequency_mhz?: number;
    rssi_dbm?: number;
    snr_db?: number;
  };
};

export default function Dashboard() {
  // Holds the latest telemetry packet we received from the server
  const [telemetry, setTelemetry] = useState<TelemetryPacket | null>(null);

  // Simple status label so you can see if the client connected
  const [wsStatus, setWsStatus] = useState<
    "disconnected" | "connecting" | "connected"
  >("disconnected");

  // useEffect runs after the component renders.
  // With [] at the end, it runs only ONCE when the page loads.
  // Perfect for opening a WebSocket connection.
  useEffect(() => {
    setWsStatus("connecting");

    // For local testing, your backend is on the same machine.
    // Later, if server is on another computer/pi, replace localhost with its LAN IP.
    const ws = new WebSocket("ws://localhost:8765/ws/telemetry");

    // Fires when the socket successfully connects
    ws.onopen = () => {
      setWsStatus("connected");
    };

    // Fires whenever the server sends us a message
    ws.onmessage = (event) => {
      try {
        // event.data is a string (JSON)
        const data = JSON.parse(event.data) as TelemetryPacket;
        setTelemetry(data);
      } catch (err) {
        console.error("Failed to parse telemetry JSON:", err);
      }
    };

    // Fires if there's an error (network issue, wrong URL, server not running, etc.)
    ws.onerror = () => {
      setWsStatus("disconnected");
    };

    // Fires when the socket closes (server stops, tab closes, refresh, etc.)
    ws.onclose = () => {
      setWsStatus("disconnected");
    };

    // Cleanup function: runs when Dashboard unmounts or hot-reloads.
    // Prevents "ghost" sockets staying open.
    return () => {
      ws.close();
    };
  }, []);

  // Convenience values (so JSX stays clean).
  // "??" means: if left side is null/undefined, use the right side.
  const batteryV = telemetry?.power?.battery_voltage ?? null;
  const solarA = telemetry?.power?.solar_current ?? null;
  const battTemp = telemetry?.power?.battery_temp_c ?? null;

  const freqMHz = telemetry?.radio?.frequency_mhz ?? null;
  const rssi = telemetry?.radio?.rssi_dbm ?? null;
  const snr = telemetry?.radio?.snr_db ?? null;

  const roll = telemetry?.orientation?.roll_deg ?? null;
  const pitch = telemetry?.orientation?.pitch_deg ?? null;
  const yaw = telemetry?.orientation?.yaw_deg ?? null;

  return (
    // Outer grid: 3 columns across the dashboard
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
      // ================= LEFT COLUMN =================
      // This div is a COLUMN (layout container)
      <div className="space-y-6 md:col-span-2 lg:col-span-1">
        <Card title="Satellite Position">
          // Placeholder for orbit visualization
          <div className="h-56 rounded-xl bg-slate-950/60 flex items-center justify-center text-slate-500">
            Orbital visualization placeholder
          </div>

          // Position stats
          <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-slate-500">Latitude</div>
              <div>34.2° N</div>
            </div>
            <div>
              <div className="text-slate-500">Longitude</div>
              <div>118.5° W</div>
            </div>
            <div>
              <div className="text-slate-500">Altitude</div>
              <div>412 km</div>
            </div>
            <div>
              <div className="text-slate-500">Velocity</div>
              <div>7.6 km/s</div>
            </div>
          </div>

          // Optional: show WS status here so you know it's connected
          <div className="mt-4 text-xs text-slate-500">
            WebSocket:{" "}
            <span
              className={
                wsStatus === "connected"
                  ? "text-emerald-400"
                  : wsStatus === "connecting"
                    ? "text-yellow-300"
                    : "text-red-400"
              }
            >
              {wsStatus}
            </span>
          </div>
        </Card>
      </div>

      // ================= MIDDLE COLUMN =================
      <div className="space-y-6">
        <Card title="Power">
          <div className="text-sm space-y-2">
            <div className="flex justify-between">
              <span>Battery Voltage</span>
              <span className="text-emerald-400">
                {batteryV !== null ? `${batteryV} V` : "7.4 V"}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Solar Current</span>
              <span className="text-emerald-400">
                {solarA !== null ? `${solarA} A` : "1.2 A"}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Battery Temp</span>
              <span>{battTemp !== null ? `${battTemp} °C` : "18 °C"}</span>
            </div>
          </div>
        </Card>

        <Card title="Orientation (ADCS)">
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <div className="text-slate-500">Roll</div>
              <div>{roll !== null ? `${roll}°` : "-2.3°"}</div>
            </div>
            <div>
              <div className="text-slate-500">Pitch</div>
              <div>{pitch !== null ? `${pitch}°` : "1.8°"}</div>
            </div>
            <div>
              <div className="text-slate-500">Yaw</div>
              <div>{yaw !== null ? `${yaw}°` : "0.5°"}</div>
            </div>
          </div>
        </Card>
      </div>

      // ================= RIGHT COLUMN =================
      <div className="space-y-6">
        <Card title="Radio Link Status">
          <div className="text-sm space-y-2">
            <div className="flex justify-between">
              <span>Frequency</span>
              <span>{freqMHz !== null ? `${freqMHz} MHz` : "437.1 MHz"}</span>
            </div>
            <div className="flex justify-between">
              <span>RSSI</span>
              <span className="text-emerald-400">
                {rssi !== null ? `${rssi} dBm` : "-87 dBm"}
              </span>
            </div>
            <div className="flex justify-between">
              <span>SNR</span>
              <span className="text-emerald-400">
                {snr !== null ? `${snr} dB` : "12.3 dB"}
              </span>
            </div>
          </div>
        </Card>

        <Card title="Alerts">
          <div className="text-sm space-y-2">
            <div className="rounded-lg bg-slate-800/60 px-3 py-2">
              Next pass in 14 minutes
            </div>
            <div className="rounded-lg bg-yellow-900/30 px-3 py-2 text-yellow-300">
              BER elevated
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}



// ═══════════════════════════════════════════════════════════════════════════
// TELEMETRY.TSX - ORIGINAL VERSION (WATERFALL PLOT)
// ═══════════════════════════════════════════════════════════════════════════

import { useEffect, useRef, useState } from "react";
import Card from "../Components/Card";

const WS_URL = "ws://localhost:8765/ws/waterfall";
const BINS = 512;
const ROWS = 220;

// Adjust these if needed after testing
const DB_MIN = -80;
const DB_MAX = -10;

function sdrColor(t: number): [number, number, number] {
  // Clamp
  if (t < 0) t = 0;
  if (t > 1) t = 1;

  // Simple SDR-style gradient:
  // blue -> cyan -> green -> yellow -> red

  const r = Math.floor(255 * t);
  const g = Math.floor(255 * Math.min(1, t * 1.2));
  const b = Math.floor(255 * (1 - t));

  return [r, g, b];
}

export default function Telemetry() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [wsStatus, setWsStatus] = useState<
    "disconnected" | "connecting" | "connected"
  >("disconnected");

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    canvas.width = BINS;
    canvas.height = ROWS;

    ctx.fillStyle = "black";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    setWsStatus("connecting");
    const ws = new WebSocket(WS_URL);
    ws.binaryType = "arraybuffer";

    ws.onopen = () => setWsStatus("connected");
    ws.onclose = () => setWsStatus("disconnected");
    ws.onerror = () => setWsStatus("disconnected");

    ws.onmessage = (event) => {
      const row = new Float32Array(event.data);
      if (row.length !== BINS) return;

      // Scroll up
      ctx.drawImage(canvas, 0, -1);

      const img = ctx.createImageData(BINS, 1);

      for (let x = 0; x < BINS; x++) {
        const db = row[x];

        let t = (db - DB_MIN) / (DB_MAX - DB_MIN);
        if (t < 0) t = 0;
        if (t > 1) t = 1;

        const [R, G, B] = sdrColor(t);

        const p = x * 4;
        img.data[p] = R;
        img.data[p + 1] = G;
        img.data[p + 2] = B;
        img.data[p + 3] = 255;
      }

      ctx.putImageData(img, 0, ROWS - 1);
    };

    return () => ws.close();
  }, []);

  return (
    <div className="space-y-6">
      <Card title="Telemetry / Waterfall">
        <div className="mt-1 flex items-center justify-between text-xs text-slate-400">
          <div>
            WebSocket:{" "}
            <span
              className={
                wsStatus === "connected"
                  ? "text-emerald-400"
                  : wsStatus === "connecting"
                    ? "text-yellow-300"
                    : "text-red-400"
              }
            >
              {wsStatus}
            </span>
          </div>
          <div>
            dB scale: {DB_MIN} to {DB_MAX}
          </div>
        </div>

        <div className="mt-4 flex">
          // Y Axis
          <div className="flex flex-col justify-between pr-2 text-xs text-slate-400">
            <div>20 s</div>
            <div>15 s</div>
            <div>10 s</div>
            <div>5 s</div>
            <div>0 s</div>
          </div>

          // Canvas + X Axis
          <div className="flex flex-col w-full">
            <div className="overflow-hidden rounded-xl border border-slate-800 bg-black">
              <canvas ref={canvasRef} className="h-64 w-full" />
            </div>

            <div className="mt-1 flex justify-between text-xs text-slate-400 px-1">
              <span>-15</span>
              <span>-10</span>
              <span>-5</span>
              <span>0</span>
              <span>5</span>
              <span>10</span>
              <span>15</span>
            </div>

            <div className="text-center text-xs text-slate-500 mt-1">
              Frequency (kHz)
            </div>
          </div>
        </div>

        <div className="text-xs text-slate-500 mt-2">Time (s)</div>
      </Card>
    </div>
  );
}

*/

// ═══════════════════════════════════════════════════════════════════════════
// END ARCHIVED CODE
// ═══════════════════════════════════════════════════════════════════════════

export {};
