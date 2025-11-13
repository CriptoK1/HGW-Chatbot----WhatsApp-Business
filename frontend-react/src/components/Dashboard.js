// frontend-react/src/components/Dashboard.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Card, Grid, Typography, CircularProgress, Alert, alpha, Button,
  Stack, useMediaQuery, Avatar, Chip, IconButton
} from '@mui/material';
import {
  People, PersonSearch, Star, Chat, Add, TrendingUp, TrendingDown,
  PersonAdd, MoreVert, ArrowForward
} from '@mui/icons-material';
import {
  LineChart, Line, PieChart, Pie, Cell, ResponsiveContainer,
  Tooltip, XAxis, YAxis, CartesianGrid
} from 'recharts';
import api from '../api/apiClient';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const COLORS = ['#34d399', '#3b82f6', '#f59e0b', '#8b5cf6', '#ef4444'];
const STATUS_COLORS = { nuevo: '#3b82f6', contactado: '#10b981', seguimiento: '#f59e0b', perdido: '#ef4444' };

// ---------- Tarjeta estadística ----------
const StatCard = ({ title, value, icon, color, trend, subtitle }) => (
  <Card sx={{
    p: 3, borderRadius: 4, background: `linear-gradient(135deg, ${color}20, ${color}05)`,
    border: `1px solid ${alpha(color, 0.2)}`, transition: '0.3s',
    '&:hover': { transform: 'translateY(-4px)', boxShadow: `0 12px 24px ${alpha(color, 0.2)}` }
  }}>
    <Stack spacing={2}>
      <Stack direction="row" justifyContent="space-between">
        <Box>
          <Typography variant="body2" sx={{ color: '#6c757d', fontWeight: 500 }}>{title}</Typography>
          <Typography variant="h3" sx={{ fontWeight: 700 }}>{value}</Typography>
          {subtitle && <Typography variant="caption" color="text.secondary">{subtitle}</Typography>}
        </Box>
        <Box sx={{
          width: 56, height: 56, borderRadius: 3,
          background: `linear-gradient(135deg, ${color}, ${alpha(color, 0.8)})`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: `0 8px 16px ${alpha(color, 0.3)}`
        }}>{icon}</Box>
      </Stack>
      {trend !== undefined && (
        <Stack direction="row" alignItems="center" spacing={0.5}>
          {trend > 0 ? <TrendingUp sx={{ fontSize: 16, color: '#10b981' }} /> :
            <TrendingDown sx={{ fontSize: 16, color: '#ef4444' }} />}
          <Typography variant="caption" sx={{
            color: trend > 0 ? '#10b981' : '#ef4444', fontWeight: 600
          }}>{Math.abs(trend)}% vs mes anterior</Typography>
        </Stack>
      )}
    </Stack>
  </Card>
);

// ---------- Tarjeta conversación ----------
const ConversationCard = ({ c }) => (
  <Card sx={{
    p: 2.5, borderRadius: 3, border: '1px solid #e5e7eb',
    '&:hover': { boxShadow: '0 4px 12px rgba(0,0,0,0.12)', transform: 'translateY(-2px)' }
  }}>
    <Stack direction="row" spacing={2} alignItems="center">
      <Avatar sx={{
        width: 48, height: 48, bgcolor: alpha('#34d399', 0.15), color: '#10b981', fontWeight: 600
      }}>{c.user_name?.[0]?.toUpperCase() || 'U'}</Avatar>
      <Box flex={1}>
        <Typography variant="subtitle2" fontWeight={600}>{c.user_name || 'Sin nombre'}</Typography>
        <Typography variant="caption" color="text.secondary">{c.phone_number}</Typography>
      </Box>
      <Stack alignItems="flex-end" spacing={0.5}>
        <Chip label={c.status} size="small" sx={{
          bgcolor: alpha(STATUS_COLORS[c.status] || '#6c757d', 0.15),
          color: STATUS_COLORS[c.status] || '#6c757d', fontWeight: 600, fontSize: '0.7rem'
        }} />
        <Typography variant="caption" color="text.secondary">
          {c.last_interaction ? format(new Date(c.last_interaction), 'dd/MM', { locale: es }) : '-'}
        </Typography>
      </Stack>
    </Stack>
  </Card>
);

