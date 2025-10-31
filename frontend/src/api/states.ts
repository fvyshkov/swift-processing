import { apiClient } from './client';
import { ProcessState } from '../types';

export const statesApi = {
  getByType: async (typeCode: string): Promise<ProcessState[]> => {
    const response = await apiClient.get(`/types/${typeCode}/states`);
    return response.data;
  },

  getById: async (stateId: string): Promise<ProcessState> => {
    const response = await apiClient.get(`/states/${stateId}`);
    return response.data;
  },

  create: async (typeCode: string, data: Partial<ProcessState>): Promise<ProcessState> => {
    const response = await apiClient.post(`/types/${typeCode}/states`, data);
    return response.data;
  },

  update: async (stateId: string, data: Partial<ProcessState>): Promise<ProcessState> => {
    const response = await apiClient.put(`/states/${stateId}`, data);
    return response.data;
  },

  delete: async (stateId: string): Promise<void> => {
    await apiClient.delete(`/states/${stateId}`);
  },
};

