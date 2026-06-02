import { apiGet } from "./apiClient";
import type { Anomalies, DataHealth, Duplicates, FunnelIntegrity, SchemaErrors } from "../types/api";

export const qualityApi = {
  health: () => apiGet<DataHealth>("/quality/health?persist_score=false"),
  duplicates: () => apiGet<Duplicates>("/quality/duplicates"),
  schemaErrors: () => apiGet<SchemaErrors>("/quality/schema-errors"),
  integrity: () => apiGet<FunnelIntegrity>("/quality/funnel-integrity"),
  anomalies: () => apiGet<Anomalies>("/quality/anomalies")
};
