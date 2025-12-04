import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { apiClient } from '../services/authService';

function ConfigCategory() {
    const { categoryId } = useParams();

  <p>Aqui encontraras la pagina configCategory</p>
}

export default ConfigCategory;
