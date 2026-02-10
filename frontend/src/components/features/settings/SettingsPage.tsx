import React, { useEffect, useState } from 'react';
import { settingsApi, SystemSetting } from '../../../api/settings';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronRight, Activity, MessageSquare, Bell, Cpu, Settings as SettingsIcon, Eye, EyeOff, CheckCircle, AlertCircle } from 'lucide-react';
import AutomationLogs from '../../AutomationLogs';

// Translation Maps
const KEY_LABELS: Record<string, string> = {
    'openai_api_key': 'OpenAI API 密钥 (Key)',
    'openai_model_name': '模型名称 (Model Name)',
    'openai_base_url': 'API 基础地址 (Base URL)',
    'prometheus_url': 'Prometheus API 地址',
    'loki_url': 'Loki API 地址',
    'grafana_url': 'Grafana 仪表盘地址',
    'dingtalk_webhook_url': '钉钉 Webhook 地址',
    'dingtalk_secret': '钉钉加签密钥 (Secret)',
    'enable_auto_fix': '启用自动修复 (Auto Fix)'
};

const CATEGORY_LABELS: Record<string, string> = {
    'llm': '大模型配置 (LLM)',
    'monitoring': '监控系统 (Monitoring)',
    'notification': '通知设置 (Notification)',
    'automation': '自动化 (Automation)',
    'other': '其他设置'
};

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
            setError('加载设置失败');
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async (key: string, newValue: string) => {
        setSavingKey(key);
        try {
            await settingsApi.update(key, newValue);
            setSettings(prev => prev.map(s => s.key === key ? { ...s, value: newValue } : s));
        } catch (err) {
            alert('保存失败');
        } finally {
            setSavingKey(null);
        }
    };

    // Group settings
    const groups = settings.reduce((acc, output) => {
        const cat = output.category || 'other';
        if (!acc[cat]) acc[cat] = [];
        acc[cat].push(output);
        return acc;
    }, {} as Record<string, SystemSetting[]>);

    const categories = ['llm', 'monitoring', 'notification', 'automation', 'other'].filter(c => groups[c]);

    if (loading) return <div className="p-8 text-slate-500">正在加载设置...</div>;

    return (
        <div className="flex-1 bg-slate-50 p-8 overflow-y-auto">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-3xl font-bold text-slate-900 mb-2">系统设置 (System Settings)</h1>
                <p className="text-slate-500 mb-8">管理 AI Agent 的全局配置与连接信息。</p>

                {error && <div className="bg-red-50 text-red-600 p-4 rounded mb-6">{error}</div>}

                <div className="space-y-4">
                    {categories.map(cat => (
                        <CategorySection
                            key={cat}
                            category={cat}
                            settings={groups[cat]}
                            onSave={handleSave}
                            savingKey={savingKey}
                            allSettings={settings}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
};

const CategorySection: React.FC<{
    category: string;
    settings: SystemSetting[];
    onSave: (k: string, v: string) => void;
    savingKey: string | null;
    allSettings: SystemSetting[];
}> = ({ category, settings, onSave, savingKey, allSettings }) => {
    const [isOpen, setIsOpen] = useState(true);

    const getIcon = (c: string) => {
        switch (c) {
            case 'llm': return <MessageSquare className="w-5 h-5 text-indigo-500" />;
            case 'monitoring': return <Activity className="w-5 h-5 text-emerald-500" />;
            case 'notification': return <Bell className="w-5 h-5 text-amber-500" />;
            case 'automation': return <Cpu className="w-5 h-5 text-red-500" />;
            default: return <SettingsIcon className="w-5 h-5 text-slate-500" />;
        }
    };

    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="w-full flex items-center justify-between p-4 bg-slate-50 hover:bg-slate-100 transition-colors"
            >
                <div className="flex items-center gap-3">
                    {getIcon(category)}
                    <h2 className="text-lg font-semibold text-slate-800">{CATEGORY_LABELS[category] || category}</h2>
                    <span className="text-xs font-mono bg-white border border-slate-200 text-slate-500 px-2 py-0.5 rounded-full">
                        {settings.length} 项
                    </span>
                </div>
                {isOpen ? <ChevronDown className="w-5 h-5 text-slate-400" /> : <ChevronRight className="w-5 h-5 text-slate-400" />}
            </button>

            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="border-t border-slate-100"
                    >
                        <div className="p-6 space-y-6">
                            {/* Special Actions for Categories */}
                            {category === 'llm' && (
                                <div className="border-b border-slate-100 pb-4 mb-4">
                                    <TestLLMButton settings={allSettings} />
                                </div>
                            )}

                            {settings.map(s => (
                                <SettingCard
                                    key={s.key}
                                    setting={s}
                                    onSave={onSave}
                                    isSaving={savingKey === s.key}
                                />
                            ))}

                            {/* Automation Logs Table */}
                            {category === 'automation' && (
                                <AutomationLogs />
                            )}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

const TestLLMButton: React.FC<{ settings: SystemSetting[] }> = ({ settings }) => {
    const [testing, setTesting] = useState(false);
    const [result, setResult] = useState<{ success: boolean; msg: string } | null>(null);

    const handleTest = async () => {
        setTesting(true);
        setResult(null);
        const apiKey = settings.find(s => s.key === 'openai_api_key')?.value || '';
        const baseUrl = settings.find(s => s.key === 'openai_base_url')?.value || '';
        const model = settings.find(s => s.key === 'openai_model_name')?.value || 'gpt-4-turbo';

        try {
            const res = await settingsApi.testLLM({ api_key: apiKey, base_url: baseUrl, model_name: model });
            setResult({ success: true, msg: "连接成功: " + res.message });
        } catch (e: any) {
            setResult({ success: false, msg: "测试失败: " + e.message });
        } finally {
            setTesting(false);
        }
    };

    return (
        <div className="flex flex-col items-end gap-2">
            <button
                onClick={handleTest}
                disabled={testing}
                className="bg-indigo-50 hover:bg-indigo-100 text-indigo-700 px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
            >
                {testing ? <Activity className="w-4 h-4 animate-spin" /> : <Activity className="w-4 h-4" />}
                {testing ? '正在测试...' : '测试连接 (Test Connection)'}
            </button>
            {result && (
                <motion.div
                    initial={{ opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }}
                    className={`text-sm flex items-center gap-1.5 px-3 py-1.5 rounded-md ${result.success ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'
                        }`}
                >
                    {result.success ? <CheckCircle size={14} /> : <AlertCircle size={14} />}
                    {result.msg}
                </motion.div>
            )}
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
    const [showPassword, setShowPassword] = useState(false);

    useEffect(() => { setValue(setting.value); }, [setting.value]);

    // Check if the setting is a secret (key, secret, token)
    const isSecret = /key|secret|token/i.test(setting.key);
    // Check if setting is boolean
    const isBoolean = setting.key === 'enable_auto_fix';

    return (
        <div>
            <div className="flex justify-between items-start mb-2">
                <div>
                    <h3 className="font-medium text-slate-900">{KEY_LABELS[setting.key] || setting.key}</h3>
                    <p className="text-sm text-slate-500">{setting.description || "无描述"}</p>
                </div>
            </div>
            <div className="flex gap-3">
                <div className="relative flex-1 flex items-center">
                    {isBoolean ? (
                        <div className="flex items-center gap-3">
                            <button
                                onClick={() => {
                                    const newVal = value === 'true' ? 'false' : 'true';
                                    setValue(newVal);
                                    setDirty(true);
                                }}
                                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${value === 'true' ? 'bg-indigo-600' : 'bg-slate-200'
                                    }`}
                            >
                                <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${value === 'true' ? 'translate-x-6' : 'translate-x-1'
                                    }`} />
                            </button>
                            <span className="text-sm font-medium text-slate-700">
                                {value === 'true' ? '已启用 (True)' : '已禁用 (False)'}
                            </span>
                        </div>
                    ) : (
                        <>
                            <input
                                type={isSecret && !showPassword ? "password" : "text"}
                                value={value}
                                onChange={(e) => { setValue(e.target.value); setDirty(true); }}
                                className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all pr-10"
                                placeholder="请输入..."
                            />
                            {isSecret && (
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                                >
                                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                                </button>
                            )}
                        </>
                    )}
                </div>
                <button
                    onClick={() => { onSave(setting.key, value); setDirty(false); }}
                    disabled={!dirty || isSaving}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${dirty
                        ? 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm'
                        : 'bg-slate-100 text-slate-400 cursor-not-allowed'
                        }`}
                >
                    {isSaving ? '...' : '保存'}
                </button>
            </div>
        </div>
    );
};
