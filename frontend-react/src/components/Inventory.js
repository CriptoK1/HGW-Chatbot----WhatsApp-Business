// frontend-react/src/components/Inventory.js
import React, { useState, useEffect } from 'react';
import {
    Box, Card, Grid, Typography, Tabs, Tab, CircularProgress, Stack,
    Button, IconButton, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
    Dialog, DialogTitle, DialogContent, DialogActions, TextField, MenuItem, Chip,
    InputAdornment, Paper, TablePagination, alpha
} from '@mui/material';
import { Store, Inventory2, ShoppingCart, Assessment, Add, Refresh, Edit, Delete, Search } from '@mui/icons-material';
import { useSnackbar } from 'notistack';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_URL = `${API_BASE}/api/v1/inventory`;

const apiClient = axios.create({
    baseURL: API_URL,
    headers: { 'Content-Type': 'application/json' }
});

apiClient.interceptors.request.use(
    config => {
        const token = localStorage.getItem('token');
        if (token) config.headers.Authorization = `Bearer ${token}`;
        return config;
    },
    error => Promise.reject(error)
);

// ==================== COMPONENTE STAT CARD ====================
const StatCard = ({ title, value, icon, color, subtitle }) => (
    <Card
        sx={{
            p: 3,
            borderRadius: 3,
            background: `linear-gradient(135deg, ${color}20 0%, ${color}05 100%)`,
            border: `1px solid ${alpha(color, 0.2)}`,
            transition: 'all 0.3s ease',
            '&:hover': { transform: 'translateY(-4px)', boxShadow: `0 12px 24px ${alpha(color, 0.2)}` },
        }}
    >
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
            <Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>{title}</Typography>
                <Typography variant="h3" sx={{ fontWeight: 700 }}>{value}</Typography>
                {subtitle && <Typography variant="caption" color="text.secondary">{subtitle}</Typography>}
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
    </Card>
);

