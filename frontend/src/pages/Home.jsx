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
        {/* Primera línea: Búsqueda y Asistente */}
        <div style={{ 
          display: 'flex',
          gap: '0.75rem',
          alignItems: 'center',
          marginBottom: '0.75rem',
          flexWrap: 'wrap'
        }}>
          {/* Búsqueda */}
          <input
            type="text"
            className="search-input"
            placeholder="🔍 Buscar rifas..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            style={{ 
              flex: '1 1 300px',
              minWidth: 0,
              maxWidth: '100%',
              padding: '0.875rem 1.25rem',
              fontSize: '1rem'
            }}
          />
        </div>

        {/* Segunda línea: Filtros avanzados */}
        <div style={{ 
          display: 'flex',
          gap: '0.5rem',
          alignItems: 'center',
          flexWrap: 'wrap',
          padding: '0.75rem',
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '8px',
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          {/* Tipo de Premio */}
          <select
            className="form-input"
            value={prizeTypeFilter}
            onChange={e => setPrizeTypeFilter(e.target.value)}
            style={{ 
              margin: 0, 
              padding: '0.5rem',
              fontSize: '0.9rem',
              flex: '1 1 150px',
              minWidth: '140px'
            }}
          >
            <option value="all">🏆 Tipo de Premio</option>
            {prizeTypes.map(type => (
              <option key={type.id} value={type.id}>
                {type.prize_type_name}
              </option>
            ))}
          </select>

          {/* Precio Mínimo */}
          <input
            type="number"
            className="form-input"
            placeholder="$ Mín"
            value={minPrice}
            onChange={e => setMinPrice(e.target.value)}
            min="0"
            style={{ 
              margin: 0, 
              padding: '0.5rem',
              fontSize: '0.9rem',
              flex: '0 1 100px',
              minWidth: '90px'
            }}
          />

          {/* Precio Máximo */}
          <input
            type="number"
            className="form-input"
            placeholder="$ Máx"
            value={maxPrice}
            onChange={e => setMaxPrice(e.target.value)}
            min="0"
            style={{ 
              margin: 0, 
              padding: '0.5rem',
              fontSize: '0.9rem',
              flex: '0 1 100px',
              minWidth: '90px'
            }}
          />

          {/* Fecha Desde */}
          <input
            type="date"
            className="form-input"
            value={dateFrom}
            onChange={e => setDateFrom(e.target.value)}
            title="Sorteo desde"
            style={{ 
              margin: 0, 
              padding: '0.5rem',
              fontSize: '0.9rem',
              flex: '0 1 140px',
              minWidth: '130px'
            }}
          />

          {/* Fecha Hasta */}
          <input
            type="date"
            className="form-input"
            value={dateTo}
            onChange={e => setDateTo(e.target.value)}
            title="Sorteo hasta"
            style={{ 
              margin: 0, 
              padding: '0.5rem',
              fontSize: '0.9rem',
              flex: '0 1 140px',
              minWidth: '130px'
            }}
          />

          {/* Botón Limpiar */}
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
            style={{ 
              padding: '0.5rem 1rem',
              fontSize: '0.85rem',
              whiteSpace: 'nowrap',
              flex: '0 0 auto'
            }}
          >
            🔄 Limpiar
          </button>
        </div>
      </div>

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
