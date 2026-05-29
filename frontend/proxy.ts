import { NextResponse, type NextRequest } from "next/server";

const protectedRoutes = [
  "/dashboard",
  "/buildings",
  "/rooms",
  "/tenants",
  "/contracts",
  "/invoices",
  "/payments",
  "/expenses",
];

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const hasSession = request.cookies.has("access_token");
  const isProtected = protectedRoutes.some((route) => pathname.startsWith(route));

  if (isProtected && !hasSession) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (pathname === "/login" && hasSession) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/buildings/:path*",
    "/rooms/:path*",
    "/tenants/:path*",
    "/contracts/:path*",
    "/invoices/:path*",
    "/payments/:path*",
    "/expenses/:path*",
    "/login",
  ],
};
