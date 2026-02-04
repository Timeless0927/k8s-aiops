import { API_BASE_URL } from '../config';

export interface SystemSetting {
    key: string;
    value: string;
    category: string;
    description?: string;
}

export const settingsApi = {
    getAll: async (): Promise<SystemSetting[]> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/settings`);
        if (!response.ok) throw new Error('Failed to fetch settings');
        return response.json();
    },

    update: async (key: string, value: string): Promise<SystemSetting> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/settings/${key}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ value }),
        });
        if (!response.ok) throw new Error('Failed to update setting');
        return response.json();
    },
};
