import React, { useState } from 'react';
import { 
  List, 
  ListItemButton, 
  ListItemText, 
  CircularProgress, 
  Typography, 
  Box, 
  IconButton,
  Tooltip,
  Collapse 
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import SubdirectoryArrowRightIcon from '@mui/icons-material/SubdirectoryArrowRight';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import { useTypes } from '../../hooks/useTypes';
import { useSelectionStore } from '../../store/selectionStore';
import { ProcessType } from '../../types';

export default function TypeTree() {
  const { data: types, isLoading, error } = useTypes();
  const { selectedTypeCode, selectType } = useSelectionStore();
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  
  // Build tree structure
  const rootTypes = types?.filter(t => !t.parent_id) || [];
  const childrenMap = new Map<string, ProcessType[]>();
  
  types?.forEach(type => {
    if (type.parent_id) {
      const parentId = type.parent_id;
      if (!childrenMap.has(parentId)) {
        childrenMap.set(parentId, []);
      }
      childrenMap.get(parentId)!.push(type);
    }
  });
  
  // Expand all by default
  React.useEffect(() => {
    if (types && expanded.size === 0) {
      const allIds = new Set(types.map(t => t.id));
      setExpanded(allIds);
    }
  }, [types]);
  
  const handleToggle = (typeId: string, event: React.MouseEvent) => {
    event.stopPropagation();
    const newExpanded = new Set(expanded);
    if (newExpanded.has(typeId)) {
      newExpanded.delete(typeId);
    } else {
      newExpanded.add(typeId);
    }
    setExpanded(newExpanded);
  };
  
  const handleAdd = () => {
    console.log('Add new root type');
    alert('Add new root type - not implemented yet');
  };
  
  const handleAddChild = () => {
    console.log('Add child type to', selectedTypeCode);
    alert(`Add child to ${selectedTypeCode} - not implemented yet`);
  };
  
  const handleDelete = () => {
    if (selectedTypeCode && window.confirm(`Delete type ${selectedTypeCode}?`)) {
      console.log('Delete type', selectedTypeCode);
      alert(`Delete ${selectedTypeCode} - not implemented yet`);
    }
  };
  
  const [dragOver, setDragOver] = useState<string | null>(null);
  
  const handleDragStart = (event: React.DragEvent, type: ProcessType) => {
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('text/plain', type.id);
    event.dataTransfer.setData('application/json', JSON.stringify(type));
  };
  
  const handleDragOver = (event: React.DragEvent, targetType: ProcessType) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
    setDragOver(targetType.id);
  };
  
  const handleDragLeave = () => {
    setDragOver(null);
  };
  
  const handleDrop = (event: React.DragEvent, targetType: ProcessType) => {
    event.preventDefault();
    setDragOver(null);
    
    const draggedTypeId = event.dataTransfer.getData('text/plain');
    const draggedTypeData = event.dataTransfer.getData('application/json');
    
    if (!draggedTypeData) return;
    
    const draggedType = JSON.parse(draggedTypeData) as ProcessType;
    
    // Don't drop on itself
    if (draggedType.id === targetType.id) {
      return;
    }
    
    // Don't drop parent on its child (would create circular reference)
    const isDescendant = (childId: string, ancestorId: string): boolean => {
      const children = childrenMap.get(ancestorId) || [];
      if (children.some(c => c.id === childId)) return true;
      return children.some(c => isDescendant(childId, c.id));
    };
    
    if (isDescendant(targetType.id, draggedType.id)) {
      alert('Cannot move parent into its own child!');
      return;
    }
    
    // Update parent_id
    console.log(`Moving ${draggedType.code} to be child of ${targetType.code}`);
    alert(`Moving ${draggedType.code} under ${targetType.code} - API call not implemented yet`);
    
    // TODO: Call API to update parent_id
    // await updateType(draggedType.id, { parent_id: targetType.id });
  };
  
  const renderType = (type: ProcessType, level: number = 0) => {
    const children = childrenMap.get(type.id) || [];
    const hasChildren = children.length > 0;
    const isExpanded = expanded.has(type.id);
    const isDraggedOver = dragOver === type.id;
    
    return (
      <React.Fragment key={type.code}>
        <ListItemButton
          selected={selectedTypeCode === type.code}
          onClick={() => selectType(type.code)}
          draggable
          onDragStart={(e) => handleDragStart(e, type)}
          onDragOver={(e) => handleDragOver(e, type)}
          onDragLeave={handleDragLeave}
          onDrop={(e) => handleDrop(e, type)}
          sx={{ 
            py: 0.5, 
            minHeight: 32,
            pl: level * 2 + 1,
            cursor: 'grab',
            bgcolor: isDraggedOver ? 'action.hover' : 'transparent',
            borderLeft: isDraggedOver ? 3 : 0,
            borderColor: 'primary.main',
            '&:active': {
              cursor: 'grabbing'
            }
          }}
        >
          {hasChildren && (
            <IconButton
              size="small"
              onClick={(e) => handleToggle(type.id, e)}
              sx={{ mr: 0.5, p: 0 }}
            >
              {isExpanded ? <ExpandMoreIcon fontSize="small" /> : <ChevronRightIcon fontSize="small" />}
            </IconButton>
          )}
          {!hasChildren && <Box sx={{ width: 24, mr: 0.5 }} />}
          <ListItemText
            primary={type.name_en}
            secondary={type.code}
            primaryTypographyProps={{ variant: 'body2' }}
            secondaryTypographyProps={{ variant: 'caption' }}
          />
        </ListItemButton>
        {hasChildren && (
          <Collapse in={isExpanded} timeout="auto" unmountOnExit>
            {children.map(child => renderType(child, level + 1))}
          </Collapse>
        )}
      </React.Fragment>
    );
  };
  
  if (isLoading) {
    return <CircularProgress size={20} />;
  }
  
  if (error) {
    return <Typography color="error" variant="caption">Error loading types</Typography>;
  }
  
  return (
    <Box>
      {/* Action buttons */}
      <Box sx={{ display: 'flex', gap: 0.5, mb: 1, borderBottom: 1, borderColor: 'divider', pb: 0.5 }}>
        <Tooltip title="Add root type">
          <IconButton size="small" onClick={handleAdd}>
            <AddIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Add child to selected">
          <IconButton size="small" onClick={handleAddChild} disabled={!selectedTypeCode}>
            <SubdirectoryArrowRightIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Delete selected">
          <IconButton size="small" onClick={handleDelete} disabled={!selectedTypeCode}>
            <DeleteIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
      
      {/* Type tree */}
      <List dense>
        {rootTypes.map(type => renderType(type))}
      </List>
    </Box>
  );
}

