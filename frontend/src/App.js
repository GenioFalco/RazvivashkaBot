import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import WebApp from '@twa-dev/sdk';

// Импорт компонентов страниц
import MainMenu from './pages/MainMenu';

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
      <Router basename={process.env.PUBLIC_URL}>
        <Routes>
          <Route path="/" element={<MainMenu />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App; 