/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  async rewrites() {
    return [{
      source: '/api/eye/:path*',
      destination: 'https://eye-api.meetarash.ir/:path*',
    }];
  },
  // Docker/CI already run `npm test`; skipping ESLint here cuts minutes off `next build`.
  eslint: { ignoreDuringBuilds: true },
};

module.exports = nextConfig;
