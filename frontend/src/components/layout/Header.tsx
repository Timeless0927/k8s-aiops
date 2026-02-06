import React from 'react';
import { Shield, Bell } from 'lucide-react';
import { ClusterStatus } from '../features/ClusterStatus';

interface HeaderProps {
    view: 'chat' | 'plugins' | 'settings' | 'alerts';
    setView: (view: 'chat' | 'plugins' | 'settings' | 'alerts') => void;
    status: string;
    alertsCount: number;
}

export const Header: React.FC<HeaderProps> = ({ view, setView, status, alertsCount }) => {
    return (
        <header className="flex justify-between items-center bg-white/50 backdrop-blur-md h-16 px-8 sticky top-0 z-30 transition-all">
            <div className="flex items-center gap-8">
                <div className="flex items-center gap-3 select-none">
                    <div className="w-8 h-8 bg-gradient-to-br from-primary to-primary-hover rounded-xl flex items-center justify-center text-white shadow-lg shadow-primary/20">
                        <Shield size={16} strokeWidth={2.5} />
                    </div>
                    <div>
                        <h1 className="text-base font-bold tracking-tight text-slate-900 leading-none">AIOps Pro</h1>
                        <span className="text-[10px] font-mono text-slate-400 font-medium tracking-wide">控制台</span>
                    </div>
                </div>

                <nav className="flex items-center gap-1">
                    <button
                        onClick={() => {
                            window.history.pushState({}, '', '/chat');
                            window.dispatchEvent(new PopStateEvent('popstate'));
                        }}
                        className={`relative px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${view === 'chat' ? 'text-slate-900 bg-slate-100' : 'text-slate-500 hover:text-slate-900 hover:bg-slate-50'}`}
                    >
                        对话
                        {view === 'chat' && <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-1 h-1 bg-slate-900 rounded-full mb-1"></span>}
                    </button>
                    <button
                        onClick={() => {
                            window.history.pushState({}, '', '/plugins');
                            window.dispatchEvent(new PopStateEvent('popstate'));
                        }}
                        className={`relative px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${view === 'plugins' ? 'text-slate-900 bg-slate-100' : 'text-slate-500 hover:text-slate-900 hover:bg-slate-50'}`}
                    >
                        插件
                    </button>
                </nav>
            </div>

            <div className="flex gap-4 items-center">
                <ClusterStatus />
                <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-[11px] font-mono font-semibold border transition-all ${status === 'connected' || status === 'streaming' ? 'bg-emerald-50 text-emerald-600 border-emerald-100' : 'bg-rose-50 text-rose-600 border-rose-100'}`}>
                    <div className={`w-1.5 h-1.5 rounded-full ${status === 'streaming' ? 'animate-ping bg-emerald-500' : (status === 'connected' ? 'bg-emerald-500' : 'bg-rose-500')}`}></div>
                    {status === 'streaming' ? '处理中' : (status === 'connected' ? '已连接' : '未连接')}
                </div>

                <div className="h-4 w-px bg-slate-200 mx-1"></div>

                <button className="btn-ghost relative">
                    <Bell size={18} />
                    {alertsCount > 0 && <span className="absolute top-2 right-2 w-2 h-2 bg-danger rounded-full ring-2 ring-white"></span>}
                </button>
                <div className="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center text-xs font-bold cursor-pointer hover:bg-slate-800 transition-colors">
                    OP
                </div>
            </div>
        </header>
    );
};
