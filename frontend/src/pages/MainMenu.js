import React from 'react';
import { Box, Typography } from '@mui/material';

function MainMenu() {
  return (
    <Box 
      sx={{ 
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        minHeight: '100vh'
      }}
    >
      <Typography variant="h4" component="h1" gutterBottom>
        Привет! Я БотРазвивашка!
      </Typography>
      <Typography variant="body1">
        Добро пожаловать в мини-приложение!
      </Typography>
    </Box>
  );
}

export default MainMenu; 