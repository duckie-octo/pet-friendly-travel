import api from './api';

export const travelService = {
  /** Live trip search: Booking.com flights/hotels + Geoapify pet places */
  async searchTrip({
    origin,
    destination,
    destCity,
    destCountry,
    departDate,
    returnDate,
    adults = 1,
    petsAllowed = true,
  }) {
    const { data } = await api.get('/trips/search', {
      params: {
        origin,
        destination,
        dest_city: destCity,
        dest_country: destCountry,
        depart_date: departDate,
        return_date: returnDate || undefined,
        adults,
        pets_allowed: petsAllowed,
      },
    });
    return data;
  },

  async saveTrip(payload) {
    const { data } = await api.post('/trips/', payload);
    return data;
  },

  /** Legacy seeded DB search (kept for fallback) */
  async searchPetFriendlyFlights({ origin, destination, date, maxPetKg, cargoOnly }) {
    const { data } = await api.get('/flights/pet-friendly/search', {
      params: {
        origin: origin || undefined,
        destination: destination || undefined,
        date: date || undefined,
        max_pet_kg: maxPetKg ?? undefined,
        cargo_only: cargoOnly ?? false,
      },
    });
    return data;
  },

  async listPetFriendlyHotels({ city, country } = {}) {
    const { data } = await api.get('/hotels/pet-friendly', {
      params: {
        city: city || undefined,
        country: country || undefined,
      },
    });
    return data;
  },

  async listPetFriendlyAirlines() {
    const { data } = await api.get('/airlines/pet-friendly');
    return data;
  },
};
