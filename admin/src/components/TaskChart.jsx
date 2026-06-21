import {
  Card,
  CardContent,
  Typography,
} from "@mui/material";

import {
  PieChart,
  Pie,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function TaskChart({
  completed,
  pending,
}) {

  const data = [
    {
      name: "Completed",
      value: completed,
    },
    {
      name: "Pending",
      value: pending,
    },
  ];

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
          Task Status
        </Typography>

        <ResponsiveContainer
          width="100%"
          height={320}
        >
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              outerRadius={100}
              label
            />

            <Tooltip />
          </PieChart>
        </ResponsiveContainer>

      </CardContent>
    </Card>
  );
}