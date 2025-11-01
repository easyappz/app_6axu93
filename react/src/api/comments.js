import instance from './axios';

export async function updateComment(id, content) {
  const res = await instance.patch(`/api/comments/${id}`, { content });
  return res.data;
}

export async function deleteComment(id) {
  const res = await instance.delete(`/api/comments/${id}`);
  return res.data;
}
