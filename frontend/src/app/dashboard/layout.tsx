"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import { FileText, LayoutDashboard, LogOut, User as UserIcon } from "lucide-react";
import { useAuthStore } from "@/store/auth-store";
import { useCurrentUser } from "@/lib/hooks";

const NAV_ITEMS = [
  { href: "/dashboard/profile", label: "Profile", icon: UserIcon },
  { href: "/dashboard/resume", label: "Master Resume", icon: FileText },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const accessToken = useAuthStore((s) => s.accessToken);
  const logout = useAuthStore((s) => s.logout);
  const { data: user } = useCurrentUser();

  useEffect(() => {
    if (!accessToken) router.replace("/login");
  }, [accessToken, router]);

  if (!accessToken) return null;

  return (
    <div className="flex min-h-screen bg-ink">
      {/* Sidebar */}
      <aside className="hidden w-64 flex-col border-r border-line bg-panel px-4 py-6 md:flex">
        <div className="mb-8 flex items-center gap-2 px-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/15 text-accent">
            <LayoutDashboard size={16} />
          </div>
          <span className="font-display text-sm font-semibold tracking-wide text-white">CAREER COPILOT</span>
        </div>

        <nav className="flex flex-1 flex-col gap-1">
          {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                  active ? "bg-accent/15 text-accent" : "text-muted hover:bg-panel2 hover:text-white"
                }`}
              >
                <Icon size={16} />
                {label}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-line pt-4">
          <div className="mb-3 px-2">
            <p className="truncate text-sm font-medium text-white">{user?.full_name ?? "…"}</p>
            <p className="truncate text-xs text-muted">{user?.email ?? ""}</p>
          </div>
          <button
            onClick={() => {
              logout();
              router.replace("/login");
            }}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-muted transition-colors hover:bg-panel2 hover:text-danger"
          >
            <LogOut size={16} />
            Log out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 px-6 py-8 sm:px-10">{children}</main>
    </div>
  );
}
