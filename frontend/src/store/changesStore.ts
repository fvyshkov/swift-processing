import { create } from 'zustand';
import { ProcessType, ProcessState, ProcessOperation } from '../types';

interface ChangesStore {
  hasChanges: boolean;
  type: ProcessType | null;
  types: {
    created: ProcessType[];
    updated: ProcessType[];
    deleted: string[];
  };
  states: {
    created: ProcessState[];
    updated: ProcessState[];
    deleted: string[];
  };
  operations: {
    created: ProcessOperation[];
    updated: ProcessOperation[];
    deleted: string[];
  };
  
  createType: (type: ProcessType) => void;
  updateType: (type: ProcessType) => void;
  deleteType: (code: string) => void;
  createState: (state: ProcessState) => void;
  updateState: (state: ProcessState) => void;
  deleteState: (id: string) => void;
  createOperation: (op: ProcessOperation) => void;
  updateOperation: (op: ProcessOperation) => void;
  deleteOperation: (id: string) => void;
  clear: () => void;
}

export const useChangesStore = create<ChangesStore>((set) => ({
  hasChanges: false,
  type: null,
  types: {
    created: [],
    updated: [],
    deleted: [],
  },
  states: {
    created: [],
    updated: [],
    deleted: [],
  },
  operations: {
    created: [],
    updated: [],
    deleted: [],
  },
  
  createType: (type) => set((prev) => ({
    types: {
      ...prev.types,
      created: [...prev.types.created, type],
    },
    hasChanges: true,
  })),
  
  updateType: (type) => set((prev) => ({
    types: {
      ...prev.types,
      updated: [...prev.types.updated.filter(t => t.code !== type.code), type],
    },
    type,
    hasChanges: true,
  })),
  
  deleteType: (code) => set((prev) => ({
    types: {
      ...prev.types,
      deleted: [...prev.types.deleted, code],
      created: prev.types.created.filter(t => t.code !== code),
      updated: prev.types.updated.filter(t => t.code !== code),
    },
    hasChanges: true,
  })),
  
  createState: (state) => set((prev) => ({
    states: {
      ...prev.states,
      created: [...prev.states.created, state],
    },
    hasChanges: true,
  })),
  
  updateState: (state) => set((prev) => ({
    states: {
      ...prev.states,
      updated: [...prev.states.updated.filter(s => s.id !== state.id), state],
    },
    hasChanges: true,
  })),
  
  deleteState: (id) => set((prev) => ({
    states: {
      ...prev.states,
      deleted: [...prev.states.deleted, id],
      created: prev.states.created.filter(s => s.id !== id),
      updated: prev.states.updated.filter(s => s.id !== id),
    },
    hasChanges: true,
  })),
  
  createOperation: (op) => set((prev) => ({
    operations: {
      ...prev.operations,
      created: [...prev.operations.created, op],
    },
    hasChanges: true,
  })),
  
  updateOperation: (op) => set((prev) => ({
    operations: {
      ...prev.operations,
      updated: [...prev.operations.updated.filter(o => o.id !== op.id), op],
    },
    hasChanges: true,
  })),
  
  deleteOperation: (id) => set((prev) => ({
    operations: {
      ...prev.operations,
      deleted: [...prev.operations.deleted, id],
      created: prev.operations.created.filter(o => o.id !== id),
      updated: prev.operations.updated.filter(o => o.id !== id),
    },
    hasChanges: true,
  })),
  
  clear: () => set({
    hasChanges: false,
    type: null,
    types: { created: [], updated: [], deleted: [] },
    states: { created: [], updated: [], deleted: [] },
    operations: { created: [], updated: [], deleted: [] },
  }),
}));

