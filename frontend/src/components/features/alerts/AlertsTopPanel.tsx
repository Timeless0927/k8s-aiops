import React from 'react';
import { Activity, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

interface AlertsTopPanelProps {
    alerts: any[];
    onAlertClick: (alert: any) => void;
}

export const AlertsTopPanel: React.FC<AlertsTopPanelProps> = ({ alerts, onAlertClick }) => {
    // Only show active alerts
    const activeAlerts = alerts.filter(a => a.status === 'active');

    if (activeAlerts.length === 0) {
        return (
            <div className="bg-emerald-50 border-b border-emerald-100 py-2 px-6 flex items-center justify-center gap-2 text-emerald-700 text-sm font-medium animate-in slide-in-from-top-2">
                <CheckCircle size={16} />
                <span>All Systems Operational. No active alerts.</span>
            </div>
        );
    }

    return (
        <div className="bg-white border-b border-gray-200 py-3 px-6 overflow-x-auto">
            <div className="flex items-center gap-4 min-w-max">
                <div className="flex items-center gap-2 text-muted text-xs font-bold uppercase tracking-wider shrink-0 mr-2">
                    <Activity size={14} /> Active Alerts ({activeAlerts.length})
                </div>

                {activeAlerts.map((alert) => (
                    <div
                        key={alert.id}
                        onClick={() => onAlertClick(alert)}
                        className={`
                            flex items-center gap-3 px-3 py-1.5 rounded-lg border cursor-pointer hover:shadow-md transition-all shrink-0
                            ${alert.severity === 'critical' ? 'bg-red-50 border-red-100 hover:border-red-200' : 'bg-amber-50 border-amber-100 hover:border-amber-200'}
                            ${alert.analysis ? 'ring-2 ring-indigo-500/20' : ''}
                        `}
                    >
                        {alert.severity === 'critical' ? (
                            <XCircle size={16} className="text-red-500" />
                        ) : (
                            <AlertTriangle size={16} className="text-amber-500" />
                        )}

                        <div className="flex flex-col">
                            <span className={`text-sm font-semibold ${alert.severity === 'critical' ? 'text-red-900' : 'text-amber-900'}`}>
                                {alert.title || alert.name || 'Alert'}
                            </span>
                            <span className="text-[10px] text-muted font-mono leading-none">
                                {alert.source || alert.pod || 'Unknown'} • {alert.created_at ? new Date(alert.created_at).toLocaleTimeString() : 'Just now'}
                            </span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
