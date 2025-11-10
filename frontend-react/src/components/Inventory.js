// frontend-react/src/components/Inventory.js
import React, { useState, useEffect } from 'react';
import {
    Box, Card, Grid, Typography, Tabs, Tab, CircularProgress, Alert, alpha, Stack,
    Button, IconButton, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
    Dialog, DialogTitle, DialogContent, DialogActions, TextField, MenuItem, Chip,
    InputAdornment, Paper, TablePagination,
} from '@mui/material';
import {
    Store, Inventory2, ShoppingCart, Assessment, Add, Refresh, Edit, Delete,
    Search, FilterList, TrendingUp,
} from '@mui/icons-material';
import { useSnackbar } from 'notistack';
import axios from 'axios';

// Configuración de API
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_URL = `${API_BASE}/api/v1/inventory`;

// Cliente axios configurado
const apiClient = axios.create({
    baseURL: API_URL,
    headers: { 'Content-Type': 'application/json' }
});

// Interceptor para agregar token
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) config.headers.Authorization = `Bearer ${token}`;
        return config;
    },
    (error) => Promise.reject(error)
);

// ==================== COMPONENTES DE UTILIDAD ====================
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

    // Estados para datos
    const [vendedores, setVendedores] = useState([]);
    const [productos, setProductos] = useState([]);
    const [stock, setStock] = useState([]);
    const [ventas, setVentas] = useState([]);

    // Diálogos
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
            if (currentTab === 0) {
                const { data } = await apiClient.get('/vendedores', {
                    params: { search, limit: 100 }
                });
                setVendedores(data);
            } else if (currentTab === 1) {
                const { data } = await apiClient.get('/productos', {
                    params: { search, limit: 100 }
                });
                setProductos(data);
            } else if (currentTab === 2) {
                const { data } = await apiClient.get('/stock', {
                    params: { limit: 100 }
                });
                setStock(data);
            } else if (currentTab === 3) {
                const { data } = await apiClient.get('/ventas', {
                    params: { limit: 100 }
                });
                setVentas(data);
            }
        } catch (err) {
            enqueueSnackbar('Error al cargar datos: ' + (err.response?.data?.detail || err.message), { variant: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const formatCurrency = (value) => {
        return new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: 'COP',
            minimumFractionDigits: 0,
        }).format(value || 0);
    };

    // ==================== MANEJO DE DIÁLOGOS ====================
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
                if (editingItem) {
                    await apiClient.put(`/vendedores/${editingItem.id}`, formData);
                    enqueueSnackbar('Vendedor actualizado', { variant: 'success' });
                } else {
                    await apiClient.post('/vendedores', formData);
                    enqueueSnackbar('Vendedor creado', { variant: 'success' });
                }
            } else if (dialogType === 'producto') {
                if (editingItem) {
                    await apiClient.put(`/productos/${editingItem.id}`, formData);
                    enqueueSnackbar('Producto actualizado', { variant: 'success' });
                } else {
                    await apiClient.post('/productos', formData);
                    enqueueSnackbar('Producto creado', { variant: 'success' });
                }
            } else if (dialogType === 'stock') {
                await apiClient.post('/stock/asignar', formData);
                enqueueSnackbar('Stock asignado', { variant: 'success' });
            } else if (dialogType === 'venta') {
                if (editingItem) {
                    await apiClient.put(`/ventas/${editingItem.id}`, formData);
                    enqueueSnackbar('Venta actualizada', { variant: 'success' });
                } else {
                    await apiClient.post('/ventas', formData);
                    enqueueSnackbar('Venta registrada', { variant: 'success' });
                }
            }
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
            if (type === 'vendedor') {
                await apiClient.delete(`/vendedores/${id}`);
            } else if (type === 'producto') {
                await apiClient.delete(`/productos/${id}`);
            } else if (type === 'venta') {
                await apiClient.delete(`/ventas/${id}`);
            }

            enqueueSnackbar('Eliminado correctamente', { variant: 'success' });
            loadData();
            loadStats();
        } catch (err) {
            enqueueSnackbar(err.response?.data?.detail || 'Error al eliminar', { variant: 'error' });
        }
    };

    // ==================== RENDERIZADO DE TABLAS ====================
    const renderVendedoresTable = () => (
        <TableContainer component={Paper} sx={{ boxShadow: 'none', border: '1px solid #e5e7eb' }}>
            <Table>
                <TableHead sx={{ bgcolor: '#f9fafb' }}>
                    <TableRow>
                        <TableCell sx={{ fontWeight: 600 }}>Nombre</TableCell>
                        <TableCell>Teléfono</TableCell>
                        <TableCell>Ciudad</TableCell>
                        <TableCell>Estado</TableCell>
                        <TableCell align="right">Acciones</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {vendedores.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((v) => (
                        <TableRow key={v.id} hover>
                            <TableCell sx={{ fontWeight: 500 }}>{v.nombre}</TableCell>
                            <TableCell>{v.telefono}</TableCell>
                            <TableCell>{v.ciudad || '-'}</TableCell>
                            <TableCell>
                                <Chip
                                    label={v.estado}
                                    size="small"
                                    color={v.estado === 'activo' ? 'success' : 'default'}
                                />
                            </TableCell>
                            <TableCell align="right">
                                <IconButton size="small" onClick={() => handleOpenDialog('vendedor', v)}>
                                    <Edit fontSize="small" />
                                </IconButton>
                                <IconButton size="small" onClick={() => handleDelete('vendedor', v.id)}>
                                    <Delete fontSize="small" />
                                </IconButton>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
            <TablePagination
                component="div"
                count={vendedores.length}
                page={page}
                onPageChange={(e, newPage) => setPage(newPage)}
                rowsPerPage={rowsPerPage}
                onRowsPerPageChange={(e) => setRowsPerPage(parseInt(e.target.value, 10))}
            />
        </TableContainer>
    );

    const renderProductosTable = () => (
        <TableContainer component={Paper} sx={{ boxShadow: 'none', border: '1px solid #e5e7eb' }}>
            <Table>
                <TableHead sx={{ bgcolor: '#f9fafb' }}>
                    <TableRow>
                        <TableCell sx={{ fontWeight: 600 }}>Nombre</TableCell>
                        <TableCell>Código</TableCell>
                        <TableCell>Categoría</TableCell>
                        <TableCell align="right">Precio</TableCell>
                        <TableCell>Estado</TableCell>
                        <TableCell align="right">Acciones</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {productos.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((p) => (
                        <TableRow key={p.id} hover>
                            <TableCell sx={{ fontWeight: 500 }}>{p.nombre}</TableCell>
                            <TableCell>{p.codigo}</TableCell>
                            <TableCell>{p.categoria || '-'}</TableCell>
                            <TableCell align="right">{formatCurrency(p.precio_unitario)}</TableCell>
                            <TableCell>
                                <Chip
                                    label={p.estado}
                                    size="small"
                                    color={p.estado === 'activo' ? 'success' : 'default'}
                                />
                            </TableCell>
                            <TableCell align="right">
                                <IconButton size="small" onClick={() => handleOpenDialog('producto', p)}>
                                    <Edit fontSize="small" />
                                </IconButton>
                                <IconButton size="small" onClick={() => handleDelete('producto', p.id)}>
                                    <Delete fontSize="small" />
                                </IconButton>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
            <TablePagination
                component="div"
                count={productos.length}
                page={page}
                onPageChange={(e, newPage) => setPage(newPage)}
                rowsPerPage={rowsPerPage}
                onRowsPerPageChange={(e) => setRowsPerPage(parseInt(e.target.value, 10))}
            />
        </TableContainer>
    );

    const renderStockTable = () => (
        <TableContainer component={Paper} sx={{ boxShadow: 'none', border: '1px solid #e5e7eb' }}>
            <Table>
                <TableHead sx={{ bgcolor: '#f9fafb' }}>
                    <TableRow>
                        <TableCell sx={{ fontWeight: 600 }}>Vendedor</TableCell>
                        <TableCell>Producto</TableCell>
                        <TableCell align="right">Stock Inicial</TableCell>
                        <TableCell align="right">Stock Actual</TableCell>
                        <TableCell>Última Actualización</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {stock.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((s) => (
                        <TableRow key={s.id} hover>
                            <TableCell sx={{ fontWeight: 500 }}>{s.vendedor?.nombre || '-'}</TableCell>
                            <TableCell>{s.producto?.nombre || '-'}</TableCell>
                            <TableCell align="right">{s.cantidad_inicial}</TableCell>
                            <TableCell align="right">
                                <Chip label={s.cantidad_actual} color={s.cantidad_actual > 0 ? 'success' : 'error'} size="small" />
                            </TableCell>
                            <TableCell>
                                {s.ultima_actualizacion ? new Date(s.ultima_actualizacion).toLocaleDateString() : '-'}
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
            <TablePagination
                component="div"
                count={stock.length}
                page={page}
                onPageChange={(e, newPage) => setPage(newPage)}
                rowsPerPage={rowsPerPage}
                onRowsPerPageChange={(e) => setRowsPerPage(parseInt(e.target.value, 10))}
            />
        </TableContainer>
    );

    const renderVentasTable = () => (
        <TableContainer component={Paper} sx={{ boxShadow: 'none', border: '1px solid #e5e7eb' }}>
            <Table>
                <TableHead sx={{ bgcolor: '#f9fafb' }}>
                    <TableRow>
                        <TableCell sx={{ fontWeight: 600 }}>Fecha</TableCell>
                        <TableCell>Vendedor</TableCell>
                        <TableCell>Producto</TableCell>
                        <TableCell align="right">Cantidad</TableCell>
                        <TableCell align="right">Precio</TableCell>
                        <TableCell align="right">Total</TableCell>
                        <TableCell align="right">Acciones</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {ventas.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((v) => (
                        <TableRow key={v.id} hover>
                            <TableCell>{new Date(v.fecha_venta).toLocaleDateString()}</TableCell>
                            <TableCell sx={{ fontWeight: 500 }}>{v.vendedor?.nombre || '-'}</TableCell>
                            <TableCell>{v.producto?.nombre || '-'}</TableCell>
                            <TableCell align="right">{v.cantidad}</TableCell>
                            <TableCell align="right">{formatCurrency(v.precio_venta)}</TableCell>
                            <TableCell align="right" sx={{ fontWeight: 600 }}>
                                {formatCurrency(v.cantidad * v.precio_venta)}
                            </TableCell>
                            <TableCell align="right">
                                <IconButton size="small" onClick={() => handleOpenDialog('venta', v)}>
                                    <Edit fontSize="small" />
                                </IconButton>
                                <IconButton size="small" onClick={() => handleDelete('venta', v.id)}>
                                    <Delete fontSize="small" />
                                </IconButton>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
            <TablePagination
                component="div"
                count={ventas.length}
                page={page}
                onPageChange={(e, newPage) => setPage(newPage)}
                rowsPerPage={rowsPerPage}
                onRowsPerPageChange={(e) => setRowsPerPage(parseInt(e.target.value, 10))}
            />
        </TableContainer>
    );

    // ==================== RENDERIZADO DE DIÁLOGO ====================
    const renderDialog = () => (
        <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
            <DialogTitle>
                {editingItem ? 'Editar' : 'Crear'} {dialogType}
            </DialogTitle>
            <DialogContent>
                <Stack spacing={2} sx={{ mt: 2 }}>
                    {dialogType === 'vendedor' && (
                        <>
                            <TextField
                                label="Nombre"
                                fullWidth
                                required
                                value={formData.nombre || ''}
                                onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                            />
                            <TextField
                                label="Teléfono"
                                fullWidth
                                required
                                value={formData.telefono || ''}
                                onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
                            />
                            <TextField
                                label="Email"
                                fullWidth
                                value={formData.email || ''}
                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            />
                            <TextField
                                label="Ciudad"
                                fullWidth
                                value={formData.ciudad || ''}
                                onChange={(e) => setFormData({ ...formData, ciudad: e.target.value })}
                            />
                        </>
                    )}

                    {dialogType === 'producto' && (
                        <>
                            <TextField
                                label="Nombre"
                                fullWidth
                                required
                                value={formData.nombre || ''}
                                onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                            />
                            <TextField
                                label="Código"
                                fullWidth
                                required
                                value={formData.codigo || ''}
                                onChange={(e) => setFormData({ ...formData, codigo: e.target.value })}
                            />
                            <TextField
                                label="Precio Unitario"
                                type="number"
                                fullWidth
                                required
                                value={formData.precio_unitario || ''}
                                onChange={(e) => setFormData({ ...formData, precio_unitario: parseFloat(e.target.value) })}
                            />
                            <TextField
                                label="Categoría"
                                fullWidth
                                value={formData.categoria || ''}
                                onChange={(e) => setFormData({ ...formData, categoria: e.target.value })}
                            />
                            <TextField
                                label="Descripción"
                                fullWidth
                                multiline
                                rows={3}
                                value={formData.descripcion || ''}
                                onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
                            />
                        </>
                    )}

                    {dialogType === 'stock' && (
                        <>
                            <TextField
                                select
                                label="Vendedor"
                                fullWidth
                                required
                                value={formData.vendedor_id || ''}
                                onChange={(e) => setFormData({ ...formData, vendedor_id: parseInt(e.target.value) })}
                            >
                                {vendedores.map((v) => (
                                    <MenuItem key={v.id} value={v.id}>
                                        {v.nombre}
                                    </MenuItem>
                                ))}
                            </TextField>
                            <TextField
                                select
                                label="Producto"
                                fullWidth
                                required
                                value={formData.producto_id || ''}
                                onChange={(e) => setFormData({ ...formData, producto_id: parseInt(e.target.value) })}
                            >
                                {productos.map((p) => (
                                    <MenuItem key={p.id} value={p.id}>
                                        {p.nombre}
                                    </MenuItem>
                                ))}
                            </TextField>
                            <TextField
                                label="Cantidad"
                                type="number"
                                fullWidth
                                required
                                value={formData.cantidad || ''}
                                onChange={(e) => setFormData({ ...formData, cantidad: parseInt(e.target.value) })}
                            />
                        </>
                    )}

                    {dialogType === 'venta' && (
                        <>
                            <TextField
                                select
                                label="Vendedor"
                                fullWidth
                                required
                                value={formData.vendedor_id || ''}
                                onChange={(e) => setFormData({ ...formData, vendedor_id: parseInt(e.target.value) })}
                            >
                                {vendedores.map((v) => (
                                    <MenuItem key={v.id} value={v.id}>
                                        {v.nombre}
                                    </MenuItem>
                                ))}
                            </TextField>
                            <TextField
                                select
                                label="Producto"
                                fullWidth
                                required
                                value={formData.producto_id || ''}
                                onChange={(e) => setFormData({ ...formData, producto_id: parseInt(e.target.value) })}
                            >
                                {productos.map((p) => (
                                    <MenuItem key={p.id} value={p.id}>
                                        {p.nombre} - {formatCurrency(p.precio_unitario)}
                                    </MenuItem>
                                ))}
                            </TextField>
                            <TextField
                                label="Cantidad"
                                type="number"
                                fullWidth
                                required
                                value={formData.cantidad || ''}
                                onChange={(e) => setFormData({ ...formData, cantidad: parseInt(e.target.value) })}
                            />
                            <TextField
                                label="Precio de Venta"
                                type="number"
                                fullWidth
                                value={formData.precio_venta || ''}
                                onChange={(e) => setFormData({ ...formData, precio_venta: parseFloat(e.target.value) })}
                                helperText="Dejar vacío para usar el precio del producto"
                            />
                            <TextField
                                label="Notas"
                                fullWidth
                                multiline
                                rows={2}
                                value={formData.notas || ''}
                                onChange={(e) => setFormData({ ...formData, notas: e.target.value })}
                            />
                        </>
                    )}
                </Stack>
            </DialogContent>
            <DialogActions>
                <Button onClick={handleCloseDialog}>Cancelar</Button>
                <Button onClick={handleSave} variant="contained" sx={{ bgcolor: '#34d399' }}>
                    Guardar
                </Button>
            </DialogActions>
        </Dialog>
    );

    // ==================== RENDERIZADO PRINCIPAL ====================
    const statCards = [
        {
            title: 'Vendedores Activos',
            value: stats.total_vendedores || 0,
            icon: <Store sx={{ fontSize: 28, color: '#fff' }} />,
            color: '#3b82f6',
        },
        {
            title: 'Productos',
            value: stats.total_productos || 0,
            icon: <Inventory2 sx={{ fontSize: 28, color: '#fff' }} />,
            color: '#34d399',
        },
        {
            title: 'Stock Total',
            value: stats.stock_total || 0,
            icon: <Assessment sx={{ fontSize: 28, color: '#fff' }} />,
            color: '#f59e0b',
            subtitle: formatCurrency(stats.valor_inventario),
        },
        {
            title: 'Ventas del Mes',
            value: stats.ventas_mes || 0,
            icon: <ShoppingCart sx={{ fontSize: 28, color: '#fff' }} />,
            color: '#8b5cf6',
            subtitle: formatCurrency(stats.valor_ventas_mes),
        },
    ];

    return (
        <Box>
            {/* Header */}
            <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
                <Box>
                    <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>
                        Gestión de Inventario
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Control de centros de distribución
                    </Typography>
                </Box>
                <IconButton onClick={() => { loadData(); loadStats(); }} sx={{ bgcolor: alpha('#34d399', 0.1) }}>
                    <Refresh sx={{ color: '#34d399' }} />
                </IconButton>
            </Stack>

            {/* Stats Cards */}
            <Grid container spacing={3} mb={3}>
                {statCards.map((card, i) => (
                    <Grid item xs={12} sm={6} lg={3} key={i}>
                        <StatCard {...card} />
                    </Grid>
                ))}
            </Grid>

            {/* Tabs */}
            <Card sx={{ borderRadius: 3, border: '1px solid #e5e7eb' }}>
                <Box sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}>
                    <Tabs
                        value={currentTab}
                        onChange={(e, v) => {
                            setCurrentTab(v);
                            setPage(0);
                        }}
                        sx={{
                            '& .MuiTab-root': { textTransform: 'none', fontWeight: 600 },
                            '& .Mui-selected': { color: '#34d399' },
                            '& .MuiTabs-indicator': { bgcolor: '#34d399' },
                        }}
                    >
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
                            InputProps={{
                                startAdornment: (
                                    <InputAdornment position="start">
                                        <Search />
                                    </InputAdornment>
                                ),
                            }}
                            sx={{ flexGrow: 1 }}
                        />
                        <Button
                            variant="contained"
                            startIcon={<Add />}
                            onClick={() => {
                                const types = ['vendedor', 'producto', 'stock', 'venta'];
                                handleOpenDialog(types[currentTab]);
                            }}
                            sx={{ bgcolor: '#34d399', '&:hover': { bgcolor: '#10b981' } }}
                        >
                            Nuevo
                        </Button>
                    </Stack>

                    {/* Tablas */}
                    {loading ? (
                        <Box display="flex" justifyContent="center" py={4}>
                            <CircularProgress sx={{ color: '#34d399' }} />
                        </Box>
                    ) : (
                        <>
                            {currentTab === 0 && renderVendedoresTable()}
                            {currentTab === 1 && renderProductosTable()}
                            {currentTab === 2 && renderStockTable()}
                            {currentTab === 3 && renderVentasTable()}
                        </>
                    )}
                </Box>
            </Card>

            {/* Diálogo */}
            {renderDialog()}
        </Box>
    );
}

export default Inventory;