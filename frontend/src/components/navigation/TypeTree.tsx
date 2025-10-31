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
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import { useTypesWithChanges } from '../../hooks/useTypesWithChanges';
import { useSelectionStore } from '../../store/selectionStore';
import { useChangesStore } from '../../store/changesStore';
import { ProcessType } from '../../types';
import ConfirmDialog from '../common/ConfirmDialog';

export default function TypeTree() {
  const { data: types, isLoading, error } = useTypesWithChanges();
  const { selectedTypeCode, selectType } = useSelectionStore();
  const { createType, updateType, deleteType } = useChangesStore();
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [deleteDialog, setDeleteDialog] = useState<{
    open: boolean;
    typeCode: string;
    childrenCount: number;
  }>({ open: false, typeCode: '', childrenCount: 0 });
  
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
  
  // Expand all by default and select first terminal node
  React.useEffect(() => {
    if (types && expanded.size === 0) {
      const allIds = new Set(types.map(t => t.id));
      setExpanded(allIds);
      
      // Auto-select first terminal (leaf) node
      const terminals = types.filter(t => {
        const children = childrenMap.get(t.id) || [];
        return children.length === 0; // No children = terminal
      });
      
      if (terminals.length > 0 && !selectedTypeCode) {
        selectType(terminals[0].code);
      }
    }
  }, [types, selectedTypeCode]);
  
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
    const id = crypto.randomUUID();
    
    const newType: ProcessType = {
      id,
      code: '',
      name_en: '',
      name_ru: '',
      attributes_table: '',
      parent_id: undefined
    };
    
    createType(newType);
    selectType(''); // Select the empty type
  };
  
  const handleAddChild = () => {
    if (!selectedTypeCode) return;
    
    const selectedType = types?.find(t => t.code === selectedTypeCode);
    if (!selectedType) return;
    
    const id = crypto.randomUUID();
    
    const newType: ProcessType = {
      id,
      code: '',
      name_en: '',
      name_ru: '',
      attributes_table: selectedType.attributes_table || '',
      parent_id: selectedType.id
    };
    
    createType(newType);
    
    // Expand parent
    const newExpanded = new Set(expanded);
    newExpanded.add(selectedType.id);
    setExpanded(newExpanded);
    
    selectType('');
  };
  
  const handleDelete = () => {
    if (!selectedTypeCode) return;
    
    const selectedType = types?.find(t => t.code === selectedTypeCode);
    const children = selectedType ? childrenMap.get(selectedType.id) || [] : [];
    
    setDeleteDialog({
      open: true,
      typeCode: selectedTypeCode,
      childrenCount: children.length
    });
  };
  
  const confirmDelete = () => {
    deleteType(deleteDialog.typeCode);
    selectType(null as any);
    setDeleteDialog({ open: false, typeCode: '', childrenCount: 0 });
  };
  
  const cancelDelete = () => {
    setDeleteDialog({ open: false, typeCode: '', childrenCount: 0 });
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
      console.warn('Cannot move parent into its own child!');
      return;
    }
    
    // Update parent_id - move to new parent
    const updatedType = {
      ...draggedType,
      parent_id: targetType.id
    };
    
    updateType(updatedType);
    
    // Expand target parent
    const newExpanded = new Set(expanded);
    newExpanded.add(targetType.id);
    setExpanded(newExpanded);
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
            <AccountTreeIcon fontSize="small" />
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
      
      {/* Delete confirmation dialog */}
      <ConfirmDialog
        open={deleteDialog.open}
        title="Delete Type"
        message={
          deleteDialog.childrenCount > 0
            ? `Delete ${deleteDialog.typeCode} and ${deleteDialog.childrenCount} child type(s)?`
            : `Delete ${deleteDialog.typeCode}?`
        }
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
    </Box>
  );
}

