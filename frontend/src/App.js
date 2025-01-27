import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import WebApp from '@twa-dev/sdk';

// Импорт компонентов страниц
import MainMenu from './pages/MainMenu';
import Creativity from './pages/Creativity';
import DailyTasks from './pages/DailyTasks';
import Puzzles from './pages/Puzzles';
import Riddles from './pages/Riddles';
import TongueTwisters from './pages/TongueTwisters';
import Exercises from './pages/Exercises';
import Achievements from './pages/Achievements';
import PhotoBoard from './pages/PhotoBoard';
import ForParents from './pages/ForParents';

// Импорт темы
import theme from './styles/theme';

function App() {
  useEffect(() => {
    // Инициализация Telegram WebApp
    WebApp.ready();
    
    // Установка основного цвета в цвет темы Telegram
    WebApp.setHeaderColor(theme.palette.primary.main);
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<MainMenu />} />
          <Route path="/creativity/*" element={<Creativity />} />
          <Route path="/daily-tasks" element={<DailyTasks />} />
          <Route path="/puzzles" element={<Puzzles />} />
          <Route path="/riddles" element={<Riddles />} />
          <Route path="/tongue-twisters" element={<TongueTwisters />} />
          <Route path="/exercises/*" element={<Exercises />} />
          <Route path="/achievements" element={<Achievements />} />
          <Route path="/photo-board" element={<PhotoBoard />} />
          <Route path="/for-parents" element={<ForParents />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App; 