import { useMemo } from 'react';
import { useTypes } from './useTypes';
import { useChangesStore } from '../store/changesStore';
import { ProcessType } from '../types';

export const useTypesWithChanges = () => {
  const { data: serverTypes, isLoading, error } = useTypes();
  const { types: changes } = useChangesStore();
  
  const types = useMemo(() => {
    if (!serverTypes) return [];
    
    let result = [...serverTypes];
    
    // Add created types
    result = [...result, ...changes.created];
    
    // Apply updates
    result = result.map(type => {
      const updated = changes.updated.find(u => u.code === type.code);
      return updated || type;
    });
    
    // Remove deleted types
    result = result.filter(type => !changes.deleted.includes(type.code));
    
    return result;
  }, [serverTypes, changes]);
  
  return { data: types, isLoading, error };
};

