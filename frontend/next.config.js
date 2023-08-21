/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['example.com', 'characterai.io','upload.wikimedia.org'],
  },
  webpack: (config) => {
    config.module.rules.push({
      test: /\.svg$/,
      use: ["@svgr/webpack"],
    });
    return config;
  },
};

module.exports = nextConfig;
