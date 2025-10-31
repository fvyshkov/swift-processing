import { apiClient } from './client';
import { ProcessOperation } from '../types';

export const operationsApi = {
  getByType: async (typeCode: string): Promise<ProcessOperation[]> => {
    const response = await apiClient.get(`/types/${typeCode}/operations`);
    return response.data;
  },

  getById: async (operationId: string): Promise<ProcessOperation> => {
    const response = await apiClient.get(`/operations/${operationId}`);
    return response.data;
  },

  create: async (typeCode: string, data: Partial<ProcessOperation>): Promise<ProcessOperation> => {
    const response = await apiClient.post(`/types/${typeCode}/operations`, data);
    return response.data;
  },

  update: async (operationId: string, data: Partial<ProcessOperation>): Promise<ProcessOperation> => {
    const response = await apiClient.put(`/operations/${operationId}`, data);
    return response.data;
  },

  delete: async (operationId: string): Promise<void> => {
    await apiClient.delete(`/operations/${operationId}`);
  },
};

