import React, { useState, useEffect } from 'react'
import { MainLayout } from './components/layout/MainLayout'
import { Header } from './components/layout/Header'
import { ChatArea } from './components/features/chat/ChatArea'
import { ChatInput } from './components/features/chat/ChatInput'
import { AlertsTopPanel } from './components/features/alerts/AlertsTopPanel'
import { AlertsPage } from './components/features/alerts/AlertsPage'
import PluginDashboard from './components/features/plugins/PluginDashboard'
import { SettingsPage } from './components/features/settings/SettingsPage'
import { useChatWebSocket } from './hooks/useChatWebSocket'

function App() {
    console.log("Rendering App Component");
    const [view, setView] = useState<'chat' | 'plugins' | 'settings' | 'alerts'>('chat')
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

    const { messages, setMessages, sendMessage, stopGeneration, status, currentTool, streamingContent } = useChatWebSocket(currentConversationId, onConversationInit);

    // Fetch conversation history when ID changes
    useEffect(() => {
        console.log("App: conversationId changed to:", currentConversationId);
        if (!currentConversationId) {
            console.log("App: No ID, clearing messages.");
            setMessages([]);
            return;
        }

        // Clear existing messages immediately to avoid showing stale data during fetch
        setMessages([]);

        const fetchHistory = async () => {
            console.log(`App: Fetching history for ${currentConversationId}...`);
            try {
                const res = await fetch(`/api/conversations/${currentConversationId}/messages`);
                if (res.ok) {
                    const data = await res.json();
                    console.log(`App: History loaded. Count: ${data.length}`);

                    // Post-process history to recover "Thought" state (Heuristic)
                    const processed = data.map((msg: any, idx: number) => {
                        if (msg.role !== 'assistant') return msg;
                        const nextMsg = data[idx + 1];
                        // Heuristic: If followed by Tool or another Assistant, it is likely a Thought/Reasoning step
                        if (nextMsg && (nextMsg.role === 'tool' || nextMsg.role === 'assistant')) {
                            return { ...msg, isThought: true };
                        }
                        return msg;
                    });

                    setMessages(processed);
                } else {
                    console.warn(`App: Fetch failed with status ${res.status}`);
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

    useEffect(() => {
        const handleLocationChange = () => {
            const path = window.location.pathname;

            // Check params
            const params = new URLSearchParams(window.location.search);
            const urlId = params.get('id');
            if (urlId) {
                console.log("Deep Link ID:", urlId);
                setCurrentConversationId(urlId);
            } else if (path === '/' || path === '/chat') {
                // If on chat view but no ID, reset to new chat
                console.log("Route is /chat with no ID -> Resetting state");
                setCurrentConversationId(null);
                setUiSelectedId(null);
                localStorage.removeItem("activeConversationId");
            }

            if (path === '/settings') setView('settings');
            else if (path === '/plugins') setView('plugins');
            else if (path === '/alerts') setView('alerts');
            else setView('chat');
        };
        handleLocationChange(); // Initial check
        window.addEventListener('popstate', handleLocationChange);

        // HACK: Intercept link clicks in Sidebar
        const originalPushState = history.pushState;
        history.pushState = function (...args) {
            originalPushState.apply(this, args);
            handleLocationChange();
        };

        return () => {
            window.removeEventListener('popstate', handleLocationChange);
            history.pushState = originalPushState;
        }
    }, []);

    // Fetch alerts periodically
    const fetchAlerts = async () => {
        try {
            const res = await fetch('/api/v1/alerts')
            if (res.ok) {
                const uiAlerts = await res.json()
                setAlerts(uiAlerts || [])
            }
        } catch (err) {
            console.error("Failed to fetch alerts", err)
        }
    }

    useEffect(() => {
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
        if (!alert.conversation_id) return;

        // Navigate
        const url = new URL(window.location.origin + '/chat');
        url.searchParams.set('id', alert.conversation_id);
        window.history.pushState({}, '', url.toString());
        window.dispatchEvent(new PopStateEvent('popstate'));

        if (view !== 'chat') setView('chat');
    }

    // Sidebar Handlers
    // Sidebar Handlers
    const handleSelectConversation = (id: string) => {
        // Force navigate to /chat + ID
        const newUrl = new URL(window.location.origin + '/chat');
        newUrl.searchParams.set('id', id);
        window.history.pushState({}, '', newUrl.toString());

        // Redundant but safe
        setCurrentConversationId(id);
        setUiSelectedId(id);
        localStorage.setItem("activeConversationId", id);
    };

    const handleNewChat = () => {
        // Force navigate to /chat (Clean State)
        const newUrl = new URL(window.location.origin + '/chat');
        window.history.pushState({}, '', newUrl.toString());

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
                    {view === 'chat' && (
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
                                stopGeneration={stopGeneration}
                                status={status}
                            />
                        </>
                    )}

                    {view === 'alerts' && (
                        <div className="h-full overflow-hidden flex flex-col">
                            <AlertsPage alerts={alerts} onRefresh={fetchAlerts} />
                        </div>
                    )}

                    {view === 'plugins' && (
                        <div className="h-full overflow-y-auto p-6">
                            <PluginDashboard />
                        </div>
                    )}

                    {view === 'settings' && (
                        <div className="h-full overflow-y-auto">
                            <SettingsPage />
                        </div>
                    )}
                </main>
            </div>
        </MainLayout>
    )
}

export default App
