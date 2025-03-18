// App.js - Componente principal de la aplicación
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import ProjectsDashboard from './components/projects/ProjectsDashboard';
import LoginPage from './components/auth/LoginPage';
import { AuthProvider, useAuth } from './context/AuthContext';

// Componente para rutas protegidas que requieren autenticación
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

const App = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          
          {/* Rutas protegidas dentro del layout principal */}
          <Route path="/" element={
            <ProtectedRoute>
              <AppLayout>
                <Navigate to="/projects" replace />
              </AppLayout>
            </ProtectedRoute>
          } />
          
          <Route path="/projects" element={
            <ProtectedRoute>
              <AppLayout>
                <ProjectsDashboard />
              </AppLayout>
            </ProtectedRoute>
          } />
          
          {/* Añadir más rutas según se necesite */}
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;