// context/AuthContext.js
import React, { createContext, useState, useContext, useEffect } from 'react';

// Crear el contexto de autenticación
const AuthContext = createContext(null);

// Proveedor de autenticación que envolverá la aplicación
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Comprobar si hay un usuario autenticado al cargar la aplicación
  useEffect(() => {
    // Verificar si hay un token en localStorage
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      try {
        // Parseamos los datos del usuario
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
        setIsAuthenticated(true);
      } catch (error) {
        // Si hay algún error, limpiamos el almacenamiento
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
    
    setIsLoading(false);
  }, []);

  // Función para iniciar sesión
  const login = async (email, password) => {
    try {
      setIsLoading(true);
      
      // En una implementación real, esto sería una llamada a tu API
      // Simulamos un pequeño retraso para la demo
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Demo: aceptamos cualquier credencial para facilitar pruebas
      // En producción, esto vendría de la respuesta de tu API
      const userData = {
        id: 1,
        name: 'Usuario Demo',
        email: email,
        role: 'user'
      };
      
      // Generamos un token falso para la demo
      const token = 'demo_token_' + Math.random().toString(36).substring(2);
      
      // Guardamos la información en localStorage
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(userData));
      
      // Actualizamos el estado
      setUser(userData);
      setIsAuthenticated(true);
      
      return { success: true };
    } catch (error) {
      throw new Error('Error al iniciar sesión');
    } finally {
      setIsLoading(false);
    }
  };

  // Función para cerrar sesión
  const logout = () => {
    // Eliminamos datos de localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    
    // Actualizamos el estado
    setUser(null);
    setIsAuthenticated(false);
  };

  // Valor del contexto
  const value = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Hook personalizado para acceder al contexto
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider');
  }
  return context;
};