import { useEffect, useRef, useState } from "react";
import Card from "../Components/Card";

// WebSocket URLs
const WS_PROTOCOL = window.location.protocol === "https:" ? "wss" : "ws";
const WS_BASE = `${WS_PROTOCOL}://${window.location.host}`;
const WS_TELEMETRY = `${WS_BASE}/ws/telemetry`;
const WS_WATERFALL = `${WS_BASE}/ws/waterfall`;

// Waterfall config
const BINS = 512;
const ROWS = 240;
const DB_MIN = -80;
const DB_MAX = -10;
const USE_FAKE_TELEMETRY = true;

// ---- Types matching app_fastapi.py latest_telemetry shape ----------------

type ImuData = {
  gx_dps: number | null;
  gy_dps: number | null;
  gz_dps: number | null;
  ax_mg: number | null;
  ay_mg: number | null;
  az_mg: number | null;
  qi: number | null;
  qj: number | null;
  qk: number | null;
  qr: number | null;
};

type BatteryData = {
  current_mA: number | null;
  avg_current_mA: number | null;
  voltage_mV: number | null;
  average_voltage_mV: number | null;
  cycle_count: number | null;
  temperature_c: number | null;
  ext_temp1_c: number | null;
  ext_temp2_c: number | null;
  ext_temp3_c: number | null;
  ext_temp4_c: number | null;
  ext_temp5_c: number | null;
  ext_temp6_c: number | null;
  ext_temp7_c: number | null;
  ext_temp8_c: number | null;
  cell_voltage1_mV: number | null;
  cell_voltage2_mV: number | null;
  cell_voltage3_mV: number | null;
  cell_voltage4_mV: number | null;
};

type TcData = {
  tc_avg1: number | null;
  tc_avg2: number | null;
};

type TelemetryPacket = {
  timestamp?: number;
  packet_type?: number | null;
  imu?: ImuData;
  battery?: BatteryData;
  tc?: TcData;
  ground_station?: string;
};

// ---- Helpers ---------------------------------------------------------------

function fmt(v: number | null | undefined, unit: string, decimals = 1): string {
  return v != null ? `${Number(v).toFixed(decimals)} ${unit}` : "—";
}

function fmtInt(v: number | null | undefined, unit: string): string {
  return v != null ? `${Math.round(v)} ${unit}` : "—";
}

function sdrColor(t: number): [number, number, number] {
  if (t < 0) t = 0;
  if (t > 1) t = 1;
  return [
    Math.floor(255 * t),
    Math.floor(255 * Math.min(1, t * 1.2)),
    Math.floor(255 * (1 - t)),
  ];
}

function clamp(n: number, lo: number, hi: number) {
  return Math.max(lo, Math.min(hi, n));
}

// A small row component so the cards stay readable
function Row({
  label,
  value,
  highlight,
}: {
  label: string;
  value: string;
  highlight?: boolean;
}) {
  return (
    <div className="flex justify-between text-sm py-0.5">
      <span className="text-slate-400">{label}</span>
      <span className={highlight ? "text-emerald-400 font-mono" : "font-mono"}>
        {value}
      </span>
    </div>
  );
}

// ---- Fake telemetry for dev ------------------------------------------------

function makeFakeTelemetry(): TelemetryPacket {
  const t = Date.now() / 1000;
  return {
    timestamp: Math.floor(t),
    packet_type:
      Math.floor(t / 3) % 3 === 0 ? 1 : Math.floor(t / 3) % 3 === 1 ? 3 : 2,
    imu: {
      gx_dps: Math.round(12 * Math.sin(t / 3)),
      gy_dps: Math.round(8 * Math.sin(t / 4)),
      gz_dps: Math.round(5 * Math.sin(t / 5)),
      ax_mg: Math.round(200 * Math.sin(t / 6)),
      ay_mg: Math.round(150 * Math.sin(t / 7)),
      az_mg: Math.round(980 + 20 * Math.sin(t / 8)),
      qi: Math.round(1000 * Math.cos(t / 10)),
      qj: Math.round(100 * Math.sin(t / 10)),
      qk: Math.round(50 * Math.sin(t / 11)),
      qr: Math.round(900 * Math.cos(t / 9)),
    },
    battery: {
      current_mA: Math.round(450 + 50 * Math.sin(t / 5)),
      avg_current_mA: Math.round(440 + 30 * Math.sin(t / 8)),
      voltage_mV: Math.round(7600 + 100 * Math.sin(t / 6)),
      average_voltage_mV: Math.round(7580 + 80 * Math.sin(t / 7)),
      cycle_count: 42,
      temperature_c: Number((25 + 2 * Math.sin(t / 10)).toFixed(2)),
      ext_temp1_c: Number((27 + Math.sin(t / 9)).toFixed(2)),
      ext_temp2_c: Number((26 + Math.sin(t / 8)).toFixed(2)),
      ext_temp3_c: Number((28 + Math.sin(t / 7)).toFixed(2)),
      ext_temp4_c: null,
      ext_temp5_c: null,
      ext_temp6_c: null,
      ext_temp7_c: null,
      ext_temp8_c: null,
      cell_voltage1_mV: Math.round(1900 + 20 * Math.sin(t / 6)),
      cell_voltage2_mV: Math.round(1910 + 15 * Math.sin(t / 5)),
      cell_voltage3_mV: Math.round(1895 + 18 * Math.sin(t / 7)),
      cell_voltage4_mV: Math.round(1905 + 12 * Math.sin(t / 8)),
    },
    tc: {
      tc_avg1: Number((312 + 5 * Math.sin(t / 4)).toFixed(1)),
      tc_avg2: Number((318 + 4 * Math.sin(t / 5)).toFixed(1)),
    },
    ground_station: "UCI",
  };
}

