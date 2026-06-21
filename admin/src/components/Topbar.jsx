import {
  AppBar,
  Toolbar,
  Typography,
} from "@mui/material";

import { useLocation } from "react-router-dom";

export default function Topbar() {

  const location = useLocation();

  const titles = {
    "/dashboard": "Dashboard",
    "/users": "Users",
    "/tasks": "Tasks",
    "/focus": "Focus Sessions",
    "/pending": "Pending OTP",
  };

  const title =
    titles[location.pathname]
    || "ADHD Planner";

  return (
    <AppBar
      position="static"
      elevation={0}
      sx={{
        background: "#0F172A",
        borderBottom:
          "1px solid #1E293B",
      }}
    >
      <Toolbar>

        <Typography
          variant="h5"
          fontWeight="bold"
        >
          {title}
        </Typography>

      </Toolbar>
    </AppBar>
  );
}