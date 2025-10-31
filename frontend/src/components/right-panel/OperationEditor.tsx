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
import CodeEditor from '../common/CodeEditor';
import IconPicker from '../common/IconPicker';

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
          InputLabelProps={{ shrink: true }}
        />
        <TextField
          label="Name (English)"
          value={localOperation.name_en}
          fullWidth
          margin="dense"
          size="small"
          onChange={(e) => handleChange({ name_en: e.target.value })}
          InputLabelProps={{ shrink: true }}
        />
        <TextField
          label="Name (Russian)"
          value={localOperation.name_ru}
          fullWidth
          margin="dense"
          size="small"
          onChange={(e) => handleChange({ name_ru: e.target.value })}
          InputLabelProps={{ shrink: true }}
        />
        <IconPicker
          value={localOperation.icon || ''}
          onChange={(icon) => handleChange({ icon })}
          label="Icon"
        />
        <TextField
          label="Workflow"
          value={localOperation.workflow || ''}
          fullWidth
          margin="dense"
          size="small"
          placeholder="Workflow name"
          onChange={(e) => handleChange({ workflow: e.target.value })}
          InputLabelProps={{ shrink: true }}
        />
        <TextField
          label="Database"
          value={localOperation.database || ''}
          fullWidth
          margin="dense"
          size="small"
          placeholder="Database name"
          onChange={(e) => handleChange({ database: e.target.value })}
          InputLabelProps={{ shrink: true }}
        />
        <CodeEditor
          value={localOperation.resource_url || ''}
          onChange={(value) => handleChange({ resource_url: value })}
          label="SQL"
          language="sql"
          minHeight={80}
        />
        <CodeEditor
          value={localOperation.move_to_state_script || ''}
          onChange={(value) => handleChange({ move_to_state_script: value })}
          label="Move to State Script (Python)"
          language="python"
          minHeight={80}
        />
        <CodeEditor
          value={localOperation.availability_condition || 'available = True'}
          onChange={(value) => handleChange({ availability_condition: value })}
          label="Availability Condition (Python)"
          language="python"
          minHeight={60}
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

