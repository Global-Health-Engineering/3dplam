import { defineConfig } from 'astro/config';

// Deployed as a GitHub Pages project site at
// https://global-health-engineering.github.io/3dplam — `base` MUST match
// the repo name or every absolute asset path (images, CSS, the brand SVG)
// 404s on the deployed site while working fine in local dev.
export default defineConfig({
  site: 'https://global-health-engineering.github.io',
  base: '/3dplam',
  build: { assets: '_astro' },
});
