import api, { clearTokens, setTokens } from './api';

function normalizeUser(raw) {
  if (!raw) return null;
  const fullName =
    raw.full_name || [raw.first_name, raw.last_name].filter(Boolean).join(' ');
  const parts = fullName.split(' ');
  return {
    user_id: raw.user_id,
    email: raw.email,
    full_name: fullName,
    first_name: raw.first_name || parts[0] || '',
    last_name: raw.last_name || parts.slice(1).join(' ') || '',
    locale: raw.locale || 'en',
    is_admin: raw.is_admin || false,
  };
}

export const authService = {
  getStoredUser() {
    try {
      const raw = localStorage.getItem('user');
      return raw ? normalizeUser(JSON.parse(raw)) : null;
    } catch {
      return null;
    }
  },

  isAuthenticated() {
    return Boolean(localStorage.getItem('access_token'));
  },

  clearTokens,

  async login({ email, password }) {
    const body = new URLSearchParams();
    body.append('username', email.trim().toLowerCase());
    body.append('password', password);

    const { data: tokenData } = await api.post('/auth/login', body, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });

    setTokens(tokenData.access_token);
    const { data: me } = await api.get('/auth/me');
    const user = normalizeUser(me);
    localStorage.setItem('user', JSON.stringify(user));
    return { user, access_token: tokenData.access_token };
  },

  async register({ first_name, last_name, email, password, phone_number }) {
    await api.post('/auth/register', {
      first_name,
      last_name,
      email: email.trim().toLowerCase(),
      password,
      phone_number: phone_number || null,
    });
    return this.login({ email, password });
  },

  async getMe() {
    const { data } = await api.get('/auth/me');
    const user = normalizeUser(data);
    localStorage.setItem('user', JSON.stringify(user));
    return user;
  },

  async logout() {
    clearTokens();
  },
};
