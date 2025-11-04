import React, { useState } from 'react';
import {
    Box,
    Card,
    TextField,
    Button,
    Typography,
    Alert,
    IconButton,
    InputAdornment,
    Link,
    alpha,
} from '@mui/material';
import {
    Visibility,
    VisibilityOff,
    Spa as SpaIcon,
} from '@mui/icons-material';
import api from '../api/apiClient';

function Login({ onLogin }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [showPassword, setShowPassword] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            const response = await api.login(username, password);
            onLogin(response.user, response.access_token);
        } catch (err) {
            setError('Credenciales inválidas');
        }
    };

    const handleTogglePassword = () => {
        setShowPassword(!showPassword);
    };

    return (
        <Box
            sx={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                minHeight: '100vh',
                width: '100vw',
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'radial-gradient(circle at center, #022c22 0%, #064e3b 50%, #022c22 100%)',
                overflow: 'auto',
                p: 2,
                '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundImage: `
            radial-gradient(circle at 20% 30%, ${alpha('#34d399', 0.15)} 0%, transparent 50%),
            radial-gradient(circle at 80% 70%, ${alpha('#10b981', 0.15)} 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, ${alpha('#059669', 0.1)} 0%, transparent 50%)
    `,
                    pointerEvents: 'none',
                },
            }}
        >
            <Card
                sx={{
                    p: { xs: 3, sm: 4 },
                    maxWidth: 420,
                    width: '100%',
                    margin: 'auto',
                    background: 'linear-gradient(135deg, rgba(6, 20, 15, 0.95) 0%, rgba(10, 31, 21, 0.98) 100%)',
                    backdropFilter: 'blur(20px)',
                    border: `1px solid ${alpha('#34d399', 0.2)}`,
                    borderRadius: 4,
                    boxShadow: `
            0 20px 60px rgba(0, 0, 0, 0.5),
            0 0 100px ${alpha('#34d399', 0.1)},
            inset 0 1px 1px ${alpha('#34d399', 0.1)}
          `,
                    position: 'relative',
                    zIndex: 1,
                }}
            >
                {/* Logo/Icono Superior */}
                <Box
                    sx={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mb: 3,
                        gap: 1,
                    }}
                >
                    <SpaIcon sx={{ color: '#34d399', fontSize: 24 }} />
                    <Typography
                        sx={{
                            color: '#fff',
                            fontSize: '0.875rem',
                            fontWeight: 500,
                            letterSpacing: '0.5px',
                        }}
                    >
                        Empoderando Lideres
                    </Typography>
                </Box>

                {/* Título */}
                <Typography
                    variant="h4"
                    align="center"
                    sx={{
                        color: '#fff',
                        fontWeight: 700,
                        mb: 1,
                        fontSize: { xs: '1.75rem', sm: '2rem' },
                    }}
                >
                    Hola,
                </Typography>
                <Typography
                    variant="h4"
                    align="center"
                    sx={{
                        color: '#fff',
                        fontWeight: 700,
                        mb: 4,
                        fontSize: { xs: '1.75rem', sm: '2rem' },
                    }}
                >
                    Bienvenido Richard!
                </Typography>

                {/* Error Alert */}
                {error && (
                    <Alert
                        severity="error"
                        sx={{
                            mb: 3,
                            backgroundColor: alpha('#ef4444', 0.1),
                            color: '#fca5a5',
                            border: `1px solid ${alpha('#ef4444', 0.3)}`,
                            '& .MuiAlert-icon': {
                                color: '#ef4444',
                            },
                        }}
                    >
                        {error}
                    </Alert>
                )}

                {/* Formulario */}
                <form onSubmit={handleSubmit}>
                    {/* Campo Email */}
                    <TextField
                        fullWidth
                        label="E-mail"
                        placeholder="admin"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                        sx={{
                            mb: 3,
                            '& .MuiOutlinedInput-root': {
                                color: '#1a1a1a',
                                backgroundColor: alpha('#fff', 0.95),
                                borderRadius: 2.5,
                                '& fieldset': {
                                    borderColor: 'transparent',
                                },
                                '&:hover fieldset': {
                                    borderColor: alpha('#34d399', 0.3),
                                },
                                '&.Mui-focused fieldset': {
                                    borderColor: '#34d399',
                                    borderWidth: 2,
                                },
                            },
                            '& .MuiInputLabel-root': {
                                color: alpha('#1a1a1a', 0.6),
                                fontSize: '0.8rem',
                                fontWeight: 500,
                            },
                            '& .MuiInputLabel-root.Mui-focused': {
                                color: '#10b981',
                            },
                            '& input::placeholder': {
                                color: alpha('#1a1a1a', 0.4),
                                opacity: 1,
                            },
                        }}
                    />

                    {/* Campo Password */}
                    <TextField
                        fullWidth
                        label="Password"
                        type={showPassword ? 'text' : 'password'}
                        placeholder="••••••••"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        InputProps={{
                            endAdornment: (
                                <InputAdornment position="end">
                                    <IconButton
                                        onClick={handleTogglePassword}
                                        edge="end"
                                        sx={{
                                            color: alpha('#1a1a1a', 0.6),
                                            '&:hover': {
                                                color: '#10b981',
                                                backgroundColor: alpha('#34d399', 0.1),
                                            },
                                        }}
                                    >
                                        {showPassword ? <VisibilityOff /> : <Visibility />}
                                    </IconButton>
                                </InputAdornment>
                            ),
                        }}
                        sx={{
                            mb: 1,
                            '& .MuiOutlinedInput-root': {
                                color: '#1a1a1a',
                                backgroundColor: alpha('#fff', 0.95),
                                borderRadius: 2.5,
                                '& fieldset': {
                                    borderColor: 'transparent',
                                },
                                '&:hover fieldset': {
                                    borderColor: alpha('#34d399', 0.3),
                                },
                                '&.Mui-focused fieldset': {
                                    borderColor: '#34d399',
                                    borderWidth: 2,
                                },
                            },
                            '& .MuiInputLabel-root': {
                                color: alpha('#1a1a1a', 0.6),
                                fontSize: '0.8rem',
                                fontWeight: 500,
                            },
                            '& .MuiInputLabel-root.Mui-focused': {
                                color: '#10b981',
                            },
                            '& input::placeholder': {
                                color: alpha('#1a1a1a', 0.4),
                                opacity: 1,
                            },
                        }}
                    />

                    {/* Forget Password Link */}
                    <Box sx={{ textAlign: 'right', mb: 3 }}>
                        <Link
                            href="#"
                            underline="none"
                            sx={{
                                color: alpha('#fff', 0.8),
                                fontSize: '0.85rem',
                                transition: 'all 0.2s',
                                '&:hover': {
                                    color: '#34d399',
                                },
                            }}
                        >
                            Forget password?
                        </Link>
                    </Box>

                    {/* Botón Login */}
                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        sx={{
                            mt: 1,
                            mb: 3,
                            py: 1.5,
                            fontSize: '1rem',
                            fontWeight: 700,
                            textTransform: 'none',
                            borderRadius: 2.5,
                            background: 'linear-gradient(135deg, #34d399 0%, #10b981 100%)',
                            color: '#064e3b',
                            boxShadow: `0 8px 24px ${alpha('#34d399', 0.4)}`,
                            transition: 'all 0.3s ease',
                            '&:hover': {
                                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                                boxShadow: `0 12px 32px ${alpha('#34d399', 0.5)}`,
                                transform: 'translateY(-2px)',
                            },
                            '&:active': {
                                transform: 'translateY(0)',
                            },
                        }}
                    >
                        Login
                    </Button>

                    {/* Sign Up Link */}
                    <Typography
                        variant="body2"
                        align="center"
                        sx={{
                            color: alpha('#fff', 0.8),
                            fontSize: '0.875rem',
                        }}
                    >
                        Don't have an account?{' '}
                        <Link
                            href="#"
                            underline="none"
                            sx={{
                                color: '#34d399',
                                fontWeight: 600,
                                transition: 'all 0.2s',
                                '&:hover': {
                                    color: '#5eead4',
                                    textDecoration: 'underline',
                                },
                            }}
                        >
                            Sign up
                        </Link>
                    </Typography>
                </form>

                {/* Credenciales de prueba */}
                <Box
                    sx={{
                        mt: 4,
                        pt: 3,
                        borderTop: `1px solid ${alpha('#34d399', 0.1)}`,
                    }}
                >
                    <Typography
                        variant="caption"
                        display="block"
                        align="center"
                        sx={{
                            color: alpha('#fff', 0.5),
                            fontSize: '0.75rem',
                            lineHeight: 1.6,
                        }}
                    >
                        Credenciales de prueba:
                        <br />
                        Usuario: <strong style={{ color: '#34d399' }}>admin</strong> |
                        Contraseña: <strong style={{ color: '#34d399' }}>admin123</strong>
                    </Typography>
                </Box>
            </Card>
        </Box>
    );
}

export default Login;