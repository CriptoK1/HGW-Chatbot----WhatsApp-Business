// frontend-react/src/components/Leads.js
import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Card,
    CircularProgress,
    Chip,
    alpha,
    Grid,
    useMediaQuery,
    Stack,
    Avatar,
    IconButton,
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { TrendingUp, People, Phone, Email, MoreVert, Person } from '@mui/icons-material';
import api from '../api/apiClient';

// Configuraciones centralizadas
const COLORS = {
    profile: {
        sin_tiempo: '#f59e0b',
        joven_economico: '#3b82f6',
        bienestar: '#10b981',
        emprendedor: '#8b5cf6',
        otro: '#6c757d',
    },
    status: {
        nuevo: '#3b82f6',
        contactado: '#10b981',
        seguimiento: '#f59e0b',
        convertido: '#8b5cf6',
        perdido: '#ef4444',
    },
};

const getInterestColor = (level) => {
    if (level >= 7) return '#10b981';
    if (level >= 4) return '#f59e0b';
    return '#ef4444';
};

// Componente reutilizable para Chips
const StatusChip = ({ value, type = 'status' }) => {
    const colors = type === 'profile' ? COLORS.profile : COLORS.status;
    const color = colors[value] || '#6c757d';
    const label = type === 'status'
        ? (value || 'Nuevo')
        : (value?.replace('_', ' ') || 'Otro');

    return (
        <Chip
            label={label}
            size="small"
            sx={{
                backgroundColor: alpha(color, 0.15),
                color,
                fontWeight: 600,
                fontSize: '0.75rem',
                textTransform: 'capitalize',
                borderRadius: 2,
            }}
        />
    );
};

// Componente para tarjeta móvil
const LeadCard = ({ lead }) => {
    const interestColor = getInterestColor(lead.interest_level);

    return (
        <Card
            sx={{
                p: 2.5,
                borderRadius: 3,
                border: '1px solid #e5e7eb',
                boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
                '&:hover': {
                    boxShadow: '0 4px 12px rgba(0,0,0,0.12)',
                    transform: 'translateY(-2px)',
                },
            }}
        >
            <Stack spacing={2}>
                <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                    <Stack direction="row" spacing={1.5} alignItems="center" flex={1}>
                        <Avatar
                            sx={{
                                width: 48,
                                height: 48,
                                bgcolor: alpha('#34d399', 0.15),
                                color: '#10b981',
                                fontWeight: 600,
                            }}
                        >
                            {lead.user_name?.[0]?.toUpperCase() || 'L'}
                        </Avatar>
                        <Box flex={1}>
                            <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#1a1a1a', mb: 0.5 }}>
                                {lead.user_name || 'Sin nombre'}
                            </Typography>
                            <Stack direction="row" spacing={1} flexWrap="wrap" gap={0.5}>
                                <StatusChip value={lead.status} />
                                <Chip
                                    label={`Interés: ${lead.interest_level || 0}`}
                                    size="small"
                                    sx={{
                                        backgroundColor: alpha(interestColor, 0.15),
                                        color: interestColor,
                                        fontWeight: 600,
                                        fontSize: '0.7rem',
                                        height: 22,
                                    }}
                                />
                            </Stack>
                        </Box>
                    </Stack>
                    <IconButton size="small">
                        <MoreVert fontSize="small" />
                    </IconButton>
                </Stack>

                <Stack spacing={1.5}>
                    <Stack direction="row" spacing={1} alignItems="center">
                        <Phone sx={{ fontSize: 18, color: '#6c757d' }} />
                        <Typography variant="body2" color="text.secondary">{lead.phone_number || '-'}</Typography>
                    </Stack>
                    {lead.email && (
                        <Stack direction="row" spacing={1} alignItems="center">
                            <Email sx={{ fontSize: 18, color: '#6c757d' }} />
                            <Typography variant="body2" color="text.secondary" noWrap>{lead.email}</Typography>
                        </Stack>
                    )}
                    {lead.profile_type && (
                        <Stack direction="row" spacing={1} alignItems="center">
                            <Person sx={{ fontSize: 18, color: '#6c757d' }} />
                            <StatusChip value={lead.profile_type} type="profile" />
                        </Stack>
                    )}
                </Stack>
            </Stack>
        </Card>
    );
};

// Componente para tarjeta de estadísticas
const StatCard = ({ icon, value, label, color }) => (
    <Card
        sx={{
            p: { xs: 2, sm: 2.5 },
            borderRadius: { xs: 2, sm: 3 },
            border: '1px solid #e5e7eb',
            boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
            '&:hover': {
                boxShadow: '0 4px 12px rgba(0,0,0,0.12)',
                transform: 'translateY(-2px)',
            },
        }}
    >
        <Stack spacing={1.5}>
            <Box
                sx={{
                    width: { xs: 36, sm: 48 },
                    height: { xs: 36, sm: 48 },
                    borderRadius: 2,
                    bgcolor: alpha(color, 0.1),
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                }}
            >
                {icon}
            </Box>
            <Box>
                <Typography variant="h4" sx={{ fontWeight: 700, fontSize: { xs: '1.5rem', sm: '2rem' } }}>
                    {value}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>
                    {label}
                </Typography>
            </Box>
        </Stack>
    </Card>
);

