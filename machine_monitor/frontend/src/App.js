import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  ThemeProvider, 
  createTheme, 
  Card, 
  CardContent, 
  Typography, 
  Grid, 
  Box, 
  Container, 
  AppBar, 
  Toolbar,
  CssBaseline
} from '@mui/material';
import { 
  CheckCircle as CheckCircleIcon, 
  Warning as WarningIcon, 
  Error as ErrorIcon 
} from '@mui/icons-material';
import MachineCard from './components/MachineCard';

const API_URL = 'http://localhost:8000';

// Create a light theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2', // A professional blue
      light: '#4791db',
      dark: '#115293'
    },
    secondary: {
      main: '#dc004e', // A vibrant accent color
      light: '#ff4081',
      dark: '#9a0036'
    },
    background: {
      default: '#f4f6f8', // Light gray background
      paper: '#ffffff'
    },
    text: {
      primary: '#2c3345', // Dark gray for text
      secondary: '#5f6368'
    },
    success: {
      main: '#4caf50', // Green for healthy status
      light: '#81c784',
      dark: '#388e3c'
    },
    warning: {
      main: '#ff9800', // Orange for warning status
      light: '#ffb74d',
      dark: '#f57c00'
    },
    error: {
      main: '#f44336', // Red for critical status
      light: '#ef5350',
      dark: '#d32f2f'
    }
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif'
    ].join(','),
    h6: {
      fontWeight: 600
    }
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }
      }
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
        }
      }
    }
  }
});

function App() {
  const [machines, setMachines] = useState([]);
  const [machineData, setMachineData] = useState({});
  const [machineAnalysis, setMachineAnalysis] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [overallSystemHealth, setOverallSystemHealth] = useState('Healthy');

  useEffect(() => {
    const fetchMachines = async () => {
      try {
        const response = await axios.get(`${API_URL}/machines`);
        setMachines(response.data);
        setIsLoading(false);
      } catch (error) {
        console.error('Error fetching machines:', error);
        setIsLoading(false);
      }
    };
    fetchMachines();
  }, []);

  useEffect(() => {
    const fetchMachineData = async () => {
      if (machines.length === 0) return;

      try {
        const dataPromises = machines.map(async (machineId) => {
          const [metricsResponse, analysisResponse] = await Promise.all([
            axios.get(`${API_URL}/machine/${machineId}/metrics`),
            axios.get(`${API_URL}/machine/${machineId}/analysis`)
          ]);

          setMachineData(prev => ({
            ...prev,
            [machineId]: [...(prev[machineId] || []), metricsResponse.data].slice(-20)
          }));

          setMachineAnalysis(prev => ({
            ...prev,
            [machineId]: analysisResponse.data
          }));
        });

        await Promise.all(dataPromises);

        // Calculate overall system health
        const healthStatuses = Object.values(machineAnalysis)
          .map(analysis => {
            const anomalyPercentage = analysis?.anomaly_detection?.anomaly_percentage || 0;
            if (anomalyPercentage > 20) return 'Critical';
            if (anomalyPercentage > 10) return 'Warning';
            return 'Healthy';
          });

        const statusPriority = { 'Critical': 3, 'Warning': 2, 'Healthy': 1 };
        const worstStatus = healthStatuses.reduce((worst, current) => 
          statusPriority[current] > statusPriority[worst] ? current : worst, 
          'Healthy'
        );
        setOverallSystemHealth(worstStatus);

      } catch (error) {
        console.error('Error fetching machine data:', error);
      }
    };

    const interval = setInterval(fetchMachineData, 5000);
    fetchMachineData(); // Initial fetch

    return () => clearInterval(interval);
  }, [machines]);

  const getHealthIcon = () => {
    switch (overallSystemHealth) {
      case 'Healthy':
        return <CheckCircleIcon color="success" />;
      case 'Warning':
        return <WarningIcon color="warning" />;
      case 'Critical':
        return <ErrorIcon color="error" />;
      default:
        return null;
    }
  };

  if (isLoading) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Container maxWidth="xl" sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '100vh' 
        }}>
          <Typography variant="h4" color="textSecondary">
            Loading Machine Monitor...
          </Typography>
        </Container>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ 
        flexGrow: 1, 
        backgroundColor: theme.palette.background.default, 
        minHeight: '100vh',
        padding: 3 
      }}>
        <AppBar position="static" color="primary" elevation={1}>
          <Toolbar>
            <Typography variant="h6" sx={{ flexGrow: 1, color: 'white' }}>
              Machine Monitor Dashboard
            </Typography>
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              backgroundColor: 
                overallSystemHealth === 'Healthy' ? theme.palette.success.light :
                overallSystemHealth === 'Warning' ? theme.palette.warning.light :
                theme.palette.error.light,
              padding: '5px 15px',
              borderRadius: '20px'
            }}>
              {getHealthIcon()}
              <Typography variant="body2" sx={{ 
                ml: 1, 
                color: 
                  overallSystemHealth === 'Healthy' ? theme.palette.success.dark :
                  overallSystemHealth === 'Warning' ? theme.palette.warning.dark :
                  theme.palette.error.dark 
              }}>
                System Health: {overallSystemHealth}
              </Typography>
            </Box>
          </Toolbar>
        </AppBar>
        <Container maxWidth="xl" sx={{ mt: 3 }}>
          <Grid container spacing={3}>
            {machines.map(machineId => (
              <Grid item xs={12} sm={6} md={4} key={machineId}>
                <MachineCard 
                  machineId={machineId} 
                  machineData={machineData[machineId]} 
                  analysis={machineAnalysis[machineId]}
                />
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
