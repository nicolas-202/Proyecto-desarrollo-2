import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { apiClient } from '../services/authService';
import ReactMarkdown from 'react-markdown';

function Home() {
  // Obtener el contexto de autenticación
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [rifas, setRifas] = useState([]);
  const [prizeTypes, setPrizeTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [prizeTypeFilter, setPrizeTypeFilter] = useState('all');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [isSendingMessage, setIsSendingMessage] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);  

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Cargar rifas y tipos de premio en paralelo usando apiClient
        // que automáticamente agrega el token si el usuario está logueado
        const [rifasResponse, prizeTypesResponse] = await Promise.all([
          apiClient.get('/raffle/list/'),
          apiClient.get('/raffle-info/prizetype/'),
        ]);

        setRifas(rifasResponse.data);
        setPrizeTypes(prizeTypesResponse.data);
      } catch (err) {
        setError('Error al cargar los datos');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    // Solo cargar datos cuando el contexto de auth esté listo
    if (!authLoading) {
      fetchData();
    }
  }, [authLoading]);

  const getRifaIcon = rifa => {
    // Si la rifa tiene imagen, usarla
    if (rifa.raffle_image) {
      return (
        <img
          src={rifa.raffle_image}
          alt={rifa.raffle_name}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
          }}
        />
      );
    }
    return '🎁';
  };

  const filteredRifas = rifas.filter(rifa => {
    const searchLower = searchTerm.toLowerCase();
    const matchesSearch =
      searchTerm === '' ||
      rifa.raffle_name?.toLowerCase().includes(searchLower) ||
      rifa.raffle_description?.toLowerCase().includes(searchLower) ||
      rifa.raffle_prize_type?.prize_type_name?.toLowerCase().includes(searchLower);

    const matchesPrizeType =
      prizeTypeFilter === 'all' || rifa.raffle_prize_type?.id === parseInt(prizeTypeFilter);

    // Filtro por rango de precio del ticket
    const matchesMinPrice = minPrice === '' || rifa.raffle_number_price >= parseFloat(minPrice);
    const matchesMaxPrice = maxPrice === '' || rifa.raffle_number_price <= parseFloat(maxPrice);

    // Filtro por fecha de sorteo
    const raffleDate = new Date(rifa.raffle_draw_date);
    const matchesDateFrom = dateFrom === '' || raffleDate >= new Date(dateFrom);
    const matchesDateTo = dateTo === '' || raffleDate <= new Date(dateTo + 'T23:59:59');

    return matchesSearch && matchesPrizeType && matchesMinPrice && matchesMaxPrice && matchesDateFrom && matchesDateTo;
  });

  const sendChatMessage = async () => {
    if (!chatInput.trim() || isSendingMessage) return;

    const userMessage = chatInput.trim();
    const CHATBOT_URL = import.meta.env.VITE_CHATBOT_URL || 'http://localhost:5678/webhook/bf8716c0-40cd-4859-a3bb-482899d973a1/chat';
    
    setChatInput('');
    setIsSendingMessage(true);

    // Agregar mensaje del usuario
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);

    try {
      const response = await fetch(CHATBOT_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          chatInput: userMessage,
          sessionId: sessionId 
        }),
      });

      const data = await response.json();
      
      // Extraer la respuesta del formato de n8n
      let botResponse = 'Lo siento, no pude procesar tu mensaje.';
      
      if (data.response?.generations?.[0]?.[0]?.text) {
        botResponse = data.response.generations[0][0].text;
      } else if (data.output) {
        botResponse = data.output;
      } else if (data.message) {
        botResponse = data.message;
      }
      
      // Agregar respuesta del bot
      setChatMessages(prev => [...prev, { 
        role: 'assistant', 
        content: botResponse
      }]);
    } catch (err) {
      console.error('Error al enviar mensaje:', err);
      setChatMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Error al conectar con el chatbot. Por favor intenta de nuevo.' 
      }]);
    } finally {
      setIsSendingMessage(false);
    }
  };

  // Mostrar loading mientras se cargan los datos o el contexto de auth
  if (loading || authLoading)
    return (
      <div className="module-container active">
        <div style={{ textAlign: 'center', color: 'white', fontSize: '1.2rem', marginTop: '3rem' }}>
          Cargando rifas... 🎰
        </div>
      </div>
    );

  if (error)
    return (
      <div className="module-container active">
        <div className="message error show">Error: {error}</div>
      </div>
    );

  return (
    <div className="module-container active">
      {/* Breadcrumbs */}
      <div className="breadcrumbs">
        <div className="breadcrumb-item">Inicio</div>
      </div>

      {/* Texto de orientación personalizado */}
      <div className="guidance-text highlight">
        {isAuthenticated ? (
          <strong>🎯 ¡Hola {user?.first_name}! ¿Listo para ganar increíbles premios?</strong>
        ) : (
          <strong>🎯 ¿Listo para ganar increíbles premios?</strong>
        )}{' '}
        Explora todas las rifas disponibles y encuentra la que más te guste.
        {isAuthenticated
          ? ' ¡Cada número que compres te acerca más al premio!'
          : ' ¡Crea tu cuenta para participar!'}
      </div>

      {/* Mensaje adicional para usuarios no autenticados */}
      {!isAuthenticated && (
        <div
          className="guidance-text"
          style={{
            background: '#FFF4ED',
            padding: '1rem',
            borderRadius: '8px',
            borderLeft: '4px solid #FF6B35',
            marginBottom: '1rem',
          }}
        >
          💡 <strong>¡Únete a la diversión!</strong> Para participar en las rifas necesitas{' '}
          <a href="/auth" style={{ color: '#FF6B35', textDecoration: 'underline' }}>
            crear tu cuenta
          </a>{' '}
          o{' '}
          <a href="/auth" style={{ color: '#FF6B35', textDecoration: 'underline' }}>
            iniciar sesión
          </a>
          . ¡Es rápido y gratis!
        </div>
      )}

      {/* Filtros */}
      <div className="filters" style={{ marginBottom: '1.5rem' }}>
        {/* Barra de búsqueda con botón de filtros */}
        <div className="search-container">
          {/* Búsqueda - ocupa el espacio restante */}
          <input
            type="text"
            className="search-input"
            placeholder="🔍 Buscar rifas por nombre, descripción..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
          />

          {/* Botón de filtros con indicador */}
          <button
            className="btn-secondary filters-toggle-btn"
            onClick={() => setShowFilters(true)}
          >
            🔧 Filtros
            {/* Indicador de filtros activos */}
            {(minPrice || maxPrice || dateFrom || dateTo) && (
              <span className="filters-badge">
                {[minPrice, maxPrice, dateFrom, dateTo].filter(Boolean).length}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Modal flotante de filtros */}
      {showFilters && (
        <>
          {/* Overlay oscuro */}
          <div 
            className="filters-modal-overlay"
            onClick={() => setShowFilters(false)}
          />
          
          {/* Panel de filtros flotante */}
          <div className="filters-modal-panel">
            {/* Header del modal */}
            <div className="filters-modal-header">
              <h3 className="filters-modal-title">
                🔧 Filtros Avanzados
              </h3>
              <button
                className="filters-modal-close"
                onClick={() => setShowFilters(false)}
              >
                ✕
              </button>
            </div>

            {/* Contenido scrolleable */}
            <div className="filters-modal-content">
              <div className="filters-group-container">
                {/* Rango de Precio */}
                <div className="filter-group">
                  <label className="filter-label">
                    💰 Rango de Precio del Ticket
                  </label>
                  <div className="filter-range-grid">
                    <input
                      type="number"
                      className="filter-input"
                      placeholder="Mínimo"
                      value={minPrice}
                      onChange={e => setMinPrice(e.target.value)}
                      min="0"
                    />
                    <span className="filter-range-separator">-</span>
                    <input
                      type="number"
                      className="filter-input"
                      placeholder="Máximo"
                      value={maxPrice}
                      onChange={e => setMaxPrice(e.target.value)}
                      min="0"
                    />
                  </div>
                </div>

                {/* Rango de Fechas */}
                <div className="filter-group">
                  <label className="filter-label">
                    📅 Fecha de Sorteo
                  </label>
                  <div className="filter-range-grid">
                    <input
                      type="date"
                      className="filter-input"
                      value={dateFrom}
                      onChange={e => setDateFrom(e.target.value)}
                    />
                    <span className="filter-range-separator">→</span>
                    <input
                      type="date"
                      className="filter-input"
                      value={dateTo}
                      onChange={e => setDateTo(e.target.value)}
                    />
                  </div>
                </div>

                {/* Resumen de filtros activos */}
                {(minPrice || maxPrice || dateFrom || dateTo) && (
                  <div className="filters-summary">
                    <div className="filters-summary-title">
                      ✓ Filtros activos:
                    </div>
                    <ul className="filters-summary-list">
                      {minPrice && <li>Precio mínimo: ${parseFloat(minPrice).toLocaleString()}</li>}
                      {maxPrice && <li>Precio máximo: ${parseFloat(maxPrice).toLocaleString()}</li>}
                      {dateFrom && <li>Desde: {new Date(dateFrom).toLocaleDateString('es-ES')}</li>}
                      {dateTo && <li>Hasta: {new Date(dateTo).toLocaleDateString('es-ES')}</li>}
                    </ul>
                  </div>
                )}
              </div>
            </div>

            {/* Footer con botones */}
            <div className="filters-modal-footer">
              <button
                className="btn-secondary"
                onClick={() => {
                  setSearchTerm('');
                  setPrizeTypeFilter('all');
                  setMinPrice('');
                  setMaxPrice('');
                  setDateFrom('');
                  setDateTo('');
                }}
              >
                🔄 Limpiar Todo
              </button>
              <button
                className="btn-primary"
                onClick={() => setShowFilters(false)}
              >
                ✓ Aplicar Filtros
              </button>
            </div>
          </div>
        </>
      )}

      {/* Grid de rifas */}
      <div className="rifa-grid">
        {filteredRifas.length === 0 ? (
          <div
            style={{
              gridColumn: '1 / -1',
              textAlign: 'center',
              color: 'white',
              fontSize: '1.1rem',
              marginTop: '2rem',
            }}
          >
            {rifas.length === 0
              ? 'No hay rifas disponibles en este momento.'
              : 'No se encontraron rifas con esos criterios.'}
          </div>
        ) : (
          filteredRifas.map(rifa => (
            <div key={rifa.id} className="rifa-card">
              {/* Imagen de la rifa */}
              <div className="rifa-image">{getRifaIcon(rifa)}</div>

              {/* Contenido de la rifa */}
              <div className="rifa-content">
                <div className="rifa-title">{rifa.raffle_name}</div>
                <p style={{ marginBottom: '0.5rem', fontSize: '0.9rem', color: '#666' }}>
                  {rifa.description}
                </p>
                <div className="rifa-prize">
                  Precio ticket: ${rifa.raffle_number_price?.toLocaleString()}
                </div>
                <div className="rifa-card-content">
                  <strong>Premio:</strong> ${rifa.raffle_prize_amount?.toLocaleString()}
                </div>
                <div className="rifa-card-content">
                  <strong>Creada por: </strong>
                  {rifa.raffle_created_by?.first_name} {rifa.raffle_created_by?.last_name}
                  {/* Mostrar indicador si es la rifa del usuario actual */}
                  {isAuthenticated && user?.id === rifa.raffle_created_by?.id && (
                    <span
                      style={{
                        color: '#6A4C93',
                        fontSize: '0.8rem',
                        fontWeight: 'bold',
                        marginLeft: '0.5rem',
                      }}
                    >
                      (Tu rifa)
                    </span>
                  )}
                </div>
                <div className="rifa-date">
                  Sorteo:{' '}
                  {new Date(rifa.raffle_draw_date).toLocaleDateString('es-ES', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </div>

                {/* Botón de acción según el estado de autenticación */}
                <div style={{ marginTop: '1rem' }}>
                  {isAuthenticated ? (
                    user?.id === rifa.raffle_created_by?.id ? (
                      // Si es la rifa del usuario
                      <button
                        className="btn-secondary"
                        style={{ width: '100%', fontSize: '0.9rem' }}
                        onClick={() => navigate(`/raffle/${rifa.id}`)}
                      >
                        ⚙️ Gestionar mi rifa
                      </button>
                    ) : (
                      // Si puede participar
                      <button
                        className="btn-primary"
                        style={{ width: '100%', fontSize: '0.9rem' }}
                        onClick={() => navigate(`/raffle/${rifa.id}`)}
                      >
                        🎯 Comprar números
                      </button>
                    )
                  ) : (
                    // Si no está autenticado - dejar ver la rifa
                    <button
                      className="btn-primary"
                      style={{ width: '100%', fontSize: '0.9rem' }}
                      onClick={() => navigate(`/raffle/${rifa.id}`)}
                    >
                      👁️ Ver rifa
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      
    </div>
  );
}

export default Home;
