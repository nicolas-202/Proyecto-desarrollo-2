import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {apiClient} from '../services/authService';

function MyNumbers() {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [activeTab, setActiveTab] = useState('purchased');
  const [myTickets, setMyTickets] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/auth');
      return;
    }

    const fetchMyTickets = async () => {
      try {
        setLoading(true);
        const [ticketsResponse, statsResponse] = await Promise.all([
          apiClient.get('/tickets/my-tickets/'),
          apiClient.get('/tickets/stats/')
        ]);

        setMyTickets(ticketsResponse.data);
        setStats(statsResponse.data);
      } catch (err) {
        setError('Error al cargar tus números');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchMyTickets();
  }, [isAuthenticated, navigate]);

  const getRifaIcon = (raffleName) => {
    if (!raffleName) return '🎁';

    const prize = raffleName?.toLowerCase() || '';
    if (prize.includes('iphone') || prize.includes('celular')) return '📱';
    if (prize.includes('playstation') || prize.includes('xbox')) return '🎮';
    if (prize.includes('laptop') || prize.includes('computador')) return '💻';
    if (prize.includes('carro') || prize.includes('auto')) return '🚗';
    if (prize.includes('moto')) return '🏍️';
    if (prize.includes('viaje')) return '✈️';
    if (prize.includes('dinero') || prize.includes('efectivo')) return '💰';
    return '🎁';
  };

  const getRaffleStatus = (ticket) => {
    // Por ahora retornar estado genérico
    // TODO: Obtener detalles completos de la rifa si es necesario
    return 'Activa';
  };

  const groupTicketsByRaffle = () => {
    const grouped = {};

    myTickets.forEach(ticket => {
      const rafflId = ticket.raffle_id;
      if (!rafflId) return;

      if (!grouped[rafflId]) {
        grouped[rafflId] = {
          raffle_id: rafflId,
          raffle_name: ticket.raffle_name,
          tickets: [],
          totalSpent: 0
        };
      }

      grouped[rafflId].tickets.push(ticket);
      // Por ahora no podemos calcular el precio total sin los detalles de la rifa
      grouped[rafflId].totalSpent += 0;
    });

    return Object.values(grouped);
  };

  const getWonRaffles = () => {
    return myTickets.filter(ticket => ticket.is_winner === true);
  };

  if (loading) {
    return (
      <div className="module-container active">
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '400px',
          color: 'white',
          fontSize: '1.2rem'
        }}>
          Cargando tus números...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="module-container active">
        <div className="message error show">
          {error}
        </div>
      </div>
    );
  }

  const groupedTickets = groupTicketsByRaffle();
  const wonRaffles = getWonRaffles();

  return (
    <div className="module-container active">
      {/* Breadcrumbs */}
      <div className="breadcrumbs">
        <div className="breadcrumb-item" onClick={() => navigate('/')}>Inicio</div>
        <div className="breadcrumb-separator">&gt;</div>
        <div className="breadcrumb-item">Mis números</div>
      </div>

      {/* Estadísticas rápidas */}
      {stats && (
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '1.5rem',
          marginBottom: '2rem',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1.5rem'
        }}>
          <div style={{textAlign: 'center'}}>
            <div style={{fontSize: '2rem', marginBottom: '0.5rem'}}>🎫</div>
            <div style={{fontSize: '1.5rem', fontWeight: 'bold', color: '#FF6B35'}}>
              {stats.total_tickets_purchased || 0}
            </div>
            <div style={{color: '#666', fontSize: '0.9rem'}}>Números comprados</div>
          </div>

          <div style={{textAlign: 'center'}}>
            <div style={{fontSize: '2rem', marginBottom: '0.5rem'}}>🎯</div>
            <div style={{fontSize: '1.5rem', fontWeight: 'bold', color: '#6A4C93'}}>
              {stats.active_tickets || 0}
            </div>
            <div style={{color: '#666', fontSize: '0.9rem'}}>Tickets activos</div>
          </div>

          <div style={{textAlign: 'center'}}>
            <div style={{fontSize: '2rem', marginBottom: '0.5rem'}}>🏆</div>
            <div style={{fontSize: '1.5rem', fontWeight: 'bold', color: '#2ECC71'}}>
              {stats.winning_tickets || 0}
            </div>
            <div style={{color: '#666', fontSize: '0.9rem'}}>Tickets ganadores</div>
          </div>

          <div style={{textAlign: 'center'}}>
            <div style={{fontSize: '2rem', marginBottom: '0.5rem'}}>💰</div>
            <div style={{fontSize: '1.5rem', fontWeight: 'bold', color: '#F4A261'}}>
              ${parseFloat(stats.total_amount_spent || 0).toLocaleString()}
            </div>
            <div style={{color: '#666', fontSize: '0.9rem'}}>Total invertido</div>
          </div>

          <div style={{textAlign: 'center'}}>
            <div style={{fontSize: '2rem', marginBottom: '0.5rem'}}>📊</div>
            <div style={{fontSize: '1.5rem', fontWeight: 'bold', color: '#3498DB'}}>
              {stats.win_rate || '0.0%'}
            </div>
            <div style={{color: '#666', fontSize: '0.9rem'}}>Tasa de éxito</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="tabs">
        <div 
          className={`tab ${activeTab === 'purchased' ? 'active' : ''}`}
          onClick={() => setActiveTab('purchased')}
        >
          Números comprados
        </div>
        <div 
          className={`tab ${activeTab === 'won' ? 'active' : ''}`}
          onClick={() => setActiveTab('won')}
        >
          ¡Mis premios! 🏆
        </div>
      </div>

      {/* Tab de Números Comprados */}
      {activeTab === 'purchased' && (
        <div className="tab-content active">
          <div className="guidance-text" style={{color: 'white'}}>
            Aquí puedes ver todos los números que has comprado y el estado de cada rifa.
          </div>

          {groupedTickets.length === 0 ? (
            <div style={{
              background: 'white',
              borderRadius: '12px',
              padding: '3rem',
              textAlign: 'center',
              marginTop: '2rem'
            }}>
              <div style={{fontSize: '3rem', marginBottom: '1rem'}}>🎲</div>
              <h3 style={{marginBottom: '0.5rem'}}>No has comprado números aún</h3>
              <p style={{color: '#666', marginBottom: '1.5rem'}}>
                ¡Explora las rifas disponibles y participa para ganar increíbles premios!
              </p>
              <button 
                className="btn-primary"
                onClick={() => navigate('/')}
              >
                Ver rifas disponibles
              </button>
            </div>
          ) : (
            <div style={{marginTop: '2rem'}}>
              {groupedTickets.map((group, index) => (
                <div 
                  key={index}
                  style={{
                    background: 'white',
                    borderRadius: '12px',
                    padding: '1.5rem',
                    marginBottom: '1.5rem',
                    boxShadow: '0 4px 15px rgba(0,0,0,0.1)'
                  }}
                >
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'start',
                    marginBottom: '1rem'
                  }}>
                    <div style={{flex: 1}}>
                      <div style={{display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem'}}>
                        <div style={{fontSize: '2rem'}}>
                          {getRifaIcon(group.raffle_name)}
                        </div>
                        <div>
                          <h3 style={{
                            fontSize: '1.3rem',
                            marginBottom: '0.25rem',
                            color: '#2C3E50'
                          }}>
                            {group.raffle_name}
                          </h3>
                          <span style={{
                            display: 'inline-block',
                            padding: '0.25rem 0.75rem',
                            borderRadius: '6px',
                            fontSize: '0.85rem',
                            fontWeight: '600',
                            background: '#d4f4dd',
                            color: '#155724'
                          }}>
                            {getRaffleStatus(group)}
                          </span>
                        </div>
                      </div>

                      <div style={{
                        background: '#F8F9FA',
                        padding: '1rem',
                        borderRadius: '8px',
                        marginBottom: '1rem'
                      }}>
                        <div style={{
                          fontWeight: '600',
                          marginBottom: '0.5rem',
                          color: '#2C3E50'
                        }}>
                          Tus números ({group.tickets.length}):
                        </div>
                        <div style={{
                          display: 'flex',
                          flexWrap: 'wrap',
                          gap: '0.5rem'
                        }}>
                          {group.tickets.map((ticket) => (
                            <div 
                              key={ticket.id}
                              style={{
                                padding: '0.5rem 1rem',
                                background: ticket.is_winner ? '#2ECC71' : 'white',
                                color: ticket.is_winner ? 'white' : '#2C3E50',
                                border: ticket.is_winner ? '2px solid #27AE60' : '2px solid #E0E0E0',
                                borderRadius: '8px',
                                fontWeight: 'bold',
                                fontSize: '1.1rem',
                                position: 'relative'
                              }}
                            >
                              {ticket.number}
                              {ticket.is_winner && (
                                <span style={{
                                  position: 'absolute',
                                  top: '-8px',
                                  right: '-8px',
                                  fontSize: '1.2rem'
                                }}>
                                  👑
                                </span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>

                      <div style={{
                        display: 'flex',
                        justifyContent: 'flex-end',
                        alignItems: 'center',
                        paddingTop: '1rem',
                        borderTop: '1px solid #E0E0E0'
                      }}>
                        <button 
                          className="btn-secondary"
                          onClick={() => navigate(`/raffle/${group.raffle_id}`)}
                        >
                          Ver detalle de rifa
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab de Rifas Ganadas */}
      {activeTab === 'won' && (
        <div className="tab-content active">
          <div className="guidance-text" style={{color: 'white'}}>
            ¡Celebra tus victorias! Aquí aparecerán todas las rifas que has ganado.
          </div>

          {wonRaffles.length === 0 ? (
            <div style={{
              background: 'white',
              borderRadius: '12px',
              padding: '3rem',
              textAlign: 'center',
              marginTop: '2rem'
            }}>
              <div style={{fontSize: '3rem', marginBottom: '1rem'}}>🎯</div>
              <h3 style={{marginBottom: '0.5rem'}}>Aún no has ganado ninguna rifa</h3>
              <p style={{color: '#666', marginBottom: '1.5rem'}}>
                ¡No te desanimes! Sigue participando y tu momento llegará.
              </p>
              <button 
                className="btn-primary"
                onClick={() => navigate('/')}
              >
                Seguir participando
              </button>
            </div>
          ) : (
            <div style={{marginTop: '2rem'}}>
              {wonRaffles.map((ticket) => (
                <div 
                  key={ticket.id}
                  style={{
                    background: 'linear-gradient(135deg, #2ECC71 0%, #27AE60 100%)',
                    borderRadius: '12px',
                    padding: '2rem',
                    marginBottom: '1.5rem',
                    boxShadow: '0 8px 20px rgba(46, 204, 113, 0.3)',
                    color: 'white',
                    position: 'relative',
                    overflow: 'hidden'
                  }}
                >
                  <div style={{
                    position: 'absolute',
                    top: '-20px',
                    right: '-20px',
                    fontSize: '8rem',
                    opacity: '0.1'
                  }}>
                    🏆
                  </div>

                  <div style={{position: 'relative', zIndex: 1}}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '1rem',
                      marginBottom: '1rem'
                    }}>
                      <div style={{fontSize: '3rem'}}>
                        {getRifaIcon(ticket.raffle_name)}
                      </div>
                      <div>
                        <h3 style={{fontSize: '1.5rem', marginBottom: '0.25rem'}}>
                          ¡GANASTE!
                        </h3>
                        <div style={{fontSize: '1.2rem', fontWeight: '600'}}>
                          {ticket.raffle_name}
                        </div>
                      </div>
                    </div>

                    <div style={{
                      background: 'rgba(255,255,255,0.2)',
                      padding: '1rem',
                      borderRadius: '8px',
                      marginBottom: '1rem'
                    }}>
                      <div style={{marginBottom: '0.5rem'}}>
                        <strong>Tu número ganador:</strong> {ticket.number}
                      </div>
                      <div>
                        <strong>Fecha de compra:</strong> {new Date(ticket.created_at).toLocaleDateString('es-ES', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </div>
                    </div>

                    <button 
                      className="btn-secondary"
                      style={{
                        background: 'white',
                        color: '#27AE60',
                        border: 'none'
                      }}
                      onClick={() => navigate(`/raffle/${ticket.raffle_id}`)}
                    >
                      Ver detalles de la rifa
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default MyNumbers;