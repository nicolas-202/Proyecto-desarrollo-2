import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { apiClient } from '../services/authService';

function EditRaffle() {
  const { raffleId } = useParams();
  const navigate = useNavigate();
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();

  const [formData, setFormData] = useState({
    raffle_name: '',
    raffle_description: '',
    raffle_prize_amount: '',
    raffle_ticket_value: '',
    raffle_tickets_quantity: '',
    raffle_minimum_numbers_sold: '',
    raffle_date: '',
    raffle_prize_type: '',
    raffle_image: null
  });

  const [currentImage, setCurrentImage] = useState(null);
  const [prizeTypes, setPrizeTypes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingData, setLoadingData] = useState(true);
  const [message, setMessage] = useState({ text: '', type: '', show: false });
  const [raffle, setRaffle] = useState(null);

  // Verificar autenticación
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate('/auth', { replace: true });
    }
  }, [authLoading, isAuthenticated, navigate]);

  // Cargar datos de la rifa y tipos de premio
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoadingData(true);
        
        const [raffleResponse, prizeTypesResponse] = await Promise.all([
          apiClient.get(`/raffle/${raffleId}/`),
          apiClient.get('/raffle-info/prizetype/')
        ]);

        const raffleData = raffleResponse.data;
        setRaffle(raffleData);

        // Verificar permisos
        const isCreator = user?.id === raffleData.raffle_created_by?.id;
        const isAdmin = user?.is_staff || user?.is_admin;
        
        if (!isCreator && !isAdmin) {
          showMessage('No tienes permisos para editar esta rifa', 'error');
          setTimeout(() => navigate(`/raffle/${raffleId}`), 2000);
          return;
        }

        // Verificar que esté activa
        if (raffleData.raffle_state?.state_raffle_name !== 'Activa') {
          showMessage('Solo puedes editar rifas activas', 'error');
          setTimeout(() => navigate(`/raffle/${raffleId}`), 2000);
          return;
        }

        // Cargar datos en el formulario
        setFormData({
          raffle_name: raffleData.raffle_name || '',
          raffle_description: raffleData.raffle_description || '',
          raffle_prize_amount: raffleData.raffle_prize_amount || '',
          raffle_ticket_value: raffleData.raffle_ticket_value || '',
          raffle_tickets_quantity: raffleData.raffle_tickets_quantity || '',
          raffle_minimum_numbers_sold: raffleData.raffle_minimum_numbers_sold || '',
          raffle_date: raffleData.raffle_date ? raffleData.raffle_date.slice(0, 16) : '',
          raffle_prize_type: raffleData.raffle_prize_type?.id || '',
          raffle_image: null
        });

        setCurrentImage(raffleData.raffle_image);

        const types = prizeTypesResponse.data.results || prizeTypesResponse.data || [];
        setPrizeTypes(types);

      } catch (error) {
        console.error('Error cargando datos:', error);
        showMessage('Error al cargar la información de la rifa', 'error');
        setTimeout(() => navigate('/'), 2000);
      } finally {
        setLoadingData(false);
      }
    };

    if (isAuthenticated && user?.id && raffleId) {
      fetchData();
    }
  }, [isAuthenticated, user, raffleId]);

  const showMessage = (text, type) => {
    setMessage({ text, type, show: true });
    setTimeout(() => {
      setMessage({ text: '', type: '', show: false });
    }, 4000);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        showMessage('Por favor selecciona una imagen válida', 'error');
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        showMessage('La imagen no puede pesar más de 5MB', 'error');
        return;
      }
      setFormData(prev => ({
        ...prev,
        raffle_image: file
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validaciones
    if (!formData.raffle_name || !formData.raffle_description) {
      showMessage('El nombre y descripción son obligatorios 📝', 'error');
      return;
    }

    if (formData.raffle_date) {
      const drawDate = new Date(formData.raffle_date);
      const now = new Date();
      if (drawDate <= now) {
        showMessage('La fecha del sorteo debe ser en el futuro 📅', 'error');
        return;
      }
    }

    setLoading(true);

    try {
      // El backend solo acepta multipart/form-data, siempre usar FormData
      const requestData = new FormData();
      
      // Agregar campos básicos
      requestData.append('raffle_name', formData.raffle_name);
      requestData.append('raffle_description', formData.raffle_description);
      
      // Agregar fecha si existe (el backend espera raffle_draw_date, no raffle_date)
      if (formData.raffle_date) {
        requestData.append('raffle_draw_date', formData.raffle_date);
      }
      
      // Agregar imagen solo si hay una nueva
      if (formData.raffle_image) {
        requestData.append('raffle_image', formData.raffle_image);
      }

      // Importante: eliminar el Content-Type por defecto para que axios lo configure automáticamente
      await apiClient.patch(`/raffle/${raffleId}/update/`, requestData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      showMessage('¡Rifa actualizada con éxito! 🎉 Redirigiendo...', 'success');
      
      setTimeout(() => {
        navigate(`/raffle/${raffleId}`);
      }, 1500);

    } catch (error) {
      console.error('Error al actualizar rifa:', error);
      console.error('Respuesta del servidor:', error.response?.data);
      
      let errorMessage = 'Error al actualizar la rifa';
      if (error.response?.data) {
        // Mostrar el error completo del backend para debugging
        console.log('Detalles del error:', JSON.stringify(error.response.data, null, 2));
        
        if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        } else if (error.response.data.error) {
          errorMessage = error.response.data.error;
        } else if (error.response.data.detail) {
          errorMessage = error.response.data.detail;
        } else if (error.response.data.raffle_draw_date) {
          // Error específico de la fecha
          errorMessage = Array.isArray(error.response.data.raffle_draw_date) 
            ? error.response.data.raffle_draw_date[0] 
            : error.response.data.raffle_draw_date;
        } else if (error.response.data.raffle_name) {
          errorMessage = Array.isArray(error.response.data.raffle_name)
            ? error.response.data.raffle_name[0]
            : error.response.data.raffle_name;
        } else if (error.response.data.raffle_description) {
          errorMessage = Array.isArray(error.response.data.raffle_description)
            ? error.response.data.raffle_description[0]
            : error.response.data.raffle_description;
        } else if (error.response.data.non_field_errors) {
          errorMessage = Array.isArray(error.response.data.non_field_errors)
            ? error.response.data.non_field_errors[0]
            : error.response.data.non_field_errors;
        } else {
          // Mostrar el primer error que encuentre
          const firstError = Object.values(error.response.data)[0];
          errorMessage = Array.isArray(firstError) ? firstError[0] : firstError;
        }
      }
      
      showMessage(errorMessage, 'error');
    } finally {
      setLoading(false);
    }
  };

  if (authLoading || loadingData) {
    return (
      <div className="module-container active">
        <div style={{ textAlign: 'center', color: 'white', fontSize: '1.2rem', marginTop: '3rem' }}>
          Cargando información... 🎰
        </div>
      </div>
    );
  }

  if (!raffle) {
    return (
      <div className="module-container active">
        <div className="message error show">
          No se pudo cargar la rifa
        </div>
        <button className="btn-secondary" onClick={() => navigate('/')}>
          ← Volver al inicio
        </button>
      </div>
    );
  }

  return (
    <div className="module-container active">
      <div className="breadcrumbs">
        <div className="breadcrumb-item" onClick={() => navigate('/')}>Inicio</div>
        <div className="breadcrumb-separator">&gt;</div>
        <div className="breadcrumb-item" onClick={() => navigate(`/raffle/${raffleId}`)}>
          {raffle.raffle_name}
        </div>
        <div className="breadcrumb-separator">&gt;</div>
        <div className="breadcrumb-item">Editar</div>
      </div>

      <div className="form-container">
        <h2>Editar Rifa</h2>
        <div className="guidance-text">
          Actualiza la información de tu rifa. Solo puedes editar rifas activas.
        </div>

        {message.show && (
          <div className={`message ${message.type} show`}>
            {message.text}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Nombre de la rifa *</label>
            <input
              type="text"
              name="raffle_name"
              className="form-input"
              value={formData.raffle_name}
              onChange={handleInputChange}
              placeholder="Ej: iPhone 15 Pro"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Descripción *</label>
            <textarea
              name="raffle_description"
              className="form-input"
              rows="4"
              value={formData.raffle_description}
              onChange={handleInputChange}
              placeholder="Describe tu premio..."
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">¿Cuándo será el sorteo?</label>
            <input
              type="datetime-local"
              name="raffle_date"
              className="form-input"
              value={formData.raffle_date}
              onChange={handleInputChange}
            />
            <small style={{ color: '#666', fontSize: '0.85rem' }}>
              El sorteo debe ser en una fecha futura. Las ventas se cerrarán en esta fecha.
            </small>
          </div>

          <div className="form-group">
            <label className="form-label">Imagen actual</label>
            {currentImage && (
              <div style={{ marginBottom: '1rem' }}>
                <img 
                  src={currentImage} 
                  alt="Imagen actual" 
                  style={{ 
                    maxWidth: '200px', 
                    borderRadius: '8px',
                    border: '2px solid #ddd'
                  }} 
                />
              </div>
            )}
            <label className="form-label">Cambiar imagen (opcional)</label>
            <input
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              className="form-input"
              style={{ padding: '0.5rem' }}
            />
            <small style={{ color: '#666', fontSize: '0.85rem' }}>
              Máximo 5MB. Formato: JPG, PNG, GIF
            </small>
          </div>

          <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
            <button
              type="button"
              className="btn-secondary"
              onClick={() => navigate(`/raffle/${raffleId}`)}
              style={{ flex: 1 }}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={loading}
              style={{ flex: 1 }}
            >
              {loading ? 'Guardando...' : 'Guardar cambios'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default EditRaffle;
