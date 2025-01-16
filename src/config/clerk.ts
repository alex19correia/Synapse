import { authMiddleware } from '@clerk/nextjs';

export const clerkConfig = {
  signInUrl: "/sign-in",
  signUpUrl: "/sign-up",
  afterSignInUrl: "/",
  afterSignUpUrl: "/",
  publishableKey: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY,
  secretKey: process.env.CLERK_SECRET_KEY,
  publicRoutes: [
    '/',
    '/login',
    '/signup',
    '/api/health',
    '/api/trpc(.*)',
    '/api/webhook',
    '/_next/static/(.*)',
    '/_next/image(.*)',
    '/favicon.ico',
  ],
};

export const middleware = authMiddleware({
  publicRoutes: clerkConfig.publicRoutes,
});

// Configure middleware handler
export const config = {
  matcher: ['/((?!.+\\.[\\w]+$|_next).*)', '/', '/(api|trpc)(.*)'],
}; 