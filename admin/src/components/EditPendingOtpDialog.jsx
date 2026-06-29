import { useEffect, useState } from "react";

import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  Box,
  IconButton,
  CircularProgress,
} from "@mui/material";

import CasinoIcon from "@mui/icons-material/Casino";

import api from "../services/api";

export default function EditPendingOtpDialog({

  open,

  onClose,

  pending,

  refresh,

}) {

  const [otp, setOtp] =
    useState("");

  const [expireMinutes, setExpireMinutes] =
    useState(5);

  const [loading, setLoading] =
    useState(false);

  useEffect(() => {

    if (pending) {

      setOtp(
        pending.otp
      );

      setExpireMinutes(5);

    }

  }, [pending]);

  const generateOTP = () => {

    const value = Math.floor(
      100000 +
      Math.random() * 900000
    );

    setOtp(
      value.toString()
    );

  };

  const handleSubmit = async () => {

    try {

      setLoading(true);

      await api.put(

        `/admin/pending-registrations/${pending.email}`,

        {

          otp,

          expire_minutes:
            expireMinutes,

        }

      );

      refresh();

      onClose();

    } catch (error) {

      console.log(error);

      alert(
        error.response?.data?.detail ||
        "Gagal memperbarui OTP."
      );

    }

    setLoading(false);

  };

  if (!pending)
    return null;

  return (

    <Dialog
      open={open}
      onClose={onClose}
      fullWidth
      maxWidth="sm"
    >

      <DialogTitle>
        Edit Pending OTP
      </DialogTitle>

      <DialogContent>

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

        <Box mb={3}>

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

        <Box
          display="flex"
          gap={2}
          alignItems="center"
        >

          <TextField
            label="OTP"
            value={otp}
            fullWidth
            onChange={(e)=>
              setOtp(
                e.target.value
              )
            }
          />

          <IconButton
            color="primary"
            onClick={
              generateOTP
            }
          >
            <CasinoIcon />
          </IconButton>

        </Box>

        <TextField
          sx={{
            mt:3
          }}
          fullWidth
          type="number"
          label="Expire (Minutes)"
          value={expireMinutes}
          onChange={(e)=>
            setExpireMinutes(
              e.target.value
            )
          }
        />

      </DialogContent>

      <DialogActions>

        <Button
          onClick={onClose}
        >
          Cancel
        </Button>

        <Button
          variant="contained"
          onClick={
            handleSubmit
          }
          disabled={loading}
        >

          {

            loading
            ?

            <CircularProgress
              size={20}
            />

            :

            "Save & Resend"

          }

        </Button>

      </DialogActions>

    </Dialog>

  );

}