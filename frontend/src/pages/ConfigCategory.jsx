import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { apiClient } from '../services/authService';

function ConfigCategory() {
  const { categoryId } = useParams();
  const navigate = useNavigate();
  const { isAdmin } = useAuth();

  const [selectedEntity, setSelectedEntity] = useState(null);
  const [entities, setEntities] = useState([]);
  const [items, setItems] = useState([]);
  const [filteredItems, setFilteredItems] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState('create'); // 'create' | 'edit'
  const [currentItem, setCurrentItem] = useState(null);
  const [formData, setFormData] = useState({});
  const [foreignKeyData, setForeignKeyData] = useState({});
  const [message, setMessage] = useState({ text: '', type: '', show: false });

  // Catálogo de entidades (igual que en Config.jsx)
  const catalogEntities = {
    location: {
      name: '📍 Ubicaciones',
      entities: [
        { 
          id: 'countries', 
          name: 'Países', 
          endpoint: '/location/countries/',
          fields: [
            { name: 'country_name', label: 'Nombre del País', type: 'text', required: true },
            { name: 'country_code', label: 'Código', type: 'text', required: true }
          ],
          displayField: 'country_name'
        },
        { 
          id: 'states', 
          name: 'Estados/Departamentos', 
          endpoint: '/location/states/',
          fields: [
            { name: 'state_name', label: 'Nombre del Estado', type: 'text', required: true },
            { name: 'state_code', label: 'Código', type: 'text', required: true },
            { 
              name: 'country_id', 
              label: 'País', 
              type: 'select', 
              required: true, 
              foreignKey: { endpoint: '/location/countries/', display: 'country_name' },
              displayField: 'state_country' // Campo que viene en la respuesta GET
            }
          ],
          displayField: 'state_name'
        },
        { 
          id: 'cities', 
          name: 'Ciudades', 
          endpoint: '/location/cities/',
          fields: [
            { name: 'city_name', label: 'Nombre de la Ciudad', type: 'text', required: true },
            { name: 'city_code', label: 'Código', type: 'text', required: true },
            { 
              name: 'state_id', 
              label: 'Estado/Departamento', 
              type: 'select', 
              required: true, 
              foreignKey: { endpoint: '/location/states/', display: 'state_name' },
              displayField: 'city_state' // Campo que viene en la respuesta GET
            }
          ],
          displayField: 'city_name'
        }
      ]
    },
    userInfo: {
      name: '👤 Información de Usuarios',
      entities: [
        { 
          id: 'document-types', 
          name: 'Tipos de Documento', 
          endpoint: '/user-info/document-types/',
          fields: [
            { name: 'document_type_name', label: 'Nombre', type: 'text', required: true },
            { name: 'document_type_code', label: 'Código', type: 'text', required: true }
          ],
          displayField: 'document_type_name'
        },
        { 
          id: 'genders', 
          name: 'Géneros', 
          endpoint: '/user-info/genders/',
          fields: [
            { name: 'gender_name', label: 'Nombre', type: 'text', required: true },
            { name: 'gender_code', label: 'Código', type: 'text', required: true }
          ],
          displayField: 'gender_name'
        },
        { 
          id: 'payment-method-types', 
          name: 'Tipos de Método de Pago', 
          endpoint: '/user-info/payment-method-types/',
          fields: [
            { name: 'payment_method_type_name', label: 'Nombre', type: 'text', required: true },
            { name: 'payment_method_type_code', label: 'Código', type: 'text', required: true }
          ],
          displayField: 'payment_method_type_name'
        }
      ]
    },
    raffleInfo: {
      name: '🎰 Información de Rifas',
      entities: [
        { 
          id: 'prize-types', 
          name: 'Tipos de Premio', 
          endpoint: '/raffle-info/prizetype/',
          fields: [
            { name: 'prize_type_name', label: 'Nombre', type: 'text', required: true },
            { name: 'prize_type_code', label: 'Código', type: 'text', required: true }
          ],
          displayField: 'prize_type_name'
        },
        { 
          id: 'state-raffles', 
          name: 'Estados de Rifa', 
          endpoint: '/raffle-info/stateraffle/',
          fields: [
            { name: 'state_raffle_name', label: 'Nombre', type: 'text', required: true },
            { name: 'state_raffle_code', label: 'Código', type: 'text', required: true }
          ],
          displayField: 'state_raffle_name'
        }
      ]
    }
  };

  const category = catalogEntities[categoryId];

  useEffect(() => {
    if (category) {
      setEntities(category.entities);
      // Seleccionar la primera entidad por defecto
      if (category.entities.length > 0) {
        selectEntity(category.entities[0]);
      }
    }
  }, [categoryId]);

  const showMessage = (text, type) => {
    setMessage({ text, type, show: true });
    setTimeout(() => {
      setMessage({ text: '', type: '', show: false });
    }, 4000);
  };

  const selectEntity = async (entity) => {
    setSelectedEntity(entity);
    await fetchItems(entity);
    
    // Cargar datos de foreign keys si existen
    const fkData = {};
    for (const field of entity.fields) {
      if (field.foreignKey) {
        try {
          const response = await apiClient.get(field.foreignKey.endpoint);
          fkData[field.name] = response.data.results || response.data || [];
        } catch (error) {
          console.error(`Error cargando ${field.name}:`, error);
        }
      }
    }
    setForeignKeyData(fkData);
  };

  const fetchItems = async (entity) => {
    setLoading(true);
    try {
      const response = await apiClient.get(entity.endpoint);
      const data = response.data.results || response.data || [];
      setItems(data);
      setFilteredItems(data);
      setSearchTerm('');
    } catch (error) {
      console.error('Error cargando items:', error);
      showMessage('Error al cargar los datos', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Filtrar items cuando cambia el término de búsqueda
  useEffect(() => {
    if (!searchTerm.trim()) {
      setFilteredItems(items);
      return;
    }

    const term = searchTerm.toLowerCase();
    const filtered = items.filter(item => {
      // Buscar en ID
      if (item.id?.toString().includes(term)) return true;

      // Buscar en todos los campos de texto de la entidad
      return selectedEntity?.fields.some(field => {
        if (field.type === 'text') {
          const value = item[field.name];
          return value && value.toString().toLowerCase().includes(term);
        }
        return false;
      });
    });

    setFilteredItems(filtered);
  }, [searchTerm, items, selectedEntity]);

  const handleCreate = () => {
    setModalMode('create');
    setCurrentItem(null);
    const initialData = {};
    selectedEntity.fields.forEach(field => {
      initialData[field.name] = '';
    });
    setFormData(initialData);
    setShowModal(true);
  };

  const handleEdit = (item) => {
    setModalMode('edit');
    setCurrentItem(item);
    const editData = {};
    selectedEntity.fields.forEach(field => {
      if (field.type === 'select') {
        // Para campos select, buscar en displayField si existe
        const fieldToRead = field.displayField || field.name;
        const value = item[fieldToRead];
        editData[field.name] = (typeof value === 'object' ? value?.id : value) || '';
      } else {
        editData[field.name] = item[field.name] || '';
      }
    });
    setFormData(editData);
    setShowModal(true);
  };

  const handleDelete = async (item) => {
    if (!window.confirm(`¿Estás seguro de eliminar "${item[selectedEntity.displayField]}"?`)) {
      return;
    }

    setLoading(true);
    try {
      await apiClient.delete(`${selectedEntity.endpoint}${item.id}/`);
      showMessage('✅ Eliminado correctamente', 'success');
      await fetchItems(selectedEntity);
    } catch (error) {
      console.error('Error eliminando:', error);
      showMessage(error.response?.data?.detail || 'Error al eliminar', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Convertir foreign keys a números
      const dataToSend = {...formData};
      selectedEntity.fields.forEach(field => {
        if (field.type === 'select' && dataToSend[field.name]) {
          dataToSend[field.name] = parseInt(dataToSend[field.name]);
        }
      });

      console.log('Datos a enviar:', dataToSend);

      if (modalMode === 'create') {
        await apiClient.post(selectedEntity.endpoint, dataToSend);
        showMessage('✅ Creado correctamente', 'success');
      } else {
        await apiClient.put(`${selectedEntity.endpoint}${currentItem.id}/`, dataToSend);
        showMessage('✅ Actualizado correctamente', 'success');
      }
      setShowModal(false);
      await fetchItems(selectedEntity);
    } catch (error) {
      console.error('Error guardando:', error);
      console.error('Respuesta del servidor:', error.response?.data);
      
      // Mostrar errores de validación específicos
      let errorMsg = 'Error al guardar';
      if (error.response?.data) {
        const errorData = error.response.data;
        if (typeof errorData === 'object') {
          // Concatenar todos los errores de validación
          errorMsg = Object.entries(errorData)
            .map(([field, errors]) => `${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`)
            .join('\n');
        } else {
          errorMsg = errorData.detail || errorData.message || String(errorData);
        }
      }
      showMessage(errorMsg, 'error');
    } finally {
      setLoading(false);
    }
  };

  if (!isAdmin) {
    return (
      <div className="module-container active">
        <div className="message error show">⚠️ No tienes permisos</div>
        <button className="btn-secondary" onClick={() => navigate('/')}>← Volver</button>
      </div>
    );
  }

  if (!category) {
    return (
      <div className="module-container active">
        <div className="message error show">Categoría no encontrada</div>
        <button className="btn-secondary" onClick={() => navigate('/config')}>← Volver</button>
      </div>
    );
  }

  return (
    <div className="module-container active">
      <div className="breadcrumbs">
        <div className="breadcrumb-item" onClick={() => navigate('/')}>Inicio</div>
        <div className="breadcrumb-separator">&gt;</div>
        <div className="breadcrumb-item" onClick={() => navigate('/config')}>Configuración</div>
        <div className="breadcrumb-separator">&gt;</div>
        <div className="breadcrumb-item">{category.name}</div>
      </div>

      <h1 style={{ color: 'white', textAlign: 'center' }}>{category.name}</h1>

      {message.show && (
        <div className={`message ${message.type} show`}>{message.text}</div>
      )}

      <div className="config-layout">
        {/* Sidebar con lista de entidades */}
        <div className="config-sidebar">
          <h3 style={{ color: 'white', marginTop: 0 }}>Entidades</h3>
          <div className="config-entities-list">
            {entities.map(entity => (
              <div
                key={entity.id}
                className={`config-entity-item ${selectedEntity?.id === entity.id ? 'active' : ''}`}
                onClick={() => selectEntity(entity)}
              >
                {entity.name}
              </div>
            ))}
          </div>
        </div>

        {/* Contenido principal */}
        <div>
          {selectedEntity && (
            <>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                marginBottom: '1.5rem'
              }}>
                <h2 style={{ color: 'white', margin: 0 }}>{selectedEntity.name}</h2>
                <button className="btn-secondary" onClick={handleCreate}>
                  ➕ Crear nuevo
                </button>
              </div>

              {/* Buscador */}
              {items.length > 0 && (
                <div style={{ marginBottom: '1rem' }}>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="🔍 Buscar por nombre, código o ID..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      fontSize: '0.95rem',
                      background: 'rgba(255,255,255,0.3)',
                      border: '1px solid rgba(255,255,255,0.9)',
                      borderRadius: '8px',
                      color: 'white'
                    }}
                  />
                  {searchTerm && (
                    <div style={{ 
                      marginTop: '0.5rem', 
                      color: '#999', 
                      fontSize: '0.85rem' 
                    }}>
                      {filteredItems.length} resultado{filteredItems.length !== 1 ? 's' : ''} encontrado{filteredItems.length !== 1 ? 's' : ''}
                    </div>
                  )}
                </div>
              )}

              {loading ? (
                <div style={{ textAlign: 'center', color: 'white', padding: '2rem' }}>
                  Cargando...
                </div>
              ) : items.length === 0 ? (
                <div style={{ 
                  textAlign: 'center', 
                  color: '#666', 
                  padding: '3rem',
                  background: 'rgba(255,255,255,0.05)',
                  borderRadius: '12px'
                }}>
                  <p style={{ fontSize: '3rem', margin: '0 0 1rem 0' }}>📭</p>
                  <p>No hay registros aún</p>
                  <button className="btn-secondary" onClick={handleCreate} style={{ marginTop: '1rem' }}>
                    Crear el primero
                  </button>
                </div>
              ) : (
                <div className="config-table-wrapper">
                  <table className="config-table">
                    <thead>
                      <tr>
                        <th>ID</th>
                        {selectedEntity.fields.map(field => (
                          <th key={field.name}>{field.label}</th>
                        ))}
                        <th style={{ textAlign: 'center' }}>Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredItems.length === 0 ? (
                        <tr>
                          <td colSpan={selectedEntity.fields.length + 2} style={{ textAlign: 'center', padding: '2rem', color: '#999' }}>
                            {searchTerm ? '❌ No se encontraron resultados' : '📭 No hay registros'}
                          </td>
                        </tr>
                      ) : (
                        filteredItems.map(item => (
                          <tr key={item.id}>
                            <td>{item.id}</td>
                            {selectedEntity.fields.map(field => {
                              // Para campos select, usar displayField si existe, sino usar field.name
                              const fieldToDisplay = field.type === 'select' && field.displayField 
                                ? field.displayField 
                                : field.name;
                              
                              const value = item[fieldToDisplay];
                              
                              return (
                                <td key={field.name}>
                                  {field.type === 'select' && typeof value === 'object' 
                                    ? value?.[field.foreignKey.display] 
                                    : value}
                                </td>
                              );
                            })}
                            <td>
                              <div className="config-table-actions">
                                <button 
                                  className="btn-edit"
                                  onClick={() => handleEdit(item)}
                                >
                                  ✏️ Editar
                                </button>
                                <button 
                                  className="btn-delete"
                                  onClick={() => handleDelete(item)}
                                >
                                  🗑️ Eliminar
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Modal para crear/editar */}
      {showModal && (
        <div 
          className="config-modal"
          onClick={() => setShowModal(false)}
        >
          <div 
            className="form-container"
            onClick={(e) => e.stopPropagation()}
            style={{ margin: 0, maxWidth: '500px', maxHeight: '80vh', overflow: 'auto' }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3>{modalMode === 'create' ? 'Crear' : 'Editar'} {selectedEntity?.name}</h3>
              <button 
                onClick={() => setShowModal(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '1.5rem',
                  cursor: 'pointer',
                  color: '#666'
                }}
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              {selectedEntity?.fields.map(field => (
                <div key={field.name} className="form-group">
                  <label className="form-label">
                    {field.label} {field.required && '*'}
                  </label>
                  {field.type === 'select' ? (
                    <select
                      className="form-input"
                      value={formData[field.name] || ''}
                      onChange={(e) => setFormData({...formData, [field.name]: e.target.value})}
                      required={field.required}
                    >
                      <option value="">Selecciona...</option>
                      {(foreignKeyData[field.name] || []).map(option => (
                        <option key={option.id} value={option.id}>
                          {option[field.foreignKey.display]}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <input
                      type={field.type}
                      className="form-input"
                      value={formData[field.name] || ''}
                      onChange={(e) => setFormData({...formData, [field.name]: e.target.value})}
                      required={field.required}
                      placeholder={field.label}
                    />
                  )}
                </div>
              ))}

              <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
                <button 
                  type="button" 
                  className="btn-secondary"
                  onClick={() => setShowModal(false)}
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
                  {loading ? 'Guardando...' : 'Guardar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <button 
        className="btn-secondary" 
        onClick={() => navigate('/config')} 
        style={{ marginTop: '2rem' }}
      >
        ← Volver a configuración
      </button>
    </div>
  );
}

export default ConfigCategory;
