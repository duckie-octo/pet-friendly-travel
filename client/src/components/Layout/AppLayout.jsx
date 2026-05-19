import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { Avatar } from '../ui';
import './AppLayout.css';

const NAV_ITEMS = [
  { to: '/', icon: '🔍', label: 'Search' },
  { to: '/bookings', icon: '✈️', label: 'My Bookings' },
];

export default function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar__logo">
          <span className="sidebar__logo-icon">✈</span>
          <span className="sidebar__logo-text">Skyway Travel</span>
        </div>

        <nav className="sidebar__nav">
          {NAV_ITEMS.map(({ to, icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `sidebar__link ${isActive ? 'sidebar__link--active' : ''}`
              }
            >
              <span className="sidebar__link-icon">{icon}</span>
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar__bottom">
          <div className="sidebar__user">
            <Avatar name={user?.full_name || user?.email} size="sm" />
            <div className="sidebar__user-info">
              <p className="sidebar__user-name">{user?.full_name || 'Traveler'}</p>
              <p className="sidebar__user-email">{user?.email}</p>
            </div>
            <button type="button" className="sidebar__logout" onClick={handleLogout} title="Sign out">
              ↗
            </button>
          </div>
        </div>
      </aside>

      <div className="main-wrapper">
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
