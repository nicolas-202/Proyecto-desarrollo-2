import { useNavigate } from 'react-router-dom';

function MyNumbers() {
  const navigate = useNavigate();

  return (
    <div className="module-container active">
      <div className="breadcrumbs">
        <div className="breadcrumb-item" onClick={() => navigate('/')}>Inicio</div>
        <div className="breadcrumb-separator">&gt;</div>
        <div className="breadcrumb-item">Mis números</div>
      </div>

      <h1 style={{color: 'white', textAlign: 'center', marginTop: '3rem'}}>
        Página Mis Números
      </h1>
      <p style={{color: 'white', textAlign: 'center'}}>
        Aquí podrás ver todos los números que has comprado en las rifas.
      </p>
    </div>
  );
}

export default MyNumbers;
