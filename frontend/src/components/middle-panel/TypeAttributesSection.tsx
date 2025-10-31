import React, { useState, useEffect } from 'react';
import { Box, Typography, TextField } from '@mui/material';
import { useType } from '../../hooks/useTypes';
import { useChangesStore } from '../../store/changesStore';

interface Props {
  typeCode: string;
}

export default function TypeAttributesSection({ typeCode }: Props) {
  const { data: type, isLoading } = useType(typeCode);
  const updateType = useChangesStore((state) => state.updateType);
  const [localType, setLocalType] = useState<any>(null);
  
  useEffect(() => {
    if (type) {
      setLocalType(type);
    }
  }, [type]);
  
  const handleChange = (field: string, value: string) => {
    const updated = { ...localType, [field]: value };
    setLocalType(updated);
    updateType(updated);
  };
  
  if (isLoading) {
    return <Typography variant="caption">Loading...</Typography>;
  }
  
  if (!localType) {
    return null;
  }
  
  return (
    <Box>
      <TextField
        label="Code"
        value={localType.code}
        fullWidth
        margin="dense"
        disabled
        size="small"
      />
      <TextField
        label="Name (English)"
        value={localType.name_en}
        fullWidth
        margin="dense"
        size="small"
        onChange={(e) => handleChange('name_en', e.target.value)}
      />
      <TextField
        label="Name (Russian)"
        value={localType.name_ru}
        fullWidth
        margin="dense"
        size="small"
        onChange={(e) => handleChange('name_ru', e.target.value)}
      />
      <TextField
        label="Attributes Table"
        value={localType.attributes_table || ''}
        fullWidth
        margin="dense"
        size="small"
        onChange={(e) => handleChange('attributes_table', e.target.value)}
      />
    </Box>
  );
}

