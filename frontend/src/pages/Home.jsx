import { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

function Home() {
  const [rifas, setRifas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    const fetchRifas = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/raffle/list/`);
        setRifas(response.data);
      } catch (err) {
        setError('Error al cargar las rifas');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchRifas();
  }, []);

  const getRifaIcon = (prize) => {
    if (!prize) return '🎁';
    const lowerPrize = prize.toString().toLowerCase();
    if (lowerPrize.includes('iphone') || lowerPrize.includes('celular') || lowerPrize.includes('telefono')) return '📱';
    if (lowerPrize.includes('playstation') || lowerPrize.includes('xbox') || lowerPrize.includes('consola')) return '🎮';
    if (lowerPrize.includes('laptop') || lowerPrize.includes('computador') || lowerPrize.includes('pc')) return '💻';
    if (lowerPrize.includes('carro') || lowerPrize.includes('auto') || lowerPrize.includes('vehiculo')) return '🚗';
    if (lowerPrize.includes('moto') || lowerPrize.includes('motocicleta')) return '🏍️';
    if (lowerPrize.includes('viaje') || lowerPrize.includes('vacaciones')) return '✈️';
    if (lowerPrize.includes('dinero') || lowerPrize.includes('efectivo') || lowerPrize.includes('cash')) return '💰';
    if (lowerPrize.includes('tv') || lowerPrize.includes('television')) return '📺';
    if (lowerPrize.includes('bicicleta') || lowerPrize.includes('bici')) return '🚲';
    return '🎁';
  };

  const filteredRifas = rifas.filter(rifa => {
    const matchesSearch = rifa.raffle_name?.toLowerCase().includes(searchTerm.toLowerCase()) || 
                         rifa.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || 
                         (statusFilter === 'active' && new Date(rifa.draw_date) > new Date()) ||
                         (statusFilter === 'finished' && new Date(rifa.draw_date) <= new Date());
    return matchesSearch && matchesStatus;
  });

  if (loading) return (
    <div className="module-container active">
      <div style={{textAlign: 'center', color: 'white', fontSize: '1.2rem', marginTop: '3rem'}}>
        Cargando rifas... 🎰
      </div>
    </div>
  );

  if (error) return (
    <div className="module-container active">
      <div className="message error show">
        Error: {error}
      </div>
    </div>
  );

  return (
    <div className="module-container active">
      {/* Breadcrumbs */}
      <div className="breadcrumbs">
        <div className="breadcrumb-item">Inicio</div>
      </div>
      
      {/* Texto de orientación */}
      <div className="guidance-text highlight">
        <strong>🎯 ¿Listo para ganar increíbles premios?</strong> Explora todas las rifas disponibles y encuentra la que más te guste. ¡Cada número que compres te acerca más al premio!
      </div>
      
      {/* Filtros */}
      <div className="filters">
        <input 
          type="text" 
          className="search-input" 
          placeholder="Busca rifas por nombre o premio..." 
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <select 
          className="form-input" 
          style={{width: 'auto'}} 
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="all">Todas las rifas</option>
          <option value="active">Rifas activas</option>
          <option value="finished">Rifas finalizadas</option>
        </select>
      </div>

      {/* Grid de rifas */}
      <div className="rifa-grid">
        {filteredRifas.length === 0 ? (
          <div style={{
            gridColumn: '1 / -1',
            textAlign: 'center', 
            color: 'white', 
            fontSize: '1.1rem',
            marginTop: '2rem'
          }}>
            {rifas.length === 0 
              ? 'No hay rifas disponibles en este momento.' 
              : 'No se encontraron rifas con esos criterios.'}
          </div>
        ) : (
          filteredRifas.map((rifa) => (
            <div key={rifa.id} className="rifa-card">
              {/* Imagen de la rifa */}
              <div className="rifa-image">
                {getRifaIcon(rifa.prize_description || rifa.raffle_name)}
              </div>
              
              {/* Contenido de la rifa */}
              <div className="rifa-content">
                <div className="rifa-title">{rifa.raffle_name}</div>
                <p style={{marginBottom: '0.5rem', fontSize: '0.9rem', color: '#666'}}>
                  {rifa.description}
                </p>
                <div className="rifa-price">
                  ${rifa.raffle_number_price?.toLocaleString()}
                </div>
                <div style={{marginBottom: '0.5rem', fontSize: '0.9rem', color: '#666'}}>
                  <strong>Premio:</strong> ${rifa.prize_amount?.toLocaleString()}
                </div>
                <div className="rifa-date">
                  Sorteo: {new Date(rifa.draw_date).toLocaleDateString('es-ES', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
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