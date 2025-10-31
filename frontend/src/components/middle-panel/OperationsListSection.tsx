import React from 'react';
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
} from '@mui/material';
import { useOperations } from '../../hooks/useOperations';
import { useSelectionStore } from '../../store/selectionStore';

interface Props {
  typeCode: string;
}

export default function OperationsListSection({ typeCode }: Props) {
  const { data: operations, isLoading } = useOperations(typeCode);
  const { selectedOperationId, selectOperation } = useSelectionStore();
  
  if (isLoading) {
    return <Typography variant="caption">Loading operations...</Typography>;
  }
  
  return (
    <Box>
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
    </Box>
  );
}

