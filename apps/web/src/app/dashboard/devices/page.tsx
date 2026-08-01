"use client";

import { useEffect, useState } from "react";
import { Monitor, RefreshCw, ShieldAlert, ShieldCheck, Smartphone, Tablet } from "lucide-react";

type DeviceSession = {
  token: string;
  ip_address: string;
  browser: string;
  os: string;
  device_type: "desktop" | "mobile" | "tablet" | string;
  device_name: string;
  login_at: string;
  logout_at?: string | null;
  last_active_at: string;
  is_current: boolean;
  is_active: boolean;
};

const DEVICE_ICON: Record<string, React.ReactNode> = {
  desktop: <Monitor className="h-5 w-5" />,
  mobile: <Smartphone className="h-5 w-5" />,
  tablet: <Tablet className="h-5 w-5" />,
};

export default function DevicesPage() {
  const [devices, setDevices] = useState<DeviceSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadDevices() {
    setLoading(true);
    setError("");
    try {
      const response = await fetch("/api/devices", { credentials: "include" });
      if (!response.ok) throw new Error("Qurilmalar ro'yxatini olishda xatolik.");
      const payload = await response.json();
      setDevices(Array.isArray(payload.devices) ? payload.devices : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Noma'lum xatolik.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDevices();
  }, []);

  async function revoke(device: DeviceSession) {
    const prefix = device.token.replace("...", "");
    const response = await fetch(`/api/auth/sessions/${encodeURIComponent(prefix)}/logout`, {
      method: "POST",
      credentials: "include",
    });
    if (response.ok) {
      await loadDevices();
    }
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-4 lg:p-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="mb-1 text-[10px] font-bold uppercase tracking-widest text-cyan-400">Dashboard / Qurilmalar</p>
          <h1 className="text-2xl font-black tracking-tight theme-text-primary sm:text-3xl">Qurilmalar</h1>
          <p className="mt-2 max-w-lg text-sm theme-text-secondary">
            Login qilingan browser, OS, IP manzil va sessiya holati real bazaga saqlanadi.
          </p>
        </div>
        <button onClick={loadDevices} className="btn btn-ghost h-10 justify-center">
          <RefreshCw className="h-4 w-4" />
          Yangilash
        </button>
      </div>

      {loading ? (
        <div className="card grid min-h-60 place-items-center p-8">
          <div className="text-center">
            <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent" />
            <p className="text-sm font-bold theme-text-secondary">Qurilmalar yuklanmoqda...</p>
          </div>
        </div>
      ) : error ? (
        <div className="card p-8 text-center text-sm font-bold text-red-400">{error}</div>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {devices.map((dev) => {
            const Icon = DEVICE_ICON[dev.device_type] ?? DEVICE_ICON.desktop;
            return (
              <div key={`${dev.token}-${dev.login_at}`} className="card flex flex-col gap-4 p-5 transition-all duration-300 hover:border-cyan-500/30 hover:shadow-[0_0_20px_rgba(0,229,255,0.08)]">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${dev.is_active ? "bg-green-500/10 text-green-400" : "bg-white/5 theme-text-secondary"}`}>
                      {Icon}
                    </div>
                    <div>
                      <h3 className="text-sm font-bold theme-text-primary">{dev.device_name || `${dev.browser} on ${dev.os}`}</h3>
                      <p className="mt-0.5 text-[10px] font-bold uppercase tracking-widest theme-text-muted">{dev.device_type}</p>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-1.5">
                    {dev.is_current ? (
                      <span className="rounded-full border border-cyan-500/20 bg-cyan-500/10 px-2 py-0.5 text-[9px] font-bold uppercase tracking-widest text-cyan-400">
                        Joriy
                      </span>
                    ) : null}
                    {dev.is_active ? (
                      <span className="flex items-center gap-1.5 rounded-full border border-green-500/20 bg-green-500/10 px-2 py-0.5 text-[9px] font-bold uppercase tracking-widest text-green-500">
                        <span className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" /> Aktiv
                      </span>
                    ) : (
                      <span className="rounded-full border theme-border bg-white/5 px-2 py-0.5 text-[9px] font-bold uppercase tracking-widest theme-text-muted">
                        Chiqilgan
                      </span>
                    )}
                  </div>
                </div>

                <div className="space-y-2 py-2">
                  {[
                    ["Browser", dev.browser],
                    ["OS", dev.os],
                    ["IP manzil", dev.ip_address || "Noma'lum"],
                    ["Kirish", formatDate(dev.login_at)],
                    ["Oxirgi aktiv", formatDate(dev.last_active_at)],
                    ["Chiqish", dev.logout_at ? formatDate(dev.logout_at) : "Aktiv sessiya"],
                  ].map(([k, v]) => (
                    <div key={k} className="flex justify-between gap-3 text-xs">
                      <span className="theme-text-muted">{k}</span>
                      <span className="text-right font-medium theme-text-secondary">{v}</span>
                    </div>
                  ))}
                </div>

                <div className={`flex items-center gap-2 rounded-lg border p-2.5 text-xs font-bold ${dev.is_active ? "border-green-500/10 bg-green-500/5 text-green-500" : "border-amber-500/10 bg-amber-500/5 text-amber-500"}`}>
                  {dev.is_active ? <ShieldCheck className="h-4 w-4" /> : <ShieldAlert className="h-4 w-4" />}
                  {dev.is_active ? "Faol sessiya" : "Yopilgan sessiya"}
                </div>

                {dev.is_active && !dev.is_current ? (
                  <button
                    className="mt-2 w-full rounded-lg border border-red-500/20 bg-red-500/10 py-2 text-xs font-bold text-red-500 transition-colors hover:bg-red-500/20"
                    onClick={() => revoke(dev)}
                  >
                    Sessiyani tugatish
                  </button>
                ) : null}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function formatDate(value?: string | null) {
  if (!value) return "Noma'lum";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString("uz-UZ");
}



