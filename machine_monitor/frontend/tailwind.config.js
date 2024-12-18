/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'ocean-blue': {
          '50': '#e6f1ff',
          '100': '#b3d7ff',
          '200': '#80bdff',
          '300': '#4da3ff',
          '400': '#1a89ff',
          '500': '#0070e6',
          '600': '#0059b3',
          '700': '#004080',
          '800': '#00264d',
          '900': '#000d1a'
        },
        'glass': {
          light: 'rgba(255, 255, 255, 0.1)',
          dark: 'rgba(0, 0, 0, 0.1)',
        }
      },
      backgroundImage: {
        'gradient-ocean': 'linear-gradient(135deg, #0070e6 0%, #004080 50%, #000d1a 100%)',
      },
      boxShadow: {
        'glass': '0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08)',
        'glass-lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
      },
      backdropBlur: {
        'xs': '2px',
      },
      animation: {
        'pulse-slow': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography')
  ],
};
