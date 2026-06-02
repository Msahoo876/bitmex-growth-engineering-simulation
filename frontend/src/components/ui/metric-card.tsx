import type { LucideIcon } from "lucide-react";

import { cn } from "../../lib/cn";
import { Badge } from "./badge";
import { Card, CardContent } from "./card";

interface MetricCardProps {
  label: string;
  value: string;
  delta?: string;
  icon: LucideIcon;
  tone?: "green" | "cyan" | "amber" | "red" | "neutral";
}

export function MetricCard({ label, value, delta, icon: Icon, tone = "green" }: MetricCardProps) {
  return (
    <Card>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted">{label}</span>
          <span
            className={cn(
              "rounded-md border border-border p-2",
              tone === "green" && "text-primary",
              tone === "cyan" && "text-accent",
              tone === "amber" && "text-warning",
              tone === "red" && "text-danger"
            )}
          >
            <Icon className="h-4 w-4" />
          </span>
        </div>
        <div className="flex items-end justify-between gap-3">
          <strong className="text-2xl font-semibold text-white">{value}</strong>
          {delta ? <Badge tone={tone}>{delta}</Badge> : null}
        </div>
      </CardContent>
    </Card>
  );
}
