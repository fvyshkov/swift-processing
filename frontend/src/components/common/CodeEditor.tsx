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
  
  return (
    <Box sx={{ mt: 1, mb: 1 }}>
      <Typography variant="caption" sx={{ mb: 0.5, display: 'block', fontWeight: 'bold' }}>
        {label}
      </Typography>
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
          borderRadius: 4,
          border: isDark ? '1px solid rgba(255, 255, 255, 0.23)' : '1px solid rgba(0, 0, 0, 0.23)',
          color: isDark ? '#fff' : '#000',
        }}
      />
    </Box>
  );
}

