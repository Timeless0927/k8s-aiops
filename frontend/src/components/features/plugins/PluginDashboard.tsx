import React, { useEffect, useState } from 'react';
import { Package, Upload, Trash2, RefreshCw, CheckCircle, XCircle } from 'lucide-react';

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

const PluginDashboard: React.FC = () => {
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
        <div className="p-6 max-w-6xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                <div>
                    <h2 className="text-2xl font-bold flex items-center gap-2 text-gray-900">
                        <Package className="text-primary" /> Plugin Management
                    </h2>
                    <p className="text-gray-500 text-sm mt-1">Manage agent capabilities and extensions</p>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={handleReload}
                        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-50 hover:bg-gray-100 border border-gray-200 transition-colors text-sm font-semibold text-gray-700"
                        disabled={loading}
                    >
                        <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
                        Reload Registry
                    </button>
                    <label className={`flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary-hover text-white rounded-lg cursor-pointer transition-colors text-sm font-bold shadow-sm ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}>
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
                <div className={`p-4 rounded-lg flex items-center gap-2 border ${message.type === 'success' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-red-50 text-red-700 border-red-200'}`}>
                    {message.type === 'success' ? <CheckCircle size={18} /> : <XCircle size={18} />}
                    <span className="text-sm font-medium">{message.text}</span>
                </div>
            )}

            {/* Plugin Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {plugins.map((plugin) => (
                    <div key={plugin.id} className={`relative group bg-white rounded-xl p-5 border shadow-sm transition-all hover:shadow-lg hover:border-primary/30 ${plugin.status === 'error' ? 'border-red-200 bg-red-50/50' : 'border-gray-200'}`}>
                        <div className="flex justify-between items-start mb-4">
                            <div className={`p-2.5 rounded-lg shadow-sm border ${plugin.is_builtin ? 'bg-blue-50 text-blue-600 border-blue-100' : 'bg-purple-50 text-purple-600 border-purple-100'}`}>
                                <Package size={22} />
                            </div>

                            <div className="flex items-center gap-2">
                                {/* Toggle Switch */}
                                <button
                                    onClick={() => handleToggle(plugin.id, plugin.status)}
                                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary ${plugin.status === 'active' ? 'bg-emerald-500' : 'bg-gray-300'}`}
                                    title={plugin.status === 'active' ? 'Disable Plugin' : 'Enable Plugin'}
                                >
                                    <span className={`inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition-transform ${plugin.status === 'active' ? 'translate-x-6' : 'translate-x-1'}`} />
                                </button>

                                {!plugin.is_builtin && (
                                    <button
                                        onClick={() => handleDelete(plugin.id)}
                                        className="text-gray-400 hover:text-red-500 transition-colors p-1.5 hover:bg-red-50 rounded"
                                        title="Delete Plugin"
                                    >
                                        <Trash2 size={16} />
                                    </button>
                                )}
                            </div>
                        </div>

                        <div className="flex justify-between items-center mb-2">
                            <h3 className="font-bold text-lg text-gray-900">{plugin.name}</h3>
                            <span className={`text-xs px-2.5 py-1 rounded-full font-bold tracking-wide ${plugin.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-600'}`}>
                                {plugin.status.toUpperCase()}
                            </span>
                        </div>

                        <div className="flex gap-2 text-xs text-gray-500 mb-4 font-mono items-center">
                            <span className="bg-gray-100 px-1.5 py-0.5 rounded">v{plugin.version}</span>
                            <span>•</span>
                            <span>{plugin.is_builtin ? 'Built-in' : 'User Uploaded'}</span>
                        </div>

                        <p className="text-sm text-gray-600 h-10 overflow-hidden text-ellipsis line-clamp-2 mb-3">
                            {plugin.description}
                        </p>

                        {plugin.error && (
                            <div className="mt-3 p-3 bg-red-50 border border-red-100 rounded-lg text-xs text-red-600 break-all font-mono">
                                <strong>Error:</strong> {plugin.error}
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {plugins.length === 0 && !loading && (
                <div className="text-center py-24 bg-white rounded-xl border border-gray-200 border-dashed">
                    <Package size={48} className="mx-auto mb-4 text-gray-300" />
                    <p className="text-gray-500 font-medium">No plugins found.</p>
                    <p className="text-sm text-muted">Upload a zip file to add new capabilities.</p>
                </div>
            )}
        </div>
    );
};

export default PluginDashboard;
