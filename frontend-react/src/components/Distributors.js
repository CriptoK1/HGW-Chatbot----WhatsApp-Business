import React, { useState, useEffect, useCallback } from 'react';
import {
  Box, Button, Card, Dialog, DialogActions, DialogContent, DialogTitle,
  TextField, Grid, IconButton, Chip, MenuItem, InputAdornment, Typography,
  Tooltip, alpha, Avatar, Stack, Divider, useTheme, useMediaQuery, Paper,
} from '@mui/material';
import { DataGrid, GridToolbar, esES } from '@mui/x-data-grid';
import {
  Edit, Delete, Search, CheckCircle, Block, PersonAdd,
  Phone, Email, Star, Visibility, VisibilityOff,
} from '@mui/icons-material';
import { useSnackbar } from 'notistack';
import { useForm, Controller } from 'react-hook-form';
import { format } from 'date-fns';
import api from '../api/apiClient';

const NIVEL = { Diamante: '#00bcd4', Platino: '#9e8a97', Oro: '#facc15', Plata: '#c0c0c0', Master: '#8b5cf6', Senior: '#3b82f6', Junior: '#10b981', 'Pre-Junior': '#6c757d' };
const ESTADO = { activo: '#10b981', suspendido: '#f59e0b', inactivo: '#ef4444' };

const initialForm = {
  nombres: '', apellidos: '', telefono: '', email: '', usuario: '', contrasena: '',
  contrasena_doble_factor: '', fecha_ingreso: format(new Date(), 'yyyy-MM-dd'),
  fecha_cumpleanos: '', nivel: 'Pre-Junior', estado: 'activo', notas: '',
};

