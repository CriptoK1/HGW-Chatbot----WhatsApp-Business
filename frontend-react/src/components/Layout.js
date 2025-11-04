import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar, Box, Drawer, IconButton, List, ListItem, ListItemButton,
  ListItemIcon, ListItemText, Toolbar, Typography, Avatar, Menu, MenuItem,
  useTheme, useMediaQuery, Badge, alpha, Divider, Tooltip,
} from '@mui/material';
import {
  Menu as MenuIcon, Dashboard as DashboardIcon, People as PeopleIcon,
  Chat as ChatIcon, PersonSearch as PersonSearchIcon, Logout as LogoutIcon,
  AccountCircle as AccountCircleIcon, Notifications as NotificationsIcon, Spa as SpaIcon,
} from '@mui/icons-material';

const drawerWidthExpanded = 240;
const drawerWidthCollapsed = 72;

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
  { text: 'Distribuidores', icon: <PeopleIcon />, path: '/distributors' },
  { text: 'Conversaciones', icon: <ChatIcon />, path: '/conversations' },
  { text: 'Leads', icon: <PersonSearchIcon />, path: '/leads' },
];

const commonStyles = {
  avatar: {
    width: 36,
    height: 36,
    background: 'linear-gradient(135deg, #34d399 0%, #10b981 100%)',
    color: '#064e3b',
    fontWeight: 700,
    fontSize: '0.9rem',
  },
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  transitionFast: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
};

