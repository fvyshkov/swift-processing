import React from 'react';
import { Box, Typography, useTheme } from '@mui/material';
import CodeEditorField from '@uiw/react-textarea-code-editor';

interface Props {
  value: string;
  onChange: (value: string) => void;
  label: string;
  language?: 'python' | 'json' | 'sql';
  minHeight?: number;
}

export default function CodeEditor({ value, onChange, label, language = 'python', minHeight = 100 }: Props) {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  
  // Add line numbers
  const lines = value.split('\n');
  const lineNumbers = lines.map((_, i) => (i + 1).toString().padStart(3, ' ')).join('\n');
  
  return (
    <Box sx={{ mt: 1, mb: 1 }}>
      <Typography variant="caption" sx={{ mb: 0.5, display: 'block', fontWeight: 'bold' }}>
        {label}
      </Typography>
      <Box sx={{ display: 'flex', border: isDark ? '1px solid rgba(255, 255, 255, 0.23)' : '1px solid rgba(0, 0, 0, 0.23)', borderRadius: '4px', overflow: 'hidden' }}>
        {/* Line numbers */}
        <Box sx={{ 
          padding: '8px 4px',
          backgroundColor: isDark ? 'rgba(0, 0, 0, 0.2)' : 'rgba(0, 0, 0, 0.03)',
          borderRight: isDark ? '1px solid rgba(255, 255, 255, 0.1)' : '1px solid rgba(0, 0, 0, 0.1)',
          minWidth: '40px',
          textAlign: 'right',
        }}>
          <pre style={{ 
            margin: 0, 
            fontSize: 11,
            fontFamily: 'ui-monospace, SFMono-Regular, SF Mono, Consolas, Liberation Mono, Menlo, monospace',
            color: isDark ? 'rgba(255, 255, 255, 0.4)' : 'rgba(0, 0, 0, 0.4)',
            lineHeight: '18px',
          }}>
            {lineNumbers}
          </pre>
        </Box>
        {/* Code editor */}
        <Box sx={{ flex: 1 }}>
          <CodeEditorField
            value={value}
            language={language}
            placeholder={`Enter ${language} code...`}
            onChange={(e) => onChange(e.target.value)}
            padding={8}
            data-color-mode={isDark ? 'dark' : 'light'}
            style={{
              fontSize: 12,
              fontFamily: 'ui-monospace, SFMono-Regular, SF Mono, Consolas, Liberation Mono, Menlo, monospace',
              minHeight,
              backgroundColor: isDark ? 'rgba(0, 0, 0, 0.3)' : 'rgba(0, 0, 0, 0.05)',
              border: 'none',
              color: isDark ? '#fff' : '#000',
              lineHeight: '18px',
            }}
          />
        </Box>
      </Box>
    </Box>
  );
}

