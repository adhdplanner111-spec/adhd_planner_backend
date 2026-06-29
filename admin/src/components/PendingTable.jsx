import {
  Card,
  Chip,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";

import VisibilityIcon from "@mui/icons-material/Visibility";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";

export default function PendingTable({

  pending,

  onView,

  onEdit,

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

          <TableRow>

            <TableCell>
              <Typography fontWeight="bold">
                Full Name
              </Typography>
            </TableCell>

            <TableCell>
              <Typography fontWeight="bold">
                Email
              </Typography>
            </TableCell>

            <TableCell align="center">
              <Typography fontWeight="bold">
                OTP
              </Typography>
            </TableCell>

            <TableCell align="center">
              <Typography fontWeight="bold">
                Status
              </Typography>
            </TableCell>

            <TableCell align="center">
              <Typography fontWeight="bold">
                Expired
              </Typography>
            </TableCell>

            <TableCell align="center">
              <Typography fontWeight="bold">
                Action
              </Typography>
            </TableCell>

          </TableRow>

        </TableHead>

        <TableBody>

          {

            pending.length === 0 && (

              <TableRow>

                <TableCell
                  colSpan={6}
                  align="center"
                >

                  Tidak ada pending registration.

                </TableCell>

              </TableRow>

            )

          }

          {

            pending.map((item) => (

              <TableRow
                hover
                key={item.email}
              >

                <TableCell>
                  {item.fullname}
                </TableCell>

                <TableCell>
                  {item.email}
                </TableCell>

                <TableCell
                  align="center"
                >
                  {item.otp}
                </TableCell>

                <TableCell
                  align="center"
                >

                  <Chip

                    label={item.status}

                    color={
                      item.status === "active"
                        ? "success"
                        : "error"
                    }

                    size="small"

                  />

                </TableCell>

                <TableCell
                  align="center"
                >

                  {

                    item.expires_at

                      ?

                      new Date(
                        item.expires_at
                      ).toLocaleString(
                        "id-ID"
                      )

                      :

                      "-"

                  }

                </TableCell>

                <TableCell
                  align="center"
                >

                  <IconButton
                    color="primary"
                    onClick={() =>
                      onView(item)
                    }
                  >
                    <VisibilityIcon />
                  </IconButton>

                  <IconButton
                    color="warning"
                    onClick={() =>
                      onEdit(item)
                    }
                  >
                    <EditIcon />
                  </IconButton>

                  <IconButton
                    color="error"
                    onClick={() =>
                      onDelete(item)
                    }
                  >
                    <DeleteIcon />
                  </IconButton>

                </TableCell>

              </TableRow>

            ))

          }

        </TableBody>

      </Table>

    </Card>

  );

}