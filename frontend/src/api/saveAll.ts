import { apiClient } from './client';
import { SaveAllRequest } from '../types';

export const saveAllApi = {
  save: async (data: SaveAllRequest): Promise<{ success: boolean; message: string }> => {
    const response = await apiClient.post('/save-all', data);
    return response.data;
  },
};

