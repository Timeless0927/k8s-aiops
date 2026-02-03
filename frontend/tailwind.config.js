/** @type {import('tailwindcss').Config} */
export default {
    darkMode: 'class',
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Pro Max Theme - Clean, Professional, Slate-based
                background: "#ffffff", // Pure White
                surface: "#f8fafc",    // Slate-50

                // Primary Action Color (Indigo-600)
                primary: {
                    DEFAULT: "#4f46e5",
                    hover: "#4338ca",
                    light: "#e0e7ff", // Indigo-100
                    soft: "#eff0ff", // Used for Qwen-style bubbles
                },

                // Semantic Colors
                secondary: "#10b981",  // Emerald-500
                danger: "#f43f5e",     // Rose-500 (Softer than red)
                warning: "#f59e0b",    // Amber-500
                info: "#3b82f6",       // Blue-500

                // Typography (Slate Scale) -> Foreground
                foreground: {
                    DEFAULT: "#0f172a",   // Slate-900 (Primary Text)
                    secondary: "#475569", // Slate-600
                    muted: "#94a3b8",     // Slate-400
                    inverted: "#ffffff",
                },

                // Borders
                border: "#e2e8f0",      // Slate-200
            },
            fontFamily: {
                mono: ['"JetBrains Mono"', '"Fira Code"', 'monospace'],
                sans: ['Inter', 'sans-serif'],
            },
            boxShadow: {
                'sm': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
                'md': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
                'lg': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
                'xl': '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
                'float': '0 20px 40px -4px rgba(0, 0, 0, 0.08)', // High-end float
                'input': '0 0 0 1px #e2e8f0, 0 2px 6px 0 rgba(0,0,0,0.05)',
                'input-focus': '0 0 0 2px #4f46e5, 0 4px 12px 0 rgba(79, 70, 229, 0.1)',
            },
            animation: {
                'fade-in': 'fadeIn 0.3s ease-out',
                'slide-up': 'slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                slideUp: {
                    '0%': { transform: 'translateY(10px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                }
            }
        },
    },
    plugins: [
        require('@tailwindcss/typography'),
    ],
}
