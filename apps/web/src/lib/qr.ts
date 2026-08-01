export function qrCodeUrlFor(data: string, size = 180) {
  return `https://api.qrserver.com/v1/create-qr-code/?size=${size}x${size}&data=${encodeURIComponent(data)}`;
}

export function appOrigin() {
  if (typeof window !== "undefined") {
    return window.location.origin;
  }

  return process.env.NEXT_PUBLIC_APP_URL || "http://127.0.0.1:3000";
}

export function localeFromPathname(pathname: string) {
  const locale = pathname.split("/").filter(Boolean)[0];
  return locale === "en" || locale === "ru" || locale === "uz" ? locale : "uz";
}

export function reportPublicPath(reportId: string | number, locale = "uz") {
  const prefix = locale === "uz" ? "/uz" : `/${locale}`;
  return `${prefix}/report/${reportId}`;
}

export function reportPublicUrl(reportId: string | number, locale = "uz") {
  return `${appOrigin()}${reportPublicPath(reportId, locale)}`;
}

export function reportQrCodeUrl(reportId: string | number, locale = "uz", size = 180) {
  return qrCodeUrlFor(reportPublicUrl(reportId, locale), size);
}



