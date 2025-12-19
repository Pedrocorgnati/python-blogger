/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#0f172a',
        smoke: '#0b1324',
        haze: '#eef2ff',
        glow: '#f59e0b',
        mint: '#10b981',
        coral: '#f97316'
      },
      fontFamily: {
        sans: ['"Space Grotesk"', 'ui-sans-serif', 'system-ui'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'SFMono-Regular']
      },
      boxShadow: {
        soft: '0 12px 40px rgba(15, 23, 42, 0.12)'
      }
    }
  },
  plugins: []
};
