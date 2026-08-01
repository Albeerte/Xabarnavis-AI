"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  Bot,
  CheckCircle,
  Clock,
  Database,
  Eye,
  FileBarChart2,
  FileText,
  ImageIcon,
  Mic,
  QrCode,
  Shield,
  TrendingUp,
  Upload,
  Video,
} from "lucide-react";

type ApiStats = {
  total_cases: number;
  flagged_cases: number;
  avg_real_score: number;
};

type ApiUser = {
  username?: string;
  first_name?: string;
  last_name?: string;
  email?: string;
  organization?: string;
};

type CaseSummary = {
  id: number;
  original_filename: string;
  file_hash: string;
  status: string;
  media_type?: string;
  uploaded_at: string;
  real_score?: number | null;
  ai_score?: number | null;
  manipulated_score?: number | null;
  final_verdict?: string | null;
  confidence?: string | null;
  report_path?: string | null;
  model_version?: string | null;
};

const copy = {
  uz: {
    eyebrow: "Markaziy tizim",
    title: "Tahlil boshqaruv paneli",
    subtitle: "Hisobingizga bog'langan real analizlar, xavf ko'rsatkichlari va so'nggi forensic hisobotlar.",
    newAnalysis: "Yangi tahlil yaratish",
    total: "Jami tahlillar",
    flagged: "Xavfli topildi",
    authentic: "Haqiqiylik",
    aiAverage: "AI o'rtacha",
    exports: "Hisobotlar",
    weekly: "So'nggi 7 kun faolligi",
    weeklySub: "Bazaga yozilgan analizlar sanasi bo'yicha",
    typeTitle: "Media turlari",
    typeSub: "Image, audio, video va text taqsimoti",
    modules: "Forensic modullar",
    recent: "So'nggi tahlillar",
    recentSub: "Bazadan olingan oxirgi forensic xulosalar",
    all: "Barchasini ko'rish",
    empty: "Hali analiz yo'q. Birinchi faylni yuklab, hisobot yarating.",
    source: "Real API ma'lumotlari",
  },
  en: {
    eyebrow: "Central system",
    title: "Analysis dashboard",
    subtitle: "Real analyses linked to your account, risk indicators, and the latest forensic reports.",
    newAnalysis: "Create new analysis",
    total: "Total analyses",
    flagged: "Flagged cases",
    authentic: "Authenticity",
    aiAverage: "Average AI",
    exports: "Reports",
    weekly: "Last 7 days activity",
    weeklySub: "Analyses stored in the database by date",
    typeTitle: "Media types",
    typeSub: "Image, audio, video, and text distribution",
    modules: "Forensic modules",
    recent: "Latest analyses",
    recentSub: "Most recent forensic conclusions from the database",
    all: "View all",
    empty: "No analyses yet. Upload the first file and generate a report.",
    source: "Real API data",
  },
  ru: {
    eyebrow: "Ð¦ÐµÐ½Ñ‚Ñ€Ð°Ð»ÑŒÐ½Ð°Ñ ÑÐ¸ÑÑ‚ÐµÐ¼Ð°",
    title: "ÐŸÐ°Ð½ÐµÐ»ÑŒ Ð°Ð½Ð°Ð»Ð¸Ð·Ð°",
    subtitle: "Ð ÐµÐ°Ð»ÑŒÐ½Ñ‹Ðµ Ð°Ð½Ð°Ð»Ð¸Ð·Ñ‹ Ð²Ð°ÑˆÐµÐ³Ð¾ Ð°ÐºÐºÐ°ÑƒÐ½Ñ‚Ð°, Ð¿Ð¾ÐºÐ°Ð·Ð°Ñ‚ÐµÐ»Ð¸ Ñ€Ð¸ÑÐºÐ° Ð¸ Ð¿Ð¾ÑÐ»ÐµÐ´Ð½Ð¸Ðµ forensic Ð¾Ñ‚Ñ‡Ñ‘Ñ‚Ñ‹.",
    newAnalysis: "Ð¡Ð¾Ð·Ð´Ð°Ñ‚ÑŒ Ð°Ð½Ð°Ð»Ð¸Ð·",
    total: "Ð’ÑÐµÐ³Ð¾ Ð°Ð½Ð°Ð»Ð¸Ð·Ð¾Ð²",
    flagged: "ÐžÐ¿Ð°ÑÐ½Ñ‹Ñ… Ð½Ð°Ð¹Ð´ÐµÐ½Ð¾",
    authentic: "ÐŸÐ¾Ð´Ð»Ð¸Ð½Ð½Ð¾ÑÑ‚ÑŒ",
    aiAverage: "Ð¡Ñ€ÐµÐ´Ð½Ð¸Ð¹ AI",
    exports: "ÐžÑ‚Ñ‡Ñ‘Ñ‚Ñ‹",
    weekly: "ÐÐºÑ‚Ð¸Ð²Ð½Ð¾ÑÑ‚ÑŒ Ð·Ð° 7 Ð´Ð½ÐµÐ¹",
    weeklySub: "ÐÐ½Ð°Ð»Ð¸Ð·Ñ‹ Ð¸Ð· Ð±Ð°Ð·Ñ‹ Ð¿Ð¾ Ð´Ð°Ñ‚Ð°Ð¼",
    typeTitle: "Ð¢Ð¸Ð¿Ñ‹ Ð¼ÐµÐ´Ð¸Ð°",
    typeSub: "Ð Ð°ÑÐ¿Ñ€ÐµÐ´ÐµÐ»ÐµÐ½Ð¸Ðµ image, audio, video Ð¸ text",
    modules: "Forensic Ð¼Ð¾Ð´ÑƒÐ»Ð¸",
    recent: "ÐŸÐ¾ÑÐ»ÐµÐ´Ð½Ð¸Ðµ Ð°Ð½Ð°Ð»Ð¸Ð·Ñ‹",
    recentSub: "ÐŸÐ¾ÑÐ»ÐµÐ´Ð½Ð¸Ðµ forensic Ð²Ñ‹Ð²Ð¾Ð´Ñ‹ Ð¸Ð· Ð±Ð°Ð·Ñ‹ Ð´Ð°Ð½Ð½Ñ‹Ñ…",
    all: "ÐŸÐ¾ÐºÐ°Ð·Ð°Ñ‚ÑŒ Ð²ÑÐµ",
    empty: "ÐÐ½Ð°Ð»Ð¸Ð·Ð¾Ð² Ð¿Ð¾ÐºÐ° Ð½ÐµÑ‚. Ð—Ð°Ð³Ñ€ÑƒÐ·Ð¸Ñ‚Ðµ Ð¿ÐµÑ€Ð²Ñ‹Ð¹ Ñ„Ð°Ð¹Ð» Ð¸ ÑÐ¾Ð·Ð´Ð°Ð¹Ñ‚Ðµ Ð¾Ñ‚Ñ‡Ñ‘Ñ‚.",
    source: "Ð ÐµÐ°Ð»ÑŒÐ½Ñ‹Ðµ API Ð´Ð°Ð½Ð½Ñ‹Ðµ",
  },
};