function Layout({ user, onLogout }) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();

  const [mobileOpen, setMobileOpen] = useState(false);
  const [desktopOpen, setDesktopOpen] = useState(true);
  const [anchorEl, setAnchorEl] = useState(null);

  const handleDrawerToggle = () => {
    isMobile ? setMobileOpen(!mobileOpen) : setDesktopOpen(!desktopOpen);
  };

  const handleProfileClick = (event) => setAnchorEl(event.currentTarget);
  const handleProfileClose = () => setAnchorEl(null);

  const handleLogout = () => {
    handleProfileClose();
    onLogout();
    navigate('/login');
  };

  const handleNavigation = (path) => {
    navigate(path);
    if (isMobile) setMobileOpen(false);
  };

  const drawerWidth = isMobile ? drawerWidthExpanded : (desktopOpen ? drawerWidthExpanded : drawerWidthCollapsed);
  const isExpanded = desktopOpen || isMobile;
  const isCollapsed = !desktopOpen && !isMobile;

  const drawer = (
    <Box sx={{
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      background: 'linear-gradient(180deg, #059669 0%, #047857 50%, #065f46 100%)',
      position: 'relative',
      overflow: 'hidden',
      '&::before': {
        content: '""',
        position: 'absolute',
        inset: 0,
        backgroundImage: `
          radial-gradient(circle at 20% 20%, ${alpha('#34d399', 0.1)} 0%, transparent 50%),
          radial-gradient(circle at 80% 80%, ${alpha('#10b981', 0.1)} 0%, transparent 50%)
        `,
        pointerEvents: 'none',
      },
    }}>
      {/* Logo */}
      <Box
        onClick={() => !isMobile && handleDrawerToggle()}
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: isExpanded ? 'flex-start' : 'center',
          p: 2.5,
          minHeight: 80,
          cursor: isMobile ? 'default' : 'pointer',
          transition: commonStyles.transition,
          '&:hover': !isMobile && { background: alpha('#fff', 0.05) },
        }}
      >
        <Box sx={{
          width: 44,
          height: 44,
          borderRadius: '50%',
          background: alpha('#fff', 0.15),
          backdropFilter: 'blur(10px)',
          border: `2px solid ${alpha('#34d399', 0.3)}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: commonStyles.transition,
          '&:hover': {
            background: alpha('#fff', 0.2),
            borderColor: alpha('#34d399', 0.5),
          },
        }}>
          <SpaIcon sx={{ fontSize: 24, color: '#34d399' }} />
        </Box>
        {isExpanded && (
          <Typography variant="h6" sx={{
            ml: 1.5,
            fontWeight: 700,
            color: '#fff',
            fontSize: '1.1rem',
          }}>
            HGW Admin
          </Typography>
        )}
      </Box>

      <Divider sx={{ borderColor: alpha('#fff', 0.1) }} />

      {/* Menú */}
      <List sx={{ px: 1.5, py: 2, flex: 1 }}>
        {menuItems.map((item) => {
          const isSelected = location.pathname === item.path;
          return (
            <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
              <Tooltip title={isCollapsed ? item.text : ''} placement="right" arrow>
                <ListItemButton
                  selected={isSelected}
                  onClick={() => handleNavigation(item.path)}
                  sx={{
                    borderRadius: 2,
                    justifyContent: isCollapsed ? 'center' : 'flex-start',
                    px: isCollapsed ? 1 : 2,
                    '&.Mui-selected': {
                      background: alpha('#fff', 0.12),
                      '&:hover': { background: alpha('#fff', 0.18) },
                    },
                  }}
                >
                  <ListItemIcon sx={{
                    color: isSelected ? '#34d399' : alpha('#fff', 0.9),
                    minWidth: isCollapsed ? 'auto' : 40,
                  }}>
                    {item.icon}
                  </ListItemIcon>
                  {!isCollapsed && (
                    <ListItemText
                      primary={item.text}
                      primaryTypographyProps={{
                        fontWeight: isSelected ? 600 : 500,
                        fontSize: '0.9rem',
                        color: alpha('#fff', 0.95),
                      }}
                    />
                  )}
                </ListItemButton>
              </Tooltip>
            </ListItem>
          );
        })}
      </List>

      {/* Perfil */}
      {isExpanded && (
        <Box sx={{
          p: 2,
          borderTop: `1px solid ${alpha('#fff', 0.1)}`,
        }}>
          <Box
            onClick={handleProfileClick}
            sx={{
              display: 'flex',
              alignItems: 'center',
              p: 1.5,
              borderRadius: 2,
              background: alpha('#fff', 0.08),
              cursor: 'pointer',
              '&:hover': { background: alpha('#fff', 0.12) },
            }}
          >
            <Avatar sx={commonStyles.avatar}>
              {user?.username?.[0]?.toUpperCase() || 'A'}
            </Avatar>
            <Box sx={{ ml: 1.5 }}>
              <Typography variant="body2" sx={{ color: '#fff', fontWeight: 600 }}>
                {user?.username || 'Admin'}
              </Typography>
              <Typography variant="caption" sx={{ color: alpha('#fff', 0.6) }}>
                Administrador
              </Typography>
            </Box>
          </Box>
        </Box>
      )}
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', width: '100%', minHeight: '100vh' }}>
      {/* AppBar */}
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          backgroundColor: '#fff',
          color: '#1a1a1a',
          boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
        }}
      >
        <Toolbar>
          <IconButton color="inherit" onClick={handleDrawerToggle} sx={{ mr: 2, display: { md: 'none' } }}>
            <MenuIcon />
          </IconButton>

          <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 600 }}>
            {menuItems.find(item => item.path === location.pathname)?.text || 'Dashboard'}
          </Typography>

          <IconButton sx={{ mr: 2 }}>
            <Badge badgeContent={4} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>

          <IconButton onClick={handleProfileClick}>
            <Avatar sx={commonStyles.avatar}>
              {user?.username?.[0]?.toUpperCase() || 'A'}
            </Avatar>
          </IconButton>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleProfileClose}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          >
            <MenuItem onClick={handleProfileClose}>
              <AccountCircleIcon fontSize="small" sx={{ mr: 1, color: '#10b981' }} />
              Mi Perfil
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout} sx={{ color: '#ef4444' }}>
              <LogoutIcon fontSize="small" sx={{ mr: 1 }} />
              Cerrar Sesión
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Drawer */}
      <Box component="nav" sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}>
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': { width: drawerWidthExpanded, border: 'none' },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': {
              width: drawerWidth,
              border: 'none',
              overflowX: 'hidden',
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Contenido principal */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: { xs: 2, sm: 3 },
          mt: { xs: 7, sm: 8 },
          backgroundColor: '#f4f6f9',
          minHeight: '100vh',
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
}

export default Layout;
