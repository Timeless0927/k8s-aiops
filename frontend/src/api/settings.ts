import { API_BASE_URL } from '../config';

export interface SystemSetting {
    key: string;
    value: string;
    category: string;
    description?: string;
}

export const settingsApi = {
    getAll: async (): Promise<SystemSetting[]> => {
        const response = await fetch(`/api/v1/settings`);
        if (!response.ok) throw new Error('Failed to fetch settings');
        return response.json();
    },

    update: async (key: string, value: string): Promise<SystemSetting> => {
        const response = await fetch(`/api/v1/settings/${key}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ value }),
        });
        if (!response.ok) throw new Error('Failed to update setting');
        return response.json();
    },

    testLLM: async (config: { api_key: string; base_url: string; model_name: string }): Promise<{ success: boolean; message: string }> => {
        const response = await fetch(`/api/v1/settings/test-llm`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config),
        });
        if (!response.ok) throw new Error('Failed to test connection');
        return response.json();
    },
};
