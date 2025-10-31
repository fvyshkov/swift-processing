import React, { useState } from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Checkbox,
  Typography,
  IconButton,
  Tooltip,
  Collapse,
  Chip,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import { useStates } from '../../hooks/useStates';
import { useOperations } from '../../hooks/useOperations';
import { useSelectionStore } from '../../store/selectionStore';
import { useChangesStore } from '../../store/changesStore';
import { useType } from '../../hooks/useTypes';
import { ProcessState, ProcessOperation } from '../../types';
import ConfirmDialog from '../common/ConfirmDialog';

interface Props {
  typeCode: string;
}

export default function StatesListSection({ typeCode }: Props) {
  const { data: serverStates, isLoading: statesLoading } = useStates(typeCode);
  const { data: serverOperations, isLoading: operationsLoading } = useOperations(typeCode);
  const { data: type } = useType(typeCode);
  const { selectedStateId, selectedOperationId, selectState, selectOperation } = useSelectionStore();
  const { createState, deleteState, createOperation, deleteOperation, states: stateChanges, operations: operationChanges } = useChangesStore();
  
  const [expandedStates, setExpandedStates] = useState<Set<string>>(new Set());
  const [deleteDialog, setDeleteDialog] = useState<{
    open: boolean;
    itemId: string;
    itemCode: string;
    itemType: 'state' | 'operation';
  }>({ open: false, itemId: '', itemCode: '', itemType: 'state' });
  
  // Merge server states with changes
  const states = React.useMemo(() => {
    if (!serverStates) return [];
    let result = [...serverStates, ...stateChanges.created.filter(s => s.type_id === type?.id)];
    result = result.filter(s => !stateChanges.deleted.includes(s.id));
    return result;
  }, [serverStates, stateChanges, type]);
  
  // Merge server operations with changes
  const operations = React.useMemo(() => {
    if (!serverOperations) return [];
    let result = [...serverOperations, ...operationChanges.created.filter(o => o.type_id === type?.id)];
    result = result.filter(o => !operationChanges.deleted.includes(o.id));
    return result;
  }, [serverOperations, operationChanges, type]);
  
  // Build state -> operations map
  const stateOperationsMap = React.useMemo(() => {
    const map = new Map<string, ProcessOperation[]>();
    operations.forEach(op => {
      (op.available_state_ids || []).forEach(stateId => {
        if (!map.has(stateId)) {
          map.set(stateId, []);
        }
        map.get(stateId)!.push(op);
      });
    });
    return map;
  }, [operations]);
  
  // Expand all states by default
  React.useEffect(() => {
    if (states.length > 0) {
      setExpandedStates(new Set(states.map(s => s.id)));
    }
  }, [states]);
  
  const toggleState = (stateId: string, event: React.MouseEvent) => {
    event.stopPropagation();
    const newExpanded = new Set(expandedStates);
    if (newExpanded.has(stateId)) {
      newExpanded.delete(stateId);
    } else {
      newExpanded.add(stateId);
    }
    setExpandedStates(newExpanded);
  };
  
  const handleAddState = () => {
    if (!type) return;
    
    const stateNum = states.length + 1;
    const newState: ProcessState = {
      id: crypto.randomUUID(),
      type_id: type.id,
      code: `STATE_${stateNum}`,
      name_en: `New State ${stateNum}`,
      name_ru: `Новое состояние ${stateNum}`,
      color_code: '#FFFFFF',
      allow_edit: true,
      allow_delete: true,
      start: false,
    };
    
    createState(newState);
    selectState(newState.id);
  };
  
  const handleAddOperation = () => {
    if (!selectedStateId || !type) return;
    
    const opNum = operations.length + 1;
    const newOperation: ProcessOperation = {
      id: crypto.randomUUID(),
      type_id: type.id,
      code: `OPERATION_${opNum}`,
      name_en: `New Operation ${opNum}`,
      name_ru: `Новая операция ${opNum}`,
      icon: '',
      resource_url: '',
      availability_condition: '',
      cancel: false,
      move_to_state_script: '',
      workflow: '',
      database: '',
      available_state_ids: [selectedStateId]
    };
    
    createOperation(newOperation);
    selectOperation(newOperation.id);
    
    // Expand the state to show new operation
    const newExpanded = new Set(expandedStates);
    newExpanded.add(selectedStateId);
    setExpandedStates(newExpanded);
  };
  
  const handleDelete = (itemType: 'state' | 'operation') => {
    if (itemType === 'state' && selectedStateId) {
      const state = states.find(s => s.id === selectedStateId);
      if (!state) return;
      
      setDeleteDialog({
        open: true,
        itemId: selectedStateId,
        itemCode: state.code,
        itemType: 'state'
      });
    } else if (itemType === 'operation' && selectedOperationId) {
      const operation = operations.find(o => o.id === selectedOperationId);
      if (!operation) return;
      
      setDeleteDialog({
        open: true,
        itemId: selectedOperationId,
        itemCode: operation.code,
        itemType: 'operation'
      });
    }
  };
  
  const confirmDelete = () => {
    if (deleteDialog.itemType === 'state') {
      deleteState(deleteDialog.itemId);
      selectState(null);
    } else {
      deleteOperation(deleteDialog.itemId);
      selectOperation(null);
    }
    setDeleteDialog({ open: false, itemId: '', itemCode: '', itemType: 'state' });
  };
  
  const cancelDelete = () => {
    setDeleteDialog({ open: false, itemId: '', itemCode: '', itemType: 'state' });
  };
  
  if (statesLoading || operationsLoading) {
    return <Typography variant="caption">Loading...</Typography>;
  }
  
  return (
    <Box>
      {/* Action buttons */}
      <Box sx={{ display: 'flex', gap: 0.5, mb: 1, pb: 0.5, borderBottom: 1, borderColor: 'divider' }}>
        <Tooltip title="Add state">
          <IconButton size="small" onClick={handleAddState}>
            <AddIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Add operation to selected state">
          <IconButton size="small" onClick={handleAddOperation} disabled={!selectedStateId}>
            <AddIcon fontSize="small" color={selectedStateId ? "primary" : "disabled"} />
          </IconButton>
        </Tooltip>
        <Tooltip title="Delete selected item">
          <IconButton size="small" onClick={() => handleDelete(selectedOperationId ? 'operation' : 'state')} disabled={!selectedStateId && !selectedOperationId}>
            <DeleteIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
      
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell sx={{ py: 0.5, fontSize: '0.75rem', width: 24 }}></TableCell>
              <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }}>Code</TableCell>
              <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }}>Name (EN)</TableCell>
              <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }}>Color</TableCell>
              <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }} align="center">E</TableCell>
              <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }} align="center">D</TableCell>
              <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }} align="center">S</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {states?.map((state) => {
              const stateOperations = stateOperationsMap.get(state.id) || [];
              const isExpanded = expandedStates.has(state.id);
              const hasOperations = stateOperations.length > 0;
              
              return (
                <React.Fragment key={state.id}>
                  {/* State row */}
                  <TableRow
                    selected={selectedStateId === state.id}
                    onClick={() => selectState(state.id)}
                    sx={{
                      cursor: 'pointer',
                      bgcolor: state.color_code || 'transparent',
                      '&:hover': { opacity: 0.85 },
                    }}
                  >
                    <TableCell sx={{ py: 0.5, px: 0.5 }}>
                      {hasOperations && (
                        <IconButton
                          size="small"
                          onClick={(e) => toggleState(state.id, e)}
                          sx={{ p: 0 }}
                        >
                          {isExpanded ? <ExpandMoreIcon fontSize="small" /> : <ChevronRightIcon fontSize="small" />}
                        </IconButton>
                      )}
                    </TableCell>
                    <TableCell sx={{ py: 0.5, fontSize: '0.75rem', fontWeight: 'bold' }}>{state.code}</TableCell>
                    <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }}>{state.name_en}</TableCell>
                    <TableCell sx={{ py: 0.5 }}>
                      <Box
                        sx={{
                          width: 16,
                          height: 16,
                          bgcolor: state.color_code || '#fff',
                          border: '1px solid',
                          borderColor: 'divider',
                          borderRadius: 0.5,
                        }}
                      />
                    </TableCell>
                    <TableCell sx={{ py: 0.5 }} align="center">
                      <Checkbox checked={state.allow_edit} disabled size="small" sx={{ p: 0 }} />
                    </TableCell>
                    <TableCell sx={{ py: 0.5 }} align="center">
                      <Checkbox checked={state.allow_delete} disabled size="small" sx={{ p: 0 }} />
                    </TableCell>
                    <TableCell sx={{ py: 0.5 }} align="center">
                      <Checkbox checked={state.start} disabled size="small" sx={{ p: 0 }} />
                    </TableCell>
                  </TableRow>
                  
                  {/* Operations rows (nested) */}
                  {hasOperations && (
                    <TableRow>
                      <TableCell colSpan={7} sx={{ p: 0, border: 0 }}>
                        <Collapse in={isExpanded} timeout="auto" unmountOnExit>
                          <Table size="small">
                            <TableBody>
                              {stateOperations.map((operation) => (
                                <TableRow
                                  key={operation.id}
                                  selected={selectedOperationId === operation.id}
                                  onClick={() => selectOperation(operation.id)}
                                  sx={{
                                    cursor: 'pointer',
                                    bgcolor: 'action.hover',
                                    '&:hover': { bgcolor: 'action.selected' },
                                  }}
                                >
                                  <TableCell sx={{ py: 0.5, px: 0.5, width: 24 }}></TableCell>
                                  <TableCell sx={{ py: 0.5, fontSize: '0.7rem', pl: 3 }}>
                                    {operation.code}
                                  </TableCell>
                                  <TableCell sx={{ py: 0.5, fontSize: '0.7rem' }}>
                                    {operation.name_en}
                                  </TableCell>
                                  <TableCell sx={{ py: 0.5, fontSize: '0.7rem' }}>
                                    {operation.icon || '-'}
                                  </TableCell>
                                  <TableCell sx={{ py: 0.5 }} align="center" colSpan={3}>
                                    {operation.cancel && <Chip label="Cancel" size="small" color="warning" sx={{ height: 16, fontSize: '0.6rem' }} />}
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </Collapse>
                      </TableCell>
                    </TableRow>
                  )}
                </React.Fragment>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
      
      {/* Delete confirmation dialog */}
      <ConfirmDialog
        open={deleteDialog.open}
        title={deleteDialog.itemType === 'state' ? 'Delete State' : 'Delete Operation'}
        message={`Delete ${deleteDialog.itemType} ${deleteDialog.itemCode}?`}
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
    </Box>
  );
}

