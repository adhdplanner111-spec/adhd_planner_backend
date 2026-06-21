import {
  Card,
  CardContent,
  Typography,
} from "@mui/material";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

export default function FocusChart({
  data,
}) {
  return (
    <Card
      sx={{
        borderRadius: 5,
        height: 420,
      }}
    >
      <CardContent>

        <Typography
          variant="h6"
          mb={2}
        >
          Weekly Focus
        </Typography>

        <ResponsiveContainer
          width="100%"
          height={320}
        >
          <LineChart data={data}>
            <CartesianGrid />

            <XAxis
              dataKey="day"
            />

            <YAxis />

            <Tooltip />

            <Line
              type="monotone"
              dataKey="focus"
            />
          </LineChart>
        </ResponsiveContainer>

      </CardContent>
    </Card>
  );
}