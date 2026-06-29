import {
  Card,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  IconButton,
  Chip,
  Typography,
} from "@mui/material";

import VisibilityIcon from "@mui/icons-material/Visibility";
import DeleteIcon from "@mui/icons-material/Delete";

export default function UserTable({
  users,
  onView,
  onDelete,
}) {

  return (
    <Card
      sx={{
        borderRadius: 4,
        overflow: "hidden",
      }}
    >

      <Table>

        <TableHead>

          <TableRow
            sx={{
              bgcolor: "#1E293B",
            }}
          >

            <TableCell>
              <Typography
                fontWeight="bold"
              >
                Full Name
              </Typography>
            </TableCell>

            <TableCell>
              <Typography
                fontWeight="bold"
              >
                Email
              </Typography>
            </TableCell>

            <TableCell align="center">
              <Typography
                fontWeight="bold"
              >
                Streak
              </Typography>
            </TableCell>

            <TableCell align="center">
              <Typography
                fontWeight="bold"
              >
                Productivity
              </Typography>
            </TableCell>

            <TableCell align="center">
              <Typography
                fontWeight="bold"
              >
                Total Task
              </Typography>
            </TableCell>

            <TableCell>
              <Typography
                fontWeight="bold"
              >
                Join Date
              </Typography>
            </TableCell>

            <TableCell align="center">
              <Typography
                fontWeight="bold"
              >
                Action
              </Typography>
            </TableCell>

          </TableRow>

        </TableHead>

        <TableBody>

          {users.map((user) => (

            <TableRow
              key={user.uid}
              hover
            >

              <TableCell>
                {user.fullname}
              </TableCell>

              <TableCell>
                {user.email}
              </TableCell>

              <TableCell align="center">

                <Chip
                  label={user.streak}
                  color="primary"
                  size="small"
                />

              </TableCell>

              <TableCell align="center">

                <Chip
                  label={
                    user.productivity_score +
                    "%"
                  }
                  color="success"
                  size="small"
                />

              </TableCell>

              <TableCell align="center">
                {user.total_tasks}
              </TableCell>

              <TableCell>

                {new Date(
                  user.created_at
                ).toLocaleDateString(
                  "id-ID"
                )}

              </TableCell>

              <TableCell align="center">

                <IconButton
                  color="primary"
                  onClick={() =>
                    onView(user)
                  }
                >
                  <VisibilityIcon />
                </IconButton>

                <IconButton
                  color="error"
                  onClick={() =>
                    onDelete(user)
                  }
                >
                  <DeleteIcon />
                </IconButton>

              </TableCell>

            </TableRow>

          ))}

        </TableBody>

      </Table>

    </Card>
  );
}