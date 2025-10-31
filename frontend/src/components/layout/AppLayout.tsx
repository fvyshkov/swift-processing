import React from 'react';
import { Box, IconButton, Tooltip, useTheme } from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import TypeTree from '../navigation/TypeTree';
import MiddlePanel from '../middle-panel/MiddlePanel';
import RightPanel from '../right-panel/RightPanel';
import { useChangesStore } from '../../store/changesStore';
import { useSaveAll } from '../../hooks/useSaveAll';
import { useThemeStore } from '../../store/themeStore';

export default function AppLayout() {
  const hasChanges = useChangesStore((state) => state.hasChanges);
  const { mutate: saveAll, isPending } = useSaveAll();
  const { mode, toggleTheme } = useThemeStore();
  
  const handleSave = () => {
    const store = useChangesStore.getState();
    saveAll({
      type: store.type || undefined,
      states: store.states,
      operations: store.operations,
    });
  };
  
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Compact Header */}
      <Box sx={{ 
        px: 1, 
        py: 0.5, 
        borderBottom: 1, 
        borderColor: 'divider', 
        bgcolor: 'background.paper',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <Tooltip title={hasChanges ? 'Save changes' : 'No changes'}>
          <span>
            <IconButton
              color="primary"
              disabled={!hasChanges || isPending}
              onClick={handleSave}
              size="small"
            >
              <SaveIcon />
            </IconButton>
          </span>
        </Tooltip>
        
        <Tooltip title="Toggle theme">
          <IconButton onClick={toggleTheme} size="small">
            {mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
          </IconButton>
        </Tooltip>
      </Box>
      
      {/* 3-panel layout */}
      <Box sx={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Left Panel - 20% */}
        <Box sx={{ width: '20%', borderRight: 1, borderColor: 'divider', overflow: 'auto', p: 1 }}>
          <TypeTree />
        </Box>
        
        {/* Middle Panel - 50% */}
        <Box sx={{ width: '50%', borderRight: 1, borderColor: 'divider', overflow: 'auto' }}>
          <MiddlePanel />
        </Box>
        
        {/* Right Panel - 30% */}
        <Box sx={{ width: '30%', overflow: 'auto' }}>
          <RightPanel />
        </Box>
      </Box>
    </Box>
  );
}

