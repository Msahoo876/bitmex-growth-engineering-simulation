import {
  Area,
  AreaChart,
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
  useQualityAnomalies,
  useQualityDuplicates,
  useQualityHealth,
  useQualityIntegrity,
  useQualitySchemaErrors
} from "../hooks/useGrowthData";
import { AlertTriangle, CopyX, Gauge, GitPullRequestClosed, ShieldCheck } from "lucide-react";

export function DataQuality() {
  const health = useQualityHealth();
  const duplicates = useQualityDuplicates();
  const schemaErrors = useQualitySchemaErrors();
  const integrity = useQualityIntegrity();
  const anomalies = useQualityAnomalies();
  const queries = [health, duplicates, schemaErrors, integrity, anomalies] as const;

  if (queries.some((query) => query.isLoading)) return <LoadingState label="Loading data quality" />;
  if (queries.some((query) => query.isError)) {
    return <ErrorState onRetry={() => queries.forEach((query) => void query.refetch())} />;
  }

  const score = health.data?.health_score ?? 0;
  const trendData = Object.entries(anomalies.data?.daily_volume ?? {}).map(([date, count]) => ({
    date,
    count
  }));

  return (
    <>
      <PageHeading
        eyebrow="Data Quality"
        title="Tracking reliability and analytics health"
        description="Monitor duplicate events, schema errors, funnel integrity, and volume anomalies before they distort growth reporting."
        action={<Badge tone={score >= 90 ? "green" : "amber"}>{score} health score</Badge>}
      />

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <MetricCard label="Health Score" value={`${score}`} icon={Gauge} tone={score >= 90 ? "green" : "amber"} />
        <MetricCard
          label="Duplicate Events"
          value={`${duplicates.data?.total_duplicate_events ?? 0}`}
          icon={CopyX}
          tone="amber"
        />
        <MetricCard
          label="Schema Errors"
          value={`${schemaErrors.data?.total_errors ?? 0}`}
          icon={AlertTriangle}
          tone="red"
        />
        <MetricCard
          label="Broken Paths"
          value={`${integrity.data?.total_broken_paths ?? 0}`}
          icon={GitPullRequestClosed}
          tone="cyan"
        />
        <MetricCard
          label="Anomalies"
          value={`${anomalies.data?.total_anomalies ?? 0}`}
          icon={ShieldCheck}
          tone="green"
        />
      </section>

      <section className="mt-4 grid gap-4 xl:grid-cols-[.75fr_1.25fr]">
        <Card>
          <CardHeader>
            <CardTitle>Score Gauge</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center gap-4">
            <div
              className="grid h-44 w-44 place-items-center rounded-full border-8 border-primary bg-primary/10"
              style={{
                boxShadow: `inset 0 0 0 ${Math.max(0, 100 - score) / 2}px rgba(255,92,92,.12)`
              }}
            >
              <div className="text-center">
                <p className="text-4xl font-semibold text-white">{score}</p>
                <p className="text-xs uppercase text-muted">out of 100</p>
              </div>
            </div>
            <p className="max-w-sm text-center text-sm text-muted">
              Scores below 85 should block executive interpretation until instrumentation issues are reviewed.
            </p>
          </CardContent>
        </Card>

        <ChartShell title="Event Volume Trend">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={trendData}>
              <defs>
                <linearGradient id="volume" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="5%" stopColor="#00b7c7" stopOpacity={0.7} />
                  <stop offset="95%" stopColor="#00b7c7" stopOpacity={0.05} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="#202621" vertical={false} />
              <XAxis dataKey="date" stroke="#9aa39c" />
              <YAxis stroke="#9aa39c" />
              <Tooltip contentStyle={{ background: "#0d0f0e", border: "1px solid #202621" }} />
              <Area dataKey="count" fill="url(#volume)" stroke="#00b7c7" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </ChartShell>
      </section>

      <Card className="mt-4">
        <CardHeader>
          <CardTitle>Penalty Breakdown</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {Object.entries(health.data?.breakdown ?? {}).map(([key, value]) => (
            <div key={key} className="rounded-md border border-border bg-black/30 p-4">
              <p className="text-xs uppercase text-muted">{key.replaceAll("_", " ")}</p>
              <p className="mt-2 text-xl font-semibold text-white">{value.toFixed(2)}</p>
            </div>
          ))}
        </CardContent>
      </Card>
    </>
  );
}
