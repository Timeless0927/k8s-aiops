import React from 'react';
import { Sidebar } from './Sidebar';

interface MainLayoutProps {
    children: React.ReactNode;
    uiSelectedId: string | null;
    handleSelectConversation: (id: string) => void;
    handleNewChat: () => void;
}

export const MainLayout: React.FC<MainLayoutProps> = ({
    children,
    uiSelectedId,
    handleSelectConversation,
    handleNewChat
}) => {
    return (
        <div className="h-screen w-screen flex bg-slate-50 overflow-hidden">
            {/* Sidebar */}
            <div className="shrink-0 h-full">
                <Sidebar
                    onSelect={handleSelectConversation}
                    currentId={uiSelectedId}
                    onNewChat={handleNewChat}
                />
            </div>

            {/* Main Content */}
            <div className="flex-1 h-full min-w-0 bg-slate-50 overflow-hidden">
                {children}
            </div>
        </div>
    );
};
