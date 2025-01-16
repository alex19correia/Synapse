declare module "@clerk/nextjs/server" {
  export interface User {
    id: string;
    getToken(): Promise<string>;
    factors?: Factor[];
  }

  export interface Auth {
    userId: string | null;
    getToken(): Promise<string>;
  }

  export interface ClerkClient {
    sessions: {
      getToken(userId: string, options?: any): Promise<string>;
    };
  }

  export const clerkClient: () => Promise<ClerkClient>;
  export function auth(): Promise<Auth>;
  export function currentUser(): Promise<User | null>;
}

declare module "@clerk/nextjs" {
  export interface User {
    id: string;
    getToken(): Promise<string>;
  }

  export function auth(): {
    userId: string | null;
    getToken(): Promise<string>;
  };

  export function authMiddleware(options?: {
    beforeAuth?: (req: import("next/server").NextRequest) => Promise<import("next/server").NextResponse | undefined>;
    publicRoutes?: string[];
  }): (
    req: import("next/server").NextRequest
  ) => Promise<import("next/server").NextResponse>;

  // UI Components
  export const SignIn: React.ComponentType<{
    path?: string;
    routing?: "path" | "hash" | "virtual";
    signUpUrl?: string;
    redirectUrl?: string;
    appearance?: {
      elements?: {
        rootBox?: string;
        card?: string;
      };
    };
  }>;

  export const SignUp: React.ComponentType<{
    path?: string;
    routing?: "path" | "hash" | "virtual";
    signInUrl?: string;
    redirectUrl?: string;
    appearance?: {
      elements?: {
        rootBox?: string;
        card?: string;
      };
    };
  }>;

  export const ClerkProvider: React.ComponentType<{
    children: React.ReactNode;
    publishableKey?: string;
    signInUrl?: string;
    signUpUrl?: string;
    afterSignInUrl?: string;
    afterSignUpUrl?: string;
  }>;
} 