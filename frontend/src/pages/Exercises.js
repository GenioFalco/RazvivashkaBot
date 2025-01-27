import React from 'react';
import { useNavigate, Routes, Route } from 'react-router-dom';
import { Container, Typography, Button, Box } from '@mui/material';
import { ArrowBack as ArrowBackIcon } from '@mui/icons-material';

function ExercisesMenu() {
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
          🧠 Упражнения
        </Typography>

        <Typography variant="body1">
          Раздел в разработке
        </Typography>
      </Box>
    </Container>
  );
}

function Exercises() {
  return (
    <Routes>
      <Route path="/" element={<ExercisesMenu />} />
      <Route path="/neuro" element={<ExercisesMenu />} />
      <Route path="/articular" element={<ExercisesMenu />} />
    </Routes>
  );
}

export default Exercises; 