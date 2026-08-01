import { NextRequest, NextResponse } from "next/server";

const locales = ["uz", "en", "ru"] as const;

function isPublicAsset(pathname: string) {
  return (
    pathname.startsWith("/_next") ||
    pathname.startsWith("/api") ||
    pathname.startsWith("/health") ||
    pathname.includes(".")
  );
}

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (isPublicAsset(pathname)) {
    return NextResponse.next();
  }

  if (pathname === "/") {
    return NextResponse.redirect(new URL("/uz", request.url));
  }

  const [maybeLocale, ...rest] = pathname.replace(/^\/+/, "").split("/");

  if (locales.includes(maybeLocale as (typeof locales)[number])) {
    if (rest.length === 0 || rest[0] === "") {
      return NextResponse.next();
    }

    const rewritten = request.nextUrl.clone();
    rewritten.pathname = rest[0] === "register" ? "/login" : `/${rest.join("/")}`;
    if (rest[0] === "register") {
      rewritten.searchParams.set("mode", "register");
    }
    return NextResponse.rewrite(rewritten);
  }

  if (pathname === "/register") {
    const rewritten = request.nextUrl.clone();
    rewritten.pathname = "/login";
    rewritten.searchParams.set("mode", "register");
    return NextResponse.rewrite(rewritten);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};



