import React from 'react';
import { Activity } from 'lucide-react';

interface AlertSidebarProps {
    alerts: any[];
    onAlertClick: (alert: any) => void;
}

export const AlertSidebar: React.FC<AlertSidebarProps> = ({ alerts, onAlertClick }) => {
    return (
        <section className="lg:col-span-1 space-y-4 overflow-y-auto pr-2 custom-scrollbar">
            <h2 className="text-muted font-mono text-sm uppercase tracking-wider mb-2 flex items-center gap-2">
                <Activity size={16} /> Active Alerts
            </h2>

            {alerts.length === 0 && <div className="text-muted text-sm italic glass-card p-4">No active alerts. Waiting for webhook...</div>}

            {alerts.map((alert) => (
                <div key={alert.id} onClick={() => onAlertClick(alert)} className={`glass-card hover:translate-x-1 cursor-pointer group ${alert.analysis ? 'ring-1 ring-emerald-500/50' : ''}`}>
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
    );
};
