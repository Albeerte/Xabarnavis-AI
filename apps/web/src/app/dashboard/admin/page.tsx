"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  FileBarChart2,
  RefreshCw,
  Save,
  Search,
  Shield,
  SlidersHorizontal,
  Trash2,
  UserRound,
} from "lucide-react";

type AdminModel = {
  model_id: string;
  display_name: string;
  enabled: boolean;
  family: string;
  media_type: string;
  status_snapshot: string;
  purpose: string;
  repository: string;
  local_path: string;
  sort_order: number;
};

type AdminUser = {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  role: string;
  organization: string;
  is_active: number | boolean;
  is_blocked: number | boolean;
  case_count: number;
  session_count: number;
};

type AdminReport = {
  id: number;
  username?: string | null;
  original_filename: string;
  status: string;
  media_type: string;
  uploaded_at: string;
  final_verdict?: string | null;
  confidence?: string | null;
  report_path?: string | null;
};

type NewUserForm = {
  username: string;
  password: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  organization: string;
};

type Overview = {
  models: AdminModel[];
  users: AdminUser[];
  reports: AdminReport[];
  stats: {
    models: number;
    enabled_models: number;
    users: number;
    reports: number;
  };
};

const emptyOverview: Overview = {
  models: [],
  users: [],
  reports: [],
  stats: { models: 0, enabled_models: 0, users: 0, reports: 0 },
};

const emptyNewUser: NewUserForm = {
  username: "",
  password: "",
  email: "",
  first_name: "",
  last_name: "",
  role: "",
  organization: "",
};

