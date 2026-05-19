import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAuth } from '../hooks/useAuth';
import { Button, Input } from '../components/ui';
import toast from 'react-hot-toast';
import './css/Registration.css';

export default function RegisterPage() {
  const { register: registerUser } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm();

  const password = watch('password');

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      await registerUser({
        first_name: data.first_name,
        last_name: data.last_name,
        email: data.email,
        password: data.password,
        phone_number: data.phone_number || undefined,
      });
      toast.success('Account created!');
      navigate('/bookings');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Registration failed';
      toast.error(typeof msg === 'string' ? msg : 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page auth-page--register">
      <div className="auth-visual">
        <div className="auth-visual__content">
          <p className="auth-visual__tagline">Every journey is better with a paw to hold.</p>
          <div className="auth-visual__bubbles">
            <span className="bubble bubble--1">✅ Real API bookings</span>
            <span className="bubble bubble--2">🗺️ Pet-friendly search</span>
            <span className="bubble bubble--3">🏨 Welcoming stays</span>
          </div>
        </div>
      </div>

      <div className="auth-panel">
        <div className="auth-form-wrap">
          <div className="auth-brand">
            <span className="auth-brand__icon">✈</span>
            <span className="auth-brand__name">Skyway Travel</span>
          </div>

          <h1 className="auth-title">Create your account</h1>
          <p className="auth-subtitle">Start planning pet-friendly adventures today.</p>

          <form className="auth-form" onSubmit={handleSubmit(onSubmit)} noValidate>
            <Input
              label="First name"
              type="text"
              placeholder="Alex"
              autoComplete="given-name"
              error={errors.first_name?.message}
              {...register('first_name', { required: 'First name is required' })}
            />

            <Input
              label="Last name"
              type="text"
              placeholder="Johnson"
              autoComplete="family-name"
              error={errors.last_name?.message}
              {...register('last_name', { required: 'Last name is required' })}
            />

            <Input
              label="Email address"
              type="email"
              placeholder="you@example.com"
              autoComplete="email"
              error={errors.email?.message}
              {...register('email', {
                required: 'Email is required',
                pattern: { value: /^\S+@\S+\.\S+$/, message: 'Enter a valid email' },
              })}
            />

            <Input
              label="Phone (optional)"
              type="tel"
              placeholder="555-0100"
              autoComplete="tel"
              {...register('phone_number')}
            />

            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              autoComplete="new-password"
              helper="At least 8 characters"
              error={errors.password?.message}
              {...register('password', {
                required: 'Password is required',
                minLength: { value: 8, message: 'Password must be at least 8 characters' },
              })}
            />

            <Input
              label="Confirm password"
              type="password"
              placeholder="••••••••"
              autoComplete="new-password"
              error={errors.confirm_password?.message}
              {...register('confirm_password', {
                required: 'Please confirm your password',
                validate: (v) => v === password || 'Passwords do not match',
              })}
            />

            <Button type="submit" loading={loading} size="lg" className="auth-form__submit">
              Create account
            </Button>
          </form>

          <p className="auth-footer">
            Already have an account?{' '}
            <Link to="/login" className="auth-link">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
