/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  // Docker/CI already run `npm test`; skipping ESLint here cuts minutes off `next build`.
  eslint: { ignoreDuringBuilds: true },
};

module.exports = nextConfig;
