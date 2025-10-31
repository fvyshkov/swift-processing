import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  FormControlLabel,
  Checkbox,
  Paper,
} from '@mui/material';
import { useOperations } from '../../hooks/useOperations';
import { useSelectionStore } from '../../store/selectionStore';
import { useChangesStore } from '../../store/changesStore';
import { ProcessOperation } from '../../types';

interface Props {
  operationId: string;
}

export default function OperationEditor({ operationId }: Props) {
  const selectedTypeCode = useSelectionStore((state) => state.selectedTypeCode);
  const { data: operations } = useOperations(selectedTypeCode);
  const operation = operations?.find((o) => o.id === operationId);
  const updateOperation = useChangesStore((state) => state.updateOperation);
  
  const [localOperation, setLocalOperation] = useState<ProcessOperation | null>(null);
  
  useEffect(() => {
    if (operation) {
      setLocalOperation(operation);
    }
  }, [operation]);
  
  const handleChange = (updates: Partial<ProcessOperation>) => {
    const updated = { ...localOperation, ...updates } as ProcessOperation;
    setLocalOperation(updated);
    updateOperation(updated);
  };
  
  if (!localOperation) {
    return <Typography variant="caption">Loading...</Typography>;
  }
  
  return (
    <Box sx={{ p: 1 }}>
      <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
        Operation Editor
      </Typography>
      <Paper sx={{ p: 1.5 }} elevation={1}>
        <TextField
          label="Code"
          value={localOperation.code}
          fullWidth
          margin="dense"
          size="small"
          disabled
        />
        <TextField
          label="Name (English)"
          value={localOperation.name_en}
          fullWidth
          margin="dense"
          size="small"
          onChange={(e) => handleChange({ name_en: e.target.value })}
        />
        <TextField
          label="Name (Russian)"
          value={localOperation.name_ru}
          fullWidth
          margin="dense"
          size="small"
          onChange={(e) => handleChange({ name_ru: e.target.value })}
        />
        <TextField
          label="Icon"
          value={localOperation.icon || ''}
          fullWidth
          margin="dense"
          size="small"
          onChange={(e) => handleChange({ icon: e.target.value })}
        />
        <TextField
          label="Resource URL"
          value={localOperation.resource_url || ''}
          fullWidth
          margin="dense"
          size="small"
          multiline
          rows={2}
          onChange={(e) => handleChange({ resource_url: e.target.value })}
        />
        <TextField
          label="Move to State Script"
          value={localOperation.move_to_state_script || ''}
          fullWidth
          margin="dense"
          size="small"
          multiline
          rows={3}
          onChange={(e) => handleChange({ move_to_state_script: e.target.value })}
        />
        <FormControlLabel
          control={
            <Checkbox
              checked={localOperation.cancel}
              onChange={(e) => handleChange({ cancel: e.target.checked })}
              size="small"
            />
          }
          label={<Typography variant="caption">Cancel Operation</Typography>}
        />
      </Paper>
    </Box>
  );
}

