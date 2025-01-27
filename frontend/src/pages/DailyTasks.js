import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Typography, Button, Box } from '@mui/material';
import { ArrowBack as ArrowBackIcon } from '@mui/icons-material';

function DailyTasks() {
  const navigate = useNavigate();

  return (
    <Container maxWidth="sm">
      <Box py={3}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/')}
          sx={{ mb: 3 }}
        >
          Назад
        </Button>

        <Typography variant="h4" component="h1" gutterBottom>
          📝 Задания на день
        </Typography>

        <Typography variant="body1">
          Раздел в разработке
        </Typography>
      </Box>
    </Container>
  );
}

export default DailyTasks; 