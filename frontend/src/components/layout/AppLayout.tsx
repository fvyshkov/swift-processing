import React from 'react';
import { Box, IconButton, Tooltip } from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
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
  
  const handleSave = async () => {
    const store = useChangesStore.getState();
    
    try {
      // Create new types
      for (const type of store.types.created) {
        await fetch('http://localhost:8000/api/v1/types', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(type)
        });
      }
      
      // Update types
      for (const type of store.types.updated) {
        await fetch(`http://localhost:8000/api/v1/types/${type.code}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(type)
        });
      }
      
      // Delete types
      for (const code of store.types.deleted) {
        await fetch(`http://localhost:8000/api/v1/types/${code}`, {
          method: 'DELETE'
        });
      }
      
      // Save states and operations through existing save-all endpoint
      if (store.states || store.operations) {
        saveAll({
          type: store.type || undefined,
          states: store.states,
          operations: store.operations,
        });
      } else {
        // Just reload if only types changed
        window.location.reload();
      }
    } catch (err) {
      console.error('Error saving:', err);
      alert('Error saving changes: ' + (err as Error).message);
    }
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
      
      {/* 3-panel layout with resizable panels */}
      <Box sx={{ flex: 1, overflow: 'hidden' }}>
        <PanelGroup direction="horizontal">
          {/* Left Panel - resizable */}
          <Panel defaultSize={20} minSize={15} maxSize={35}>
            <Box sx={{ height: '100%', borderRight: 1, borderColor: 'divider', overflow: 'auto', p: 1 }}>
              <TypeTree />
            </Box>
          </Panel>
          
          <PanelResizeHandle style={{ width: '4px', background: 'rgba(0,0,0,0.1)', cursor: 'col-resize' }} />
          
          {/* Middle Panel - takes remaining space */}
          <Panel minSize={30}>
            <Box sx={{ height: '100%', borderRight: 1, borderColor: 'divider', overflow: 'auto' }}>
              <MiddlePanel />
            </Box>
          </Panel>
          
          <PanelResizeHandle style={{ width: '4px', background: 'rgba(0,0,0,0.1)', cursor: 'col-resize' }} />
          
          {/* Right Panel - resizable */}
          <Panel defaultSize={25} minSize={20} maxSize={40}>
            <Box sx={{ height: '100%', overflow: 'auto' }}>
              <RightPanel />
            </Box>
          </Panel>
        </PanelGroup>
      </Box>
    </Box>
  );
}

