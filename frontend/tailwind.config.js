/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'uw-red': '#C5050C',
        'uw-red-dark': '#9B0000',
        'uw-white': '#FFFFFF',
      },
    },
  },
  plugins: [],
}

