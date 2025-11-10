import { forwardRef } from "react";
import type {
  AnchorHTMLAttributes,
  HTMLAttributes,
  ReactNode,
} from "react";

import { cn } from "@/lib/utils";

type PrimitiveProps<T> = HTMLAttributes<T> & { children?: ReactNode };

type ButtonProps = AnchorHTMLAttributes<HTMLAnchorElement> & {
  className?: string;
  children?: ReactNode;
};

export function Html({ children, ...props }: PrimitiveProps<HTMLDivElement>) {
  return (
    <div data-email-root="true" {...props}>
      {children}
    </div>
  );
}

export function Head({ children, ...props }: PrimitiveProps<HTMLDivElement>) {
  return (
    <div data-email-head="true" {...props}>
      {children}
    </div>
  );
}

export function Body({ children, className, ...props }: PrimitiveProps<HTMLDivElement>) {
  return (
    <div
      className={cn("bg-background text-foreground", className)}
      data-email-body="true"
      {...props}
    >
      {children}
    </div>
  );
}

export function Preview({ children }: { children?: ReactNode }) {
  return <span className="sr-only">{children}</span>;
}

export const Container = forwardRef<HTMLDivElement, PrimitiveProps<HTMLDivElement>>(
  ({ children, className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("mx-auto w-full max-w-xl", className)}
      {...props}
    >
      {children}
    </div>
  ),
);
Container.displayName = "Container";

export const Section = forwardRef<HTMLDivElement, PrimitiveProps<HTMLDivElement>>(
  ({ children, className, ...props }, ref) => (
    <section ref={ref} className={cn(className)} {...props}>
      {children}
    </section>
  ),
);
Section.displayName = "Section";

export const Heading = forwardRef<HTMLHeadingElement, PrimitiveProps<HTMLHeadingElement>>(
  ({ children, className, ...props }, ref) => (
    <h2
      ref={ref}
      className={cn("text-lg font-semibold text-foreground", className)}
      {...props}
    >
      {children}
    </h2>
  ),
);
Heading.displayName = "Heading";

export const Text = forwardRef<HTMLParagraphElement, PrimitiveProps<HTMLParagraphElement>>(
  ({ children, className, ...props }, ref) => (
    <p
      ref={ref}
      className={cn("text-sm leading-6 text-muted-foreground", className)}
      {...props}
    >
      {children}
    </p>
  ),
);
Text.displayName = "Text";

export const Button = forwardRef<HTMLAnchorElement, ButtonProps>(
  ({ children, className, ...props }, ref) => (
    <a
      ref={ref}
      className={cn(
        "inline-flex items-center justify-center rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground no-underline",
        className,
      )}
      {...props}
    >
      {children}
    </a>
  ),
);
Button.displayName = "Button";
