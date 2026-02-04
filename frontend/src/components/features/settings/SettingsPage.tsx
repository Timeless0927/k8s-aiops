import React, { useEffect, useState } from 'react';
import { settingsApi, SystemSetting } from '../../../api/settings';
import { motion } from 'framer-motion';

export const SettingsPage: React.FC = () => {
    const [settings, setSettings] = useState<SystemSetting[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [savingKey, setSavingKey] = useState<string | null>(null);

    useEffect(() => {
        loadSettings();
    }, []);

    const loadSettings = async () => {
        try {
            const data = await settingsApi.getAll();
            setSettings(data);
        } catch (err) {
            setError('Failed to load settings');
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async (key: string, newValue: string) => {
        setSavingKey(key);
        try {
            await settingsApi.update(key, newValue);
            // Optimistic update
            setSettings(prev => prev.map(s => s.key === key ? { ...s, value: newValue } : s));
        } catch (err) {
            alert('Failed to save setting');
        } finally {
            setSavingKey(null);
        }
    };

    if (loading) return <div className="p-8 text-slate-500">Loading settings...</div>;

    return (
        <div className="flex-1 bg-slate-50 p-8 overflow-y-auto">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-3xl font-bold text-slate-900 mb-2">System Settings</h1>
                <p className="text-slate-500 mb-8">Manage global configuration for the AI Agent.</p>

                {error && <div className="bg-red-50 text-red-600 p-4 rounded mb-6">{error}</div>}

                <div className="space-y-6">
                    {settings.map((setting) => (
                        <SettingCard
                            key={setting.key}
                            setting={setting}
                            onSave={handleSave}
                            isSaving={savingKey === setting.key}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
};

const SettingCard: React.FC<{
    setting: SystemSetting;
    onSave: (key: string, val: string) => void;
    isSaving: boolean;
}> = ({ setting, onSave, isSaving }) => {
    const [value, setValue] = useState(setting.value);
    const [dirty, setDirty] = useState(false);

    // Sync state if prop changes (e.g. initial load)
    useEffect(() => { setValue(setting.value); }, [setting.value]);

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-xl shadow-sm border border-slate-200 p-6"
        >
            <div className="flex justify-between items-start mb-4">
                <div>
                    <h3 className="font-semibold text-slate-900">{setting.key}</h3>
                    <p className="text-sm text-slate-500 mt-1">{setting.description || "No description provided."}</p>
                </div>
                <span className="text-xs font-mono bg-slate-100 text-slate-600 px-2 py-1 rounded">
                    {setting.category}
                </span>
            </div>

            <div className="flex gap-4">
                <input
                    type="text"
                    value={value}
                    onChange={(e) => { setValue(e.target.value); setDirty(true); }}
                    className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all"
                    placeholder="Enter value..."
                />
                <button
                    onClick={() => { onSave(setting.key, value); setDirty(false); }}
                    disabled={!dirty || isSaving}
                    className={`px-6 py-2 rounded-lg font-medium transition-all ${dirty
                            ? 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-md'
                            : 'bg-slate-100 text-slate-400 cursor-not-allowed'
                        }`}
                >
                    {isSaving ? 'Saving...' : 'Save'}
                </button>
            </div>
        </motion.div>
    );
};
