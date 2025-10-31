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
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import { useStates } from '../../hooks/useStates';
import { useSelectionStore } from '../../store/selectionStore';
import { useChangesStore } from '../../store/changesStore';
import { useType } from '../../hooks/useTypes';
import { ProcessState } from '../../types';
import ConfirmDialog from '../common/ConfirmDialog';

interface Props {
  typeCode: string;
}

export default function StatesListSection({ typeCode }: Props) {
  const { data: serverStates, isLoading } = useStates(typeCode);
  const { data: type } = useType(typeCode);
  const { selectedStateId, selectState } = useSelectionStore();
  const { createState, deleteState, states: stateChanges } = useChangesStore();
  
  const [deleteDialog, setDeleteDialog] = useState<{
    open: boolean;
    stateId: string;
    stateCode: string;
  }>({ open: false, stateId: '', stateCode: '' });
  
  // Merge server states with changes
  const states = React.useMemo(() => {
    if (!serverStates) return [];
    let result = [...serverStates, ...stateChanges.created.filter(s => s.type_id === type?.id)];
    result = result.filter(s => !stateChanges.deleted.includes(s.id));
    return result;
  }, [serverStates, stateChanges, type]);
  
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
  
  const handleDeleteState = () => {
    if (!selectedStateId) return;
    
    const state = states.find(s => s.id === selectedStateId);
    if (!state) return;
    
    setDeleteDialog({
      open: true,
      stateId: selectedStateId,
      stateCode: state.code
    });
  };
  
  const confirmDeleteState = () => {
    deleteState(deleteDialog.stateId);
    selectState(null);
    setDeleteDialog({ open: false, stateId: '', stateCode: '' });
  };
  
  const cancelDeleteState = () => {
    setDeleteDialog({ open: false, stateId: '', stateCode: '' });
  };
  
  if (isLoading) {
    return <Typography variant="caption">Loading states...</Typography>;
  }
  
  return (
    <Box>
      {/* Action buttons */}
      <Box sx={{ display: 'flex', gap: 0.5, mb: 1, pb: 0.5 }}>
        <Tooltip title="Add state">
          <IconButton size="small" onClick={handleAddState}>
            <AddIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Delete selected state">
          <IconButton size="small" onClick={handleDeleteState} disabled={!selectedStateId}>
            <DeleteIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
      
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }}>Code</TableCell>
              <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }}>Name (EN)</TableCell>
              <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }}>Color</TableCell>
              <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }} align="center">E</TableCell>
              <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }} align="center">D</TableCell>
              <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }} align="center">S</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {states?.map((state) => (
              <TableRow
                key={state.id}
                selected={selectedStateId === state.id}
                onClick={() => selectState(state.id)}
                sx={{
                  cursor: 'pointer',
                  bgcolor: state.color_code || 'transparent',
                  '&:hover': { opacity: 0.85 },
                }}
              >
                <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }}>{state.code}</TableCell>
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
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      
      {/* Delete confirmation dialog */}
      <ConfirmDialog
        open={deleteDialog.open}
        title="Delete State"
        message={`Delete state ${deleteDialog.stateCode}?`}
        onConfirm={confirmDeleteState}
        onCancel={cancelDeleteState}
      />
    </Box>
  );
}