// ---- Dashboard -------------------------------------------------------------

export default function Dashboard() {
  const [status, setStatus] = useState<"offline" | "connecting" | "online">(
    USE_FAKE_TELEMETRY ? "online" : "connecting",
  );
  const [telemetry, setTelemetry] = useState<TelemetryPacket | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // Fake telemetry
  useEffect(() => {
    if (!USE_FAKE_TELEMETRY) return;
    const id = setInterval(() => setTelemetry(makeFakeTelemetry()), 250);
    return () => clearInterval(id);
  }, []);

  // Real telemetry WS
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
        setTelemetry(JSON.parse(event.data) as TelemetryPacket);
      } catch (e) {
        console.error("Telemetry parse error:", e);
      }
    };
    return () => ws.close();
  }, []);

  // Waterfall WS
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
      ctx.drawImage(canvas, 0, -1);
      const img = ctx.createImageData(BINS, 1);
      for (let x = 0; x < BINS; x++) {
        const t = clamp((row[x] - DB_MIN) / (DB_MAX - DB_MIN), 0, 1);
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

  const imu = telemetry?.imu;
  const batt = telemetry?.battery;
  const tc = telemetry?.tc;

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
      {/* Header */}
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

      <div className="mx-auto max-w-7xl px-4 py-4 space-y-4">
        {/* Waterfall */}
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

        {/* IMU + Battery row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* IMU card */}
          <Card title="IMU (PACKET_IMU)">
            <div className="mt-1 space-y-1">
              <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">
                Gyroscope (°/s)
              </p>
              <Row label="Gx" value={fmtInt(imu?.gx_dps, "°/s")} highlight />
              <Row label="Gy" value={fmtInt(imu?.gy_dps, "°/s")} highlight />
              <Row label="Gz" value={fmtInt(imu?.gz_dps, "°/s")} highlight />

              <p className="text-xs text-slate-500 uppercase tracking-wide mt-3 mb-2">
                Accelerometer (mg)
              </p>
              <Row label="Ax" value={fmtInt(imu?.ax_mg, "mg")} />
              <Row label="Ay" value={fmtInt(imu?.ay_mg, "mg")} />
              <Row label="Az" value={fmtInt(imu?.az_mg, "mg")} />

              <p className="text-xs text-slate-500 uppercase tracking-wide mt-3 mb-2">
                Quaternion (raw int16)
              </p>
              <div className="grid grid-cols-4 gap-2 text-sm">
                {(["qi", "qj", "qk", "qr"] as const).map((k) => (
                  <div key={k}>
                    <div className="text-slate-500 text-xs">{k}</div>
                    <div className="font-mono">{imu?.[k] ?? "—"}</div>
                  </div>
                ))}
              </div>
            </div>
          </Card>

          {/* Battery card */}
          <Card title="Battery (batt_combined_telemetry_1)">
            <div className="space-y-1">
              <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">
                Electrical
              </p>
              <Row
                label="Voltage"
                value={fmtInt(batt?.voltage_mV, "mV")}
                highlight
              />
              <Row
                label="Avg Voltage"
                value={fmtInt(batt?.average_voltage_mV, "mV")}
              />
              <Row
                label="Current"
                value={fmtInt(batt?.current_mA, "mA")}
                highlight
              />
              <Row
                label="Avg Current"
                value={fmtInt(batt?.avg_current_mA, "mA")}
              />
              <Row
                label="Cycle Count"
                value={
                  batt?.cycle_count != null ? String(batt.cycle_count) : "—"
                }
              />

              <p className="text-xs text-slate-500 uppercase tracking-wide mt-3 mb-2">
                Cell Voltages (mV)
              </p>
              <div className="grid grid-cols-4 gap-2 text-sm">
                {([1, 2, 3, 4] as const).map((n) => (
                  <div key={n}>
                    <div className="text-slate-500 text-xs">Cell {n}</div>
                    <div className="font-mono">
                      {batt?.[`cell_voltage${n}_mV` as keyof BatteryData] ??
                        "—"}
                    </div>
                  </div>
                ))}
              </div>

              <p className="text-xs text-slate-500 uppercase tracking-wide mt-3 mb-2">
                Temperatures (°C)
              </p>
              <Row label="Cell Temp" value={fmt(batt?.temperature_c, "°C")} />
              {([1, 2, 3, 4, 5, 6, 7, 8] as const).map((n) => {
                const v = batt?.[`ext_temp${n}_c` as keyof BatteryData] as
                  | number
                  | null
                  | undefined;
                if (v == null) return null;
                return (
                  <Row key={n} label={`Ext Sensor ${n}`} value={fmt(v, "°C")} />
                );
              })}
            </div>
          </Card>
        </div>

        {/* Thermocouple card — full width */}
        <Card title="Thermocouples (TCPayload)">
          <div className="grid grid-cols-2 gap-6 text-sm mt-1">
            <div>
              <div className="text-slate-500 text-xs mb-1">TC Average 1</div>
              <div className="text-2xl font-mono text-emerald-400">
                {tc?.tc_avg1 != null ? `${tc.tc_avg1.toFixed(1)}` : "—"}
                <span className="text-base text-slate-400 ml-1">°C</span>
              </div>
            </div>
            <div>
              <div className="text-slate-500 text-xs mb-1">TC Average 2</div>
              <div className="text-2xl font-mono text-emerald-400">
                {tc?.tc_avg2 != null ? `${tc.tc_avg2.toFixed(1)}` : "—"}
                <span className="text-base text-slate-400 ml-1">°C</span>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
