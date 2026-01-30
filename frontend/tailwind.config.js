/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Futuristic / Hacker Palettes (Cyberpunk-ish but clean)
                background: "#09090b", // zinc-950
                surface: "#18181b",    // zinc-900
                primary: "#3b82f6",    // blue-500
                secondary: "#10b981",  // emerald-500
                danger: "#ef4444",     // red-500
                warning: "#f59e0b",    // amber-500
                text: "#e4e4e7",       // zinc-200
                muted: "#71717a",      // zinc-500
            },
            fontFamily: {
                mono: ['"JetBrains Mono"', '"Fira Code"', 'monospace'], // Hacker style
                sans: ['Inter', 'sans-serif'],
            }
        },
    },
    plugins: [],
}
