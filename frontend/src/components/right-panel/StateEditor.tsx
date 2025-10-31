import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  FormControlLabel,
  Checkbox,
  Paper,
} from '@mui/material';
import { useStates } from '../../hooks/useStates';
import { useSelectionStore } from '../../store/selectionStore';
import { useChangesStore } from '../../store/changesStore';
import { ProcessState } from '../../types';
import ColorPicker from '../common/ColorPicker';
import CodeEditor from '../common/CodeEditor';

interface Props {
  stateId: string;
}

export default function StateEditor({ stateId }: Props) {
  const selectedTypeCode = useSelectionStore((state) => state.selectedTypeCode);
  const { data: states } = useStates(selectedTypeCode);
  const state = states?.find((s) => s.id === stateId);
  const updateState = useChangesStore((state) => state.updateState);
  
  const [localState, setLocalState] = useState<ProcessState | null>(null);
  
  useEffect(() => {
    if (state) {
      setLocalState(state);
    }
  }, [state]);
  
  const handleChange = (updates: Partial<ProcessState>) => {
    const updated = { ...localState, ...updates } as ProcessState;
    setLocalState(updated);
    updateState(updated);
  };
  
  if (!localState) {
    return <Typography variant="caption">Loading...</Typography>;
  }
  
  return (
    <Box sx={{ p: 1 }}>
      <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
        State Editor
      </Typography>
      <Paper sx={{ p: 1.5 }} elevation={1}>
        <TextField
          label="Code"
          value={localState.code}
          fullWidth
          margin="dense"
          size="small"
          disabled
        />
        <TextField
          label="Name (English)"
          value={localState.name_en}
          fullWidth
          margin="dense"
          size="small"
          onChange={(e) => handleChange({ name_en: e.target.value })}
        />
        <TextField
          label="Name (Russian)"
          value={localState.name_ru}
          fullWidth
          margin="dense"
          size="small"
          onChange={(e) => handleChange({ name_ru: e.target.value })}
        />
        <ColorPicker
          color={localState.color_code || '#FFFFFF'}
          onChange={(color) => handleChange({ color_code: color })}
          label="Color"
        />
        <Box sx={{ mt: 1 }}>
          <FormControlLabel
            control={
              <Checkbox
                checked={localState.allow_edit}
                onChange={(e) => handleChange({ allow_edit: e.target.checked })}
                size="small"
              />
            }
            label={<Typography variant="caption">Allow Edit</Typography>}
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={localState.allow_delete}
                onChange={(e) => handleChange({ allow_delete: e.target.checked })}
                size="small"
              />
            }
            label={<Typography variant="caption">Allow Delete</Typography>}
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={localState.start}
                onChange={(e) => handleChange({ start: e.target.checked })}
                size="small"
              />
            }
            label={<Typography variant="caption">Start State</Typography>}
          />
        </Box>
      </Paper>
    </Box>
  );
}

