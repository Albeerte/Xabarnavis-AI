export const locales = ["uz", "en", "ru"] as const;
export type Locale = (typeof locales)[number];

export function isLocale(value: string | undefined): value is Locale {
  return !!value && locales.includes(value as Locale);
}

export function getLocale(value: string | undefined): Locale {
  return isLocale(value) ? value : "uz";
}

export const dictionaries = {
  uz: {
    nav: {
      home: "Bosh sahifa",
      analyze: "Tekshiruv",
      reports: "Hisobotlar",
      pricing: "Narxlar",
      api: "API",
      contact: "Aloqa",
      login: "Kirish",
      register: "Ro'yxatdan o'tish",
    },
    home: {
      badge: "AI media haqiqiylik laboratoriyasi",
      title: "XABARNAVIS AI",
      subtitle: "media dalillarni rasmiy uslubda tekshiradi",
      description:
        "Rasm, audio, video va matn bo'yicha AI, deepfake, tahrir va manipulyatsiya izlarini aniqlang. Har bir tekshiruv foydalanuvchi profiliga bog'lanadi va professional hisobotga aylanadi.",
      start: "Tekshiruvni boshlash",
      dashboard: "Dashboardga kirish",
      modules: "Tahlil modullari",
      process: "Qanday ishlaydi?",
      report: "Har bir analiz bitta rasmiy hisobotga aylanadi",
    },
    status: {
      authentic: "Haqiqiy",
      suspicious: "Shubhali",
      fake: "Soxta",
      aiGenerated: "AI yaratilgan",
      manipulated: "Manipulyatsiya qilingan",
      unknown: "Noma'lum",
    },
  },
  en: {
    nav: {
      home: "Home",
      analyze: "Analyze",
      reports: "Reports",
      pricing: "Pricing",
      api: "API",
      contact: "Contact",
      login: "Login",
      register: "Register",
    },
    home: {
      badge: "AI media authenticity laboratory",
      title: "XABARNAVIS AI",
      subtitle: "verifies media evidence with official-grade reports",
      description:
        "Detect AI traces, deepfakes, edits, and manipulation in images, audio, video, and text. Each analysis is linked to the user profile and becomes a professional report.",
      start: "Start analysis",
      dashboard: "Open dashboard",
      modules: "Analysis modules",
      process: "How it works",
      report: "Every analysis becomes one official report",
    },
    status: {
      authentic: "Authentic",
      suspicious: "Suspicious",
      fake: "Fake",
      aiGenerated: "AI-generated",
      manipulated: "Manipulated",
      unknown: "Unknown",
    },
  },
  ru: {
    nav: {
      home: "Ð“Ð»Ð°Ð²Ð½Ð°Ñ",
      analyze: "ÐÐ½Ð°Ð»Ð¸Ð·",
      reports: "ÐžÑ‚Ñ‡Ñ‘Ñ‚Ñ‹",
      pricing: "Ð¦ÐµÐ½Ñ‹",
      api: "API",
      contact: "ÐšÐ¾Ð½Ñ‚Ð°ÐºÑ‚Ñ‹",
      login: "Ð’Ð¾Ð¹Ñ‚Ð¸",
      register: "Ð ÐµÐ³Ð¸ÑÑ‚Ñ€Ð°Ñ†Ð¸Ñ",
    },
    home: {
      badge: "Ð›Ð°Ð±Ð¾Ñ€Ð°Ñ‚Ð¾Ñ€Ð¸Ñ Ð¿Ñ€Ð¾Ð²ÐµÑ€ÐºÐ¸ Ð¼ÐµÐ´Ð¸Ð° Ñ Ð˜Ð˜",
      title: "XABARNAVIS AI",
      subtitle: "Ð¿Ñ€Ð¾Ð²ÐµÑ€ÑÐµÑ‚ Ð¼ÐµÐ´Ð¸Ð°-Ð´Ð¾ÐºÐ°Ð·Ð°Ñ‚ÐµÐ»ÑŒÑÑ‚Ð²Ð° Ð² Ð¾Ñ„Ð¸Ñ†Ð¸Ð°Ð»ÑŒÐ½Ð¾Ð¼ Ñ„Ð¾Ñ€Ð¼Ð°Ñ‚Ðµ",
      description:
        "ÐžÐ¿Ñ€ÐµÐ´ÐµÐ»ÑÐ¹Ñ‚Ðµ ÑÐ»ÐµÐ´Ñ‹ Ð˜Ð˜, Ð´Ð¸Ð¿Ñ„ÐµÐ¹ÐºÐ¸, Ñ€ÐµÐ´Ð°ÐºÑ‚Ð¸Ñ€Ð¾Ð²Ð°Ð½Ð¸Ðµ Ð¸ Ð¼Ð°Ð½Ð¸Ð¿ÑƒÐ»ÑÑ†Ð¸Ð¸ Ð² Ð¸Ð·Ð¾Ð±Ñ€Ð°Ð¶ÐµÐ½Ð¸ÑÑ…, Ð°ÑƒÐ´Ð¸Ð¾, Ð²Ð¸Ð´ÐµÐ¾ Ð¸ Ñ‚ÐµÐºÑÑ‚Ðµ. ÐšÐ°Ð¶Ð´Ñ‹Ð¹ Ð°Ð½Ð°Ð»Ð¸Ð· ÑÐ²ÑÐ·Ñ‹Ð²Ð°ÐµÑ‚ÑÑ Ñ Ð¿Ñ€Ð¾Ñ„Ð¸Ð»ÐµÐ¼ Ð¿Ð¾Ð»ÑŒÐ·Ð¾Ð²Ð°Ñ‚ÐµÐ»Ñ Ð¸ Ð¿Ñ€ÐµÐ²Ñ€Ð°Ñ‰Ð°ÐµÑ‚ÑÑ Ð² Ð¿Ñ€Ð¾Ñ„ÐµÑÑÐ¸Ð¾Ð½Ð°Ð»ÑŒÐ½Ñ‹Ð¹ Ð¾Ñ‚Ñ‡Ñ‘Ñ‚.",
      start: "ÐÐ°Ñ‡Ð°Ñ‚ÑŒ Ð°Ð½Ð°Ð»Ð¸Ð·",
      dashboard: "ÐžÑ‚ÐºÑ€Ñ‹Ñ‚ÑŒ Ð¿Ð°Ð½ÐµÐ»ÑŒ",
      modules: "ÐœÐ¾Ð´ÑƒÐ»Ð¸ Ð°Ð½Ð°Ð»Ð¸Ð·Ð°",
      process: "ÐšÐ°Ðº ÑÑ‚Ð¾ Ñ€Ð°Ð±Ð¾Ñ‚Ð°ÐµÑ‚",
      report: "ÐšÐ°Ð¶Ð´Ñ‹Ð¹ Ð°Ð½Ð°Ð»Ð¸Ð· ÑÑ‚Ð°Ð½Ð¾Ð²Ð¸Ñ‚ÑÑ Ð¾Ñ„Ð¸Ñ†Ð¸Ð°Ð»ÑŒÐ½Ñ‹Ð¼ Ð¾Ñ‚Ñ‡Ñ‘Ñ‚Ð¾Ð¼",
    },
    status: {
      authentic: "ÐŸÐ¾Ð´Ð»Ð¸Ð½Ð½Ñ‹Ð¹",
      suspicious: "ÐŸÐ¾Ð´Ð¾Ð·Ñ€Ð¸Ñ‚ÐµÐ»ÑŒÐ½Ñ‹Ð¹",
      fake: "Ð¤ÐµÐ¹Ðº",
      aiGenerated: "Ð¡Ð¾Ð·Ð´Ð°Ð½Ð¾ Ð˜Ð˜",
      manipulated: "Ð˜Ð·Ð¼ÐµÐ½ÐµÐ½Ð¾",
      unknown: "ÐÐµÐ¸Ð·Ð²ÐµÑÑ‚Ð½Ð¾",
    },
  },
} as const;

export function switchLocalePath(pathname: string, nextLocale: Locale) {
  const parts = pathname.split("/").filter(Boolean);
  if (isLocale(parts[0])) {
    parts[0] = nextLocale;
  } else {
    parts.unshift(nextLocale);
  }
  return `/${parts.join("/")}`;
}



