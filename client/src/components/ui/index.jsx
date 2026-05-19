// src/components/ui/index.jsx
// Reusable design-system components for PawTrip

import React, { forwardRef } from 'react';
import './UI.css';

// ── Button ─────────────────────────────────────────────────────────────────────
export const Button = forwardRef(function Button(
  { variant = 'primary', size = 'md', loading = false, icon, children, className = '', ...props },
  ref
) {
  return (
    <button
      ref={ref}
      className={`btn btn--${variant} btn--${size} ${loading ? 'btn--loading' : ''} ${className}`}
      disabled={loading || props.disabled}
      {...props}
    >
      {loading && <span className="btn__spinner" aria-hidden="true" />}
      {icon && !loading && <span className="btn__icon">{icon}</span>}
      {children && <span>{children}</span>}
    </button>
  );
});

// ── Input ──────────────────────────────────────────────────────────────────────
export const Input = forwardRef(function Input(
  { label, error, helper, icon, className = '', ...props },
  ref
) {
  return (
    <div className={`field ${error ? 'field--error' : ''} ${className}`}>
      {label && (
        <label className="field__label" htmlFor={props.id || props.name}>
          {label}
        </label>
      )}
      <div className="field__control">
        {icon && <span className="field__icon">{icon}</span>}
        <input ref={ref} className={`field__input ${icon ? 'field__input--icon' : ''}`} {...props} />
      </div>
      {error && <p className="field__error">{error}</p>}
      {helper && !error && <p className="field__helper">{helper}</p>}
    </div>
  );
});

// ── TextArea ───────────────────────────────────────────────────────────────────
export const TextArea = forwardRef(function TextArea(
  { label, error, helper, className = '', ...props },
  ref
) {
  return (
    <div className={`field ${error ? 'field--error' : ''} ${className}`}>
      {label && (
        <label className="field__label" htmlFor={props.id || props.name}>
          {label}
        </label>
      )}
      <textarea ref={ref} className="field__textarea" {...props} />
      {error && <p className="field__error">{error}</p>}
      {helper && !error && <p className="field__helper">{helper}</p>}
    </div>
  );
});

// ── Select ─────────────────────────────────────────────────────────────────────
export const Select = forwardRef(function Select(
  { label, error, options = [], placeholder, className = '', ...props },
  ref
) {
  return (
    <div className={`field ${error ? 'field--error' : ''} ${className}`}>
      {label && (
        <label className="field__label" htmlFor={props.id || props.name}>
          {label}
        </label>
      )}
      <select ref={ref} className="field__select" {...props}>
        {placeholder && <option value="">{placeholder}</option>}
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && <p className="field__error">{error}</p>}
    </div>
  );
});

// ── Badge ──────────────────────────────────────────────────────────────────────
export function Badge({ variant = 'default', children, className = '' }) {
  return (
    <span className={`badge badge--${variant} ${className}`}>{children}</span>
  );
}

// ── Card ───────────────────────────────────────────────────────────────────────
export function Card({ className = '', children, onClick, hover = false, ...props }) {
  return (
    <div
      className={`card ${hover ? 'card--hover' : ''} ${onClick ? 'card--clickable' : ''} ${className}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      {...props}
    >
      {children}
    </div>
  );
}

// ── Spinner ────────────────────────────────────────────────────────────────────
export function Spinner({ size = 'md', className = '' }) {
  return <div className={`spinner spinner--${size} ${className}`} aria-label="Loading" />;
}

// ── Avatar ─────────────────────────────────────────────────────────────────────
export function Avatar({ src, name, size = 'md', className = '' }) {
  const initials = name
    ? name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
    : '?';
  return (
    <div className={`avatar avatar--${size} ${className}`}>
      {src ? (
        <img src={src} alt={name || 'Avatar'} />
      ) : (
        <span>{initials}</span>
      )}
    </div>
  );
}

// ── Modal ──────────────────────────────────────────────────────────────────────
export function Modal({ open, onClose, title, children, footer, size = 'md' }) {
  if (!open) return null;
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className={`modal modal--${size}`}
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label={title}
      >
        <div className="modal__header">
          <h3 className="modal__title">{title}</h3>
          <button className="modal__close" onClick={onClose} aria-label="Close">
            ✕
          </button>
        </div>
        <div className="modal__body">{children}</div>
        {footer && <div className="modal__footer">{footer}</div>}
      </div>
    </div>
  );
}

// ── EmptyState ─────────────────────────────────────────────────────────────────
export function EmptyState({ icon, title, description, action }) {
  return (
    <div className="empty-state">
      {icon && <div className="empty-state__icon">{icon}</div>}
      <h3 className="empty-state__title">{title}</h3>
      {description && <p className="empty-state__desc">{description}</p>}
      {action && <div className="empty-state__action">{action}</div>}
    </div>
  );
}

// ── ProgressBar ────────────────────────────────────────────────────────────────
export function ProgressBar({ value = 0, max = 100, label, variant = 'primary' }) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  return (
    <div className="progress">
      {label && <span className="progress__label">{label}</span>}
      <div className="progress__track">
        <div
          className={`progress__fill progress__fill--${variant}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="progress__value">{Math.round(pct)}%</span>
    </div>
  );
}