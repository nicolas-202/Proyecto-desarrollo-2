import { useNavigate } from 'react-router-dom';

function Header() {
  const navigate = useNavigate();
  // TODO: Aquí irá el estado de autenticación cuando lo implementemos
  const isAuthenticated = false;
  const isAdmin = false;

  const handleNavigate = (path) => {
    navigate(path);
  };

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

          {/* Mostrar solo si está autenticado */}
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

          {/* Botones de autenticación */}
          {!isAuthenticated ? (
            <div id="nav-auth">
              <button 
                className="btn-primary" 
                onClick={() => handleNavigate('/auth')}
              >
                Entrar
              </button>
            </div>
          ) : (
            <div id="nav-user">
              <div 
                className="nav-item" 
                onClick={() => handleNavigate('/profile')}
              >
                Mi perfil
              </div>
              <button 
                className="btn-secondary" 
                onClick={() => {/* TODO: logout */}}
              >
                Salir
              </button>
            </div>
          )}

          {/* Configuración (solo admin) */}
          {isAdmin && (
            <div 
              className="nav-item" 
              onClick={() => handleNavigate('/config')}
            >
              ⚙️ Configuración
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Header;
