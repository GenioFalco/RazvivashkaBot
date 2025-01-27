import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Container, 
  Grid, 
  Button, 
  Typography,
  Box
} from '@mui/material';
import {
  Palette as PaletteIcon,
  Assignment as AssignmentIcon,
  Extension as ExtensionIcon,
  QuestionMark as QuestionMarkIcon,
  RecordVoiceOver as RecordVoiceOverIcon,
  FitnessCenter as FitnessCenterIcon,
  EmojiEvents as EmojiEventsIcon,
  PhotoLibrary as PhotoLibraryIcon,
  People as PeopleIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';

const menuItems = [
  { title: '📝 Задания на день', path: '/daily-tasks', icon: AssignmentIcon },
  { title: '🎨 Творчество', path: '/creativity', icon: PaletteIcon },
  { title: '🧩 Ребусы', path: '/puzzles', icon: ExtensionIcon },
  { title: '❓ Загадки', path: '/riddles', icon: QuestionMarkIcon },
  { title: '👄 Скороговорки', path: '/tongue-twisters', icon: RecordVoiceOverIcon },
  { title: '🧠 Нейрогимнастика', path: '/exercises/neuro', icon: FitnessCenterIcon },
  { title: '👅 Артикуляция', path: '/exercises/articular', icon: RecordVoiceOverIcon },
  { title: '🏆 Достижения', path: '/achievements', icon: EmojiEventsIcon },
  { title: '🖼 Доска для всех', path: '/photo-board', icon: PhotoLibraryIcon },
  { title: '👩‍👦 Для мам', path: '/for-parents', icon: PeopleIcon }
];

function MainMenu() {
  const navigate = useNavigate();

  return (
    <Container maxWidth="sm">
      <Box py={3}>
        <Typography variant="h4" component="h1" align="center" gutterBottom>
          👋 Привет! Я БотРазвивашка!
        </Typography>
        
        <Typography variant="body1" align="center" paragraph>
          Я помогу тебе:
          • Выполнять интересные задания
          • Учиться рисовать
          • Развивать творческие способности
          • Получать награды за успехи
        </Typography>

        <Grid container spacing={2} sx={{ mt: 2 }}>
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <Grid item xs={12} key={item.path}>
                <Button
                  fullWidth
                  variant="contained"
                  size="large"
                  onClick={() => navigate(item.path)}
                  startIcon={<Icon />}
                  sx={{
                    justifyContent: 'flex-start',
                    textAlign: 'left',
                    py: 2
                  }}
                >
                  {item.title}
                </Button>
              </Grid>
            );
          })}
        </Grid>
      </Box>
    </Container>
  );
}

export default MainMenu; 