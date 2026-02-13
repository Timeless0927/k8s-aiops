import React, { useRef, useEffect } from 'react';
import { Shield, Loader2 } from 'lucide-react';
import { ChatMessage } from './ChatMessage';
import { ThinkingIndicator } from './ThinkingIndicator';
import Markdown from 'react-markdown';
import { ErrorBoundary } from '../../common/ErrorBoundary';

interface ChatAreaProps {
    messages: any[];
    status: string;
    currentTool: any;
    streamingContent: string;
}

export const ChatArea: React.FC<ChatAreaProps> = ({ messages, status, currentTool, streamingContent }) => {
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }

    useEffect(() => {
        scrollToBottom();
    }, [messages, streamingContent, currentTool]);

    // Helper to group consecutive thought messages
    const groupedMessages = React.useMemo(() => {
        if (!messages.length) return [];

        const res: any[] = [];
        let lastMsg: any = null;

        // Filter out tools first so consecutive thoughts (separated by tools) merge together
        const visibleMessages = messages.filter(m => m.role !== 'tool');

        for (const msg of visibleMessages) {
            // Check if we should merge with previous thought
            if (lastMsg && lastMsg.role === 'assistant' && lastMsg.isThought && msg.role === 'assistant' && msg.isThought) {
                lastMsg.content += "\n\n" + msg.content;
            } else {
                // If it's a new message, push it
                // We clone it to avoid mutating original state if we modify content
                const newMsg = { ...msg };
                res.push(newMsg);
                lastMsg = newMsg;
            }
        }
        return res;
    }, [messages]);

    return (
        <div className="flex-1 overflow-y-auto px-8 py-10 pb-40 scroll-smooth">
            {messages.length === 0 && (
                <div className="flex flex-col items-center justify-center h-[60vh] text-center max-w-lg mx-auto space-y-6">
                    <div className="w-16 h-16 bg-white rounded-2xl shadow-sm flex items-center justify-center text-primary mb-4 p-4 border border-gray-100">
                        <Shield size={32} />
                    </div>
                    <h2 className="text-xl font-bold text-gray-900">今天有什么可以帮您？</h2>
                    <p className="text-gray-500">
                        我是您的 K8s 智能助手。我可以帮您诊断故障、查询日志并监控集群健康。
                    </p>
                    <div className="grid grid-cols-2 gap-3 w-full text-sm">
                        <div className="p-3 bg-white border border-gray-200 rounded-lg shadow-sm hover:border-primary/50 cursor-pointer transition-colors text-left">
                            查看活跃告警
                        </div>
                        <div className="p-3 bg-white border border-gray-200 rounded-lg shadow-sm hover:border-primary/50 cursor-pointer transition-colors text-left">
                            检查 Pod 状态
                        </div>
                    </div>
                </div>
            )}

            <div className="space-y-6 max-w-4xl mx-auto pb-6">
                {groupedMessages.map((msg, idx) => (
                    <ChatMessage key={idx} msg={msg} />
                ))}

                {/* Streaming Content & Thinking State */}
                {(status === 'streaming' || currentTool || streamingContent) && (
                    <div className="flex gap-4 max-w-4xl mx-auto animate-in fade-in duration-300">
                        {/* Avatar */}
                        <div className="w-8 h-8 rounded-lg bg-white border border-gray-200 text-primary flex items-center justify-center shrink-0 shadow-sm">
                            <Shield size={16} />
                        </div>

                        <div className="space-y-2 w-[85%]">
                            <div className="text-xs font-semibold text-gray-500 ml-1">智能助手</div>

                            {/* 1. Pure Thinking State (No Content yet) */}
                            {(!currentTool && !streamingContent && status === 'streaming') && (
                                <div className="animate-in fade-in zoom-in-95 duration-300">
                                    <ThinkingIndicator />
                                </div>
                            )}

                            {/* 2. Tool Execution Panel */}
                            {currentTool && (
                                <div className="flex items-center gap-3 bg-blue-50/50 border border-blue-100 px-4 py-3 rounded-xl w-fit mb-2">
                                    <div className="h-4 w-4 flex items-center justify-center">
                                        <Loader2 size={16} className="animate-spin text-primary" />
                                    </div>
                                    <div className="flex flex-col">
                                        <span className="text-xs font-semibold text-gray-700">正在使用工具</span>
                                        <span className="text-xs text-gray-500 font-mono">{currentTool.tool}</span>
                                    </div>
                                </div>
                            )}

                            {/* 3. Streaming Text Bubble (treated as Thinking/Reasoning by default for Agent) */}
                            {streamingContent && (
                                <div className="animate-in fade-in duration-300">
                                    {/* Streaming Header */}
                                    <div className="flex items-center gap-2 mb-2 text-primary/80">
                                        <ThinkingIndicator />
                                    </div>

                                    {/* Streaming Body - Styled as Thinking Process */}
                                    <div className="bg-gray-50/80 border border-gray-100 text-gray-600 rounded-xl p-4 text-sm leading-relaxed shadow-sm font-mono text-[13px]">
                                        <div className="prose prose-sm max-w-none prose-gray prose-p:my-0">
                                            <ErrorBoundary>
                                                <Markdown
                                                    components={{
                                                        a: ({ node, ...props }) => <a {...props} className="text-primary hover:underline font-bold break-all" target="_blank" rel="noopener noreferrer" />,
                                                        code: ({ node, ...props }) => {
                                                            const match = /language-(\w+)/.exec(props.className || '');
                                                            return !match ? (
                                                                <code {...props} className="bg-gray-100 px-1.5 py-0.5 rounded font-mono text-xs border border-gray-200 text-gray-800" />
                                                            ) : (
                                                                <code {...props} />
                                                            )
                                                        },
                                                        pre: ({ node, ...props }) => (
                                                            <pre {...props} className="p-3 rounded-xl overflow-x-auto my-3 text-xs font-mono bg-white border border-gray-100" />
                                                        )
                                                    }}
                                                >
                                                    {String(streamingContent)}
                                                </Markdown>
                                            </ErrorBoundary>
                                        </div>
                                        <div className="flex items-center gap-2 mt-2 opacity-50">
                                            <span className="inline-block w-1.5 h-4 bg-primary animate-pulse rounded-full"></span>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} className="h-48 w-full shrink-0" />
            </div>
        </div>
    );
};
