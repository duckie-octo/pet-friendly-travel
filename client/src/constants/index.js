export const TENANTS = {
  skyway: {
    name: 'Skyway Travel',
    tagline: 'Elevate Every Journey',
    accent: '#1a6bdb',
    accentLight: '#e8f0fd',
    accentDark: '#0d3e82',
    logo: '✈',
  },
};

export const DESTINATIONS = [
  { code: 'JFK', label: 'New York (JFK)', city: 'New York', country: 'USA' },
  { code: 'LAX', label: 'Los Angeles (LAX)', city: 'Los Angeles', country: 'USA' },
  { code: 'LHR', label: 'London (LHR)', city: 'London', country: 'UK' },
  { code: 'CDG', label: 'Paris (CDG)', city: 'Paris', country: 'France' },
  { code: 'HND', label: 'Tokyo (HND)', city: 'Tokyo', country: 'Japan' },
  { code: 'SFO', label: 'San Francisco (SFO)', city: 'San Francisco', country: 'USA' },
];

export const DEMO_DEPART_DATE = '2026-08-15';
export const DEMO_RETURN_DATE = '2026-08-25';

export function destinationByCode(code) {
  return DESTINATIONS.find((d) => d.code === code);
}

export function cityForAirport(code) {
  return destinationByCode(code)?.city;
}
