import { API_BASE_URL } from '../config';

export interface AutomationLog {
    id: number;
    fingerprint: string;
    action: string;
    namespace: string | null;
    status: string;
    message: string | null;
    timestamp: string;
}

export const getAutomationLogs = async (skip: number = 0, limit: number = 50): Promise<AutomationLog[]> => {
    const response = await fetch(`${API_BASE_URL}/plugins/automation/logs?skip=${skip}&limit=${limit}`);
    if (!response.ok) {
        throw new Error('Failed to fetch automation logs');
    }
    return response.json();
};
