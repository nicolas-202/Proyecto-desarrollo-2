import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function Config() {
  const navigate = useNavigate();
  const { isAdmin } = useAuth();
  const [selectedCategory, setSelectedCategory] = useState(null);

  // Si no es admin, redirigir o mostrar error
  if (!isAdmin) {
    return (
      <div className="module-container active">
        <div className="message error show">
          ⚠️ No tienes permisos para acceder a esta página
        </div>
        <button className="btn-secondary" onClick={() => navigate('/')}>
          ← Volver al inicio
        </button>
      </div>
    );
  }

  // Catálogo de entidades organizadas por categorías
  const catalogEntities = [
    {
      id: 'location',
      name: '📍 Ubicaciones',
      description: 'Gestiona países, estados y ciudades',
      icon: '🌎',
      entities: [
        { 
          id: 'countries', 
          name: 'Países', 
          endpoint: '/location/countries/',
          fields: ['country_name', 'country_code'],
          displayField: 'country_name'
        },
        { 
          id: 'states', 
          name: 'Estados/Departamentos', 
          endpoint: '/location/states/',
          fields: ['state_name', 'state_code', 'country'],
          displayField: 'state_name',
          foreignKeys: { country: { endpoint: '/location/countries/', display: 'country_name' } }
        },
        { 
          id: 'cities', 
          name: 'Ciudades', 
          endpoint: '/location/cities/',
          fields: ['city_name', 'city_code', 'state'],
          displayField: 'city_name',
          foreignKeys: { state: { endpoint: '/location/states/', display: 'state_name' } }
        }
      ]
    },
    {
      id: 'userInfo',
      name: '👤 Información de Usuarios',
      description: 'Gestiona tipos de documento, géneros y métodos de pago',
      icon: '📋',
      entities: [
        { 
          id: 'document-types', 
          name: 'Tipos de Documento', 
          endpoint: '/user-info/document-types/',
          fields: ['document_type_name', 'document_type_code'],
          displayField: 'document_type_name'
        },
        { 
          id: 'genders', 
          name: 'Géneros', 
          endpoint: '/user-info/genders/',
          fields: ['gender_name', 'gender_code'],
          displayField: 'gender_name'
        },
        { 
          id: 'payment-method-types', 
          name: 'Tipos de Método de Pago', 
          endpoint: '/user-info/payment-method-types/',
          fields: ['payment_method_type_name', 'payment_method_type_code'],
          displayField: 'payment_method_type_name'
        }
      ]
    },
    {
      id: 'raffleInfo',
      name: '🎰 Información de Rifas',
      description: 'Gestiona tipos de premio y estados de rifas',
      icon: '🎟️',
      entities: [
        { 
          id: 'prize-types', 
          name: 'Tipos de Premio', 
          endpoint: '/raffle-info/prizetype/',
          fields: ['prize_type_name', 'prize_type_code'],
          displayField: 'prize_type_name'
        },
        { 
          id: 'state-raffles', 
          name: 'Estados de Rifa', 
          endpoint: '/raffle-info/stateraffle/',
          fields: ['state_raffle_name', 'state_raffle_code'],
          displayField: 'state_raffle_name'
        }
      ]
    }
  ];

  return (
    <div className="module-container active">
      {/* Breadcrumbs */}
      <div className="breadcrumbs">
        <div className="breadcrumb-item" onClick={() => navigate('/')}>Inicio</div>
        <div className="breadcrumb-separator">&gt;</div>
        <div className="breadcrumb-item">Configuración</div>
      </div>

      <h1 style={{ textAlign: 'center', color: 'white', marginBottom: '1rem' }}>
        ⚙️ Panel de Configuración
      </h1>
      
      <div className="guidance-text" style={{ color: 'white', textAlign: 'center' }}>
        Administra las entidades del sistema. Selecciona una categoría para ver sus entidades.
      </div>

      {/* Grid de categorías */}
      <div className="config-grid">
        {catalogEntities.map(category => (
          <div
            key={category.id}
            className="rifa-card"
            onClick={() => navigate(`/config/${category.id}`)}
            style={{
              cursor: 'pointer',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              border: 'none',
              transition: 'transform 0.2s ease',
            }}
            onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
            onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
          >
            <div style={{
              fontSize: '4rem',
              textAlign: 'center',
              marginBottom: '1rem'
            }}>
              {category.icon}
            </div>
            <h3 style={{ 
              color: 'white', 
              textAlign: 'center', 
              marginBottom: '0.5rem',
              fontSize: '1.3rem'
            }}>
              {category.name}
            </h3>
            <p style={{
              color: 'rgba(255,255,255,0.9)',
              textAlign: 'center',
              fontSize: '0.95rem'
            }}>
              {category.description}
            </p>
            <div style={{
              marginTop: '1rem',
              padding: '0.75rem',
              background: 'rgba(255,255,255,0.2)',
              borderRadius: '8px',
              textAlign: 'center',
              color: 'white',
              fontWeight: 'bold'
            }}>
              {category.entities.length} {category.entities.length === 1 ? 'entidad' : 'entidades'}
            </div>
          </div>
        ))}
      </div>

      {/* Botón volver */}
      <button 
        className="btn-secondary" 
        onClick={() => navigate('/')} 
        style={{ marginTop: '2rem', width: '100%', maxWidth: '300px', margin: '2rem auto 0', display: 'block' }}
      >
        ← Volver al inicio
      </button>
    </div>
  );
}

export default Config;
