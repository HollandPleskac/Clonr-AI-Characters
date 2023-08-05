/** @type {import('tailwindcss').Config} */
import preline from 'preline/plugin.js';

module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",

    // Or if using `src` directory:
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    'node_modules/preline/dist/*.js'
  ],
  theme: {
    extend: {
      fontFamily: {
        'fabada': ["Fabada", "sans-serif"]
      }
    },
  },
  plugins: [
    require("@tailwindcss/forms"),
    preline
  ],
}

