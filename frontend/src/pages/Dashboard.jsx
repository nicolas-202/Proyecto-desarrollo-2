import React, { useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

const Dashboard = () => {
  const { user, getUserProfile, isAdmin } = useAuth();

  useEffect(() => {
    // Actualizar perfil del usuario al cargar el dashboard
    const loadUserProfile = async () => {
      try {
        await getUserProfile();
      } catch (error) {
        console.error('Error cargando perfil:', error);
      }
    };

    if (!user?.full_name) {
      loadUserProfile();
    }
  }, [user, getUserProfile]);

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div className="welcome-section">
          <h1>¡Bienvenido, {user?.first_name || 'Usuario'}!</h1>
          <p className="welcome-message">
            Estás en tu panel de control. Desde aquí puedes gestionar tus rifas y participaciones.
          </p>
        </div>

        {isAdmin() && (
          <div className="admin-badge">
            <span className="badge badge-admin">👑 Administrador</span>
          </div>
        )}
      </div>

      <div className="dashboard-content">
        <div className="dashboard-stats">
          <div className="stat-card">
            <div className="stat-icon">🎯</div>
            <div className="stat-info">
              <h3>Rifas Activas</h3>
              <p className="stat-number">0</p>
              <p className="stat-description">Rifas disponibles para participar</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">🎲</div>
            <div className="stat-info">
              <h3>Mis Participaciones</h3>
              <p className="stat-number">0</p>
              <p className="stat-description">Números que has comprado</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">🏆</div>
            <div className="stat-info">
              <h3>Rifas Ganadas</h3>
              <p className="stat-number">0</p>
              <p className="stat-description">Premios obtenidos</p>
            </div>
          </div>

          {isAdmin() && (
            <div className="stat-card">
              <div className="stat-icon">⚙️</div>
              <div className="stat-info">
                <h3>Mis Rifas</h3>
                <p className="stat-number">0</p>
                <p className="stat-description">Rifas que has creado</p>
              </div>
            </div>
          )}
        </div>

        <div className="dashboard-sections">
          <div className="section">
            <div className="section-header">
              <h2>Rifas Populares</h2>
              <a href="/rifas" className="section-link">
                Ver todas
              </a>
            </div>
            <div className="section-content">
              <div className="empty-state">
                <div className="empty-icon">🎯</div>
                <h3>No hay rifas disponibles</h3>
                <p>Mantente atento, pronto habrá nuevas rifas emocionantes.</p>
              </div>
            </div>
          </div>

          <div className="section">
            <div className="section-header">
              <h2>Mis Últimas Participaciones</h2>
              <a href="/mis-participaciones" className="section-link">
                Ver historial
              </a>
            </div>
            <div className="section-content">
              <div className="empty-state">
                <div className="empty-icon">🎲</div>
                <h3>No has participado en rifas</h3>
                <p>¡Empieza a participar y ten la oportunidad de ganar!</p>
                <button className="btn btn-primary">Ver Rifas Disponibles</button>
              </div>
            </div>
          </div>
        </div>

        {isAdmin() && (
          <div className="admin-section">
            <div className="section-header">
              <h2>Panel de Administrador</h2>
            </div>
            <div className="admin-actions">
              <button className="btn btn-success">
                <span className="btn-icon">➕</span>
                Crear Nueva Rifa
              </button>
              <button className="btn btn-info">
                <span className="btn-icon">📊</span>
                Ver Estadísticas
              </button>
              <button className="btn btn-secondary">
                <span className="btn-icon">👥</span>
                Gestionar Usuarios
              </button>
            </div>
          </div>
        )}

        <div className="user-profile-section">
          <div className="section-header">
            <h2>Mi Perfil</h2>
            <a href="/perfil" className="section-link">
              Editar perfil
            </a>
          </div>
          <div className="profile-info">
            <div className="profile-item">
              <span className="profile-label">Email:</span>
              <span className="profile-value">{user?.email}</span>
            </div>
            <div className="profile-item">
              <span className="profile-label">Nombre completo:</span>
              <span className="profile-value">
                {user?.first_name} {user?.last_name}
              </span>
            </div>
            <div className="profile-item">
              <span className="profile-label">Ciudad:</span>
              <span className="profile-value">{user?.city?.city_name || 'No especificada'}</span>
            </div>
            <div className="profile-item">
              <span className="profile-label">Teléfono:</span>
              <span className="profile-value">{user?.phone_number || 'No especificado'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
