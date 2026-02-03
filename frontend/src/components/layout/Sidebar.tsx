import React, { useEffect, useState } from 'react';
import { MessageSquare, Trash2, Plus } from 'lucide-react';

interface Conversation {
    id: string;
    title: string;
    created_at: string;
}

interface SidebarProps {
    onSelect: (id: string) => void;
    currentId: string | null;
    onNewChat: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onSelect, currentId, onNewChat }) => {
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [loading, setLoading] = useState(false);
    const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);

    const fetchConversations = async () => {
        setLoading(true);
        try {
            const res = await fetch('/api/conversations');
            if (res.ok) {
                const data = await res.json();
                setConversations(data);
            }
        } catch (e) {
            console.error("Failed to list conversations", e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchConversations();
        const interval = setInterval(fetchConversations, 10000);
        return () => clearInterval(interval);
    }, []);

    const handleDelete = async (e: React.MouseEvent, id: string) => {
        e.stopPropagation();
        if (confirmDeleteId === id) {
            try {
                await fetch(`/api/conversations/${id}`, { method: 'DELETE' });
                fetchConversations();
                if (currentId === id) {
                    onNewChat();
                }
                setConfirmDeleteId(null);
            } catch (err) {
                console.error("Failed to delete", err);
            }
        } else {
            setConfirmDeleteId(id);
            // Auto reset confirm state after 3 seconds
            setTimeout(() => setConfirmDeleteId(null), 3000);
        }
    };

    return (
        <div className="w-64 h-full bg-white flex flex-col text-sm border-r-0">
            {/* New Chat Button */}
            <div className="p-4 pt-6">
                <button
                    onClick={onNewChat}
                    className="w-full py-2.5 px-4 bg-slate-900 hover:bg-slate-800 text-white rounded-lg shadow-md hover:shadow-lg font-medium flex items-center justify-center gap-2 transition-all active:scale-[0.98]"
                >
                    <Plus size={16} /> 新建对话
                </button>
            </div>

            {/* Conversation List */}
            <div className="flex-1 overflow-y-auto px-3 py-2 space-y-0.5 custom-scrollbar">
                {/* Section Header */}
                <div className="px-3 py-2 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                    最近访问
                </div>

                {/* Loading State */}
                {loading && conversations.length === 0 && (
                    <div className="p-4 text-center text-slate-400 text-xs animate-pulse">加载中...</div>
                )}

                {/* Empty State */}
                {!loading && conversations.length === 0 && (
                    <div className="p-4 text-center text-slate-400 text-xs italic">暂无历史记录</div>
                )}

                {conversations.map(conv => {
                    const isActive = currentId === conv.id;
                    const isConfirming = confirmDeleteId === conv.id;

                    return (
                        <div
                            key={conv.id}
                            onClick={() => {
                                onSelect(conv.id);
                                setConfirmDeleteId(null);
                            }}
                            className={`
                                group relative p-2.5 rounded-lg cursor-pointer transition-all duration-200
                                ${isActive
                                    ? 'bg-slate-200/60 text-slate-900 font-medium'
                                    : 'text-slate-500 hover:bg-slate-100/80 hover:text-slate-900'}
                            `}
                        >
                            <div className="flex items-center gap-3">
                                <MessageSquare size={16} className={`shrink-0 transition-colors ${isActive ? 'text-primary' : 'text-slate-400 group-hover:text-slate-500'}`} />
                                <div className="flex-1 min-w-0">
                                    <div className="truncate text-[13px] leading-snug">
                                        {conv.title && conv.title !== "New Chat" ? conv.title : "未命名会话"}
                                    </div>
                                    <div className="text-[10px] text-slate-400 truncate mt-0.5 font-mono opacity-80">
                                        {new Date(conv.created_at).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}
                                    </div>
                                </div>
                            </div>

                            {/* Delete Button */}
                            <button
                                onClick={(e) => handleDelete(e, conv.id)}
                                className={`
                                    absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-md transition-all
                                    ${isConfirming
                                        ? 'bg-rose-100 text-rose-600 opacity-100 shadow-sm'
                                        : 'text-slate-400 hover:text-rose-500 opacity-0 group-hover:opacity-100 hover:bg-white'}
                                `}
                                title={isConfirming ? "点击确认删除" : "删除"}
                            >
                                <Trash2 size={13} />
                            </button>
                        </div>
                    );
                })}
            </div>

            {/* Footer */}
            <div className="p-4 text-center border-t border-border/50">
                <span className="text-[10px] text-slate-400 font-mono select-none">v0.5.0 • Pro Max</span>
            </div>
        </div>
    );
};
