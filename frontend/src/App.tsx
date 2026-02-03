import React, { useState, useEffect } from 'react'
import { MainLayout } from './components/layout/MainLayout'
import { Header } from './components/layout/Header'
import { ChatArea } from './components/features/chat/ChatArea'
import { ChatInput } from './components/features/chat/ChatInput'
import { AlertsTopPanel } from './components/features/alerts/AlertsTopPanel'
import PluginDashboard from './components/features/plugins/PluginDashboard'
import { useChatWebSocket } from './hooks/useChatWebSocket'
import { Terminal } from 'lucide-react'

function App() {
    console.log("Rendering App Component");
    const [view, setView] = useState<'chat' | 'plugins'>('chat')
    const [input, setInput] = useState('')
    const [alerts, setAlerts] = useState<any[]>([])

    // State for Conversation History
    const [currentConversationId, setCurrentConversationId] = useState<string | null>(() => {
        const stored = localStorage.getItem("activeConversationId");
        return (stored && stored !== "null" && stored !== "undefined") ? stored : null;
    });

    // UI state for Sidebar Highlight - separated from connection state
    const [uiSelectedId, setUiSelectedId] = useState<string | null>(currentConversationId);

    // Sync UI state if storage was loaded initially
    useEffect(() => {
        setUiSelectedId(currentConversationId);
    }, []);

    // WebSocket Hook
    const onConversationInit = React.useCallback((newId: string) => {
        console.log("New Conversation Created (Lazy):", newId);
        setUiSelectedId(newId);
        localStorage.setItem("activeConversationId", newId);
    }, []);

    const { messages, setMessages, sendMessage, status, currentTool, streamingContent } = useChatWebSocket(currentConversationId, onConversationInit);

    // Fetch conversation history when ID changes
    useEffect(() => {
        if (!currentConversationId) {
            setMessages([]);
            return;
        }

        const fetchHistory = async () => {
            try {
                const res = await fetch(`/api/conversations/${currentConversationId}/messages`);
                if (res.ok) {
                    const data = await res.json();
                    setMessages(data);
                } else {
                    if (res.status === 404) {
                        console.warn("Conversation not found, resetting state.");
                        setCurrentConversationId(null);
                        setUiSelectedId(null);
                        localStorage.removeItem("activeConversationId");
                    }
                }
            } catch (e) {
                console.error("Failed to load history", e);
            }
        };
        fetchHistory();
    }, [currentConversationId, setMessages]);

    // Fetch alerts periodically
    useEffect(() => {
        const fetchAlerts = async () => {
            try {
                const res = await fetch('/api/alerts')
                if (res.ok) {
                    const uiAlerts = await res.json()
                    setAlerts(uiAlerts || [])
                }
            } catch (err) {
                console.error("Failed to fetch alerts", err)
            }
        }

        fetchAlerts()
        const interval = setInterval(fetchAlerts, 5000)
        return () => clearInterval(interval)
    }, [])

    const handleSend = () => {
        if (!input.trim() || status === 'streaming') return;
        sendMessage(input);
        setInput('');
    }

    const handleAlertClick = (alert: any) => {
        if (view !== 'chat') setView('chat');
        if (alert.analysis) {
            setInput(`Please analyze the alert: ${alert.name} on ${alert.pod}`);
        } else {
            setInput(`Analyze alert ${alert.name} on pod ${alert.pod}`)
        }
    }

    // Sidebar Handlers
    const handleSelectConversation = (id: string) => {
        setCurrentConversationId(id);
        setUiSelectedId(id);
        localStorage.setItem("activeConversationId", id);
    };

    const handleNewChat = () => {
        setCurrentConversationId(null);
        setUiSelectedId(null);
        localStorage.removeItem("activeConversationId");
    };

    return (
        <MainLayout
            uiSelectedId={uiSelectedId}
            handleSelectConversation={handleSelectConversation}
            handleNewChat={handleNewChat}
        >
            <div className="flex flex-col h-screen bg-slate-50">
                {/* Header */}
                <Header
                    view={view}
                    setView={setView}
                    status={status}
                    alertsCount={alerts.length}
                />

                {/* Alerts Top Panel */}
                <AlertsTopPanel
                    alerts={alerts}
                    onAlertClick={handleAlertClick}
                />

                {/* Main Content Area */}
                <main className="flex-1 overflow-hidden relative flex flex-col">
                    {view === 'chat' ? (
                        <>
                            {/* Chat Header Status (Simple) */}


                            {/* Chat Body */}
                            <ChatArea
                                messages={messages}
                                status={status}
                                currentTool={currentTool}
                                streamingContent={streamingContent}
                            />

                            {/* Input Area */}
                            <ChatInput
                                input={input}
                                setInput={setInput}
                                handleSend={handleSend}
                                status={status}
                            />
                        </>
                    ) : (
                        <div className="h-full overflow-y-auto p-6">
                            <PluginDashboard />
                        </div>
                    )}
                </main>
            </div>
        </MainLayout>
    )
}

export default App
