import { useQuery } from '@tanstack/react-query';
import { typesApi } from '../api/types';

export const useTypes = () => {
  return useQuery({
    queryKey: ['types'],
    queryFn: typesApi.getAll,
  });
};

export const useType = (code: string | null) => {
  return useQuery({
    queryKey: ['type', code],
    queryFn: () => code ? typesApi.getByCode(code) : null,
    enabled: !!code,
  });
};

