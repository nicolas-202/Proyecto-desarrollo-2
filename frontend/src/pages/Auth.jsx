import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { authService } from '../services/authService';
const Auth = () => {
  const navigate = useNavigate();
  const { login, register, isAuthenticated, isLoading, error, clearError } = useAuth();
  
  // Estado para las pestañas
  const [activeTab, setActiveTab] = useState('login');
  
  // Estados para los formularios
  const [loginData, setLoginData] = useState({
    email: '',
    password: ''
  });
  
  const [registerData, setRegisterData] = useState({
    email: '',
    password: '',
    confirm_password: '',
    first_name: '',
    last_name: '',
    document_number: '',
    phone_number: '',
    address: '',
    country: '',
    state: '',
    city: '',
    gender: '',
    document_type: ''
  });
  
  // Estado para opciones del formulario de registro
  const [formOptions, setFormOptions] = useState({
    countries: [],
    states: [],
    cities: [],
    genders: [],
    documentTypes: [],
    loading: true
  });
  
  // Estados para mensajes
  const [messages, setMessages] = useState({
    login: { text: '', type: '', show: false },
    register: { text: '', type: '', show: false }
  });

  // Si ya está autenticado, redirigir
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  // Cargar opciones iniciales para el formulario de registro
  useEffect(() => {
    const loadInitialOptions = async () => {
      try {
        const [countriesRes, gendersRes, docTypesRes] = await Promise.all([
          authService.getCountries(),
          authService.getGenders(),
          authService.getDocumentTypes()
        ]);

        setFormOptions({
          countries: countriesRes.results || countriesRes || [],
          states: [],
          cities: [],
          genders: gendersRes.results || gendersRes || [],
          documentTypes: docTypesRes.results || docTypesRes || [],
          loading: false
        });
      } catch (error) {
        console.error('Error cargando opciones:', error);
        setFormOptions(prev => ({ ...prev, loading: false }));
      }
    };

    loadInitialOptions();
  }, []);

  // Cargar estados cuando se selecciona un país
  const handleCountryChange = async (e) => {
    const countryId = e.target.value;
    setRegisterData(prev => ({ 
      ...prev, 
      country: countryId,
      state: '', // Reset state
      city: ''   // Reset city
    }));

    if (countryId) {
      try {
        const statesRes = await authService.getStates(countryId);
        setFormOptions(prev => ({
          ...prev,
          states: statesRes.results || statesRes || [],
          cities: [] // Reset cities
        }));
      } catch (error) {
        console.error('Error cargando estados:', error);
        setFormOptions(prev => ({ ...prev, states: [], cities: [] }));
      }
    } else {
      setFormOptions(prev => ({ ...prev, states: [], cities: [] }));
    }
  };

  // Cargar ciudades cuando se selecciona un estado
  const handleStateChange = async (e) => {
    const stateId = e.target.value;
    setRegisterData(prev => ({ 
      ...prev, 
      state: stateId,
      city: '' // Reset city
    }));

    if (stateId) {
      try {
        const citiesRes = await authService.getCities(stateId);
        setFormOptions(prev => ({
          ...prev,
          cities: citiesRes.results || citiesRes || []
        }));
      } catch (error) {
        console.error('Error cargando ciudades:', error);
        setFormOptions(prev => ({ ...prev, cities: [] }));
      }
    } else {
      setFormOptions(prev => ({ ...prev, cities: [] }));
    }
  };

  // Función para mostrar mensajes
  const showMessage = (tab, message, type) => {
    setMessages(prev => ({
      ...prev,
      [tab]: { text: message, type, show: true }
    }));
    
    setTimeout(() => {
      setMessages(prev => ({
        ...prev,
        [tab]: { ...prev[tab], show: false }
      }));
    }, 3000);
  };

  // Manejar cambio de pestañas
  const switchTab = (tab) => {
    setActiveTab(tab);
    clearError();
    setMessages({
      login: { text: '', type: '', show: false },
      register: { text: '', type: '', show: false }
    });
  };

  // Manejar cambios en formulario de login
  const handleLoginChange = (e) => {
    const { name, value } = e.target;
    setLoginData(prev => ({ ...prev, [name]: value }));
    if (error) clearError();
  };

  // Manejar cambios en formulario de registro
  const handleRegisterChange = (e) => {
    const { name, value } = e.target;
    setRegisterData(prev => ({ ...prev, [name]: value }));
    if (error) clearError();
  };

  // Manejar envío de login
  const handleLogin = async (e) => {
    e.preventDefault();
    
    if (!loginData.email || !loginData.password) {
      showMessage('login', 'Completa todos los campos 📝', 'error');
      return;
    }

    const result = await login({
      email: loginData.email.trim(),
      password: loginData.password
    });

    if (result.success) {
      showMessage('login', '¡Bienvenido de nuevo! 🎉 Has entrado correctamente', 'success');
      setTimeout(() => {
        navigate('/', { replace: true });
      }, 1000);
    } else {
      showMessage('login', result.error || 'Error al iniciar sesión', 'error');
    }
  };

  // Manejar envío de registro
  const handleRegister = async (e) => {
    e.preventDefault();
    
    // Validaciones básicas
    if (!registerData.email || !registerData.password || !registerData.first_name || 
        !registerData.last_name || !registerData.country || !registerData.state || 
        !registerData.city || !registerData.document_type || !registerData.document_number || 
        !registerData.gender) {
      showMessage('register', 'Completa todos los campos obligatorios 📝', 'error');
      return;
    }

    if (registerData.password !== registerData.confirm_password) {
      showMessage('register', 'Las contraseñas no coinciden 🔒', 'error');
      return;
    }

    if (registerData.password.length < 8) {
      showMessage('register', 'La contraseña debe tener al menos 8 caracteres 🔒', 'error');
      return;
    }

    const result = await register(registerData);

    if (result.success) {
      showMessage('register', '¡Cuenta creada con éxito! 🎉 Ya puedes entrar a tu cuenta', 'success');
      setTimeout(() => {
        switchTab('login');
        setLoginData(prev => ({ ...prev, email: registerData.email }));
      }, 1500);
    } else {
      showMessage('register', result.error || 'Error al crear la cuenta', 'error');
    }
  };

  return (
    <div className="module-container active">
      {/* Breadcrumbs */}
      <div className="breadcrumbs">
        <div className="breadcrumb-item" onClick={() => navigate('/')}>Inicio</div>
        <div className="breadcrumb-separator">&gt;</div>
        <div className="breadcrumb-item">Entrar o registrarse</div>
      </div>
      
      {/* Pestañas */}
      <div className="tabs">
        <div 
          className={`tab ${activeTab === 'login' ? 'active' : ''}`}
          onClick={() => switchTab('login')}
        >
          Entrar
        </div>
        <div 
          className={`tab ${activeTab === 'register' ? 'active' : ''}`}
          onClick={() => switchTab('register')}
        >
          Crear cuenta
        </div>
      </div>

      {/* Contenido de Login */}
      <div className={`tab-content ${activeTab === 'login' ? 'active' : ''}`}>
        <div className="form-container">
          <h2 style={{textAlign: 'center', marginBottom: '2rem'}}>¡Bienvenido de nuevo! 👋</h2>
          <div className="guidance-text">
            Ingresa tus datos para acceder a tu cuenta y continuar con la diversión.
          </div>
          
          {/* Mensaje de login */}
          {messages.login.show && (
            <div className={`message ${messages.login.type} show`}>
              {messages.login.text}
            </div>
          )}
          
          {/* Error del contexto */}
          {error && activeTab === 'login' && (
            <div className="message error show">
              {error}
            </div>
          )}
          
          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label className="form-label">Tu correo electrónico</label>
              <input
                type="email"
                name="email"
                className="form-input"
                placeholder="ejemplo@email.com"
                value={loginData.email}
                onChange={handleLoginChange}
                disabled={isLoading}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Tu contraseña</label>
              <input
                type="password"
                name="password"
                className="form-input"
                placeholder="Escribe tu contraseña"
                value={loginData.password}
                onChange={handleLoginChange}
                disabled={isLoading}
                required
              />
            </div>
            <button 
              type="submit" 
              className="btn-primary" 
              style={{width: '100%'}}
              disabled={isLoading}
            >
              {isLoading ? 'Entrando...' : 'Entrar a mi cuenta'}
            </button>
          </form>
        </div>
      </div>

      {/* Contenido de Registro */}
      <div className={`tab-content ${activeTab === 'register' ? 'active' : ''}`}>
        <div className="form-container">
          <h2 style={{textAlign: 'center', marginBottom: '2rem'}}>¡Únete a la comunidad! 🎉</h2>
          <div className="guidance-text">
            Crea tu cuenta en solo unos pasos y comienza a disfrutar de todas las rifas.
          </div>
          
          {/* Mensaje de registro */}
          {messages.register.show && (
            <div className={`message ${messages.register.type} show`}>
              {messages.register.text}
            </div>
          )}
          
          {/* Error del contexto */}
          {error && activeTab === 'register' && (
            <div className="message error show">
              {error}
            </div>
          )}
          
          {formOptions.loading ? (
            <div style={{textAlign: 'center', color: '#666', margin: '2rem 0'}}>
              Cargando formulario... 🔄
            </div>
          ) : (
            <form onSubmit={handleRegister}>
              {/* Información de cuenta */}
              <div className="form-group">
                <label className="form-label">Tu correo electrónico *</label>
                <input
                  type="email"
                  name="email"
                  className="form-input"
                  placeholder="ejemplo@email.com"
                  value={registerData.email}
                  onChange={handleRegisterChange}
                  disabled={isLoading}
                  required
                />
              </div>

              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem'}}>
                <div className="form-group">
                  <label className="form-label">Crea una contraseña *</label>
                  <input
                    type="password"
                    name="password"
                    className="form-input"
                    placeholder="Mínimo 8 caracteres"
                    value={registerData.password}
                    onChange={handleRegisterChange}
                    disabled={isLoading}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Confirma tu contraseña *</label>
                  <input
                    type="password"
                    name="confirm_password"
                    className="form-input"
                    placeholder="Repite tu contraseña"
                    value={registerData.confirm_password}
                    onChange={handleRegisterChange}
                    disabled={isLoading}
                    required
                  />
                </div>
              </div>

              {/* Información personal */}
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem'}}>
                <div className="form-group">
                  <label className="form-label">Tu nombre *</label>
                  <input
                    type="text"
                    name="first_name"
                    className="form-input"
                    placeholder="Cómo te llamas"
                    value={registerData.first_name}
                    onChange={handleRegisterChange}
                    disabled={isLoading}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Tu apellido *</label>
                  <input
                    type="text"
                    name="last_name"
                    className="form-input"
                    placeholder="Tu apellido"
                    value={registerData.last_name}
                    onChange={handleRegisterChange}
                    disabled={isLoading}
                    required
                  />
                </div>
              </div>

              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem'}}>
                <div className="form-group">
                  <label className="form-label">Tipo de documento *</label>
                  <select
                    name="document_type"
                    className="form-input"
                    value={registerData.document_type}
                    onChange={handleRegisterChange}
                    disabled={isLoading}
                    required
                  >
                    <option value="">Selecciona...</option>
                    {formOptions.documentTypes.map(type => (
                      <option key={type.id} value={type.id}>
                        {type.document_type_name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Número de documento *</label>
                  <input
                    type="text"
                    name="document_number"
                    className="form-input"
                    placeholder="Solo números"
                    value={registerData.document_number}
                    onChange={handleRegisterChange}
                    disabled={isLoading}
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Género *</label>
                <select
                  name="gender"
                  className="form-input"
                  value={registerData.gender}
                  onChange={handleRegisterChange}
                  disabled={isLoading}
                  required
                >
                  <option value="">Selecciona...</option>
                  {formOptions.genders.map(gender => (
                    <option key={gender.id} value={gender.id}>
                      {gender.gender_name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Tu número de teléfono *</label>
                <input
                  type="tel"
                  name="phone_number"
                  className="form-input"
                  placeholder="Para contactarte si ganas"
                  value={registerData.phone_number}
                  onChange={handleRegisterChange}
                  disabled={isLoading}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">País *</label>
                <select
                  name="country"
                  className="form-input"
                  value={registerData.country}
                  onChange={handleCountryChange}
                  disabled={isLoading}
                  required
                >
                  <option value="">Selecciona tu país...</option>
                  {formOptions.countries.map(country => (
                    <option key={country.id} value={country.id}>
                      {country.country_name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Departamento/Estado *</label>
                <select
                  name="state"
                  className="form-input"
                  value={registerData.state}
                  onChange={handleStateChange}
                  disabled={isLoading || !registerData.country}
                  required
                >
                  <option value="">
                    {!registerData.country 
                      ? 'Primero selecciona un país...' 
                      : 'Selecciona tu departamento/estado...'
                    }
                  </option>
                  {formOptions.states.map(state => (
                    <option key={state.id} value={state.id}>
                      {state.state_name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Ciudad *</label>
                <select
                  name="city"
                  className="form-input"
                  value={registerData.city}
                  onChange={handleRegisterChange}
                  disabled={isLoading || !registerData.state}
                  required
                >
                  <option value="">
                    {!registerData.state 
                      ? 'Primero selecciona un departamento/estado...' 
                      : 'Selecciona tu ciudad...'
                    }
                  </option>
                  {formOptions.cities.map(city => (
                    <option key={city.id} value={city.id}>
                      {city.city_name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Tu dirección *</label>
                <input
                  type="text"
                  name="address"
                  className="form-input"
                  placeholder="Para enviarte premios físicos"
                  value={registerData.address}
                  onChange={handleRegisterChange}
                  disabled={isLoading}
                  required
                />
              </div>

              <button 
                type="submit" 
                className="btn-primary" 
                style={{width: '100%'}}
                disabled={isLoading}
              >
                {isLoading ? 'Creando cuenta...' : 'Crear mi cuenta'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default Auth;