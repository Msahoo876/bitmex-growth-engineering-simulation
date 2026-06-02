import type { ReactNode } from "react";

import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";

export function ChartShell({
  title,
  children,
  action
}: {
  title: string;
  children: ReactNode;
  action?: ReactNode;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>{title}</CardTitle>
        {action}
      </CardHeader>
      <CardContent className="h-80">{children}</CardContent>
    </Card>
  );
}
