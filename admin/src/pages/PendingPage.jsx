import {
    Box,
    Button,
    TextField,
} from "@mui/material";

import RefreshIcon from "@mui/icons-material/Refresh";

import { useEffect, useState } from "react";

import api from "../services/api";

import PendingTable from "../components/PendingTable";
import PendingDetailDialog from "../components/PendingDetailDialog";
import EditPendingOtpDialog from "../components/EditPendingOtpDialog";
import DeletePendingDialog from "../components/DeletePendingDialog";

export default function PendingPage() {

    const [pendingRegistrations, setPendingRegistrations] =
        useState([]);

    const [search, setSearch] =
        useState("");

    const [selectedPending, setSelectedPending] =
        useState(null);

    const [openDetail, setOpenDetail] =
        useState(false);

    const [openEdit, setOpenEdit] =
        useState(false);

    const [openDelete, setOpenDelete] =
        useState(false);

    useEffect(() => {

        fetchPendingRegistrations();

    }, []);

    const fetchPendingRegistrations = async () => {

        try {

            const response =
                await api.get(
                    "/admin/pending-registrations"
                );

            setPendingRegistrations(
                response.data.data
            );

        } catch (error) {

            console.log(error);

        }

    };

    const filteredPending =
        pendingRegistrations.filter((item) =>

            item.fullname
                .toLowerCase()
                .includes(
                    search.toLowerCase()
                )

            ||

            item.email
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
                        gap: 2,
                    }}
                >

                    <TextField
                        size="small"
                        placeholder="Search pending..."
                        value={search}
                        onChange={(e) =>
                            setSearch(
                                e.target.value
                            )
                        }
                        sx={{
                            width: 320,
                        }}
                    />

                    <Button
                        variant="outlined"
                        startIcon={
                            <RefreshIcon />
                        }
                        onClick={
                            fetchPendingRegistrations
                        }
                    >
                        Refresh
                    </Button>

                </Box>

            </Box>

            <PendingTable

                pending={filteredPending}

                onView={(item) => {

                    setSelectedPending(item);

                    setOpenDetail(true);

                }}

                onEdit={(item) => {

                    setSelectedPending(item);

                    setOpenEdit(true);

                }}

                onDelete={(item) => {

                    setSelectedPending(item);

                    setOpenDelete(true);

                }}

            />

            <PendingDetailDialog

                open={openDetail}

                onClose={() =>
                    setOpenDetail(false)
                }

                pending={selectedPending}

            />

            <EditPendingOtpDialog

                open={openEdit}

                onClose={() =>
                    setOpenEdit(false)
                }

                pending={selectedPending}

                refresh={
                    fetchPendingRegistrations
                }

            />

            <DeletePendingDialog

                open={openDelete}

                onClose={() =>
                    setOpenDelete(false)
                }

                pending={selectedPending}

                refresh={
                    fetchPendingRegistrations
                }

            />

        </Box>

    );

}