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

import api from "../services/api";

export default function DeleteUserDialog({
  open,
  onClose,
  user,
  refresh,
}) {

  if (!user) return null;

  const handleDelete = async () => {

    try {

      await api.delete(
        `/admin/users/${user.uid}`
      );

      refresh();

      onClose();

    } catch (error) {

      console.log(error);

      alert("Gagal menghapus user.");

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
        Delete User
      </DialogTitle>

      <DialogContent>

        <Typography mb={2}>
          Apakah Anda yakin ingin menghapus user berikut?
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
            {user.fullname}
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
            {user.email}
          </Typography>

        </Box>

        <Alert severity="warning">

          User akan dihapus secara permanen.

        </Alert>

      </DialogContent>

      <DialogActions>

        <Button
          onClick={onClose}
        >
          Cancel
        </Button>

        <Button
          color="error"
          variant="contained"
          onClick={handleDelete}
        >
          Delete User
        </Button>

      </DialogActions>

    </Dialog>

  );

}