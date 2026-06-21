import {
  Card,
  CardContent,
  Typography,
} from "@mui/material";

export default function StatCard({
  title,
  value,
}) {
  return (
    <Card
      sx={{
        borderRadius: 5,
        minHeight: 140,
        background:
          "#1E293B",
        transition: ".3s",

        "&:hover": {
          transform:
            "translateY(-5px)",
        },
      }}
    >
      <CardContent>

        <Typography
          color="gray"
          mb={1}
        >
          {title}
        </Typography>

        <Typography
          variant="h3"
          fontWeight="bold"
        >
          {value}
        </Typography>

      </CardContent>
    </Card>
  );
}