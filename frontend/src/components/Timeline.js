import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Button,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import {
  TrendingUp,
  Article,
  Description,
  PlayArrow
} from '@mui/icons-material';
import { format } from 'date-fns';

import ReportDialog from './ReportDialog';
import LoadingSkeleton from './LoadingSkeleton';

// Mock data for MVP demonstration
const mockEvents = [
  {
    id: 1,
    type: 'market_data',
    date: new Date('2024-01-15T09:30:00'),
    title: 'AAPL Stock Price Movement',
    description: 'Apple Inc. stock dropped 3.2% in morning trading',
    stockSymbols: ['AAPL'],
    metadata: {
      priceChange: -3.2,
      volume: 45000000,
      price: 185.64
    }
  },
  {
    id: 2,
    type: 'sec_filing',
    date: new Date('2024-01-15T08:00:00'),
    title: 'AAPL Files 8-K Form',
    description: 'Apple Inc. filed an 8-K form regarding executive compensation changes',
    stockSymbols: ['AAPL'],
    metadata: {
      filingType: '8-K',
      accessionNumber: '0000320193-24-000001'
    }
  },
  {
    id: 3,
    type: 'news',
    date: new Date('2024-01-15T07:45:00'),
    title: 'Apple Announces New AI Initiative',
    description: 'Apple Inc. announces significant investment in artificial intelligence research',
    stockSymbols: ['AAPL'],
    metadata: {
      source: 'Reuters',
      sentiment: 0.7
    }
  },
  {
    id: 4,
    type: 'market_data',
    date: new Date('2024-01-14T16:00:00'),
    title: 'TSLA Earnings Beat',
    description: 'Tesla reports strong Q4 earnings, stock surges 8.5%',
    stockSymbols: ['TSLA'],
    metadata: {
      priceChange: 8.5,
      volume: 120000000,
      price: 248.32
    }
  }
];

const Timeline = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedStock, setSelectedStock] = useState('');
  const [reportDialogOpen, setReportDialogOpen] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [error, setError] = useState(null);

  const trackedStocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'BRK.B', 'JNJ', 'V'];

  const loadTimelineData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      // For MVP, use mock data
      // In production, this would call: await apiService.getTimeline(selectedStock);
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      let filteredEvents = mockEvents;
      if (selectedStock) {
        filteredEvents = mockEvents.filter(event => 
          event.stockSymbols.includes(selectedStock)
        );
      }
      
      setEvents(filteredEvents);
    } catch (err) {
      console.error('Failed to load timeline data:', err);
      setError('Failed to load timeline data. Please try again.');
      setEvents(mockEvents); // Fallback to mock data
    } finally {
      setLoading(false);
    }
  }, [selectedStock]);

  useEffect(() => {
    loadTimelineData();
  }, [selectedStock, loadTimelineData]);

  const handleEventClick = (event) => {
    setSelectedEvent(event);
    setReportDialogOpen(true);
  };

  const getEventIcon = (type) => {
    switch (type) {
      case 'market_data':
        return <TrendingUp />;
      case 'sec_filing':
        return <Description />;
      case 'news':
        return <Article />;
      default:
        return <TrendingUp />;
    }
  };

  const getEventColor = (type, metadata) => {
    switch (type) {
      case 'market_data':
        if (metadata?.priceChange > 0) return '#4caf50';
        if (metadata?.priceChange < 0) return '#f44336';
        return '#ff9800';
      case 'sec_filing':
        return '#2196f3';
      case 'news':
        return '#9c27b0';
      default:
        return '#757575';
    }
  };

  const formatEventMetadata = (type, metadata) => {
    switch (type) {
      case 'market_data':
        return `Price: $${metadata?.price} | Change: ${metadata?.priceChange > 0 ? '+' : ''}${metadata?.priceChange}%`;
      case 'sec_filing':
        return `Filing: ${metadata?.filingType} | ${metadata?.accessionNumber}`;
      case 'news':
        return `Source: ${metadata?.source} | Sentiment: ${metadata?.sentiment > 0 ? 'Positive' : metadata?.sentiment < 0 ? 'Negative' : 'Neutral'}`;
      default:
        return '';
    }
  };

  if (loading) {
    return <LoadingSkeleton />;
  }

  return (
    <Box>
      {/* Controls */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2, alignItems: 'center' }}>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Filter by Stock</InputLabel>
          <Select
            value={selectedStock}
            label="Filter by Stock"
            onChange={(e) => setSelectedStock(e.target.value)}
          >
            <MenuItem value="">All Stocks</MenuItem>
            {trackedStocks.map(stock => (
              <MenuItem key={stock} value={stock}>{stock}</MenuItem>
            ))}
          </Select>
        </FormControl>
        
        <Button
          variant="outlined"
          onClick={loadTimelineData}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Timeline */}
      <Typography variant="h5" gutterBottom>
        Market Events Timeline
      </Typography>
      
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Click on any event to generate an AI-powered correlation analysis report.
      </Typography>

      <Grid container spacing={2}>
        {events.map((event) => (
          <Grid item xs={12} key={event.id}>
            <Card
              sx={{
                cursor: 'pointer',
                transition: 'all 0.2s',
                borderLeft: `4px solid ${getEventColor(event.type, event.metadata)}`,
                '&:hover': {
                  boxShadow: 4,
                  transform: 'translateY(-2px)'
                }
              }}
              onClick={() => handleEventClick(event)}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Box sx={{ color: getEventColor(event.type, event.metadata), mr: 1 }}>
                    {getEventIcon(event.type)}
                  </Box>
                  <Typography variant="h6" sx={{ flexGrow: 1 }}>
                    {event.title}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {format(event.date, 'MMM dd, yyyy HH:mm')}
                  </Typography>
                </Box>

                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {event.description}
                </Typography>

                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    {event.stockSymbols.map(symbol => (
                      <Chip
                        key={symbol}
                        label={symbol}
                        size="small"
                        variant="outlined"
                        color="primary"
                      />
                    ))}
                    <Chip
                      label={event.type.replace('_', ' ').toUpperCase()}
                      size="small"
                      sx={{ 
                        backgroundColor: getEventColor(event.type, event.metadata),
                        color: 'white'
                      }}
                    />
                  </Box>

                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                      {formatEventMetadata(event.type, event.metadata)}
                    </Typography>
                    <PlayArrow sx={{ color: 'action.active' }} />
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {events.length === 0 && !loading && (
        <Alert severity="info" sx={{ mt: 3 }}>
          No events found for the selected criteria. Try adjusting your filters or refresh the data.
        </Alert>
      )}

      {/* Report Generation Dialog */}
      <ReportDialog
        open={reportDialogOpen}
        onClose={() => setReportDialogOpen(false)}
        event={selectedEvent}
      />
    </Box>
  );
};

export default Timeline;