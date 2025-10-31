import React, { useState } from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Typography,
  IconButton,
  Tooltip,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import { useOperations } from '../../hooks/useOperations';
import { useSelectionStore } from '../../store/selectionStore';
import { useChangesStore } from '../../store/changesStore';
import { useType } from '../../hooks/useTypes';
import { ProcessOperation } from '../../types';
import ConfirmDialog from '../common/ConfirmDialog';

interface Props {
  typeCode: string;
}

export default function OperationsListSection({ typeCode }: Props) {
  const { data: serverOperations, isLoading } = useOperations(typeCode);
  const { data: type } = useType(typeCode);
  const { selectedOperationId, selectOperation } = useSelectionStore();
  const { createOperation, deleteOperation, operations: operationChanges } = useChangesStore();
  
  const [deleteDialog, setDeleteDialog] = useState<{
    open: boolean;
    operationId: string;
    operationCode: string;
  }>({ open: false, operationId: '', operationCode: '' });
  
  // Merge server operations with changes
  const operations = React.useMemo(() => {
    if (!serverOperations) return [];
    let result = [...serverOperations, ...operationChanges.created.filter(o => o.type_id === type?.id)];
    result = result.filter(o => !operationChanges.deleted.includes(o.id));
    return result;
  }, [serverOperations, operationChanges, type]);
  
  const handleAddOperation = () => {
    if (!type) return;
    
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
      available_state_ids: []
    };
    
    createOperation(newOperation);
    selectOperation(newOperation.id);
  };
  
  const handleDeleteOperation = () => {
    if (!selectedOperationId) return;
    
    const operation = operations.find(o => o.id === selectedOperationId);
    if (!operation) return;
    
    setDeleteDialog({
      open: true,
      operationId: selectedOperationId,
      operationCode: operation.code
    });
  };
  
  const confirmDeleteOperation = () => {
    deleteOperation(deleteDialog.operationId);
    selectOperation(null);
    setDeleteDialog({ open: false, operationId: '', operationCode: '' });
  };
  
  const cancelDeleteOperation = () => {
    setDeleteDialog({ open: false, operationId: '', operationCode: '' });
  };
  
  if (isLoading) {
    return <Typography variant="caption">Loading operations...</Typography>;
  }
  
  return (
    <Box>
      {/* Action buttons */}
      <Box sx={{ display: 'flex', gap: 0.5, mb: 1, pb: 0.5 }}>
        <Tooltip title="Add operation">
          <IconButton size="small" onClick={handleAddOperation}>
            <AddIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Delete selected operation">
          <IconButton size="small" onClick={handleDeleteOperation} disabled={!selectedOperationId}>
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
              <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }}>Icon</TableCell>
              <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }} align="center">Cancel</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {operations?.map((operation) => (
              <TableRow
                key={operation.id}
                selected={selectedOperationId === operation.id}
                onClick={() => selectOperation(operation.id)}
                sx={{ cursor: 'pointer', '&:hover': { bgcolor: 'action.hover' } }}
              >
                <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }}>{operation.code}</TableCell>
                <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }}>{operation.name_en}</TableCell>
                <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }}>{operation.icon || '-'}</TableCell>
                <TableCell sx={{ py: 0.5 }} align="center">
                  {operation.cancel && <Chip label="C" size="small" color="warning" sx={{ height: 16, fontSize: '0.65rem' }} />}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      
      {/* Delete confirmation dialog */}
      <ConfirmDialog
        open={deleteDialog.open}
        title="Delete Operation"
        message={`Delete operation ${deleteDialog.operationCode}?`}
        onConfirm={confirmDeleteOperation}
        onCancel={cancelDeleteOperation}
      />
    </Box>
  );
}

