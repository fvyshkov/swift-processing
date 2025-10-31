import { useQuery } from '@tanstack/react-query';
import { statesApi } from '../api/states';

export const useStates = (typeCode: string | null) => {
  return useQuery({
    queryKey: ['states', typeCode],
    queryFn: () => typeCode ? statesApi.getByType(typeCode) : [],
    enabled: !!typeCode,
  });
};

