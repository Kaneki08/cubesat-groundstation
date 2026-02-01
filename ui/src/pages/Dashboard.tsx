// Import the reusable Card component
import Card from "../Components/Card";

export default function Dashboard() {
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
        </Card>
      </div>

      {/* ================= MIDDLE COLUMN ================= */}
      <div className="space-y-6">

        <Card title="Power">
          <div className="text-sm space-y-2">
            <div className="flex justify-between">
              <span>Battery Voltage</span>
              <span className="text-emerald-400">7.4 V</span>
            </div>
            <div className="flex justify-between">
              <span>Solar Current</span>
              <span className="text-emerald-400">1.2 A</span>
            </div>
            <div className="flex justify-between">
              <span>Battery Temp</span>
              <span>18 °C</span>
            </div>
          </div>
        </Card>

        <Card title="Orientation (ADCS)">
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <div className="text-slate-500">Roll</div>
              <div>-2.3°</div>
            </div>
            <div>
              <div className="text-slate-500">Pitch</div>
              <div>1.8°</div>
            </div>
            <div>
              <div className="text-slate-500">Yaw</div>
              <div>0.5°</div>
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
              <span>437.1 MHz</span>
            </div>
            <div className="flex justify-between">
              <span>RSSI</span>
              <span className="text-emerald-400">-87 dBm</span>
            </div>
            <div className="flex justify-between">
              <span>SNR</span>
              <span className="text-emerald-400">12.3 dB</span>
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
