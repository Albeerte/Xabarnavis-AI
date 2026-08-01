export type RiskLevel = "past" | "ortacha" | "yuqori" | "juda_yuqori";
export type FileType = "image" | "video" | "audio" | "text";
export type ResultType = "Haqiqiy" | "AI yaratgan" | "Manipulyatsiya" | "Shubhali";
export type DeviceType = "desktop" | "mobile" | "tablet";

export interface Report {
  id: string;
  publicToken: string;
  fileName: string;
  fileType: FileType;
  fileSize: string;
  mimeType: string;
  sha256: string;
  uploadedAt: string;
  analyzedAt: string;
  userId: string;
  deviceId: string;
  aiProbability: number;
  realProbability: number;
  manipulationScore: number;
  riskLevel: RiskLevel;
  result: ResultType;
  conclusionUz: string;
  modelName: string;
  modelVersion: string;
  explainability: string;
  qrCodeUrl: string;
  publicUrl: string;
  device: string;
  browser: string;
  os: string;
  ip: string;
  maskedIp: string;
  timezone: string;
  screenResolution: string;
  userAgent: string;
}

export interface Device {
  id: string;
  userId: string;
  deviceName: string;
  deviceType: DeviceType;
  browser: string;
  os: string;
  ipAddress: string;
  maskedIp: string;
  timezone: string;
  screenResolution: string;
  firstLoginAt: string;
  lastLoginAt: string;
  lastLogoutAt: string;
  isActive: boolean;
  isTrusted: boolean;
  reportsCount: number;
  lastFile: string;
}

export interface SessionLog {
  id: string;
  userId: string;
  deviceId: string;
  deviceName: string;
  loginAt: string;
  logoutAt: string | null;
  ipAddress: string;
  browser: string;
  os: string;
  status: "success" | "failed";
  duration: string;
}

export interface Notification {
  id: string;
  type: "report" | "danger" | "device" | "qr" | "export" | "model";
  title: string;
  message: string;
  time: string;
  read: boolean;
}

