import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import MainLayout from './layouts/MainLayout'
import Home from './pages/Home'
import Auth from './pages/Auth'
import BuyNumbers from './pages/BuyNumbers'
import CreateRaffle from './pages/CreateRaffle'
import MyNumbers from './pages/MyNumbers'

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Home />} />
          <Route path="auth" element={<Auth />} />
          <Route path="rifa/:rifaId" element={<BuyNumbers />} />
          <Route path="create-rifa" element={<CreateRaffle />} />
          <Route path="my-numbers" element={<MyNumbers />} />
        </Route>
      </Routes>
    </AuthProvider>
  )
}

export default App
