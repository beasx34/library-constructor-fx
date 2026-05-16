// api.ts
import axios from 'axios'
const baseURL = (process.env.NEXT_PUBLIC_BASE_URL ?? 'https://rapidstream.ru').replace(/\/+$/, '');

export const api = axios.create({
  baseURL: `${baseURL}/v2`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: true, // Для передачи кук, если требуется
})

// Добавляем обработчик ошибок CORS
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 0) {
      return Promise.reject(new Error('CORS Error: Проверьте настройки сервера'))
    }
    return Promise.reject(error)
  }
)