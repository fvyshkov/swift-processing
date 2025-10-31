import React, { useState } from 'react';
import { Box, Popover, TextField, InputAdornment, IconButton } from '@mui/material';
import { ChromePicker, ColorResult } from 'react-color';
import PaletteIcon from '@mui/icons-material/Palette';

interface Props {
  color: string;
  onChange: (color: string) => void;
  label?: string;
}

export default function ColorPicker({ color, onChange, label = 'Color' }: Props) {
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  const [localColor, setLocalColor] = useState(color || '#FFFFFF');

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleChangeComplete = (color: ColorResult) => {
    setLocalColor(color.hex);
    onChange(color.hex);
  };

  const open = Boolean(anchorEl);

  return (
    <Box>
      <TextField
        label={label}
        value={localColor}
        fullWidth
        margin="dense"
        size="small"
        onChange={(e) => {
          setLocalColor(e.target.value);
          onChange(e.target.value);
        }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Box
                sx={{
                  width: 20,
                  height: 20,
                  bgcolor: localColor,
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 0.5,
                  cursor: 'pointer',
                }}
                onClick={handleClick}
              />
            </InputAdornment>
          ),
          endAdornment: (
            <InputAdornment position="end">
              <IconButton size="small" onClick={handleClick}>
                <PaletteIcon fontSize="small" />
              </IconButton>
            </InputAdornment>
          ),
        }}
      />
      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'left',
        }}
      >
        <ChromePicker
          color={localColor}
          onChangeComplete={handleChangeComplete}
          disableAlpha
        />
      </Popover>
    </Box>
  );
}

