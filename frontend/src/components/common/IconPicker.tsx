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
import CheckIcon from '@mui/icons-material/Check';
import CancelIcon from '@mui/icons-material/Cancel';
import PaymentIcon from '@mui/icons-material/Payment';
import UndoIcon from '@mui/icons-material/Undo';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import SendIcon from '@mui/icons-material/Send';
import SaveIcon from '@mui/icons-material/Save';
import ErrorIcon from '@mui/icons-material/Error';
import WarningIcon from '@mui/icons-material/Warning';
import InfoIcon from '@mui/icons-material/Info';
import SettingsIcon from '@mui/icons-material/Settings';
import FolderIcon from '@mui/icons-material/Folder';
import DescriptionIcon from '@mui/icons-material/Description';
import ScheduleIcon from '@mui/icons-material/Schedule';
import RefreshIcon from '@mui/icons-material/Refresh';
import CloseIcon from '@mui/icons-material/Close';
import DoneIcon from '@mui/icons-material/Done';

interface Props {
  value: string;
  onChange: (icon: string) => void;
  label?: string;
}

// Icon components map
const ICON_MAP: { [key: string]: React.ComponentType } = {
  'check': CheckIcon,
  'cancel': CancelIcon,
  'payment': PaymentIcon,
  'undo': UndoIcon,
  'edit': EditIcon,
  'delete': DeleteIcon,
  'add': AddIcon,
  'send': SendIcon,
  'save': SaveIcon,
  'error': ErrorIcon,
  'warning': WarningIcon,
  'info': InfoIcon,
  'settings': SettingsIcon,
  'folder': FolderIcon,
  'description': DescriptionIcon,
  'schedule': ScheduleIcon,
  'refresh': RefreshIcon,
  'close': CloseIcon,
  'done': DoneIcon,
};

const ICONS = Object.keys(ICON_MAP);

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

  const IconComponent = value ? ICON_MAP[value] : null;

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
              const IconComp = ICON_MAP[icon];
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

