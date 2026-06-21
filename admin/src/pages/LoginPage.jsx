import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
} from "@mui/material";

import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";

export default function LoginPage() {
  const navigate = useNavigate();

  const [username, setUsername] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [error, setError] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  useEffect(() => {
    const token = localStorage.getItem(
      "admin_token"
    );

    if (token) {
      navigate("/dashboard");
    }
  }, []);

  const handleLogin = async () => {
    setError("");
    setLoading(true);

    try {
      const response = await api.post(
        "/admin/login",
        {
          username,
          password,
        }
      );

      localStorage.setItem(
        "admin_token",
        response.data.access_token
      );

      navigate("/dashboard");
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Login gagal"
      );
    }

    setLoading(false);
  };

  return (
    <Box
        sx={{
        minHeight: "100vh",
        width: "100vw",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        background:
            "linear-gradient(135deg, #111827 0%, #1F2937 100%)",
        overflow: "hidden",
        }}
    >
        <Paper
        elevation={10}
        sx={{
            width: 420,
            p: 5,
            borderRadius: 4,
            backdropFilter: "blur(20px)",
        }}
        >
        <Box
            display="flex"
            justifyContent="center"
            mb={2}
        >
            <AdminPanelSettingsIcon
            sx={{
                fontSize: 70,
                color: "#6366F1",
            }}
            />
        </Box>

        <Typography
            variant="h4"
            fontWeight="bold"
            textAlign="center"
            gutterBottom
        >
            ADHD Planner
        </Typography>

        <Typography
            textAlign="center"
            color="text.secondary"
            mb={4}
        >
            Admin Dashboard
        </Typography>

        {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
            {error}
            </Alert>
        )}

        <TextField
            fullWidth
            label="Username"
            margin="normal"
            value={username}
            onChange={(e) =>
            setUsername(e.target.value)
            }
        />

        <TextField
            fullWidth
            type="password"
            label="Password"
            margin="normal"
            value={password}
            onChange={(e) =>
            setPassword(e.target.value)
            }
        />

        <Button
            fullWidth
            variant="contained"
            size="large"
            sx={{
            mt: 3,
            py: 1.5,
            borderRadius: 3,
            }}
            onClick={handleLogin}
            disabled={loading}
        >
            {loading ? "Loading..." : "Login"}
        </Button>
        </Paper>
    </Box>
  );
}