const analyzerLabels = {
  uz: [
    ["Rasm tahlili", "JONLI", "AI-rasm, EXIF, ELA, heatmap va yuz forensic nazorati"],
    ["Video tahlili", "JONLI", "Deepfake frame-by-frame tahlili va vaqt izchilligi"],
    ["Audio tahlili", "JONLI", "Ovoz klonlash, spektral artifact va speaker ID"],
    ["Matn tahlili", "JONLI", "AI model tomonidan yozilganlik va manba tekshiruvi"],
  ],
  en: [
    ["Image analysis", "LIVE", "AI image, EXIF, ELA, heatmap, and visual forensics"],
    ["Video analysis", "LIVE", "Deepfake frame-by-frame analysis and timeline consistency"],
    ["Audio analysis", "LIVE", "Voice cloning, spectral artifacts, and speaker consistency"],
    ["Text analysis", "LIVE", "AI writing, misinformation, and source credibility signals"],
  ],
  ru: [
    ["ÐÐ½Ð°Ð»Ð¸Ð· Ð¸Ð·Ð¾Ð±Ñ€Ð°Ð¶ÐµÐ½Ð¸Ð¹", "ÐÐšÐ¢Ð˜Ð’ÐÐž", "AI image, EXIF, ELA, heatmap Ð¸ Ð²Ð¸Ð·ÑƒÐ°Ð»ÑŒÐ½Ð°Ñ ÑÐºÑÐ¿ÐµÑ€Ñ‚Ð¸Ð·Ð°"],
    ["Ð’Ð¸Ð´ÐµÐ¾ Ð°Ð½Ð°Ð»Ð¸Ð·", "ÐÐšÐ¢Ð˜Ð’ÐÐž", "Deepfake Ð°Ð½Ð°Ð»Ð¸Ð· Ð¿Ð¾ ÐºÐ°Ð´Ñ€Ð°Ð¼ Ð¸ Ð²Ñ€ÐµÐ¼ÐµÐ½Ð½Ð°Ñ ÑÐ¾Ð³Ð»Ð°ÑÐ¾Ð²Ð°Ð½Ð½Ð¾ÑÑ‚ÑŒ"],
    ["ÐÑƒÐ´Ð¸Ð¾ Ð°Ð½Ð°Ð»Ð¸Ð·", "ÐÐšÐ¢Ð˜Ð’ÐÐž", "ÐšÐ»Ð¾Ð½Ð¸Ñ€Ð¾Ð²Ð°Ð½Ð¸Ðµ Ð³Ð¾Ð»Ð¾ÑÐ°, ÑÐ¿ÐµÐºÑ‚Ñ€Ð°Ð»ÑŒÐ½Ñ‹Ðµ Ð°Ñ€Ñ‚ÐµÑ„Ð°ÐºÑ‚Ñ‹ Ð¸ speaker consistency"],
    ["Ð¢ÐµÐºÑÑ‚Ð¾Ð²Ñ‹Ð¹ Ð°Ð½Ð°Ð»Ð¸Ð·", "ÐÐšÐ¢Ð˜Ð’ÐÐž", "AI-Ñ‚ÐµÐºÑÑ‚, Ð´ÐµÐ·Ð¸Ð½Ñ„Ð¾Ñ€Ð¼Ð°Ñ†Ð¸Ñ Ð¸ ÑÐ¸Ð³Ð½Ð°Ð»Ñ‹ Ð´Ð¾Ð²ÐµÑ€Ð¸Ñ Ð¸ÑÑ‚Ð¾Ñ‡Ð½Ð¸ÐºÐ°"],
  ],
};

