import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Select } from '../components/ui';
import {
  DESTINATIONS,
  DEMO_DEPART_DATE,
  DEMO_RETURN_DATE,
  TENANTS,
} from '../constants';
import './css/HomePage.css';

const tenant = TENANTS.skyway;

export default function HomePage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    origin: 'JFK',
    destination: 'LAX',
    departDate: DEMO_DEPART_DATE,
    returnDate: DEMO_RETURN_DATE,
    travelers: '1',
    budget: '2000',
    travelingWithPets: true,
    petCount: '1',
    maxPetKg: '8',
  });
  const [error, setError] = useState('');

  const update = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));

  const handleSearch = (e) => {
    e.preventDefault();
    if (!form.origin || !form.destination || !form.departDate || !form.budget) {
      setError('Please fill in origin, destination, depart date, and budget.');
      return;
    }
    if (form.origin === form.destination) {
      setError('Origin and destination must be different.');
      return;
    }
    setError('');
    navigate('/results', { state: { search: form } });
  };

  return (
    <div className="home-page">
      <section
        className="home-hero"
        style={{
          background: `linear-gradient(135deg, ${tenant.accentDark} 0%, ${tenant.accent} 60%, #1a8dd4 100%)`,
        }}
      >
        <div className="home-hero__content">
          <p className="home-hero__eyebrow">{tenant.tagline}</p>
          <h1 className="home-hero__title">
            Pet-friendly travel,
            <br />
            planned with care
          </h1>
          <p className="home-hero__subtitle">
            Search flights on pet-friendly airlines and hotels that welcome your companions.
          </p>

          <form className="search-card" onSubmit={handleSearch}>
            {error && <p className="search-card__error">{error}</p>}

            <div className="search-card__grid">
              <Select
                label="From"
                value={form.origin}
                onChange={(e) => update('origin', e.target.value)}
                options={DESTINATIONS.map((d) => ({ value: d.code, label: d.label }))}
              />
              <Select
                label="To"
                value={form.destination}
                onChange={(e) => update('destination', e.target.value)}
                options={DESTINATIONS.map((d) => ({ value: d.code, label: d.label }))}
              />
              <label className="field">
                <span className="field__label">Depart</span>
                <input
                  type="date"
                  className="field__input"
                  value={form.departDate}
                  onChange={(e) => update('departDate', e.target.value)}
                />
              </label>
              <label className="field">
                <span className="field__label">Return</span>
                <input
                  type="date"
                  className="field__input"
                  value={form.returnDate}
                  onChange={(e) => update('returnDate', e.target.value)}
                />
              </label>
              <Select
                label="Travelers"
                value={form.travelers}
                onChange={(e) => update('travelers', e.target.value)}
                options={[1, 2, 3, 4, 5, 6].map((n) => ({
                  value: String(n),
                  label: `${n} traveler${n > 1 ? 's' : ''}`,
                }))}
              />
              <label className="field">
                <span className="field__label">Budget (USD)</span>
                <input
                  type="number"
                  className="field__input"
                  min="100"
                  value={form.budget}
                  onChange={(e) => update('budget', e.target.value)}
                />
              </label>
            </div>

            <div className="search-card__pets">
              <label className="search-card__checkbox">
                <input
                  type="checkbox"
                  checked={form.travelingWithPets}
                  onChange={(e) => update('travelingWithPets', e.target.checked)}
                />
                Traveling with pets
              </label>
              {form.travelingWithPets && (
                <div className="search-card__pet-fields">
                  <label className="field">
                    <span className="field__label">Number of pets</span>
                    <input
                      type="number"
                      min="1"
                      className="field__input"
                      value={form.petCount}
                      onChange={(e) => update('petCount', e.target.value)}
                    />
                  </label>
                  <label className="field">
                    <span className="field__label">Pet weight (kg)</span>
                    <input
                      type="number"
                      min="1"
                      step="0.5"
                      className="field__input"
                      value={form.maxPetKg}
                      onChange={(e) => update('maxPetKg', e.target.value)}
                    />
                  </label>
                </div>
              )}
            </div>

            <p className="search-card__hint">
              Results come from Booking.com (flights &amp; hotels) and Geoapify (pet-friendly places).
              Use future dates for best availability.
            </p>

            <Button type="submit" size="lg" className="search-card__submit">
              Search flights &amp; hotels
            </Button>
          </form>
        </div>
      </section>

      <section className="home-features">
        <h2>Why {tenant.name}?</h2>
        <div className="home-features__grid">
          {[
            {
              icon: '🐾',
              title: 'Pet-friendly first',
              desc: 'Filter airlines and hotels that welcome pets, with policy details up front.',
            },
            {
              icon: '💰',
              title: 'Budget aware',
              desc: 'See totals for flights and stays and know what fits your trip budget.',
            },
            {
              icon: '✈️',
              title: 'Real bookings',
              desc: 'Save trips to your account via the travel agency API.',
            },
          ].map((f) => (
            <article key={f.title} className="feature-card">
              <span className="feature-card__icon">{f.icon}</span>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
