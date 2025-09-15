import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Stepper,
  Step,
  StepLabel,
  CircularProgress,
  Alert,
  Chip,
  Paper,
  Divider,
  LinearProgress
} from '@mui/material';
import {
  Psychology,
  Assessment,
  CheckCircle,
  Error as ErrorIcon
} from '@mui/icons-material';
import { format } from 'date-fns';

import { apiService } from '../services/apiService';

const ReportDialog = ({ open, onClose, event }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [reportJob, setReportJob] = useState(null);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);

  const steps = [
    'Confirm Analysis',
    'Generating Report',
    'Review Results'
  ];

  useEffect(() => {
    if (open && event) {
      resetDialog();
    }
  }, [open, event]);

  const resetDialog = () => {
    setActiveStep(0);
    setReportJob(null);
    setReport(null);
    setLoading(false);
    setError(null);
    setProgress(0);
  };

  const handleStartAnalysis = async () => {
    if (!event) return;

    setLoading(true);
    setError(null);
    setActiveStep(1);

    try {
      // Start report generation
      const jobResponse = await apiService.generateReport({
        stock_symbol: event.stockSymbols[0],
        event_date: event.date.toISOString(),
        analysis_type: 'correlation_analysis',
        include_sources: ['market_data', 'sec_filing', 'news']
      });

      setReportJob(jobResponse);
      
      // Poll for completion
      pollReportStatus(jobResponse.job_id);

    } catch (err) {
      console.error('Failed to start report generation:', err);
      setError('Failed to start analysis. Please try again.');
      setLoading(false);
    }
  };

  const pollReportStatus = async (jobId) => {
    const maxAttempts = 30; // 30 attempts = 3 minutes max
    let attempts = 0;

    const poll = async () => {
      try {
        const status = await apiService.getReportStatus(jobId);
        setProgress(status.progress || 0);

        if (status.status === 'completed') {
          setReport(status.result);
          setActiveStep(2);
          setLoading(false);
          return;
        }

        if (status.status === 'failed') {
          setError(status.error_message || 'Report generation failed');
          setLoading(false);
          return;
        }

        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(poll, 6000); // Poll every 6 seconds
        } else {
          setError('Report generation timeout. Please try again.');
          setLoading(false);
        }

      } catch (err) {
        console.error('Failed to check report status:', err);
        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(poll, 6000);
        } else {
          setError('Failed to check report status. Please try again.');
          setLoading(false);
        }
      }
    };

    poll();
  };

  const handleClose = () => {
    resetDialog();
    onClose();
  };

  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Generate AI Correlation Analysis
            </Typography>
            
            {event && (
              <Paper sx={{ p: 2, mb: 3, bgcolor: 'background.default' }}>
                <Typography variant="subtitle1" gutterBottom>
                  Selected Event:
                </Typography>
                <Typography variant="body1" gutterBottom>
                  {event.title}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {event.description}
                </Typography>
                <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                  {event.stockSymbols.map(symbol => (
                    <Chip key={symbol} label={symbol} size="small" color="primary" />
                  ))}
                  <Chip 
                    label={format(event.date, 'MMM dd, yyyy HH:mm')} 
                    size="small" 
                    variant="outlined" 
                  />
                </Box>
              </Paper>
            )}

            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                This will generate an AI-powered analysis looking for correlations between:
              </Typography>
              <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                <li>Market price movements</li>
                <li>SEC filings and regulatory documents</li>
                <li>News articles and social sentiment</li>
              </ul>
            </Alert>

            <Alert severity="warning">
              <Typography variant="body2">
                <strong>Disclaimer:</strong> This analysis is AI-generated and for educational 
                purposes only. It is not financial advice. Correlations do not imply causation.
              </Typography>
            </Alert>
          </Box>
        );

      case 1:
        return (
          <Box sx={{ textAlign: 'center', py: 3 }}>
            <Psychology sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              AI Analysis in Progress
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Our AI is analyzing market data, SEC filings, and news to identify correlations...
            </Typography>
            
            <Box sx={{ width: '100%', mb: 2 }}>
              <LinearProgress variant="determinate" value={progress} />
            </Box>
            <Typography variant="caption" color="text.secondary">
              {progress}% complete
            </Typography>

            {reportJob && (
              <Box sx={{ mt: 3, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                <Typography variant="caption" display="block">
                  Job ID: {reportJob.job_id}
                </Typography>
                <Typography variant="caption" display="block">
                  Status: {reportJob.status}
                </Typography>
              </Box>
            )}
          </Box>
        );

      case 2:
        return (
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <CheckCircle sx={{ color: 'success.main', mr: 1 }} />
              <Typography variant="h6">
                Analysis Complete
              </Typography>
            </Box>

            {report && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  {report.title}
                </Typography>

                {report.confidence_score && (
                  <Box sx={{ mb: 2 }}>
                    <Chip
                      label={`Confidence: ${Math.round(report.confidence_score * 100)}%`}
                      color={
                        report.confidence_score > 0.7 ? 'success' :
                        report.confidence_score > 0.4 ? 'warning' : 'error'
                      }
                      size="small"
                    />
                  </Box>
                )}

                <Divider sx={{ my: 2 }} />

                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
                  {report.content}
                </Typography>

                {report.correlations_found && Object.keys(report.correlations_found).length > 0 && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      Key Correlations Found:
                    </Typography>
                    <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                      <pre style={{ margin: 0, fontFamily: 'inherit', fontSize: '0.875rem' }}>
                        {JSON.stringify(report.correlations_found, null, 2)}
                      </pre>
                    </Paper>
                  </Box>
                )}

                <Divider sx={{ my: 2 }} />

                <Alert severity="warning" sx={{ mt: 2 }}>
                  <Typography variant="body2">
                    <strong>Important:</strong> This analysis is AI-generated and should not be 
                    used as the sole basis for investment decisions. Always conduct additional 
                    research and consult with qualified financial advisors.
                  </Typography>
                </Alert>
              </Box>
            )}
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { minHeight: '500px' }
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Assessment sx={{ mr: 1 }} />
          AI Correlation Analysis
        </Box>
      </DialogTitle>

      <DialogContent>
        <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <ErrorIcon sx={{ mr: 1 }} />
              {error}
            </Box>
          </Alert>
        )}

        {renderStepContent()}
      </DialogContent>

      <DialogActions>
        {activeStep === 0 && (
          <>
            <Button onClick={handleClose}>
              Cancel
            </Button>
            <Button
              variant="contained"
              onClick={handleStartAnalysis}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : <Psychology />}
            >
              Start Analysis
            </Button>
          </>
        )}

        {activeStep === 1 && (
          <Button onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
        )}

        {activeStep === 2 && (
          <>
            <Button onClick={() => setActiveStep(0)}>
              Generate New Analysis
            </Button>
            <Button variant="contained" onClick={handleClose}>
              Close
            </Button>
          </>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default ReportDialog;