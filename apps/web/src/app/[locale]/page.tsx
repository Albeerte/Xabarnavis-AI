import type { Metadata } from "next";
import Home from "../page";
import { getLocale, dictionaries } from "@/lib/i18n";

export async function generateMetadata({ params }: { params: Promise<{ locale: string }> }): Promise<Metadata> {
  const { locale: rawLocale } = await params;
  const locale = getLocale(rawLocale);
  const t = dictionaries[locale];

  return {
    metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || "http://127.0.0.1:3000"),
    title: `${t.home.title} | ${t.nav.analyze}`,
    description: t.home.description,
    alternates: {
      canonical: `/${locale}`,
      languages: {
        uz: "/uz",
        en: "/en",
        ru: "/ru",
      },
    },
    openGraph: {
      title: `${t.home.title} | AI Forensics`,
      description: t.home.description,
      images: ["/xabarnavis-logo.png"],
    },
  };
}

export default function LocaleHome() {
  return <Home />;
}



