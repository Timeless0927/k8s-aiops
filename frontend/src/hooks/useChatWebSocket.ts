import { useState, useEffect, useRef, useCallback } from 'react';

export interface Message {
    role: 'user' | 'assistant' | 'system' | 'tool';
    content: string;
    isThought?: boolean;
}

export interface ToolState {
    tool: string;
    args: string;
    output: string | null;
    status: 'running' | 'completed' | 'error';
}

export const useChatWebSocket = (conversationId: string | null, onConversationInit?: (id: string, title?: string) => void) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [status, setStatus] = useState<'idle' | 'connected' | 'streaming' | 'error'>('idle');
    const [currentTool, setCurrentTool] = useState<ToolState | null>(null);
    const [streamingContent, setStreamingContent] = useState<string>("");

    const wsRef = useRef<WebSocket | null>(null);
    const contentRef = useRef<string>("");
    // Reset state when conversation ID changes
    useEffect(() => {
        setMessages([]);
        setStreamingContent("");
        setCurrentTool(null);
        setStatus('idle');
    }, [conversationId]);

    const connect = useCallback(() => {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        let wsUrl = `${protocol}//${host}/api/chat/ws`;

        if (conversationId) {
            wsUrl += `?conversation_id=${conversationId}`;
        }

        console.log(`Connecting to WS: ${wsUrl}`);
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log("WS Connected");
            setStatus('connected');
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                switch (data.type) {
                    case 'init':
                        // New session created by backend
                        console.log("WS Session Init:", data.conversation_id);
                        if (onConversationInit) {
                            onConversationInit(data.conversation_id, data.title);
                        }
                        break;

                    case 'token':
                        setStatus('streaming');
                        contentRef.current += data.content;
                        setStreamingContent(contentRef.current);
                        break;

                    case 'tool_start':
                        // 1. Commit pending thought/text if any
                        if (contentRef.current) {
                            const thought = contentRef.current;
                            // Mark as thought since it precedes a tool call
                            setMessages(prev => [...prev, { role: 'assistant', content: thought, isThought: true }]);
                            contentRef.current = "";
                            setStreamingContent("");
                        }

                        // 2. Start Tool UI
                        setCurrentTool({
                            tool: data.tool,
                            args: data.args,
                            output: null,
                            status: 'running'
                        });
                        break;

                    case 'tool_result':
                        // 1. Update Tool UI (Optional, maybe skip if we commit immediately)
                        setCurrentTool(prev => prev ? { ...prev, output: data.output, status: 'completed' } : null);

                        // 2. Commit Tool Result as a message (Mirroring DB)
                        // Note: App.tsx renders 'tool' role same as 'assistant' currently.
                        setMessages(prev => [...prev, { role: 'tool', content: data.output }]);

                        // 3. Clear Tool UI to prepare for next step
                        setCurrentTool(null);
                        break;

                    case 'error':
                        console.error("WS Error:", data.content);
                        setStatus('error');
                        contentRef.current += `\n[Error: ${data.content}]`;
                        setStreamingContent(contentRef.current);
                        break;

                    case 'done':
                        console.log("WS Done Event. Content length:", contentRef.current.length);
                        setStatus('connected');
                        if (contentRef.current) {
                            const finalContent = contentRef.current;
                            console.log("Appending FINAL message:", finalContent.substring(0, 50));
                            setMessages(prev => {
                                console.log("Previous messages count:", prev.length);
                                return [...prev, { role: 'assistant', content: finalContent, isThought: false }];
                            });
                        }
                        contentRef.current = "";
                        setStreamingContent("");
                        setCurrentTool(null);
                        break;
                }
            } catch (e) {
                console.error("WS Parse Error", e);
            }
        };

        ws.onerror = (e) => {
            console.error("WS Error", e);
            setStatus('error');
        };

        ws.onclose = (event) => {
            console.log(`WS Closed: code=${event.code}, reason=${event.reason}`);

            // Ignore normal closures (1000: Normal, 1005: No Status Recvd)
            if (event.code === 1000 || event.code === 1005) {
                setStatus('idle');
                return;
            }

            // If we have pending content when abnormally closed, save it
            if (contentRef.current) {
                console.log("Committing interrupted message:", contentRef.current);
                setMessages(prev => [...prev, { role: 'assistant', content: contentRef.current + "\n\n[连接异常断开]" }]);
                contentRef.current = "";
                setStreamingContent("");
            }
            setStatus('error');
        };

        wsRef.current = ws;
    }, [conversationId, onConversationInit]); // Reconnect when ID changes

    useEffect(() => {
        connect();
        return () => {
            wsRef.current?.close();
        };
    }, [connect]);

    const sendMessage = useCallback((text: string) => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
            console.warn("WS disconnected, reconnecting...");
            connect();
            // TODO: Queue message? For now just alert
            alert("Connection lost. Please try again in a second.");
            return;
        }

        // UI Updates
        contentRef.current = "";
        setStreamingContent("");
        setCurrentTool(null);
        setStatus('streaming');

        const newMsg: Message = { role: 'user', content: text };
        setMessages(prev => [...prev, newMsg]);

        // Send
        const payload = {
            messages: [...messages, newMsg],
            model: "qwen3-coder-plus"
        };
        wsRef.current.send(JSON.stringify(payload));
    }, [messages, connect]); // Added connect to deps

    const stopGeneration = useCallback(() => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ type: "stop" }));
            // We don't manually set status here, we wait for backend to close/confirm
            // OR we can force it for UI responsiveness
            // setStatus('connected'); 
        }
    }, []);

    return { messages, setMessages, sendMessage, stopGeneration, status, currentTool, streamingContent };
};
