import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    mode: "dark",
    primary: {
      main: "#6366F1",
    },
    background: {
      default: "#111827",
      paper: "#1F2937",
    },
  },
  typography: {
    fontFamily: "Inter, sans-serif",
  },
});

export default theme;