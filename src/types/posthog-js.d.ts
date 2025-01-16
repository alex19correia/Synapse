declare module 'posthog-js' {
  interface PostHog {
    init(apiKey: string, options?: any): void;
    capture(event: string, properties?: any): void;
    identify(distinctId: string, properties?: any): void;
    reset(): void;
    opt_in_capturing(): void;
    opt_out_capturing(): void;
  }

  const posthog: PostHog;
  export default posthog;
} 