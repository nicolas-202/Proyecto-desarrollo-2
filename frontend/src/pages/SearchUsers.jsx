import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../services/authService';

function SearchUsers() {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async e => {
    e.preventDefault();
    if (!searchTerm.trim()) return;

    try {
      setLoading(true);
      setSearched(true);
      const response = await apiClient.get(`/auth/list/?search=${searchTerm}`);
      setUsers(response.data);
    } catch (err) {
      console.error('Error al buscar usuarios:', err);
      setUsers([]);
    } finally {
      setLoading(false);
    }
  };

  const calculateAverageRating = user => {
    // Si el backend ya devuelve el rating calculado
    if (user.rating !== undefined && user.rating !== null) {
      return parseFloat(user.rating).toFixed(1);
    }

    // Si el backend devuelve las interacciones
    if (
      user.target_interactions &&
      Array.isArray(user.target_interactions) &&
      user.target_interactions.length > 0
    ) {
      const sum = user.target_interactions.reduce(
        (acc, int) => acc + (int.interaction_rating || 0),
        0
      );
      return (sum / user.target_interactions.length).toFixed(1);
    }

    return '0.0';
  };

  const getRatingStars = user => {
    const rating = calculateAverageRating(user);
    const numRating = Math.round(parseFloat(rating));
    return numRating > 0 ? '⭐'.repeat(numRating) : '☆☆☆☆☆';
  };

  return (
    <div className="module-container active">
      {/* Breadcrumb */}
      <div className="breadcrumbs">
        <div className="breadcrumb-item" onClick={() => navigate('/')}>
          Inicio
        </div>
        <div className="breadcrumb-separator">&gt;</div>
        <div className="breadcrumb-item">Buscar usuarios</div>
      </div>

      {/* Título y descripción */}
      <div className="guidance-text highlight">
        <strong>🔍 Busca usuarios en la comunidad</strong> Encuentra otros usuarios por su nombre o
        correo electrónico para ver sus perfiles y calificaciones.
      </div>

      {/* Buscador */}
      <div className="filters">
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '1rem', width: '100%' }}>
          <input
            type="text"
            className="search-input"
            placeholder="Busca por nombre o correo electrónico..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            style={{ flex: 1 }}
          />
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Buscando...' : '🔍 Buscar'}
          </button>
        </form>
      </div>

      {/* Resultados */}
      {loading && (
        <div style={{ textAlign: 'center', padding: '4rem', color: 'white' }}>
          <p>Buscando usuarios...</p>
        </div>
      )}

      {!loading && searched && users.length === 0 && (
        <div className="form-container">
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔍</div>
            <h3 style={{ marginBottom: '0.5rem' }}>No se encontraron usuarios</h3>
            <p style={{ color: '#666' }}>Intenta con otro término de búsqueda</p>
          </div>
        </div>
      )}

      {!loading && users.length > 0 && (
        <div className="rifa-grid">
          {users.map(user => (
            <div key={user.id} className="user-card" onClick={() => navigate(`/user/${user.id}`)}>
              <div
                className="rifa-image"
                style={{ background: 'linear-gradient(135deg, #6A4C93 0%, #5B2C6F 100%)' }}
              >
                <div
                  style={{
                    fontSize: '4rem',
                    color: 'white',
                    fontWeight: 'bold',
                  }}
                >
                  {user.first_name?.[0]}
                  {user.last_name?.[0]}
                </div>
              </div>
              <div className="rifa-content">
                <div className="rifa-title" style={{ color: '#2C3E50', fontSize: '1.3rem' }}>
                  {user.full_name || `${user.first_name} ${user.last_name}`}
                </div>
                <p style={{ color: '#666', fontSize: '0.9rem', marginTop: '0.5rem' }}>
                  📧 {user.email}
                </p>
                {user.phone_number && (
                  <p style={{ color: '#666', fontSize: '0.9rem' }}>📱 {user.phone_number}</p>
                )}
                <div
                  style={{
                    marginTop: '1rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                  }}
                >
                  <div className="rating">{getRatingStars(user)}</div>
                  <span style={{ color: '#666', fontSize: '0.9rem' }}>
                    {calculateAverageRating(user)}
                  </span>
                </div>
                <button
                  className="btn-primary"
                  style={{ width: '100%', marginTop: '1rem' }}
                  onClick={e => {
                    e.stopPropagation();
                    navigate(`/user/${user.id}`);
                  }}
                >
                  Ver perfil
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {!searched && (
        <div className="form-container">
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>👥</div>
            <h3 style={{ marginBottom: '0.5rem' }}>Comienza a buscar</h3>
            <p style={{ color: '#666' }}>
              Escribe el nombre o correo de un usuario en el buscador para encontrarlo
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default SearchUsers;
