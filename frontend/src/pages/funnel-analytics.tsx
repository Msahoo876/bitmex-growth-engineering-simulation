import {
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
import { EmptyState, ErrorState, LoadingState } from "../components/ui/page-state";
import { useDropoffAnalytics, useFunnelAnalytics } from "../hooks/useGrowthData";

export function FunnelAnalytics() {
  const funnel = useFunnelAnalytics();
  const dropoff = useDropoffAnalytics();
  const isLoading = funnel.isLoading || dropoff.isLoading;
  const isError = funnel.isError || dropoff.isError;

  if (isLoading) return <LoadingState label="Loading funnel analytics" />;
  if (isError) return <ErrorState onRetry={() => void Promise.all([funnel.refetch(), dropoff.refetch()])} />;
  if (!funnel.data?.steps.length) return <EmptyState label="No funnel events have been tracked yet." />;

  const chartData = funnel.data.steps.map((step) => ({
    step: step.label,
    users: step.users,
    completion: step.conversion_rate_from_start
  }));

  return (
    <>
      <PageHeading
        eyebrow="Funnel Analytics"
        title="Landing to trade conversion"
        description="Track the crypto exchange activation path from first landing page view through first trade."
        action={<Badge tone="cyan">{funnel.data.completion_rate}% completion</Badge>}
      />

      <section className="grid gap-4 xl:grid-cols-[.85fr_1.15fr]">
        <Card>
          <CardHeader>
            <CardTitle>Funnel Visualization</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {funnel.data.steps.map((step, index) => (
              <div key={step.key}>
                <div className="flex items-center justify-between rounded-md border border-border bg-black/30 p-4">
                  <div>
                    <p className="text-sm font-medium text-white">{step.label}</p>
                    <p className="text-xs text-muted">{step.event_name}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-semibold text-white">{step.users}</p>
                    <p className="text-xs text-muted">{step.conversion_rate_from_start}% from start</p>
                  </div>
                </div>
                {index < funnel.data.steps.length - 1 ? (
                  <div className="mx-6 h-5 border-l border-dashed border-primary/40" />
                ) : null}
              </div>
            ))}
          </CardContent>
        </Card>

        <ChartShell title="Step Completion">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid stroke="#202621" vertical={false} />
              <XAxis dataKey="step" stroke="#9aa39c" />
              <YAxis stroke="#9aa39c" />
              <Tooltip contentStyle={{ background: "#0d0f0e", border: "1px solid #202621" }} />
              <Bar dataKey="users" fill="#00d084" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartShell>
      </section>

      <section className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {dropoff.data?.steps.map((step) => (
          <Card key={`${step.from_step}-${step.to_step}`}>
            <CardContent>
              <p className="text-xs uppercase text-muted">
                {step.from_step} to {step.to_step}
              </p>
              <p className="mt-3 text-2xl font-semibold text-white">{step.dropoff_rate}%</p>
              <p className="text-sm text-muted">{step.users_lost} users lost</p>
            </CardContent>
          </Card>
        ))}
      </section>
    </>
  );
}
