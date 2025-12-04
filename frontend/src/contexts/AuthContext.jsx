import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { authService } from '../services/authService';

// Estado inicial - como empieza la aplicación
const initialState = {
  user: null, // Información del usuario (nombre, email, etc.)
  token: null, // Token JWT para hacer peticiones autenticadas
  refreshToken: null, // Token para renovar el acceso cuando expire
  isAuthenticated: false, // ¿Está logueado?
  isLoading: true, // ¿Estamos cargando?
  error: null, // ¿Hay algún error?
};

// Tipos de acciones que pueden pasar
const AUTH_ACTIONS = {
  LOGIN_START: 'LOGIN_START',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_ERROR: 'LOGIN_ERROR',
  LOGOUT: 'LOGOUT',
  REGISTER_START: 'REGISTER_START',
  REGISTER_SUCCESS: 'REGISTER_SUCCESS',
  REGISTER_ERROR: 'REGISTER_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR',
  SET_LOADING: 'SET_LOADING',
  RESTORE_SESSION: 'RESTORE_SESSION',
};

// Reducer - decide qué hacer cuando pasa cada acción
const authReducer = (state, action) => {
  switch (action.type) {
    case AUTH_ACTIONS.LOGIN_START:
    case AUTH_ACTIONS.REGISTER_START:
      return {
        ...state,
        isLoading: true,
        error: null,
      };

    case AUTH_ACTIONS.LOGIN_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.access,
        refreshToken: action.payload.refresh,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };

    case AUTH_ACTIONS.REGISTER_SUCCESS:
      return {
        ...state,
        isLoading: false,
        error: null,
        // No guardamos usuario hasta que haga login
      };

    case AUTH_ACTIONS.LOGIN_ERROR:
    case AUTH_ACTIONS.REGISTER_ERROR:
      return {
        ...state,
        user: null,
        token: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      };

    case AUTH_ACTIONS.LOGOUT:
      return {
        ...initialState,
        isLoading: false,
      };

    case AUTH_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null,
      };

    case AUTH_ACTIONS.SET_LOADING:
      return {
        ...state,
        isLoading: action.payload,
      };

    case AUTH_ACTIONS.RESTORE_SESSION:
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        refreshToken: action.payload.refreshToken,
        isAuthenticated: true,
        isLoading: false,
      };

    default:
      return state;
  }
};

// Crear el contexto
const AuthContext = createContext();

// Hook personalizado para usar la autenticación en cualquier componente
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de un AuthProvider');
  }
  return context;
};

// Proveedor del contexto - envuelve toda la aplicación
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Al cargar la app, intentar restaurar la sesión desde localStorage
  useEffect(() => {
    const restoreSession = () => {
      try {
        const storedToken = localStorage.getItem('accessToken');
        const storedRefreshToken = localStorage.getItem('refreshToken');
        const storedUser = localStorage.getItem('user');

        if (storedToken && storedRefreshToken && storedUser) {
          // Verificar si el token no ha expirado
          const tokenData = JSON.parse(atob(storedToken.split('.')[1]));
          const currentTime = Date.now() / 1000;

          if (tokenData.exp > currentTime) {
            dispatch({
              type: AUTH_ACTIONS.RESTORE_SESSION,
              payload: {
                token: storedToken,
                refreshToken: storedRefreshToken,
                user: JSON.parse(storedUser),
              },
            });
          } else {
            // Token expirado, limpiar todo
            clearStoredAuth();
            dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
          }
        } else {
          dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
        }
      } catch (error) {
        console.error('Error al restaurar sesión:', error);
        clearStoredAuth();
        dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
      }
    };

    restoreSession();
  }, []);

  // Funciones auxiliares para manejar localStorage
  const clearStoredAuth = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  };

  const storeAuthData = (tokens, user) => {
    localStorage.setItem('accessToken', tokens.access);
    localStorage.setItem('refreshToken', tokens.refresh);
    localStorage.setItem('user', JSON.stringify(user));
  };

  // Función de login - conectada al backend real
  const login = async credentials => {
    try {
      dispatch({ type: AUTH_ACTIONS.LOGIN_START });

      const response = await authService.login(credentials);
      const { access, refresh, user } = response;

      // Guardar en localStorage para que persista al recargar
      storeAuthData({ access, refresh }, user);

      dispatch({
        type: AUTH_ACTIONS.LOGIN_SUCCESS,
        payload: { access, refresh, user },
      });

      return { success: true };
    } catch (error) {
      const errorMessage =
        error.response?.data?.detail || error.response?.data?.message || 'Error al iniciar sesión';

      dispatch({
        type: AUTH_ACTIONS.LOGIN_ERROR,
        payload: errorMessage,
      });

      return { success: false, error: errorMessage };
    }
  };

  // Función de registro - conectada al backend real
  const register = async userData => {
    try {
      dispatch({ type: AUTH_ACTIONS.REGISTER_START });

      await authService.register(userData);

      dispatch({ type: AUTH_ACTIONS.REGISTER_SUCCESS });

      return { success: true, message: 'Usuario registrado exitosamente' };
    } catch (error) {
      const errorMessage =
        error.response?.data?.message ||
        error.response?.data?.detail ||
        'Error al registrar usuario';

      dispatch({
        type: AUTH_ACTIONS.REGISTER_ERROR,
        payload: errorMessage,
      });

      return { success: false, error: errorMessage };
    }
  };

  // Función de logout
  const logout = () => {
    clearStoredAuth();
    dispatch({ type: AUTH_ACTIONS.LOGOUT });
  };

  // Limpiar errores
  const clearError = () => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  };

  // Verificar si es admin (computed value, no función)
  const isAdmin = state.user?.is_staff || state.user?.is_admin || false;

  // Lo que estará disponible para toda la aplicación
  const contextValue = {
    // Estado actual
    ...state,

    // Funciones
    login,
    register,
    logout,
    clearError,

    // Computed values
    isAdmin,
  };

  return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>;
};

export default AuthContext;
