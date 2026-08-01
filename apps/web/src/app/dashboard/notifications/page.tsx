"use client";

import { mockNotifications } from "@/lib/mock-data";
import { useState } from "react";
import { FileBarChart2, AlertTriangle, Monitor, QrCode, Download, Cpu, Check } from "lucide-react";

const ICON: Record<string, React.ReactNode> = {
  report: <FileBarChart2 className="w-5 h-5 text-cyan-400" />,
  danger: <AlertTriangle  className="w-5 h-5 text-red-500" />,
  device: <Monitor        className="w-5 h-5 text-purple-400" />,
  qr:     <QrCode         className="w-5 h-5 text-amber-500" />,
  export: <Download       className="w-5 h-5 text-green-500" />,
  model:  <Cpu            className="w-5 h-5 text-blue-400" />,
};

const ICON_BG: Record<string, string> = {
  report: "bg-cyan-500/10 border-cyan-500/20",
  danger: "bg-red-500/10 border-red-500/20",
  device: "bg-purple-500/10 border-purple-500/20",
  qr:     "bg-amber-500/10 border-amber-500/20",
  export: "bg-green-500/10 border-green-500/20",
  model:  "bg-blue-500/10 border-blue-500/20",
};

export default function NotificationsPage() {
  const [notifs, setNotifs] = useState(mockNotifications);
  const markAllRead = () => setNotifs(n => n.map(x => ({ ...x, read: true })));

  const unread = notifs.filter(n => !n.read);
  const read   = notifs.filter(n =>  n.read);

  return (
    <div className="p-4 lg:p-6 lg:max-w-3xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-widest text-cyan-400 mb-1">Dashboard / Bildirishnomalar</p>
          <h1 className="text-2xl sm:text-3xl font-black theme-text-primary tracking-tight">Mening bildirishnomalarim</h1>
          <p className="text-sm theme-text-secondary mt-2 max-w-lg">
            Hisobingiz, yangi hisobotlar, qurilmalar va xavfsizlik xabarlari shu yerda ko'rinadi. Sizda {unread.length} ta o'qilmagan xabar mavjud.
          </p>
        </div>
        {unread.length > 0 && (
          <button 
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold text-cyan-400 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/20 transition-colors"
            onClick={markAllRead}
          >
            <Check className="w-4 h-4" /> Barchasini o'qilgan deb belgilash
          </button>
        )}
      </div>

      <div className="space-y-6 mt-8">
        {/* Unread */}
        {unread.length > 0 && (
          <div>
            <h3 className="text-[10px] font-bold theme-text-muted uppercase tracking-widest mb-3 px-1">Yangi Bildirishnomalar</h3>
            <div className="space-y-2">
              {unread.map(n => (
                <div key={n.id} className="card p-4 flex items-start gap-4 border-l-2 border-l-cyan-400 hover:border-cyan-500/30 hover:shadow-[0_0_15px_rgba(0,229,255,0.05)] transition-all">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 border ${ICON_BG[n.type]}`}>
                    {ICON[n.type]}
                  </div>
                  <div className="flex-1 min-w-0 pt-0.5">
                    <div className="flex items-start justify-between gap-4">
                      <h4 className="text-sm font-bold theme-text-primary leading-tight">{n.title}</h4>
                      <div className="w-2 h-2 rounded-full bg-cyan-400 shrink-0 shadow-[0_0_8px_rgba(0,229,255,0.6)] mt-1" />
                    </div>
                    <p className="text-xs theme-text-secondary mt-1.5 leading-relaxed">{n.message}</p>
                    <p className="text-[10px] font-bold theme-text-muted mt-2">{n.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Read */}
        {read.length > 0 && (
          <div>
            <h3 className="text-[10px] font-bold theme-text-muted uppercase tracking-widest mb-3 px-1">Avvalgi Bildirishnomalar</h3>
            <div className="space-y-2">
              {read.map(n => (
                <div key={n.id} className="card p-4 flex items-start gap-4 opacity-60 hover:opacity-100 transition-opacity">
                  <div className="w-12 h-12 rounded-xl flex items-center justify-center shrink-0 border border-[var(--border)] bg-white/5">
                    {ICON[n.type]}
                  </div>
                  <div className="flex-1 min-w-0 pt-0.5">
                    <h4 className="text-sm font-semibold theme-text-primary leading-tight">{n.title}</h4>
                    <p className="text-xs theme-text-secondary mt-1.5 leading-relaxed">{n.message}</p>
                    <p className="text-[10px] font-medium theme-text-muted mt-2">{n.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}



