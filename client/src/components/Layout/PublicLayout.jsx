import { Outlet } from 'react-router-dom';
import SiteHeader from './SiteHeader';

export default function PublicLayout() {
  return (
    <>
      <SiteHeader />
      <Outlet />
      <footer className="site-footer">
        <p>© 2025 Skyway Travel · CMPE 131</p>
      </footer>
    </>
  );
}
