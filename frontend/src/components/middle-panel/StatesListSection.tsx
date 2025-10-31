import React from 'react';
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
} from '@mui/material';
import { useStates } from '../../hooks/useStates';
import { useSelectionStore } from '../../store/selectionStore';

interface Props {
  typeCode: string;
}

export default function StatesListSection({ typeCode }: Props) {
  const { data: states, isLoading } = useStates(typeCode);
  const { selectedStateId, selectState } = useSelectionStore();
  
  if (isLoading) {
    return <Typography variant="caption">Loading states...</Typography>;
  }
  
  return (
    <Box>
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
    </Box>
  );
}

