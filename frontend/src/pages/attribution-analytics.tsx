import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

import { ChartShell } from "../components/charts/chart-shell";
import { PageHeading } from "../components/layout/page-heading";
import { Badge } from "../components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { EmptyState, ErrorState, LoadingState } from "../components/ui/page-state";
import {
  useCampaignAttribution,
  useDeepLinks,
  useReferrals,
  useSourceAttribution,
  useTopSource
} from "../hooks/useGrowthData";

const COLORS = ["#00d084", "#00b7c7", "#f6b44b", "#ff5c5c", "#7ddf64"];

export function AttributionAnalytics() {
  const sources = useSourceAttribution();
  const campaigns = useCampaignAttribution();
  const topSource = useTopSource();
  const referrals = useReferrals();
  const deepLinks = useDeepLinks();
  const queries = [sources, campaigns, topSource, referrals, deepLinks] as const;

  if (queries.some((query) => query.isLoading)) return <LoadingState label="Loading attribution analytics" />;
  if (queries.some((query) => query.isError)) {
    return <ErrorState onRetry={() => queries.forEach((query) => void query.refetch())} />;
  }
  if (!sources.data?.metrics.length) return <EmptyState label="No attribution events are available yet." />;

  const sourceData = sources.data.metrics.map((metric) => ({
    name: `${metric.source} (${metric.touch_type})`,
    users: metric.users
  }));

  return (
    <>
      <PageHeading
        eyebrow="Attribution Analytics"
        title="Source and campaign performance"
        description="Compare first-touch and last-touch acquisition paths, referrals, deep links, and campaign contribution."
        action={<Badge tone="cyan">Top: {topSource.data?.source ?? "N/A"}</Badge>}
      />

      <section className="grid gap-4 xl:grid-cols-2">
        <ChartShell title="Source Performance">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={sourceData}>
              <CartesianGrid stroke="#202621" vertical={false} />
              <XAxis dataKey="name" stroke="#9aa39c" />
              <YAxis stroke="#9aa39c" />
              <Tooltip contentStyle={{ background: "#0d0f0e", border: "1px solid #202621" }} />
              <Bar dataKey="users" fill="#00b7c7" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartShell>

        <ChartShell title="Channel Mix">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={sourceData} dataKey="users" nameKey="name" outerRadius={110} label>
                {sourceData.map((entry, index) => (
                  <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: "#0d0f0e", border: "1px solid #202621" }} />
            </PieChart>
          </ResponsiveContainer>
        </ChartShell>
      </section>

      <section className="mt-4 grid gap-4 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <CardHeader>
            <CardTitle>Campaign Performance</CardTitle>
          </CardHeader>
          <CardContent className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-xs uppercase text-muted">
                <tr>
                  <th className="py-2">Campaign</th>
                  <th>Source</th>
                  <th>Touch</th>
                  <th className="text-right">Users</th>
                </tr>
              </thead>
              <tbody>
                {campaigns.data?.metrics.map((metric) => (
                  <tr key={`${metric.campaign_name}-${metric.touch_type}`} className="border-t border-border">
                    <td className="py-3 text-white">{metric.campaign_name}</td>
                    <td>{metric.source}</td>
                    <td>{metric.touch_type}</td>
                    <td className="text-right">{metric.users}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Referral and Deep Link Leaders</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="mb-2 text-xs uppercase text-muted">Referrals</p>
              {(referrals.data?.metrics ?? []).slice(0, 4).map((metric) => (
                <div key={metric.referral_code} className="flex justify-between border-t border-border py-2 text-sm">
                  <span>{metric.referral_code}</span>
                  <span className="text-white">{metric.users}</span>
                </div>
              ))}
            </div>
            <div>
              <p className="mb-2 text-xs uppercase text-muted">Deep Links</p>
              {(deepLinks.data?.metrics ?? []).slice(0, 4).map((metric) => (
                <div key={metric.deep_link} className="flex justify-between border-t border-border py-2 text-sm">
                  <span>{metric.deep_link}</span>
                  <span className="text-white">{metric.users}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </section>
    </>
  );
}
