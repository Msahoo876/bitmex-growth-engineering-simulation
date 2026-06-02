import { apiGet, apiPost } from "./apiClient";
import type { ExecutiveSummary, GeneratedInsights, InsightList } from "../types/api";

export const insightApi = {
  list: () => apiGet<InsightList>("/insights"),
  executiveSummary: () => apiGet<ExecutiveSummary>("/insights/executive-summary"),
  generate: () =>
    apiPost<GeneratedInsights>("/insights/generate", {
      insight_types: ["executive", "funnel", "attribution", "quality", "recommendations"]
    })
};
