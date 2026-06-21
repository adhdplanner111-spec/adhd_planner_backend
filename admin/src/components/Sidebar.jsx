import {
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Divider,
} from "@mui/material";

import DashboardIcon from "@mui/icons-material/Dashboard";
import PeopleIcon from "@mui/icons-material/People";
import TaskIcon from "@mui/icons-material/Task";
import TimerIcon from "@mui/icons-material/Timer";
import MailIcon from "@mui/icons-material/Mail";
import LogoutIcon from "@mui/icons-material/Logout";

import { useNavigate } from "react-router-dom";

const drawerWidth = 240;

export default function Sidebar() {
  const navigate = useNavigate();

  const logout = () => {
    localStorage.removeItem(
      "admin_token"
    );

    navigate("/");
  };

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,

        "& .MuiDrawer-paper": {
          width: drawerWidth,
          boxSizing: "border-box",
          backgroundColor: "#1F2937",
        },
      }}
    >
      <Toolbar>
        <Typography
          variant="h6"
          fontWeight="bold"
        >
          ADHD Admin
        </Typography>
      </Toolbar>

      <Divider />

      <List>

        <ListItemButton
          onClick={() =>
            navigate("/dashboard")
          }
        >
          <ListItemIcon>
            <DashboardIcon />
          </ListItemIcon>

          <ListItemText
            primary="Dashboard"
          />
        </ListItemButton>

        <ListItemButton
          onClick={() =>
            navigate("/users")
          }
        >
          <ListItemIcon>
            <PeopleIcon />
          </ListItemIcon>

          <ListItemText
            primary="Users"
          />
        </ListItemButton>

        <ListItemButton
          onClick={() =>
            navigate("/tasks")
          }
        >
          <ListItemIcon>
            <TaskIcon />
          </ListItemIcon>

          <ListItemText
            primary="Tasks"
          />
        </ListItemButton>

        <ListItemButton
          onClick={() =>
            navigate("/focus")
          }
        >
          <ListItemIcon>
            <TimerIcon />
          </ListItemIcon>

          <ListItemText
            primary="Focus"
          />
        </ListItemButton>

        <ListItemButton
          onClick={() =>
            navigate("/pending")
          }
        >
          <ListItemIcon>
            <MailIcon />
          </ListItemIcon>

          <ListItemText
            primary="Pending OTP"
          />
        </ListItemButton>

      </List>

      <Divider />

      <List>
        <ListItemButton
          onClick={logout}
        >
          <ListItemIcon>
            <LogoutIcon />
          </ListItemIcon>

          <ListItemText
            primary="Logout"
          />
        </ListItemButton>
      </List>
    </Drawer>
  );
}