import instance from './axios';

/**
 * Auth API (strictly follows api_schema.yaml)
 *
 * - POST /api/auth/register -> 201 { user, token }
 * - POST /api/auth/login    -> 200 { user, token }
 * - GET  /api/auth/me       -> 200 UserMe
 *
 * Always returns response.data as is.
 */
export async function register({ email, password, name }) {
  const res = await instance.post('/api/auth/register', { email, password, name });
  return res.data;
}

export async function login({ email, password }) {
  const res = await instance.post('/api/auth/login', { email, password });
  return res.data;
}

export async function me() {
  const res = await instance.get('/api/auth/me');
  return res.data;
}
