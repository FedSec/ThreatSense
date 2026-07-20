/** @type {import('next').NextConfig} */
const path = require("path");

function resolveApiInternal() {
  for (const candidate of [
    process.env.API_INTERNAL_URL,
    process.env.NEXT_PUBLIC_API_BASE,
    "http://localhost:8000",
  ]) {
    if (candidate && /^https?:\/\//i.test(candidate)) {
      return candidate.replace(/\/$/, "");
    }
  }
  return "http://localhost:8000";
}

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  webpack: (config) => {
    config.resolve.alias["@"] = path.resolve(__dirname, "src");
    return config;
  },
  async rewrites() {
    // Absolute NEXT_PUBLIC_API_BASE → browser talks to API directly (no proxy).
    if (/^https?:\/\//i.test(process.env.NEXT_PUBLIC_API_BASE || "")) {
      return [];
    }
    const apiInternal = resolveApiInternal();
    return [
      {
        source: "/api/:path*",
        destination: `${apiInternal}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
