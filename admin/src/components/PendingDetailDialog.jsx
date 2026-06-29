import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Typography,
    Divider,
    Box,
    Chip,
} from "@mui/material";

export default function PendingDetailDialog({

    open,

    onClose,

    pending,

}) {

    if (!pending) return null;

    return (

        <Dialog
            open={open}
            onClose={onClose}
            fullWidth
            maxWidth="sm"
        >

            <DialogTitle
                fontWeight="bold"
            >
                Pending Registration Detail
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

                <Divider />

                <Box my={2}>

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

                <Divider />

                <Box my={2}>

                    <Typography
                        color="text.secondary"
                    >
                        OTP
                    </Typography>

                    <Typography
                        fontWeight="bold"
                    >
                        {pending.otp}
                    </Typography>

                </Box>

                <Divider />

                <Box my={2}>

                    <Typography
                        color="text.secondary"
                    >
                        Status
                    </Typography>

                    <Chip

                        label={pending.status}

                        color={
                            pending.status === "active"
                                ? "success"
                                : "error"
                        }

                    />

                </Box>

                <Divider />

                <Box my={2}>

                    <Typography
                        color="text.secondary"
                    >
                        Expired At
                    </Typography>

                    <Typography
                        fontWeight="bold"
                    >
                        {
                            pending.expires_at
                                ?

                                new Date(
                                    pending.expires_at
                                ).toLocaleString(
                                    "id-ID"
                                )

                                :

                                "-"
                        }
                    </Typography>

                </Box>

                <Divider />

                <Box mt={2}>

                    <Typography
                        color="text.secondary"
                    >
                        Created At
                    </Typography>

                    <Typography
                        fontWeight="bold"
                    >
                        {
                            pending.created_at
                                ?

                                new Date(
                                    pending.created_at
                                ).toLocaleString(
                                    "id-ID"
                                )

                                :

                                "-"
                        }
                    </Typography>

                </Box>

            </DialogContent>

            <DialogActions>

                <Button
                    variant="contained"
                    onClick={onClose}
                >
                    Close
                </Button>

            </DialogActions>

        </Dialog>

    );

}