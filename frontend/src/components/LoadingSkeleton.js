import React from 'react';
import { Box, Card, CardContent, Skeleton, Grid } from '@mui/material';

const LoadingSkeleton = () => {
  return (
    <Box>
      {/* Controls skeleton */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
        <Skeleton variant="rectangular" width={200} height={56} />
        <Skeleton variant="rectangular" width={100} height={56} />
      </Box>

      {/* Title skeleton */}
      <Skeleton variant="text" width={300} height={40} sx={{ mb: 1 }} />
      <Skeleton variant="text" width={500} height={24} sx={{ mb: 3 }} />

      {/* Timeline events skeleton */}
      <Grid container spacing={2}>
        {[1, 2, 3, 4].map((item) => (
          <Grid item xs={12} key={item}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Skeleton variant="circular" width={24} height={24} sx={{ mr: 1 }} />
                  <Skeleton variant="text" width={300} height={32} sx={{ flexGrow: 1 }} />
                  <Skeleton variant="text" width={100} height={16} />
                </Box>
                
                <Skeleton variant="text" width="80%" height={20} sx={{ mb: 2 }} />
                
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Skeleton variant="rectangular" width={50} height={24} sx={{ borderRadius: 12 }} />
                    <Skeleton variant="rectangular" width={80} height={24} sx={{ borderRadius: 12 }} />
                  </Box>
                  <Skeleton variant="text" width={150} height={16} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default LoadingSkeleton;