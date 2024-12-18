import React from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Grid, 
  Box,
  Chip
} from '@mui/material';
import { 
  CheckCircle as CheckCircleIcon, 
  Warning as WarningIcon, 
  Error as ErrorIcon 
} from '@mui/icons-material';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';

const formatTimestamp = (timestamp) => {
  const now = new Date();
  const dataTime = new Date(timestamp);
  const diff = now - dataTime;

  // Less than a minute ago
  if (diff < 60000) {
    return 'just now';
  }

  // Less than an hour ago
  if (diff < 3600000) {
    const minutes = Math.floor(diff / 60000);
    return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
  }

  // Less than a day ago
  if (diff < 86400000) {
    const hours = Math.floor(diff / 3600000);
    return `${hours} hour${hours > 1 ? 's' : ''} ago`;
  }

  // More than a day ago
  const days = Math.floor(diff / 86400000);
  return `${days} day${days > 1 ? 's' : ''} ago`;
};

const MachineCard = ({ machineId, machineData, analysis }) => {
  // Determine overall machine health
  const getHealthStatus = () => {
    if (!analysis) return 'Unknown';
    
    const anomalyPercentage = analysis.anomaly_detection?.anomaly_percentage || 0;
    if (anomalyPercentage > 20) return 'Critical';
    if (anomalyPercentage > 10) return 'Warning';
    return 'Healthy';
  };

  const getHealthColor = () => {
    const status = getHealthStatus();
    switch (status) {
      case 'Healthy': return 'success';
      case 'Warning': return 'warning';
      case 'Critical': return 'error';
      default: return 'default';
    }
  };

  const getHealthIcon = () => {
    const status = getHealthStatus();
    switch (status) {
      case 'Healthy': return <CheckCircleIcon />;
      case 'Warning': return <WarningIcon />;
      case 'Critical': return <ErrorIcon />;
      default: return null;
    }
  };

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" color="textPrimary">{machineId}</Typography>
          <Chip 
            icon={getHealthIcon()} 
            label={`Status: ${getHealthStatus()}`} 
            color={getHealthColor()}
            variant="outlined"
          />
        </Box>

        <Box height={250} width="100%">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={machineData || []}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis 
                dataKey="timestamp" 
                tickFormatter={formatTimestamp}
                tick={{ fill: '#666' }} 
                axisLine={{ stroke: '#666' }}
              />
              <YAxis 
                tick={{ fill: '#666' }} 
                axisLine={{ stroke: '#666' }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#f4f4f4', 
                  border: '1px solid #ddd',
                  borderRadius: '8px'
                }} 
              />
              <Legend />
              <Line type="monotone" dataKey="temperature" stroke="#1976d2" name="Temperature" strokeWidth={2} />
              <Line type="monotone" dataKey="cpu_usage" stroke="#4caf50" name="CPU Usage" strokeWidth={2} />
              <Line type="monotone" dataKey="memory_usage" stroke="#ff9800" name="Memory Usage" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </Box>

        <Grid container spacing={2} mt={2}>
          <Grid item xs={4} textAlign="center">
            <Typography variant="subtitle2" color="textSecondary">Temperature</Typography>
            <Typography variant="h6" color="textPrimary">
              {analysis?.statistical_summary?.temperature?.mean?.toFixed(2) || 'N/A'}°C
            </Typography>
          </Grid>
          <Grid item xs={4} textAlign="center">
            <Typography variant="subtitle2" color="textSecondary">CPU Usage</Typography>
            <Typography variant="h6" color="textPrimary">
              {analysis?.statistical_summary?.cpu_usage?.mean?.toFixed(2) || 'N/A'}%
            </Typography>
          </Grid>
          <Grid item xs={4} textAlign="center">
            <Typography variant="subtitle2" color="textSecondary">Memory Usage</Typography>
            <Typography variant="h6" color="textPrimary">
              {analysis?.statistical_summary?.memory_usage?.mean?.toFixed(2) || 'N/A'}%
            </Typography>
          </Grid>
        </Grid>

        <Box mt={2} textAlign="center">
          <Typography variant="body2" color="textSecondary">
            Anomalies: {analysis?.anomaly_detection?.anomaly_count || 0} 
            ({(analysis?.anomaly_detection?.anomaly_percentage || 0).toFixed(2)}%)
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default MachineCard;
