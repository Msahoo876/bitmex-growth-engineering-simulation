import { AlertCircle, RefreshCw } from "lucide-react";

import { Button } from "./button";
import { Card, CardContent } from "./card";

export function LoadingState({ label = "Loading analytics" }: { label?: string }) {
  return (
    <Card>
      <CardContent className="flex min-h-40 items-center justify-center text-sm text-muted">
        <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
        {label}
      </CardContent>
    </Card>
  );
}

export function EmptyState({ label = "No data available yet" }: { label?: string }) {
  return (
    <Card>
      <CardContent className="flex min-h-36 items-center justify-center text-sm text-muted">
        {label}
      </CardContent>
    </Card>
  );
}

export function ErrorState({ onRetry }: { onRetry?: () => void }) {
  return (
    <Card>
      <CardContent className="flex min-h-40 flex-col items-center justify-center gap-3 text-sm text-muted">
        <AlertCircle className="h-5 w-5 text-danger" />
        <span>Could not load this analytics view.</span>
        {onRetry ? (
          <Button variant="secondary" onClick={onRetry}>
            Retry
          </Button>
        ) : null}
      </CardContent>
    </Card>
  );
}
