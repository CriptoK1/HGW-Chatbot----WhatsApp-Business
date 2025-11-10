// frontend-react/src/App.js
import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { SnackbarProvider } from 'notistack';
import Box from '@mui/material/Box';

// Componentes
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Distributors from './components/Distributors';
import Conversations from './components/Conversations';
import Leads from './components/Leads';
import Inventory from './components/Inventory';
import Layout from './components/Layout';

// 🎨 Tema personalizado
const theme = createTheme({
  palette: {
    primary: {
      main: '#28a745',
    },
    secondary: {
      main: '#6c757d',
    },
    background: {
      default: '#f4f6f9',
    },
  },
  typography: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    h4: { fontWeight: 600 },
    h5: { fontWeight: 600 },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 0 20px rgba(0,0,0,0.08)',
        },
      },
    },
  },
});

// 🔒 Componente de ruta protegida
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  if (!token) return <Navigate to="/login" replace />;
  return children;
};

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    if (token && userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  const handleLogin = (userData, token) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SnackbarProvider
        maxSnack={3}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        autoHideDuration={3000}
      >
        <Box sx={{ display: 'flex', minHeight: '100vh' }}>
          <Routes>
            {/* Ruta de Login */}
            <Route
              path="/login"
              element={
                user ? <Navigate to="/" replace /> : <Login onLogin={handleLogin} />
              }
            />

            {/* Rutas protegidas con Layout */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout user={user} onLogout={handleLogout} />
                </ProtectedRoute>
              }
            >
              <Route index element={<Dashboard />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="distributors" element={<Distributors />} />
              <Route path="conversations" element={<Conversations />} />
              <Route path="leads" element={<Leads />} />
              <Route path="inventory" element={<Inventory />} />
            </Route>

            {/* Ruta por defecto */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Box>
      </SnackbarProvider>
    </ThemeProvider>
  );
}

export default App;