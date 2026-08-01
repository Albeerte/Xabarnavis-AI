import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    proxyClientMaxBodySize: 100 * 1024 * 1024,
  },
  async rewrites() {
    const apiUrl = process.env.XABARNAVIS_API_URL ?? "http://127.0.0.1:8001";

    return [
      {
        source: "/api/:path*",
        destination: `${apiUrl}/api/:path*`,
      },
      {
        source: "/health",
        destination: `${apiUrl}/health`,
      },
    ];
  },
};

export default nextConfig;

