import { useNavigate } from 'react-router-dom';

function EditRaffle() {
  const navigate = useNavigate();

  return (
    <div className="module-container active">
      <div className="breadcrumbs">
        <div className="breadcrumb-item" onClick={() => navigate('/')}>
          Inicio
        </div>
        <div className="breadcrumb-separator">&gt;</div>
        <div className="breadcrumb-item">Editar rifa</div>
      </div>

      <h1 style={{ color: 'white', textAlign: 'center', marginTop: '3rem' }}>Página Editar rifa</h1>
      <p style={{ color: 'white', textAlign: 'center' }}>Aquí podrás editar tus rifas.</p>
    </div>
  );
}

export default EditRaffle;
