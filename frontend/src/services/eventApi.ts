import { apiGet } from "./apiClient";
import type { EventHealth } from "../types/api";

export const eventApi = {
  health: () => apiGet<EventHealth>("/events/health")
};
