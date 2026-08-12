/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    // IMPORTANT: this rewrite runs server-side, inside whatever process is
    // running `next start`/`next dev`. Under docker-compose, that's the
    // frontend container - and "localhost" from inside that container means
    // itself, not the backend container. So this deliberately does NOT reuse
    // NEXT_PUBLIC_API_URL (which is for the browser, and correctly points at
    // the host-exposed http://localhost:8000). BACKEND_INTERNAL_URL is a
    // separate, server-only var set to http://backend:8000 in
    // docker-compose.yml, and defaults to localhost for non-Docker local dev.
    const backendUrl = process.env.BACKEND_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};
module.exports = nextConfig;
