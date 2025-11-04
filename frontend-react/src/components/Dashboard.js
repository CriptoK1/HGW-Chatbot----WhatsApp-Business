// frontend-react/src/components/Dashboard.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  Grid,
  Typography,
  CircularProgress,
  Alert,
  alpha,
  Button,
  Stack,
  useMediaQuery,
  Avatar,
  Chip,
  IconButton,
} from '@mui/material';
import {
  People,
  PersonSearch,
  Star,
  Chat,
  Add,
  TrendingUp,
  TrendingDown,
  PersonAdd,
  MoreVert,
  ArrowForward,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts';
import api from '../api/apiClient';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const COLORS = ['#34d399', '#3b82f6', '#f59e0b', '#8b5cf6', '#ef4444'];
const STATUS_COLORS = {
  nuevo: '#3b82f6',
  contactado: '#10b981',
  seguimiento: '#f59e0b',
  perdido: '#ef4444',
};

// Componente de tarjeta de estadística
const StatCard = ({ title, value, icon, color, trend, subtitle }) => (
  <Card
    sx={{
      p: 3,
      borderRadius: 4,
      background: `linear-gradient(135deg, ${color}20 0%, ${color}05 100%)`,
      border: `1px solid ${alpha(color, 0.2)}`,
      transition: 'all 0.3s ease',
      '&:hover': {
        transform: 'translateY(-4px)',
        boxShadow: `0 12px 24px ${alpha(color, 0.2)}`,
      },
    }}
  >
    <Stack spacing={2}>
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
        <Box>
          <Typography variant="body2" sx={{ color: '#6c757d', fontWeight: 500, mb: 1 }}>
            {title}
          </Typography>
          <Typography variant="h3" sx={{ fontWeight: 700, color: '#1a1a1a' }}>
            {value}
          </Typography>
          {subtitle && (
            <Typography variant="caption" sx={{ color: '#6c757d', mt: 0.5 }}>
              {subtitle}
            </Typography>
          )}
        </Box>
        <Box
          sx={{
            width: 56,
            height: 56,
            borderRadius: 3,
            background: `linear-gradient(135deg, ${color} 0%, ${alpha(color, 0.8)} 100%)`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: `0 8px 16px ${alpha(color, 0.3)}`,
          }}
        >
          {icon}
        </Box>
      </Stack>
      {trend !== undefined && (
        <Stack direction="row" alignItems="center" spacing={0.5}>
          {trend > 0 ? (
            <TrendingUp sx={{ fontSize: 16, color: '#10b981' }} />
          ) : (
            <TrendingDown sx={{ fontSize: 16, color: '#ef4444' }} />
          )}
          <Typography
            variant="caption"
            sx={{
              color: trend > 0 ? '#10b981' : '#ef4444',
              fontWeight: 600,
            }}
          >
            {Math.abs(trend)}% vs mes anterior
          </Typography>
        </Stack>
      )}
    </Stack>
  </Card>
);

// Componente de tarjeta de conversación
const ConversationCard = ({ conversation }) => (
  <Card
    sx={{
      p: 2.5,
      borderRadius: 3,
      border: '1px solid #e5e7eb',
      transition: 'all 0.2s ease',
      '&:hover': {
        boxShadow: '0 4px 12px rgba(0,0,0,0.12)',
        transform: 'translateY(-2px)',
      },
    }}
  >
    <Stack direction="row" spacing={2} alignItems="center">
      <Avatar
        sx={{
          width: 48,
          height: 48,
          bgcolor: alpha('#34d399', 0.15),
          color: '#10b981',
          fontWeight: 600,
        }}
      >
        {conversation.user_name?.[0]?.toUpperCase() || 'U'}
      </Avatar>
      <Box flex={1}>
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 0.5 }}>
          {conversation.user_name || 'Sin nombre'}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {conversation.phone_number}
        </Typography>
      </Box>
      <Stack spacing={0.5} alignItems="flex-end">
        <Chip
          label={conversation.status}
          size="small"
          sx={{
            backgroundColor: alpha(STATUS_COLORS[conversation.status] || '#6c757d', 0.15),
            color: STATUS_COLORS[conversation.status] || '#6c757d',
            fontWeight: 600,
            fontSize: '0.7rem',
          }}
        />
        <Typography variant="caption" color="text.secondary">
          {conversation.last_interaction
            ? format(new Date(conversation.last_interaction), 'dd/MM', { locale: es })
            : '-'}
        </Typography>
      </Stack>
    </Stack>
  </Card>
);

function Dashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    total_conversations: 0,
    total_distributors: 0,
    total_leads: 0,
    active_distributors: 0,
    high_interest_leads: 0,
  });
  const [recentConversations, setRecentConversations] = useState([]);
  const [distributorStats, setDistributorStats] = useState([]);
  const [activityData, setActivityData] = useState([]);

  const isMobile = useMediaQuery((theme) => theme.breakpoints.down('md'));

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);

      // Cargar datos básicos primero
      const statsData = await api.getStats();
      setStats(statsData);

      // Cargar resto de datos en paralelo
      const [conversationsData, distributorsData, activityFlowData] = await Promise.all([
        api.getConversations({ limit: 6 }),
        api.getDistributorsStats().catch(() => ({ por_nivel: {} })),
        api.getActivityFlow ? api.getActivityFlow().catch(() => []) : Promise.resolve([]),
      ]);

      setRecentConversations(conversationsData || []);

      // Datos para gráfico de distribuidores
      if (distributorsData?.por_nivel) {
        const chartData = Object.entries(distributorsData.por_nivel).map(([name, value]) => ({
          name,
          value,
        }));
        setDistributorStats(chartData);
      }

      // Datos para flujo de actividad
      setActivityData(activityFlowData || []);

      setError(null);
    } catch (err) {
      setError('Error al cargar el dashboard');
      console.error('Error cargando dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleNewDistributor = () => {
    // Navegar a la página de distribuidores con parámetro para abrir el diálogo
    navigate('/distributors?action=new');
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress sx={{ color: '#34d399' }} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 3 }}>
        {error}
      </Alert>
    );
  }

  const statCards = [
    {
      title: 'Total Conversaciones',
      value: stats.total_conversations || 0,
      icon: <Chat sx={{ fontSize: 28, color: '#fff' }} />,
      color: '#3b82f6',
      trend: 12.5,
    },
    {
      title: 'Distribuidores',
      value: stats.total_distributors || 0,
      icon: <People sx={{ fontSize: 28, color: '#fff' }} />,
      color: '#34d399',
      subtitle: `${stats.active_distributors || 0} activos`,
      trend: 8.2,
    },
    {
      title: 'Total Leads',
      value: stats.total_leads || 0,
      icon: <PersonSearch sx={{ fontSize: 28, color: '#fff' }} />,
      color: '#f59e0b',
      trend: -3.1,
    },
    {
      title: 'Alto Interés',
      value: stats.high_interest_leads || 0,
      icon: <Star sx={{ fontSize: 28, color: '#fff' }} />,
      color: '#8b5cf6',
      trend: 15.7,
    },
  ];

  return (
    <Box sx={{ pb: { xs: 3, md: 0 } }}>
      {/* Header con acciones */}
      <Stack
        direction={{ xs: 'column', sm: 'row' }}
        justifyContent="space-between"
        alignItems={{ xs: 'flex-start', sm: 'center' }}
        spacing={2}
        sx={{ mb: 4 }}
      >
        <Box>
          <Typography
            variant="h4"
            sx={{
              fontWeight: 700,
              color: '#1a1a1a',
              mb: 0.5,
              fontSize: { xs: '1.5rem', sm: '2rem' },
            }}
          >
            Mi Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Resumen de actividad y métricas HGW
          </Typography>
        </Box>
        <Stack direction="row" spacing={2}>
          <Button
            variant="contained"
            startIcon={<PersonAdd />}
            onClick={handleNewDistributor}
            sx={{
              bgcolor: '#34d399',
              color: '#fff',
              borderRadius: 2,
              textTransform: 'none',
              fontWeight: 600,
              px: 3,
              boxShadow: '0 4px 12px rgba(52, 211, 153, 0.3)',
              '&:hover': {
                bgcolor: '#10b981',
                boxShadow: '0 6px 16px rgba(52, 211, 153, 0.4)',
              },
            }}
          >
            Nuevo Distribuidor
          </Button>
          {!isMobile && (
            <Button
              variant="outlined"
              startIcon={<Add />}
              onClick={() => navigate('/leads')}
              sx={{
                borderColor: '#e5e7eb',
                color: '#374151',
                borderRadius: 2,
                textTransform: 'none',
                fontWeight: 600,
                px: 3,
                '&:hover': {
                  borderColor: '#34d399',
                  bgcolor: alpha('#34d399', 0.05),
                },
              }}
            >
              Ver Leads
            </Button>
          )}
        </Stack>
      </Stack>

      {/* Cards de Estadísticas */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {statCards.map((card, index) => (
          <Grid item xs={12} sm={6} lg={3} key={index}>
            <StatCard {...card} />
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        {/* Gráfico de Actividad */}
        <Grid item xs={12} lg={8}>
          <Card
            sx={{
              p: 3,
              borderRadius: 4,
              border: '1px solid #e5e7eb',
              boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
            }}
          >
            <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
                  Flujo de Conversaciones
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Últimos 6 meses
                </Typography>
              </Box>
              <Button
                size="small"
                endIcon={<ArrowForward />}
                onClick={() => navigate('/conversations')}
                sx={{
                  textTransform: 'none',
                  color: '#34d399',
                  fontWeight: 600,
                }}
              >
                Ver todo
              </Button>
            </Stack>
            {activityData.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={activityData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                  <XAxis dataKey="month" stroke="#6c757d" style={{ fontSize: '12px' }} />
                  <YAxis stroke="#6c757d" style={{ fontSize: '12px' }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#fff',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke="#34d399"
                    strokeWidth={3}
                    dot={{ fill: '#34d399', r: 6 }}
                    activeDot={{ r: 8 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <Box
                sx={{
                  height: 280,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Typography variant="body2" color="text.secondary">
                  No hay datos de actividad disponibles
                </Typography>
              </Box>
            )}
          </Card>
        </Grid>

        {/* Gráfico de Distribuidores */}
        <Grid item xs={12} lg={4}>
          <Card
            sx={{
              p: 3,
              borderRadius: 4,
              border: '1px solid #e5e7eb',
              boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
              height: '100%',
            }}
          >
            <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Por Nivel
              </Typography>
              <IconButton size="small" onClick={() => navigate('/distributors')}>
                <MoreVert fontSize="small" />
              </IconButton>
            </Stack>
            {distributorStats.length > 0 ? (
              <>
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie
                      data={distributorStats}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {distributorStats.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#fff',
                        border: '1px solid #e5e7eb',
                        borderRadius: '8px',
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                <Stack spacing={1.5} mt={2}>
                  {distributorStats.map((item, index) => (
                    <Stack
                      key={index}
                      direction="row"
                      justifyContent="space-between"
                      alignItems="center"
                    >
                      <Stack direction="row" spacing={1} alignItems="center">
                        <Box
                          sx={{
                            width: 12,
                            height: 12,
                            borderRadius: 1,
                            bgcolor: COLORS[index % COLORS.length],
                          }}
                        />
                        <Typography variant="body2" sx={{ fontSize: '0.875rem' }}>
                          {item.name}
                        </Typography>
                      </Stack>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {item.value}
                      </Typography>
                    </Stack>
                  ))}
                </Stack>
              </>
            ) : (
              <Box
                sx={{
                  height: 280,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Typography variant="body2" color="text.secondary">
                  No hay datos disponibles
                </Typography>
              </Box>
            )}
          </Card>
        </Grid>

        {/* Conversaciones Recientes */}
        <Grid item xs={12}>
          <Card
            sx={{
              p: 3,
              borderRadius: 4,
              border: '1px solid #e5e7eb',
              boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
            }}
          >
            <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Conversaciones Recientes
              </Typography>
              <Button
                size="small"
                endIcon={<ArrowForward />}
                onClick={() => navigate('/conversations')}
                sx={{
                  textTransform: 'none',
                  color: '#34d399',
                  fontWeight: 600,
                }}
              >
                Ver todas
              </Button>
            </Stack>
            {recentConversations.length > 0 ? (
              <Grid container spacing={2}>
                {recentConversations.map((conv) => (
                  <Grid item xs={12} sm={6} md={4} key={conv.id}>
                    <ConversationCard conversation={conv} />
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Box sx={{ py: 4, textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  No hay conversaciones recientes
                </Typography>
              </Box>
            )}
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard;