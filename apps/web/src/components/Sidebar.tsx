"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, ImageIcon, Video, Mic, FileText,
  FileBarChart2, Monitor, Clock, Bell, Settings,
  UserRound, ChevronLeft, ChevronRight, Shield,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

const NAV = [
  { href: "/dashboard",                    icon: LayoutDashboard, label: "Dashboard" },
  { href: "/dashboard/image-analyzer",     icon: ImageIcon,       label: "Rasm tahlili",  badge: "JONLI", badgeCls: "text-green-400 bg-green-500/10 border-green-500/20" },
  { href: "/dashboard/video-analyzer",     icon: Video,           label: "Video tahlili", badge: "TEZDA", badgeCls: "text-amber-400 bg-amber-500/10 border-amber-500/20" },
  { href: "/dashboard/audio-analyzer",     icon: Mic,             label: "Audio tahlili", badge: "TEZDA", badgeCls: "text-amber-400 bg-amber-500/10 border-amber-500/20" },
  { href: "/dashboard/text-analyzer",      icon: FileText,        label: "Matn tahlili",  badge: "TEZDA", badgeCls: "text-amber-400 bg-amber-500/10 border-amber-500/20" },
  { href: "/dashboard/reports",            icon: FileBarChart2,   label: "Analizlar" },
  { href: "/dashboard/admin",              icon: Shield,          label: "Admin panel" },
  { href: "/dashboard/devices",            icon: Monitor,         label: "Qurilmalar" },
  { href: "/dashboard/login-history",      icon: Clock,           label: "Kirish tarixi" },
  { href: "/dashboard/notifications",      icon: Bell,            label: "Bildirishnomalar" },
  { href: "/dashboard/settings",           icon: Settings,        label: "Sozlamalar" },
  { href: "/dashboard/portfolio",          icon: UserRound,       label: "Profil" },
];

type NavItem = (typeof NAV)[number];

interface Props { mobileOpen: boolean; onClose: () => void; }

function localeInfo(pathname: string) {
  const parts = pathname.split("/").filter(Boolean);
  const locale = parts[0] === "en" || parts[0] === "ru" || parts[0] === "uz" ? parts[0] : "";
  const pathWithoutLocale = locale ? `/${parts.slice(1).join("/")}` : pathname;
  return {
    prefix: locale && locale !== "uz" ? `/${locale}` : "",
    activePath: pathWithoutLocale === "/" ? "/dashboard" : pathWithoutLocale,
  };
}

export default function Sidebar({ mobileOpen, onClose }: Props) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [canSeeAdmin, setCanSeeAdmin] = useState(false);
  const { prefix, activePath } = localeInfo(pathname);

  useEffect(() => {
    let ignore = false;

    async function loadUser() {
      try {
        const response = await fetch("/api/auth/me", { credentials: "include" });
        if (!response.ok) return;
        const payload = await response.json();
        const user = payload.user || {};
        const role = String(user.role || "").toLowerCase();
        const username = String(user.username || "").toLowerCase();
        if (!ignore) setCanSeeAdmin(username === "admin" || role === "admin" || role === "superadmin");
      } catch {
        if (!ignore) setCanSeeAdmin(false);
      }
    }

    loadUser();
    return () => {
      ignore = true;
    };
  }, []);

  const visibleNav = useMemo<NavItem[]>(
    () => NAV.filter((item) => item.href !== "/dashboard/admin" || canSeeAdmin),
    [canSeeAdmin],
  );

  return (
    <>
      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden transition-opacity"
          onClick={onClose}
        />
      )}

      <aside
        className={`theme-sidebar border-r theme-border flex flex-col h-screen fixed lg:relative z-50 transition-all duration-300 ${
          collapsed ? "w-16" : "w-60"
        } ${mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}`}
      >
        {/* Logo */}
        <div className="h-16 flex items-center px-4 border-b theme-border shrink-0 gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center overflow-hidden rounded-xl border theme-border bg-white/[0.04] p-1 shadow-[var(--glow-cyan)]">
            <Image
              src="/xabarnavis-logo.png"
              alt="Xabarnavis AI logo"
              width={40}
              height={40}
              className="h-full w-full object-contain"
              priority
            />
          </div>
          {!collapsed && (
            <div className="overflow-hidden whitespace-nowrap">
              <p className="text-sm font-bold theme-text-primary tracking-wide">Xabarnavis AI</p>
              <p className="text-[9px] font-mono uppercase tracking-widest text-cyan-400">Forensics Engine</p>
            </div>
          )}
          {/* Mobile close */}
          <button onClick={onClose} className="ml-auto lg:hidden theme-text-muted p-1 hover:text-white transition-colors">
            âœ•
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {visibleNav.map((item) => {
            const active = activePath === item.href;
            return (
              <Link
                key={item.href}
                href={`${prefix}${item.href}`}
                onClick={onClose}
                title={item.label}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 border ${
                  active
                    ? "bg-[var(--accent-cyan)]/10 text-[var(--accent-cyan)] border-[var(--accent-cyan)]/20 shadow-sm"
                    : "text-[var(--text-secondary)] border-transparent hover:bg-white/5 hover:theme-text-primary"
                }`}
              >
                <item.icon className={`h-[18px] w-[18px] shrink-0 ${active ? "" : "opacity-70"}`} />
                {!collapsed && (
                  <>
                    <span className="flex-1 truncate">{item.label}</span>
                    {item.badge && (
                      <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded-full border ${item.badgeCls}`}>
                        {item.badge}
                      </span>
                    )}
                  </>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Collapse toggle (desktop only) */}
        <div className="hidden lg:block border-t theme-border p-3 shrink-0">
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="flex items-center justify-center w-full p-2.5 rounded-xl theme-text-secondary hover:bg-white/5 hover:theme-text-primary transition-all border border-transparent"
            title={collapsed ? "Kengaytirish" : "Yig'ish"}
          >
            {collapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <div className="flex items-center gap-2">
                <ChevronLeft className="h-4 w-4" />
                <span className="text-xs font-medium">Yig'ish</span>
              </div>
            )}
          </button>
        </div>
      </aside>
    </>
  );
}



