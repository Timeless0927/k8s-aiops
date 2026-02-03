import React from 'react';
import { Send, Terminal } from 'lucide-react';

interface ChatInputProps {
    input: string;
    setInput: (input: string) => void;
    handleSend: () => void;
    status: string;
}

export const ChatInput: React.FC<ChatInputProps> = ({ input, setInput, handleSend, status }) => {
    return (
        <div className="absolute bottom-10 left-0 w-full z-40 px-8 flex justify-center pointer-events-none">
            <div className="w-full max-w-4xl transform transition-all duration-500 ease-out animate-slide-up pointer-events-auto">
                <div className="relative group">
                    <div className="absolute -inset-1 bg-gradient-to-r from-primary/30 to-indigo-500/30 rounded-[32px] blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
                    <div className="relative bg-white/80 backdrop-blur-xl rounded-[28px] shadow-float border border-white/50 p-2 flex items-center gap-3 transition-all ring-1 ring-black/5 focus-within:ring-primary/50 focus-within:shadow-2xl">

                        {/* Command Icon */}
                        <div className="pl-4 text-slate-400 group-focus-within:text-primary transition-colors duration-300">
                            <Terminal size={22} strokeWidth={1.5} />
                        </div>

                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                            placeholder="描述问题或执行命令..."
                            className="flex-1 bg-transparent border-none focus:ring-0 py-4 text-[15px] text-slate-800 placeholder:text-slate-400 font-medium"
                            disabled={status === 'streaming'}
                            autoFocus
                        />

                        <div className="pr-2 flex items-center gap-2">
                            {input.length > 0 && (
                                <span className="hidden sm:inline-block text-[10px] font-mono text-slate-400 bg-slate-100 px-2 py-1 rounded border border-slate-200">
                                    发送
                                </span>
                            )}
                            <button
                                onClick={handleSend}
                                disabled={!input.trim() || status === 'streaming'}
                                className={`
                                p-3 rounded-2xl transition-all duration-300 transform
                                ${input.trim() && status !== 'streaming'
                                        ? 'bg-primary text-white hover:bg-primary-hover shadow-lg hover:shadow-primary/30 hover:scale-105 active:scale-95'
                                        : 'bg-slate-100 text-slate-300 cursor-not-allowed'}
                            `}
                            >
                                <Send size={18} strokeWidth={2} className={input.trim() ? 'ml-0.5' : ''} />
                            </button>
                        </div>
                    </div>
                </div>

                <div className="text-[10px] text-slate-400 mt-4 text-center font-medium tracking-wide opacity-80 select-none">
                    AI 可能会犯错。请独立核查重要信息。
                </div>
            </div>
        </div>
    );
};
