import { apiGet } from "./apiClient";
import type { CampaignAttribution, SourceAttribution, TopSource } from "../types/api";

export const attributionApi = {
  sources: () => apiGet<SourceAttribution>("/attribution/sources"),
  campaigns: () => apiGet<CampaignAttribution>("/attribution/campaigns"),
  topSource: () => apiGet<TopSource>("/attribution/top-source"),
  referrals: () => apiGet<{ metrics: { referral_code: string; users: number }[] }>("/attribution/referrals"),
  deepLinks: () => apiGet<{ metrics: { deep_link: string; users: number }[] }>("/attribution/deep-links")
};
