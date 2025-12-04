import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import MainLayout from './layouts/MainLayout';
import Home from './pages/Home';
import Auth from './pages/Auth';
import BuyNumbers from './pages/BuyNumbers';
import CreateRaffle from './pages/CreateRaffle';
import EditRaffle from './pages/EditRaffle';
import MyNumbers from './pages/MyNumbers';
import UserProfile from './pages/UserProfile';
import SearchUsers from './pages/SearchUsers';
import Config from './pages/Config';
import ConfigCategory from './pages/ConfigCategory';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Home />} />
          <Route path="auth" element={<Auth />} />
          <Route path="raffle/:raffleId" element={<BuyNumbers />} />
          <Route
            path="create-raffle"
            element={
              <ProtectedRoute>
                <CreateRaffle />
              </ProtectedRoute>
            }
          />
          <Route
            path="edit-raffle/:raffleId"
            element={
              <ProtectedRoute>
                <EditRaffle />
              </ProtectedRoute>
            }
          />
          <Route
            path="my-numbers"
            element={
              <ProtectedRoute>
                <MyNumbers />
              </ProtectedRoute>
            }
          />
          <Route path="user/:userId" element={<UserProfile />} />
          <Route path="search-users" element={<SearchUsers />} />
          <Route
            path="config"
            element={
              <ProtectedRoute>
                <Config />
              </ProtectedRoute>
            }
          />
          <Route
            path="config/:categoryId"
            element={
              <ProtectedRoute>
                <ConfigCategory />
              </ProtectedRoute>
            }
          />
        </Route>
      </Routes>
    </AuthProvider>
  );
}

export default App;
