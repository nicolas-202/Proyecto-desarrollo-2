import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ProtectedRoute = ({ children, adminOnly = false, redirectTo = '/auth' }) => {
  const { isAuthenticated, isLoading, isAdmin } = useAuth();
  const location = useLocation();

  // Mostrar loader mientras se verifica la autenticación
  if (isLoading) {
    return (
      <div className="protected-route-loading">
        <div className="spinner"></div>
        <p>Verificando acceso...</p>
      </div>
    );
  }

  // Si no está autenticado, redirigir al login con la ruta actual
  if (!isAuthenticated) {
    return (
      <Navigate 
        to={`${redirectTo}?redirect=${encodeURIComponent(location.pathname + location.search)}`}
        replace 
      />
    );
  }

  // Si requiere permisos de admin y el usuario no es admin
  if (adminOnly && !isAdmin()) {
    return (
      <div className="access-denied">
        <div className="access-denied-content">
          <div className="access-denied-icon">🚫</div>
          <h2>Acceso Denegado</h2>
          <p>No tienes permisos suficientes para acceder a esta página.</p>
          <button 
            className="btn btn-primary"
            onClick={() => window.history.back()}
          >
            Volver Atrás
          </button>
        </div>
      </div>
    );
  }

  // Si todo está bien, renderizar los children
  return children;
};

export default ProtectedRoute;