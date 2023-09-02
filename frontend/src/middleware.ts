export { default } from "next-auth/middleware";

export const config = {
  matcher: ['/nothing-here-yet'],
  // matcher: ["/((?!register|api|login).*)"],
};