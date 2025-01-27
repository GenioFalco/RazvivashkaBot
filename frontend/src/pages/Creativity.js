import React, { useState, useEffect } from 'react';
import { useNavigate, Routes, Route } from 'react-router-dom';
import {
  Container,
  Grid,
  Button,
  Typography,
  Box,
  Card,
  CardContent,
  CardMedia,
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  PlayArrow as PlayArrowIcon,
  Check as CheckIcon,
  PhotoCamera as PhotoCameraIcon
} from '@mui/icons-material';
import WebApp from '@twa-dev/sdk';

const sections = [
  { title: '🎨 Рисовать', path: 'drawing' },
  { title: '📄 Бумага', path: 'paper' },
  { title: '🏺 Лепка', path: 'sculpting' }
];

function CreativityMenu() {
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
          🎨 Творчество
        </Typography>

        <Typography variant="body1" paragraph>
          Выбери раздел, в котором хочешь заниматься:
        </Typography>

        <Grid container spacing={2}>
          {sections.map((section) => (
            <Grid item xs={12} key={section.path}>
              <Button
                fullWidth
                variant="contained"
                size="large"
                onClick={() => navigate(section.path)}
                sx={{ py: 2 }}
              >
                {section.title}
              </Button>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Container>
  );
}

function MasterclassList({ section }) {
  const navigate = useNavigate();
  const [masterclasses, setMasterclasses] = useState([]);
  const [completedToday, setCompletedToday] = useState(false);
  const [showPhotoDialog, setShowPhotoDialog] = useState(false);
  const [currentMasterclass, setCurrentMasterclass] = useState(null);

  useEffect(() => {
    // Здесь будет запрос к API для получения списка мастер-классов
    // и проверка выполненных за день
  }, [section]);

  const handleComplete = async (masterclassId) => {
    // Здесь будет запрос к API для отметки выполнения
  };

  const handlePhotoUpload = async () => {
    try {
      // Запрашиваем фото через Telegram WebApp
      const photo = await WebApp.showPopup({
        title: 'Загрузка фото',
        message: 'Выберите фото вашей работы',
        buttons: [
          { id: 'camera', type: 'default', text: 'Сделать фото' },
          { id: 'gallery', type: 'default', text: 'Выбрать из галереи' },
          { id: 'cancel', type: 'cancel', text: 'Отмена' }
        ]
      });

      if (photo && photo.id !== 'cancel') {
        // Здесь будет логика загрузки фото
        setShowPhotoDialog(false);
      }
    } catch (error) {
      console.error('Error uploading photo:', error);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box py={3}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/creativity')}
          sx={{ mb: 3 }}
        >
          Назад
        </Button>

        {completedToday ? (
          <Typography variant="h6" color="error" gutterBottom>
            ⚠️ Вы уже выполнили мастер-класс сегодня!
          </Typography>
        ) : null}

        <Grid container spacing={2}>
          {masterclasses.map((masterclass) => (
            <Grid item xs={12} key={masterclass.id}>
              <Card>
                <CardMedia
                  component="img"
                  height="200"
                  image={masterclass.previewImage}
                  alt={masterclass.title}
                />
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {masterclass.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {masterclass.description}
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button
                    startIcon={<PlayArrowIcon />}
                    onClick={() => window.open(masterclass.videoUrl)}
                  >
                    Смотреть
                  </Button>
                  <Button
                    startIcon={<CheckIcon />}
                    onClick={() => handleComplete(masterclass.id)}
                    disabled={completedToday}
                  >
                    Выполнил
                  </Button>
                  <Button
                    startIcon={<PhotoCameraIcon />}
                    onClick={() => {
                      setCurrentMasterclass(masterclass);
                      setShowPhotoDialog(true);
                    }}
                  >
                    Фото
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>

        <Dialog open={showPhotoDialog} onClose={() => setShowPhotoDialog(false)}>
          <DialogTitle>Загрузка фото</DialogTitle>
          <DialogContent>
            <Typography>
              Загрузите фото вашей работы по мастер-классу "{currentMasterclass?.title}"
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowPhotoDialog(false)}>Отмена</Button>
            <Button onClick={handlePhotoUpload} variant="contained">
              Выбрать фото
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
}

function Creativity() {
  return (
    <Routes>
      <Route path="/" element={<CreativityMenu />} />
      <Route path="/drawing" element={<MasterclassList section="drawing" />} />
      <Route path="/paper" element={<MasterclassList section="paper" />} />
      <Route path="/sculpting" element={<MasterclassList section="sculpting" />} />
    </Routes>
  );
}

export default Creativity; 