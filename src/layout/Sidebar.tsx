import { NavLink } from "react-router-dom";

const navItems = [
  { label: "Dashboard", to: "/" },
  { label: "Telemetry", to: "/telemetry" },
  { label: "RF & Link", to: "/rf-link" },
  { label: "Pass Planner", to: "/pass-planner" },
  { label: "Antenna Control", to: "/antenna-control" },
  { label: "Logs", to: "/logs" },
  { label: "Settings", to: "/settings" },
];

export default function Sidebar() {
  return (
    <aside className="w-72 border-r border-slate-800 bg-slate-950/60 px-4 py-5">
      {/* Brand */}
      <div className="mb-6">
        <div className="text-sm text-slate-400">UCI CubeSat</div>
        <div className="text-lg font-semibold">Ground Station Console</div>
      </div>

      {/* Nav */}
      <nav className="space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"} // makes "/" only active on exact home
            className={({ isActive }) =>
              isActive
                ? "block rounded-xl px-3 py-2 text-sm transition bg-slate-800/60 text-slate-50"
                : "block rounded-xl px-3 py-2 text-sm transition text-slate-300 hover:bg-slate-900 hover:text-slate-50"
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="mt-8 border-t border-slate-800 pt-4">
        <div className="text-xs text-slate-500">Operator</div>
        <div className="text-sm text-slate-200">Mission Control</div>
      </div>
    </aside>
  );
}
