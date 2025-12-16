import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import ReactMarkdown from 'react-markdown';

function Header() {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout, isAdmin, isLoading } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [isSendingMessage, setIsSendingMessage] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);

  const handleNavigate = path => {
    navigate(path);
    setMobileMenuOpen(false); // Cerrar menú móvil al navegar
  };

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

  // Mostrar loading si aún se está verificando la autenticación
  if (isLoading) {
    return (
      <div className="header">
        <div className="header-content">
          <div className="logo" onClick={() => handleNavigate('/')}>
            🎰 RifaPlus
          </div>
          <div style={{ color: 'white', fontSize: '0.9rem' }}>Cargando...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="header">
      <div className="header-content">
        {/* Logo */}
        <div className="logo" onClick={() => handleNavigate('/')}>
          🎰 RifaPlus
        </div>

        {/* Botón hamburguesa para móvil */}
        <button
          className="mobile-menu-btn"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle menu"
        >
          <span className={`hamburger ${mobileMenuOpen ? 'open' : ''}`}>
            <span></span>
            <span></span>
            <span></span>
          </span>
        </button>

        {/* Menú de navegación */}
        <div className={`nav-menu ${mobileMenuOpen ? 'mobile-open' : ''}`}>
          <div className="nav-item active" onClick={() => handleNavigate('/')}>
            Descubre rifas
          </div>

          {/* Buscar usuarios - Disponible para todos */}
          <div className="nav-item" onClick={() => handleNavigate('/search-users')}>
            👥 Usuarios
          </div>

          {/* Menú solo para usuarios autenticados */}
          {isAuthenticated && (
            <>
              <div className="nav-item" onClick={() => handleNavigate('/my-numbers')}>
                🔢 Mis números
              </div>
              <div className="nav-item" onClick={() => handleNavigate('/create-raffle')}>
                🏆 Lanza tu rifa
              </div>
            </>
          )}
          {/* Botón Asistente Virtual */}
          <button
            className="btn-primary"
            onClick={() => setIsChatOpen(true)}
            style={{ marginLeft: '0.5rem' }}
          >
            💬 Asistente
          </button>
          {/* Configuración (solo para administradores) */}
          {isAuthenticated && isAdmin && (
            <div className="nav-item" onClick={() => handleNavigate('/config')}>
              ⚙️ Configuración
            </div>
          )}

          {/* Sección de autenticación - Botón Entrar O Menú de usuario */}
          {!isAuthenticated ? (
            // Usuario no autenticado - Mostrar botón Entrar
            <div id="nav-auth">
              <button className="btn-primary" onClick={() => handleNavigate('/auth')}>
                Entrar
              </button>
            </div>
          ) : (
            // Usuario autenticado - Mostrar menú de usuario
            <div id="nav-user">
              <div className="nav-item" onClick={() => handleNavigate(`/user/${user?.id}`)}>
                👤 {user?.first_name || 'Mi perfil'}
              </div>
              <button
                className="btn-secondary"
                onClick={() => {
                  logout();
                  handleNavigate('/');
                }}
              >
                Salir
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Modal de Chat */}
      {isChatOpen && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 1000,
          }}
          onClick={() => setIsChatOpen(false)}
        >
          <div 
            style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              width: '90%',
              maxWidth: '500px',
              maxHeight: '600px',
              display: 'flex',
              flexDirection: 'column',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
            }}
            onClick={e => e.stopPropagation()}
          >
            {/* Header del chat */}
            <div style={{
              padding: '1rem 1.5rem',
              backgroundColor: '#6A4C93',
              color: 'white',
              borderTopLeftRadius: '12px',
              borderTopRightRadius: '12px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}>
              <h3 style={{ margin: 0, fontSize: '1.1rem' }}>💬 Asistente Virtual</h3>
              <button
                onClick={() => setIsChatOpen(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'white',
                  fontSize: '1.5rem',
                  cursor: 'pointer',
                  padding: '0',
                  lineHeight: 1,
                }}
              >
                ×
              </button>
            </div>

            {/* Mensajes del chat */}
            <div style={{
              flex: 1,
              overflowY: 'auto',
              padding: '1rem',
              backgroundColor: '#f9f9f9',
            }}>
              {chatMessages.length === 0 ? (
                <div style={{ 
                  textAlign: 'center', 
                  color: '#666', 
                  marginTop: '2rem',
                  fontSize: '0.95rem',
                }}>
                  👋 ¡Hola! Soy tu asistente virtual.<br/>
                  ¿En qué puedo ayudarte hoy?
                </div>
              ) : (
                chatMessages.map((msg, index) => (
                  <div
                    key={index}
                    style={{
                      marginBottom: '1rem',
                      display: 'flex',
                      justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                    }}
                  >
                    <div
                      style={{
                        maxWidth: '70%',
                        padding: '0.75rem 1rem',
                        borderRadius: '12px',
                        backgroundColor: msg.role === 'user' ? '#6A4C93' : '#e9ecef',
                        color: msg.role === 'user' ? 'white' : '#333',
                        fontSize: '0.95rem',
                        lineHeight: 1.4,
                      }}
                    >
                      {msg.role === 'user' ? (
                        msg.content
                      ) : (
                        <ReactMarkdown
                          components={{
                            strong: ({children}) => <strong style={{fontWeight: 'bold'}}>{children}</strong>,
                            ul: ({children}) => <ul style={{margin: '0.5rem 0', paddingLeft: '1.5rem'}}>{children}</ul>,
                            ol: ({children}) => <ol style={{margin: '0.5rem 0', paddingLeft: '1.5rem'}}>{children}</ol>,
                            li: ({children}) => <li style={{marginBottom: '0.25rem'}}>{children}</li>,
                            p: ({children}) => <p style={{margin: '0.5rem 0'}}>{children}</p>,
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      )}
                    </div>
                  </div>
                ))
              )}
              {isSendingMessage && (
                <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                  <div
                    style={{
                      padding: '0.75rem 1rem',
                      borderRadius: '12px',
                      backgroundColor: '#e9ecef',
                      color: '#666',
                      fontSize: '0.95rem',
                    }}
                  >
                    Escribiendo...
                  </div>
                </div>
              )}
            </div>

            {/* Input del chat */}
            <div style={{
              padding: '1rem',
              borderTop: '1px solid #e0e0e0',
              backgroundColor: 'white',
              borderBottomLeftRadius: '12px',
              borderBottomRightRadius: '12px',
            }}>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <input
                  type="text"
                  className="form-input"
                  placeholder="Escribe tu mensaje..."
                  value={chatInput}
                  onChange={e => setChatInput(e.target.value)}
                  onKeyPress={e => e.key === 'Enter' && sendChatMessage()}
                  disabled={isSendingMessage}
                  style={{
                    flex: 1,
                    margin: 0,
                  }}
                />
                <button
                  className="btn-primary"
                  onClick={sendChatMessage}
                  disabled={!chatInput.trim() || isSendingMessage}
                  style={{
                    padding: '0.75rem 1.25rem',
                    minWidth: 'auto',
                  }}
                >
                  {isSendingMessage ? '⏳' : '📤'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Header;
