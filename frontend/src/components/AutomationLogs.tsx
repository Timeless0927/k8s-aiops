import React, { useEffect, useState } from 'react';
import { getAutomationLogs, AutomationLog } from '../api/automation';
import { RefreshCw, AlertTriangle, CheckCircle, XCircle, Clock } from 'lucide-react';

const AutomationLogs: React.FC = () => {
    const [logs, setLogs] = useState<AutomationLog[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    const fetchLogs = async () => {
        setLoading(true);
        try {
            const data = await getAutomationLogs();
            setLogs(data);
            setError(null);
        } catch (err) {
            setError('加载自动化日志失败');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLogs();
        const interval = setInterval(fetchLogs, 30000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="mt-6 border-t border-slate-100 pt-6">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                    <Clock size={16} className="text-slate-500" />
                    近期自动修复记录 (Recent Actions)
                </h3>
                <button
                    onClick={fetchLogs}
                    disabled={loading}
                    className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-md transition-colors"
                    title="刷新日志"
                >
                    <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
                </button>
            </div>

            {error && (
                <div className="bg-red-50 text-red-600 text-xs p-3 rounded-md mb-4 flex items-center gap-2">
                    <AlertTriangle size={14} /> {error}
                </div>
            )}

            <div className="overflow-hidden rounded-lg border border-slate-200">
                <table className="min-w-full divide-y divide-slate-200">
                    <thead className="bg-slate-50">
                        <tr>
                            <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">时间</th>
                            <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">目标 (Fingerprint)</th>
                            <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">动作</th>
                            <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">状态</th>
                            <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">详情</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-slate-200 text-sm">
                        {loading && logs.length === 0 ? (
                            <tr><td colSpan={5} className="px-4 py-8 text-center text-slate-400">加载中...</td></tr>
                        ) : logs.length === 0 ? (
                            <tr><td colSpan={5} className="px-4 py-8 text-center text-slate-400 italic">暂无自动修复记录</td></tr>
                        ) : (
                            logs.map((log) => (
                                <tr key={log.id} className="hover:bg-slate-50/80 transition-colors">
                                    <td className="px-4 py-3 whitespace-nowrap text-slate-500 text-xs font-mono">
                                        {new Date(log.timestamp).toLocaleString('zh-CN')}
                                    </td>
                                    <td className="px-4 py-3 whitespace-nowrap font-mono text-xs text-indigo-600/90 font-medium">
                                        {log.fingerprint}
                                    </td>
                                    <td className="px-4 py-3 whitespace-nowrap">
                                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-800 border border-slate-200">
                                            {log.action}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 whitespace-nowrap">
                                        <StatusBadge status={log.status} />
                                    </td>
                                    <td className="px-4 py-3 text-slate-500 text-xs max-w-xs truncate" title={log.message || ''}>
                                        {log.message || '-'}
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
    if (status === 'success') {
        return <span className="flex items-center gap-1.5 text-emerald-600 text-xs font-medium"><CheckCircle size={12} /> 成功</span>;
    }
    if (status === 'throttled') {
        return <span className="flex items-center gap-1.5 text-amber-600 text-xs font-medium"><Clock size={12} /> 熔断 (Throttled)</span>;
    }
    return <span className="flex items-center gap-1.5 text-rose-600 text-xs font-medium"><XCircle size={12} /> 失败</span>;
};

export default AutomationLogs;