function Distributors() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { enqueueSnackbar } = useSnackbar();
  const [mostrarPass, setMostrarPass] = useState({});
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [edit, setEdit] = useState(false);
  const [selected, setSelected] = useState(null);
  const [search, setSearch] = useState('');
  const [filterE, setFilterE] = useState('');
  const [filterN, setFilterN] = useState('');
  const { control, handleSubmit, reset, formState: { errors } } = useForm({ defaultValues: initialForm });

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const params = {};
      if (search) params.search = search;
      if (filterE) params.estado = filterE;
      if (filterN) params.nivel = filterN;
      setData(await api.getDistributors(params));
    } catch (e) {
      enqueueSnackbar('Error al cargar', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  }, [search, filterE, filterN, enqueueSnackbar]);

  useEffect(() => { load(); }, [load]);

  const openDialog = (d = null) => {
    if (d) {
      setEdit(true);
      setSelected(d);
      reset({
        ...d,
        fecha_ingreso: d.fecha_ingreso ? format(new Date(d.fecha_ingreso), 'yyyy-MM-dd') : '',
        fecha_cumpleanos: d.fecha_cumpleanos ? format(new Date(d.fecha_cumpleanos), 'yyyy-MM-dd') : '',
        contrasena: '', contrasena_doble_factor: '',
      });
    } else {
      setEdit(false);
      setSelected(null);
      reset(initialForm);
    }
    setOpen(true);
  };

  const closeDialog = () => {
    setOpen(false);
    setEdit(false);
    setSelected(null);
    reset(initialForm);
  };

  const onSubmit = async (d) => {
    try {
      const p = {
        nombres: d.nombres?.trim() ?? '', apellidos: d.apellidos?.trim() ?? '',
        telefono: d.telefono?.trim() ?? '', usuario: d.usuario?.trim() ?? '',
        nivel: d.nivel || 'Pre-Junior', estado: d.estado || 'activo',
      };

      ['fecha_ingreso', 'fecha_cumpleanos'].forEach(f => {
        if (d[f]) {
          const dt = new Date(d[f]);
          if (!isNaN(dt.getTime())) p[f] = dt.toISOString().split('T')[0];
        }
      });

      if (d.email?.trim()) p.email = d.email.trim();
      if (d.notas?.trim()) p.notas = d.notas.trim();

      if (edit) {
        if (d.contrasena?.trim()) {
          if (d.contrasena.trim().length < 6) return enqueueSnackbar('Contraseña mínimo 6 caracteres', { variant: 'error' });
          p.contrasena = d.contrasena.trim();
        }
        if (d.contrasena_doble_factor?.trim()) p.contrasena_doble_factor = d.contrasena_doble_factor.trim();
      } else {
        const pw = d.contrasena?.trim();
        if (!pw || pw.length < 6) return enqueueSnackbar('Contraseña mínimo 6 caracteres', { variant: 'error' });
        p.contrasena = pw;
        if (d.contrasena_doble_factor?.trim()) p.contrasena_doble_factor = d.contrasena_doble_factor.trim();
      }

      if (edit) {
        await api.updateDistributor(selected.id, p);
        enqueueSnackbar('Actualizado', { variant: 'success' });
      } else {
        await api.createDistributor(p);
        enqueueSnackbar('Creado', { variant: 'success' });
      }
      closeDialog();
      await load();
    } catch (e) {
      const r = e.response?.data?.detail;
      if (Array.isArray(r) && r.length) {
        enqueueSnackbar(`${r[0].loc?.join(' > ')} - ${r[0].msg}`, { variant: 'error' });
      } else if (typeof r === 'string') {
        enqueueSnackbar(r, { variant: 'error' });
      } else {
        enqueueSnackbar('Error al guardar', { variant: 'error' });
      }
    }
  };

  const del = async (id) => {
    if (window.confirm('¿Eliminar?')) {
      try {
        await api.deleteDistributor(id);
        enqueueSnackbar('Eliminado', { variant: 'success' });
        load();
      } catch (e) {
        enqueueSnackbar('Error', { variant: 'error' });
      }
    }
  };

  const toggle = async (id, estado) => {
    try {
      if (estado === 'activo') {
        await api.suspendDistributor(id);
        enqueueSnackbar('Suspendido', { variant: 'warning' });
      } else {
        await api.activateDistributor(id);
        enqueueSnackbar('Activado', { variant: 'success' });
      }
      load();
    } catch (e) {
      enqueueSnackbar('Error', { variant: 'error' });
    }
  };

  const initials = (n, a) => ((n?.charAt(0) || '') + (a?.charAt(0) || '')).toUpperCase() || '?';
  const togglePass = (id, c) => setMostrarPass(p => ({ ...p, [`${id}_${c}`]: !p[`${id}_${c}`] }));

  const Actions = ({ d }) => (
    <Box sx={{ display: 'flex', gap: 0.5 }}>
      <Tooltip title="Editar">
        <IconButton size="small" onClick={() => openDialog(d)} sx={{ color: '#3b82f6' }}>
          <Edit fontSize="small" />
        </IconButton>
      </Tooltip>
      <Tooltip title={d.estado === 'activo' ? 'Suspender' : 'Activar'}>
        <IconButton size="small" onClick={() => toggle(d.id, d.estado)}
          sx={{ color: d.estado === 'activo' ? '#f59e0b' : '#10b981' }}>
          {d.estado === 'activo' ? <Block fontSize="small" /> : <CheckCircle fontSize="small" />}
        </IconButton>
      </Tooltip>
      <Tooltip title="Eliminar">
        <IconButton size="small" onClick={() => del(d.id)} sx={{ color: '#ef4444' }}>
          <Delete fontSize="small" />
        </IconButton>
      </Tooltip>
    </Box>
  );

  const DistCard = ({ d }) => {
    const nc = NIVEL[d.nivel] || '#6c757d';
    const ec = ESTADO[d.estado] || '#6c757d';
    const showPass = mostrarPass[`${d.id}_contrasena`];
    const show2FA = mostrarPass[`${d.id}_contrasena_doble_factor`];
    return (
      <Card sx={{ mb: 2, borderRadius: 2, border: '1px solid #e5e7eb', '&:hover': { boxShadow: '0 4px 12px rgba(0,0,0,0.12)' } }}>
        <Box sx={{ p: 2 }}>
          <Box sx={{ display: 'flex', mb: 1.5 }}>
            <Avatar sx={{
              width: 48, height: 48, mr: 1.5,
              background: `linear-gradient(135deg, ${nc} 0%, ${alpha(nc, 0.7)} 100%)`,
              color: '#fff', fontWeight: 700,
            }}>{initials(d.nombres, d.apellidos)}</Avatar>
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography variant="subtitle1" sx={{
                fontWeight: 600, fontSize: '0.95rem', mb: 0.5,
                overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'
              }}>
                {d.nombre_completo}
              </Typography>
              <Box sx={{ display: 'flex', gap: 0.5 }}>
                <Chip icon={<Star sx={{ fontSize: 12 }} />} label={d.nivel} size="small"
                  sx={{ backgroundColor: alpha(nc, 0.15), color: nc, height: 22, fontSize: '0.7rem', fontWeight: 600 }} />
                <Chip label={d.estado} size="small"
                  sx={{ backgroundColor: alpha(ec, 0.15), color: ec, height: 22, fontSize: '0.7rem', fontWeight: 600 }} />
              </Box>
            </Box>
          </Box>
          <Divider sx={{ my: 1.5 }} />
          <Stack spacing={1}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Phone sx={{ fontSize: 16, color: '#10b981', mr: 1 }} />
              <Typography variant="body2">{d.telefono}</Typography>
            </Box>
            {d.email && (
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Email sx={{ fontSize: 16, color: '#3b82f6', mr: 1 }} />
                <Typography variant="body2" sx={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{d.email}</Typography>
              </Box>
            )}
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', backgroundColor: '#f9fafb', p: 1, borderRadius: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', flex: 1, minWidth: 0 }}>
                <Typography variant="caption" sx={{ color: '#6c757d', mr: 1, minWidth: 50, fontWeight: 600 }}>Contraseña:</Typography>
                <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.85rem', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {showPass ? (d.contrasena_texto || 'N/A') : '•'.repeat((d.contrasena_texto?.length || 8))}
                </Typography>
              </Box>
              <IconButton size="small" onClick={() => togglePass(d.id, 'contrasena')} sx={{ ml: 0.5 }}>
                {showPass ? <VisibilityOff sx={{ fontSize: 16 }} /> : <Visibility sx={{ fontSize: 16, color: '#10b981' }} />}
              </IconButton>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', backgroundColor: '#f9fafb', p: 1, borderRadius: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', flex: 1, minWidth: 0 }}>
                <Typography variant="caption" sx={{ color: '#6c757d', mr: 1, minWidth: 50, fontWeight: 600 }}>2FA:</Typography>
                <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.85rem', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {show2FA ? (d.contrasena_2fa_texto || 'N/A') : '•'.repeat((d.contrasena_2fa_texto?.length || 8))}
                </Typography>
              </Box>
              <IconButton size="small" onClick={() => togglePass(d.id, 'contrasena_doble_factor')} sx={{ ml: 0.5 }}>
                {show2FA ? <VisibilityOff sx={{ fontSize: 16 }} /> : <Visibility sx={{ fontSize: 16, color: '#10b981' }} />}
              </IconButton>
            </Box>
          </Stack>
          <Divider sx={{ my: 1.5 }} />
          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}><Actions d={d} /></Box>
        </Box>
      </Card>
    );
  };

  const cols = [
    { field: 'id', headerName: 'ID', width: 70, align: 'center' },
    {
      field: 'nombre_completo', headerName: 'Distribuidor', flex: 1, minWidth: 200,
      renderCell: (p) => {
        const nc = NIVEL[p.row.nivel] || '#6c757d';
        return (
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Avatar sx={{
              width: 36, height: 36, mr: 1.5,
              background: `linear-gradient(135deg, ${nc}, ${alpha(nc, 0.7)})`,
              color: '#fff', fontWeight: 700
            }}>{initials(p.row.nombres, p.row.apellidos)}</Avatar>
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>{p.value}</Typography>
              <Typography variant="caption" sx={{ color: '#6c757d' }}>@{p.row.usuario}</Typography>
            </Box>
          </Box>
        );
      },
    },
    {
      field: 'telefono', headerName: 'Teléfono', width: 130,
      renderCell: (p) => (
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Phone sx={{ fontSize: 16, color: '#10b981', mr: 1 }} />
          <Typography variant="body2">{p.value}</Typography>
        </Box>
      ),
    },
    { field: 'email', headerName: 'Email', width: 180 },
    {
      field: 'contrasena_texto', headerName: 'Contraseña', width: 160,
      renderCell: (p) => {
        const v = mostrarPass[`${p.row.id}_contrasena`];
        return (
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography sx={{ fontFamily: 'monospace', mr: 1, fontSize: '0.875rem' }}>
              {v ? p.value : '•'.repeat(p.value?.length || 8)}
            </Typography>
            <IconButton size="small" onClick={() => togglePass(p.row.id, 'contrasena')}>
              {v ? <VisibilityOff sx={{ fontSize: 16 }} /> : <Visibility sx={{ fontSize: 16, color: '#10b981' }} />}
            </IconButton>
          </Box>
        );
      }
    },
    {
      field: 'contrasena_2fa_texto', headerName: '2FA', width: 160,
      renderCell: (p) => {
        const v = mostrarPass[`${p.row.id}_contrasena_doble_factor`];
        return (
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography sx={{ fontFamily: 'monospace', mr: 1, fontSize: '0.875rem' }}>
              {v ? p.value : '•'.repeat(p.value?.length || 8)}
            </Typography>
            <IconButton size="small" onClick={() => togglePass(p.row.id, 'contrasena_doble_factor')}>
              {v ? <VisibilityOff sx={{ fontSize: 16 }} /> : <Visibility sx={{ fontSize: 16, color: '#10b981' }} />}
            </IconButton>
          </Box>
        );
      }
    },
    {
      field: 'nivel', headerName: 'Nivel', width: 120,
      renderCell: (p) => {
        const c = NIVEL[p.value] || '#6c757d';
        return (
          <Chip icon={<Star sx={{ fontSize: 12 }} />} label={p.value} size="small"
            sx={{ backgroundColor: alpha(c, 0.15), color: c, fontWeight: 600 }} />
        );
      },
    },
    {
      field: 'estado', headerName: 'Estado', width: 110,
      renderCell: (p) => {
        const c = ESTADO[p.value] || '#6c757d';
        return (
          <Chip label={p.value} size="small"
            sx={{ backgroundColor: alpha(c, 0.15), color: c, fontWeight: 600 }} />
        );
      },
    },
    {
      field: 'fecha_ingreso', headerName: 'F. Ingreso', width: 110,
      renderCell: (p) => p.value ? format(new Date(p.value), 'dd/MM/yyyy') : '-'
    },
    { field: 'actions', headerName: 'Acciones', width: 140, sortable: false, renderCell: (p) => <Actions d={p.row} /> },
  ];

  if (loading) return <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px"><Typography>Cargando...</Typography></Box>;

  return (
    <Box sx={{ px: { xs: 1, sm: 2 }, py: 2 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3} flexWrap="wrap" gap={2}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, fontSize: { xs: '1.5rem', sm: '2rem' } }}>Distribuidores</Typography>
          <Typography variant="body2" sx={{ color: '#6c757d' }}>Gestiona tu red</Typography>
        </Box>
        <Button variant="contained" startIcon={<PersonAdd />} onClick={() => openDialog()}
          size={isMobile ? "medium" : "large"}
          sx={{
            background: 'linear-gradient(135deg, #34d399, #10b981)', color: '#0a1f15', fontWeight: 600,
            '&:hover': { background: 'linear-gradient(135deg, #10b981, #059669)' }
          }}>
          {isMobile ? 'Nuevo' : 'Nuevo Distribuidor'}
        </Button>
      </Box>

      <Card sx={{ p: { xs: 1.5, sm: 2.5 }, mb: 3, borderRadius: 2 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={4}>
            <TextField fullWidth placeholder="Buscar..." value={search} onChange={(e) => setSearch(e.target.value)}
              size={isMobile ? "small" : "medium"}
              InputProps={{ startAdornment: <InputAdornment position="start"><Search /></InputAdornment> }} />
          </Grid>
          <Grid item xs={12} sm={3} md={3}>
            <TextField select fullWidth label="Estado" value={filterE} onChange={(e) => setFilterE(e.target.value)}
              size={isMobile ? "small" : "medium"}>
              <MenuItem value="">Todos</MenuItem>
              <MenuItem value="activo">Activo</MenuItem>
              <MenuItem value="inactivo">Inactivo</MenuItem>
              <MenuItem value="suspendido">Suspendido</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={3} md={3}>
            <TextField select fullWidth label="Nivel" value={filterN} onChange={(e) => setFilterN(e.target.value)}
              size={isMobile ? "small" : "medium"}>
              <MenuItem value="">Todos</MenuItem>
              <MenuItem value="Pre-Junior">Pre-Junior</MenuItem>
              <MenuItem value="Junior">Junior</MenuItem>
              <MenuItem value="Senior">Senior</MenuItem>
              <MenuItem value="Master">Master</MenuItem>
              <MenuItem value="Plata">Plata</MenuItem>
              <MenuItem value="Oro">Oro</MenuItem>
              <MenuItem value="Platino">Platino</MenuItem>
              <MenuItem value="Diamante">Diamante</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={12} md={2}>
            <Chip label={`Total: ${data.length}`} sx={{
              backgroundColor: alpha('#34d399', 0.15), color: '#10b981',
              fontWeight: 600, height: { xs: 32, sm: 40 }, width: '100%'
            }} />
          </Grid>
        </Grid>
      </Card>

      {isMobile ? (
        <Box>{data.length > 0 ? data.map(d => <DistCard key={d.id} d={d} />) :
          <Paper sx={{ p: 4, textAlign: 'center', borderRadius: 2 }}>
            <Typography>No hay distribuidores</Typography>
          </Paper>}
        </Box>
      ) : (
        <Card sx={{ borderRadius: 2, overflow: 'hidden' }}>
          <DataGrid rows={data} columns={cols} pageSize={10} autoHeight disableSelectionOnClick rowHeight={70}
            components={{ Toolbar: GridToolbar }} localeText={esES.components.MuiDataGrid.defaultProps.localeText}
            sx={{
              border: 'none', '& .MuiDataGrid-columnHeaders': { backgroundColor: '#f9fafb', fontWeight: 600 },
              '& .MuiDataGrid-row:hover': { backgroundColor: alpha('#34d399', 0.04) }
            }} />
        </Card>
      )}

      <Dialog open={open} onClose={closeDialog} maxWidth="md" fullWidth fullScreen={isMobile}>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogTitle sx={{ fontWeight: 600 }}>{edit ? 'Editar' : 'Nuevo'} Distribuidor</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 0.5 }}>
              <Grid item xs={12} sm={6}>
                <Controller name="nombres" control={control} rules={{ required: 'Requerido', minLength: { value: 2, message: 'Mín 2 chars' } }}
                  render={({ field }) => <TextField {...field} fullWidth label="Nombres *" error={!!errors.nombres}
                    helperText={errors.nombres?.message} size={isMobile ? "small" : "medium"} />} />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller name="apellidos" control={control} rules={{ required: 'Requerido', minLength: { value: 2, message: 'Mín 2 chars' } }}
                  render={({ field }) => <TextField {...field} fullWidth label="Apellidos *" error={!!errors.apellidos}
                    helperText={errors.apellidos?.message} size={isMobile ? "small" : "medium"} />} />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller name="telefono" control={control} rules={{ required: 'Requerido', minLength: { value: 7, message: 'Mín 7 dígitos' } }}
                  render={({ field }) => <TextField {...field} fullWidth label="Teléfono *" error={!!errors.telefono}
                    helperText={errors.telefono?.message} size={isMobile ? "small" : "medium"} />} />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller name="email" control={control}
                  render={({ field }) => <TextField {...field} fullWidth label="Email" type="email" size={isMobile ? "small" : "medium"} />} />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller name="fecha_ingreso" control={control} rules={{ required: 'Requerido' }}
                  render={({ field }) => <TextField {...field} fullWidth label="Fecha Ingreso *" type="date"
                    InputLabelProps={{ shrink: true }} error={!!errors.fecha_ingreso}
                    helperText={errors.fecha_ingreso?.message} size={isMobile ? "small" : "medium"} />} />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller name="fecha_cumpleanos" control={control}
                  render={({ field }) => <TextField {...field} fullWidth label="Cumpleaños" type="date"
                    InputLabelProps={{ shrink: true }} size={isMobile ? "small" : "medium"} />} />
              </Grid>
              <Grid item xs={12} sm={4}>
                <Controller name="usuario" control={control} rules={{ required: 'Requerido', minLength: { value: 3, message: 'Mín 3 chars' } }}
                  render={({ field }) => <TextField {...field} fullWidth label="Usuario *" error={!!errors.usuario}
                    helperText={errors.usuario?.message} size={isMobile ? "small" : "medium"} />} />
              </Grid>
              <Grid item xs={12} sm={4}>
                <Controller name="contrasena" control={control}
                  rules={{ required: !edit && 'Requerido', minLength: { value: 6, message: 'Mín 6 chars' } }}
                  render={({ field }) => <TextField {...field} fullWidth label={edit ? 'Nueva Contraseña' : 'Contraseña *'}
                    type="text" error={!!errors.contrasena} helperText={errors.contrasena?.message} size={isMobile ? "small" : "medium"} />} />
              </Grid>
              <Grid item xs={12} sm={4}>
                <Controller name="contrasena_doble_factor" control={control}
                  render={({ field }) => <TextField {...field} fullWidth label="2FA" type="text" size={isMobile ? "small" : "medium"} />} />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller name="nivel" control={control}
                  render={({ field }) => (
                    <TextField {...field} select fullWidth label="Nivel *" size={isMobile ? "small" : "medium"}>
                      <MenuItem value="Pre-Junior">Pre-Junior</MenuItem>
                      <MenuItem value="Junior">Junior</MenuItem>
                      <MenuItem value="Senior">Senior</MenuItem>
                      <MenuItem value="Master">Master</MenuItem>
                      <MenuItem value="Plata">Plata</MenuItem>
                      <MenuItem value="Oro">Oro</MenuItem>
                      <MenuItem value="Platino">Platino</MenuItem>
                      <MenuItem value="Diamante">Diamante</MenuItem>
                    </TextField>
                  )} />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller name="estado" control={control}
                  render={({ field }) => (
                    <TextField {...field} select fullWidth label="Estado *" size={isMobile ? "small" : "medium"}>
                      <MenuItem value="activo">Activo</MenuItem>
                      <MenuItem value="inactivo">Inactivo</MenuItem>
                      <MenuItem value="suspendido">Suspendido</MenuItem>
                    </TextField>
                  )} />
              </Grid>
              <Grid item xs={12}>
                <Controller name="notas" control={control}
                  render={({ field }) => <TextField {...field} fullWidth label="Notas" multiline rows={isMobile ? 2 : 3}
                    size={isMobile ? "small" : "medium"} />} />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions sx={{ p: { xs: 1.5, sm: 2.5 } }}>
            <Button onClick={closeDialog} size={isMobile ? "medium" : "large"}>Cancelar</Button>
            <Button type="submit" variant="contained" size={isMobile ? "medium" : "large"}
              sx={{
                background: 'linear-gradient(135deg, #34d399, #10b981)', color: '#0a1f15', fontWeight: 600,
                '&:hover': { background: 'linear-gradient(135deg, #10b981, #059669)' }
              }}>
              {edit ? 'Actualizar' : 'Crear'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
}

export default Distributors;