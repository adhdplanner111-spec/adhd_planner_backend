import { Box } from "@mui/material";

import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";

export default function AdminLayout({
  children,
}) {
  return (
    <Box sx={{ display: "flex" }}>
      <Sidebar />

        <Box
        sx={{
            flexGrow: 1,
            background: "#020817",
            minHeight: "100vh",
        }}
        >
            <Topbar />

            <Box
            sx={{
                p: 4,
            }}
            >
                {children}
            </Box>
        </Box>
    </Box>
  );
}