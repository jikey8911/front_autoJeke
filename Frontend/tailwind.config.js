/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./node_modules/@jikey8911/jeikei-ui/dist/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        neo: {
          cyan: "#00ffe0",
          magenta: "#ff007f",
          amber: "#ffb000",
          bg: "#020202"
        }
      }
    }
  },
  plugins: [],
}