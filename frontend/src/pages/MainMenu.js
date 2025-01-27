import React from 'react';
import { Container, Typography, Box } from '@mui/material';

function MainMenu() {
  return (
    <Container maxWidth="sm">
      <Box py={3}>
        <Typography variant="h4" component="h1" align="center" gutterBottom>
          👋 Привет! Я БотРазвивашка!
        </Typography>
        
        <Typography variant="body1" align="center">
          Добро пожаловать в мини-приложение!
        </Typography>
      </Box>
    </Container>
  );
}

export default MainMenu; 