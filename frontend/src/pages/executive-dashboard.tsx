import { Activity, DollarSign, Gauge, Users, Wallet, Waypoints } from "lucide-react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

import { ChartShell } from "../components/charts/chart-shell";
import { PageHeading } from "../components/layout/page-heading";
import { Badge } from "../components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { MetricCard } from "../components/ui/metric-card";
import { ErrorState, LoadingState } from "../components/ui/page-state";
import {
  useExecutiveSummary,
  useFunnelAnalytics,
  useQualityHealth,
  useRetentionAnalytics,
  useSourceAttribution,
  useTopSource
} from "../hooks/useGrowthData";

const formatNumber = (value?: number) => new Intl.NumberFormat().format(value ?? 0);
const formatCurrency = (value?: number) =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(
    value ?? 0
  );

export function ExecutiveDashboard() {
  const funnel = useFunnelAnalytics();
  const quality = useQualityHealth();
  const topSource = useTopSource();
  const sources = useSourceAttribution();
  const retention = useRetentionAnalytics();
  const summary = useExecutiveSummary();

  const queries = [funnel, quality, topSource, sources, retention, summary] as const;
  const isLoading = queries.some((query) => query.isLoading);
  const isError = queries.some((query) => query.isError);
  const retry = () => queries.forEach((query) => void query.refetch());

  if (isLoading) return <LoadingState label="Loading executive dashboard" />;
  if (isError) return <ErrorState onRetry={retry} />;

  const activeTraders = funnel.data?.total_completed ?? 0;
  const estimatedRevenue = activeTraders * 1250;
  const retentionData = retention.data?.periods.map((period) => ({
    day: `D${period.day}`,
    retention: period.retention_rate
  }));
  const sourceData = sources.data?.metrics.slice(0, 6).map((metric) => ({
    source: metric.source,
    users: metric.users
  }));

  return (
    <>
      <PageHeading
        eyebrow="Executive Dashboard"
        title="Crypto growth command center"
        description="A single operating view for acquisition, onboarding, trading activation, revenue proxy, and analytics health."
        action={<Badge tone="green">Live API</Badge>}
      />

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-6">
        <MetricCard label="Total Users" value={formatNumber(funnel.data?.total_entered)} icon={Users} />
        <MetricCard
          label="Active Users"
          value={formatNumber(retention.data?.cohort_size)}
          icon={Activity}
          tone="cyan"
        />
        <MetricCard
          label="Active Traders"
          value={formatNumber(activeTraders)}
          icon={Wallet}
          tone="green"
        />
        <MetricCard
          label="Revenue"
          value={formatCurrency(estimatedRevenue)}
          icon={DollarSign}
          tone="amber"
        />
        <MetricCard
          label="Health Score"
          value={`${quality.data?.health_score ?? 0}`}
          icon={Gauge}
          tone={(quality.data?.health_score ?? 0) >= 85 ? "green" : "amber"}
        />
        <MetricCard
          label="Top Source"
          value={topSource.data?.source ?? "N/A"}
          delta={`${topSource.data?.users ?? 0} users`}
          icon={Waypoints}
          tone="cyan"
        />
      </section>

      <section className="mt-4 grid gap-4 xl:grid-cols-[1.1fr_.9fr]">
        <ChartShell title="Retention Trend">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={retentionData}>
              <defs>
                <linearGradient id="retention" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="5%" stopColor="#00d084" stopOpacity={0.7} />
                  <stop offset="95%" stopColor="#00d084" stopOpacity={0.05} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="#202621" vertical={false} />
              <XAxis dataKey="day" stroke="#9aa39c" />
              <YAxis stroke="#9aa39c" />
              <Tooltip contentStyle={{ background: "#0d0f0e", border: "1px solid #202621" }} />
              <Area dataKey="retention" fill="url(#retention)" stroke="#00d084" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </ChartShell>

        <ChartShell title="Top Source Volume">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={sourceData}>
              <CartesianGrid stroke="#202621" vertical={false} />
              <XAxis dataKey="source" stroke="#9aa39c" />
              <YAxis stroke="#9aa39c" />
              <Tooltip contentStyle={{ background: "#0d0f0e", border: "1px solid #202621" }} />
              <Bar dataKey="users" fill="#00b7c7" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartShell>
      </section>

      <section className="mt-4 grid gap-4 lg:grid-cols-[.9fr_1.1fr]">
        <Card>
          <CardHeader>
            <CardTitle>AI Executive Summary</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <h3 className="text-lg font-semibold text-white">{summary.data?.title}</h3>
            <p className="text-sm leading-6 text-zinc-300">{summary.data?.summary}</p>
            <div className="space-y-2">
              {summary.data?.recommendations.slice(0, 3).map((item) => (
                <div key={item.text} className="rounded-md border border-border bg-black/30 p-3 text-sm">
                  {item.text}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quality Penalty Breakdown</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3 sm:grid-cols-2">
            {Object.entries(quality.data?.breakdown ?? {}).map(([key, value]) => (
              <div key={key} className="rounded-md border border-border bg-black/30 p-4">
                <p className="text-xs uppercase text-muted">{key.replaceAll("_", " ")}</p>
                <p className="mt-2 text-xl font-semibold text-white">{value.toFixed(2)}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      </section>
    </>
  );
}
