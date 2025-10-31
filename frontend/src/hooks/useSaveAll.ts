import { useMutation, useQueryClient } from '@tanstack/react-query';
import { saveAllApi } from '../api/saveAll';
import { useChangesStore } from '../store/changesStore';
import { SaveAllRequest } from '../types';

export const useSaveAll = () => {
  const queryClient = useQueryClient();
  const clear = useChangesStore((state) => state.clear);
  
  return useMutation({
    mutationFn: (data: SaveAllRequest) => saveAllApi.save(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['types'] });
      queryClient.invalidateQueries({ queryKey: ['states'] });
      queryClient.invalidateQueries({ queryKey: ['operations'] });
      clear();
    },
  });
};

