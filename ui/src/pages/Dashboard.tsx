// Dashboard.tsx
// This page shows the main dashboard grid (3 columns) and pulls live telemetry via WebSocket.

// Import React hooks (needed for live state + side effects)
import { useEffect, useState } from "react";

// Import the reusable Card component
import Card from "../Components/Card";

/**
 * TypeScript "shape" for the JSON we expect from the Python server.
 * Everything is optional (with ?) so the UI doesn't crash if a field is missing.
 *
 * You can expand this later as your telemetry grows.
 */
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
  const [wsStatus, setWsStatus] = useState<"disconnected" | "connecting" | "connected" >("disconnected");

  /**
   * useEffect runs after the component renders.
   * With [] at the end, it runs only ONCE when the page loads.
   * Perfect for opening a WebSocket connection.
   */
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
      {/* ================= LEFT COLUMN ================= */}
      {/* This div is a COLUMN (layout container) */}
      <div className="space-y-6 md:col-span-2 lg:col-span-1">
        <Card title="Satellite Position">
          {/* Placeholder for orbit visualization */}
          <div className="h-56 rounded-xl bg-slate-950/60 flex items-center justify-center text-slate-500">
            Orbital visualization placeholder
          </div>

          {/* Position stats */}
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

          {/* Optional: show WS status here so you know it's connected */}
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

      {/* ================= MIDDLE COLUMN ================= */}
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

      {/* ================= RIGHT COLUMN ================= */}
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
