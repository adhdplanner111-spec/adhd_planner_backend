import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Alert,
  Box,
} from "@mui/material";

import { useState } from "react";

import api from "../services/api";

export default function DeletePendingDialog({

  open,

  onClose,

  pending,

  refresh,

}) {

  const [loading, setLoading] =
    useState(false);

  if (!pending) return null;

  const handleDelete = async () => {

    try {

      setLoading(true);

      await api.delete(
        `/admin/pending-registrations/${pending.email}`
      );

      refresh();

      onClose();

    } catch (error) {

      console.log(error);

      alert(
        error.response?.data?.detail ||
        "Gagal menghapus data."
      );

    } finally {

      setLoading(false);

    }

  };

  return (

    <Dialog
      open={open}
      onClose={onClose}
      fullWidth
      maxWidth="sm"
    >

      <DialogTitle
        fontWeight="bold"
      >
        Delete Pending Registration
      </DialogTitle>

      <DialogContent>

        <Typography mb={2}>
          Apakah Anda yakin ingin menghapus pending registration berikut?
        </Typography>

        <Box mb={2}>

          <Typography
            color="text.secondary"
          >
            Full Name
          </Typography>

          <Typography
            fontWeight="bold"
          >
            {pending.fullname}
          </Typography>

        </Box>

        <Box mb={2}>

          <Typography
            color="text.secondary"
          >
            Email
          </Typography>

          <Typography
            fontWeight="bold"
          >
            {pending.email}
          </Typography>

        </Box>

        <Alert severity="warning">

          Pending registration akan dihapus secara permanen.

        </Alert>

      </DialogContent>

      <DialogActions>

        <Button
          onClick={onClose}
          disabled={loading}
        >
          Cancel
        </Button>

        <Button
          color="error"
          variant="contained"
          disabled={loading}
          onClick={handleDelete}
        >
          Delete
        </Button>

      </DialogActions>

    </Dialog>

  );

}