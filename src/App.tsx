import { BrowserRouter, Routes, Route } from "react-router-dom";
import AppLayout from "./layout/AppLayout";

import Dashboard from "./pages/Dashboard";
import Telemetry from "./pages/Telemetry";
import RFLink from "./pages/RFLink";
import PassPlanner from "./pages/PassPlanner";
import AntennaControl from "./pages/AntennaControl";
import Logs from "./pages/Logs";
import Settings from "./pages/Settings";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Layout wrapper route */}
        <Route element={<AppLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/telemetry" element={<Telemetry />} />
          <Route path="/rf-link" element={<RFLink />} />
          <Route path="/pass-planner" element={<PassPlanner />} />
          <Route path="/antenna-control" element={<AntennaControl />} />
          <Route path="/logs" element={<Logs />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
