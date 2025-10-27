import type { ReactNode } from "react";
import Link from "next/link";
import AppHeader from "@/components/layout/AppHeader";

const ADMIN_NAV = [
  { href: "/admin/backtests", label: "Backtests" },
  { href: "/admin/subscribers", label: "Subscribers" },
  { href: "/dashboard", label: "Dashboard" },
];

export default function AdminLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-black text-white">
      <AppHeader
        navItems={ADMIN_NAV}
        rightSlot={
          <Link href="/" className="btn-primary text-sm">
            Home
          </Link>
        }
        logoLabel="Signals Admin"
        className="bg-background/85"
      />
      <main className="pt-10 pb-16 px-4">
        <div className="container-app">{children}</div>
      </main>
    </div>
  );
}
