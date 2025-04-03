import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    serverActions: {
      bodySizeLimit: '2mb',
    },
  },
  reactStrictMode: true,
  typescript: {
    ignoreBuildErrors: false, // true only if you're debugging types
  },
  eslint: {
    ignoreDuringBuilds: true, // optional
  },
};

export default nextConfig;
