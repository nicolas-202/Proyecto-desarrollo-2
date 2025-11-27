import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { apiClient } from '../services/authService';

function BuyNumbers(){
    // Hooks para obtener parámetros de la URL y navegación
    const { rifaId } = useParams();
    const navigate = useNavigate();
    const { user, isAuthenticated, isLoading: authLoading } = useAuth();

    // Estados para los datos de la página
    const [rifa, setRifa] = useState(null);
    const [availableNumbers, setAvailableNumbers] = useState([]);
    const [selectedNumbers, setSelectedNumbers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [paymentMethods, setPaymentMethods] = useState([]);
    const [selectedPaymentMethod, setSelectedPaymentMethod] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                // Usar rifaId real en las URLs
                const[rifaResponse, availableNumbersResponse] = await Promise.all([
                    apiClient.get(`/raffle/${rifaId}/`),
                    apiClient.get(`/raffle/${rifaId}/available/`)
                ]);
                setRifa(rifaResponse.data);
                // Si la respuesta tiene .numbers, usar ese campo
                if (Array.isArray(availableNumbersResponse.data)) {
                    setAvailableNumbers(availableNumbersResponse.data);
                } else if (Array.isArray(availableNumbersResponse.data.numbers)) {
                    setAvailableNumbers(availableNumbersResponse.data.numbers);
                } else {
                    setAvailableNumbers([]);
                }
            } catch (err) {
                console.error('Error cargando datos:', err);
                setError('Error al cargar la información de la rifa');
            } finally {
                setLoading(false);
            }
        };

        // Solo cargar datos si tenemos rifaId y auth está listo
        if (rifaId && !authLoading) {
            fetchData();
        }
    }, [rifaId, authLoading]);

    // Cargar métodos de pago del usuario
    useEffect(() => {
        const fetchPaymentMethods = async () => {
            if (!user?.id) return;
            try {
                const response = await apiClient.get(`/user-info/payment-methods/${user.id}/`);
                console.log('Respuesta métodos de pago:', response.data);
                let arr = [];
                if (Array.isArray(response.data)) {
                    arr = response.data;
                } else if (Array.isArray(response.data.results)) {
                    arr = response.data.results;
                } else if (typeof response.data === 'object' && response.data !== null) {
                    arr = [response.data];
                }
                setPaymentMethods(arr);
                if (arr.length === 1) {
                    setSelectedPaymentMethod(arr[0].id);
                }
                console.log('Métodos de pago en estado:', arr);
            } catch (err) {
                console.error('Error cargando métodos de pago:', err);
                setPaymentMethods([]);
            }
        };
        if (isAuthenticated) {
            fetchPaymentMethods();
        }
    }, [user, isAuthenticated]);

    // Función para recargar datos después de una compra exitosa
    const reloadRaffleData = async () => {
        try {
            const [rifaResponse, availableNumbersResponse] = await Promise.all([
                apiClient.get(`/raffle/${rifaId}/`),
                apiClient.get(`/raffle/${rifaId}/available/`)
            ]);
            
            setRifa(rifaResponse.data);
            setAvailableNumbers(availableNumbersResponse.data);
        } catch (error) {
            console.error('Error recargando datos:', error);
        }
    };

    // Función para manejar clic en números
    const handleNumberClick = (number, isAvailable) => {
        // Si el número no está disponible (ya vendido), no hacer nada
        if (!isAvailable) {
            return;
        }

        // Si el usuario no está autenticado, redirigir a login
        if (!isAuthenticated) {
            navigate('/auth');
            return;
        }

        // Toggle: si ya está seleccionado, lo quitamos; si no, lo agregamos
        setSelectedNumbers(prev => {
            const isAlreadySelected = prev.includes(number);
            
            if (isAlreadySelected) {
                // Quitar número de la selección
                return prev.filter(n => n !== number);
            } else {
                // Agregar número a la selección
                return [...prev, number];
            }
        });
    };

    // Función para manejar la compra de números
    const handlePurchase = async () => {
        if (selectedNumbers.length === 0) {
            alert('Selecciona al menos un número para comprar');
            return;
        }
        if (!selectedPaymentMethod) {
            alert('Selecciona un método de pago');
            return;
        }
        const precio = Number(rifa.raffle_number_price);
        const confirmMessage = `¿Confirmas la compra de ${selectedNumbers.length} número(s) por $${(selectedNumbers.length * precio).toLocaleString()}?`;
        if (window.confirm(confirmMessage)) {
            setLoading(true);
            let exitos = 0;
            let fallos = 0;
            for (const num of selectedNumbers) {
                try {
                    const purchaseData = {
                        raffle_id: rifa.id,
                        number: num,
                        payment_method_id: selectedPaymentMethod,
                        total_amount: precio,
                        quantity: 1
                    };
                    const response = await apiClient.post(`/tickets/purchase/`, purchaseData);
                    if (response.data) {
                        exitos++;
                    }
                } catch (error) {
                    fallos++;
                    console.error(`Error comprando el número ${num}:`, error);
                }
            }
            let mensaje = '';
            if (exitos > 0) mensaje += `¡Compra realizada de ${exitos} número(s)! 🎉\n`;
            if (fallos > 0) mensaje += `${fallos} número(s) no se pudieron comprar.`;
            alert(mensaje);
            setSelectedNumbers([]);
            await reloadRaffleData();
            setLoading(false);
        }
    };

    // Función para ejecutar el sorteo (solo admin)
    const handleExecuteDraw = async () => {
        if (!window.confirm('¿Estás seguro de ejecutar el sorteo? Esta acción no se puede deshacer.')) {
            return;
        }

        setLoading(true);
        try {
            const response = await apiClient.patch(`/raffle/${rifaId}/draw/`);
            
            // Mostrar resultado del sorteo
            const result = response.data;
            
            // Si ya fue sorteada
            if (result.is_already_drawn && result.winner_info) {
                const winner = result.winner_info;
                alert(
                    `Esta rifa ya fue sorteada anteriormente\n\n` +
                    `🏆 Ganador: ${winner.winner_name}\n` +
                    `📧 Email: ${winner.winner_email}\n` +
                    `📱 Teléfono: ${winner.winner_phone}\n` +
                    `🎯 Número ganador: ${winner.winning_number}\n` +
                    `💰 Premio: $${parseFloat(winner.prize_amount).toLocaleString()}\n` +
                    `🎁 Tipo: ${winner.prize_type}`
                );
            } 
            // Si se acaba de ejecutar el sorteo
            else if (result.message) {
                alert(
                    `¡SORTEO EJECUTADO! 🎉\n\n` +
                    `${result.message}\n\n` +
                    `🏆 Ganador: ${result.winner_user || 'N/A'}\n` +
                    `🎯 Número ganador: ${result.winner_number || 'N/A'}\n` +
                    `💰 Premio: $${result.prize_amount ? parseFloat(result.prize_amount).toLocaleString() : 'N/A'}\n` +
                    `🎁 Tipo: ${result.prize_type || 'N/A'}\n` +
                    `🎫 Números vendidos: ${result.tickets_sold || 'N/A'}\n` +
                    `💵 Ingresos totales: $${result.total_revenue ? parseFloat(result.total_revenue).toLocaleString() : 'N/A'}\n` +
                    `📊 Estado: ${result.raffle_status || 'N/A'}`
                );
            }

            // Recargar datos de la rifa
            await reloadRaffleData();
        } catch (error) {
            console.error('Error ejecutando sorteo:', error);
            const errorData = error.response?.data;
            
            let errorMessage = 'Error al ejecutar el sorteo';
            
            if (errorData?.error) {
                errorMessage = errorData.error;
                
                // Si incluye información del ganador en el error
                if (errorData.winner_info) {
                    const winner = errorData.winner_info;
                    errorMessage += `\n\n🏆 Información del ganador:\n` +
                        `Nombre: ${winner.winner_name}\n` +
                        `Número: ${winner.winning_number}\n` +
                        `Premio: $${parseFloat(winner.prize_amount).toLocaleString()}`;
                }
            }
            
            alert(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    // Función para editar/modificar rifa (creador o admin)
    const handleEditRaffle = () => {
        // TODO: Implementar página de edición de rifa
        alert('Función de edición en desarrollo. Próximamente podrás modificar tu rifa.');
        // navigate(`/edit-rifa/${rifaId}`);
    };

    // Verificar si el usuario es el creador de la rifa
    const isRaffleCreator = isAuthenticated && user?.id === rifa?.raffle_created_by?.id;
    
    // Verificar si el usuario es admin
    const isAdmin = isAuthenticated && (user?.is_staff || user?.is_admin);

    // Renderizado condicional para loading y errores
    console.log('RIFA:', rifa);
    console.log('AVAILABLE NUMBERS:', availableNumbers);
    // Aseguramos que availableNumbers sea un array
    const numbersArray = Array.isArray(availableNumbers) ? availableNumbers : [];
    if (authLoading || loading) {
        return (
            <div className="module-container active">
                <div style={{textAlign: 'center', color: 'white', fontSize: '1.2rem', marginTop: '3rem'}}>
                    Cargando información de la rifa... 🎰
                </div>
            </div>
        );
    }

    if (error || !rifa) {
        return (
            <div className="module-container active">
                <div className="message error show">
                    {error || 'Rifa no encontrada'}
                </div>
                <button className="btn-secondary" onClick={() => navigate('/')}>
                    ← Volver al inicio
                </button>
            </div>
        );
    }

    return (
        <div className="module-container active">
            {/* Breadcrumbs */}
            <div className="breadcrumbs">
                <div className="breadcrumb-item" onClick={() => navigate('/')}>Inicio</div>
                <div className="breadcrumb-separator">&gt;</div>
                <div className="breadcrumb-item">{rifa.raffle_name}</div>
            </div>

            {/* Botón volver */}
            <button className="btn-secondary" onClick={() => navigate('/')} style={{marginBottom: '1rem'}}>
                ← Volver a rifas
            </button>

            {/* Botones de administración (solo para creador o admin) */}
            {(isRaffleCreator || isAdmin) && (
                <div style={{
                    display: 'flex', 
                    gap: '1rem', 
                    marginBottom: '1rem',
                    flexWrap: 'wrap'
                }}>
                    {/* Botón para modificar rifa (creador o admin) */}
                    {(isRaffleCreator || isAdmin) && (
                        <button 
                            className="btn-secondary" 
                            onClick={handleEditRaffle}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem'
                            }}
                        >
                            ✏️ Modificar rifa
                        </button>
                    )}

                    {/* Botón para ejecutar sorteo (solo admin) */}
                    {isAdmin && rifa.raffle_state?.state_raffle_name === 'Activa' && (
                        <button 
                            className="btn-primary" 
                            onClick={handleExecuteDraw}
                            disabled={loading}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem',
                                background: 'linear-gradient(135deg, #2ECC71 0%, #27AE60 100%)'
                            }}
                        >
                            🎲 Ejecutar sorteo
                        </button>
                    )}
                </div>
            )}

            {/* Contenedor principal */}
            <div className="rifa-details">
                <h1>{rifa.raffle_name}</h1>
                
                {/* Mostrar información del ganador si la rifa ya fue sorteada */}
                {rifa.raffle_winner && (
                    <div style={{
                        background: 'linear-gradient(135deg, #2ECC71 0%, #27AE60 100%)',
                        borderRadius: '12px',
                        padding: '2rem',
                        marginTop: '1rem',
                        marginBottom: '2rem',
                        color: 'white',
                        boxShadow: '0 8px 20px rgba(46, 204, 113, 0.3)'
                    }}>
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '1rem',
                            marginBottom: '1rem'
                        }}>
                            <div style={{fontSize: '3rem'}}>🏆</div>
                            <div>
                                <h2 style={{margin: 0, fontSize: '1.8rem'}}>¡Rifa Sorteada!</h2>
                                <p style={{margin: '0.5rem 0 0 0', opacity: 0.9}}>
                                    Ya se realizó el sorteo de esta rifa
                                </p>
                            </div>
                        </div>
                        
                        <div style={{
                            background: 'rgba(255,255,255,0.2)',
                            padding: '1.5rem',
                            borderRadius: '8px'
                        }}>
                            <h3 style={{marginTop: 0, marginBottom: '1rem'}}>Información del Ganador</h3>
                            <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem'}}>
                                <div>
                                    <strong>👤 Nombre:</strong><br/>
                                    {rifa.raffle_winner.first_name} {rifa.raffle_winner.last_name}
                                </div>
                                <div>
                                    <strong>📧 Email:</strong><br/>
                                    {rifa.raffle_winner.email}
                                </div>
                                <div>
                                    <strong>📱 Teléfono:</strong><br/>
                                    {rifa.raffle_winner.phone_number || 'No disponible'}
                                </div>
                                <div>
                                    <strong>💰 Premio:</strong><br/>
                                    ${rifa.raffle_prize_amount?.toLocaleString()}
                                </div>
                            </div>
                            <div style={{
                                marginTop: '1rem',
                                padding: '1rem',
                                background: 'rgba(255,255,255,0.3)',
                                borderRadius: '8px',
                                textAlign: 'center'
                            }}>
                                <strong style={{fontSize: '1.2rem'}}>
                                    🎯 Tipo de premio: {rifa.raffle_prize_type?.prize_type_name}
                                </strong>
                            </div>
                        </div>
                    </div>
                )}

                {/* Mostrar mensaje de cancelación si la rifa está cancelada */}
                {rifa.raffle_state?.state_raffle_name === 'Cancelada' && (
                    <div style={{
                        background: 'linear-gradient(135deg, #E74C3C 0%, #C0392B 100%)',
                        borderRadius: '12px',
                        padding: '2rem',
                        marginTop: '1rem',
                        marginBottom: '2rem',
                        color: 'white',
                        boxShadow: '0 8px 20px rgba(231, 76, 60, 0.3)'
                    }}>
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '1rem',
                            marginBottom: '1rem'
                        }}>
                            <div style={{fontSize: '3rem'}}>❌</div>
                            <div>
                                <h2 style={{margin: 0, fontSize: '1.8rem'}}>Rifa Cancelada</h2>
                                <p style={{margin: '0.5rem 0 0 0', opacity: 0.9}}>
                                    Esta rifa ha sido cancelada
                                </p>
                            </div>
                        </div>
                        
                        <div style={{
                            background: 'rgba(255,255,255,0.2)',
                            padding: '1.5rem',
                            borderRadius: '8px'
                        }}>
                            <h3 style={{marginTop: 0, marginBottom: '1rem'}}>💰 Información de Reembolsos</h3>
                            <div style={{
                                background: 'rgba(255,255,255,0.3)',
                                padding: '1rem',
                                borderRadius: '8px',
                                marginBottom: '1rem'
                            }}>
                                <p style={{margin: '0.5rem 0', fontSize: '1.1rem'}}>
                                    ✅ <strong>Todos los tickets han sido reembolsados</strong>
                                </p>
                                <p style={{margin: '0.5rem 0', opacity: 0.9}}>
                                    Si compraste números en esta rifa, el dinero ya fue devuelto a tu método de pago.
                                </p>
                            </div>
                            
                            <div style={{
                                padding: '1rem',
                                background: 'rgba(255,255,255,0.15)',
                                borderRadius: '8px',
                                fontSize: '0.95rem'
                            }}>
                                <p style={{margin: '0.5rem 0'}}>
                                    📋 <strong>Motivo:</strong> Esta rifa fue cancelada por el organizador o por razones administrativas.
                                </p>
                                <p style={{margin: '0.5rem 0'}}>
                                    🔄 El reembolso se procesó automáticamente al momento de la cancelación.
                                </p>
                                <p style={{margin: '0.5rem 0'}}>
                                    💡 Puedes verificar tu saldo en la sección de métodos de pago.
                                </p>
                            </div>
                        </div>
                    </div>
                )}

                {/* Grid de información y números */}
                <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginTop: '2rem'}}>
                    {/* Información de la rifa */}
                    <div>
                        <h3>Información de la rifa</h3>
                        <p><strong>Descripción:</strong> {rifa.raffle_description}</p>
                        <p><strong>Premio:</strong> ${rifa.raffle_prize_amount?.toLocaleString()}</p>
                        <p><strong>Precio por número:</strong> ${rifa.raffle_number_price?.toLocaleString()}</p>
                        <p><strong>Total números:</strong> {rifa.raffle_number_amount}</p>
                        <p><strong>Números vendidos:</strong> {rifa.raffle_number_amount - numbersArray.length}</p>
                        <p><strong>Sorteo:</strong> {new Date(rifa.raffle_draw_date).toLocaleDateString('es-ES', {
                            year: 'numeric',
                            month: 'long', 
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                        })}</p>
                        <p><strong>Creada por:</strong> {rifa.raffle_created_by?.first_name} {rifa.raffle_created_by?.last_name}</p>
                    </div>

                    {/* Información de compra */}
                    <div>
                        <h3>Tu compra</h3>
                        {/* Select de métodos de pago */}
                        {isAuthenticated && (
                            <div className="form-group">
                                <label className="form-label">Selecciona método de pago</label>
                                <select
                                    className="form-input"
                                    value={selectedPaymentMethod}
                                    onChange={e => setSelectedPaymentMethod(e.target.value)}
                                    required
                                >
                                    <option value="">Selecciona...</option>
                                    {paymentMethods.map(pm => (
                                        <option key={pm.id} value={pm.id}>
                                            {pm.payment_method_type_name}
                                            {pm.last_digits ? ` (${pm.last_digits})` : pm.masked_card_number ? ` (${pm.masked_card_number})` : ''}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        )}
                        <div id="selected-numbers-info">
                            {selectedNumbers.length > 0 ? (
                                <>
                                    <p><strong>Números seleccionados:</strong> {selectedNumbers.sort((a,b) => a-b).join(', ')}</p>
                                    <p><strong>Total a pagar:</strong> {(selectedNumbers.length * Number(rifa.raffle_number_price)).toLocaleString()}</p>
                                </>
                            ) : (
                                <p style={{color: '#666'}}>Selecciona números para ver el total</p>
                            )}
                        </div>

                        {/* Botón de compra */}
                        {isAuthenticated ? (
                            selectedNumbers.length > 0 && (
                                <button 
                                    className="btn-primary" 
                                    style={{width: '100%', marginTop: '1rem'}}
                                    onClick={handlePurchase}
                                >
                                    🛒 Comprar {selectedNumbers.length} número(s)
                                </button>
                            )
                        ) : (
                            <div style={{marginTop: '1rem'}}>
                                <p style={{color: '#666', marginBottom: '0.5rem'}}>
                                    Debes iniciar sesión para comprar números
                                </p>
                                <button 
                                    className="btn-primary" 
                                    onClick={() => navigate('/auth')}
                                    style={{width: '100%'}}
                                >
                                    🔐 Iniciar sesión
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                {/* Grid de números */}
                {rifa.raffle_state?.state_raffle_name === 'Activa' && (
                    <div style={{marginTop: '3rem'}}>
                        <h3>Selecciona tus números de la suerte</h3>
                        <p style={{color: '#666', marginBottom: '1rem'}}>
                            Haz clic en los números que quieres comprar. Los números en gris ya están vendidos.
                        </p>
                        {/* Grid de números */}
                        <div className="numbers-grid">
                            {Array.from({length: rifa.raffle_number_amount}, (_, i) => i + 1).map(number => {
                                const isAvailable = numbersArray.includes(number);
                                const isSelected = selectedNumbers.includes(number);
                                return (
                                    <div
                                        key={number}
                                        className={`number-item ${!isAvailable ? 'sold' : ''} ${isSelected ? 'selected' : ''}`}
                                        onClick={() => handleNumberClick(number, isAvailable)}
                                        style={{
                                            cursor: isAvailable ? 'pointer' : 'not-allowed'
                                        }}
                                    >
                                        {number}
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default BuyNumbers;
