"use client";

import Image from "next/image";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, Suspense, useEffect, useMemo, useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  Camera,
  LockKeyhole,
  Mail,
  ShieldCheck,
  UserPlus,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

type AuthMode = "login" | "register";

function requestedMode(value: string | null): AuthMode {
  return value === "register" ? "register" : "login";
}

function safeNext(value: string | null) {
  if (!value) {
    return "dashboard";
  }

  return /^[a-z-]+$/.test(value) ? value : "dashboard";
}

function LoginContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nextPage = useMemo(() => safeNext(searchParams.get("next")), [searchParams]);
  const mode = requestedMode(searchParams.get("mode"));
  const [username, setUsername] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [organization, setOrganization] = useState("");
  const [role, setRole] = useState("");
  const [bio, setBio] = useState("");
  const [avatar, setAvatar] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState("");
  const [password, setPassword] = useState("");
  const [passwordCheck, setPasswordCheck] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function checkSession() {
      try {
        const response = await fetch("/api/auth/me", { credentials: "same-origin" });
        if (response.ok && !cancelled) {
          router.replace(`/dashboard#${nextPage}`);
        }
      } catch {
        // Not logged in yet.
      }
    }

    checkSession();
    return () => {
      cancelled = true;
    };
  }, [nextPage, router]);

  useEffect(() => {
    return () => {
      if (avatarPreview) {
        URL.revokeObjectURL(avatarPreview);
      }
    };
  }, [avatarPreview]);

  function selectMode(nextMode: AuthMode) {
    setError("");
    setPassword("");
    setPasswordCheck("");
    const params = new URLSearchParams(searchParams.toString());
    if (nextMode === "register") {
      params.set("mode", "register");
    } else {
      params.delete("mode");
    }
    router.replace(`/login${params.size ? `?${params.toString()}` : ""}`, { scroll: false });
  }

  async function submitAuth(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    if (mode === "register" && password !== passwordCheck) {
      setError("Password va password check bir xil emas.");
      return;
    }
    if (!/^[a-zA-Z0-9._-]{3,40}$/.test(username.trim())) {
      setError("Username 3–40 ta harf, raqam, nuqta, chiziq yoki pastki chiziqdan iborat bo‘lsin.");
      return;
    }

    setIsLoading(true);

    const form = new FormData();
    form.append("username", username.trim());
    form.append("password", password);
    if (mode === "register") {
      form.append("first_name", firstName.trim());
      form.append("last_name", lastName.trim());
      form.append("email", email.trim());
      form.append("phone", phone.trim());
      form.append("organization", organization.trim());
      form.append("role", role.trim());
      form.append("bio", bio.trim());
      if (avatar) {
        form.append("avatar", avatar);
      }
    }

    try {
      const response = await fetch(`/api/auth/${mode}`, {
        method: "POST",
        body: form,
        credentials: "same-origin",
      });
      const payload = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(payload.detail || "Login yoki register bajarilmadi.");
      }

      router.replace(`/dashboard#${nextPage}`);
    } catch (authError) {
      setError(authError instanceof Error ? authError.message : "Noma'lum xatolik yuz berdi.");
    } finally {
      setIsLoading(false);
    }
  }

  async function startGoogleLogin() {
    setError("");
    try {
      const response = await fetch("/api/auth/google", { credentials: "same-origin" });
      const payload = await response.json().catch(() => ({}));
      setError(payload.detail || "Google login hozircha sozlanmagan.");
    } catch {
      setError("Google login ulanishida xatolik yuz berdi.");
    }
  }

  return (
    <main className="min-h-screen neural-grid px-5 py-8 text-white lg:px-8">
      <div className="mx-auto flex max-w-6xl items-center justify-between">
        <button
          type="button"
          onClick={() => router.push("/")}
          className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.06] px-4 py-2 text-sm font-semibold text-slate-200 transition hover:border-cyan-300/40 hover:text-white"
        >
          <ArrowLeft className="size-4" />
          Bosh sahifa
        </button>
        <Badge>
          <ShieldCheck className="size-3.5" />
          Xavfsiz local login
        </Badge>
      </div>

      <section className="mx-auto grid max-w-6xl gap-8 py-14 lg:grid-cols-[0.95fr_1.05fr] lg:items-center lg:py-20">
        <div>
          <div className="flex items-center gap-4">
            <div className="logo-shell grid size-16 place-items-center rounded-3xl border border-white/10 bg-white/[0.06] p-2 shadow-[0_0_38px_rgba(34,211,238,0.32)]">
              <Image
                src="/xabarnavis-logo.png"
                alt="Xabarnavis AI logo"
                width={52}
                height={52}
                priority
                className="logo-img object-contain"
              />
            </div>
            <div>
              <h1 className="text-2xl font-semibold">Xabarnavis AI</h1>
              <p className="text-sm uppercase tracking-[0.28em] text-cyan-200">
                forensic laboratoriya
              </p>
            </div>
          </div>

          <h2 className="mt-10 max-w-2xl text-5xl font-semibold tracking-[-0.05em] md:text-6xl">
            Dashboardga xavfsiz kirish
          </h2>
          <p className="mt-6 max-w-xl text-lg leading-8 text-slate-300">
            Login yoki register qiling. Account yaratilgandan keyin rasm tahlili,
            legal DOCX/JSON reportlar va case arxivi sizning profilingizga bog&apos;lanadi.
          </p>

          <div className="mt-8 grid max-w-xl gap-3 sm:grid-cols-3">
            {["Private session", "Account reports", "Image analyzer"].map((item) => (
              <div
                key={item}
                className="rounded-2xl border border-white/10 bg-white/[0.05] p-4 text-sm text-slate-300 backdrop-blur-xl"
              >
                <ShieldCheck className="mb-3 size-4 text-cyan-300" />
                {item}
              </div>
            ))}
          </div>
        </div>

        <Card className="p-2">
          <CardHeader>
            <div className="flex rounded-full border border-white/10 bg-white/[0.04] p-1">
              {(["login", "register"] as const).map((item) => (
                <button
                  key={item}
                  type="button"
                  onClick={() => selectMode(item)}
                  aria-pressed={mode === item}
                  className={`h-11 flex-1 rounded-full text-sm font-semibold transition ${
                    mode === item
                      ? "bg-cyan-300 text-slate-950"
                      : "text-slate-300 hover:text-white"
                  }`}
                >
                  {item === "login" ? "Login" : "Register"}
                </button>
              ))}
            </div>
            <div className="pt-5">
              <Badge>{mode === "login" ? "Hisobga kirish" : "Yangi account"}</Badge>
              <h3 className="mt-4 text-3xl font-semibold">
                {mode === "login" ? "Dashboardni ochish" : "Account yaratish"}
              </h3>
              <p className="mt-3 text-slate-300">
                {mode === "login"
                  ? "Username va parolni kiriting. Muvaffaqiyatli login bo'lsa, dashboard ochiladi."
                  : "To'liq profilingizni kiriting. Barcha tahlillar shu hisobga bog'lanadi."}
              </p>
            </div>
          </CardHeader>
          <CardContent>
            <form className="space-y-5" onSubmit={submitAuth}>
              <button
                type="button"
                onClick={startGoogleLogin}
                className="flex h-12 w-full items-center justify-center gap-3 rounded-2xl border border-white/10 bg-white/[0.06] text-sm font-semibold text-white transition hover:border-cyan-300/40 hover:bg-white/[0.1]"
              >
                <Mail className="size-4 text-cyan-200" />
                Google orqali kirish
              </button>

              <div className="flex items-center gap-3 text-xs uppercase tracking-[0.18em] text-slate-500">
                <span className="h-px flex-1 bg-white/10" />
                yoki lokal hisob
                <span className="h-px flex-1 bg-white/10" />
              </div>

              {mode === "register" ? (
                <div className="grid gap-5 md:grid-cols-2">
                  <label className="block">
                    <span className="text-sm font-medium text-slate-300">Ism</span>
                    <input
                      value={firstName}
                      onChange={(event) => setFirstName(event.target.value)}
                      required
                      className="mt-2 h-13 w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300/60"
                      placeholder="Ali"
                    />
                  </label>
                  <label className="block">
                    <span className="text-sm font-medium text-slate-300">Familiya</span>
                    <input
                      value={lastName}
                      onChange={(event) => setLastName(event.target.value)}
                      required
                      className="mt-2 h-13 w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300/60"
                      placeholder="Valiyev"
                    />
                  </label>
                </div>
              ) : null}

              <label className="block">
                <span className="text-sm font-medium text-slate-300">
                  {mode === "login" ? "Username yoki email" : "Username"}
                </span>
                <input
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  minLength={3}
                  required
                  autoComplete="username"
                  className="mt-2 h-13 w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300/60"
                  maxLength={40}
                  placeholder={mode === "login" ? "username yoki email" : "username"}
                />
              </label>

              {mode === "register" ? (
                <>
                  <div className="grid gap-5 md:grid-cols-2">
                    <label className="block">
                      <span className="text-sm font-medium text-slate-300">Email</span>
                      <input
                        value={email}
                        onChange={(event) => setEmail(event.target.value)}
                        type="email"
                        autoComplete="email"
                        className="mt-2 h-13 w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300/60"
                        placeholder="name@example.com"
                      />
                    </label>
                    <label className="block">
                      <span className="text-sm font-medium text-slate-300">Telefon</span>
                      <input
                        value={phone}
                        onChange={(event) => setPhone(event.target.value)}
                        autoComplete="tel"
                        className="mt-2 h-13 w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300/60"
                        placeholder="+998"
                      />
                    </label>
                  </div>
                  <div className="grid gap-5 md:grid-cols-2">
                    <label className="block">
                      <span className="text-sm font-medium text-slate-300">Tashkilot</span>
                      <input
                        value={organization}
                        onChange={(event) => setOrganization(event.target.value)}
                        className="mt-2 h-13 w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300/60"
                        placeholder="Universitet, media, laboratoriya"
                      />
                    </label>
                    <label className="block">
                      <span className="text-sm font-medium text-slate-300">Lavozim / role</span>
                      <input
                        value={role}
                        onChange={(event) => setRole(event.target.value)}
                        className="mt-2 h-13 w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300/60"
                        placeholder="Jurnalist, talaba, investigator"
                      />
                    </label>
                  </div>
                  <label className="block">
                    <span className="text-sm font-medium text-slate-300">Profil rasmi</span>
                    <div className="mt-2 flex items-center gap-4 rounded-2xl border border-dashed border-cyan-300/30 bg-cyan-300/[0.035] p-4">
                      <div className="grid size-16 place-items-center overflow-hidden rounded-2xl border border-white/10 bg-white/[0.06]">
                        {avatarPreview ? (
                          // eslint-disable-next-line @next/next/no-img-element
                          <img src={avatarPreview} alt="Avatar preview" className="size-full object-cover" />
                        ) : (
                          <Camera className="size-6 text-cyan-200" />
                        )}
                      </div>
                      <input
                        type="file"
                        accept="image/png,image/jpeg,image/webp"
                        onChange={(event) => {
                          const file = event.target.files?.[0] ?? null;
                          if (avatarPreview) {
                            URL.revokeObjectURL(avatarPreview);
                          }
                          setAvatar(file);
                          setAvatarPreview(file ? URL.createObjectURL(file) : "");
                        }}
                        className="text-sm text-slate-300 file:mr-4 file:rounded-full file:border-0 file:bg-cyan-300 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-slate-950"
                      />
                    </div>
                  </label>
                  <label className="block">
                    <span className="text-sm font-medium text-slate-300">To&apos;liq ma&apos;lumot / bio</span>
                    <textarea
                      value={bio}
                      onChange={(event) => setBio(event.target.value)}
                      rows={3}
                      className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300/60"
                      placeholder="Siz haqingizda qisqa ma'lumot..."
                    />
                  </label>
                </>
              ) : null}

              <label className="block">
                <span className="text-sm font-medium text-slate-300">Password</span>
                <input
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  minLength={6}
                  required
                  type="password"
                  autoComplete={mode === "login" ? "current-password" : "new-password"}
                  className="mt-2 h-13 w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300/60"
                  placeholder="kamida 6 belgi"
                />
              </label>
              {mode === "register" ? (
                <label className="block">
                  <span className="text-sm font-medium text-slate-300">Password check</span>
                  <input
                    value={passwordCheck}
                    onChange={(event) => setPasswordCheck(event.target.value)}
                    minLength={6}
                    required
                    type="password"
                    autoComplete="new-password"
                    className="mt-2 h-13 w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300/60"
                    placeholder="parolni qayta kiriting"
                  />
                </label>
              ) : null}

              {error ? (
                <div className="rounded-2xl border border-rose-300/25 bg-rose-400/10 px-4 py-3 text-sm text-rose-100">
                  {error}
                </div>
              ) : null}

              <Button className="w-full" size="lg" type="submit" disabled={isLoading}>
                {mode === "login" ? <LockKeyhole className="size-5" /> : <UserPlus className="size-5" />}
                {isLoading ? "Tekshirilmoqda..." : mode === "login" ? "Login qilish" : "Register qilish"}
                <ArrowRight className="size-5" />
              </Button>
            </form>
          </CardContent>
        </Card>
      </section>
    </main>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<main className="min-h-screen neural-grid" />}>
      <LoginContent />
    </Suspense>
  );
}



