import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Card,
    CircularProgress,
    Chip,
    alpha,
    TextField,
    InputAdornment,
    Avatar,
    Stack,
    Divider,
    useTheme,
    useMediaQuery,
    Grid,
    Paper,
} from '@mui/material';
import {
    Search as SearchIcon,
    Phone as PhoneIcon,
    Message as MessageIcon,
    Schedule as ScheduleIcon,
} from '@mui/icons-material';
import { DataGrid } from '@mui/x-data-grid';
import api from '../api/apiClient';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

function Conversations() {
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('md'));
    const [conversations, setConversations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        loadConversations();
    }, []);

    const loadConversations = async () => {
        try {
            setLoading(true);
            const data = await api.getConversations();
            setConversations(data);
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredConversations = conversations.filter((conv) => {
        const searchLower = searchTerm.toLowerCase();
        return (
            conv.phone_number?.toLowerCase().includes(searchLower) ||
            conv.user_name?.toLowerCase().includes(searchLower) ||
            conv.profile_type?.toLowerCase().includes(searchLower)
        );
    });

    const getStatusColor = (status) => {
        const colors = {
            nuevo: '#3b82f6',
            activo: '#10b981',
            seguimiento: '#f59e0b',
            cerrado: '#6c757d',
        };
        return colors[status] || '#6c757d';
    };

    const getProfileColor = (profile) => {
        const colors = {
            distribuidor: '#8b5cf6',
            lead: '#f59e0b',
            cliente: '#10b981',
            otro: '#6c757d',
        };
        return colors[profile] || '#10b981';
    };

    const getInitials = (name) => {
        if (!name) return '?';
        return name
            .split(' ')
            .map((n) => n[0])
            .join('')
            .substring(0, 2)
            .toUpperCase();
    };

    // Componente de Card para Mobile
    const ConversationCard = ({ conversation }) => {
        const statusColor = getStatusColor(conversation.status);
        const profileColor = getProfileColor(conversation.profile_type);

        return (
            <Card
                sx={{
                    mb: 2,
                    borderRadius: 3,
                    border: '1px solid #e5e7eb',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                        boxShadow: '0 4px 12px rgba(0,0,0,0.12)',
                        transform: 'translateY(-2px)',
                        borderColor: alpha('#34d399', 0.3),
                    },
                }}
            >
                <Box sx={{ p: 2.5 }}>
                    {/* Header con Avatar y Nombre */}
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <Avatar
                            sx={{
                                width: 48,
                                height: 48,
                                background: `linear-gradient(135deg, ${profileColor} 0%, ${alpha(profileColor, 0.7)} 100%)`,
                                color: '#fff',
                                fontWeight: 700,
                                fontSize: '1rem',
                            }}
                        >
                            {getInitials(conversation.user_name)}
                        </Avatar>
                        <Box sx={{ ml: 2, flex: 1 }}>
                            <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '1rem', color: '#1a1a1a', mb: 0.5 }}>
                                {conversation.user_name || 'Sin nombre'}
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Chip
                                    label={conversation.profile_type || 'otro'}
                                    size="small"
                                    sx={{
                                        backgroundColor: alpha(profileColor, 0.15),
                                        color: profileColor,
                                        fontWeight: 600,
                                        fontSize: '0.7rem',
                                        height: 22,
                                    }}
                                />
                                <Chip
                                    label={conversation.status}
                                    size="small"
                                    sx={{
                                        backgroundColor: alpha(statusColor, 0.15),
                                        color: statusColor,
                                        fontWeight: 600,
                                        fontSize: '0.7rem',
                                        height: 22,
                                    }}
                                />
                            </Box>
                        </Box>
                    </Box>

                    <Divider sx={{ my: 2 }} />

                    {/* Información detallada */}
                    <Stack spacing={1.5}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <PhoneIcon sx={{ fontSize: 18, color: '#10b981', mr: 1.5 }} />
                            <Typography variant="body2" sx={{ color: '#374151', fontWeight: 500 }}>
                                {conversation.phone_number}
                            </Typography>
                        </Box>

                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <MessageIcon sx={{ fontSize: 18, color: '#3b82f6', mr: 1.5 }} />
                            <Typography variant="body2" sx={{ color: '#374151' }}>
                                {conversation.messages_count || 0} mensajes
                            </Typography>
                        </Box>

                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <ScheduleIcon sx={{ fontSize: 18, color: '#f59e0b', mr: 1.5 }} />
                            <Typography variant="body2" sx={{ color: '#6c757d', fontSize: '0.875rem' }}>
                                {conversation.last_interaction
                                    ? format(new Date(conversation.last_interaction), "dd 'de' MMMM, HH:mm", { locale: es })
                                    : 'Sin interacción'}
                            </Typography>
                        </Box>
                    </Stack>
                </Box>
            </Card>
        );
    };

    // Columnas para Desktop
    const columns = [
        {
            field: 'id',
            headerName: 'ID',
            width: 70,
            headerAlign: 'center',
            align: 'center',
        },
        {
            field: 'user_name',
            headerName: 'Usuario',
            width: 200,
            renderCell: (params) => (
                <Box sx={{ display: 'flex', alignItems: 'center', py: 1 }}>
                    <Avatar
                        sx={{
                            width: 36,
                            height: 36,
                            background: `linear-gradient(135deg, ${getProfileColor(params.row.profile_type)} 0%, ${alpha(
                                getProfileColor(params.row.profile_type),
                                0.7
                            )} 100%)`,
                            color: '#fff',
                            fontWeight: 700,
                            fontSize: '0.875rem',
                            mr: 1.5,
                        }}
                    >
                        {getInitials(params.value)}
                    </Avatar>
                    <Box>
                        <Typography variant="body2" sx={{ fontWeight: 600, color: '#1a1a1a', lineHeight: 1.2 }}>
                            {params.value || 'Sin nombre'}
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#6c757d', fontSize: '0.75rem' }}>
                            ID: {params.row.id}
                        </Typography>
                    </Box>
                </Box>
            ),
        },
        {
            field: 'phone_number',
            headerName: 'Teléfono',
            width: 150,
            renderCell: (params) => (
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <PhoneIcon sx={{ fontSize: 16, color: '#10b981', mr: 1 }} />
                    <Typography variant="body2" sx={{ color: '#374151', fontWeight: 500 }}>
                        {params.value}
                    </Typography>
                </Box>
            ),
        },
        {
            field: 'profile_type',
            headerName: 'Perfil',
            width: 130,
            renderCell: (params) => {
                const color = getProfileColor(params.value);
                return (
                    <Chip
                        label={params.value || 'Otro'}
                        size="small"
                        sx={{
                            backgroundColor: alpha(color, 0.15),
                            color: color,
                            fontWeight: 600,
                            fontSize: '0.75rem',
                            borderRadius: 2,
                        }}
                    />
                );
            },
        },
        {
            field: 'status',
            headerName: 'Estado',
            width: 120,
            renderCell: (params) => {
                const color = getStatusColor(params.value);
                return (
                    <Chip
                        label={params.value}
                        size="small"
                        sx={{
                            backgroundColor: alpha(color, 0.15),
                            color: color,
                            fontWeight: 600,
                            fontSize: '0.75rem',
                            borderRadius: 2,
                        }}
                    />
                );
            },
        },
        {
            field: 'messages_count',
            headerName: 'Mensajes',
            width: 100,
            align: 'center',
            headerAlign: 'center',
            renderCell: (params) => (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <MessageIcon sx={{ fontSize: 16, color: '#3b82f6', mr: 0.5 }} />
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#374151' }}>
                        {params.value || 0}
                    </Typography>
                </Box>
            ),
        },
        {
            field: 'last_interaction',
            headerName: 'Última Interacción',
            width: 180,
            renderCell: (params) => (
                <Typography variant="body2" sx={{ color: '#6c757d', fontSize: '0.875rem' }}>
                    {params.value ? format(new Date(params.value), 'dd/MM/yyyy HH:mm') : '-'}
                </Typography>
            ),
        },
    ];

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
                <CircularProgress sx={{ color: '#34d399' }} />
            </Box>
        );
    }

    return (
        <Box>
            {/* Header */}
            <Box sx={{ mb: 3 }}>
                <Typography
                    variant="h4"
                    sx={{
                        fontWeight: 700,
                        color: '#1a1a1a',
                        mb: 0.5,
                        fontSize: { xs: '1.5rem', sm: '2rem' },
                    }}
                >
                    Conversaciones
                </Typography>
                <Typography variant="body2" sx={{ color: '#6c757d' }}>
                    Gestiona todas las conversaciones con clientes
                </Typography>
            </Box>

            {/* Barra de búsqueda y filtros */}
            <Card
                sx={{
                    mb: 3,
                    p: { xs: 2, sm: 2.5 },
                    borderRadius: 3,
                    border: '1px solid #e5e7eb',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
                }}
            >
                <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} md={8}>
                        <TextField
                            fullWidth
                            placeholder="Buscar por nombre, teléfono o perfil..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            InputProps={{
                                startAdornment: (
                                    <InputAdornment position="start">
                                        <SearchIcon sx={{ color: '#6c757d' }} />
                                    </InputAdornment>
                                ),
                            }}
                            sx={{
                                '& .MuiOutlinedInput-root': {
                                    backgroundColor: '#f9fafb',
                                    borderRadius: 2,
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
                            }}
                        />
                    </Grid>
                    <Grid item xs={12} md={4}>
                        <Box sx={{ display: 'flex', gap: 1, justifyContent: { xs: 'flex-start', md: 'flex-end' } }}>
                            <Chip
                                label={`Total: ${filteredConversations.length}`}
                                sx={{
                                    backgroundColor: alpha('#34d399', 0.15),
                                    color: '#10b981',
                                    fontWeight: 600,
                                    fontSize: '0.875rem',
                                }}
                            />
                        </Box>
                    </Grid>
                </Grid>
            </Card>

            {/* Contenido: Cards para Mobile, Tabla para Desktop */}
            {isMobile ? (
                // Vista Mobile con Cards
                <Box>
                    {filteredConversations.length > 0 ? (
                        filteredConversations.map((conversation) => (
                            <ConversationCard key={conversation.id} conversation={conversation} />
                        ))
                    ) : (
                        <Paper
                            sx={{
                                p: 4,
                                textAlign: 'center',
                                borderRadius: 3,
                                border: '1px solid #e5e7eb',
                            }}
                        >
                            <Typography variant="body1" color="textSecondary">
                                No se encontraron conversaciones
                            </Typography>
                        </Paper>
                    )}
                </Box>
            ) : (
                // Vista Desktop con Tabla
                <Card
                    sx={{
                        borderRadius: 3,
                        border: '1px solid #e5e7eb',
                        boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
                        overflow: 'hidden',
                    }}
                >
                    <DataGrid
                        rows={filteredConversations}
                        columns={columns}
                        pageSize={10}
                        rowsPerPageOptions={[10, 25, 50]}
                        autoHeight
                        disableSelectionOnClick
                        rowHeight={70}
                        sx={{
                            border: 'none',
                            '& .MuiDataGrid-cell': {
                                borderColor: '#f3f4f6',
                            },
                            '& .MuiDataGrid-cell:hover': {
                                color: '#10b981',
                            },
                            '& .MuiDataGrid-columnHeaders': {
                                backgroundColor: '#f9fafb',
                                fontWeight: 600,
                                color: '#374151',
                                fontSize: '0.875rem',
                                borderBottom: '2px solid #e5e7eb',
                            },
                            '& .MuiDataGrid-row': {
                                transition: 'all 0.2s ease',
                                '&:hover': {
                                    backgroundColor: alpha('#34d399', 0.04),
                                    cursor: 'pointer',
                                },
                            },
                            '& .MuiDataGrid-footerContainer': {
                                borderTop: '2px solid #e5e7eb',
                                backgroundColor: '#f9fafb',
                            },
                        }}
                    />
                </Card>
            )}
        </Box>
    );
}

export default Conversations;