function localeFromPath(pathname: string) {
  const first = pathname.split("/").filter(Boolean)[0];
  return first === "en" || first === "ru" || first === "uz" ? first : "uz";
}

function stripLocalePath(pathname: string) {
  const parts = pathname.split("/").filter(Boolean);
  if (parts[0] === "en" || parts[0] === "ru" || parts[0] === "uz") {
    return `/${parts.slice(1).join("/")}`;
  }
  return pathname;
}

function percent(value?: number | null) {
  return Math.round(Math.max(0, Math.min(1, value ?? 0)) * 100);
}

function riskForCase(item: CaseSummary) {
  const ai = percent(item.ai_score);
  const manipulated = percent(item.manipulated_score);
  const max = Math.max(ai, manipulated);
  if (max >= 75) return { label: "CRITICAL", className: "bg-red-500/15 text-red-500 border-red-500/30" };
  if (max >= 55) return { label: "HIGH", className: "bg-orange-500/15 text-orange-500 border-orange-500/30" };
  if (max >= 35) return { label: "MEDIUM", className: "bg-amber-500/15 text-amber-500 border-amber-500/30" };
  return { label: "LOW", className: "bg-green-500/15 text-green-500 border-green-500/30" };
}

function mediaIcon(type?: string | null) {
  if (type === "video") return Video;
  if (type === "audio") return Mic;
  if (type === "text") return FileText;
  return ImageIcon;
}

function BarChart({ data }: { data: { label: string; count: number }[] }) {
  const max = Math.max(1, ...data.map((d) => d.count));
  return (
    <div className="mt-4 flex h-28 items-end gap-2">
      {data.map((d) => (
        <div key={d.label} className="group flex flex-1 flex-col items-center gap-1">
          <div
            className="relative w-full rounded-md bg-[var(--accent-cyan)]/25 transition-all duration-300 hover:bg-[var(--accent-cyan)]/70"
            style={{ height: `${Math.max((d.count / max) * 100, d.count ? 12 : 6)}%` }}
          >
            <span className="absolute -top-7 left-1/2 -translate-x-1/2 rounded bg-[var(--accent-cyan)] px-1.5 py-0.5 text-[10px] font-bold text-[#07111f] opacity-0 transition-opacity group-hover:opacity-100">
              {d.count}
            </span>
          </div>
          <span className="text-[9px] font-bold uppercase tracking-wider theme-text-muted">{d.label}</span>
        </div>
      ))}
    </div>
  );
}

