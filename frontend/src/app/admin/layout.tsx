import type { ReactNode } from "react";
import Link from "next/link";
import AppHeader from "@/components/layout/AppHeader";

const ADMIN_NAV = [
  { href: "/admin/backtests", label: "Backtests" },
  { href: "/admin/subscribers", label: "Subscribers" },
  { href: "/signals", label: "Signals" },
];

export default function AdminLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-black text-white">
      <main className="pt-10 pb-16 px-4">
        <div className="container-app">{children}</div>
      </main>
    </div>
  );
}