// ---------- Dashboard ----------
export default function Dashboard() {
  const navigate = useNavigate();
  const isMobile = useMediaQuery(t => t.breakpoints.down('md'));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({});
  const [recent, setRecent] = useState([]);
  const [dist, setDist] = useState([]);
  const [activity, setActivity] = useState([]);

  useEffect(() => { load(); }, []);
  const load = async () => {
    try {
      const s = await api.getStats();
      const [conv, d, a] = await Promise.all([
        api.getConversations({ limit: 6 }),
        api.getDistributorsStats().catch(() => ({ por_nivel: {} })),
        api.getActivityFlow?.().catch(() => []) || []
      ]);
      setStats(s);
      setRecent(conv || []);
      setDist(Object.entries(d.por_nivel || {}).map(([n, v]) => ({ name: n, value: v })));
      setActivity(a || []);
    } catch { setError('Error al cargar el dashboard'); }
    finally { setLoading(false); }
  };

  if (loading) return <Box display="flex" justifyContent="center" minHeight="400px"><CircularProgress sx={{ color: '#34d399' }} /></Box>;
  if (error) return <Alert severity="error" sx={{ m: 3 }}>{error}</Alert>;

  const cards = [
    { t: 'Total Conversaciones', v: stats.total_conversations, i: <Chat sx={{ fontSize: 28, color: '#fff' }} />, c: '#3b82f6', tr: 12.5 },
    { t: 'Distribuidores', v: stats.total_distributors, i: <People sx={{ fontSize: 28, color: '#fff' }} />, c: '#34d399', sub: `${stats.active_distributors || 0} activos`, tr: 8.2 },
    { t: 'Total Leads', v: stats.total_leads, i: <PersonSearch sx={{ fontSize: 28, color: '#fff' }} />, c: '#f59e0b', tr: -3.1 },
    { t: 'Alto Interés', v: stats.high_interest_leads, i: <Star sx={{ fontSize: 28, color: '#fff' }} />, c: '#8b5cf6', tr: 15.7 }
  ];

  return (
    <Box sx={{ pb: { xs: 3, md: 0 } }}>
      {/* Header */}
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ xs: 'flex-start', sm: 'center' }} spacing={2} mb={4}>
        <Box>
          <Typography variant="h4" fontWeight={700}>Mi Dashboard</Typography>
          <Typography variant="body2" color="text.secondary">Resumen de actividad y métricas HGW</Typography>
        </Box>
        <Stack direction="row" spacing={2}>
          <Button variant="contained" startIcon={<PersonAdd />} onClick={() => navigate('/distributors?action=new')}
            sx={{ bgcolor: '#34d399', color: '#fff', borderRadius: 2, textTransform: 'none', fontWeight: 600, px: 3 }}>
            Nuevo Distribuidor
          </Button>
          {!isMobile && (
            <Button variant="outlined" startIcon={<Add />} onClick={() => navigate('/leads')}
              sx={{ borderColor: '#e5e7eb', color: '#374151', borderRadius: 2, textTransform: 'none', fontWeight: 600, px: 3 }}>
              Ver Leads
            </Button>
          )}
        </Stack>
      </Stack>

      {/* Cards */}
      <Grid container spacing={3} mb={4}>
        {cards.map((x, i) => (
          <Grid item xs={12} sm={6} lg={3} key={i}>
            <StatCard title={x.t} value={x.v || 0} icon={x.i} color={x.c} trend={x.tr} subtitle={x.sub} />
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        {/* Actividad */}
        <Grid item xs={12} lg={8}>
          <Card sx={{ p: 3, borderRadius: 4, border: '1px solid #e5e7eb' }}>
            <Stack direction="row" justifyContent="space-between" mb={3}>
              <Box><Typography variant="h6" fontWeight={600}>Flujo de Conversaciones</Typography><Typography variant="caption" color="text.secondary">Últimos 6 meses</Typography></Box>
              <Button size="small" endIcon={<ArrowForward />} onClick={() => navigate('/conversations')} sx={{ textTransform: 'none', color: '#34d399', fontWeight: 600 }}>Ver todo</Button>
            </Stack>
            {activity.length ? (
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={activity}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                  <XAxis dataKey="month" stroke="#6c757d" fontSize={12} />
                  <YAxis stroke="#6c757d" fontSize={12} />
                  <Tooltip contentStyle={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 8 }} />
                  <Line type="monotone" dataKey="value" stroke="#34d399" strokeWidth={3} dot={{ fill: '#34d399', r: 6 }} activeDot={{ r: 8 }} />
                </LineChart>
              </ResponsiveContainer>
            ) : <EmptyMsg text="No hay datos de actividad disponibles" />}
          </Card>
        </Grid>

        {/* Distribuidores */}
        <Grid item xs={12} lg={4}>
          <Card sx={{ p: 3, borderRadius: 4, border: '1px solid #e5e7eb', height: '100%' }}>
            <Stack direction="row" justifyContent="space-between" mb={2}>
              <Typography variant="h6" fontWeight={600}>Por Nivel</Typography>
              <IconButton size="small" onClick={() => navigate('/distributors')}><MoreVert fontSize="small" /></IconButton>
            </Stack>
            {dist.length ? (
              <>
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie data={dist} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={5} dataKey="value">
                      {dist.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Pie>
                    <Tooltip contentStyle={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 8 }} />
                  </PieChart>
                </ResponsiveContainer>
                <Stack spacing={1.5} mt={2}>
                  {dist.map((d, i) => (
                    <Stack key={i} direction="row" justifyContent="space-between" alignItems="center">
                      <Stack direction="row" spacing={1} alignItems="center">
                        <Box sx={{ width: 12, height: 12, borderRadius: 1, bgcolor: COLORS[i % COLORS.length] }} />
                        <Typography variant="body2">{d.name}</Typography>
                      </Stack>
                      <Typography variant="body2" fontWeight={600}>{d.value}</Typography>
                    </Stack>
                  ))}
                </Stack>
              </>
            ) : <EmptyMsg text="No hay datos disponibles" />}
          </Card>
        </Grid>

        {/* Conversaciones */}
        <Grid item xs={12}>
          <Card sx={{ p: 3, borderRadius: 4, border: '1px solid #e5e7eb' }}>
            <Stack direction="row" justifyContent="space-between" mb={3}>
              <Typography variant="h6" fontWeight={600}>Conversaciones Recientes</Typography>
              <Button size="small" endIcon={<ArrowForward />} onClick={() => navigate('/conversations')}
                sx={{ textTransform: 'none', color: '#34d399', fontWeight: 600 }}>Ver todas</Button>
            </Stack>
            {recent.length ? (
              <Grid container spacing={2}>
                {recent.map(r => <Grid item xs={12} sm={6} md={4} key={r.id}><ConversationCard c={r} /></Grid>)}
              </Grid>
            ) : <EmptyMsg text="No hay conversaciones recientes" />}
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

// ---------- Mensaje vacío ----------
const EmptyMsg = ({ text }) => (
  <Box sx={{ height: 280, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
    <Typography variant="body2" color="text.secondary">{text}</Typography>
  </Box>
);
