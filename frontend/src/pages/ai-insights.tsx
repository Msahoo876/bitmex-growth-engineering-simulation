import { RefreshCw, Sparkles } from "lucide-react";

import { PageHeading } from "../components/layout/page-heading";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { EmptyState, ErrorState, LoadingState } from "../components/ui/page-state";
import { useExecutiveSummary, useGenerateInsights, useInsights } from "../hooks/useGrowthData";

const toneForPriority = (priority?: string | null) => {
  if (priority === "high") return "red" as const;
  if (priority === "medium") return "amber" as const;
  return "green" as const;
};

export function AiInsights() {
  const insights = useInsights();
  const executive = useExecutiveSummary();
  const generate = useGenerateInsights();

  if (insights.isLoading || executive.isLoading) return <LoadingState label="Loading AI insights" />;
  if (insights.isError || executive.isError) {
    return <ErrorState onRetry={() => void Promise.all([insights.refetch(), executive.refetch()])} />;
  }

  const items = insights.data?.insights ?? [];

  return (
    <>
      <PageHeading
        eyebrow="AI Insights"
        title="Gemini growth recommendations"
        description="Generate executive summaries, funnel recommendations, attribution guidance, and data quality actions from structured metrics."
        action={
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => void insights.refetch()}>
              <RefreshCw className="h-4 w-4" />
              Refresh
            </Button>
            <Button onClick={() => generate.mutate()} disabled={generate.isPending}>
              <Sparkles className="h-4 w-4" />
              {generate.isPending ? "Generating" : "Generate Insights"}
            </Button>
          </div>
        }
      />

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>{executive.data?.title}</CardTitle>
          <Badge tone="green">Executive Summary</Badge>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm leading-6 text-zinc-300">{executive.data?.summary}</p>
          <div className="grid gap-3 md:grid-cols-3">
            {executive.data?.recommendations.map((item) => (
              <div key={item.text} className="rounded-md border border-border bg-black/30 p-4">
                <Badge tone="cyan">{item.category}</Badge>
                <p className="mt-3 text-sm text-white">{item.text}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <section className="mt-4 grid gap-4 xl:grid-cols-2">
        {items.length === 0 ? (
          <EmptyState label="No stored insights yet. Generate a fresh set to populate this workspace." />
        ) : (
          items.map((item) => (
            <Card key={item.id}>
              <CardHeader className="flex flex-row items-start justify-between gap-3">
                <div>
                  <CardTitle>{item.title}</CardTitle>
                  <p className="mt-1 text-xs uppercase text-muted">{item.insight_type}</p>
                </div>
                <Badge tone={toneForPriority(item.priority)}>{item.priority ?? "normal"}</Badge>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm leading-6 text-zinc-300">{item.summary}</p>
                <div className="space-y-2">
                  {item.recommendations.map((recommendation) => (
                    <div key={recommendation.text} className="rounded-md border border-border bg-black/30 p-3">
                      <div className="mb-2 flex flex-wrap gap-2">
                        <Badge tone="cyan">{recommendation.category}</Badge>
                        <Badge>{recommendation.impact} impact</Badge>
                        <Badge>{recommendation.effort} effort</Badge>
                      </div>
                      <p className="text-sm text-white">{recommendation.text}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </section>
    </>
  );
}
