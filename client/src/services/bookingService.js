import api from './api';

/** Trip persistence (ERD: trips, trip_flights, trip_hotels, trip_pet_places) */
export const bookingService = {
  async listBookings() {
    const { data } = await api.get('/trips/');
    return data;
  },

  async getBooking(tripId) {
    const { data } = await api.get(`/trips/${tripId}`);
    return data;
  },

  async createBooking(payload) {
    const { data } = await api.post('/trips/', payload);
    return data;
  },

  async deleteBooking(tripId) {
    await api.delete(`/trips/${tripId}`);
  },
};