export default function AdminDashboardPage() {
  const [data, setData] = useState<Overview>(emptyOverview);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState("");
  const [error, setError] = useState("");
  const [tab, setTab] = useState<"models" | "users" | "reports">("models");
  const [query, setQuery] = useState("");
  const [newUser, setNewUser] = useState<NewUserForm>(emptyNewUser);

  async function load() {
    setError("");
    try {
      const response = await fetch("/api/admin/overview", { credentials: "include" });
      if (response.status === 403) {
        setError("Bu sahifa faqat admin uchun. Sizda admin huquqi yo'q.");
        return;
      }
      if (!response.ok) throw new Error(await response.text());
      setData(await response.json());
    } catch {
      setError("Admin ma'lumotlarini yuklashda xatolik yuz berdi. Login qilinganini tekshiring.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function syncModels() {
    setSaving("sync");
    try {
      const response = await fetch("/api/admin/models/sync", { method: "POST", credentials: "include" });
      if (!response.ok) throw new Error(await response.text());
      const payload = await response.json();
      setData((prev) => ({ ...prev, models: payload.models, stats: { ...prev.stats, models: payload.models.length, enabled_models: payload.models.filter((item: AdminModel) => item.enabled).length } }));
    } catch {
      setError("Modellarni sync qilishda xatolik yuz berdi.");
    } finally {
      setSaving("");
    }
  }

  async function updateModel(model: AdminModel, patch: Partial<AdminModel>) {
    setSaving(model.model_id);
    try {
      const response = await fetch(`/api/admin/models/${encodeURIComponent(model.model_id)}`, {
        method: "PATCH",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(patch),
      });
      if (!response.ok) throw new Error(await response.text());
      const payload = await response.json();
      setData((prev) => ({
        ...prev,
        models: payload.models,
        stats: {
          ...prev.stats,
          models: payload.models.length,
          enabled_models: payload.models.filter((item: AdminModel) => item.enabled).length,
        },
      }));
    } catch {
      setError("Model sozlamasini saqlashda xatolik yuz berdi.");
    } finally {
      setSaving("");
    }
  }

  async function updateUser(user: AdminUser, patch: Partial<AdminUser>) {
    setSaving(`user-${user.id}`);
    try {
      const response = await fetch(`/api/admin/users/${user.id}`, {
        method: "PATCH",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(patch),
      });
      if (!response.ok) throw new Error(await response.text());
      const payload = await response.json();
      setData((prev) => ({ ...prev, users: payload.users, stats: { ...prev.stats, users: payload.users.length } }));
    } catch {
      setError("User ma'lumotini saqlashda xatolik yuz berdi.");
    } finally {
      setSaving("");
    }
  }

  async function createUser(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving("create-user");
    setError("");
    try {
      const response = await fetch("/api/admin/users", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newUser),
      });
      if (!response.ok) throw new Error(await response.text());
      const payload = await response.json();
      setData((prev) => ({
        ...prev,
        users: payload.users,
        stats: { ...prev.stats, users: payload.users.length },
      }));
      setNewUser(emptyNewUser);
    } catch {
      setError("Yangi user qo'shishda xatolik yuz berdi. Username yoki email band bo'lishi mumkin.");
    } finally {
      setSaving("");
    }
  }

  async function deleteUser(user: AdminUser) {
    if (!confirm(`${user.username} userini o'chirasizmi?`)) return;
    setSaving(`user-${user.id}`);
    try {
      const response = await fetch(`/api/admin/users/${user.id}`, { method: "DELETE", credentials: "include" });
      if (!response.ok) throw new Error(await response.text());
      const payload = await response.json();
      setData((prev) => ({ ...prev, users: payload.users, reports: payload.reports, stats: { ...prev.stats, users: payload.users.length, reports: payload.reports.length } }));
    } catch {
      setError("Userni o'chirishda xatolik yuz berdi.");
    } finally {
      setSaving("");
    }
  }

  async function deleteReport(report: AdminReport) {
    if (!confirm(`CASE-${report.id} reportini o'chirasizmi?`)) return;
    setSaving(`report-${report.id}`);
    try {
      const response = await fetch(`/api/admin/reports/${report.id}`, { method: "DELETE", credentials: "include" });
      if (!response.ok) throw new Error(await response.text());
      const payload = await response.json();
      setData((prev) => ({ ...prev, reports: payload.reports, stats: { ...prev.stats, reports: payload.reports.length } }));
    } catch {
      setError("Reportni o'chirishda xatolik yuz berdi.");
    } finally {
      setSaving("");
    }
  }

  const filteredModels = useFiltered(data.models, query, (item) => `${item.model_id} ${item.display_name} ${item.family} ${item.media_type} ${item.status_snapshot}`);
  const filteredUsers = useFiltered(data.users, query, (item) => `${item.username} ${item.first_name} ${item.last_name} ${item.email} ${item.role} ${item.organization}`);
  const filteredReports = useFiltered(data.reports, query, (item) => `${item.id} ${item.username || ""} ${item.original_filename} ${item.final_verdict || ""} ${item.media_type}`);

  return (
    <div className="space-y-5 p-4 lg:p-6">
      <section className="rounded-2xl border theme-border bg-[linear-gradient(135deg,rgba(0,212,255,0.14),rgba(255,255,255,0.03))] p-5 lg:p-7">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-400">Dashboard / Admin</p>
            <h1 className="mt-3 text-3xl font-black theme-text-primary">Website admin panel</h1>
            <p className="mt-2 max-w-2xl text-sm theme-text-secondary">
              Modellar, userlar va barcha reportlarni bitta joydan boshqarish.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button onClick={syncModels} className="btn btn-ghost h-10" disabled={saving === "sync"}>
              <RefreshCw className={`h-4 w-4 ${saving === "sync" ? "animate-spin" : ""}`} />
              Sync models
            </button>
            <button onClick={load} className="btn btn-cyan h-10">
              <RefreshCw className="h-4 w-4" />
              Yangilash
            </button>
          </div>
        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <Stat label="Jami model" value={data.stats.models} icon={SlidersHorizontal} />
          <Stat label="Yoqilgan model" value={data.stats.enabled_models} icon={Shield} />
          <Stat label="Userlar" value={data.stats.users} icon={UserRound} />
          <Stat label="Reportlar" value={data.stats.reports} icon={FileBarChart2} />
        </div>
      </section>

      <section className="card p-4">
        <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <div className="relative min-w-0 flex-1 xl:max-w-md">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 theme-text-muted" />
            <input className="xinput h-11 pl-10" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Qidirish..." />
          </div>
          <div className="flex flex-wrap gap-2">
            {(["models", "users", "reports"] as const).map((item) => (
              <button key={item} onClick={() => setTab(item)} className={`rounded-full border px-4 py-2 text-xs font-bold ${tab === item ? "border-cyan-400 bg-cyan-400/10 text-cyan-300" : "theme-border theme-text-secondary"}`}>
                {item === "models" ? "Modellar" : item === "users" ? "Userlar" : "Reportlar"}
              </button>
            ))}
          </div>
        </div>
      </section>

      {error && <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-sm font-bold text-red-300">{error}</div>}
      {loading ? (
        <section className="card grid min-h-64 place-items-center p-8">
          <div className="h-10 w-10 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent" />
        </section>
      ) : tab === "models" ? (
        <ModelsTable models={filteredModels} saving={saving} onUpdate={updateModel} />
      ) : tab === "users" ? (
        <UsersTable
          users={filteredUsers}
          saving={saving}
          newUser={newUser}
          setNewUser={setNewUser}
          onCreate={createUser}
          onUpdate={updateUser}
          onDelete={deleteUser}
        />
      ) : (
        <ReportsTable reports={filteredReports} saving={saving} onDelete={deleteReport} />
      )}
    </div>
  );
}

function ModelsTable({ models, saving, onUpdate }: { models: AdminModel[]; saving: string; onUpdate: (model: AdminModel, patch: Partial<AdminModel>) => void }) {
  return (
    <section className="grid gap-3">
      {models.map((model) => (
        <article key={model.model_id} className="card p-4">
          <div className="grid gap-3 xl:grid-cols-[80px_minmax(220px,1fr)_160px_120px_120px] xl:items-center">
            <input className="xinput h-10" type="number" defaultValue={model.sort_order} onBlur={(event) => onUpdate(model, { sort_order: Number(event.target.value) })} />
            <div>
              <input className="xinput h-10 font-bold" defaultValue={model.display_name} onBlur={(event) => event.target.value !== model.display_name && onUpdate(model, { display_name: event.target.value })} />
              <p className="mt-1 font-mono text-[11px] theme-text-muted">{model.model_id}</p>
              <p className="mt-1 line-clamp-2 text-xs theme-text-secondary">{model.purpose}</p>
            </div>
            <Badge>{model.media_type} / {model.family}</Badge>
            <Badge>{model.status_snapshot}</Badge>
            <button onClick={() => onUpdate(model, { enabled: !model.enabled })} disabled={saving === model.model_id} className={`h-10 rounded-xl border text-xs font-black ${model.enabled ? "border-green-400/40 bg-green-400/10 text-green-300" : "border-red-400/40 bg-red-400/10 text-red-300"}`}>
              {saving === model.model_id ? "..." : model.enabled ? "Yoqilgan" : "O'chirilgan"}
            </button>
          </div>
          {model.local_path && <p className="mt-2 break-all font-mono text-[10px] theme-text-muted">{model.local_path}</p>}
        </article>
      ))}
    </section>
  );
}

function UsersTable({
  users,
  saving,
  newUser,
  setNewUser,
  onCreate,
  onUpdate,
  onDelete,
}: {
  users: AdminUser[];
  saving: string;
  newUser: NewUserForm;
  setNewUser: React.Dispatch<React.SetStateAction<NewUserForm>>;
  onCreate: (event: React.FormEvent<HTMLFormElement>) => void;
  onUpdate: (user: AdminUser, patch: Partial<AdminUser>) => void;
  onDelete: (user: AdminUser) => void;
}) {
  return (
    <section className="grid gap-3">
      <form onSubmit={onCreate} className="card grid gap-3 p-4 xl:grid-cols-[1fr_1fr_1fr_1fr_auto] xl:items-end">
        <label className="grid gap-1 text-xs font-bold theme-text-muted">
          Username
          <input
            required
            minLength={3}
            className="xinput h-10"
            value={newUser.username}
            onChange={(event) => setNewUser((prev) => ({ ...prev, username: event.target.value }))}
            placeholder="username"
          />
        </label>
        <label className="grid gap-1 text-xs font-bold theme-text-muted">
          Password
          <input
            required
            minLength={6}
            type="password"
            className="xinput h-10"
            value={newUser.password}
            onChange={(event) => setNewUser((prev) => ({ ...prev, password: event.target.value }))}
            placeholder="kamida 6 belgi"
          />
        </label>
        <label className="grid gap-1 text-xs font-bold theme-text-muted">
          Email
          <input
            type="email"
            className="xinput h-10"
            value={newUser.email}
            onChange={(event) => setNewUser((prev) => ({ ...prev, email: event.target.value }))}
            placeholder="email"
          />
        </label>
        <label className="grid gap-1 text-xs font-bold theme-text-muted">
          Role
          <input
            className="xinput h-10"
            value={newUser.role}
            onChange={(event) => setNewUser((prev) => ({ ...prev, role: event.target.value }))}
            placeholder="admin, expert..."
          />
        </label>
        <button disabled={saving === "create-user"} className="btn btn-cyan h-10 justify-center px-5">
          <Save className="h-4 w-4" />
          {saving === "create-user" ? "Qo'shilmoqda" : "User qo'shish"}
        </button>
        <label className="grid gap-1 text-xs font-bold theme-text-muted xl:col-span-2">
          Ism
          <input
            className="xinput h-10"
            value={newUser.first_name}
            onChange={(event) => setNewUser((prev) => ({ ...prev, first_name: event.target.value }))}
            placeholder="ismi"
          />
        </label>
        <label className="grid gap-1 text-xs font-bold theme-text-muted">
          Familiya
          <input
            className="xinput h-10"
            value={newUser.last_name}
            onChange={(event) => setNewUser((prev) => ({ ...prev, last_name: event.target.value }))}
            placeholder="familiyasi"
          />
        </label>
        <label className="grid gap-1 text-xs font-bold theme-text-muted xl:col-span-2">
          Organization
          <input
            className="xinput h-10"
            value={newUser.organization}
            onChange={(event) => setNewUser((prev) => ({ ...prev, organization: event.target.value }))}
            placeholder="tashkilot"
          />
        </label>
      </form>
      {users.map((user) => (
        <article key={user.id} className="card p-4">
          <div className="grid gap-3 xl:grid-cols-[1fr_1fr_140px_130px_120px_120px] xl:items-center">
            <div>
              <p className="text-sm font-black theme-text-primary">{user.username}</p>
              <p className="text-xs theme-text-muted">ID {user.id} · {user.case_count} reports · {user.session_count} sessions</p>
            </div>
            <input className="xinput h-10" defaultValue={user.email || ""} placeholder="email" onBlur={(event) => event.target.value !== user.email && onUpdate(user, { email: event.target.value })} />
            <select className="xinput h-10" defaultValue={user.role || "user"} onChange={(event) => event.target.value !== user.role && onUpdate(user, { role: event.target.value })}>
              <option value="user">user</option>
              <option value="support">support</option>
              <option value="analyst">analyst</option>
              <option value="admin">admin</option>
              <option value="superadmin">superadmin</option>
            </select>
            <Badge>{user.is_blocked ? "Bloklangan" : user.is_active ? "Faol" : "Nofaol"}</Badge>
            <button
              disabled={saving === `user-${user.id}`}
              onClick={() => onUpdate(user, user.is_blocked ? { is_blocked: false, is_active: true } : { is_blocked: true, is_active: false })}
              className={`h-10 rounded-xl border text-xs font-black ${user.is_blocked ? "border-green-400/40 bg-green-400/10 text-green-300" : "border-amber-400/40 bg-amber-400/10 text-amber-300"}`}
            >
              {user.is_blocked ? "Faollashtirish" : "Bloklash"}
            </button>
            <button disabled={saving === `user-${user.id}`} onClick={() => onDelete(user)} className="btn btn-danger h-10 justify-center">
              <Trash2 className="h-4 w-4" />
              O'chirish
            </button>
          </div>
        </article>
      ))}
    </section>
  );
}

function ReportsTable({ reports, saving, onDelete }: { reports: AdminReport[]; saving: string; onDelete: (report: AdminReport) => void }) {
  return (
    <section className="grid gap-3">
      {reports.map((report) => (
        <article key={report.id} className="card p-4">
          <div className="grid gap-3 xl:grid-cols-[1fr_150px_150px_120px_150px] xl:items-center">
            <div>
              <p className="text-sm font-black theme-text-primary">{report.original_filename}</p>
              <p className="text-xs theme-text-muted">CASE-{report.id} · {report.username || "user yo'q"} · {formatDate(report.uploaded_at)}</p>
            </div>
            <Badge>{report.media_type}</Badge>
            <Badge>{report.final_verdict || report.status}</Badge>
            <Link href={`/dashboard/reports/${report.id}`} className="btn btn-ghost h-10 justify-center text-xs">Ochish</Link>
            <button disabled={saving === `report-${report.id}`} onClick={() => onDelete(report)} className="btn btn-danger h-10 justify-center">
              <Trash2 className="h-4 w-4" />
              O'chirish
            </button>
          </div>
        </article>
      ))}
    </section>
  );
}

function Stat({ label, value, icon: Icon }: { label: string; value: number; icon: typeof Shield }) {
  return (
    <div className="rounded-2xl border theme-border bg-black/10 p-4">
      <div className="flex items-center justify-between">
        <p className="text-xs font-bold uppercase tracking-[0.12em] theme-text-muted">{label}</p>
        <Icon className="h-4 w-4 text-cyan-300" />
      </div>
      <p className="mt-3 text-3xl font-black text-cyan-300">{value}</p>
    </div>
  );
}

function Badge({ children }: { children: React.ReactNode }) {
  return <span className="inline-flex min-h-9 items-center rounded-xl border theme-border px-3 py-2 text-xs font-bold theme-text-secondary">{children}</span>;
}

function useFiltered<T>(items: T[], query: string, text: (item: T) => string) {
  return useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!needle) return items;
    return items.filter((item) => text(item).toLowerCase().includes(needle));
  }, [items, query, text]);
}

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("uz-UZ");
}