export const mockReports: Report[] = [
  {
    id: "RPT-2024-001",
    publicToken: "xb_pub_a8f5f167f44f4964e6c998dee827110c",
    fileName: "shubhali_rasm_01.jpg",
    fileType: "image",
    fileSize: "4.2 MB",
    mimeType: "image/jpeg",
    sha256: "a8f5f167f44f4964e6c998dee827110c5a7f4b3d2e1c9b8a7f6e5d4c3b2a1908",
    uploadedAt: "2026-06-30 14:29:13",
    analyzedAt: "2026-06-30 14:29:45",
    userId: "user_001",
    deviceId: "dev_001",
    aiProbability: 87,
    realProbability: 13,
    manipulationScore: 82,
    riskLevel: "juda_yuqori",
    result: "AI yaratgan",
    conclusionUz: "Rasmda sun'iy intellekt orqali yaratilgan kontentga xos bo'lgan ayrim vizual belgilar aniqlandi. Ayniqsa, yuz/chegara/chiroq/noise qatlamlarida nomuvofiqlik bor.",
    modelName: "XabarnavisVision v2.1",
    modelVersion: "2.1.4",
    explainability: "EXIF yo'q, noise pattern g'ayrioddiy, chegara artifaktlari topildi",
    qrCodeUrl: "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://xabarnavis.ai/r/public/xb_pub_a8f5f167f44f4964e6c998dee827110c",
    publicUrl: "https://xabarnavis.ai/r/public/xb_pub_a8f5f167f44f4964e6c998dee827110c",
    device: "MacBook Pro",
    browser: "Chrome 126",
    os: "macOS 14.5",
    ip: "192.168.1.45",
    maskedIp: "192.168.*.*",
    timezone: "Asia/Tashkent (UTC+5)",
    screenResolution: "2560x1600",
    userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
  },
  {
    id: "RPT-2024-002",
    publicToken: "xb_pub_b9e6g278h55g5075f7d009eff938221d",
    fileName: "musiqa_ovozi.mp3",
    fileType: "audio",
    fileSize: "8.7 MB",
    mimeType: "audio/mpeg",
    sha256: "b9e6g278h55g5075f7d009eff938221d6b8e5c2a1f4d7g3h2i9j0k1l2m3n4o5p6",
    uploadedAt: "2026-06-30 14:29:08",
    analyzedAt: "2026-06-30 14:29:38",
    userId: "user_001",
    deviceId: "dev_001",
    aiProbability: 59,
    realProbability: 41,
    manipulationScore: 55,
    riskLevel: "ortacha",
    result: "Shubhali",
    conclusionUz: "Audio faylda ovoz klonlash texnologiyasiga xos spektral anomaliyalar aniqlandi. Frekanslar taqsimotida g'ayrioddiy naqshlar mavjud.",
    modelName: "XabarnavisAudio v1.3",
    modelVersion: "1.3.2",
    explainability: "Spectral artifact 3 ta joyda, noise profile o'zgaruvchan",
    qrCodeUrl: "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://xabarnavis.ai/r/public/xb_pub_b9e6g278h55g5075f7d009eff938221d",
    publicUrl: "https://xabarnavis.ai/r/public/xb_pub_b9e6g278h55g5075f7d009eff938221d",
    device: "iPhone 15 Pro",
    browser: "Safari 17",
    os: "iOS 17.5",
    ip: "10.0.0.22",
    maskedIp: "10.0.*.*",
    timezone: "Asia/Tashkent (UTC+5)",
    screenResolution: "1290x2796",
    userAgent: "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15",
  },
  {
    id: "RPT-2024-003",
    publicToken: "xb_pub_c1d2e3f4g5h6i7j8k9l0m1n2o3p4q5r6",
    fileName: "hujjat_tahlil.pdf",
    fileType: "text",
    fileSize: "1.1 MB",
    mimeType: "application/pdf",
    sha256: "c1d2e3f4g5h6i7j8k9l0m1n2o3p4q5r6s7t8u9v0w1x2y3z4a5b6c7d8e9f0g1h2",
    uploadedAt: "2026-06-30 13:15:22",
    analyzedAt: "2026-06-30 13:15:48",
    userId: "user_001",
    deviceId: "dev_002",
    aiProbability: 34,
    realProbability: 66,
    manipulationScore: 28,
    riskLevel: "past",
    result: "Haqiqiy",
    conclusionUz: "Matn tahlili natijasiga ko'ra, ushbu hujjat asosan inson tomonidan yozilgan. AI yozim belgilari minimal darajada aniqlandi.",
    modelName: "XabarnavisText v1.8",
    modelVersion: "1.8.1",
    explainability: "Perplexity ko'rsatkichi normal, burst pattern minimal",
    qrCodeUrl: "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://xabarnavis.ai/r/public/xb_pub_c1d2e3f4g5h6i7j8k9l0m1n2o3p4q5r6",
    publicUrl: "https://xabarnavis.ai/r/public/xb_pub_c1d2e3f4g5h6i7j8k9l0m1n2o3p4q5r6",
    device: "Dell XPS 15",
    browser: "Firefox 127",
    os: "Windows 11",
    ip: "172.16.0.5",
    maskedIp: "172.16.*.*",
    timezone: "Asia/Tashkent (UTC+5)",
    screenResolution: "1920x1200",
    userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
  },
  {
    id: "RPT-2024-004",
    publicToken: "xb_pub_d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9",
    fileName: "video_klip.mp4",
    fileType: "video",
    fileSize: "128.5 MB",
    mimeType: "video/mp4",
    sha256: "d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5",
    uploadedAt: "2026-06-30 11:44:05",
    analyzedAt: "2026-06-30 11:46:30",
    userId: "user_001",
    deviceId: "dev_001",
    aiProbability: 72,
    realProbability: 28,
    manipulationScore: 68,
    riskLevel: "yuqori",
    result: "Manipulyatsiya",
    conclusionUz: "Videoda yuz almashtirishga (deepfake) xos belgilar aniqlandi. 23-47 soniya oralig'ida yuz landmarklari beqarorligi kuzatildi.",
    modelName: "XabarnavisVideo v1.1",
    modelVersion: "1.1.0",
    explainability: "Frame 340-580 oralig'ida deepfake artifakti, lip-sync nomuvofiqlik",
    qrCodeUrl: "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://xabarnavis.ai/r/public/xb_pub_d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9",
    publicUrl: "https://xabarnavis.ai/r/public/xb_pub_d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9",
    device: "MacBook Pro",
    browser: "Chrome 126",
    os: "macOS 14.5",
    ip: "192.168.1.45",
    maskedIp: "192.168.*.*",
    timezone: "Asia/Tashkent (UTC+5)",
    screenResolution: "2560x1600",
    userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
  },
];

export const mockDevices: Device[] = [
  {
    id: "dev_001",
    userId: "user_001",
    deviceName: "MacBook Pro",
    deviceType: "desktop",
    browser: "Chrome 126",
    os: "macOS 14.5",
    ipAddress: "192.168.1.45",
    maskedIp: "192.168.*.*",
    timezone: "Asia/Tashkent (UTC+5)",
    screenResolution: "2560x1600",
    firstLoginAt: "2026-05-15 09:23:11",
    lastLoginAt: "2026-06-30 14:00:00",
    lastLogoutAt: "2026-06-30 18:30:00",
    isActive: true,
    isTrusted: true,
    reportsCount: 28,
    lastFile: "shubhali_rasm_01.jpg",
  },
  {
    id: "dev_002",
    userId: "user_001",
    deviceName: "iPhone 15 Pro",
    deviceType: "mobile",
    browser: "Safari 17",
    os: "iOS 17.5",
    ipAddress: "10.0.0.22",
    maskedIp: "10.0.*.*",
    timezone: "Asia/Tashkent (UTC+5)",
    screenResolution: "1290x2796",
    firstLoginAt: "2026-06-10 16:45:00",
    lastLoginAt: "2026-06-30 11:20:00",
    lastLogoutAt: "2026-06-30 12:00:00",
    isActive: false,
    isTrusted: true,
    reportsCount: 7,
    lastFile: "musiqa_ovozi.mp3",
  },
  {
    id: "dev_003",
    userId: "user_001",
    deviceName: "Dell XPS 15",
    deviceType: "desktop",
    browser: "Firefox 127",
    os: "Windows 11",
    ipAddress: "172.16.0.5",
    maskedIp: "172.16.*.*",
    timezone: "Asia/Tashkent (UTC+5)",
    screenResolution: "1920x1200",
    firstLoginAt: "2026-06-28 08:00:00",
    lastLoginAt: "2026-06-30 08:15:00",
    lastLogoutAt: "2026-06-30 09:00:00",
    isActive: false,
    isTrusted: false,
    reportsCount: 3,
    lastFile: "hujjat_tahlil.pdf",
  },
];

