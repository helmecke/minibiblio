import { auth } from "@/lib/auth";
import createIntlMiddleware from "next-intl/middleware";
import { NextResponse } from "next/server";
import { locales, defaultLocale } from "./i18n/config";

const intlMiddleware = createIntlMiddleware({
  locales,
  defaultLocale,
  localePrefix: "always",
});

export default auth((req) => {
  const { pathname } = req.nextUrl;

  // Skip API routes and static files
  if (
    pathname.startsWith("/api") ||
    pathname.startsWith("/_next") ||
    pathname.includes(".")
  ) {
    return NextResponse.next();
  }

  // Run i18n middleware first
  const response = intlMiddleware(req);

  // Check if user is logged in
  const isLoggedIn = !!req.auth;

  // Extract locale from pathname (e.g., /en/admin -> en)
  const pathnameLocale = locales.find(
    (locale) => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
  );
  const pathWithoutLocale = pathnameLocale
    ? pathname.replace(`/${pathnameLocale}`, "") || "/"
    : pathname;

  const isOnAdmin = pathWithoutLocale.startsWith("/admin");
  const isOnLogin = pathWithoutLocale === "/login";

  // Redirect to login if accessing admin without auth
  if (isOnAdmin && !isLoggedIn) {
    const locale = pathnameLocale || defaultLocale;
    return NextResponse.redirect(new URL(`/${locale}/login`, req.url));
  }

  // Redirect to admin if already logged in and on login page
  if (isOnLogin && isLoggedIn) {
    const locale = pathnameLocale || defaultLocale;
    return NextResponse.redirect(new URL(`/${locale}/admin`, req.url));
  }

  return response;
});

export const config = {
  matcher: ["/((?!api|_next|.*\\..*).*)"],
};
