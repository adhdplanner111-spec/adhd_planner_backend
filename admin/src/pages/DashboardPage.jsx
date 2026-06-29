import {
  Typography,
  CircularProgress,
  Box,
} from "@mui/material";

import Grid from "@mui/material/Grid";

import { useEffect, useState } from "react";

import api from "../services/api";

import StatCard from "../components/StatCard";
import FocusChart from "../components/FocusChart";
import TaskChart from "../components/TaskChart";
import ActivityLog from "../components/ActivityLog";

export default function DashboardPage() {
  const [loading, setLoading] =
    useState(true);

  const [data, setData] =
    useState(null);

  const [weeklyData, setWeeklyData] =
    useState([]);

  const [logs, setLogs] =
    useState([]);
  
  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const dashboardResponse =
        await api.get(
          "/admin/dashboard"
        );

      const weeklyResponse =
        await api.get(
          "/admin/analytics/weekly"
        );

      const activityResponse =
        await api.get(
            "/admin/activity-logs"
      );

      setLogs(
        activityResponse.data.data
      );

      setData(
        dashboardResponse.data.data
      );

      setWeeklyData(
        weeklyResponse.data.data
      );
    } catch (error) {
      console.log(error);
    }

    setLoading(false);
  };

  if (loading || !data) {
    return (
      <Box
        sx={{
          height: "70vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Grid
        container
        spacing={3}
      >

        <Grid size={{ xs: 12, sm: 6, md: 4, lg: 2.4 }}>
          <StatCard
            title="Users"
            value={data.total_users}
          />
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 4, lg: 2.4 }}>
          <StatCard
            title="Tasks"
            value={data.total_tasks}
          />
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 4, lg: 2.4 }}>
          <StatCard
            title="Focus Plans"
            value={data.total_focus_plans}
          />
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 4, lg: 2.4 }}>
          <StatCard
            title="Sessions"
            value={data.total_focus_sessions}
          />
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 4, lg: 2.4 }}>
          <StatCard
            title="Pending OTP"
            value={data.pending_registrations}
          />
        </Grid>

        <Grid size={{ xs: 12, lg: 8 }}>
          <FocusChart
            data={weeklyData}
          />
        </Grid>

        <Grid size={{ xs: 12, lg: 4 }}>
          <TaskChart
            completed={
              data.completed_tasks
            }
            pending={
              data.pending_tasks
            }
          />
        </Grid>
        
        <Grid size={12}>
            <ActivityLog
                logs={logs}
            />
        </Grid>

      </Grid>

    </Box>
  );
}