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

interface Props {
  value: string;
  onChange: (icon: string) => void;
  label?: string;
}

// Popular Material Icons for operations
const ICONS = [
  'check', 'cancel', 'close', 'done', 'clear',
  'payment', 'attach_money', 'account_balance', 'credit_card',
  'undo', 'redo', 'refresh', 'sync', 'update',
  'edit', 'create', 'mode_edit', 'border_color',
  'delete', 'delete_outline', 'remove', 'remove_circle',
  'add', 'add_circle', 'plus_one',
  'send', 'forward', 'arrow_forward', 'arrow_right',
  'save', 'save_alt', 'backup',
  'error', 'warning', 'info', 'help',
  'verified', 'verified_user', 'security', 'lock',
  'visibility', 'visibility_off', 'preview',
  'print', 'email', 'phone', 'message',
  'settings', 'build', 'construction', 'engineering',
  'schedule', 'event', 'today', 'calendar_today',
  'folder', 'folder_open', 'description', 'article',
];

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
          startAdornment: value ? (
            <InputAdornment position="start">
              <Box component="i" className="material-icons" sx={{ fontSize: 20 }}>
                {value}
              </Box>
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
            {filteredIcons.map((icon) => (
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
                  <Box component="i" className="material-icons" sx={{ fontSize: 24, mb: 0.5 }}>
                    {icon}
                  </Box>
                  <Typography variant="caption" sx={{ fontSize: '0.65rem', textAlign: 'center', wordBreak: 'break-all' }}>
                    {icon}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Box>
      </Popover>
    </Box>
  );
}

