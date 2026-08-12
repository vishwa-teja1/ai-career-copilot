"use client";

import { ButtonHTMLAttributes, forwardRef } from "react";
import clsx from "clsx";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "ghost";
  loading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", loading, children, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={clsx(
          "inline-flex items-center justify-center gap-2 rounded-xl px-5 py-3 font-medium transition-all duration-150",
          "disabled:cursor-not-allowed disabled:opacity-60",
          variant === "primary" &&
            "bg-accent text-ink hover:brightness-110 active:scale-[0.98] shadow-[0_0_0_1px_rgba(79,140,255,0.4)]",
          variant === "ghost" && "border border-line text-muted hover:text-white hover:border-accent/60",
          className
        )}
        {...props}
      >
        {loading && (
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
        )}
        {children}
      </button>
    );
  }
);
Button.displayName = "Button";
