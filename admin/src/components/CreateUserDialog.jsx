import { useState } from "react";

import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  InputAdornment,
  IconButton,
  CircularProgress,
} from "@mui/material";

import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";

import api from "../services/api";

export default function CreateUserDialog({
  open,
  onClose,
  refresh,
}) {

  const [fullname, setFullname] =
    useState("");

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [showPassword, setShowPassword] =
    useState(false);

  const [loading, setLoading] =
    useState(false);

  const resetForm = () => {

    setFullname("");

    setEmail("");

    setPassword("");

    setShowPassword(false);

  };

  const handleClose = () => {

    resetForm();

    onClose();

  };

  const handleCreate = async () => {

    if (
      !fullname ||
      !email ||
      !password
    ) {
      alert("Semua field wajib diisi.");
      return;
    }

    try {

      setLoading(true);

      await api.post(
        "/admin/users",
        {
          fullname,
          email,
          password,
        }
      );

      refresh();

      handleClose();

    } catch (error) {

      alert(
        error?.response?.data?.detail ||
        "Gagal menambahkan user."
      );

    } finally {

      setLoading(false);

    }

  };

  return (

    <Dialog
      open={open}
      onClose={handleClose}
      fullWidth
      maxWidth="sm"
    >

      <DialogTitle
        fontWeight="bold"
      >
        Add User
      </DialogTitle>

      <DialogContent>

        <TextField
          label="Full Name"
          fullWidth
          margin="normal"
          value={fullname}
          onChange={(e)=>
            setFullname(
              e.target.value
            )
          }
        />

        <TextField
          label="Email"
          type="email"
          fullWidth
          margin="normal"
          value={email}
          onChange={(e)=>
            setEmail(
              e.target.value
            )
          }
        />

        <TextField
          label="Password"
          fullWidth
          margin="normal"
          type={
            showPassword
              ? "text"
              : "password"
          }
          value={password}
          onChange={(e)=>
            setPassword(
              e.target.value
            )
          }
          InputProps={{

            endAdornment: (

              <InputAdornment
                position="end"
              >

                <IconButton
                  onClick={()=>
                    setShowPassword(
                      !showPassword
                    )
                  }
                >

                  {
                    showPassword
                    ? <VisibilityOff />
                    : <Visibility />
                  }

                </IconButton>

              </InputAdornment>

            )

          }}
        />

      </DialogContent>

      <DialogActions>

        <Button
          onClick={handleClose}
        >
          Cancel
        </Button>

        <Button
          variant="contained"
          onClick={handleCreate}
          disabled={loading}
        >

          {
            loading
            ? <CircularProgress size={22}/>
            : "Create User"
          }

        </Button>

      </DialogActions>

    </Dialog>

  );

}