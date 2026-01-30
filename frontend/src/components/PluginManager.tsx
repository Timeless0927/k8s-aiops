import React, { useEffect, useState } from 'react';
import { Package, Upload, Trash2, RefreshCw, CheckCircle, XCircle, Power } from 'lucide-react';

interface Plugin {
    id: string;
    name: string;
    version: string;
    description: string;
    status: string;
    author?: string;
    is_builtin: boolean;
    error?: string;
}

const PluginManager: React.FC = () => {
    const [plugins, setPlugins] = useState<Plugin[]>([]);
    const [loading, setLoading] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

    const fetchPlugins = async () => {
        setLoading(true);
        try {
            const res = await fetch('/api/plugins/');
            if (!res.ok) throw new Error("Failed to fetch plugins");
            const data = await res.json();
            setPlugins(data);
        } catch (err: any) {
            setMessage({ type: 'error', text: err.message });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPlugins();
    }, []);

    const handleReload = async () => {
        setLoading(true);
        try {
            await fetch('/api/plugins/reload', { method: 'POST' });
            await fetchPlugins();
            setMessage({ type: 'success', text: "Plugins reloaded successfully" });
        } catch (err: any) {
            setMessage({ type: 'error', text: "Reload failed: " + err.message });
        } finally {
            setLoading(false);
        }
    };

    const handleToggle = async (pluginId: string, currentStatus: string) => {
        const newActive = currentStatus !== 'active';
        try {
            const res = await fetch(`/api/plugins/${pluginId}/toggle`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ active: newActive })
            });
            if (!res.ok) throw new Error("Toggle failed");
            await fetchPlugins();
            setMessage({ type: 'success', text: `Plugin ${newActive ? 'enabled' : 'disabled'}` });
        } catch (err: any) {
            setMessage({ type: 'error', text: err.message });
        }
    };

    const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        setUploading(true);
        setMessage(null);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await fetch('/api/plugins/upload', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Upload failed");

            setMessage({ type: 'success', text: `Plugin uploaded: ${data.plugin_id}` });
            await fetchPlugins();
        } catch (err: any) {
            setMessage({ type: 'error', text: err.message });
        } finally {
            setUploading(false);
            // Reset input
            event.target.value = '';
        }
    };

    const handleDelete = async (pluginId: string) => {
        if (!confirm(`Are you sure you want to delete plugin: ${pluginId}?`)) return;

        try {
            const res = await fetch(`/api/plugins/${pluginId}`, { method: 'DELETE' });
            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.detail || "Delete failed");
            }
            await fetchPlugins();
            setMessage({ type: 'success', text: "Plugin deleted" });
        } catch (err: any) {
            setMessage({ type: 'error', text: err.message });
        }
    };

    return (
        <div className="p-6 max-w-5xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center bg-surface/30 p-4 rounded-xl border border-white/5">
                <div>
                    <h2 className="text-2xl font-bold flex items-center gap-2">
                        <Package className="text-primary" /> Plugin Management
                    </h2>
                    <p className="text-muted text-sm mt-1">Manage agent capabilities and extensions</p>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={handleReload}
                        className="flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-white/5 transition-colors text-sm font-semibold"
                        disabled={loading}
                    >
                        <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
                        Reload Registry
                    </button>
                    <label className={`flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary-hover rounded-lg cursor-pointer transition-colors text-sm font-bold text-black ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}>
                        <Upload size={16} />
                        {uploading ? 'Uploading...' : 'Upload Plugin (.zip)'}
                        <input
                            type="file"
                            accept=".zip"
                            className="hidden"
                            onChange={handleUpload}
                            disabled={uploading}
                        />
                    </label>
                </div>
            </div>

            {/* Message Area */}
            {message && (
                <div className={`p-4 rounded-lg flex items-center gap-2 ${message.type === 'success' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'}`}>
                    {message.type === 'success' ? <CheckCircle size={18} /> : <XCircle size={18} />}
                    {message.text}
                </div>
            )}

            {/* Plugin Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {plugins.map((plugin) => (
                    <div key={plugin.id} className={`relative group glass-card p-5 transition-all hover:-translate-y-1 ${plugin.status === 'error' ? 'border-red-500/30' : ''}`}>
                        <div className="flex justify-between items-start mb-3">
                            <div className={`p-2 rounded-lg ${plugin.is_builtin ? 'bg-blue-500/20 text-blue-400' : 'bg-purple-500/20 text-purple-400'}`}>
                                <Package size={20} />
                            </div>

                            <div className="flex items-center gap-2">
                                {/* Toggle Switch */}
                                <button
                                    onClick={() => handleToggle(plugin.id, plugin.status)}
                                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${plugin.status === 'active' ? 'bg-emerald-500' : 'bg-gray-600'}`}
                                    title={plugin.status === 'active' ? 'Disable Plugin' : 'Enable Plugin'}
                                >
                                    <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${plugin.status === 'active' ? 'translate-x-6' : 'translate-x-1'}`} />
                                </button>

                                {!plugin.is_builtin && (
                                    <button
                                        onClick={() => handleDelete(plugin.id)}
                                        className="text-muted hover:text-red-400 transition-colors p-1"
                                        title="Delete Plugin"
                                    >
                                        <Trash2 size={16} />
                                    </button>
                                )}
                            </div>
                        </div>

                        <div className="flex justify-between items-center mb-2">
                            <h3 className="font-bold text-lg">{plugin.name}</h3>
                            <span className={`text-xs px-2 py-1 rounded font-mono ${plugin.status === 'active' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
                                {plugin.status.toUpperCase()}
                            </span>
                        </div>

                        <div className="flex gap-2 text-xs text-muted mb-3 font-mono">
                            <span>v{plugin.version}</span>
                            <span>•</span>
                            <span>{plugin.is_builtin ? 'Built-in' : 'User Uploaded'}</span>
                        </div>

                        <p className="text-sm text-text/80 h-10 overflow-hidden text-ellipsis line-clamp-2 mb-2">
                            {plugin.description}
                        </p>

                        {plugin.error && (
                            <div className="mt-3 p-2 bg-red-950/30 border border-red-500/20 rounded text-xs text-red-300 break-all font-mono">
                                Error: {plugin.error}
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {plugins.length === 0 && !loading && (
                <div className="text-center py-20 text-muted">
                    <Package size={48} className="mx-auto mb-4 opacity-20" />
                    <p>No plugins found.</p>
                </div>
            )}
        </div>
    );
};

export default PluginManager;
