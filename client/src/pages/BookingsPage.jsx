import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { format } from 'date-fns';
import { useAuth } from '../hooks/useAuth';
import { bookingService } from '../services/bookingService';
import { Button, Card, Spinner, Badge } from '../components/ui';
import './css/BookingsPage.css';

export default function BookingsPage() {
  const { user } = useAuth();
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const data = await bookingService.listBookings();
      setTrips(data);
    } catch {
      toast.error('Could not load trips');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleCancel = async (id) => {
    if (!window.confirm('Delete this trip? This cannot be undone.')) return;
    try {
      await bookingService.deleteBooking(id);
      toast.success('Trip removed');
      setTrips((prev) => prev.filter((t) => t.id !== id));
    } catch {
      toast.error('Failed to delete trip');
    }
  };

  return (
    <div className="bookings-page">
      <header className="bookings-page__header">
        <div>
          <h1>My trips</h1>
          <p>
            {user?.full_name} · {user?.email}
          </p>
        </div>
        <Link to="/">
          <Button>+ New search</Button>
        </Link>
      </header>

      {loading ? (
        <div className="bookings-loading">
          <Spinner size="lg" />
        </div>
      ) : trips.length === 0 ? (
        <Card className="bookings-empty">
          <p className="bookings-empty__icon">✈️</p>
          <h2>No trips yet</h2>
          <p>Search for pet-friendly flights and hotels to plan your next adventure.</p>
          <Link to="/">
            <Button variant="outline">Start searching</Button>
          </Link>
        </Card>
      ) : (
        <div className="bookings-list">
          {trips.map((t) => (
            <Card key={t.id} className="booking-card">
              <div className="booking-card__main">
                <div>
                  <h3>{t.title}</h3>
                  <p>
                    {format(new Date(t.start_date), 'MMM d, yyyy')} –{' '}
                    {format(new Date(t.end_date), 'MMM d, yyyy')}
                  </p>
                </div>
                <Badge variant="success">{t.status}</Badge>
              </div>
              <div className="booking-card__actions">
                <Link to={`/bookings/${t.id}`}>
                  <Button variant="outline" size="sm">
                    View details
                  </Button>
                </Link>
                <Button variant="danger" size="sm" onClick={() => handleCancel(t.id)}>
                  Delete
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
