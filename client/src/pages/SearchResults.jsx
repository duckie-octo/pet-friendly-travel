import { useEffect, useMemo, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuth } from '../hooks/useAuth';
import { travelService } from '../services/travelService';
import { destinationByCode } from '../constants';
import { Badge, Button, Spinner } from '../components/ui';
import './css/SearchResults.css';

function flightTotal(flight, travelers) {
  return (flight.rate || 0) * travelers;
}

function hotelTotal(hotel, nights) {
  const nightly = hotel.rate ? hotel.rate / Math.max(nights, 1) : 150;
  return nightly * nights;
}

export default function SearchResults() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const search = state?.search;

  const [loading, setLoading] = useState(true);
  const [flights, setFlights] = useState([]);
  const [hotels, setHotels] = useState([]);
  const [places, setPlaces] = useState([]);
  const [hints, setHints] = useState([]);
  const [selectedFlight, setSelectedFlight] = useState(null);
  const [selectedHotel, setSelectedHotel] = useState(null);
  const [selectedPlaces, setSelectedPlaces] = useState([]);
  const [booking, setBooking] = useState(false);

  const travelers = parseInt(search?.travelers || '1', 10);
  const budget = parseInt(search?.budget || '0', 10);
  const nights = useMemo(() => {
    if (!search?.departDate || !search?.returnDate) return 5;
    const diff = new Date(search.returnDate) - new Date(search.departDate);
    return Math.max(1, Math.round(diff / 86400000));
  }, [search]);

  const destMeta = destinationByCode(search?.destination);
  const destLabel = destMeta?.label || search?.destination;

  useEffect(() => {
    if (!search) {
      navigate('/', { replace: true });
      return;
    }

    let cancelled = false;

    async function load() {
      setLoading(true);
      try {
        const res = await travelService.searchTrip({
          origin: search.origin,
          destination: search.destination,
          destCity: destMeta?.city || search.destination,
          destCountry: destMeta?.country || 'USA',
          departDate: search.departDate,
          returnDate: search.returnDate,
          adults: travelers,
          petsAllowed: Boolean(search.travelingWithPets),
        });

        if (cancelled) return;

        const flightList = (res.flights || []).filter(
          (f) => flightTotal(f, travelers) <= budget * 0.65
        );
        const hotelList = (res.hotels || []).filter(
          (h) => (h.rate || hotelTotal(h, nights)) <= budget * 0.5
        );

        setFlights(flightList);
        setHotels(hotelList);
        setPlaces(res.places || []);
        setHints(res.hints || []);
        if (flightList[0]) setSelectedFlight(flightList[0]);
        if (hotelList[0]) setSelectedHotel(hotelList[0]);
        setSelectedPlaces([]);
      } catch (err) {
        const msg = err.response?.data?.detail || 'Failed to load search results';
        toast.error(typeof msg === 'string' ? msg : 'Search failed');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [search, navigate, travelers, budget, nights, destMeta]);

  const total = useMemo(() => {
    if (!selectedFlight || !selectedHotel) return 0;
    return flightTotal(selectedFlight, travelers) + hotelTotal(selectedHotel, nights);
  }, [selectedFlight, selectedHotel, travelers, nights]);

  const togglePlace = (place) => {
    setSelectedPlaces((prev) => {
      const key = place.place_id || place.name;
      if (prev.some((p) => (p.place_id || p.name) === key)) {
        return prev.filter((p) => (p.place_id || p.name) !== key);
      }
      return [...prev, place];
    });
  };

  const handleBook = async () => {
    if (!user) {
      navigate('/login', { state: { from: { pathname: '/results' }, searchState: search } });
      return;
    }
    if (!selectedFlight || !selectedHotel) {
      toast.error('Select a flight and hotel to continue.');
      return;
    }

    setBooking(true);
    try {
      const created = await travelService.saveTrip({
        start_date: search.departDate,
        end_date: search.returnDate || search.departDate,
        guests: travelers,
        selected_flight: selectedFlight,
        selected_hotel: selectedHotel,
        selected_places: selectedPlaces.map((p) => ({
          place_id: p.place_id,
          name: p.name,
          address: p.address,
          lat: p.lat,
          lon: p.lon,
          categories: p.categories || [],
        })),
        traveling_with_pets: Boolean(search.travelingWithPets),
        pet_count: search.travelingWithPets
          ? parseInt(search.petCount || '1', 10)
          : null,
      });
      navigate('/confirmation', {
        state: {
          booking: created,
          search,
          total,
          selectedFlight,
          selectedHotel,
          selectedPlaces,
        },
      });
    } catch (err) {
      const detail = err.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : 'Booking failed');
    } finally {
      setBooking(false);
    }
  };

  if (!search) return null;

  return (
    <div className="results-page">
      <div className="results-page__header">
        <Link to="/" className="results-back">
          ← Back
        </Link>
        <div>
          <h1>Results for {destLabel}</h1>
          <p>
            {travelers} traveler{travelers > 1 ? 's' : ''} · {nights} nights · Budget $
            {budget.toLocaleString()} · Live APIs
          </p>
        </div>
      </div>

      {hints.length > 0 && (
        <div className="results-hints">
          {hints.map((h) => (
            <p key={h}>{h}</p>
          ))}
        </div>
      )}

      {loading ? (
        <div className="results-loading">
          <Spinner size="lg" />
        </div>
      ) : (
        <div className="results-layout">
          <div className="results-main">
            <section>
              <h2>Flights (Booking.com)</h2>
              {flights.length === 0 ? (
                <p className="results-empty">No pet-friendly flights match your filters.</p>
              ) : (
                <div className="option-list">
                  {flights.map((f) => {
                    const flightKey =
                      f.offer_token || `${f.airline_code}-${f.flight_number}-${f.departure_date}`;
                    const isSelected =
                      selectedFlight &&
                      (selectedFlight.offer_token
                        ? selectedFlight.offer_token === f.offer_token
                        : `${selectedFlight.airline_code}-${selectedFlight.flight_number}-${selectedFlight.departure_date}` ===
                          flightKey);
                    return (
                      <button
                        type="button"
                        key={flightKey}
                        className={`option-card ${isSelected ? 'option-card--selected' : ''}`}
                        onClick={() => setSelectedFlight(f)}
                      >
                        <div>
                          <strong>{f.airline_name}</strong>
                          <p>
                            {f.origin} → {f.destination} · {f.departure_date} {f.departure_time}
                          </p>
                          {f.pet_policy && (
                            <p className="option-card__meta">
                              In-cabin up to {f.pet_policy.max_kg} kg
                            </p>
                          )}
                        </div>
                        <div className="option-card__price">
                          <strong>${(f.rate || 0).toLocaleString()}</strong>
                          <span>per person</span>
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}
            </section>

            <section>
              <h2>Hotels (Booking.com)</h2>
              {hotels.length === 0 ? (
                <p className="results-empty">No pet-friendly hotels found for this destination.</p>
              ) : (
                <div className="option-list">
                  {hotels.map((h) => (
                    <button
                      type="button"
                      key={h.hotel_id}
                      className={`option-card ${selectedHotel?.hotel_id === h.hotel_id ? 'option-card--selected' : ''}`}
                      onClick={() => setSelectedHotel(h)}
                    >
                      <div>
                        <strong>{h.hotel_name}</strong>
                        <p>
                          {h.city}, {h.country}
                        </p>
                        <div className="option-card__badges">
                          <Badge variant="success">Pet-friendly search</Badge>
                          {h.rate != null && (
                            <Badge variant="warning">
                              From {h.currency || 'USD'} {h.rate.toLocaleString()}
                            </Badge>
                          )}
                        </div>
                      </div>
                      <div className="option-card__price">
                        <strong>${hotelTotal(h, nights).toLocaleString()}</strong>
                        <span>est. stay</span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </section>

            <section>
              <h2>Pet-friendly places (Geoapify)</h2>
              {places.length === 0 ? (
                <p className="results-empty">No places found for this city.</p>
              ) : (
                <div className="option-list">
                  {places.map((p) => {
                    const key = p.place_id || p.name;
                    const selected = selectedPlaces.some(
                      (sp) => (sp.place_id || sp.name) === key
                    );
                    return (
                      <button
                        type="button"
                        key={key}
                        className={`option-card ${selected ? 'option-card--selected' : ''}`}
                        onClick={() => togglePlace(p)}
                      >
                        <div>
                          <strong>{p.name}</strong>
                          <p>{p.address || '—'}</p>
                        </div>
                        <Badge variant={selected ? 'success' : 'default'}>
                          {selected ? 'Added' : 'Add'}
                        </Badge>
                      </button>
                    );
                  })}
                </div>
              )}
            </section>
          </div>

          <aside className="results-summary">
            <h3>Trip summary</h3>
            {selectedFlight && (
              <div className="summary-block">
                <span className="summary-label">Flight</span>
                <p>{selectedFlight.airline_name}</p>
                <p className="summary-muted">
                  ${flightTotal(selectedFlight, travelers).toLocaleString()}
                </p>
              </div>
            )}
            {selectedHotel && (
              <div className="summary-block">
                <span className="summary-label">Hotel</span>
                <p>{selectedHotel.hotel_name}</p>
                <p className="summary-muted">
                  ${hotelTotal(selectedHotel, nights).toLocaleString()} est.
                </p>
              </div>
            )}
            {selectedPlaces.length > 0 && (
              <div className="summary-block">
                <span className="summary-label">Places</span>
                <p>{selectedPlaces.length} selected</p>
              </div>
            )}
            {(selectedFlight || selectedHotel) && (
              <div className="summary-total">
                <span>Total</span>
                <strong>${total.toLocaleString()}</strong>
                <p className={budget >= total ? 'summary-ok' : 'summary-warn'}>
                  {budget >= total
                    ? `Within budget ($${(budget - total).toLocaleString()} left)`
                    : `Over budget by $${(total - budget).toLocaleString()}`}
                </p>
              </div>
            )}
            <Button
              size="lg"
              loading={booking}
              disabled={!selectedFlight || !selectedHotel}
              onClick={handleBook}
              className="summary-book"
            >
              {user ? 'Save trip' : 'Sign in to save trip'}
            </Button>
          </aside>
        </div>
      )}
    </div>
  );
}
