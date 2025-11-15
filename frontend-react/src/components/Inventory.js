import React, { useState, useEffect } from 'react';
import {
    Box, Card, Grid, Typography, Tabs, Tab, CircularProgress, Stack, Button, IconButton,
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Dialog, DialogTitle,
    DialogContent, DialogActions, TextField, MenuItem, Chip, InputAdornment, Paper,
    TablePagination, alpha, useMediaQuery, useTheme, Tooltip, Collapse, Divider
} from '@mui/material';
import { Store, Inventory2, ShoppingCart, Assessment, Add, Refresh, Edit, Delete, Search, ExpandMore, ExpandLess } from '@mui/icons-material';
import { useSnackbar } from 'notistack';
import { useForm, Controller } from 'react-hook-form';
import api from '../api/apiClient';

const EC = { activo: '#10b981', inactivo: '#ef4444' };

const SC = ({ title, value, icon, color, subtitle }) => {
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

    return (
        <Card sx={{
            p: { xs: 1.5, sm: 3 },
            borderRadius: { xs: 2, sm: 4 },
            background: `linear-gradient(135deg, ${color}20, ${color}05)`,
            border: `1px solid ${alpha(color, 0.2)}`,
            transition: '0.3s',
            height: '100%',
            '&:hover': { transform: 'translateY(-4px)', boxShadow: `0 12px 24px ${alpha(color, 0.2)}` }
        }}>
            <Stack spacing={{ xs: 1, sm: 1.5 }}>
                <Stack direction="row" justifyContent="space-between" alignItems="flex-start" spacing={1}>
                    <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Typography variant="body2" sx={{ color: '#6c757d', fontWeight: 500, fontSize: { xs: '0.65rem', sm: '0.875rem' }, lineHeight: 1.2, mb: 0.5 }}>
                            {title}
                        </Typography>
                        <Typography variant={isMobile ? 'h5' : 'h3'} sx={{ fontWeight: 700, fontSize: { xs: '1.25rem', sm: '2.5rem' }, lineHeight: 1.1 }}>
                            {value}
                        </Typography>
                        {subtitle && (
                            <Typography variant="caption" color="text.secondary" sx={{ fontSize: { xs: '0.6rem', sm: '0.75rem' }, display: 'block', mt: 0.3, lineHeight: 1.2 }}>
                                {subtitle}
                            </Typography>
                        )}
                    </Box>
                    <Box sx={{
                        width: { xs: 40, sm: 56 },
                        height: { xs: 40, sm: 56 },
                        minWidth: { xs: 40, sm: 56 },
                        borderRadius: { xs: 2, sm: 3 },
                        background: `linear-gradient(135deg, ${color}, ${alpha(color, 0.8)})`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        boxShadow: `0 8px 16px ${alpha(color, 0.3)}`
                    }}>
                        {icon}
                    </Box>
                </Stack>
            </Stack>
        </Card>
    );
};

const MobileCard = ({ item, columns, type, onEdit, onDelete }) => {
    const [expanded, setExpanded] = useState(false);

    return (
        <Card sx={{ mb: 2, borderRadius: 2, border: '1px solid #e5e7eb' }}>
            <Box sx={{ p: 2 }}>
                <Stack spacing={1.5}>
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                        <Box sx={{ flex: 1 }}>
                            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 0.5 }}>
                                {columns[0].render ? columns[0].render(item) : item[columns[0].key]}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                {columns[1].render ? columns[1].render(item) : item[columns[1].key]}
                            </Typography>
                        </Box>
                        <Stack direction="row" spacing={0.5}>
                            <Tooltip title="Editar">
                                <IconButton size="small" onClick={() => onEdit(type, item)} sx={{ color: '#3b82f6' }}>
                                    <Edit fontSize="small" />
                                </IconButton>
                            </Tooltip>
                            {type !== 'stock' && (
                                <Tooltip title="Eliminar">
                                    <IconButton size="small" onClick={() => onDelete(type, item.id)} sx={{ color: '#ef4444' }}>
                                        <Delete fontSize="small" />
                                    </IconButton>
                                </Tooltip>
                            )}
                        </Stack>
                    </Stack>

                    {columns.length > 2 && (
                        <Stack direction="row" spacing={2} flexWrap="wrap">
                            {columns.slice(2, Math.min(4, columns.length)).map((col, idx) => (
                                <Box key={idx}>
                                    <Typography variant="caption" color="text.secondary" display="block">
                                        {col.label}
                                    </Typography>
                                    <Box sx={{ mt: 0.5 }}>
                                        {col.render ? col.render(item) : (
                                            <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                                {item[col.key] || '-'}
                                            </Typography>
                                        )}
                                    </Box>
                                </Box>
                            ))}
                        </Stack>
                    )}

                    {columns.length > 4 && (
                        <>
                            <Button
                                size="small"
                                onClick={() => setExpanded(!expanded)}
                                endIcon={expanded ? <ExpandLess /> : <ExpandMore />}
                                sx={{ alignSelf: 'flex-start', textTransform: 'none' }}
                            >
                                {expanded ? 'Ver menos' : 'Ver más'}
                            </Button>
                            <Collapse in={expanded}>
                                <Divider sx={{ my: 1 }} />
                                <Stack spacing={1}>
                                    {columns.slice(4).map((col, idx) => (
                                        <Box key={idx}>
                                            <Typography variant="caption" color="text.secondary" display="block">
                                                {col.label}
                                            </Typography>
                                            <Box sx={{ mt: 0.5 }}>
                                                {col.render ? col.render(item) : (
                                                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                                        {item[col.key] || '-'}
                                                    </Typography>
                                                )}
                                            </Box>
                                        </Box>
                                    ))}
                                </Stack>
                            </Collapse>
                        </>
                    )}
                </Stack>
            </Box>
        </Card>
    );
};

