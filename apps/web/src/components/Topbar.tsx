"use client";

import { useTheme } from "./ThemeProvider";
import { Sun, Moon, Bell, LogOut, Menu } from "lucide-react";
import { mockNotifications } from "@/lib/mock-data";
import { useRouter } from "next/navigation";
import { usePathname } from "next/navigation";

interface Props { onMenuOpen: () => void; }

export default function Topbar({ onMenuOpen }: Props) {
  const { theme, toggleTheme } = useTheme();
  const router = useRouter();
  const pathname = usePathname();
  const unread = mockNotifications.filter(n => !n.read).length;
  const first = pathname.split("/").filter(Boolean)[0];
  const prefix = first === "uz" || first === "en" || first === "ru" ? `/${first}` : "";

  async function logout() {
    try {
      await fetch("/api/auth/logout", { method: "POST", credentials: "include" });
    } finally {
      router.push(`${prefix}/login`);
      router.refresh();
    }
  }

  return (
    <header className="h-16 theme-topbar border-b theme-border flex items-center px-4 lg:px-6 gap-4 sticky top-0 z-40 transition-colors">
      {/* Mobile menu */}
      <button 
        className="lg:hidden p-2 -ml-2 rounded-lg theme-text-secondary hover:theme-text-primary hover:bg-white/5 transition-colors" 
        onClick={onMenuOpen}
      >
        <Menu className="h-5 w-5" />
      </button>

      {/* Live status */}
      <div className="hidden md:flex items-center gap-3 flex-1 min-w-0">
        <span className="flex items-center gap-1.5 text-xs font-bold text-green-400 bg-green-500/10 px-2.5 py-1 rounded-full border border-green-500/20">
          <span className="h-1.5 w-1.5 rounded-full bg-green-400 shadow-[0_0_8px_rgba(34,197,94,0.8)] animate-pulse" />
          JONLI
        </span>
        <span className="text-xs font-medium theme-text-muted truncate">
          Ko'p modelli forensic tahlil tizimi faol
        </span>
      </div>

      <div className="flex items-center gap-3 lg:gap-4 ml-auto">
        {/* Minimalist Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="flex items-center justify-center h-9 w-9 rounded-xl border theme-border theme-text-secondary hover:theme-text-primary hover:bg-[var(--accent-cyan)]/10 hover:border-[var(--accent-cyan)]/30 hover:text-[var(--accent-cyan)] transition-all"
          title={theme === "dark" ? "Kun rejimi" : "Tun rejimi"}
        >
          {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </button>

        {/* Notifications */}
        <button
          className="relative flex items-center justify-center h-9 w-9 rounded-xl border theme-border theme-text-secondary hover:theme-text-primary hover:bg-[var(--accent-cyan)]/10 hover:border-[var(--accent-cyan)]/30 hover:text-[var(--accent-cyan)] transition-all"
          onClick={() => router.push(`${prefix}/dashboard/notifications`)}
          title="Bildirishnomalar"
        >
          <Bell className="h-4 w-4" />
          {unread > 0 && (
            <span className="absolute -top-1.5 -right-1.5 h-4 w-4 flex items-center justify-center rounded-full text-[9px] font-bold text-white bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)] border-2 border-[var(--bg-primary)]">
              {unread}
            </span>
          )}
        </button>

        {/* Role badge */}
        <span className="hidden sm:flex items-center gap-1.5 text-xs font-bold px-3 py-1.5 rounded-xl border border-[var(--accent-cyan)]/30 bg-[var(--accent-cyan)]/10 text-[var(--accent-cyan)]">
          Talaba
        </span>

        {/* Logout */}
        <button
          className="flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-bold theme-text-secondary hover:text-red-400 hover:bg-red-500/10 border border-transparent hover:border-red-500/20 transition-all"
          onClick={logout}
          title="Chiqish"
        >
          <LogOut className="h-4 w-4" />
          <span className="hidden sm:inline">Chiqish</span>
        </button>
      </div>
    </header>
  );
}



