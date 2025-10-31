import { create } from 'zustand';

interface SelectionStore {
  selectedTypeCode: string | null;
  selectedStateId: string | null;
  selectedOperationId: string | null;
  
  selectType: (code: string) => void;
  selectState: (id: string | null) => void;
  selectOperation: (id: string | null) => void;
  clearSelection: () => void;
}

export const useSelectionStore = create<SelectionStore>((set) => ({
  selectedTypeCode: null,
  selectedStateId: null,
  selectedOperationId: null,
  
  selectType: (code) => set({ selectedTypeCode: code, selectedStateId: null, selectedOperationId: null }),
  selectState: (id) => set({ selectedStateId: id, selectedOperationId: null }),
  selectOperation: (id) => set({ selectedOperationId: id, selectedStateId: null }),
  clearSelection: () => set({ selectedTypeCode: null, selectedStateId: null, selectedOperationId: null }),
}));