function Donut({ data }: { data: { label: string; count: number; color: string }[] }) {
  const total = data.reduce((sum, item) => sum + item.count, 0);
  let offset = 0;
  const r = 34;
  const circ = 2 * Math.PI * r;

  return (
    <div className="mt-4 flex items-center gap-6">
      <div className="relative h-[84px] w-[84px] shrink-0">
        <svg width="84" height="84" className="-rotate-90">
          {total === 0 ? (
            <circle cx="42" cy="42" r={r} fill="none" stroke="rgba(148,163,184,0.25)" strokeWidth="8" />
          ) : (
            data.map((item) => {
              const pct = item.count / total;
              const dash = pct * circ;
              const circle = (
                <circle
                  key={item.label}
                  cx="42"
                  cy="42"
                  r={r}
                  fill="none"
                  stroke={item.color}
                  strokeDasharray={`${dash} ${circ - dash}`}
                  strokeDashoffset={-(offset * circ)}
                  strokeLinecap="round"
                  strokeWidth="8"
                />
              );
              offset += pct;
              return circle;
            })
          )}
        </svg>
        <div className="absolute inset-0 flex items-center justify-center text-lg font-black theme-text-primary">{total}</div>
      </div>
      <div className="flex flex-1 flex-col gap-2.5">
        {data.map((item) => (
          <div key={item.label} className="flex items-center gap-2 text-xs">
            <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ backgroundColor: item.color }} />
            <span className="flex-1 font-medium theme-text-secondary">{item.label}</span>
            <span className="font-bold tabular-nums theme-text-primary">{item.count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color }: { icon: typeof Shield; label: string; value: string | number; color: string }) {
  return (
    <div className="card p-5 transition-all hover:border-[var(--accent-cyan)]/30 hover:shadow-[0_0_20px_rgba(0,229,255,0.1)]">
      <div className="mb-4 flex items-start justify-between">
        <p className="text-xs font-bold uppercase tracking-wider theme-text-muted">{label}</p>
        <div className="flex h-8 w-8 items-center justify-center rounded-lg" style={{ backgroundColor: `${color}18`, color }}>
          <Icon className="h-4 w-4" />
        </div>
      </div>
      <p className="text-3xl font-black tracking-tight theme-text-primary">{value}</p>
    </div>
  );
}

export default function DashboardPage() {
  const router = useRouter();
  const pathname = usePathname();
  const locale = localeFromPath(pathname);
  const prefix = locale === "uz" ? "" : `/${locale}`;
  const t = copy[locale];
  const [stats, setStats] = useState<ApiStats | null>(null);
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [user, setUser] = useState<ApiUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadDashboard() {
      setLoading(true);
      try {
        const [statsResponse, casesResponse, userResponse] = await Promise.all([
          fetch("/api/stats", { credentials: "include" }),
          fetch("/api/cases?limit=50", { credentials: "include" }),
          fetch("/api/auth/me", { credentials: "include" }),
        ]);

        if (cancelled) return;

        if (statsResponse.ok) setStats(await statsResponse.json());
        if (casesResponse.ok) {
          const payload = await casesResponse.json();
          setCases(Array.isArray(payload.cases) ? payload.cases : []);
        }
        if (userResponse.ok) {
          const payload = await userResponse.json();
          setUser(payload.user ?? null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadDashboard();
    return () => {
      cancelled = true;
    };
  }, []);

  const weeklyData = useMemo(() => {
    const weekdayLabels = {
      uz: ["Du", "Se", "Cho", "Pa", "Ju", "Sha", "Ya"],
      en: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
      ru: ["ÐŸÐ½", "Ð’Ñ‚", "Ð¡Ñ€", "Ð§Ñ‚", "ÐŸÑ‚", "Ð¡Ð±", "Ð’Ñ"],
    }[locale];
    const days = Array.from({ length: 7 }, (_, index) => {
      const date = new Date();
      date.setDate(date.getDate() - (6 - index));
      const dayIndex = (date.getDay() + 6) % 7;
      return {
        key: date.toISOString().slice(0, 10),
        label: weekdayLabels[dayIndex],
        count: 0,
      };
    });
    for (const item of cases) {
      const key = item.uploaded_at?.slice(0, 10);
      const day = days.find((entry) => entry.key === key);
      if (day) day.count += 1;
    }
    return days.map(({ label, count }) => ({ label, count }));
  }, [cases, locale]);

  const typeData = useMemo(() => {
    const counts = { image: 0, video: 0, audio: 0, text: 0 };
    for (const item of cases) {
      const key = (item.media_type || "image") as keyof typeof counts;
      if (key in counts) counts[key] += 1;
    }
    return [
      { label: "Image", count: counts.image, color: "#00E5FF" },
      { label: "Video", count: counts.video, color: "#8B5CF6" },
      { label: "Audio", count: counts.audio, color: "#22C55E" },
      { label: "Text", count: counts.text, color: "#F59E0B" },
    ];
  }, [cases]);

  const total = stats?.total_cases ?? cases.length;
  const flagged = stats?.flagged_cases ?? cases.filter((item) => Math.max(percent(item.ai_score), percent(item.manipulated_score)) >= 55).length;
  const realScore = Math.round((stats?.avg_real_score ?? 0) * 100);
  const avgAi = cases.length ? Math.round(cases.reduce((sum, item) => sum + percent(item.ai_score), 0) / cases.length) : 0;
  const reportCount = cases.filter((item) => item.report_path).length;
  const displayName = [user?.first_name, user?.last_name].filter(Boolean).join(" ") || user?.username || "Xabarnavis user";

  const analyzerLinks = [
    ["/dashboard/image-analyzer", ImageIcon],
    ["/dashboard/video-analyzer", Video],
    ["/dashboard/audio-analyzer", Mic],
    ["/dashboard/text-analyzer", FileText],
  ] as const;

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-4 lg:p-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="mb-1 text-[10px] font-bold uppercase tracking-widest text-cyan-400">{t.eyebrow}</p>
          <h1 className="text-2xl font-black tracking-tight theme-text-primary sm:text-3xl">{t.title}</h1>
          <p className="mt-2 max-w-2xl text-sm theme-text-secondary">
            {t.subtitle}
          </p>
          <div className="mt-3 flex flex-wrap items-center gap-2 text-xs font-bold">
            <span className="rounded-full border border-green-500/20 bg-green-500/10 px-3 py-1 text-green-500">
              <Database className="mr-1 inline h-3.5 w-3.5" />
              {t.source}
            </span>
            <span className="rounded-full border theme-border px-3 py-1 theme-text-secondary">
              {displayName}
            </span>
          </div>
        </div>
        <button
          onClick={() => router.push(`${prefix}/dashboard/image-analyzer`)}
          className="btn-primary flex shrink-0 items-center justify-center gap-2 py-2.5"
        >
          <Upload className="h-4 w-4" />
          {t.newAnalysis}
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-5">
        <StatCard icon={Shield} label={t.total} value={loading ? "..." : total} color="var(--accent-cyan)" />
        <StatCard icon={AlertTriangle} label={t.flagged} value={loading ? "..." : flagged} color="var(--accent-red)" />
        <StatCard icon={TrendingUp} label={t.authentic} value={loading ? "..." : `${realScore}%`} color="var(--accent-green)" />
        <StatCard icon={Bot} label={t.aiAverage} value={loading ? "..." : `${avgAi}%`} color="var(--accent-purple)" />
        <StatCard icon={FileBarChart2} label={t.exports} value={loading ? "..." : reportCount} color="var(--accent-amber)" />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="card flex flex-col p-6 lg:col-span-2">
          <div>
            <h2 className="text-sm font-bold theme-text-primary">{t.weekly}</h2>
            <p className="mt-1 text-xs theme-text-muted">{t.weeklySub}</p>
          </div>
          <div className="flex flex-1 flex-col justify-end">
            <BarChart data={weeklyData} />
          </div>
        </div>

        <div className="card p-6">
          <div>
            <h2 className="text-sm font-bold theme-text-primary">{t.typeTitle}</h2>
            <p className="mt-1 text-xs theme-text-muted">{t.typeSub}</p>
          </div>
          <Donut data={typeData} />
        </div>
      </div>

      <div>
        <h2 className="mb-4 text-sm font-bold uppercase tracking-wider theme-text-muted">{t.modules}</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {analyzerLabels[locale].map(([title, badge, desc], index) => {
            const [href, Icon] = analyzerLinks[index];
            return (
              <Link
                key={href}
                href={`${prefix}${href}`}
                className="card group flex flex-col p-5 transition-all hover:border-cyan-500/30 hover:shadow-[0_0_20px_rgba(0,229,255,0.08)]"
              >
                <div className="mb-4 flex items-start justify-between">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl border theme-border bg-white/5 transition-all group-hover:border-cyan-500/30 group-hover:bg-cyan-500/10">
                    <Icon className="h-5 w-5 theme-text-secondary transition-colors group-hover:text-cyan-400" />
                  </div>
                  <span className="rounded-md border border-green-400/30 bg-green-400/10 px-2 py-1 text-[9px] font-black tracking-widest text-green-400">
                    {badge}
                  </span>
                </div>
                <h3 className="mb-2 text-sm font-bold theme-text-primary transition-colors group-hover:text-cyan-400">{title}</h3>
                <p className="mb-4 text-xs leading-relaxed theme-text-muted">{desc}</p>
                <div className="mt-auto flex items-center gap-2 text-xs font-bold text-cyan-500 transition-transform group-hover:translate-x-1">
                  Open <ArrowRight className="h-3.5 w-3.5" />
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      <div className="card overflow-hidden">
        <div className="flex flex-col justify-between gap-4 border-b p-5 theme-border sm:flex-row sm:items-center">
          <div>
            <h2 className="text-sm font-bold theme-text-primary">{t.recent}</h2>
            <p className="mt-1 text-xs theme-text-muted">{t.recentSub}</p>
          </div>
          <Link href={`${prefix}/dashboard/reports`} className="flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-bold text-cyan-500 transition-colors hover:bg-cyan-500/10 hover:text-cyan-400">
            {t.all} <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>

        {cases.length === 0 ? (
          <div className="p-10 text-center">
            <Clock className="mx-auto h-10 w-10 theme-text-muted" />
            <p className="mt-4 text-sm font-semibold theme-text-secondary">{loading ? "Loading..." : t.empty}</p>
            <Link href={`${prefix}/dashboard/image-analyzer`} className="btn btn-cyan mt-5 inline-flex">
              {t.newAnalysis}
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="pro-table">
              <thead>
                <tr>
                  <th>File & ID</th>
                  <th>Type</th>
                  <th>Verdict</th>
                  <th>AI %</th>
                  <th>Manipulation</th>
                  <th>Risk</th>
                  <th>Date</th>
                  <th className="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {cases.slice(0, 8).map((item) => {
                  const Icon = mediaIcon(item.media_type);
                  const risk = riskForCase(item);
                  const ai = percent(item.ai_score);
                  const manipulation = percent(item.manipulated_score);
                  const reportHref = `${prefix}/dashboard/reports/${item.id}`;
                  const publicHref = `${prefix}/report/${item.id}`;
                  return (
                    <tr key={item.id}>
                      <td>
                        <div className="flex items-center gap-3">
                          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border bg-white/5 theme-border">
                            <Icon className="h-4 w-4 text-cyan-400" />
                          </div>
                          <div>
                            <p className="max-w-[190px] truncate text-xs font-bold theme-text-primary">{item.original_filename}</p>
                            <p className="mt-0.5 text-[10px] font-mono theme-text-muted">CASE-{item.id}</p>
                          </div>
                        </div>
                      </td>
                      <td>
                        <span className="text-[10px] font-black uppercase tracking-widest theme-text-muted">{item.media_type || "image"}</span>
                      </td>
                      <td>
                        <div className="flex items-center gap-1.5">
                          {ai >= 55 || manipulation >= 55 ? (
                            <AlertTriangle className="h-3.5 w-3.5 text-red-500" />
                          ) : (
                            <CheckCircle className="h-3.5 w-3.5 text-green-500" />
                          )}
                          <span className="text-xs font-semibold theme-text-secondary">{item.final_verdict || item.status}</span>
                        </div>
                      </td>
                      <td>
                        <span className={`text-xs font-black ${ai >= 70 ? "text-red-500" : ai >= 40 ? "text-amber-500" : "text-green-500"}`}>
                          {ai}%
                        </span>
                      </td>
                      <td>
                        <span className={`text-xs font-black ${manipulation >= 70 ? "text-red-500" : manipulation >= 40 ? "text-amber-500" : "text-green-500"}`}>
                          {manipulation}%
                        </span>
                      </td>
                      <td>
                        <span className={`rounded-md border px-2 py-1 text-[10px] font-bold tracking-wider ${risk.className}`}>
                          {risk.label}
                        </span>
                      </td>
                      <td className="text-xs font-mono theme-text-muted">{item.uploaded_at?.slice(0, 10)}</td>
                      <td>
                        <div className="flex items-center justify-end gap-2">
                          <Link href={reportHref} className="rounded-lg p-1.5 theme-text-muted transition-colors hover:bg-cyan-500/10 hover:text-cyan-400" title="Open report">
                            <Eye className="h-4 w-4" />
                          </Link>
                          <Link href={publicHref} className="rounded-lg p-1.5 theme-text-muted transition-colors hover:bg-amber-500/10 hover:text-amber-400" title="Public report">
                            <QrCode className="h-4 w-4" />
                          </Link>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}



