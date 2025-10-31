import React from 'react';
import { Box, Typography } from '@mui/material';
import { useSelectionStore } from '../../store/selectionStore';
import StateEditor from './StateEditor';
import OperationEditor from './OperationEditor';

export default function RightPanel() {
  const { selectedStateId, selectedOperationId } = useSelectionStore();
  
  if (selectedStateId) {
    return <StateEditor stateId={selectedStateId} />;
  }
  
  if (selectedOperationId) {
    return <OperationEditor operationId={selectedOperationId} />;
  }
  
  return (
    <Box sx={{ p: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
      <Typography color="text.secondary" variant="body2">
        Select state or operation
      </Typography>
    </Box>
  );
}

