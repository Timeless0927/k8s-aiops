import React, { useRef, useEffect } from 'react';
import { Shield, Loader2 } from 'lucide-react';
import { ChatMessage } from './ChatMessage';
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
                {messages.filter(msg => msg.role !== 'tool').map((msg, idx) => (
                    <ChatMessage key={idx} msg={msg} />
                ))}

                {/* Streaming Content & Thinking State */}
                {(status === 'streaming' || currentTool) && (
                    <div className="flex gap-4 max-w-4xl mx-auto animate-in fade-in duration-300">
                        <div className="w-8 h-8 rounded-lg bg-white border border-gray-200 text-primary flex items-center justify-center shrink-0 shadow-sm">
                            <Shield size={16} />
                        </div>
                        <div className="space-y-1 w-[85%]">
                            <div className="text-xs font-semibold text-gray-500 mb-1 ml-1">智能助手</div>

                            {/* Thinking / Tool Execution Panel */}
                            {currentTool && (
                                <div className="flex items-center gap-2 text-primary bg-primary/5 px-3 py-1.5 rounded-lg border border-primary/10 w-fit mb-2 text-xs font-mono">
                                    <Loader2 size={13} className="animate-spin" />
                                    <span>正在使用工具: {currentTool.tool}...</span>
                                </div>
                            )}

                            {/* Pure Thinking State */}
                            {(!currentTool && !streamingContent) && (
                                <div className="flex items-center gap-2 text-muted bg-gray-100 px-3 py-1.5 rounded-lg w-fit mb-2 text-xs font-mono">
                                    <Loader2 size={13} className="animate-spin" />
                                    <span>思考中...</span>
                                </div>
                            )}

                            {/* Streaming Text */}
                            {streamingContent && (
                                <div className="bg-white border border-gray-200 text-gray-800 rounded-2xl rounded-tl-sm p-4 text-sm leading-relaxed shadow-sm">
                                    <div className="prose prose-sm max-w-none prose-gray prose-p:my-0">
                                        <ErrorBoundary>
                                            <Markdown
                                                components={{
                                                    a: ({ node, ...props }) => <a {...props} className="text-primary hover:underline font-bold break-all" target="_blank" rel="noopener noreferrer" />,
                                                    code: ({ node, ...props }) => <code {...props} className="bg-gray-100 px-1 py-0.5 rounded font-mono text-xs border border-gray-200 text-gray-800" />
                                                }}
                                            >
                                                {String(streamingContent)}
                                            </Markdown>
                                        </ErrorBoundary>
                                    </div>
                                    <span className="inline-block w-2 h-4 bg-primary ml-1 animate-pulse align-middle"></span>
                                </div>
                            )}
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>
        </div>
    );
};
