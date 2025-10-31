import instance from './axios';

export async function ingestListing(url) {
  const res = await instance.post('/listings/ingest', { url });
  return res.data;
}

export async function getTopListings({ sort = 'views', limit = 10 } = {}) {
  const res = await instance.get('/listings', { params: { sort, limit } });
  return res.data;
}

export async function getListingById(id) {
  const res = await instance.get(`/listings/${id}`);
  return res.data;
}

export async function getComments(id) {
  const res = await instance.get(`/listings/${id}/comments`);
  return res.data;
}

export async function createComment(id, content) {
  const res = await instance.post(`/listings/${id}/comments`, { content });
  return res.data;
}
