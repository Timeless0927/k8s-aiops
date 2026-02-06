import React, { useEffect, useState } from 'react';
import { Activity, Wifi, WifiOff } from 'lucide-react';

interface SystemStatus {
    kubernetes: {
        connected: boolean;
        error: string | null;
    };
}

export const ClusterStatus: React.FC = () => {
    const [status, setStatus] = useState<SystemStatus | null>(null);
    const [loading, setLoading] = useState(true);

    const fetchStatus = async () => {
        try {
            const res = await fetch('http://localhost:8000/api/v1/system/status');
            if (res.ok) {
                const data = await res.json();
                setStatus(data);
            }
        } catch (error) {
            console.error('Failed to fetch system status', error);
            setStatus({ kubernetes: { connected: false, error: 'Network Error' } });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 30000); // Poll every 30s
        return () => clearInterval(interval);
    }, []);

    if (loading || !status) return null;

    const isConnected = status.kubernetes.connected;

    return (
        <div
            className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${isConnected
                    ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                    : 'bg-rose-50 text-rose-700 border-rose-200'
                }`}
            title={isConnected ? 'Connected to Kubernetes Cluster' : `Disconnected: ${status.kubernetes.error}`}
        >
            {isConnected ? <Wifi className="w-3.5 h-3.5" /> : <WifiOff className="w-3.5 h-3.5" />}
            <span>{isConnected ? 'K8s Online' : 'K8s Offline'}</span>
        </div>
    );
};
