// src/components/ui/instructionsCard.tsx
import * as React from "react";
import { cn } from "@/lib/utils";

const InstructionsCard = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "rounded-lg border-2 border-dashed border-gray-300 bg-card text-card-foreground shadow-sm",
      className
    )}
    {...props}
  />
));
InstructionsCard.displayName = "InstructionsCard";

const InstructionsCardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 p-6", className)}
    {...props}
  />
));
InstructionsCardHeader.displayName = "InstructionsCardHeader";

const InstructionsCardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "text-2xl font-semibold leading-none tracking-tight",
      className
    )}
    {...props}
  />
));
InstructionsCardTitle.displayName = "InstructionsCardTitle";

const InstructionsCardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
));
InstructionsCardDescription.displayName = "InstructionsCardDescription";

const InstructionsCardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
));
InstructionsCardContent.displayName = "InstructionsCardContent";

const InstructionsCardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-6 pt-0", className)}
    {...props}
  />
));
InstructionsCardFooter.displayName = "InstructionsCardFooter";

export {
  InstructionsCard,
  InstructionsCardHeader,
  InstructionsCardFooter,
  InstructionsCardTitle,
  InstructionsCardDescription,
  InstructionsCardContent,
};
