import axios from 'axios';
import { API_BASE_URL } from '../config';

// Crear una instancia de axios configurada para tu API
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor: automáticamente agrega el token a todas las peticiones
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Servicio de autenticación
export const authService = {
  /**
   * Iniciar sesión
   * @param {Object} credentials - { email, password }
   * @returns {Promise} Respuesta con tokens y datos del usuario
   */
  async login(credentials) {
    try {
      const response = await apiClient.post('/auth/login/', credentials);
      return response.data;
    } catch (error) {
      // Re-lanzar el error para que el AuthContext lo maneje
      throw error;
    }
  },

  /**
   * Registrar nuevo usuario
   * @param {Object} userData - Todos los datos del formulario de registro
   * @returns {Promise} Respuesta del servidor
   */
  async register(userData) {
    try {
      const response = await apiClient.post('/auth/register/', userData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Renovar token de acceso
   * @param {string} refreshToken - Token de refresco
   * @returns {Promise} Nuevos tokens
   */
  async refreshToken(refreshToken) {
    try {
      const response = await apiClient.post('/auth/refresh/', {
        refresh: refreshToken,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Obtener perfil del usuario autenticado
   * @returns {Promise} Datos del perfil del usuario
   */
  async getUserProfile() {
    try {
      const response = await apiClient.get('/auth/me/');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Obtener lista de países
   */
  async getCountries() {
    try {
      const response = await apiClient.get('/location/countries/');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Obtener lista de departamentos/estados por país
   */
  async getStates(countryId) {
    try {
      const response = await apiClient.get(`/location/states/?country=${countryId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Obtener lista de ciudades por departamento/estado
   */
  async getCities(stateId) {
    try {
      const response = await apiClient.get(`/location/cities/?state=${stateId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Obtener lista de géneros para el formulario de registro
   */
  async getGenders() {
    try {
      const response = await apiClient.get('/user-info/genders/');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Obtener lista de tipos de documento para el formulario de registro
   */
  async getDocumentTypes() {
    try {
      const response = await apiClient.get('/user-info/document-types/');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Validar si un token es válido
   * @param {string} token - Token a validar
   * @returns {boolean} True si el token es válido
   */
  isTokenValid(token) {
    if (!token) return false;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      return payload.exp > currentTime;
    } catch (error) {
      return false;
    }
  },

  /**
   * Limpiar datos de autenticación almacenados
   */
  clearAuthData() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  },
};

// Exportar también el cliente HTTP configurado por si lo necesitas en otros lugares
export { apiClient };

export default authService;
