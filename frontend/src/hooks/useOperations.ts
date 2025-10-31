import { useQuery } from '@tanstack/react-query';
import { operationsApi } from '../api/operations';

export const useOperations = (typeCode: string | null) => {
  return useQuery({
    queryKey: ['operations', typeCode],
    queryFn: () => typeCode ? operationsApi.getByType(typeCode) : [],
    enabled: !!typeCode,
  });
};