function Leads() {
    const [leads, setLeads] = useState([]);
    const [loading, setLoading] = useState(true);
    const isMobile = useMediaQuery((theme) => theme.breakpoints.down('md'));

    useEffect(() => {
        loadLeads();
    }, []);

    const loadLeads = async () => {
        try {
            setLoading(true);
            const data = await api.getLeads();
            setLeads(data);
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    const stats = [
        { icon: <People sx={{ color: '#3b82f6', fontSize: { xs: 20, sm: 24 } }} />, value: leads.length, label: 'Total Leads', color: '#3b82f6' },
        { icon: <TrendingUp sx={{ color: '#10b981', fontSize: { xs: 20, sm: 24 } }} />, value: leads.filter(l => l.status === 'nuevo').length, label: 'Nuevos', color: '#10b981' },
        { icon: <TrendingUp sx={{ color: '#f59e0b', fontSize: { xs: 20, sm: 24 } }} />, value: leads.filter(l => l.interest_level >= 7).length, label: 'Alto Interés', color: '#f59e0b' },
        { icon: <People sx={{ color: '#8b5cf6', fontSize: { xs: 20, sm: 24 } }} />, value: leads.filter(l => l.status === 'convertido').length, label: 'Convertidos', color: '#8b5cf6' },
    ];

    const columns = [
        { field: 'id', headerName: 'ID', width: 70, hide: isMobile },
        {
            field: 'user_name',
            headerName: 'Contacto',
            flex: 1,
            minWidth: 180,
            renderCell: (params) => (
                <Stack direction="row" spacing={1.5} alignItems="center">
                    <Avatar sx={{ width: 36, height: 36, bgcolor: alpha('#34d399', 0.15), color: '#10b981', fontSize: '0.875rem', fontWeight: 600 }}>
                        {params.value?.[0]?.toUpperCase() || 'L'}
                    </Avatar>
                    <Box>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>{params.value || 'Sin nombre'}</Typography>
                        <Typography variant="caption" color="text.secondary">{params.row.phone_number}</Typography>
                    </Box>
                </Stack>
            ),
        },
        {
            field: 'email',
            headerName: 'Email',
            flex: 1,
            minWidth: 200,
            hide: isMobile,
            renderCell: (params) => <Typography variant="body2" color="text.secondary">{params.value || '-'}</Typography>,
        },
        {
            field: 'profile_type',
            headerName: 'Perfil',
            width: 140,
            renderCell: (params) => <StatusChip value={params.value} type="profile" />,
        },
        {
            field: 'interest_level',
            headerName: 'Interés',
            width: 100,
            align: 'center',
            renderCell: (params) => (
                <Chip
                    label={params.value || 0}
                    size="small"
                    sx={{
                        backgroundColor: alpha(getInterestColor(params.value), 0.15),
                        color: getInterestColor(params.value),
                        fontWeight: 700,
                        fontSize: '0.75rem',
                        minWidth: 45,
                    }}
                />
            ),
        },
        {
            field: 'status',
            headerName: 'Estado',
            width: 130,
            renderCell: (params) => <StatusChip value={params.value} />,
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
        <Box sx={{ pb: { xs: 3, md: 0 } }}>
            <Box sx={{ mb: { xs: 2.5, md: 3.5 } }}>
                <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5, fontSize: { xs: '1.5rem', sm: '1.75rem', md: '2.125rem' } }}>
                    Leads
                </Typography>
                <Typography variant="body2" color="text.secondary">Gestiona tus prospectos y oportunidades</Typography>
            </Box>

            <Grid container spacing={{ xs: 1.5, sm: 2, md: 3 }} sx={{ mb: { xs: 2.5, md: 3.5 } }}>
                {stats.map((stat, index) => (
                    <Grid item xs={6} sm={6} md={3} key={index}>
                        <StatCard {...stat} />
                    </Grid>
                ))}
            </Grid>

            {isMobile ? (
                <Stack spacing={2}>
                    {leads.map((lead) => (
                        <LeadCard key={lead.id} lead={lead} />
                    ))}
                </Stack>
            ) : (
                <Card sx={{ borderRadius: 3, border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
                    <DataGrid
                        rows={leads}
                        columns={columns}
                        initialState={{ pagination: { paginationModel: { pageSize: 10 } } }}
                        pageSizeOptions={[10, 25, 50]}
                        autoHeight
                        disableSelectionOnClick
                        sx={{
                            border: 'none',
                            '& .MuiDataGrid-cell': { borderBottom: '1px solid #f3f4f6', py: 2 },
                            '& .MuiDataGrid-cell:hover': { color: '#10b981' },
                            '& .MuiDataGrid-columnHeaders': {
                                backgroundColor: '#f9fafb',
                                borderBottom: '2px solid #e5e7eb',
                                fontWeight: 600,
                                color: '#374151',
                            },
                            '& .MuiDataGrid-row:hover': { backgroundColor: alpha('#34d399', 0.03) },
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

export default Leads;