import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { TENANTS } from '../../constants';
import './SiteHeader.css';

const tenant = TENANTS.skyway;

export default function SiteHeader() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <header className="site-header">
      <div className="site-header__inner">
        <Link to="/" className="site-header__brand">
          <span className="site-header__logo">{tenant.logo}</span>
          <div>
            <span className="site-header__name">{tenant.name}</span>
            <p className="site-header__tagline">{tenant.tagline}</p>
          </div>
        </Link>

        <nav className="site-header__nav">
          {user ? (
            <>
              <Link to="/bookings" className="site-header__link">
                My Trips
              </Link>
              <span className="site-header__greeting">
                Hi, {user.first_name || 'Traveler'}
              </span>
              <button type="button" className="site-header__btn site-header__btn--ghost" onClick={handleLogout}>
                Sign out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="site-header__link">
                Sign in
              </Link>
              <Link to="/register" className="site-header__btn site-header__btn--primary">
                Register
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