function Inventory() {
    const { enqueueSnackbar } = useSnackbar();
    const [currentTab, setCurrentTab] = useState(0);
    const [loading, setLoading] = useState(false);
    const [stats, setStats] = useState({});
    const [search, setSearch] = useState('');
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);

    const [vendedores, setVendedores] = useState([]);
    const [productos, setProductos] = useState([]);
    const [stock, setStock] = useState([]);
    const [ventas, setVentas] = useState([]);

    const [openDialog, setOpenDialog] = useState(false);
    const [dialogType, setDialogType] = useState('');
    const [editingItem, setEditingItem] = useState(null);
    const [formData, setFormData] = useState({});

    useEffect(() => {
        loadStats();
        loadData();
    }, [currentTab, search]);

    // ==================== CARGA DE DATOS ====================
    const loadStats = async () => {
        try {
            const { data } = await apiClient.get('/estadisticas/general');
            setStats(data);
        } catch (err) {
            console.error('Error cargando estadísticas:', err);
        }
    };

    const loadData = async () => {
        setLoading(true);
        try {
            const params = { search, limit: 100 };
            if (currentTab === 0) {
                const { data } = await apiClient.get('/vendedores', { params });
                setVendedores(data);
            } else if (currentTab === 1) {
                const { data } = await apiClient.get('/productos', { params });
                setProductos(data);
            } else if (currentTab === 2) {
                const { data } = await apiClient.get('/stock', { params: { limit: 100 } });
                setStock(data);
            } else if (currentTab === 3) {
                const { data } = await apiClient.get('/ventas', { params: { limit: 100 } });
                setVentas(data);
            }
        } catch (err) {
            enqueueSnackbar('Error al cargar datos: ' + (err.response?.data?.detail || err.message), { variant: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const formatCurrency = (value) =>
        new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 }).format(value || 0);

    // ==================== DIÁLOGOS ====================
    const handleOpenDialog = (type, item = null) => {
        setDialogType(type);
        setEditingItem(item);
        setFormData(item || {});
        setOpenDialog(true);
    };

    const handleCloseDialog = () => {
        setOpenDialog(false);
        setEditingItem(null);
        setFormData({});
    };

    const handleSave = async () => {
        try {
            if (dialogType === 'vendedor') {
                if (editingItem) await apiClient.put(`/vendedores/${editingItem.id}`, formData);
                else await apiClient.post('/vendedores', formData);
            } else if (dialogType === 'producto') {
                if (editingItem) await apiClient.put(`/productos/${editingItem.id}`, formData);
                else await apiClient.post('/productos', formData);
            } else if (dialogType === 'stock') {
                await apiClient.post('/stock/asignar', formData);
            } else if (dialogType === 'venta') {
                if (editingItem) await apiClient.put(`/ventas/${editingItem.id}`, formData);
                else await apiClient.post('/ventas', formData);
            }
            enqueueSnackbar(`${editingItem ? 'Actualizado' : 'Creado'} correctamente`, { variant: 'success' });
            handleCloseDialog();
            loadData();
            loadStats();
        } catch (err) {
            enqueueSnackbar(err.response?.data?.detail || 'Error al guardar', { variant: 'error' });
        }
    };

    const handleDelete = async (type, id) => {
        if (!window.confirm('¿Está seguro de eliminar este registro?')) return;
        try {
            await apiClient.delete(`/${type === 'vendedor' ? 'vendedores' : type === 'producto' ? 'productos' : 'ventas'}/${id}`);
            enqueueSnackbar('Eliminado correctamente', { variant: 'success' });
            loadData();
            loadStats();
        } catch (err) {
            enqueueSnackbar(err.response?.data?.detail || 'Error al eliminar', { variant: 'error' });
        }
    };

    // ==================== TABLAS ====================
    const renderTable = (data, columns, type) => (
        <TableContainer component={Paper} sx={{ boxShadow: 'none', border: '1px solid #e5e7eb' }}>
            <Table>
                <TableHead sx={{ bgcolor: '#f9fafb' }}>
                    <TableRow>
                        {columns.map((col) => (
                            <TableCell key={col.label} align={col.align || 'left'} sx={{ fontWeight: 600 }}>{col.label}</TableCell>
                        ))}
                        <TableCell align="right">Acciones</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {data.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((row) => (
                        <TableRow key={row.id} hover>
                            {columns.map((col) => (
                                <TableCell key={col.label} align={col.align || 'left'}>
                                    {col.render ? col.render(row) : row[col.key] || '-'}
                                </TableCell>
                            ))}
                            <TableCell align="right">
                                <IconButton size="small" onClick={() => handleOpenDialog(type, row)}><Edit fontSize="small" /></IconButton>
                                {type !== 'stock' && <IconButton size="small" onClick={() => handleDelete(type, row.id)}><Delete fontSize="small" /></IconButton>}
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
            <TablePagination
                component="div"
                count={data.length}
                page={page}
                onPageChange={(e, newPage) => setPage(newPage)}
                rowsPerPage={rowsPerPage}
                onRowsPerPageChange={(e) => setRowsPerPage(parseInt(e.target.value, 10))}
            />
        </TableContainer>
    );

    // ==================== RENDER PRINCIPAL ====================
    const statCards = [
        { title: 'Vendedores Activos', value: stats.total_vendedores || 0, icon: <Store sx={{ fontSize: 28, color: '#fff' }} />, color: '#3b82f6' },
        { title: 'Productos', value: stats.total_productos || 0, icon: <Inventory2 sx={{ fontSize: 28, color: '#fff' }} />, color: '#34d399' },
        { title: 'Stock Total', value: stats.stock_total || 0, icon: <Assessment sx={{ fontSize: 28, color: '#fff' }} />, color: '#f59e0b', subtitle: formatCurrency(stats.valor_inventario) },
        { title: 'Ventas del Mes', value: stats.ventas_mes || 0, icon: <ShoppingCart sx={{ fontSize: 28, color: '#fff' }} />, color: '#8b5cf6', subtitle: formatCurrency(stats.valor_ventas_mes) },
    ];

    return (
        <Box>
            {/* Header */}
            <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
                <Box>
                    <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>Gestión de Inventario</Typography>
                    <Typography variant="body2" color="text.secondary">Control de centros de distribución</Typography>
                </Box>
                <IconButton onClick={() => { loadData(); loadStats(); }} sx={{ bgcolor: alpha('#34d399', 0.1) }}>
                    <Refresh sx={{ color: '#34d399' }} />
                </IconButton>
            </Stack>

            {/* Stat Cards */}
            <Grid container spacing={3} mb={3}>
                {statCards.map((card, i) => <Grid item xs={12} sm={6} lg={3} key={i}><StatCard {...card} /></Grid>)}
            </Grid>

            {/* Tabs */}
            <Card sx={{ borderRadius: 3, border: '1px solid #e5e7eb' }}>
                <Box sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}>
                    <Tabs value={currentTab} onChange={(e, v) => { setCurrentTab(v); setPage(0); }}
                        sx={{ '& .MuiTab-root': { textTransform: 'none', fontWeight: 600 }, '& .Mui-selected': { color: '#34d399' }, '& .MuiTabs-indicator': { bgcolor: '#34d399' } }}>
                        <Tab label="Vendedores" icon={<Store />} iconPosition="start" />
                        <Tab label="Productos" icon={<Inventory2 />} iconPosition="start" />
                        <Tab label="Stock" icon={<Assessment />} iconPosition="start" />
                        <Tab label="Ventas" icon={<ShoppingCart />} iconPosition="start" />
                    </Tabs>
                </Box>

                <Box p={3}>
                    {/* Barra de búsqueda y botones */}
                    <Stack direction="row" spacing={2} mb={3}>
                        <TextField
                            placeholder="Buscar..."
                            size="small"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            InputProps={{ startAdornment: (<InputAdornment position="start"><Search /></InputAdornment>) }}
                            sx={{ flexGrow: 1 }}
                        />
                        <Button variant="contained" startIcon={<Add />}
                            onClick={() => handleOpenDialog(['vendedor', 'producto', 'stock', 'venta'][currentTab])}
                            sx={{ bgcolor: '#34d399', '&:hover': { bgcolor: '#10b981' } }}>Nuevo</Button>
                    </Stack>

                    {/* Tablas */}
                    {loading ? <Box display="flex" justifyContent="center" py={4}><CircularProgress sx={{ color: '#34d399' }} /></Box> :
                        <>
                            {currentTab === 0 && renderTable(vendedores, [
                                { label: 'Nombre', key: 'nombre' },
                                { label: 'Teléfono', key: 'telefono' },
                                { label: 'Ciudad', key: 'ciudad' },
                                { label: 'Estado', key: 'estado', render: (row) => <Chip label={row.estado} size="small" color={row.estado === 'activo' ? 'success' : 'default'} /> }
                            ], 'vendedor')}

                            {currentTab === 1 && renderTable(productos, [
                                { label: 'Nombre', key: 'nombre' },
                                { label: 'Código', key: 'codigo' },
                                { label: 'Categoría', key: 'categoria' },
                                { label: 'Precio', key: 'precio_unitario', align: 'right', render: (row) => formatCurrency(row.precio_unitario) },
                                { label: 'Estado', key: 'estado', render: (row) => <Chip label={row.estado} size="small" color={row.estado === 'activo' ? 'success' : 'default'} /> }
                            ], 'producto')}

                            {currentTab === 2 && renderTable(stock, [
                                { label: 'Vendedor', key: 'vendedor', render: (row) => row.vendedor?.nombre || '-' },
                                { label: 'Producto', key: 'producto', render: (row) => row.producto?.nombre || '-' },
                                { label: 'Stock Inicial', key: 'cantidad_inicial', align: 'right' },
                                { label: 'Stock Actual', key: 'cantidad_actual', align: 'right', render: (row) => <Chip label={row.cantidad_actual} color={row.cantidad_actual > 0 ? 'success' : 'error'} size="small" /> },
                                { label: 'Última Actualización', key: 'ultima_actualizacion', render: (row) => row.ultima_actualizacion ? new Date(row.ultima_actualizacion).toLocaleDateString() : '-' }
                            ], 'stock')}

                            {currentTab === 3 && renderTable(ventas, [
                                { label: 'Fecha', key: 'fecha_venta', render: (row) => new Date(row.fecha_venta).toLocaleDateString() },
                                { label: 'Vendedor', key: 'vendedor', render: (row) => row.vendedor?.nombre || '-' },
                                { label: 'Producto', key: 'producto', render: (row) => row.producto?.nombre || '-' },
                                { label: 'Cantidad', key: 'cantidad', align: 'right' },
                                { label: 'Precio', key: 'precio_venta', align: 'right', render: (row) => formatCurrency(row.precio_venta) },
                                { label: 'Total', key: 'total', align: 'right', render: (row) => formatCurrency(row.cantidad * row.precio_venta) }
                            ], 'venta')}
                        </>
                    }
                </Box>
            </Card>

            {/* Diálogo */}
            {openDialog && (
                <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
                    <DialogTitle>{editingItem ? 'Editar' : 'Crear'} {dialogType}</DialogTitle>
                    <DialogContent>
                        <Stack spacing={2} sx={{ mt: 2 }}>
                            {/* Aquí puedes mantener los TextFields según el dialogType como en tu código */}
                        </Stack>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={handleCloseDialog}>Cancelar</Button>
                        <Button onClick={handleSave} variant="contained" sx={{ bgcolor: '#34d399' }}>Guardar</Button>
                    </DialogActions>
                </Dialog>
            )}
        </Box>
    );
}

export default Inventory;
