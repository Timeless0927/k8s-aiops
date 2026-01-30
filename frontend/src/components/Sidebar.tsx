import React, { useEffect, useState } from 'react';

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
        // Poll every 10s or just reload on mount
        const interval = setInterval(fetchConversations, 10000);
        return () => clearInterval(interval);
    }, []);

    const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);

    return (
        <div className="sidebar" style={{
            width: '250px',
            background: '#1e1e1e',
            borderRight: '1px solid #333',
            display: 'flex',
            flexDirection: 'column',
            color: '#eee',
            height: '100%',
            overflow: 'hidden'
        }}>
            <div style={{ padding: '1rem', borderBottom: '1px solid #333' }}>
                <button
                    onClick={onNewChat}
                    style={{
                        width: '100%',
                        padding: '0.5rem',
                        background: '#2563eb',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer'
                    }}
                >
                    + New Chat
                </button>
            </div>

            <div style={{ flex: 1, overflowY: 'auto' }}>
                {loading && conversations.length === 0 && (
                    <div style={{ padding: '1rem', color: '#888' }}>Loading...</div>
                )}

                {conversations.map(conv => (
                    <div
                        key={conv.id}
                        onClick={() => {
                            onSelect(conv.id);
                            setConfirmDeleteId(null);
                        }}
                        className="group relative"
                        style={{
                            padding: '0.75rem 1rem',
                            cursor: 'pointer',
                            background: currentId === conv.id ? '#333' : 'transparent',
                            borderBottom: '1px solid #2a2a2a',
                            position: 'relative',
                            transition: 'background 0.2s'
                        }}
                        onMouseLeave={() => setConfirmDeleteId(null)}
                    >
                        <div style={{ fontWeight: 'bold', fontSize: '0.9rem', marginBottom: '4px', paddingRight: '20px' }}>
                            {conv.title && conv.title !== "New Chat" ? conv.title : "New Conversation"}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: '#888' }}>
                            {new Date(conv.created_at).toLocaleString()}
                        </div>

                        <button
                            onClick={async (e) => {
                                e.stopPropagation();
                                if (confirmDeleteId === conv.id) {
                                    try {
                                        await fetch(`/api/conversations/${conv.id}`, { method: 'DELETE' });
                                        fetchConversations();
                                        if (currentId === conv.id) {
                                            onNewChat();
                                        }
                                        setConfirmDeleteId(null);
                                    } catch (err) {
                                        console.error("Failed to delete", err);
                                    }
                                } else {
                                    setConfirmDeleteId(conv.id);
                                }
                            }}
                            style={{
                                position: 'absolute',
                                top: '10px',
                                right: '10px',
                                background: confirmDeleteId === conv.id ? '#dc2626' : 'transparent',
                                border: 'none',
                                color: confirmDeleteId === conv.id ? 'white' : '#666',
                                cursor: 'pointer',
                                fontSize: confirmDeleteId === conv.id ? '0.7rem' : '1rem',
                                padding: confirmDeleteId === conv.id ? '2px 6px' : '0 4px',
                                borderRadius: '4px',
                                transition: 'all 0.2s'
                            }}
                            title={confirmDeleteId === conv.id ? "Confirm Delete" : "Delete"}
                        >
                            {confirmDeleteId === conv.id ? "Confirm" : "×"}
                        </button>
                    </div>
                ))}
            </div>

            <div style={{ padding: '0.5rem', fontSize: '0.7rem', color: '#555', textAlign: 'center' }}>
                K8s AIOps Agent v0.3
            </div>
        </div>
    );
};
