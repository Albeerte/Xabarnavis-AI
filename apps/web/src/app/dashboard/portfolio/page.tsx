"use client";

import { type ChangeEvent, type FormEvent, useEffect, useMemo, useState } from "react";
import {
  BadgeCheck,
  Building2,
  Camera,
  FileBarChart2,
  Mail,
  Phone,
  Save,
  ShieldCheck,
  UserRound,
} from "lucide-react";

type Profile = {
  id?: number;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  organization: string;
  role: string;
  bio: string;
  avatar_path?: string | null;
  created_at?: string;
};

const EMPTY_PROFILE: Profile = {
  username: "",
  first_name: "",
  last_name: "",
  email: "",
  phone: "",
  organization: "",
  role: "",
  bio: "",
  avatar_path: null,
};

const fieldClass =
  "w-full rounded-2xl border theme-border bg-white/[0.03] px-4 py-3 text-sm theme-text-primary outline-none transition focus:border-cyan-400/60 focus:ring-4 focus:ring-cyan-400/10";

export default function ProfilePage() {
  const [profile, setProfile] = useState<Profile>(EMPTY_PROFILE);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    let ignore = false;

    async function loadProfile() {
      try {
        const response = await fetch("/api/auth/me", { credentials: "include" });
        if (!response.ok) {
          throw new Error("Profile not available");
        }
        const data = await response.json();
        if (!ignore) {
          setProfile({ ...EMPTY_PROFILE, ...data.user });
          setAvatarPreview(data.user?.avatar_path || "");
        }
      } catch {
        if (!ignore) {
          setMessage("Profil ma'lumotlarini olish uchun tizimga qayta kiring.");
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    }

    loadProfile();
    return () => {
      ignore = true;
    };
  }, []);

  const displayName = useMemo(() => {
    const fullName = `${profile.first_name} ${profile.last_name}`.trim();
    return fullName || profile.username || "Foydalanuvchi";
  }, [profile.first_name, profile.last_name, profile.username]);

  const completion = useMemo(() => {
    const keys: Array<keyof Profile> = [
      "first_name",
      "last_name",
      "email",
      "phone",
      "organization",
      "role",
      "bio",
      "avatar_path",
    ];
    const filled = keys.filter((key) => Boolean(profile[key])).length + (avatarFile ? 1 : 0);
    return Math.min(100, Math.round((filled / keys.length) * 100));
  }, [avatarFile, profile]);

  function updateField(field: keyof Profile, value: string) {
    setProfile((current) => ({ ...current, [field]: value }));
  }

  function onAvatarChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    setAvatarFile(file);
    const reader = new FileReader();
    reader.onload = () => setAvatarPreview(String(reader.result || ""));
    reader.readAsDataURL(file);
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setMessage("");

    const formData = new FormData();
    formData.set("first_name", profile.first_name);
    formData.set("last_name", profile.last_name);
    formData.set("email", profile.email);
    formData.set("phone", profile.phone);
    formData.set("organization", profile.organization);
    formData.set("role", profile.role);
    formData.set("bio", profile.bio);
    if (avatarFile) {
      formData.set("avatar", avatarFile);
    }

    try {
      const response = await fetch("/api/auth/profile", {
        method: "POST",
        body: formData,
        credentials: "include",
      });
      if (!response.ok) {
        throw new Error(await response.text());
      }
      const data = await response.json();
      setProfile({ ...EMPTY_PROFILE, ...data.user });
      setAvatarFile(null);
      setAvatarPreview(data.user?.avatar_path || "");
      setMessage("Profil ma'lumotlari saqlandi.");
    } catch {
      setMessage("Profilni saqlashda xatolik yuz berdi.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="p-4 lg:p-6 space-y-6 max-w-6xl">
      <div>
        <p className="text-[10px] font-bold uppercase tracking-widest text-cyan-400 mb-1">Dashboard / Profil</p>
        <h1 className="text-2xl sm:text-3xl font-black theme-text-primary tracking-tight">Mening profilim</h1>
        <p className="text-sm theme-text-secondary mt-2 max-w-2xl">
          Shaxsiy ma'lumotlar, aloqa, ish joyi va profil rasmini tahrirlang. Barcha hisobotlar shu foydalanuvchi hisobiga bog'lanadi.
        </p>
      </div>

      <div className="grid gap-5 xl:grid-cols-[360px_1fr]">
        <aside className="card p-6 h-fit">
          <div className="flex flex-col items-center text-center">
            <label className="relative cursor-pointer group">
              <div className="h-32 w-32 overflow-hidden rounded-[2rem] border theme-border bg-cyan-500/10 shadow-[0_18px_50px_rgba(0,229,255,0.15)]">
                {avatarPreview ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={avatarPreview} alt={displayName} className="h-full w-full object-cover" />
                ) : (
                  <div className="flex h-full w-full items-center justify-center">
                    <UserRound className="h-14 w-14 text-cyan-300" />
                  </div>
                )}
              </div>
              <span className="absolute -bottom-2 -right-2 flex h-11 w-11 items-center justify-center rounded-2xl border border-cyan-400/40 bg-cyan-400 text-[#06111f] shadow-lg transition group-hover:scale-105">
                <Camera className="h-5 w-5" />
              </span>
              <input type="file" accept="image/png,image/jpeg,image/webp" className="hidden" onChange={onAvatarChange} />
            </label>

            <h2 className="mt-6 text-xl font-black theme-text-primary">{displayName}</h2>
            <p className="mt-1 text-sm theme-text-secondary">@{profile.username || "username"}</p>
            <div className="mt-4 inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-300">
              <BadgeCheck className="h-4 w-4" />
              Faol hisob
            </div>
          </div>

          <div className="mt-8 space-y-3">
            <div className="flex items-center justify-between rounded-2xl border theme-border bg-white/[0.03] p-4">
              <span className="text-sm theme-text-secondary">Profil to'liqligi</span>
              <span className="text-lg font-black text-cyan-300">{completion}%</span>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-2xl border theme-border bg-white/[0.03] p-4">
                <FileBarChart2 className="mb-3 h-5 w-5 text-cyan-300" />
                <p className="text-2xl font-black theme-text-primary">0</p>
                <p className="text-xs theme-text-muted">Hisobotlar</p>
              </div>
              <div className="rounded-2xl border theme-border bg-white/[0.03] p-4">
                <ShieldCheck className="mb-3 h-5 w-5 text-emerald-300" />
                <p className="text-2xl font-black theme-text-primary">Secure</p>
                <p className="text-xs theme-text-muted">Holat</p>
              </div>
            </div>
          </div>
        </aside>

        <form onSubmit={onSubmit} className="card p-5 sm:p-6 space-y-6">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-lg font-black theme-text-primary">Foydalanuvchi ma'lumotlari</h2>
              <p className="text-sm theme-text-secondary">Bu ma'lumotlar legal hisobotlarda muallif/profil konteksti sifatida ishlatiladi.</p>
            </div>
            <button
              type="submit"
              disabled={saving || loading}
              className="inline-flex items-center justify-center gap-2 rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-black text-[#06111f] shadow-[0_14px_35px_rgba(0,229,255,0.22)] transition hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <Save className="h-4 w-4" />
              {saving ? "Saqlanmoqda..." : "Saqlash"}
            </button>
          </div>

          {message && (
            <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-3 text-sm font-semibold text-cyan-200">
              {message}
            </div>
          )}

          <div className="grid gap-4 md:grid-cols-2">
            <label className="space-y-2">
              <span className="text-xs font-bold uppercase tracking-wider theme-text-muted">Ism</span>
              <input className={fieldClass} value={profile.first_name} onChange={(e) => updateField("first_name", e.target.value)} placeholder="Ismingiz" />
            </label>
            <label className="space-y-2">
              <span className="text-xs font-bold uppercase tracking-wider theme-text-muted">Familiya</span>
              <input className={fieldClass} value={profile.last_name} onChange={(e) => updateField("last_name", e.target.value)} placeholder="Familiyangiz" />
            </label>
            <label className="space-y-2">
              <span className="text-xs font-bold uppercase tracking-wider theme-text-muted">Username</span>
              <input className={`${fieldClass} opacity-70`} value={profile.username} disabled />
            </label>
            <label className="space-y-2">
              <span className="text-xs font-bold uppercase tracking-wider theme-text-muted">Email</span>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-cyan-300" />
                <input className={`${fieldClass} pl-11`} value={profile.email} onChange={(e) => updateField("email", e.target.value)} placeholder="email@example.com" />
              </div>
            </label>
            <label className="space-y-2">
              <span className="text-xs font-bold uppercase tracking-wider theme-text-muted">Telefon</span>
              <div className="relative">
                <Phone className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-cyan-300" />
                <input className={`${fieldClass} pl-11`} value={profile.phone} onChange={(e) => updateField("phone", e.target.value)} placeholder="+998 90 000 00 00" />
              </div>
            </label>
            <label className="space-y-2">
              <span className="text-xs font-bold uppercase tracking-wider theme-text-muted">Tashkilot</span>
              <div className="relative">
                <Building2 className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-cyan-300" />
                <input className={`${fieldClass} pl-11`} value={profile.organization} onChange={(e) => updateField("organization", e.target.value)} placeholder="Universitet, media yoki laboratoriya" />
              </div>
            </label>
            <label className="space-y-2 md:col-span-2">
              <span className="text-xs font-bold uppercase tracking-wider theme-text-muted">Lavozim / rol</span>
              <input className={fieldClass} value={profile.role} onChange={(e) => updateField("role", e.target.value)} placeholder="Jurnalist, tahlilchi, talaba, investigator..." />
            </label>
            <label className="space-y-2 md:col-span-2">
              <span className="text-xs font-bold uppercase tracking-wider theme-text-muted">Bio</span>
              <textarea
                className={`${fieldClass} min-h-32 resize-y`}
                value={profile.bio}
                onChange={(e) => updateField("bio", e.target.value)}
                placeholder="O'zingiz, ishingiz yoki forensik tekshiruv yo'nalishingiz haqida yozing."
              />
            </label>
          </div>
        </form>
      </div>
    </div>
  );
}



