import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

function Header() {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout, isAdmin, isLoading } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleNavigate = (path) => {
    navigate(path);
    setMobileMenuOpen(false); // Cerrar menú móvil al navegar
  };

  // Mostrar loading si aún se está verificando la autenticación
  if (isLoading) {
    return (
      <div className="header">
        <div className="header-content">
          <div className="logo" onClick={() => handleNavigate('/')}>
            🎰 RifaPlus
          </div>
          <div style={{ color: 'white', fontSize: '0.9rem' }}>
            Cargando...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="header">
      <div className="header-content">
        {/* Logo */}
        <div className="logo" onClick={() => handleNavigate('/')}>
          🎰 RifaPlus
        </div>

        {/* Botón hamburguesa para móvil */}
        <button 
          className="mobile-menu-btn"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle menu"
        >
          <span className={`hamburger ${mobileMenuOpen ? 'open' : ''}`}>
            <span></span>
            <span></span>
            <span></span>
          </span>
        </button>

        {/* Menú de navegación */}
        <div className={`nav-menu ${mobileMenuOpen ? 'mobile-open' : ''}`}>
          <div 
            className="nav-item active" 
            onClick={() => handleNavigate('/')}
          >
            Descubre rifas
          </div>

          {/* Buscar usuarios - Disponible para todos */}
          <div 
            className="nav-item" 
            onClick={() => handleNavigate('/search-users')}
          >
            👥 Usuarios
          </div>

          {/* Menú solo para usuarios autenticados */}
          {isAuthenticated && (
            <>
              <div 
                className="nav-item" 
                onClick={() => handleNavigate('/my-numbers')}
              >
                Mis números
              </div>

              <div 
                className="nav-item" 
                onClick={() => handleNavigate('/create-raffle')}
              >
                Lanza tu rifa
              </div>

              <div 
                className="nav-item notification-badge" 
                onClick={() => {/* TODO: toggleNotifications */}}
              >
                🔔
                <span className="badge-count">0</span>
              </div>
            </>
          )}

          {/* Configuración (solo para administradores) */}
          {isAuthenticated && isAdmin && (
            <div 
              className="nav-item" 
              onClick={() => handleNavigate('/config')}
            >
              ⚙️ Configuración
            </div>
          )}

          {/* Sección de autenticación - Botón Entrar O Menú de usuario */}
          {!isAuthenticated ? (
            // Usuario no autenticado - Mostrar botón Entrar
            <div id="nav-auth">
              <button 
                className="btn-primary" 
                onClick={() => handleNavigate('/auth')}
              >
                Entrar
              </button>
            </div>
          ) : (
            // Usuario autenticado - Mostrar menú de usuario
            <div id="nav-user">
              <div 
                className="nav-item" 
                onClick={() => handleNavigate(`/user/${user?.id}`)}
              >
                👤 {user?.first_name || 'Mi perfil'}
              </div>
              <button 
                className="btn-secondary" 
                onClick={() => {
                  logout();
                  handleNavigate('/');
                }}
              >
                Salir
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Header;
