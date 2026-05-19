import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Button } from '../components/ui';
import { destinationByCode } from '../constants';
import './css/ConfirmationPage.css';

export default function ConfirmationPage() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const { booking, search, total, selectedFlight, selectedHotel, selectedPlaces } = state || {};

  if (!booking) {
    return (
      <div className="confirm-page confirm-page--empty">
        <p>No trip details found.</p>
        <Link to="/">
          <Button>Back to search</Button>
        </Link>
      </div>
    );
  }

  const dest = destinationByCode(search?.destination);

  return (
    <div className="confirm-page">
      <div className="confirm-card">
        <div className="confirm-card__icon">🎉</div>
        <h1>Trip saved</h1>
        <p className="confirm-card__lead">Your trip is in the database. Safe travels!</p>

        <dl className="confirm-details">
          <div>
            <dt>Trip ID</dt>
            <dd>{booking.id}</dd>
          </div>
          <div>
            <dt>Title</dt>
            <dd>{booking.title}</dd>
          </div>
          <div>
            <dt>Destination</dt>
            <dd>{dest?.label || search?.destination}</dd>
          </div>
          <div>
            <dt>Dates</dt>
            <dd>
              {search?.departDate} → {search?.returnDate || '—'}
            </dd>
          </div>
          {selectedFlight && (
            <div>
              <dt>Flight</dt>
              <dd>
                {selectedFlight.airline_name} ({selectedFlight.origin} →{' '}
                {selectedFlight.destination})
              </dd>
            </div>
          )}
          {selectedHotel && (
            <div>
              <dt>Hotel</dt>
              <dd>{selectedHotel.hotel_name}</dd>
            </div>
          )}
          {selectedPlaces?.length > 0 && (
            <div>
              <dt>Pet places</dt>
              <dd>{selectedPlaces.length} added</dd>
            </div>
          )}
          <div>
            <dt>Estimated total</dt>
            <dd>${(total || 0).toLocaleString()}</dd>
          </div>
        </dl>

        <div className="confirm-actions">
          <Button onClick={() => navigate('/bookings')}>View my trips</Button>
          <Button variant="outline" onClick={() => navigate('/')}>
            Plan another trip
          </Button>
        </div>
      </div>
    </div>
  );
}
