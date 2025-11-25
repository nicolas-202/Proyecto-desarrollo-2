function MyNumbers() {
  const navigate = useNavigate();

  return (
    <div className="module-container active">
      <div className="breadcrumbs">
        <div className="breadcrumb-item" onClick={() => navigate('/')}>Inicio</div>
        <div className="breadcrumb-separator">&gt;</div>
        <div className="breadcrumb-item">Comprar numeros</div>
      </div>

      <h1 style={{color: 'white', textAlign: 'center', marginTop: '3rem'}}>
        Página MyNumbers
      </h1>
    </div>
  );
}

export default MyNumbers;
