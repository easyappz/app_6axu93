import instance from './axios';

export async function register({ email, password, name }) {
  const res = await instance.post('/auth/register', { email, password, name });
  return res.data;
}

export async function login({ email, password }) {
  const res = await instance.post('/auth/login', { email, password });
  return res.data;
}

export async function me() {
  const res = await instance.get('/auth/me');
  return res.data;
}
