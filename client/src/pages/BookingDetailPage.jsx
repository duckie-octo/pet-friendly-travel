import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { format } from 'date-fns';
import toast from 'react-hot-toast';
import { bookingService } from '../services/bookingService';
import { Badge, Button, Card, Spinner } from '../components/ui';
import './css/BookingsPage.css';

export default function BookingDetailPage() {
  const { id } = useParams();
  const [trip, setTrip] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await bookingService.getBooking(id);
        if (cancelled) return;
        setTrip(data);
      } catch {
        toast.error('Could not load trip');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [id]);

  if (loading) {
    return (
      <div className="bookings-loading">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!trip) {
    return (
      <div className="bookings-page">
        <p>Trip not found.</p>
        <Link to="/bookings">
          <Button variant="outline">Back to trips</Button>
        </Link>
      </div>
    );
  }

  const flights = trip.flights || [];
  const hotels = trip.hotels || [];
  const petPlaces = trip.pet_places || [];

  return (
    <div className="bookings-page">
      <Link to="/bookings" className="results-back">
        ← All trips
      </Link>

      <header className="bookings-page__header">
        <div>
          <h1>{trip.title}</h1>
          <p>
            {format(new Date(trip.start_date), 'MMM d, yyyy')} –{' '}
            {format(new Date(trip.end_date), 'MMM d, yyyy')}
          </p>
        </div>
        <Badge variant="success">{trip.status}</Badge>
      </header>

      {flights.length > 0 && (
        <section className="detail-section">
          <h2>Flights</h2>
          {flights.map((f) => (
            <Card key={f.id} className="detail-item">
              <p>
                <strong>
                  {f.airline_name} {f.flight_number}
                </strong>
              </p>
              <p>
                {f.origin_iata} → {f.destination_iata} ·{' '}
                {format(new Date(f.departs_at), 'MMM d, yyyy HH:mm')}
              </p>
              {f.price != null && <p className="detail-rate">${f.price.toLocaleString()}</p>}
            </Card>
          ))}
        </section>
      )}

      {hotels.length > 0 && (
        <section className="detail-section">
          <h2>Hotels</h2>
          {hotels.map((h) => (
            <Card key={h.id} className="detail-item">
              <p>
                <strong>{h.name}</strong>
              </p>
              <p>
                {h.city}, {h.country_code} · Check-in {h.check_in} · Check-out {h.check_out}
              </p>
              {h.price_per_night != null && (
                <p className="detail-rate">${h.price_per_night.toLocaleString()}/night</p>
              )}
            </Card>
          ))}
        </section>
      )}

      {petPlaces.length > 0 && (
        <section className="detail-section">
          <h2>Pet-friendly places</h2>
          {petPlaces.map((p) => (
            <Card key={p.id} className="detail-item">
              <p>
                <strong>{p.name}</strong>
              </p>
              <p>{p.address || p.city || '—'}</p>
              {p.pet_category && <Badge variant="info">{p.pet_category}</Badge>}
            </Card>
          ))}
        </section>
      )}
    </div>
  );
}
