import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function Config() {
  const navigate = useNavigate();
  const { isAdmin } = useAuth();
  const [selectedCategory, setSelectedCategory] = useState(null);

  <p>Aqui encontraras la pagina config</p>;
}

export default Config;
