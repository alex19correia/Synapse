/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['img.clerk.com'],
  },
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self' https://*.clerk.accounts.dev",
              "script-src 'self' 'unsafe-eval' 'unsafe-inline' https://*.clerk.accounts.dev https://clerk.casual-sheepdog-76.accounts.dev https://va.vercel-scripts.com",
              "worker-src 'self' blob: https://*.clerk.accounts.dev",
              "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://p.typekit.net",
              "img-src 'self' data: https://img.clerk.com https://*.clerk.accounts.dev",
              "font-src 'self' https://fonts.gstatic.com data:",
              "connect-src 'self' https://*.clerk.accounts.dev wss://ws.clerk.accounts.dev https://clerk.casual-sheepdog-76.accounts.dev",
              "frame-src 'self' https://*.clerk.accounts.dev https://clerk.casual-sheepdog-76.accounts.dev",
              "frame-ancestors 'none'",
              "media-src 'self'",
              "object-src 'none'"
            ].join('; ')
          },
          {
            key: 'Content-Type',
            value: 'text/html; charset=utf-8'
          },
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable'
          }
        ],
      },
      {
        source: '/_next/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable'
          },
          {
            key: 'Content-Type',
            value: 'application/javascript; charset=utf-8'
          }
        ]
      },
      {
        source: '/api/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'no-store, must-revalidate'
          }
        ]
      }
    ]
  },
  webpack: (config, { dev, isServer }) => {
    // Otimizações para produção
    if (!dev && !isServer) {
      Object.assign(config.optimization.splitChunks.cacheGroups, {
        // Separar vendors em chunks menores
        vendors: {
          test: /[\\/]node_modules[\\/]/,
          name(module) {
            const match = module.context.match(
              /[\\/]node_modules[\\/](.*?)([\\/]|$)/
            );
            return match ? `vendor.${match[1].replace('@', '')}` : 'vendor';
          },
          priority: 20,
        },
      });
    }

    // Ignorar avisos do Edge Runtime para o Clerk
    if (!dev) {
      config.ignoreWarnings = [
        { module: /node_modules\/scheduler/ },
        { module: /node_modules\/@clerk/ }
      ];
    }

    return config;
  },
  experimental: {
    optimizePackageImports: ['@clerk/nextjs'],
  },
}

module.exports = nextConfig 