export const mockSessionLogs: SessionLog[] = [
  { id: "ses_001", userId: "user_001", deviceId: "dev_001", deviceName: "MacBook Pro", loginAt: "2026-06-30 14:00:00", logoutAt: null, ipAddress: "192.168.1.45", browser: "Chrome 126", os: "macOS 14.5", status: "success", duration: "Aktiv" },
  { id: "ses_002", userId: "user_001", deviceId: "dev_002", deviceName: "iPhone 15 Pro", loginAt: "2026-06-30 11:20:00", logoutAt: "2026-06-30 12:00:00", ipAddress: "10.0.0.22", browser: "Safari 17", os: "iOS 17.5", status: "success", duration: "40 daqiqa" },
  { id: "ses_003", userId: "user_001", deviceId: "dev_003", deviceName: "Dell XPS 15", loginAt: "2026-06-30 08:15:00", logoutAt: "2026-06-30 09:00:00", ipAddress: "172.16.0.5", browser: "Firefox 127", os: "Windows 11", status: "success", duration: "45 daqiqa" },
  { id: "ses_004", userId: "user_001", deviceId: "dev_004", deviceName: "Noma'lum qurilma", loginAt: "2026-06-29 22:05:00", logoutAt: "2026-06-29 22:06:00", ipAddress: "203.0.113.1", browser: "Chrome 125", os: "Linux", status: "failed", duration: "1 daqiqa" },
];

export const mockNotifications: Notification[] = [
  { id: "n1", type: "report", title: "Yangi report tayyor", message: "shubhali_rasm_01.jpg tahlili yakunlandi. AI ehtimoli: 87%", time: "2 daqiqa oldin", read: false },
  { id: "n2", type: "danger", title: "Xavfli fayl topildi!", message: "video_klip.mp4 â€” Juda yuqori risk darajasi aniqlandi", time: "35 daqiqa oldin", read: false },
  { id: "n3", type: "device", title: "Yangi qurilmadan kirish", message: "Dell XPS 15 (172.16.0.5) qurilmasidan kirish amalga oshirildi", time: "2 soat oldin", read: false },
  { id: "n4", type: "qr", title: "QR report ochildi", message: "RPT-2024-001 public sahifasi QR orqali ko'rildi", time: "4 soat oldin", read: true },
  { id: "n5", type: "export", title: "Export yakunlandi", message: "hujjat_tahlil.pdf uchun PDF hisobot yuklandi", time: "6 soat oldin", read: true },
  { id: "n6", type: "model", title: "Model yangilandi", message: "XabarnavisVision v2.1.4 versiyasi o'rnatildi", time: "1 kun oldin", read: true },
];

export const chartData = {
  daily: [
    { kun: "Du", tekshiruv: 4 },
    { kun: "Se", tekshiruv: 7 },
    { kun: "Cho", tekshiruv: 5 },
    { kun: "Pa", tekshiruv: 10 },
    { kun: "Ju", tekshiruv: 8 },
    { kun: "Sha", tekshiruv: 3 },
    { kun: "Ya", tekshiruv: 6 },
  ],
  byType: [
    { tur: "Rasm", count: 18, color: "#00E5FF" },
    { tur: "Video", count: 5, color: "#8B5CF6" },
    { tur: "Audio", count: 12, color: "#22C55E" },
    { tur: "Matn", count: 9, color: "#F59E0B" },
  ],
  realVsFake: [
    { nom: "Haqiqiy", count: 16, color: "#22C55E" },
    { nom: "AI/Soxta", count: 28, color: "#EF4444" },
  ],
  devices: [
    { tur: "Desktop", count: 22, color: "#00E5FF" },
    { tur: "Mobile", count: 12, color: "#8B5CF6" },
    { tur: "Tablet", count: 4, color: "#F59E0B" },
  ],
};

export const dashboardStats = {
  totalChecks: 44,
  dangerousFound: 28,
  avgRealScore: 41,
  avgAiScore: 59,
  last24h: 6,
  todayUploads: 3,
  topFileType: "Rasm",
  reportExports: 12,
  qrOpened: 8,
  activeDevices: 1,
};



