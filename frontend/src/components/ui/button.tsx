import type { ButtonHTMLAttributes } from "react";

import { cn } from "../../lib/cn";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost";
}

export function Button({ className, variant = "primary", ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex h-10 items-center justify-center gap-2 rounded-md px-4 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-60",
        variant === "primary" && "bg-primary text-black hover:bg-primary/90",
        variant === "secondary" && "border border-border bg-zinc-900 text-zinc-100 hover:bg-zinc-800",
        variant === "ghost" && "text-zinc-300 hover:bg-zinc-900 hover:text-white",
        className
      )}
      {...props}
    />
  );
}
