import { useEffect, useRef, useState } from "react";
import Card from "../Components/Card";

// WebSocket URLs
const WS_PROTOCOL = window.location.protocol === "https:" ? "wss" : "ws";
const WS_BASE = `${WS_PROTOCOL}://${window.location.host}`;
const WS_TELEMETRY = `${WS_BASE}/ws/telemetry`; // Switch this to /ws/ingest for zmq data
const WS_WATERFALL = `${WS_BASE}/ws/waterfall`;

// Waterfall config
const BINS = 512;
const ROWS = 240;
const DB_MIN = -80;
const DB_MAX = -10;
const USE_FAKE_TELEMETRY = false;

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

// SDR-style color mapping
function sdrColor(t: number): [number, number, number] {
  if (t < 0) t = 0;
  if (t > 1) t = 1;

  const r = Math.floor(255 * t);
  const g = Math.floor(255 * Math.min(1, t * 1.2));
  const b = Math.floor(255 * (1 - t));
  return [r, g, b];
}

// Small helper
function clamp(n: number, lo: number, hi: number) {
  return Math.max(lo, Math.min(hi, n));
}

export default function Dashboard() {
  // ---- Header online status (ONE place) ----
  const [status, setStatus] = useState<"offline" | "connecting" | "online">(
    USE_FAKE_TELEMETRY ? "online" : "connecting",
  );

  // ---- Telemetry state (can be real WS or fake) ----
  const [telemetry, setTelemetry] = useState<TelemetryPacket | null>(null);

  // ---- Waterfall ----
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // Fake telemetry generator (simple + nice looking)
  useEffect(() => {
    if (!USE_FAKE_TELEMETRY) return;

    const t0 = Date.now();
    const id = setInterval(() => {
      const t = (Date.now() - t0) / 1000;

      // smooth variations
      const batt = 7.6 + 0.25 * Math.sin(t / 6);
      const solar = 1.4 + 0.8 * Math.max(0, Math.sin(t / 4));
      const temp = 33.5 + 2.0 * Math.sin(t / 10);

      const freq = 437.2 + 0.05 * Math.sin(t / 12);
      const rssi = -118 + 6 * Math.sin(t / 5);
      const snr = 3.8 + 2.0 * Math.sin(t / 7);

      const roll = -6 + 1.6 * Math.sin(t / 6);
      const pitch = -4 + 1.2 * Math.sin(t / 8);
      const yaw = 30 + 7.0 * Math.sin(t / 9);

      setTelemetry({
        power: {
          battery_voltage: Number(batt.toFixed(2)),
          solar_current: Number(solar.toFixed(2)),
          battery_temp_c: Number(temp.toFixed(1)),
        },
        radio: {
          frequency_mhz: Number(freq.toFixed(2)),
          rssi_dbm: Math.round(rssi),
          snr_db: Number(snr.toFixed(1)),
        },
        orientation: {
          roll_deg: Number(roll.toFixed(1)),
          pitch_deg: Number(pitch.toFixed(1)),
          yaw_deg: Number(yaw.toFixed(1)),
        },
      });
    }, 250);

    return () => clearInterval(id);
  }, []);

  // Real telemetry WS (only if you flip USE_FAKE_TELEMETRY = false)
  useEffect(() => {
    if (USE_FAKE_TELEMETRY) return;
    const ws = new WebSocket(WS_TELEMETRY);

    ws.onopen = () => setStatus("online");
    ws.onclose = () => {
      setStatus("offline");
      setTelemetry(null);
    };
    ws.onerror = () => {
      setStatus("offline");
      setTelemetry(null);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as TelemetryPacket;
        setTelemetry(data);
      } catch (e) {
        console.error("Telemetry parse error:", e);
      }
    };

    return () => ws.close();
  }, []);

  // Waterfall WS (this can be your “one real connection” if you want)
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    canvas.width = BINS;
    canvas.height = ROWS;
    ctx.fillStyle = "black";
    ctx.fillRect(0, 0, BINS, ROWS);

    const ws = new WebSocket(WS_WATERFALL);
    ws.binaryType = "arraybuffer";

    ws.onopen = () => setStatus("online");
    ws.onclose = () => setStatus("offline");
    ws.onerror = () => setStatus("offline");

    ws.onmessage = (event) => {
      const row = new Float32Array(event.data);
      if (row.length !== BINS) return;

      // scroll up one pixel row
      ctx.drawImage(canvas, 0, -1);

      const img = ctx.createImageData(BINS, 1);
      for (let x = 0; x < BINS; x++) {
        const db = row[x];
        const t = clamp((db - DB_MIN) / (DB_MAX - DB_MIN), 0, 1);
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

  // Values
  const batteryV = telemetry?.power?.battery_voltage ?? null;
  const solarA = telemetry?.power?.solar_current ?? null;
  const battTemp = telemetry?.power?.battery_temp_c ?? null;

  const freqMHz = telemetry?.radio?.frequency_mhz ?? null;
  const rssi = telemetry?.radio?.rssi_dbm ?? null;
  const snr = telemetry?.radio?.snr_db ?? null;

  const roll = telemetry?.orientation?.roll_deg ?? null;
  const pitch = telemetry?.orientation?.pitch_deg ?? null;
  const yaw = telemetry?.orientation?.yaw_deg ?? null;

  // Header pill styling
  const pill =
    status === "online"
      ? "bg-emerald-500/15 text-emerald-300 border-emerald-500/30"
      : status === "connecting"
        ? "bg-yellow-500/15 text-yellow-300 border-yellow-500/30"
        : "bg-red-500/15 text-red-300 border-red-500/30";

  const label =
    status === "online"
      ? "Online"
      : status === "connecting"
        ? "Connecting"
        : "Offline";

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
      {/* Darker header */}
      <div className="sticky top-0 z-10 border-b border-slate-800 bg-slate-950/80 backdrop-blur">
        <div className="mx-auto max-w-7xl px-4 py-4 flex items-start justify-between">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-slate-100">
              CubeSat Ground Station
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Real-time telemetry and signal monitoring
            </p>
          </div>

          <div
            className={`select-none rounded-full border px-3 py-1 text-xs font-medium ${pill}`}
          >
            {label}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="mx-auto max-w-7xl px-4 py-4 space-y-4">
        {/* TOP: Waterfall */}
        <Card title="RF Waterfall / Spectrum">
          <div className="mt-1 flex items-center justify-between text-xs text-slate-400">
            <div>
              dB scale: {DB_MIN} to {DB_MAX}
            </div>
            <div className="text-slate-500">
              Source: {USE_FAKE_TELEMETRY ? "Demo data" : "Live data"}
            </div>
          </div>

          <div className="mt-3 flex">
            {/* Y axis */}
            <div className="flex flex-col justify-between pr-2 text-xs text-slate-400">
              <div>20 s</div>
              <div>15 s</div>
              <div>10 s</div>
              <div>5 s</div>
              <div>0 s</div>
            </div>

            <div className="w-full">
              <div className="h-80 w-full overflow-hidden rounded-xl border border-slate-800 bg-black">
                <canvas ref={canvasRef} className="h-full w-full" />
              </div>

              {/* X axis */}
              <div className="mt-2 flex justify-between text-xs text-slate-400 px-1">
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
        </Card>

        {/* BOTTOM: changing telemetry */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card title="Power">
            <div className="text-sm space-y-2">
              <div className="flex justify-between">
                <span>Battery Voltage</span>
                <span className="text-emerald-400">
                  {batteryV !== null ? `${batteryV} V` : "—"}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Solar Current</span>
                <span className="text-emerald-400">
                  {solarA !== null ? `${solarA} A` : "—"}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Battery Temp</span>
                <span>{battTemp !== null ? `${battTemp} °C` : "—"}</span>
              </div>
            </div>
          </Card>

          <Card title="Radio Link">
            <div className="text-sm space-y-2">
              <div className="flex justify-between">
                <span>Frequency</span>
                <span>{freqMHz !== null ? `${freqMHz} MHz` : "—"}</span>
              </div>
              <div className="flex justify-between">
                <span>RSSI</span>
                <span className="text-emerald-400">
                  {rssi !== null ? `${rssi} dBm` : "—"}
                </span>
              </div>
              <div className="flex justify-between">
                <span>SNR</span>
                <span className="text-emerald-400">
                  {snr !== null ? `${snr} dB` : "—"}
                </span>
              </div>
            </div>
          </Card>

          <Card title="Orientation (ADCS)">
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <div className="text-slate-500">Roll</div>
                <div>{roll !== null ? `${roll}°` : "—"}</div>
              </div>
              <div>
                <div className="text-slate-500">Pitch</div>
                <div>{pitch !== null ? `${pitch}°` : "—"}</div>
              </div>
              <div>
                <div className="text-slate-500">Yaw</div>
                <div>{yaw !== null ? `${yaw}°` : "—"}</div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
