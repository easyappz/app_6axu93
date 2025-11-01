import instance from './axios';

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
