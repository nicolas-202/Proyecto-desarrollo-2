import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import MainLayout from './layouts/MainLayout'
import Home from './pages/Home'
import Auth from './pages/Auth'

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Home />} />
          {/* Una sola página de auth con pestañas, dentro del layout */}
          <Route path="auth" element={<Auth />} />
        </Route>
      </Routes>
    </AuthProvider>
  )
}

export default App
