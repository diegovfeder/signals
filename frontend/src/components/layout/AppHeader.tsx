import type { ReactNode } from "react";
import Link from "next/link";

type NavItem = {
  href: string;
  label: string;
};

type AppHeaderProps = {
  navItems?: NavItem[];
  rightSlot?: ReactNode;
  children?: ReactNode;
  className?: string;
  logoLabel?: string;
};

const DEFAULT_NAV: NavItem[] = [{ href: "/admin", label: "Admin" }];

const cn = (...classes: Array<string | false | null | undefined>) =>
  classes.filter(Boolean).join(" ");

export function AppHeader({
  navItems = DEFAULT_NAV,
  rightSlot,
  children,
  className,
  logoLabel = "SIGNALS",
}: AppHeaderProps) {
  return (
    <header
      className={cn(
        "sticky top-0 z-40 border-b border-border/60 bg-background/85 backdrop-blur-xl",
        className,
      )}
    >
      <div className="container-app">
        <div className="hidden sm:flex items-center justify-between gap-6 py-3 md:py-4">
          <Link
            href="/"
            className="text-lg font-black tracking-tight text-foreground hover:text-foreground-secondary transition-colors"
          >
            {logoLabel}
          </Link>

          <nav className="flex-1 flex items-center justify-center gap-5 text-sm text-foreground-muted">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="rounded-full px-3 py-1.5 transition-colors hover:text-foreground hover:bg-white/5 border border-transparent hover:border-white/10"
              >
                {item.label}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-3">{rightSlot}</div>
        </div>

        {/* Mobile condensed header */}
        <div className="flex sm:hidden items-center justify-between py-3">
          <Link
            href="/"
            className="text-lg font-black tracking-tight text-foreground hover:text-foreground-secondary transition-colors"
          >
            {logoLabel}
          </Link>
          <div className="flex items-center gap-2">{rightSlot}</div>
        </div>

        {children && <div className="pb-4">{children}</div>}
      </div>
    </header>
  );
}

export default AppHeader;
