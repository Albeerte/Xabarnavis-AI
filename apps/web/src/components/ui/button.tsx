import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-full text-sm font-semibold transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default:
          "bg-cyan-400 text-slate-950 shadow-[0_0_32px_rgba(34,211,238,0.35)] hover:bg-cyan-300 hover:shadow-[0_0_48px_rgba(34,211,238,0.45)]",
        secondary:
          "border border-white/12 bg-white/[0.06] text-white backdrop-blur-xl hover:border-cyan-300/40 hover:bg-white/[0.1]",
        ghost: "text-slate-200 hover:bg-white/[0.07] hover:text-white",
      },
      size: {
        default: "h-11 px-5",
        lg: "h-13 px-7 text-base",
        sm: "h-9 px-4",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export function Button({ className, variant, size, ...props }: ButtonProps) {
  return (
    <button
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  );
}



