import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

function Header() {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout, isAdmin, isLoading } = useAuth();

  const handleNavigate = (path) => {
    navigate(path);
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

        {/* Menú de navegación */}
        <div className="nav-menu">
          <div 
            className="nav-item active" 
            onClick={() => handleNavigate('/')}
          >
            Descubre rifas
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
                onClick={() => handleNavigate('/create-rifa')}
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
                onClick={() => handleNavigate('/profile')}
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
