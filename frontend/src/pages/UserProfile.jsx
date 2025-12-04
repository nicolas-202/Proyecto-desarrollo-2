import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { apiClient } from '../services/authService';

const UserProfile = () => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();
  
  const [user, setUser] = useState(null);
  const [interactions, setInteractions] = useState([]);
  const [raffles, setRaffles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('rifas');
  const [showRatingModal, setShowRatingModal] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [hasRated, setHasRated] = useState(false);
  const [existingRatingId, setExistingRatingId] = useState(null);
  
  // Estados para edición de perfil
  const [editForm, setEditForm] = useState({
    first_name: '',
    last_name: '',
    phone_number: '',
    address: '',
    city: '',
    gender: ''
  });
  
  // Estados para nueva calificación
  const [ratingForm, setRatingForm] = useState({
    rating: 5,
    comment: ''
  });
  
  // Estados para ubicación
  const [countries, setCountries] = useState([]);
  const [states, setStates] = useState([]);
  const [cities, setCities] = useState([]);
  const [genders, setGenders] = useState([]);
  const [selectedCountry, setSelectedCountry] = useState('');
  const [selectedState, setSelectedState] = useState('');
  
  const isOwnProfile = currentUser && currentUser.id === parseInt(userId);

  useEffect(() => {
    fetchUserData();
    fetchInteractions();
    fetchUserRaffles();
    if (isOwnProfile) {
      fetchLocationData();
    }
  }, [userId]);

  const fetchUserData = async () => {
    try {
      setLoading(true);
      let response;
      if (isOwnProfile) {
        response = await apiClient.get('/auth/me/');
      } else {
        response = await apiClient.get(`/auth/list/`);
        const userData = response.data.find(u => u.id === parseInt(userId));
        if (!userData) throw new Error('Usuario no encontrado');
        response = { data: userData };
      }
      
      setUser(response.data);
      
      if (isOwnProfile) {
        setEditForm({
          first_name: response.data.first_name || '',
          last_name: response.data.last_name || '',
          phone_number: response.data.phone_number || '',
          address: response.data.address || '',
          city: response.data.city?.id || '',
          gender: response.data.gender?.id || ''
        });
        
        if (response.data.city?.state?.id) {
          setSelectedState(response.data.city.state.id);
          fetchCities(response.data.city.state.id);
        }
        if (response.data.city?.state?.country?.id) {
          setSelectedCountry(response.data.city.state.country.id);
          fetchStates(response.data.city.state.country.id);
        }
      }
    } catch (err) {
      console.error('Error al cargar usuario:', err);
      setError('No se pudo cargar la información del usuario');
    } finally {
      setLoading(false);
    }
  };

  const fetchInteractions = async () => {
    try {
      const response = await apiClient.get(`/interactions/?target_user=${userId}`);
      setInteractions(response.data);
      
      // Verificar si el usuario actual ya ha calificado a este usuario
      if (currentUser && !isOwnProfile) {
        // El backend puede devolver el source_user como ID (número) o como objeto
        const userRating = response.data.find(int => {
          const sourceUserId = typeof int.interaction_source_user === 'object' 
            ? int.interaction_source_user?.id 
            : int.interaction_source_user;
          return sourceUserId === currentUser.id;
        });
        
        if (userRating) {
          setHasRated(true);
          setExistingRatingId(userRating.id);
          // Cargar la calificación existente en el formulario
          setRatingForm({
            rating: userRating.interaction_rating,
            comment: userRating.interaction_comment || ''
          });
        } else {
          setHasRated(false);
          setExistingRatingId(null);
          // Resetear formulario a valores por defecto
          setRatingForm({
            rating: 5,
            comment: ''
          });
        }
      }
    } catch (err) {
      console.error('Error al cargar interacciones:', err);
    }
  };

  const fetchUserRaffles = async () => {
    try {
      // Si es el propio perfil, incluir rifas inactivas también
      const includeInactive = isOwnProfile ? '?include_inactive=true' : '';
      const response = await apiClient.get(`/raffle/user/${userId}/${includeInactive}`);
      console.log('Rifas recibidas del backend:', response.data);
      console.log('Cantidad de rifas:', response.data.length);
      setRaffles(response.data);
    } catch (err) {
      console.error('Error al cargar rifas:', err);
    }
  };

  const fetchLocationData = async () => {
    try {
      const [countriesRes, gendersRes] = await Promise.all([
        apiClient.get('/location/countries/'),
        apiClient.get('/user-info/genders/')
      ]);
      setCountries(countriesRes.data);
      setGenders(gendersRes.data);
    } catch (err) {
      console.error('Error al cargar datos de ubicación:', err);
    }
  };

  const fetchStates = async (countryId) => {
    try {
      const response = await apiClient.get(`/location/states/?country=${countryId}`);
      setStates(response.data);
    } catch (err) {
      console.error('Error al cargar estados:', err);
    }
  };

  const fetchCities = async (stateId) => {
    try {
      const response = await apiClient.get(`/location/cities/?state=${stateId}`);
      setCities(response.data);
    } catch (err) {
      console.error('Error al cargar ciudades:', err);
    }
  };

  const handleCountryChange = (e) => {
    const countryId = e.target.value;
    setSelectedCountry(countryId);
    setSelectedState('');
    setEditForm({ ...editForm, city: '' });
    setStates([]);
    setCities([]);
    if (countryId) {
      fetchStates(countryId);
    }
  };

  const handleStateChange = (e) => {
    const stateId = e.target.value;
    setSelectedState(stateId);
    setEditForm({ ...editForm, city: '' });
    setCities([]);
    if (stateId) {
      fetchCities(stateId);
    }
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await apiClient.put('/auth/update_me/', editForm);
      setUser(response.data);
      setIsEditing(false);
      alert('Perfil actualizado correctamente');
    } catch (err) {
      console.error('Error al actualizar perfil:', err);
      alert(err.response?.data?.message || 'Error al actualizar el perfil');
    }
  };

  const handleRatingSubmit = async (e) => {
    e.preventDefault();
    
    try {
      if (existingRatingId) {
        // Actualizar calificación existente usando PATCH
        await apiClient.patch(`/interactions/${existingRatingId}/`, {
          interaction_rating: ratingForm.rating,
          interaction_comment: ratingForm.comment || ''
        });
        alert('Calificación actualizada correctamente');
      } else {
        // Crear nueva calificación
        await apiClient.post('/interactions/', {
          interaction_target_user: parseInt(userId),
          interaction_rating: ratingForm.rating,
          interaction_comment: ratingForm.comment || ''
        });
        alert('Calificación enviada correctamente');
      }
      
      setShowRatingModal(false);
      setHasRated(true);
      await fetchInteractions();
      await fetchUserData();
    } catch (err) {
      console.error('Error al crear/actualizar calificación:', err);
      
      // Manejar diferentes tipos de errores
      let errorMessage = 'Error al enviar la calificación';
      
      if (err.response?.data) {
        if (typeof err.response.data === 'string') {
          errorMessage = err.response.data;
        } else if (err.response.data.detail) {
          errorMessage = err.response.data.detail;
        } else if (err.response.data.non_field_errors) {
          errorMessage = err.response.data.non_field_errors[0];
        } else if (err.response.data.interaction_target_user) {
          errorMessage = err.response.data.interaction_target_user[0];
        } else {
          errorMessage = JSON.stringify(err.response.data);
        }
      }
      
      alert(errorMessage);
    }
  };

  const handleDeleteRating = async () => {
    if (!existingRatingId) return;
    
    const confirmDelete = window.confirm('¿Estás seguro de que deseas eliminar tu calificación? Esta acción no se puede deshacer.');
    if (!confirmDelete) return;
    
    try {
      await apiClient.delete(`/interactions/${existingRatingId}/`);
      alert('Calificación eliminada correctamente');
      
      setShowRatingModal(false);
      setHasRated(false);
      setExistingRatingId(null);
      setRatingForm({ rating: 5, comment: '' });
      
      await fetchInteractions();
      await fetchUserData();
    } catch (err) {
      console.error('Error al eliminar calificación:', err);
      alert(err.response?.data?.detail || 'Error al eliminar la calificación');
    }
  };

  const calculateAverageRating = () => {
    if (interactions.length === 0) return 0;
    const sum = interactions.reduce((acc, int) => acc + int.interaction_rating, 0);
    return (sum / interactions.length).toFixed(1);
  };

  if (loading) {
    return (
      <div className="module-container active">
        <div style={{ textAlign: 'center', padding: '4rem', color: 'white' }}>
          <p>Cargando perfil...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="module-container active">
        <div className="form-container">
          <h2 style={{ textAlign: 'center', color: '#e74c3c' }}>⚠️ {error}</h2>
          <button onClick={() => navigate(-1)} className="btn-secondary" style={{ width: '100%', marginTop: '1rem' }}>
            Volver
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="module-container active">
      {/* Breadcrumb */}
      <div className="breadcrumbs">
        <div className="breadcrumb-item" onClick={() => navigate('/')}>Inicio</div>
        <div className="breadcrumb-separator">&gt;</div>
        <div className="breadcrumb-item">Perfil</div>
      </div>

      {/* Cabecera de perfil */}
      <div className="profile-header">
        <div className="profile-avatar">
          {user?.first_name?.[0]}{user?.last_name?.[0]}
        </div>
        <div className="profile-info">
          <h2>{user?.full_name || `${user?.first_name} ${user?.last_name}`}</h2>
          <p style={{ color: '#666', marginBottom: '0.5rem' }}>{user?.email}</p>
          <div className="rating">
            {'⭐'.repeat(Math.round(calculateAverageRating()))}
            {' '}
            <span style={{ color: '#666' }}>
              {calculateAverageRating()} ({interactions.length} {interactions.length === 1 ? 'calificación' : 'calificaciones'})
            </span>
          </div>
          {user?.phone_number && (
            <p style={{ color: '#666', marginTop: '0.5rem' }}>📱 {user.phone_number}</p>
          )}
          {user?.city && (
            <p style={{ color: '#666' }}>📍 {user.city.city_name}, {user.city.state?.state_name}</p>
          )}
        </div>
        <div style={{ marginLeft: 'auto' }}>
          {!isOwnProfile && currentUser && (
            <button 
              className="btn-primary"
              onClick={() => setShowRatingModal(true)}
            >
              {hasRated ? '✏️ Editar calificación' : '⭐ Calificar usuario'}
            </button>
          )}
          {isOwnProfile && !isEditing && (
            <button 
              className="btn-secondary"
              onClick={() => {
                setIsEditing(true);
                setActiveTab('edit');
              }}
            >
              ✏️ Editar perfil
            </button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <div 
          className={`tab ${activeTab === 'rifas' ? 'active' : ''}`}
          onClick={() => setActiveTab('rifas')}
        >
          Rifas
        </div>
        <div 
          className={`tab ${activeTab === 'comments' ? 'active' : ''}`}
          onClick={() => setActiveTab('comments')}
        >
          Opiniones
        </div>
        {isOwnProfile && (
          <div 
            className={`tab ${activeTab === 'edit' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('edit');
              setIsEditing(true);
            }}
          >
            Editar perfil
          </div>
        )}
      </div>

      {/* Tab Content: Rifas */}
      {activeTab === 'rifas' && (
        <div className="tab-content active">
          <div className="guidance-text" style={{ color: 'white' }}>
            Aquí puedes ver todas las rifas que el usuario ha creado y su estado actual.
          </div>
          <div className="rifa-grid">
            {raffles.length === 0 ? (
              <div style={{ color: 'white', textAlign: 'center', gridColumn: '1 / -1' }}>
                {isOwnProfile 
                  ? 'Aún no has creado ninguna rifa' 
                  : 'Este usuario aún no ha creado rifas'
                }
              </div>
            ) : (
              raffles.map((raffle) => (
                <div 
                  key={raffle.id} 
                  className="rifa-card"
                  onClick={() => navigate(`/raffle/${raffle.id}`)}
                  style={{ cursor: 'pointer' }}
                >
                  <div className="rifa-image">
                    {raffle.raffle_image ? (
                      <img 
                        src={raffle.raffle_image} 
                        alt={raffle.raffle_name}
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                      />
                    ) : (
                      <div style={{ 
                        width: '100%', 
                        height: '100%', 
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '3rem'
                      }}>
                        🎟️
                      </div>
                    )}
                  </div>
                  <div className="rifa-details">
                    <h3>{raffle.raffle_name}</h3>
                    <p className="rifa-description">
                      {raffle.raffle_description?.length > 100 
                        ? `${raffle.raffle_description.substring(0, 100)}...` 
                        : raffle.raffle_description
                      }
                    </p>
                    <div className="rifa-info">
                      <div className="info-item">
                        <span className="label">💰 Precio:</span>
                        <span className="value">${parseFloat(raffle.raffle_number_price).toLocaleString()}</span>
                      </div>
                      <div className="info-item">
                        <span className="label">🎫 Números:</span>
                        <span className="value">{raffle.raffle_number_amount}</span>
                      </div>
                      <div className="info-item">
                        <span className="label">📅 Sorteo:</span>
                        <span className="value">
                          {new Date(raffle.raffle_draw_date).toLocaleDateString('es-ES', {
                            day: '2-digit',
                            month: 'short',
                            year: 'numeric'
                          })}
                        </span>
                      </div>
                      <div className="info-item">
                        <span className="label">🏆 Estado:</span>
                        <span className={`status-badge status-${raffle.raffle_state?.state_raffle_name?.toLowerCase()}`}>
                          {raffle.raffle_state?.state_raffle_name}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Tab Content: Comentarios */}
      {activeTab === 'comments' && (
        <div className="tab-content active">
          <div className="guidance-text" style={{ color: 'white' }}>
            Estas son las opiniones que otros usuarios han dejado.
          </div>
          <div className="comments-section">
            {interactions.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
                <p>⭐ Sin calificaciones aún</p>
                <p style={{ fontSize: '0.9rem', marginTop: '0.5rem' }}>
                  {isOwnProfile 
                    ? 'Aún no has recibido calificaciones de otros usuarios.'
                    : 'Este usuario aún no ha recibido calificaciones.'
                  }
                </p>
              </div>
            ) : (
              interactions.map((interaction) => (
                <div key={interaction.id} className="comment-item">
                  <div className="comment-header">
                    <div>
                      <strong>{interaction.interaction_source_user?.first_name} {interaction.interaction_source_user?.last_name}</strong>
                      <p style={{ color: '#666', fontSize: '0.9rem', marginTop: '0.25rem' }}>
                        {new Date(interaction.interaction_created_at).toLocaleDateString('es-ES', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </p>
                    </div>
                    <div className="rating">
                      {'⭐'.repeat(Math.floor(interaction.interaction_rating))}
                      <span style={{ marginLeft: '0.5rem', color: '#666' }}>
                        {interaction.interaction_rating}
                      </span>
                    </div>
                  </div>
                  {interaction.interaction_comment && (
                    <p style={{ marginTop: '0.5rem', color: '#555' }}>
                      "{interaction.interaction_comment}"
                    </p>
                  )}
                </div>
              ))
            )}
          </div>

          {!isOwnProfile && currentUser && (
            <div className="form-container">
              <h3>{hasRated ? 'Edita tu calificación' : '¿Qué te pareció este usuario?'}</h3>
              <div className="guidance-text">
                {hasRated 
                  ? 'Puedes modificar tu calificación y comentario en cualquier momento.'
                  : 'Comparte tu experiencia para ayudar a otros usuarios.'
                }
              </div>
              <form onSubmit={handleRatingSubmit}>
                <div className="form-group">
                  <label className="form-label">¿Cómo calificarías a este usuario?</label>
                  <select 
                    className="form-input"
                    value={ratingForm.rating}
                    onChange={(e) => setRatingForm({...ratingForm, rating: parseInt(e.target.value)})}
                  >
                    <option value="5">⭐⭐⭐⭐⭐ Excelente (5 estrellas)</option>
                    <option value="4">⭐⭐⭐⭐ Muy bueno (4 estrellas)</option>
                    <option value="3">⭐⭐⭐ Bueno (3 estrellas)</option>
                    <option value="2">⭐⭐ Regular (2 estrellas)</option>
                    <option value="1">⭐ Malo (1 estrella)</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Tu opinión</label>
                  <textarea 
                    className="form-input" 
                    rows="4"
                    value={ratingForm.comment}
                    onChange={(e) => setRatingForm({...ratingForm, comment: e.target.value})}
                    placeholder="Comparte tu experiencia con este usuario..."
                    maxLength="500"
                  />
                  <small style={{ color: '#666' }}>{ratingForm.comment.length}/500 caracteres</small>
                </div>
                <button type="submit" className="btn-primary">
                  {hasRated ? 'Actualizar calificación' : 'Publicar mi opinión'}
                </button>
                {hasRated && (
                  <button 
                    type="button" 
                    onClick={handleDeleteRating}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      background: '#e74c3c',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      fontSize: '1rem',
                      fontWeight: '600',
                      cursor: 'pointer',
                      marginTop: '0.5rem'
                    }}
                    onMouseOver={(e) => e.target.style.background = '#c0392b'}
                    onMouseOut={(e) => e.target.style.background = '#e74c3c'}
                  >
                    🗑️ Eliminar calificación
                  </button>
                )}
              </form>
            </div>
          )}
        </div>
      )}

      {/* Tab Content: Editar Perfil */}
      {activeTab === 'edit' && isOwnProfile && isEditing && (
        <div className="tab-content active">
          <div className="form-container" style={{ maxWidth: '700px' }}>
            <h3>Actualiza tu información</h3>
            <div className="guidance-text">
              Mantén tus datos actualizados para que podamos contactarte si ganas una rifa.
            </div>
            <form onSubmit={handleEditSubmit}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label className="form-label">Tu nombre</label>
                  <input
                    type="text"
                    className="form-input"
                    value={editForm.first_name}
                    onChange={(e) => setEditForm({...editForm, first_name: e.target.value})}
                    placeholder="Cómo te llamas"
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Tu apellido</label>
                  <input
                    type="text"
                    className="form-input"
                    value={editForm.last_name}
                    onChange={(e) => setEditForm({...editForm, last_name: e.target.value})}
                    placeholder="Tu apellido"
                    required
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label className="form-label">Tu teléfono</label>
                  <input
                    type="tel"
                    className="form-input"
                    value={editForm.phone_number}
                    onChange={(e) => setEditForm({...editForm, phone_number: e.target.value})}
                    placeholder="Para contactarte si ganas"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Género</label>
                  <select
                    className="form-input"
                    value={editForm.gender}
                    onChange={(e) => setEditForm({...editForm, gender: e.target.value})}
                    required
                  >
                    <option value="">Seleccione...</option>
                    {genders.map(gender => (
                      <option key={gender.id} value={gender.id}>
                        {gender.gender_name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Tu dirección</label>
                <input
                  type="text"
                  className="form-input"
                  value={editForm.address}
                  onChange={(e) => setEditForm({...editForm, address: e.target.value})}
                  placeholder="Para enviarte premios físicos"
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label className="form-label">País</label>
                  <select
                    className="form-input"
                    value={selectedCountry}
                    onChange={handleCountryChange}
                    required
                  >
                    <option value="">Seleccione...</option>
                    {countries.map(country => (
                      <option key={country.id} value={country.id}>
                        {country.country_name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Departamento</label>
                  <select
                    className="form-input"
                    value={selectedState}
                    onChange={handleStateChange}
                    required
                    disabled={!selectedCountry}
                  >
                    <option value="">Seleccione...</option>
                    {states.map(state => (
                      <option key={state.id} value={state.id}>
                        {state.state_name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Ciudad</label>
                  <select
                    className="form-input"
                    value={editForm.city}
                    onChange={(e) => setEditForm({...editForm, city: e.target.value})}
                    required
                    disabled={!selectedState}
                  >
                    <option value="">Seleccione...</option>
                    {cities.map(city => (
                      <option key={city.id} value={city.id}>
                        {city.city_name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                <button 
                  type="button" 
                  className="btn-secondary" 
                  onClick={() => {
                    setIsEditing(false);
                    setActiveTab('rifas');
                  }}
                  style={{ flex: 1 }}
                >
                  Cancelar
                </button>
                <button type="submit" className="btn-primary" style={{ flex: 1 }}>
                  Guardar cambios
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal para calificar (si se muestra desde el botón) */}
      {showRatingModal && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999
          }}
          onClick={() => setShowRatingModal(false)}
        >
          <div 
            className="form-container"
            onClick={(e) => e.stopPropagation()}
            style={{ margin: 0, maxWidth: '500px' }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3>{hasRated ? 'Editar calificación' : `Calificar a ${user?.first_name}`}</h3>
              <button 
                onClick={() => setShowRatingModal(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '1.5rem',
                  cursor: 'pointer',
                  color: '#666'
                }}
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleRatingSubmit}>
              <div className="form-group">
                <label className="form-label">Calificación</label>
                <select 
                  className="form-input"
                  value={ratingForm.rating}
                  onChange={(e) => setRatingForm({...ratingForm, rating: parseInt(e.target.value)})}
                >
                  <option value="5">⭐⭐⭐⭐⭐ Excelente (5 estrellas)</option>
                  <option value="4">⭐⭐⭐⭐ Muy bueno (4 estrellas)</option>
                  <option value="3">⭐⭐⭐ Bueno (3 estrellas)</option>
                  <option value="2">⭐⭐ Regular (2 estrellas)</option>
                  <option value="1">⭐ Malo (1 estrella)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Comentario (opcional)</label>
                <textarea
                  className="form-input"
                  rows="4"
                  value={ratingForm.comment}
                  onChange={(e) => setRatingForm({...ratingForm, comment: e.target.value})}
                  placeholder="Comparte tu experiencia..."
                  maxLength="500"
                />
                <small style={{ color: '#666' }}>{ratingForm.comment.length}/500 caracteres</small>
              </div>

              <div style={{ display: 'flex', gap: '1rem' }}>
                <button 
                  type="button" 
                  className="btn-secondary"
                  onClick={() => setShowRatingModal(false)}
                  style={{ flex: 1 }}
                >
                  Cancelar
                </button>
                <button type="submit" className="btn-primary" style={{ flex: 1 }}>
                  {hasRated ? 'Actualizar Calificación' : 'Enviar Calificación'}
                </button>
              </div>
              
              {hasRated && (
                <button 
                  type="button" 
                  onClick={handleDeleteRating}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    background: '#e74c3c',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '1rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    marginTop: '1rem'
                  }}
                  onMouseOver={(e) => e.target.style.background = '#c0392b'}
                  onMouseOut={(e) => e.target.style.background = '#e74c3c'}
                >
                  🗑️ Eliminar calificación
                </button>
              )}
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserProfile;
