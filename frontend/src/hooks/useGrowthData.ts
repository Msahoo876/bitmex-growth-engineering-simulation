import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { analyticsApi } from "../services/analyticsApi";
import { attributionApi } from "../services/attributionApi";
import { eventApi } from "../services/eventApi";
import { insightApi } from "../services/insightApi";
import { qualityApi } from "../services/qualityApi";

export const useFunnelAnalytics = () =>
  useQuery({ queryKey: ["analytics", "funnel"], queryFn: analyticsApi.funnel });

export const useDropoffAnalytics = () =>
  useQuery({ queryKey: ["analytics", "dropoff"], queryFn: analyticsApi.dropoff });

export const useRetentionAnalytics = () =>
  useQuery({ queryKey: ["analytics", "retention"], queryFn: analyticsApi.retention });

export const useSourceAttribution = () =>
  useQuery({ queryKey: ["attribution", "sources"], queryFn: attributionApi.sources });

export const useCampaignAttribution = () =>
  useQuery({ queryKey: ["attribution", "campaigns"], queryFn: attributionApi.campaigns });

export const useTopSource = () =>
  useQuery({ queryKey: ["attribution", "top-source"], queryFn: attributionApi.topSource });

export const useReferrals = () =>
  useQuery({ queryKey: ["attribution", "referrals"], queryFn: attributionApi.referrals });

export const useDeepLinks = () =>
  useQuery({ queryKey: ["attribution", "deep-links"], queryFn: attributionApi.deepLinks });

export const useQualityHealth = () =>
  useQuery({ queryKey: ["quality", "health"], queryFn: qualityApi.health });

export const useQualityDuplicates = () =>
  useQuery({ queryKey: ["quality", "duplicates"], queryFn: qualityApi.duplicates });

export const useQualitySchemaErrors = () =>
  useQuery({ queryKey: ["quality", "schema-errors"], queryFn: qualityApi.schemaErrors });

export const useQualityIntegrity = () =>
  useQuery({ queryKey: ["quality", "integrity"], queryFn: qualityApi.integrity });

export const useQualityAnomalies = () =>
  useQuery({ queryKey: ["quality", "anomalies"], queryFn: qualityApi.anomalies });

export const useInsights = () =>
  useQuery({ queryKey: ["insights"], queryFn: insightApi.list });

export const useExecutiveSummary = () =>
  useQuery({ queryKey: ["insights", "executive-summary"], queryFn: insightApi.executiveSummary });

export const useEventHealth = () =>
  useQuery({ queryKey: ["events", "health"], queryFn: eventApi.health });

export const useGenerateInsights = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: insightApi.generate,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["insights"] });
    }
  });
};
