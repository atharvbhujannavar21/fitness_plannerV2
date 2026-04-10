/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        ink: '#090909',
        panel: '#111214',
        muted: '#868686',
        ember: '#ff8c00',
        sand: '#ffd8b0'
      },
      boxShadow: {
        glow: '0 20px 60px rgba(0, 0, 0, 0.35)'
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        body: ['"Manrope"', 'sans-serif']
      }
    }
  },
  plugins: []
};
