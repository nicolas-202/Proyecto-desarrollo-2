import { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

function Home() {
  const [rifas, setRifas] = useState([]);
  const [prizeTypes, setPrizeTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [prizeTypeFilter, setPrizeTypeFilter] = useState('all');

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Cargar rifas y tipos de premio en paralelo
        const [rifasResponse, prizeTypesResponse] = await Promise.all([
          axios.get(`${API_BASE_URL}/raffle/list/`),
          axios.get(`${API_BASE_URL}/raffle-info/prizetype/`)
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

    fetchData();
  }, []);

  const getRifaIcon = (rifa) => {
    // Si la rifa tiene imagen, usarla
    if (rifa.raffle_image) {
      return <img 
        src={rifa.raffle_image} 
        alt={rifa.raffle_name}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover'
        }}
      />;
    }
    return '🎁';
  };

  const filteredRifas = rifas.filter(rifa => {
    const searchLower = searchTerm.toLowerCase();
    const matchesSearch = searchTerm === '' || 
                        rifa.raffle_name?.toLowerCase().includes(searchLower) || 
                        rifa.raffle_description?.toLowerCase().includes(searchLower) ||
                        rifa.raffle_prize_type?.prize_type_name?.toLowerCase().includes(searchLower);

    const matchesPrizeType = prizeTypeFilter === 'all' || 
                        rifa.raffle_prize_type?.id === parseInt(prizeTypeFilter);
    
    return matchesSearch && matchesPrizeType;
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
          placeholder="Busca rifas por nombre, descripción o tipo de premio..." 
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <select 
          className="form-input" 
          style={{width: 'auto', minWidth: '150px'}} 
          value={prizeTypeFilter}
          onChange={(e) => setPrizeTypeFilter(e.target.value)}
        >
          <option value="all">Todos los premios</option>
          {prizeTypes.map(prizeType => (
            <option key={prizeType.id} value={prizeType.id}>
              {prizeType.prize_type_name}
            </option>
          ))}
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
                {getRifaIcon(rifa)}
              </div>
              
              {/* Contenido de la rifa */}
              <div className="rifa-content">
                <div className="rifa-title">{rifa.raffle_name}</div>
                <p style={{marginBottom: '0.5rem', fontSize: '0.9rem', color: '#666'}}>
                  {rifa.description}
                </p>
                <div className="rifa-prize">
                  Precio ticket:
                  ${rifa.raffle_number_prize?.toLocaleString()}
                </div>
                <div className="rifa-card-content">
                  <strong>Premio:</strong> ${rifa.raffle_prize_amount?.toLocaleString()}
                </div>
                <div className="rifa-card-content">
                  <strong>Creada por: </strong> {rifa.raffle_created_by?.full_name?.toLocaleString()}
                </div>
                <div className="rifa-date">
                  Sorteo: {new Date(rifa.raffle_draw_date).toLocaleDateString('es-ES', {
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