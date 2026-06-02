import { apiGet } from "./apiClient";
import type { DropoffAnalytics, FunnelAnalytics, RetentionAnalytics } from "../types/api";

export const analyticsApi = {
  funnel: () => apiGet<FunnelAnalytics>("/analytics/funnel?persist_snapshot=false"),
  dropoff: () => apiGet<DropoffAnalytics>("/analytics/dropoff?persist_snapshot=false"),
  retention: () => apiGet<RetentionAnalytics>("/analytics/retention?persist_snapshot=false")
};
