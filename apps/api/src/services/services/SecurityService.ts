import { api } from '@/lib/api';

export interface SecurityConfig {
    permissions: string[];
    roles: string[];
}

export class SecurityService {
    static async validatePermissions(userId: string): Promise<SecurityConfig> {
        const response = await api.get(`/api/security/permissions/${userId}`);
        return response.data;
    }

    static async updatePermissions(userId: string, permissions: string[]): Promise<void> {
        await api.post(`/api/security/permissions/${userId}`, { permissions });
    }
} 