/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  assetPrefix: process.env.NODE_ENV === 'production' ? '' : '',
  typescript: {
    ignoreBuildErrors: true,
  },
  output: 'standalone',
  images: {
    unoptimized: true,
    remotePatterns: [
        {
            protocol: 'https',
            hostname: 'rapidstream.ru',
            pathname: '/picture/**',
        },
    ],
},
  async headers() {
    return [
      {
        source: "/picture/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "no-store, max-age=0",
          },
        ],
      },
      {
        source: "/(.*)",
        headers: [
          {
            key: "X-Forwarded-Host",
            value: "rapidstream.ru",
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;