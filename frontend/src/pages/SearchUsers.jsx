import { useNavigate } from 'react-router-dom';

function SearchUsers() {
  const navigate = useNavigate();

  return (
    <div className="module-container active">
      <div className="breadcrumbs">
        <div className="breadcrumb-item" onClick={() => navigate('/')}>Inicio</div>
        <div className="breadcrumb-separator">&gt;</div>
        <div className="breadcrumb-item">Buscar usuarios</div>
      </div>

      <h1 style={{color: 'white', textAlign: 'center', marginTop: '3rem'}}>
        Página Buscar usuarios
      </h1>
      <p style={{color: 'white', textAlign: 'center'}}>
        Aquí podrás buscar usuarios.
      </p>
    </div>
  );
}

export default SearchUsers;
