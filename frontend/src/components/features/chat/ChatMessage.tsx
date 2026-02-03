import React from 'react';
import { Shield, User } from 'lucide-react';
import Markdown from 'react-markdown';
import { ErrorBoundary } from '../../common/ErrorBoundary';

interface Message {
    role: string;
    content: string;
}

interface ChatMessageProps {
    msg: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ msg }) => {
    const isUser = msg.role === 'user';

    return (
        <div className={`flex gap-4 max-w-4xl mx-auto animate-in slide-in-from-bottom-2 duration-300 ${isUser ? 'ml-auto flex-row-reverse' : ''}`}>
            {/* Avatar */}
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 shadow-sm ${isUser ? 'bg-primary text-white' : 'bg-white border border-gray-200 text-primary'}`}>
                {isUser ? <User size={16} /> : <Shield size={16} />}
            </div>

            {/* Message Body */}
            <div className={`space-y-1 max-w-[85%] ${isUser ? 'text-right' : 'text-left'}`}>
                <div className="text-xs font-semibold text-gray-500 mb-1 ml-1">{isUser ? '您' : '智能助手'}</div>

                <div className={`text-sm leading-relaxed inline-block text-left whitespace-pre-wrap break-words
                    ${isUser
                        ? 'p-3.5 px-5 bg-[#eff0ff] text-indigo-950 rounded-[20px] rounded-br-[4px]' // User: Soft Indigo Pill
                        : 'p-0 text-gray-800' // Agent: Clean Text (No bubble)
                    }`}
                >
                    <div className={`prose max-w-none prose-p:my-0 prose-sm ${isUser ? '' : 'prose-gray'}`}>
                        <ErrorBoundary>
                            <Markdown
                                components={{
                                    a: ({ node, ...props }) => (
                                        <a
                                            {...props}
                                            className={`font-semibold hover:underline break-all ${isUser ? 'text-indigo-700' : 'text-primary'}`}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                        />
                                    ),
                                    code: ({ node, ...props }) => {
                                        const match = /language-(\w+)/.exec(props.className || '');
                                        // Inline code
                                        if (!match) {
                                            return <code {...props} className={`px-1.5 py-0.5 rounded font-mono text-xs ${isUser ? 'bg-indigo-100 text-indigo-800' : 'bg-gray-100 text-gray-800 border border-gray-200'}`} />
                                        }
                                        // Block code is handled by pre
                                        return <code {...props} />
                                    },
                                    pre: ({ node, ...props }) => (
                                        <pre
                                            {...props}
                                            className={`p-3 rounded-xl overflow-x-auto my-3 text-xs font-mono border ${isUser ? 'bg-white/50 border-indigo-100' : 'bg-gray-50 border-gray-100'}`}
                                        />
                                    )
                                }}
                            >
                                {String(msg.content)}
                            </Markdown>
                        </ErrorBoundary>
                    </div>
                </div>
            </div>
        </div>
    );
};
