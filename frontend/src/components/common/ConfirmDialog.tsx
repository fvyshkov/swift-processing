import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
} from '@mui/material';

interface Props {
  open: boolean;
  title: string;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmDialog({ open, title, message, onConfirm, onCancel }: Props) {
  return (
    <Dialog
      open={open}
      onClose={onCancel}
      aria-labelledby="confirm-dialog-title"
      maxWidth="xs"
      fullWidth
    >
      <DialogTitle id="confirm-dialog-title" sx={{ pb: 1 }}>
        {title}
      </DialogTitle>
      <DialogContent>
        <DialogContentText>{message}</DialogContentText>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onCancel} size="small">
          Cancel
        </Button>
        <Button onClick={onConfirm} variant="contained" color="error" size="small" autoFocus>
          Delete
        </Button>
      </DialogActions>
    </Dialog>
  );
}

