import React from 'react';
import { Routes, Route } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Paper,
  Alert,
  Link
} from '@mui/material';
import { Assessment, Security, TrendingUp } from '@mui/icons-material';

// Components
import Timeline from './components/Timeline';
import ReportViewer from './components/ReportViewer';

function App() {
  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* Header */}
      <AppBar position="static" sx={{ mb: 3 }}>
        <Toolbar>
          <Security sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Shadow SEC - Financial Watchdog
          </Typography>
          <TrendingUp />
        </Toolbar>
      </AppBar>

      {/* Legal Disclaimer Banner */}
      <Container maxWidth="lg">
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="body2">
            <strong>IMPORTANT DISCLAIMER:</strong> All reports and analysis provided by Shadow SEC 
            are AI-generated and for educational purposes only. This is NOT financial advice. 
            Correlations do not imply causation. Always conduct your own research and consult 
            with qualified financial advisors before making investment decisions.
          </Typography>
        </Alert>

        {/* Mission Statement */}
        <Paper elevation={2} sx={{ p: 3, mb: 3, textAlign: 'center' }}>
          <Assessment sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
          <Typography variant="h4" gutterBottom>
            Transparent Market Surveillance
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Empowering the public through open-source, AI-driven analysis of financial markets, 
            SEC filings, and market news. Our mission is to provide transparent, unbiased insights 
            into potential market anomalies and correlations.
          </Typography>
        </Paper>

        {/* Main Content */}
        <Routes>
          <Route path="/" element={<Timeline />} />
          <Route path="/report/:reportId" element={<ReportViewer />} />
        </Routes>

        {/* Footer */}
        <Box sx={{ mt: 6, py: 3, borderTop: '1px solid #e0e0e0', textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            © 2024 Shadow SEC - Open Source Financial Watchdog |{' '}
            <Link href="https://github.com/rajiv-rathod/Shadow-SEC" target="_blank" rel="noopener">
              GitHub
            </Link>{' '}
            | Built with transparency and accountability
          </Typography>
        </Box>
      </Container>
    </Box>
  );
}

export default App;