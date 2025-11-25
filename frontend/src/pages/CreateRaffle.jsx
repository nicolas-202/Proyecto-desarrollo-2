import { useNavigate } from 'react-router-dom';

function CreateRaffle() {
  const navigate = useNavigate();

  return (
    <div className="module-container active">
      <div className="breadcrumbs">
        <div className="breadcrumb-item" onClick={() => navigate('/')}>Inicio</div>
        <div className="breadcrumb-separator">&gt;</div>
        <div className="breadcrumb-item">Crear Rifa</div>
      </div>

      <h1 style={{color: 'white', textAlign: 'center', marginTop: '3rem'}}>
        Página CreateRaffle
      </h1>
    </div>
  );
}

export default CreateRaffle;
