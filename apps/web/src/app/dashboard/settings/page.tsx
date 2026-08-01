"use client";

import { useTheme } from "@/components/ThemeProvider";
import { Sun, Moon } from "lucide-react";
import { useState } from "react";

function Row({ label, desc, children }: { label: string; desc: string; children: React.ReactNode }) {
  return (
    <div style={{
      display: "flex", alignItems: "center", justifyContent: "space-between",
      padding: "14px 0", borderBottom: "1px solid var(--border)",
    }}>
      <div style={{ flex: 1, minWidth: 0, paddingRight: 16 }}>
        <p style={{ fontSize: 13, fontWeight: 600, color: "var(--txt1)" }}>{label}</p>
        <p style={{ fontSize: 11, color: "var(--txt3)", marginTop: 2 }}>{desc}</p>
      </div>
      {children}
    </div>
  );
}

function Toggle({ on, onChange }: { on: boolean; onChange: () => void }) {
  return (
    <button
      onClick={onChange}
      style={{
        width: 40, height: 22, borderRadius: 99, border: "none", cursor: "pointer",
        background: on ? "var(--cyan)" : "var(--bg2)",
        position: "relative", transition: "background 0.2s", flexShrink: 0,
      }}
    >
      <span style={{
        position: "absolute", top: 3, left: on ? 21 : 3,
        width: 16, height: 16, borderRadius: "50%", background: "#fff",
        transition: "left 0.2s", boxShadow: "0 1px 3px rgba(0,0,0,0.3)",
      }} />
    </button>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="card" style={{ padding: "16px 20px" }}>
      <p className="label" style={{ marginBottom: 4 }}>{title}</p>
      {children}
    </div>
  );
}

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const [publicReport, setPublicReport] = useState(true);
  const [qrEnabled, setQrEnabled] = useState(true);
  const [newDeviceNotif, setNewDeviceNotif] = useState(true);
  const [twoFactor, setTwoFactor] = useState(false);
  const [showToken, setShowToken] = useState(false);

  return (
    <div style={{ padding: "20px 24px", display: "flex", flexDirection: "column", gap: 16, maxWidth: 680 }}>
      <div>
        <p style={{ fontSize: 11, color: "var(--txt3)", marginBottom: 4 }}>Dashboard / Sozlamalar</p>
        <h1 style={{ fontSize: 20, fontWeight: 800, color: "var(--txt1)" }}>Vebsayt sozlamalari</h1>
        <p style={{ fontSize: 13, color: "var(--txt2)", marginTop: 4 }}>Sayt ko'rinishi, hisobot formati, xavfsizlik va bildirishnoma parametrlarini boshqarish</p>
      </div>

      {/* â”€â”€ Appearance â”€â”€ */}
      <Section title="Ko'rinish">
        <Row label="Mavzu" desc="Interfeys ko'rinishini tanlang">
          <div className="theme-pill">
            <button className={theme === "dark" ? "active" : ""} onClick={() => setTheme("dark")}>
              <Moon style={{ width: 11, height: 11 }} />Tun
            </button>
            <button className={theme === "light" ? "active" : ""} onClick={() => setTheme("light")}>
              <Sun style={{ width: 11, height: 11 }} />Kun
            </button>
          </div>
        </Row>
      </Section>

      {/* â”€â”€ Report settings â”€â”€ */}
      <Section title="Hisobot sozlamalari">
        <Row label="Hisobot tili" desc="Rasmiy hisobotlar tili">
          <select className="xinput" style={{ width: "auto", padding: "5px 10px" }}>
            <option>O'zbek</option>
            <option>Ingliz</option>
            <option>Rus</option>
          </select>
        </Row>
        <Row label="Public hisobot" desc="QR orqali ommaviy ko'rishga ruxsat berish">
          <Toggle on={publicReport} onChange={() => setPublicReport(!publicReport)} />
        </Row>
        <Row label="QR kod" desc="Har bir hisobot uchun avtomatik QR kod">
          <Toggle on={qrEnabled} onChange={() => setQrEnabled(!qrEnabled)} />
        </Row>
      </Section>

      {/* â”€â”€ Security â”€â”€ */}
      <Section title="Xavfsizlik">
        <Row label="Yangi qurilma bildirishnomasi" desc="Yangi qurilmadan kirish bo'lganda xabar olish">
          <Toggle on={newDeviceNotif} onChange={() => setNewDeviceNotif(!newDeviceNotif)} />
        </Row>
        <Row label="Ikki faktorli autentifikatsiya" desc="Kirishda qo'shimcha tasdiqlash">
          <Toggle on={twoFactor} onChange={() => setTwoFactor(!twoFactor)} />
        </Row>
      </Section>

      {/* â”€â”€ API Token â”€â”€ */}
      <Section title="API token">
        <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
          <input
            type={showToken ? "text" : "password"}
            readOnly
            value="xb_api_b4f9e2c1a7d3f6e8b1c4a9d2e5f8b3c6a1"
            className="xinput"
            style={{ fontFamily: "monospace", fontSize: 12 }}
          />
          <button className="btn btn-ghost" onClick={() => setShowToken(!showToken)}>
            {showToken ? "Yashirish" : "Ko'rsatish"}
          </button>
          <button className="btn btn-danger">Yangilash</button>
        </div>
        <p style={{ fontSize: 10, color: "var(--txt3)", marginTop: 8 }}>
          Model versiyasi:{" "}
          <span style={{ color: "var(--cyan)", fontFamily: "monospace" }}>XabarnavisVision v2.1.4</span> Â·{" "}
          XabarnavisAudio v1.3.2 Â· XabarnavisText v1.8.1
        </p>
      </Section>
    </div>
  );
}



