import type { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost";
};

export function Button({ className, variant = "primary", ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex h-10 items-center justify-center gap-2 rounded-md px-4 text-sm font-medium transition",
        "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
        variant === "primary" && "bg-ink text-white hover:bg-slate-700",
        variant === "secondary" && "border border-border bg-white text-ink hover:bg-muted",
        variant === "ghost" && "text-slate-700 hover:bg-muted",
        className,
      )}
      {...props}
    />
  );
}
