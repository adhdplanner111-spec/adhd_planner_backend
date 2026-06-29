import {
  Box,
  TextField,
  Button,
} from "@mui/material";

import { useEffect, useState } from "react";

import api from "../services/api";

import UserTable from "../components/UserTable";
import UserDetailDialog from "../components/UserDetailDialog";
import CreateUserDialog from "../components/CreateUserDialog";
import DeleteUserDialog
from "../components/DeleteUserDialog";
import PersonAddAlt1Icon
from "@mui/icons-material/PersonAddAlt1";


export default function UsersPage() {

  const [users, setUsers] =
    useState([]);

  const [search, setSearch] =
    useState("");

  const [selectedUser, setSelectedUser] =
    useState(null);

  const [openDetail, setOpenDetail] =
    useState(false);

  const [openDelete, setOpenDelete] =
    useState(false);

  const [openCreate, setOpenCreate] =
    useState(false);


  useEffect(() => {
    fetchUsers();
  }, []);

  const handleView = (user) => {
    setSelectedUser(user);
    setOpenDetail(true);
  };

  const handleDelete = (user) => {
    setSelectedUser(user);
    setOpenDelete(true);
  };

  const fetchUsers = async () => {

    const response =
      await api.get(
        "/admin/users"
      );

    setUsers(
      response.data.data
    );
  };

  const filteredUsers =
    users.filter(
      (user) =>
        user.fullname
          .toLowerCase()
          .includes(
            search.toLowerCase()
          ) ||

        user.email
          .toLowerCase()
          .includes(
            search.toLowerCase()
          )
    );

  return (
    <Box>
      <Box
        sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 3,
        }}
      >

        <Box
            sx={{
                display: "flex",
                alignItems: "center",
                gap: 2,
            }}
        >

            <TextField
                placeholder="Search user..."
                value={search}
                onChange={(e) =>
                    setSearch(e.target.value)
                }
                size="small"
                sx={{
                    width: 320,
                }}
            />

            <Button
                variant="outlined"
                onClick={fetchUsers}
            >
                Refresh
            </Button>

        </Box>

        <Button
            variant="contained"
            startIcon={<PersonAddAlt1Icon />}
            onClick={() =>
                setOpenCreate(true)
            }
        >
            Add User
        </Button>

      </Box>

      <UserTable
          users={filteredUsers}
          onView={handleView}
        onDelete={handleDelete}
      />

      <UserDetailDialog
        open={openDetail}
        onClose={() =>
          setOpenDetail(false)
        }
        user={selectedUser}
      />

      <DeleteUserDialog
        open={openDelete}
        onClose={() =>
            setOpenDelete(false)
        }
        user={selectedUser}
        refresh={fetchUsers}
      />

      <CreateUserDialog
        open={openCreate}
        onClose={() =>
            setOpenCreate(false)
        }
        refresh={fetchUsers}
      />

    </Box>
  );

  
}