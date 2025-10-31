import { apiClient } from './client';
import { ProcessType } from '../types';

export const typesApi = {
  getAll: async (): Promise<ProcessType[]> => {
    const response = await apiClient.get('/types');
    return response.data;
  },

  getByCode: async (code: string): Promise<ProcessType> => {
    const response = await apiClient.get(`/types/${code}`);
    return response.data;
  },

  create: async (data: Partial<ProcessType>): Promise<ProcessType> => {
    const response = await apiClient.post('/types', data);
    return response.data;
  },

  update: async (code: string, data: Partial<ProcessType>): Promise<ProcessType> => {
    const response = await apiClient.put(`/types/${code}`, data);
    return response.data;
  },
};

