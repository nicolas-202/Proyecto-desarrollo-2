import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { apiClient } from '../services/authService';

function CreateRaffle() {

  const navigate = useNavigate();
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();

  const [formData, setFormData] = useState({
    raffle_name: '',
    raffle_description: '',
    raffle_prize_amount: '',
    raffle_number_price: '',
    raffle_number_amount: 100, 
    raffle_minimum_numbers_sold: '', 
    raffle_draw_date: '',
    raffle_prize_type: '',
    raffle_creator_payment_method: '', 
    raffle_image: null 
  });

  // Estado para opciones de los selects (como formOptions en Auth.jsx)
  const [prizeTypes, setPrizeTypes] = useState([]);
  const [paymentMethods, setPaymentMethods] = useState([]); // NUEVO: Métodos de pago del usuario
  
  // Estados de UI (igual que en tus otras páginas)
  const [loading, setLoading] = useState(false);
  const [loadingData, setLoadingData] = useState(true);
  const [message, setMessage] = useState({ text: '', type: '', show: false });

  // ============================================
  // 3. VERIFICAR AUTENTICACIÓN
  // ============================================
  // Si no está autenticado, redirigir al login
  // Mismo patrón que en Auth.jsx (pero inverso)
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate('/auth', { replace: true });
    }
  }, [authLoading, isAuthenticated, navigate]);

  // ============================================
  // 4. CARGAR DATOS INICIALES
  // ============================================
  // Similar a como Auth.jsx carga países, géneros, etc.
  // Aquí cargamos los tipos de premio Y los métodos de pago del usuario
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        setLoadingData(true);
        
        // Cargar tipos de premio y métodos de pago en paralelo
        const [prizeTypesResponse, paymentMethodsResponse] = await Promise.all([
          apiClient.get('/raffle-info/prizetype/'),
          apiClient.get(`/user-info/payment-methods/`)
        ]);
        
        // Tipos de premio
        const types = prizeTypesResponse.data.results || prizeTypesResponse.data || [];
        setPrizeTypes(types);
        
        // Métodos de pago del usuario (NUEVO)
        // Tu API puede devolver array directo, {results: [...]} o un objeto único
        let methods = [];
        if (Array.isArray(paymentMethodsResponse.data)) {
          methods = paymentMethodsResponse.data;
        } else if (Array.isArray(paymentMethodsResponse.data.results)) {
          methods = paymentMethodsResponse.data.results;
        } else if (typeof paymentMethodsResponse.data === 'object' && paymentMethodsResponse.data !== null) {
          methods = [paymentMethodsResponse.data];
        }
        
        setPaymentMethods(methods);
        
        // Si solo tiene un método de pago, seleccionarlo automáticamente
        if (methods.length === 1) {
          setFormData(prev => ({
            ...prev,
            raffle_creator_payment_method: methods[0].id
          }));
        }
        
      } catch (error) {
        console.error('Error cargando datos iniciales:', error);
        showMessage('Error al cargar datos del formulario', 'error');
      } finally {
        setLoadingData(false);
      }
    };

    // Solo cargar datos si el usuario está autenticado
    if (isAuthenticated && user?.id) {
      fetchInitialData();
    }
  }, [isAuthenticated, user]);

  // ============================================
  // 5. FUNCIONES AUXILIARES
  // ============================================
  
  /**
   * Mostrar mensajes temporales
   * Mismo patrón que showMessage en Auth.jsx
   */
  const showMessage = (text, type) => {
    setMessage({ text, type, show: true });
    setTimeout(() => {
      setMessage({ text: '', type: '', show: false });
    }, 4000);
  };

  /**
   * Manejar cambios en inputs de texto/número/select
   * Similar a handleRegisterChange en Auth.jsx
   */
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  /**
   * Manejar cambio de archivo de imagen
   * Nuevo: No lo teníamos en otras páginas
   */
  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validar tipo de archivo
      if (!file.type.startsWith('image/')) {
        showMessage('Por favor selecciona una imagen válida', 'error');
        return;
      }
      // Validar tamaño (máximo 5MB)
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

  // ============================================
  // 6. MANEJAR ENVÍO DEL FORMULARIO
  // ============================================
  /**
   * Esta es la función más importante
   * Similar a handleRegister en Auth.jsx o handlePurchase en BuyNumbers.jsx
   */
  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevenir recarga de página
    
    // ========== VALIDACIONES FRONTEND ==========
    // Validar campos obligatorios
    if (!formData.raffle_name || !formData.raffle_description || 
        !formData.raffle_prize_amount || !formData.raffle_number_price ||
        !formData.raffle_number_amount || !formData.raffle_minimum_numbers_sold ||
        !formData.raffle_draw_date || !formData.raffle_prize_type ||
        !formData.raffle_creator_payment_method) {
      showMessage('Completa todos los campos obligatorios 📝', 'error');
      return;
    }

    // Validar que los números sean positivos
    if (formData.raffle_prize_amount <= 0 || formData.raffle_number_price <= 0 ||
        formData.raffle_number_amount <= 0 || formData.raffle_minimum_numbers_sold <= 0) {
      showMessage('Los montos y cantidades deben ser mayores a cero 💰', 'error');
      return;
    }

    // Validar que la fecha sea futura
    const drawDate = new Date(formData.raffle_draw_date);
    const now = new Date();
    if (drawDate <= now) {
      showMessage('La fecha del sorteo debe ser en el futuro 📅', 'error');
      return;
    }

    // Validar cantidad de números (mínimo 10, máximo 1000 según tu backend)
    if (formData.raffle_number_amount < 10 || formData.raffle_number_amount > 1000) {
      showMessage('La cantidad de números debe estar entre 10 y 1000 🎟️', 'error');
      return;
    }

    // NUEVO: Validar que el mínimo no sea mayor que el total
    if (parseInt(formData.raffle_minimum_numbers_sold) > parseInt(formData.raffle_number_amount)) {
      showMessage('El mínimo de números para sortear no puede ser mayor al total 📊', 'error');
      return;
    }

    // ========== PREPARAR DATOS ==========
    setLoading(true);

    try {
      // Siempre usar FormData para que sea consistente con el backend
      const requestData = new FormData();
      requestData.append('raffle_name', formData.raffle_name);
      requestData.append('raffle_description', formData.raffle_description);
      requestData.append('raffle_prize_amount', formData.raffle_prize_amount);
      requestData.append('raffle_number_price', formData.raffle_number_price);
      requestData.append('raffle_number_amount', formData.raffle_number_amount);
      requestData.append('raffle_minimum_numbers_sold', formData.raffle_minimum_numbers_sold);
      requestData.append('raffle_draw_date', formData.raffle_draw_date);
      requestData.append('raffle_prize_type', formData.raffle_prize_type);
      requestData.append('raffle_creator_payment_method', formData.raffle_creator_payment_method);
      
      // Solo agregar imagen si existe
      if (formData.raffle_image) {
        requestData.append('raffle_image', formData.raffle_image);
      }

      // ========== PETICIÓN AL BACKEND ==========
      // apiClient automáticamente agrega el token JWT (ver authService.js)
      // Para FormData, dejar que axios configure el Content-Type automáticamente
      const response = await apiClient.post('/raffle/create/', requestData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      // ========== ÉXITO ==========
      showMessage('¡Rifa creada con éxito! 🎉 Redirigiendo...', 'success');
      
      // Extraer el ID de la rifa creada
      // El backend devuelve { raffle_id, raffle_name, raffle_state, message }
      const raffleId = response.data.raffle_id || response.data.id;
      
      // Limpiar formulario
      setFormData({
        raffle_name: '',
        raffle_description: '',
        raffle_prize_amount: '',
        raffle_number_price: '',
        raffle_number_amount: 100,
        raffle_minimum_numbers_sold: '',
        raffle_draw_date: '',
        raffle_prize_type: '',
        raffle_creator_payment_method: '',
        raffle_image: null
      });

      // Redirigir a la página de detalle de la rifa creada
      setTimeout(() => {
        if (raffleId) {
          navigate(`/raffle/${raffleId}`);
        } else {
          // Si no hay ID, ir al home
          console.error('No se recibió ID de la rifa creada');
          navigate('/');
        }
      }, 1500);

    } catch (error) {
      // ========== MANEJO DE ERRORES ==========
      console.error('Error creando rifa:', error);
      
      // Extraer mensaje de error del backend
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message ||
                          error.response?.data?.error ||
                          'Error al crear la rifa. Intenta de nuevo.';
      
      showMessage(errorMessage, 'error');
    } finally {
      setLoading(false);
    }
  };

  // ============================================
  // 7. RENDERIZADO CONDICIONAL
  // ============================================
  // Mismo patrón que BuyNumbers.jsx
  
  // Mostrar loading mientras se verifica autenticación
  if (authLoading) {
    return (
      <div className="module-container active">
        <div style={{textAlign: 'center', color: 'white', fontSize: '1.2rem', marginTop: '3rem'}}>
          Verificando acceso... 🔐
        </div>
      </div>
    );
  }

  // Si no está autenticado, no mostrar nada (el useEffect lo redirige)
  if (!isAuthenticated) {
    return null;
  }

  // Mostrar loading mientras se cargan datos iniciales
  if (loadingData) {
    return (
      <div className="module-container active">
        <div style={{textAlign: 'center', color: 'white', fontSize: '1.2rem', marginTop: '3rem'}}>
          Cargando formulario... 📋
        </div>
      </div>
    );
  }

  // ============================================
  // 8. RENDERIZADO PRINCIPAL
  // ============================================
  return (
    <div className="module-container active">
      {/* ===== BREADCRUMBS ===== */}
      {/* Mismo patrón que todas tus páginas */}
      <div className="breadcrumbs">
        <div className="breadcrumb-item" onClick={() => navigate('/')}>Inicio</div>
        <div className="breadcrumb-separator">&gt;</div>
        <div className="breadcrumb-item">Lanzar rifa</div>
      </div>

      {/* ===== FORMULARIO ===== */}
      <div className="form-container" style={{maxWidth: '700px'}}>
        <h2 style={{textAlign: 'center', marginBottom: '2rem'}}>
          ¡Lanza tu propia rifa! 🚀
        </h2>
        
        {/* Texto de orientación - Como en Auth.jsx */}
        <div className="guidance-text">
          Completa la información de tu rifa para que otros usuarios puedan participar. 
          ¡Es fácil y divertido! Todos los campos marcados con * son obligatorios.
        </div>

        {/* ===== MENSAJE DE FEEDBACK ===== */}
        {/* Mismo patrón que Auth.jsx */}
        {message.show && (
          <div className={`message ${message.type} show`}>
            {message.text}
          </div>
        )}

        {/* ===== FORMULARIO ===== */}
        <form onSubmit={handleSubmit}>
          
          {/* Campo: Nombre de la rifa */}
          <div className="form-group">
            <label className="form-label">¿Qué rifa vas a lanzar? *</label>
            <input
              type="text"
              name="raffle_name"
              className="form-input"
              placeholder="Ej: iPhone 15 Pro Max"
              value={formData.raffle_name}
              onChange={handleInputChange}
              disabled={loading}
              required
            />
          </div>

          {/* Campo: Descripción */}
          <div className="form-group">
            <label className="form-label">Describe tu rifa *</label>
            <textarea
              name="raffle_description"
              className="form-input"
              rows="4"
              placeholder="Cuéntanos más detalles sobre el premio y cómo funciona tu rifa..."
              value={formData.raffle_description}
              onChange={handleInputChange}
              disabled={loading}
              required
            />
          </div>

          {/* Campos en grid - dos columnas */}
          <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem'}}>
            
            {/* Campo: Tipo de premio */}
            <div className="form-group">
              <label className="form-label">Tipo de premio *</label>
              <select
                name="raffle_prize_type"
                className="form-input"
                value={formData.raffle_prize_type}
                onChange={handleInputChange}
                disabled={loading}
                required
              >
                <option value="">Selecciona...</option>
                {prizeTypes.map(type => (
                  <option key={type.id} value={type.id}>
                    {type.prize_type_name}
                  </option>
                ))}
              </select>
            </div>

            {/* Campo: Monto del premio */}
            <div className="form-group">
              <label className="form-label">Valor del premio ($) *</label>
              <input
                type="number"
                name="raffle_prize_amount"
                className="form-input"
                placeholder="Ej: 3000000"
                min="1"
                value={formData.raffle_prize_amount}
                onChange={handleInputChange}
                disabled={loading}
                required
              />
            </div>
          </div>

          <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem'}}>
            
            {/* Campo: Precio por número */}
            <div className="form-group">
              <label className="form-label">Precio por número ($) *</label>
              <input
                type="number"
                name="raffle_number_price"
                className="form-input"
                placeholder="Ej: 50000"
                min="1"
                value={formData.raffle_number_price}
                onChange={handleInputChange}
                disabled={loading}
                required
              />
            </div>

            {/* Campo: Cantidad de números */}
            <div className="form-group">
              <label className="form-label">Cantidad de números *</label>
              <input
                type="number"
                name="raffle_number_amount"
                className="form-input"
                placeholder="Ej: 100"
                min="10"
                max="1000"
                value={formData.raffle_number_amount}
                onChange={handleInputChange}
                disabled={loading}
                required
              />
              <small style={{color: '#666', fontSize: '0.85rem'}}>
                Entre 10 y 1000 números
              </small>
            </div>
          </div>

          {/* NUEVO: Campo de mínimo para sortear */}
          <div className="form-group">
            <label className="form-label">Mínimo de números para sortear *</label>
            <input
              type="number"
              name="raffle_minimum_numbers_sold"
              className="form-input"
              placeholder="Ej: 50"
              min="1"
              value={formData.raffle_minimum_numbers_sold}
              onChange={handleInputChange}
              disabled={loading}
              required
            />
            <small style={{color: '#666', fontSize: '0.85rem'}}>
              Cantidad mínima de números que deben venderse para activar el sorteo. 
              No puede ser mayor a la cantidad total de números.
            </small>
          </div>

          {/* Campo: Fecha del sorteo */}
          <div className="form-group">
            <label className="form-label">¿Cuándo será el sorteo? *</label>
            <input
              type="datetime-local"
              name="raffle_draw_date"
              className="form-input"
              value={formData.raffle_draw_date}
              onChange={handleInputChange}
              disabled={loading}
              required
            />
            <small style={{color: '#666', fontSize: '0.85rem'}}>
              El sorteo debe ser en una fecha futura. Las ventas se cerrarán en esta fecha.
            </small>
          </div>

          {/* NUEVO: Campo de método de pago */}
          <div className="form-group">
            <label className="form-label">¿Dónde quieres recibir el dinero? *</label>
            <select
              name="raffle_creator_payment_method"
              className="form-input"
              value={formData.raffle_creator_payment_method}
              onChange={handleInputChange}
              disabled={loading || paymentMethods.length === 0}
              required
            >
              <option value="">Selecciona un método de pago...</option>
              {paymentMethods.map(method => (
                <option key={method.id} value={method.id}>
                  {method.payment_method_type_name || method.payment_method_type?.payment_method_type_name}
                  {method.last_digits ? ` (${method.last_digits})` : ''}
                  {method.masked_card_number ? ` (${method.masked_card_number})` : ''}
                  {method.payment_method_balance !== undefined ? 
                    ` - Saldo: $${parseFloat(method.payment_method_balance).toLocaleString()}` : ''}
                </option>
              ))}
            </select>
            <small style={{color: '#666', fontSize: '0.85rem'}}>
              {paymentMethods.length === 0 ? 
                '⚠️ No tienes métodos de pago registrados. Debes crear uno primero.' :
                'Aquí recibirás el dinero recaudado después del sorteo (descontando el premio).'
              }
            </small>
          </div>

          {/* Campo: Imagen (opcional) */}
          <div className="form-group">
            <label className="form-label">Imagen de la rifa (opcional)</label>
            <input
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              disabled={loading}
              className="form-input"
            />
            {formData.raffle_image && (
              <small style={{color: '#2ECC71', fontSize: '0.85rem'}}>
                ✓ Imagen seleccionada: {formData.raffle_image.name}
              </small>
            )}
            <small style={{color: '#666', fontSize: '0.85rem', display: 'block', marginTop: '0.5rem'}}>
              Formatos: JPG, PNG, GIF. Tamaño máximo: 5MB
            </small>
          </div>

          {/* Botón de envío */}
          <button 
            type="submit" 
            className="btn-primary" 
            style={{width: '100%'}}
            disabled={loading}
          >
            {loading ? 'Creando rifa...' : '¡Lanzar mi rifa!'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default CreateRaffle;
