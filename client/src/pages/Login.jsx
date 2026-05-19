import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAuth } from '../hooks/useAuth';
import { Button, Input } from '../components/ui';
import toast from 'react-hot-toast';
import './css/Registration.css';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/bookings';
  const searchState = location.state?.searchState;
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      await login(data);
      if (from === '/results' && searchState) {
        navigate('/results', { state: { search: searchState }, replace: true });
      } else {
        navigate(from, { replace: true });
      }
    } catch (err) {
      const msg = err.response?.data?.detail || 'Invalid email or password';
      toast.error(typeof msg === 'string' ? msg : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-visual">
        <div className="auth-visual__content">
          <p className="auth-visual__tagline">Travel the world with your furry family.</p>
          <div className="auth-visual__bubbles">
            <span className="bubble bubble--1">🐕 Pet-friendly hotels</span>
            <span className="bubble bubble--2">✈️ Pet-friendly airlines</span>
            <span className="bubble bubble--3">🌿 Stress-free planning</span>
          </div>
        </div>
      </div>

      <div className="auth-panel">
        <div className="auth-form-wrap">
          <div className="auth-brand">
            <span className="auth-brand__icon">✈</span>
            <span className="auth-brand__name">Skyway Travel</span>
          </div>

          <h1 className="auth-title">Welcome back</h1>
          <p className="auth-subtitle">Sign in to save bookings and manage your trips.</p>

          <form className="auth-form" onSubmit={handleSubmit(onSubmit)} noValidate>
            <Input
              label="Email address"
              type="email"
              placeholder="test@example.com"
              autoComplete="email"
              error={errors.email?.message}
              {...register('email', {
                required: 'Email is required',
                pattern: { value: /^\S+@\S+\.\S+$/, message: 'Enter a valid email' },
              })}
            />

            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              autoComplete="current-password"
              error={errors.password?.message}
              {...register('password', { required: 'Password is required' })}
            />

            <Button type="submit" loading={loading} size="lg" className="auth-form__submit">
              Sign in
            </Button>
          </form>

          <p className="auth-footer">
            New here?{' '}
            <Link to="/register" className="auth-link">
              Create an account
            </Link>
          </p>
          <p className="auth-demo-hint">
            Demo: run <code>GET /api/v1/setup-seed-data/</code> then use test@example.com / testpass123
          </p>
        </div>
      </div>
    </div>
  );
}
