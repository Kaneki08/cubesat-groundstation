import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";

export default function AppLayout() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="flex min-h-screen">
        <Sidebar />

        <div className="flex-1">
          {/* Topbar */}
          <header className="flex h-14 items-center justify-between border-b border-slate-800 bg-slate-950/40 px-6">
            <div className="text-sm text-slate-300">
              UTC Time: <span className="ml-1 text-slate-100">--:--:--</span>
            </div>

            <div className="flex items-center gap-4 text-sm">
              <span className="text-slate-300">
                Ground Station: <span className="ml-1 text-emerald-400">Online</span>
              </span>
              <span className="text-slate-300">
                Radio: <span className="ml-1 text-emerald-400">Online</span>
              </span>
            </div>
          </header>

          {/* Page content */}
          <main className="p-6 max-w-[1400px] mx-auto">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}
