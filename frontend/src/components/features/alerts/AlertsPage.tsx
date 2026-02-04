import React from 'react';
import { Shield, CheckCircle, Trash2, ExternalLink, AlertTriangle, AlertOctagon, Info } from 'lucide-react';

interface Alert {
    id: string;
    title: string;
    severity: 'critical' | 'warning' | 'info';
    status: 'active' | 'resolved';
    source: string;
    summary: string;
    conversation_id: string;
    created_at: string;
}

interface AlertsPageProps {
    alerts: Alert[];
    onRefresh: () => void;
}

export const AlertsPage: React.FC<AlertsPageProps> = ({ alerts, onRefresh }) => {
    // App handles loading state implicitly by initial empty array
    const loading = false;

    const handleResolve = async (id: string, e: React.MouseEvent) => {
        e.stopPropagation();
        await fetch(`/api/alerts/${id}?status=resolved`, { method: 'PUT' });
        onRefresh();
    };

    const handleDelete = async (id: string, e: React.MouseEvent) => {
        e.stopPropagation();
        if (!confirm('确定要删除这条告警记录吗？')) return;
        await fetch(`/api/alerts/${id}`, { method: 'DELETE' });
        onRefresh();
    };

    const handlePruneResolved = async () => {
        if (!confirm('确定要清空所有【已解决】的告警吗？')) return;
        await fetch('/api/alerts/prune?mode=resolved', { method: 'DELETE' });
        onRefresh();
    };

    const handleNavigate = (conversationId: string) => {
        // Deep link to Chat
        const url = new URL(window.location.origin + '/chat');
        url.searchParams.set('id', conversationId);
        window.history.pushState({}, '', url.toString());
        // Allow App.tsx to catch up via popstate event or just reload
        // Standard pushState doesn't trigger component re-render in our simple router unless we dispatch event
        window.dispatchEvent(new PopStateEvent('popstate'));
    };

    const getSeverityIcon = (sev: string) => {
        switch (sev) {
            case 'critical': return <AlertOctagon size={18} className="text-red-500" />;
            case 'warning': return <AlertTriangle size={18} className="text-amber-500" />;
            default: return <Info size={18} className="text-blue-500" />;
        }
    };

    return (
        <div className="flex-1 bg-slate-50 p-8 overflow-y-auto">
            <div className="max-w-5xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-slate-900 mb-2">告警中心</h1>
                        <p className="text-slate-500">查看并管理历史告警及其 AI 调查记录。</p>
                    </div>
                    <button
                        onClick={handlePruneResolved}
                        className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 text-slate-600 rounded-lg hover:bg-slate-50 hover:text-red-600 transition-colors shadow-sm"
                    >
                        <Trash2 size={16} />
                        <span>清理已解决</span>
                    </button>
                </div>

                {loading ? (
                    <div className="text-center py-20 text-slate-400">加载中...</div>
                ) : alerts.length === 0 ? (
                    <div className="text-center py-20 bg-white rounded-xl shadow-sm border border-slate-200">
                        <Shield size={48} className="mx-auto text-slate-200 mb-4" />
                        <h3 className="text-slate-900 font-medium">暂无告警</h3>
                        <p className="text-slate-500 text-sm mt-1">系统运行正常，没有发现活跃告警。</p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {alerts.map(alert => (
                            <div
                                key={alert.id}
                                onClick={() => handleNavigate(alert.conversation_id)}
                                className={`bg-white p-6 rounded-xl border transition-all cursor-pointer hover:shadow-md group relative overflow-hidden
                                    ${alert.status === 'resolved' ? 'border-slate-200 opacity-75' : 'border-l-4 border-l-red-500 border-y-slate-200 border-r-slate-200'}
                                `}
                            >
                                <div className="flex justify-between items-start">
                                    <div className="flex gap-4 items-start">
                                        <div className="mt-1">{getSeverityIcon(alert.severity)}</div>
                                        <div>
                                            <h3 className={`font-bold text-lg mb-1 ${alert.status === 'resolved' ? 'text-slate-500 line-through' : 'text-slate-900'}`}>
                                                {alert.title}
                                            </h3>
                                            <div className="text-xs font-mono text-slate-400 mb-2 flex gap-3">
                                                <span>📅 {new Date(alert.created_at).toLocaleString()}</span>
                                                <span>🔗 {alert.source}</span>
                                                <span className={`px-1.5 rounded ${alert.status === 'active' ? 'bg-red-50 text-red-600 font-bold' : 'bg-green-50 text-green-600'}`}>
                                                    {alert.status.toUpperCase()}
                                                </span>
                                            </div>
                                            <p className="text-slate-600 text-sm leading-relaxed max-w-2xl">
                                                {alert.summary}
                                            </p>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                        {alert.status === 'active' && (
                                            <button
                                                onClick={(e) => handleResolve(alert.id, e)}
                                                className="p-2 text-green-600 hover:bg-green-50 rounded-lg tooltip"
                                                title="标记为已解决"
                                            >
                                                <CheckCircle size={18} />
                                            </button>
                                        )}
                                        <button
                                            onClick={(e) => handleDelete(alert.id, e)}
                                            className="p-2 text-slate-400 hover:bg-red-50 hover:text-red-600 rounded-lg"
                                            title="删除记录"
                                        >
                                            <Trash2 size={18} />
                                        </button>
                                        <button
                                            className="p-2 text-primary hover:bg-indigo-50 rounded-lg"
                                            title="跳转到 AI 对话"
                                        >
                                            <ExternalLink size={18} />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};
