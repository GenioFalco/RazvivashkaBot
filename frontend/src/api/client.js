import axios from 'axios';
import WebApp from '@twa-dev/sdk';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Добавляем перехватчик для добавления данных пользователя из Telegram WebApp
client.interceptors.request.use((config) => {
  const initData = WebApp.initData;
  if (initData) {
    config.headers['X-Telegram-Init-Data'] = initData;
  }
  return config;
});

// API методы для творчества
export const creativityApi = {
  // Получение списка мастер-классов
  getMasterclasses: (section) => 
    client.get(`/api/creativity/${section}`),

  // Проверка выполнения мастер-класса сегодня
  checkDailyCompletion: () =>
    client.get('/api/creativity/check-daily'),

  // Отметка выполнения мастер-класса
  completeMasterclass: (masterclassId) =>
    client.post(`/api/creativity/complete/${masterclassId}`),

  // Загрузка фото работы
  uploadPhoto: (masterclassId, photo) => {
    const formData = new FormData();
    formData.append('photo', photo);
    return client.post(`/api/creativity/upload-photo/${masterclassId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

// API методы для ежедневных заданий
export const dailyTasksApi = {
  // Получение списка заданий
  getTasks: () => 
    client.get('/api/daily-tasks'),

  // Отметка выполнения задания
  completeTask: (taskId) =>
    client.post(`/api/daily-tasks/complete/${taskId}`),
};

// API методы для ребусов
export const puzzlesApi = {
  // Получение списка ребусов
  getPuzzles: () =>
    client.get('/api/puzzles'),

  // Проверка ответа
  checkAnswer: (puzzleId, answer) =>
    client.post(`/api/puzzles/check/${puzzleId}`, { answer }),
};

// API методы для загадок
export const riddlesApi = {
  // Получение списка загадок
  getRiddles: () =>
    client.get('/api/riddles'),

  // Проверка ответа
  checkAnswer: (riddleId, answer) =>
    client.post(`/api/riddles/check/${riddleId}`, { answer }),
};

// API методы для скороговорок
export const tongueTwistersApi = {
  // Получение списка скороговорок
  getTwisters: () =>
    client.get('/api/tongue-twisters'),

  // Отметка выполнения
  complete: (twisterId) =>
    client.post(`/api/tongue-twisters/complete/${twisterId}`),
};

// API методы для упражнений
export const exercisesApi = {
  // Получение списка упражнений
  getExercises: (type) =>
    client.get(`/api/exercises/${type}`),

  // Отметка выполнения
  complete: (exerciseId, status) =>
    client.post(`/api/exercises/complete/${exerciseId}`, { status }),
};

// API методы для достижений
export const achievementsApi = {
  // Получение списка достижений
  getAchievements: () =>
    client.get('/api/achievements'),

  // Получение статистики токенов
  getTokenStats: () =>
    client.get('/api/achievements/tokens'),
};

// API методы для родительского раздела
export const parentsApi = {
  // Получение информации о подписке
  getSubscription: () =>
    client.get('/api/subscription'),

  // Получение реферальной статистики
  getReferralStats: () =>
    client.get('/api/referral/stats'),

  // Получение реферальной ссылки
  getReferralLink: () =>
    client.get('/api/referral/link'),
};

export default client; 