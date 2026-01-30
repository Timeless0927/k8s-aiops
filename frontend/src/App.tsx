import React, { useState, useRef, useEffect } from 'react'
import { Bell, Activity, Shield, Terminal, Package, LayoutDashboard, Loader2 } from 'lucide-react'
import PluginManager from './components/PluginManager'
import { Sidebar } from './components/Sidebar'
import { useChatWebSocket } from './hooks/useChatWebSocket'

function App() {
    console.log("Rendering App Component");
    const [view, setView] = useState<'chat' | 'plugins'>('chat')
    const [input, setInput] = useState('')
    const [alerts, setAlerts] = useState<any[]>([])
    const messagesEndRef = useRef<HTMLDivElement>(null)

    // State for Conversation History
    // 'currentConversationId' controls the WebSocket Connection.
    const [currentConversationId, setCurrentConversationId] = useState<string | null>(() => {
        const stored = localStorage.getItem("activeConversationId");
        // Ensure we don't return "null" string
        return (stored && stored !== "null" && stored !== "undefined") ? stored : null;
    });

    // 'uiSelectedId' controls the Sidebar Highlight.
    const [uiSelectedId, setUiSelectedId] = useState<string | null>(currentConversationId);

    // Sync UI state if storage was loaded initially
    useEffect(() => {
        setUiSelectedId(currentConversationId);
    }, []);

    // WebSocket Hook
    const onConversationInit = React.useCallback((newId: string, title?: string) => {
        console.log("New Conversation Created (Lazy):", newId);
        // Only update UI and Storage. Do NOT update currentConversationId to avoid WS reconnect.
        setUiSelectedId(newId);
        localStorage.setItem("activeConversationId", newId);
    }, []);

    const { messages, setMessages, sendMessage, status, currentTool, streamingContent } = useChatWebSocket(currentConversationId, onConversationInit);

    // Fetch conversation history when ID changes
    useEffect(() => {
        // If we are in "New Chat" mode (null), clear messages
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


    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }

    useEffect(() => {
        if (view === 'chat') {
            scrollToBottom()
        }
    }, [messages, streamingContent, currentTool, view])

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
        // User manually switched. We MUST reconnect to load proper history/context.
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
        <div className="min-h-screen bg-background text-text font-sans flex text-sm">
            {/* Sidebar */}
            <div className="shrink-0 h-screen sticky top-0">
                <Sidebar
                    onSelect={handleSelectConversation}
                    currentId={uiSelectedId} // Use UI state for highlighting
                    onNewChat={handleNewChat}
                />
            </div>

            {/* Main Area */}
            <div className="flex-1 p-6 overflow-hidden">
                {/* Navbar */}
                <header className="flex justify-between items-center mb-6 glass rounded-2xl p-4 px-6">
                    <div className="flex items-center gap-6">
                        <div className="flex items-center gap-3">
                            <span className="p-2 bg-primary/20 rounded-lg text-primary"><Shield size={24} /></span>
                            <h1 className="text-xl font-bold tracking-tight">K8s AIOps <span className="text-primary">Agent</span></h1>
                        </div>

                        <nav className="flex gap-1 bg-surface/30 p-1 rounded-lg">
                            <button
                                onClick={() => setView('chat')}
                                className={`flex items-center gap-2 px-4 py-2 rounded-md transition-all text-sm font-medium ${view === 'chat' ? 'bg-primary/20 text-primary' : 'text-muted hover:text-text hover:bg-white/5'}`}
                            >
                                <LayoutDashboard size={16} /> Dashboard
                            </button>
                            <button
                                onClick={() => setView('plugins')}
                                className={`flex items-center gap-2 px-4 py-2 rounded-md transition-all text-sm font-medium ${view === 'plugins' ? 'bg-primary/20 text-primary' : 'text-muted hover:text-text hover:bg-white/5'}`}
                            >
                                <Package size={16} /> Plugins
                            </button>
                        </nav>
                    </div>

                    <div className="flex gap-4">
                        <div className="flex items-center gap-2 px-3 py-1 bg-surface/50 rounded-full text-xs font-mono text-muted">
                            <div className={`w-2 h-2 rounded-full ${status === 'connected' || status === 'streaming' ? 'bg-emerald-500' : 'bg-red-500 animate-pulse'}`}></div>
                            {status === 'streaming' ? 'GENERATING' : status.toUpperCase()}
                        </div>
                        <button className="p-2 hover:bg-surface rounded-full transition-colors relative">
                            <Bell size={20} />
                            {alerts.length > 0 && <span className="absolute top-1 right-1 w-2 h-2 bg-danger rounded-full animate-pulse"></span>}
                        </button>
                        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary to-secondary"></div>
                    </div>
                </header>

                {/* Main Content */}
                {view === 'chat' ? (
                    <main className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-120px)]">
                        {/* Left Column: Alerts Feed - Adjusted height */}
                        <section className="lg:col-span-1 space-y-4 overflow-y-auto pr-2 custom-scrollbar">
                            <h2 className="text-muted font-mono text-sm uppercase tracking-wider mb-2 flex items-center gap-2">
                                <Activity size={16} /> Active Alerts
                            </h2>

                            {alerts.length === 0 && <div className="text-muted text-sm italic glass-card p-4">No active alerts. Waiting for webhook...</div>}

                            {alerts.map((alert) => (
                                <div key={alert.id} onClick={() => handleAlertClick(alert)} className={`glass-card hover:translate-x-1 cursor-pointer group ${alert.analysis ? 'ring-1 ring-emerald-500/50' : ''}`}>
                                    <div className="flex justify-between items-start mb-2">
                                        <span className={`px-2 py-0.5 rounded text-xs font-bold font-mono ${alert.severity === 'critical' ? 'bg-danger/20 text-danger' : 'bg-warning/20 text-warning'
                                            }`}>{alert.severity.toUpperCase()}</span>
                                        <span className="text-xs text-muted font-mono">{alert.time}</span>
                                    </div>
                                    <h3 className="font-bold text-lg mb-1 group-hover:text-primary transition-colors">{alert.name}</h3>
                                    <p className="text-sm text-muted break-all font-mono">{alert.pod}</p>
                                    {alert.analysis && <div className="mt-2 text-xs text-emerald-400 font-mono flex items-center gap-1">✨ Analyzed</div>}
                                </div>
                            ))}
                        </section>

                        {/* Center/Right: Chat & Diagnosis Area */}
                        <section className="lg:col-span-2 flex flex-col h-[calc(100vh-180px)] glass rounded-2xl overflow-hidden relative">
                            {/* Chat Header */}
                            <div className="p-4 border-b border-white/5 bg-surface/30 flex justify-between items-center">
                                <div className="flex items-center gap-2">
                                    <Terminal size={18} className="text-primary" />
                                    <span className="font-mono text-sm">Agent Session: {currentConversationId ? "#" + currentConversationId.slice(0, 4) : "New"}</span>
                                </div>
                                <span className="flex h-2 w-2 relative">
                                    <span className={`absolute inline-flex h-full w-full rounded-full opacity-75 ${status === 'streaming' ? 'animate-ping bg-emerald-400' : 'bg-transparent'}`}></span>
                                    <span className={`relative inline-flex rounded-full h-2 w-2 ${status === 'connected' || status === 'streaming' ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
                                </span>
                            </div>

                            {/* Chat Body */}
                            <div className="flex-1 p-6 overflow-y-auto space-y-6">
                                {messages.length === 0 && (
                                    <div className="flex gap-4 max-w-3xl">
                                        <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center shrink-0"><Shield size={16} className="text-primary" /></div>
                                        <div className="glass rounded-r-xl rounded-bl-xl p-4 text-sm">
                                            Hello, I'm your K8s AIOps Agent (WebSocket Enabled). How can I assist you with your cluster today?
                                        </div>
                                    </div>
                                )}

                                {messages.filter(msg => msg.role !== 'tool').map((msg, idx) => (
                                    <div key={idx} className={`flex gap-4 max-w-3xl ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}>
                                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-gradient-to-tr from-primary to-secondary rounded-full' : 'bg-primary/20'}`}>
                                            {msg.role === 'user' ? '' : <Shield size={16} className="text-primary" />}
                                        </div>
                                        <div className={`space-y-2 ${msg.role === 'user' ? 'text-right' : ''}`}>
                                            <div className="text-sm font-semibold text-muted">{msg.role === 'user' ? 'You' : 'AIOps Agent'}</div>
                                            <div className={`p-4 text-sm leading-relaxed inline-block text-left whitespace-pre-wrap ${msg.role === 'user'
                                                ? 'bg-primary/20 border border-primary/20 rounded-l-xl rounded-br-xl'
                                                : 'glass rounded-r-xl rounded-bl-xl'
                                                }`}>
                                                {msg.content}
                                            </div>
                                        </div>
                                    </div>
                                ))}

                                {/* Streaming Content & Thinking State */}
                                {(status === 'streaming' || currentTool) && (
                                    <div className="flex gap-4 max-w-3xl animate-in fade-in duration-300">
                                        <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center shrink-0"><Shield size={16} className="text-primary" /></div>
                                        <div className="space-y-2 w-full">
                                            <div className="text-sm font-semibold text-muted">AIOps Agent</div>

                                            {/* Thinking / Tool Execution Panel */}
                                            {currentTool && (
                                                <div className="flex items-center gap-2 text-primary opacity-75 mb-2 text-xs font-mono ml-1">
                                                    <Loader2 size={14} className="animate-spin" />
                                                    <span>Using tool: {currentTool.tool}...</span>
                                                </div>
                                            )}

                                            {/* Pure Thinking State (No tool yet, no content yet) */}
                                            {(!currentTool && !streamingContent) && (
                                                <div className="flex items-center gap-2 text-muted opacity-50 mb-2 text-xs font-mono ml-1">
                                                    <Loader2 size={14} className="animate-spin" />
                                                    <span>Thinking...</span>
                                                </div>
                                            )}

                                            {/* Streaming Text */}
                                            {streamingContent && (
                                                <div className="glass rounded-r-xl rounded-bl-xl p-4 text-sm leading-relaxed whitespace-pre-wrap relative">
                                                    {streamingContent}
                                                    <span className="inline-block w-2 h-4 bg-primary ml-1 animate-pulse align-middle"></span>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}
                                <div ref={messagesEndRef} />
                            </div>

                            {/* Input Area */}
                            <div className="p-4 border-t border-white/5 bg-surface/30">
                                <div className="relative">
                                    <input
                                        type="text"
                                        value={input}
                                        onChange={(e) => setInput(e.target.value)}
                                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                                        placeholder="Type a command or ask a question..."
                                        className="w-full bg-surface/50 border border-white/10 rounded-xl py-3 px-4 pl-10 focus:outline-none focus:border-primary/50 font-mono text-sm"
                                        disabled={status === 'streaming'} // Disable input while streaming
                                    />
                                    <span className="absolute left-4 top-3.5 text-muted">$</span>
                                </div>
                            </div>
                        </section>
                    </main>
                ) : (
                    <PluginManager />
                )}
            </div>
        </div>
    )
}

export default App
