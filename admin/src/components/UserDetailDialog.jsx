import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Typography,
    Divider,
    Box,
} from "@mui/material";

export default function UserDetailDialog({

    open,

    onClose,

    user,

}) {

    if (!user) return null;

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
                User Detail
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
                        {user.fullname}
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
                        {user.email}
                    </Typography>
                </Box>

                <Divider />

                <Box my={2}>
                    <Typography
                        color="text.secondary"
                    >
                        Streak
                    </Typography>

                    <Typography
                        fontWeight="bold"
                    >
                        {user.streak} Days
                    </Typography>
                </Box>

                <Divider />

                <Box my={2}>
                    <Typography
                        color="text.secondary"
                    >
                        Productivity Score
                    </Typography>

                    <Typography
                        fontWeight="bold"
                    >
                        {user.productivity_score}%
                    </Typography>
                </Box>

                <Divider />

                <Box my={2}>
                    <Typography
                        color="text.secondary"
                    >
                        Total Tasks
                    </Typography>

                    <Typography
                        fontWeight="bold"
                    >
                        {user.total_tasks}
                    </Typography>
                </Box>

                <Divider />

                <Box mt={2}>
                    <Typography
                        color="text.secondary"
                    >
                        Join Date
                    </Typography>

                    <Typography
                        fontWeight="bold"
                    >
                        {
                            new Date(
                                user.created_at
                            ).toLocaleDateString(
                                "id-ID",
                                {
                                    day: "2-digit",
                                    month: "long",
                                    year: "numeric",
                                }
                            )
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