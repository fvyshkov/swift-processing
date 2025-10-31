import React, { useState } from 'react';
import { 
  Box, 
  TextField, 
  Popover, 
  Typography,
  InputAdornment,
  IconButton,
  Grid
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import * as MuiIcons from '@mui/icons-material';

interface Props {
  value: string;
  onChange: (icon: string) => void;
  label?: string;
}

// Popular icons list
const POPULAR_ICONS = [
  'Check', 'Cancel', 'Close', 'Done', 'Clear',
  'Payment', 'AttachMoney', 'AccountBalance', 'CreditCard',
  'Undo', 'Redo', 'Refresh', 'Sync', 'Update',
  'Edit', 'Create', 'ModeEdit', 'BorderColor',
  'Delete', 'DeleteOutline', 'Remove', 'RemoveCircle',
  'Add', 'AddCircle', 'PlusOne',
  'Send', 'Forward', 'ArrowForward', 'ArrowRight',
  'Save', 'SaveAlt', 'Backup',
  'Error', 'Warning', 'Info', 'Help',
  'Verified', 'VerifiedUser', 'Security', 'Lock',
  'Visibility', 'VisibilityOff', 'Preview',
  'Print', 'Email', 'Phone', 'Message',
  'Settings', 'Build', 'Construction', 'Engineering',
  'Schedule', 'Event', 'Today', 'CalendarToday',
  'Folder', 'FolderOpen', 'Description', 'Article',
];

const ICONS = POPULAR_ICONS;

export default function IconPicker({ value, onChange, label = 'Icon' }: Props) {
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  const [filter, setFilter] = useState('');

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
    setFilter('');
  };

  const handleSelect = (icon: string) => {
    onChange(icon);
    handleClose();
  };

  const open = Boolean(anchorEl);
  const filteredIcons = filter 
    ? ICONS.filter(icon => icon.includes(filter.toLowerCase()))
    : ICONS;

  const IconComponent = value ? (MuiIcons as any)[value] : null;

  return (
    <Box>
      <TextField
        label={label}
        value={value}
        fullWidth
        margin="dense"
        size="small"
        placeholder="Click to select icon"
        onClick={handleClick}
        InputProps={{
          readOnly: true,
          startAdornment: IconComponent ? (
            <InputAdornment position="start">
              <IconComponent sx={{ fontSize: 20 }} />
            </InputAdornment>
          ) : null,
          endAdornment: (
            <InputAdornment position="end">
              <IconButton size="small" onClick={handleClick}>
                <SearchIcon fontSize="small" />
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
        <Box sx={{ p: 2, width: 400, maxHeight: 500, overflow: 'auto' }}>
          <TextField
            placeholder="Search icons..."
            size="small"
            fullWidth
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            sx={{ mb: 2 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon fontSize="small" />
                </InputAdornment>
              ),
            }}
          />
          <Grid container spacing={1}>
            {filteredIcons.map((icon) => {
              const IconComp = (MuiIcons as any)[icon];
              if (!IconComp) return null;
              
              return (
                <Grid item xs={3} key={icon}>
                  <Box
                    onClick={() => handleSelect(icon)}
                    sx={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      p: 1,
                      cursor: 'pointer',
                      borderRadius: 1,
                      border: value === icon ? '2px solid' : '1px solid',
                      borderColor: value === icon ? 'primary.main' : 'divider',
                      bgcolor: value === icon ? 'action.selected' : 'transparent',
                      '&:hover': {
                        bgcolor: 'action.hover',
                      },
                    }}
                  >
                    <IconComp sx={{ fontSize: 32, mb: 0.5 }} />
                    <Typography variant="caption" sx={{ fontSize: '0.65rem', textAlign: 'center', wordBreak: 'break-all' }}>
                      {icon}
                    </Typography>
                  </Box>
                </Grid>
              );
            })}
          </Grid>
        </Box>
      </Popover>
    </Box>
  );
}