export default function Inventory() {
    const t = useTheme(), m = useMediaQuery(t.breakpoints.down('md')), isSmall = useMediaQuery(t.breakpoints.down('sm')), { enqueueSnackbar: sn } = useSnackbar();
    const [tab, setTab] = useState(0), [load, setLoad] = useState(false), [stats, setStats] = useState({}), [q, setQ] = useState(''), [p, setP] = useState(0), [rp, setRp] = useState(10);
    const [vnd, setVnd] = useState([]), [prd, setPrd] = useState([]), [stk, setStk] = useState([]), [vnt, setVnt] = useState([]);
    const [open, setOpen] = useState(false), [type, setType] = useState(''), [edit, setEdit] = useState(null);
    const { control, handleSubmit, reset, formState: { errors } } = useForm();

    const ls = async () => {
        try {
            setStats(await api.getEstadisticasInventario());
        } catch (e) {
            console.error(e);
        }
    };

    const ld = React.useCallback(async () => {
        setLoad(true);
        try {
            const params = { search: q, limit: 100 };
            if (tab === 0) setVnd(await api.getVendedores(params));
            else if (tab === 1) setPrd(await api.getProductos(params));
            else if (tab === 2) setStk(await api.getStock(params));
            else if (tab === 3) setVnt(await api.getVentas(params));
        } catch (e) {
            sn('Error: ' + (e.response?.data?.detail || e.message), { variant: 'error' });
        } finally {
            setLoad(false);
        }
    }, [tab, q, sn]);

    useEffect(() => { ls(); ld(); }, [ld]);

    const fc = v => new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 }).format(v || 0);
    const od = (tp, it = null) => { setType(tp); setEdit(it); reset(it || {}); setOpen(true); };
    const cd = () => { setOpen(false); setEdit(null); reset({}); };

    const os = async fd => {
        try {
            if (type === 'vendedor') {
                edit ? await api.updateVendedor(edit.id, fd) : await api.createVendedor(fd);
            } else if (type === 'producto') {
                edit ? await api.updateProducto(edit.id, fd) : await api.createProducto(fd);
            } else if (type === 'stock') {
                await api.asignarStock(fd);
            } else if (type === 'venta') {
                edit ? await api.updateVenta(edit.id, fd) : await api.createVenta(fd);
            }
            sn(`${edit ? 'Actualizado' : 'Creado'}`, { variant: 'success' });
            cd();
            ld();
            ls();
        } catch (e) {
            sn(e.response?.data?.detail || 'Error', { variant: 'error' });
        }
    };

    const del = async (tp, id) => {
        if (!window.confirm('¿Eliminar?')) return;
        try {
            if (tp === 'vendedor') await api.deleteVendedor(id);
            else if (tp === 'producto') await api.deleteProducto(id);
            else if (tp === 'venta') await api.deleteVenta(id);

            sn('Eliminado', { variant: 'success' });
            ld();
            ls();
        } catch (e) {
            sn('Error', { variant: 'error' });
        }
    };

    const rt = (d, cols, tp) => {
        if (m) {
            return (
                <Box>
                    {d.slice(p * rp, p * rp + rp).map(item => (
                        <MobileCard key={item.id} item={item} columns={cols} type={tp} onEdit={od} onDelete={del} />
                    ))}
                    <TablePagination component="div" count={d.length} page={p} onPageChange={(e, n) => setP(n)} rowsPerPage={rp} onRowsPerPageChange={e => { setRp(parseInt(e.target.value, 10)); setP(0); }} labelRowsPerPage="Filas:" sx={{ borderTop: '1px solid #e5e7eb' }} />
                </Box>
            );
        }

        return (
            <TableContainer component={Paper} sx={{ boxShadow: 'none', border: '1px solid #e5e7eb', borderRadius: 2 }}>
                <Table>
                    <TableHead sx={{ bgcolor: '#f9fafb' }}>
                        <TableRow>
                            {cols.map(c => <TableCell key={c.label} align={c.align || 'left'} sx={{ fontWeight: 600 }}>{c.label}</TableCell>)}
                            <TableCell align="right" sx={{ fontWeight: 600 }}>Acciones</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {d.slice(p * rp, p * rp + rp).map(r => (
                            <TableRow key={r.id} hover sx={{ '&:hover': { backgroundColor: alpha('#34d399', 0.04) } }}>
                                {cols.map(c => <TableCell key={c.label} align={c.align || 'left'}>{c.render ? c.render(r) : r[c.key] || '-'}</TableCell>)}
                                <TableCell align="right">
                                    <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'flex-end' }}>
                                        <Tooltip title="Editar">
                                            <IconButton size="small" onClick={() => od(tp, r)} sx={{ color: '#3b82f6' }}>
                                                <Edit fontSize="small" />
                                            </IconButton>
                                        </Tooltip>
                                        {tp !== 'stock' && (
                                            <Tooltip title="Eliminar">
                                                <IconButton size="small" onClick={() => del(tp, r.id)} sx={{ color: '#ef4444' }}>
                                                    <Delete fontSize="small" />
                                                </IconButton>
                                            </Tooltip>
                                        )}
                                    </Box>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
                <TablePagination component="div" count={d.length} page={p} onPageChange={(e, n) => setP(n)} rowsPerPage={rp} onRowsPerPageChange={e => { setRp(parseInt(e.target.value, 10)); setP(0); }} labelRowsPerPage="Filas:" />
            </TableContainer>
        );
    };

    const rdc = () => {
        const gs = { mt: 0.5 }, sz = isSmall ? 'small' : 'medium';
        if (type === 'vendedor') return (<Grid container spacing={2} sx={gs}><Grid item xs={12} sm={6}><Controller name="nombre" control={control} rules={{ required: 'Requerido' }} render={({ field }) => <TextField {...field} fullWidth label="Nombre *" error={!!errors.nombre} helperText={errors.nombre?.message} size={sz} />} /></Grid><Grid item xs={12} sm={6}><Controller name="telefono" control={control} rules={{ required: 'Requerido' }} render={({ field }) => <TextField {...field} fullWidth label="Teléfono *" error={!!errors.telefono} helperText={errors.telefono?.message} size={sz} />} /></Grid><Grid item xs={12} sm={6}><Controller name="ciudad" control={control} render={({ field }) => <TextField {...field} fullWidth label="Ciudad" size={sz} />} /></Grid><Grid item xs={12} sm={6}><Controller name="estado" control={control} defaultValue="activo" render={({ field }) => <TextField {...field} select fullWidth label="Estado *" size={sz}><MenuItem value="activo">Activo</MenuItem><MenuItem value="inactivo">Inactivo</MenuItem></TextField>} /></Grid><Grid item xs={12}><Controller name="direccion" control={control} render={({ field }) => <TextField {...field} fullWidth label="Dirección" multiline rows={2} size={sz} />} /></Grid></Grid>);
        if (type === 'producto') return (<Grid container spacing={2} sx={gs}><Grid item xs={12} sm={6}><Controller name="nombre" control={control} rules={{ required: 'Requerido' }} render={({ field }) => <TextField {...field} fullWidth label="Nombre *" error={!!errors.nombre} helperText={errors.nombre?.message} size={sz} />} /></Grid><Grid item xs={12} sm={6}><Controller name="codigo" control={control} render={({ field }) => <TextField {...field} fullWidth label="Código" size={sz} />} /></Grid><Grid item xs={12} sm={6}><Controller name="categoria" control={control} render={({ field }) => <TextField {...field} fullWidth label="Categoría" size={sz} />} /></Grid><Grid item xs={12} sm={6}><Controller name="precio_unitario" control={control} rules={{ required: 'Requerido', min: { value: 0, message: 'Mayor a 0' } }} render={({ field }) => <TextField {...field} fullWidth label="Precio *" type="number" error={!!errors.precio_unitario} helperText={errors.precio_unitario?.message} size={sz} InputProps={{ startAdornment: <InputAdornment position="start">$</InputAdornment> }} />} /></Grid><Grid item xs={12} sm={6}><Controller name="estado" control={control} defaultValue="activo" render={({ field }) => <TextField {...field} select fullWidth label="Estado *" size={sz}><MenuItem value="activo">Activo</MenuItem><MenuItem value="inactivo">Inactivo</MenuItem></TextField>} /></Grid><Grid item xs={12}><Controller name="descripcion" control={control} render={({ field }) => <TextField {...field} fullWidth label="Descripción" multiline rows={2} size={sz} />} /></Grid></Grid>);
        if (type === 'stock') return (<Grid container spacing={2} sx={gs}><Grid item xs={12} sm={6}><Controller name="vendedor_id" control={control} rules={{ required: 'Requerido' }} render={({ field }) => <TextField {...field} select fullWidth label="Vendedor *" error={!!errors.vendedor_id} helperText={errors.vendedor_id?.message} size={sz}>{vnd.filter(v => v.estado === 'activo').map(v => <MenuItem key={v.id} value={v.id}>{v.nombre}</MenuItem>)}</TextField>} /></Grid><Grid item xs={12} sm={6}><Controller name="producto_id" control={control} rules={{ required: 'Requerido' }} render={({ field }) => <TextField {...field} select fullWidth label="Producto *" error={!!errors.producto_id} helperText={errors.producto_id?.message} size={sz}>{prd.filter(p => p.estado === 'activo').map(p => <MenuItem key={p.id} value={p.id}>{p.nombre}</MenuItem>)}</TextField>} /></Grid><Grid item xs={12}><Controller name="cantidad" control={control} rules={{ required: 'Requerido', min: { value: 1, message: 'Mín 1' } }} render={({ field }) => <TextField {...field} fullWidth label="Cantidad *" type="number" error={!!errors.cantidad} helperText={errors.cantidad?.message} size={sz} />} /></Grid></Grid>);
        if (type === 'venta') return (<Grid container spacing={2} sx={gs}><Grid item xs={12} sm={6}><Controller name="vendedor_id" control={control} rules={{ required: 'Requerido' }} render={({ field }) => <TextField {...field} select fullWidth label="Vendedor *" error={!!errors.vendedor_id} helperText={errors.vendedor_id?.message} size={sz}>{vnd.filter(v => v.estado === 'activo').map(v => <MenuItem key={v.id} value={v.id}>{v.nombre}</MenuItem>)}</TextField>} /></Grid><Grid item xs={12} sm={6}><Controller name="producto_id" control={control} rules={{ required: 'Requerido' }} render={({ field }) => <TextField {...field} select fullWidth label="Producto *" error={!!errors.producto_id} helperText={errors.producto_id?.message} size={sz}>{prd.filter(p => p.estado === 'activo').map(p => <MenuItem key={p.id} value={p.id}>{p.nombre}</MenuItem>)}</TextField>} /></Grid><Grid item xs={12} sm={6}><Controller name="cantidad" control={control} rules={{ required: 'Requerido', min: { value: 1, message: 'Mín 1' } }} render={({ field }) => <TextField {...field} fullWidth label="Cantidad *" type="number" error={!!errors.cantidad} helperText={errors.cantidad?.message} size={sz} />} /></Grid><Grid item xs={12} sm={6}><Controller name="precio_venta" control={control} rules={{ required: 'Requerido', min: { value: 0, message: 'Mayor a 0' } }} render={({ field }) => <TextField {...field} fullWidth label="Precio *" type="number" error={!!errors.precio_venta} helperText={errors.precio_venta?.message} size={sz} InputProps={{ startAdornment: <InputAdornment position="start">$</InputAdornment> }} />} /></Grid><Grid item xs={12}><Controller name="notas" control={control} render={({ field }) => <TextField {...field} fullWidth label="Notas" multiline rows={2} size={sz} />} /></Grid></Grid>);
    };
    const sc = [
        { title: 'Vendedores Activos', value: stats.total_vendedores || 0, icon: <Store sx={{ fontSize: { xs: 20, sm: 28 }, color: '#fff' }} />, color: '#3b82f6' },
        { title: 'Productos', value: stats.total_productos || 0, icon: <Inventory2 sx={{ fontSize: { xs: 20, sm: 28 }, color: '#fff' }} />, color: '#34d399' },
        { title: 'Stock Total', value: stats.stock_total || 0, icon: <Assessment sx={{ fontSize: { xs: 20, sm: 28 }, color: '#fff' }} />, color: '#f59e0b', subtitle: fc(stats.valor_inventario) },
        { title: 'Ventas del Mes', value: stats.ventas_mes || 0, icon: <ShoppingCart sx={{ fontSize: { xs: 20, sm: 28 }, color: '#fff' }} />, color: '#8b5cf6', subtitle: fc(stats.valor_ventas_mes) }
    ];

    return (
        <Box sx={{ px: { xs: 1, sm: 2, md: 3 }, py: { xs: 1.5, sm: 2 } }}>
            <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ xs: 'flex-start', sm: 'center' }} mb={{ xs: 2, sm: 3 }} spacing={{ xs: 1, sm: 0 }}>
                <Box>
                    <Typography variant="h4" sx={{ fontWeight: 700, fontSize: { xs: '1.25rem', sm: '1.75rem', md: '2rem' } }}>Gestión de Inventario</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>Control de centros de distribución</Typography>
                </Box>
                <IconButton onClick={() => { ld(); ls(); }} sx={{ bgcolor: alpha('#34d399', 0.15), '&:hover': { bgcolor: alpha('#34d399', 0.25) } }}>
                    <Refresh sx={{ color: '#34d399' }} />
                </IconButton>
            </Stack>
            <Grid container spacing={{ xs: 2, sm: 3 }} mb={{ xs: 2, sm: 3 }}>{sc.map((c, i) => <Grid item xs={6} sm={6} lg={3} key={i}><SC {...c} /></Grid>)}</Grid>
            <Card sx={{ borderRadius: { xs: 2, sm: 3 }, border: '1px solid #e5e7eb' }}>
                <Box sx={{ borderBottom: 1, borderColor: 'divider', px: { xs: 1, sm: 2 }, overflowX: 'auto' }}>
                    <Tabs value={tab} onChange={(e, v) => { setTab(v); setP(0); }} variant={isSmall ? 'scrollable' : 'standard'} scrollButtons={isSmall ? 'auto' : false} sx={{ '& .MuiTab-root': { textTransform: 'none', fontWeight: 600, fontSize: { xs: '0.75rem', sm: '0.875rem' }, minHeight: { xs: 48, sm: 56 }, px: { xs: 1, sm: 2 } }, '& .Mui-selected': { color: '#34d399' }, '& .MuiTabs-indicator': { bgcolor: '#34d399' } }}>
                        <Tab label="Vendedores" icon={<Store sx={{ fontSize: { xs: 18, sm: 20 } }} />} iconPosition="start" />
                        <Tab label="Productos" icon={<Inventory2 sx={{ fontSize: { xs: 18, sm: 20 } }} />} iconPosition="start" />
                        <Tab label="Stock" icon={<Assessment sx={{ fontSize: { xs: 18, sm: 20 } }} />} iconPosition="start" />
                        <Tab label="Ventas" icon={<ShoppingCart sx={{ fontSize: { xs: 18, sm: 20 } }} />} iconPosition="start" />
                    </Tabs>
                </Box>
                <Box p={{ xs: 1.5, sm: 2, md: 3 }}>
                    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} mb={{ xs: 2, sm: 3 }}>
                        <TextField placeholder="Buscar..." size={isSmall ? 'small' : 'medium'} value={q} onChange={e => setQ(e.target.value)} InputProps={{ startAdornment: <InputAdornment position="start"><Search /></InputAdornment> }} sx={{ flexGrow: 1 }} />
                        <Button variant="contained" startIcon={<Add />} onClick={() => od(['vendedor', 'producto', 'stock', 'venta'][tab])} size={isSmall ? 'medium' : 'large'} fullWidth={isSmall} sx={{ background: 'linear-gradient(135deg, #34d399, #10b981)', color: '#fff', fontWeight: 600, '&:hover': { background: 'linear-gradient(135deg, #10b981, #059669)' } }}>Nuevo</Button>
                    </Stack>
                    {load ? <Box display="flex" justifyContent="center" py={4}><CircularProgress sx={{ color: '#34d399' }} /></Box> : <>{tab === 0 && rt(vnd, [{ label: 'Nombre', key: 'nombre' }, { label: 'Teléfono', key: 'telefono' }, { label: 'Ciudad', key: 'ciudad' }, { label: 'Estado', key: 'estado', render: r => <Chip label={r.estado} size="small" sx={{ bgcolor: alpha(EC[r.estado] || '#6c757d', 0.15), color: EC[r.estado] || '#6c757d', fontWeight: 600 }} /> }], 'vendedor')}{tab === 1 && rt(prd, [{ label: 'Nombre', key: 'nombre' }, { label: 'Código', key: 'codigo' }, { label: 'Categoría', key: 'categoria' }, { label: 'Precio', key: 'precio_unitario', align: 'right', render: r => fc(r.precio_unitario) }, { label: 'Estado', key: 'estado', render: r => <Chip label={r.estado} size="small" sx={{ bgcolor: alpha(EC[r.estado] || '#6c757d', 0.15), color: EC[r.estado] || '#6c757d', fontWeight: 600 }} /> }], 'producto')}{tab === 2 && rt(stk, [{ label: 'Vendedor', key: 'vendedor', render: r => r.vendedor?.nombre || '-' }, { label: 'Producto', key: 'producto', render: r => r.producto?.nombre || '-' }, { label: 'Stock Inicial', key: 'cantidad_inicial', align: 'right' }, { label: 'Stock Actual', key: 'cantidad_actual', align: 'right', render: r => <Chip label={r.cantidad_actual} sx={{ bgcolor: r.cantidad_actual > 0 ? alpha('#10b981', 0.15) : alpha('#ef4444', 0.15), color: r.cantidad_actual > 0 ? '#10b981' : '#ef4444', fontWeight: 600 }} size="small" /> }, { label: 'Última Act.', key: 'ultima_actualizacion', render: r => r.ultima_actualizacion ? new Date(r.ultima_actualizacion).toLocaleDateString() : '-' }], 'stock')}{tab === 3 && rt(vnt, [{ label: 'Fecha', key: 'fecha_venta', render: r => new Date(r.fecha_venta).toLocaleDateString() }, { label: 'Vendedor', key: 'vendedor', render: r => r.vendedor?.nombre || '-' }, { label: 'Producto', key: 'producto', render: r => r.producto?.nombre || '-' }, { label: 'Cantidad', key: 'cantidad', align: 'right' }, { label: 'Precio', key: 'precio_venta', align: 'right', render: r => fc(r.precio_venta) }, { label: 'Total', align: 'right', render: r => fc(r.cantidad * r.precio_venta) }], 'venta')}</>}
                </Box>
            </Card>
            <Dialog open={open} onClose={cd} maxWidth="md" fullWidth fullScreen={isSmall}>
                <form onSubmit={handleSubmit(os)}>
                    <DialogTitle sx={{ fontWeight: 600, fontSize: { xs: '1.125rem', sm: '1.25rem' } }}>
                        {edit ? 'Editar' : 'Crear'} {type === 'vendedor' ? 'Vendedor' : type === 'producto' ? 'Producto' : type === 'stock' ? 'Stock' : 'Venta'}
                    </DialogTitle>
                    <DialogContent>{rdc()}</DialogContent>
                    <DialogActions sx={{ p: { xs: 1.5, sm: 2.5 } }}>
                        <Button onClick={cd} size={isSmall ? 'medium' : 'large'}>Cancelar</Button>
                        <Button type="submit" variant="contained" size={isSmall ? 'medium' : 'large'} sx={{ background: 'linear-gradient(135deg, #34d399, #10b981)', color: '#fff', fontWeight: 600, '&:hover': { background: 'linear-gradient(135deg, #10b981, #059669)' } }}>
                            {edit ? 'Actualizar' : 'Crear'}
                        </Button>
                    </DialogActions>
                </form>
            </Dialog>
        </Box>
    );
}