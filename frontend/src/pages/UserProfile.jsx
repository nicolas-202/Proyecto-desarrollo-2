import { useNavigate } from 'react-router-dom';

function UserProfile() {
  const navigate = useNavigate();

  return (
    <div className="module-container active">
      <div className="breadcrumbs">
        <div className="breadcrumb-item" onClick={() => navigate('/')}>Inicio</div>
        <div className="breadcrumb-separator">&gt;</div>
        <div className="breadcrumb-item">UserProfile</div>
      </div>

      <h1 style={{color: 'white', textAlign: 'center', marginTop: '3rem'}}>
        Página Perfil de usuario
      </h1>
      <p style={{color: 'white', textAlign: 'center'}}>
        Aquí podrás ver el perfil de un usuario.
      </p>
    </div>
  );
}

export default UserProfile;
