"use client";

import { useEffect, useState } from "react";
import { CheckCircle, Monitor, ShieldAlert, XCircle } from "lucide-react";

type SessionLog = {
  token: string;
  ip_address: string;
  browser: string;
  os: string;
  device_type: string;
  device_name: string;
  login_at: string;
  logout_at?: string | null;
  last_active_at: string;
  is_current: boolean;
  is_active: boolean;
};

export default function LoginHistoryPage() {
  const [logs, setLogs] = useState<SessionLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const response = await fetch("/api/login-history", { credentials: "include" });
        if (!response.ok) throw new Error("Kirish tarixini olishda xatolik.");
        const payload = await response.json();
        if (!cancelled) setLogs(Array.isArray(payload.sessions) ? payload.sessions : []);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Noma'lum xatolik.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-4 lg:p-6">
      <div>
        <p className="mb-1 text-[10px] font-bold uppercase tracking-widest text-cyan-400">Dashboard / Kirish tarixi</p>
        <h1 className="text-2xl font-black tracking-tight theme-text-primary sm:text-3xl">Kirish tarixi</h1>
        <p className="mt-2 max-w-lg text-sm theme-text-secondary">
          Hisobingizga qilingan login/logout hodisalari, browser, OS va IP manzil auditi.
        </p>
      </div>

      <div className="card overflow-hidden">
        {loading ? (
          <div className="grid min-h-60 place-items-center p-8">
            <div className="text-center">
              <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent" />
              <p className="text-sm font-bold theme-text-secondary">Kirish tarixi yuklanmoqda...</p>
            </div>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-sm font-bold text-red-400">{error}</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="pro-table">
              <thead>
                <tr>
                  <th>Qurilma</th>
                  <th>Browser / OS</th>
                  <th>IP Manzil</th>
                  <th>Kirish vaqti</th>
                  <th>Chiqish vaqti</th>
                  <th>Oxirgi aktiv</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={`${log.token}-${log.login_at}`}>
                    <td>
                      <div className="flex items-center gap-3">
                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border bg-white/5 theme-border">
                          <Monitor className="h-4 w-4 theme-text-secondary" />
                        </div>
                        <div>
                          <span className="text-xs font-bold theme-text-primary">{log.device_name || log.device_type}</span>
                          {log.is_current ? <p className="mt-0.5 text-[10px] font-bold text-cyan-400">Joriy sessiya</p> : null}
                        </div>
                      </div>
                    </td>
                    <td>
                      <p className="text-xs font-semibold theme-text-secondary">{log.browser}</p>
                      <p className="mt-0.5 text-[10px] theme-text-muted">{log.os}</p>
                    </td>
                    <td>
                      <span className="rounded border bg-white/5 px-2 py-1 font-mono text-xs font-medium theme-border theme-text-secondary">
                        {log.ip_address || "Noma'lum"}
                      </span>
                    </td>
                    <td>
                      <span className="font-mono text-xs theme-text-primary">{formatDate(log.login_at)}</span>
                    </td>
                    <td>
                      {log.logout_at ? (
                        <span className="font-mono text-xs theme-text-muted">{formatDate(log.logout_at)}</span>
                      ) : (
                        <span className="flex items-center gap-1.5 text-xs font-bold text-green-500">
                          <span className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" /> Aktiv
                        </span>
                      )}
                    </td>
                    <td>
                      <span className="font-mono text-xs theme-text-muted">{formatDate(log.last_active_at)}</span>
                    </td>
                    <td>
                      {log.is_active ? (
                        <span className="inline-flex items-center gap-1.5 rounded-md border border-green-400/20 bg-green-400/10 px-2 py-1 text-[10px] font-bold uppercase tracking-widest text-green-400">
                          <CheckCircle className="h-3.5 w-3.5" /> Muvaffaqiyatli
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 rounded-md border border-slate-400/20 bg-slate-400/10 px-2 py-1 text-[10px] font-bold uppercase tracking-widest theme-text-muted">
                          <XCircle className="h-3.5 w-3.5" /> Yakunlangan
                        </span>
                      )}
                      {!log.is_active && !log.logout_at ? (
                        <span className="ml-2 inline-flex items-center gap-1.5 rounded-md border border-amber-500/20 bg-amber-500/10 px-2 py-1 text-[10px] font-bold uppercase tracking-widest text-amber-500">
                          <ShieldAlert className="h-3.5 w-3.5" /> Muddati o'tgan
                        </span>
                      ) : null}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function formatDate(value?: string | null) {
  if (!value) return "Noma'lum";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString("uz-UZ");
}



