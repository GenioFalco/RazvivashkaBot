import React, { useEffect } from 'react';
import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import WebApp from '@twa-dev/sdk';

// Импорт компонентов страниц
import MainMenu from './pages/MainMenu';

// Импорт темы
import theme from './styles/theme';

function App() {
  useEffect(() => {
    try {
      // Инициализация Telegram WebApp
      WebApp.ready();
      
      // Установка основного цвета в цвет темы Telegram
      WebApp.setHeaderColor(theme.palette.primary.main);
    } catch (error) {
      console.error('Error initializing WebApp:', error);
    }
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router basename="">
        <Routes>
          <Route exact path="/" element={<MainMenu />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App; 