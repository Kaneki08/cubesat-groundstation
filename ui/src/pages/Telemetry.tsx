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
          {/* Y Axis */}
          <div className="flex flex-col justify-between pr-2 text-xs text-slate-400">
            <div>20 s</div>
            <div>15 s</div>
            <div>10 s</div>
            <div>5 s</div>
            <div>0 s</div>
          </div>

          {/* Canvas + X Axis */}
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
