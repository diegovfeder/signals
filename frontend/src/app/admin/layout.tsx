import type { ReactNode } from "react";

export default function AdminLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-black text-white">
      <main className="pt-10 pb-16 px-4">
        <div className="container-app">{children}</div>
      </main>
    </div>
  );
}
