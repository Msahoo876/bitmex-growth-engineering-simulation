import { Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "./components/layout/app-layout";
import { AiInsights } from "./pages/ai-insights";
import { AttributionAnalytics } from "./pages/attribution-analytics";
import { DataQuality } from "./pages/data-quality";
import { ExecutiveDashboard } from "./pages/executive-dashboard";
import { FunnelAnalytics } from "./pages/funnel-analytics";

export function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<ExecutiveDashboard />} />
        <Route path="/funnels" element={<FunnelAnalytics />} />
        <Route path="/attribution" element={<AttributionAnalytics />} />
        <Route path="/quality" element={<DataQuality />} />
        <Route path="/insights" element={<AiInsights />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
