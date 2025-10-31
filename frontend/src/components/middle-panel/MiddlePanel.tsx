import React, { useState } from 'react';
import { Box, Typography, Accordion, AccordionSummary, AccordionDetails } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { useSelectionStore } from '../../store/selectionStore';
import { useType } from '../../hooks/useTypes';
import TypeAttributesSection from './TypeAttributesSection';
import StatesListSection from './StatesListSection';

export default function MiddlePanel() {
  const selectedTypeCode = useSelectionStore((state) => state.selectedTypeCode);
  const { data: type } = useType(selectedTypeCode);
  const [expanded, setExpanded] = useState<string[]>(['process', 'states']);
  
  const handleChange = (panel: string) => (_event: React.SyntheticEvent, isExpanded: boolean) => {
    setExpanded(isExpanded 
      ? [...expanded, panel] 
      : expanded.filter(p => p !== panel)
    );
  };
  
  if (!selectedTypeCode) {
    return (
      <Box sx={{ p: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
        <Typography color="text.secondary" variant="body2">Select a type to view details</Typography>
      </Box>
    );
  }
  
  return (
    <Box sx={{ p: 1 }}>
      <Accordion 
        expanded={expanded.includes('process')} 
        onChange={handleChange('process')}
        elevation={1}
      >
        <AccordionSummary 
          expandIcon={<ExpandMoreIcon />} 
          sx={{ 
            minHeight: 40, 
            bgcolor: 'rgba(173, 216, 230, 0.15)',
            '&:hover': { bgcolor: 'rgba(173, 216, 230, 0.25)' },
            '& .MuiAccordionSummary-content': { my: 0.5 } 
          }}
        >
          <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
            {type ? `${type.code} - ${type.name_en}` : 'Business Process'}
          </Typography>
        </AccordionSummary>
        <AccordionDetails sx={{ p: 1.5, pt: 0 }}>
          <TypeAttributesSection typeCode={selectedTypeCode} />
        </AccordionDetails>
      </Accordion>
      
      <Accordion 
        expanded={expanded.includes('states')} 
        onChange={handleChange('states')}
        elevation={1}
        sx={{ mt: 1 }}
      >
        <AccordionSummary 
          expandIcon={<ExpandMoreIcon />} 
          sx={{ 
            minHeight: 40, 
            bgcolor: 'rgba(173, 216, 230, 0.15)',
            '&:hover': { bgcolor: 'rgba(173, 216, 230, 0.25)' },
            '& .MuiAccordionSummary-content': { my: 0.5 } 
          }}
        >
          <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>States & Operations</Typography>
        </AccordionSummary>
        <AccordionDetails sx={{ p: 1.5, pt: 0 }}>
          <StatesListSection typeCode={selectedTypeCode} />
        </AccordionDetails>
      </Accordion>
    </Box>
  );
}

