import {
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Avatar,
  Divider,
} from "@mui/material";

import PersonIcon from "@mui/icons-material/Person";
import TaskIcon from "@mui/icons-material/Task";
import TimerIcon from "@mui/icons-material/Timer";
import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import LoginIcon from "@mui/icons-material/Login";

function getIcon(module) {
  switch (module) {
    case "Task":
      return <TaskIcon />;

    case "Focus":
      return <TimerIcon />;

    case "Authentication":
      return <LoginIcon />;

    case "Admin":
      return <AdminPanelSettingsIcon />;

    default:
      return <PersonIcon />;
  }
}

export default function ActivityLog({
  logs,
}) {
  return (
    <Card
      sx={{
        mt: 4,
        borderRadius: 4,
      }}
    >
      <CardContent>

        <Typography
          variant="h6"
          fontWeight="bold"
          mb={2}
        >
          Recent Activity
        </Typography>

        <List>

          {logs.map((log, index) => (
            <div key={log.id}>

              <ListItem>

                <ListItemAvatar>
                  <Avatar>
                    {getIcon(log.module)}
                  </Avatar>
                </ListItemAvatar>

                <ListItemText
                  primary={
                    <>
                      <b>
                        {log.user_name}
                      </b>

                      {" • "}

                      {log.action}
                    </>
                  }

                  secondary={
                    <>
                      {log.description}

                      <br />

                      <small>
                        {new Date(
                          log.created_at
                        ).toLocaleString()}
                      </small>
                    </>
                  }
                />

              </ListItem>

              {index <
                logs.length - 1 && (
                <Divider />
              )}

            </div>
          ))}

        </List>

      </CardContent>
    </Card>
  );
}