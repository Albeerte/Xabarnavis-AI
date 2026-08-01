"use client";

import { useState } from "react";
import Sidebar from "@/components/Sidebar";
import Topbar from "@/components/Topbar";
import { ThemeProvider } from "@/components/ThemeProvider";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <ThemeProvider>
      <div className="flex h-screen overflow-hidden theme-bg transition-colors">
        <Sidebar mobileOpen={mobileOpen} onClose={() => setMobileOpen(false)} />
        <div className="flex-1 overflow-y-auto flex flex-col min-w-0">
          <Topbar onMenuOpen={() => setMobileOpen(true)} />
          <main className="flex-1 pb-10">
            {children}
          </main>
        </div>
      </div>
    </ThemeProvider>
  );
}



