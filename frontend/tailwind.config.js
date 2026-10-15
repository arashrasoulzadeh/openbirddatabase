/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        vazir: ['Vazirmatn', 'Noto Nastaliq Urdu', 'Noto Sans Arabic', 'system-ui', 'sans-serif'],
      },
      colors: {
        brand: {
          50: '#f1f7f3', 100: '#dcebe1', 200: '#b9d7c4', 300: '#8dbb9f', 400: '#5f9c79',
          500: '#3f8160', 600: '#2f664b', 700: '#27523d', 800: '#214133', 900: '#1b362b',
        },
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
      },
    },
  },
  plugins: [],
}