import type { HTMLAttributes } from "react";

import { cn } from "../../lib/cn";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: "green" | "cyan" | "amber" | "red" | "neutral";
}

export function Badge({ className, tone = "neutral", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex rounded-full border px-2.5 py-1 text-xs font-medium",
        tone === "green" && "border-primary/30 bg-primary/10 text-primary",
        tone === "cyan" && "border-accent/30 bg-accent/10 text-accent",
        tone === "amber" && "border-warning/30 bg-warning/10 text-warning",
        tone === "red" && "border-danger/30 bg-danger/10 text-danger",
        tone === "neutral" && "border-border bg-zinc-900 text-zinc-300",
        className
      )}
      {...props}
    />
  );
}
