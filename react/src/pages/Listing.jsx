import React, { useEffect, useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getListingById, getComments, createComment } from '../api/listings';
import { updateComment, deleteComment } from '../api/comments';
import { useAuth } from '../state/authContext';

function Listing({ onRequireAuth }) {
  const { id } = useParams();
  const [listing, setListing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [comments, setComments] = useState([]);
  const [commentsLoading, setCommentsLoading] = useState(true);
  const [commentError, setCommentError] = useState('');
  const [newContent, setNewContent] = useState('');
  const [sending, setSending] = useState(false);

  const [editingId, setEditingId] = useState(null);
  const [editingValue, setEditingValue] = useState('');
  const [updating, setUpdating] = useState(false);

  const { user } = useAuth();

  const listingUrl = useMemo(() => listing?.url || '', [listing]);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        setLoading(true);
        const data = await getListingById(id);
        if (active) setListing(data.listing || null);
      } catch (e) {
        if (active) setError('Объявление не найдено');
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => { active = false; };
  }, [id]);

  const loadComments = async () => {
    try {
      setCommentsLoading(true);
      setCommentError('');
      const data = await getComments(id);
      setComments(data.items || []);
    } catch (e) {
      setCommentError('Не удалось загрузить комментарии');
    } finally {
      setCommentsLoading(false);
    }
  };

  useEffect(() => {
    loadComments();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const addComment = async (e) => {
    e.preventDefault();
    setCommentError('');
    if (!user) {
      onRequireAuth && onRequireAuth();
      return;
    }
    if (!newContent) return;
    try {
      setSending(true);
      await createComment(id, newContent);
      setNewContent('');
      await loadComments();
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Ошибка отправки комментария';
      setCommentError(typeof msg === 'string' ? msg : 'Ошибка');
    } finally {
      setSending(false);
    }
  };

  const startEdit = (comment) => {
    setEditingId(comment.id);
    setEditingValue(comment.content || '');
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditingValue('');
  };

  const saveEdit = async (commentId) => {
    setCommentError('');
    try {
      setUpdating(true);
      await updateComment(commentId, editingValue);
      setEditingId(null);
      setEditingValue('');
      await loadComments();
    } catch (e) {
      const msg = e?.response?.data?.detail || 'Не удалось сохранить изменения';
      setCommentError(typeof msg === 'string' ? msg : 'Ошибка');
    } finally {
      setUpdating(false);
    }
  };

  const removeComment = async (commentId) => {
    setCommentError('');
    const confirmed = window.confirm('Удалить комментарий?');
    if (!confirmed) return;
    try {
      setUpdating(true);
      await deleteComment(commentId);
      await loadComments();
    } catch (e) {
      const msg = e?.response?.data?.detail || 'Не удалось удалить комментарий';
      setCommentError(typeof msg === 'string' ? msg : 'Ошибка');
    } finally {
      setUpdating(false);
    }
  };

  const formatDate = (value) => {
    try {
      const d = new Date(value);
      return d.toLocaleString();
    } catch {
      return '';
    }
  };

  if (loading) {
    return <div data-easytag="id1-react/src/pages/Listing.jsx" className="text-center text-neutral-500">Загрузка…</div>;
  }

  if (error || !listing) {
    return <div data-easytag="id2-react/src/pages/Listing.jsx" className="text-center text-neutral-500">{error || 'Ошибка загрузки'}</div>;
  }

  return (
    <section data-easytag="id3-react/src/pages/Listing.jsx" className="space-y-10">
      <header data-easytag="id4-react/src/pages/Listing.jsx" className="space-y-3">
        <h1 data-easytag="id5-react/src/pages/Listing.jsx" className="text-2xl md:text-3xl font-semibold tracking-tight">{listing.title || 'Объявление'}</h1>
        <div data-easytag="id6-react/src/pages/Listing.jsx" className="flex items-center gap-4 text-neutral-600">
          <span data-easytag="id7-react/src/pages/Listing.jsx">Просмотров: {typeof listing.view_count === 'number' ? listing.view_count : 0}</span>
          {listingUrl && (
            <a data-easytag="id8-react/src/pages/Listing.jsx" href={listingUrl} target="_blank" rel="noreferrer" className="text-accent hover:underline underline-offset-4">Открыть на Авито</a>
          )}
        </div>
      </header>

      <div data-easytag="id9-react/src/pages/Listing.jsx" className="rounded-2xl overflow-hidden bg-white border">
        <div data-easytag="id10-react/src/pages/Listing.jsx" className="w-full aspect-[16/9] bg-neutral-100">
          {listing.image_url ? (
            <img data-easytag="id11-react/src/pages/Listing.jsx" src={listing.image_url} alt={listing.title || 'listing image'} className="w-full h-full object-cover" />
          ) : (
            <div data-easytag="id12-react/src/pages/Listing.jsx" className="w-full h-full" />
          )}
        </div>
      </div>

      <section data-easytag="id13-react/src/pages/Listing.jsx" className="space-y-6">
        <h2 data-easytag="id14-react/src/pages/Listing.jsx" className="text-xl font-medium">Комментарии</h2>

        <form data-easytag="id15-react/src/pages/Listing.jsx" onSubmit={addComment} className="space-y-3">
          <textarea data-easytag="id16-react/src/pages/Listing.jsx" value={newContent} onChange={(e) => setNewContent(e.target.value)} className="w-full rounded-2xl border px-4 py-3 bg-white focus:outline-none" rows={3} placeholder={user ? 'Оставьте комментарий…' : 'Войдите, чтобы оставить комментарий'} />
          <div data-easytag="id17-react/src/pages/Listing.jsx" className="flex justify-end">
            <button data-easytag="id18-react/src/pages/Listing.jsx" type="submit" disabled={sending || !user || newContent.length === 0} className="px-5 py-2 rounded-xl bg-black text-white hover:bg-neutral-800 transition-colors disabled:opacity-60">
              {sending ? 'Отправка…' : 'Отправить'}
            </button>
          </div>
          {commentError && <p data-easytag="id18a-react/src/pages/Listing.jsx" className="text-sm text-red-600">{commentError}</p>}
        </form>

        <div data-easytag="id19-react/src/pages/Listing.jsx" className="space-y-4">
          {commentsLoading && (
            <div data-easytag="id20-react/src/pages/Listing.jsx" className="text-neutral-500">Загрузка комментариев…</div>
          )}
          {!commentsLoading && comments.length === 0 && (
            <div data-easytag="id21-react/src/pages/Listing.jsx" className="text-neutral-500">Пока нет комментариев</div>
          )}
          {!commentsLoading && comments.map((c) => {
            const isOwner = typeof c.is_owner === 'boolean' ? c.is_owner : (!!user && c.author?.id === user.id);
            return (
              <article data-easytag="id22-react/src/pages/Listing.jsx" key={c.id} className="rounded-2xl border bg-white p-4">
                <header data-easytag="id23-react/src/pages/Listing.jsx" className="flex items-center justify-between mb-2">
                  <div data-easytag="id24-react/src/pages/Listing.jsx" className="text-sm text-neutral-600">
                    <span data-easytag="id24a-react/src/pages/Listing.jsx">{c.author?.email || c.author?.name || 'Аноним'}</span>
                    <span data-easytag="id24b-react/src/pages/Listing.jsx" className="ml-2 text-neutral-400">{formatDate(c.created_at)}</span>
                  </div>
                  {isOwner && (
                    <div data-easytag="id25-react/src/pages/Listing.jsx" className="flex items-center gap-2">
                      {editingId === c.id ? (
                        <>
                          <button data-easytag="id26-react/src/pages/Listing.jsx" onClick={() => saveEdit(c.id)} disabled={updating || editingValue.length === 0} className="px-3 py-1 rounded-lg bg-black text-white text-sm disabled:opacity-60">Сохранить</button>
                          <button data-easytag="id27-react/src/pages/Listing.jsx" onClick={cancelEdit} className="px-3 py-1 rounded-lg border text-sm">Отмена</button>
                        </>
                      ) : (
                        <>
                          <button data-easytag="id28-react/src/pages/Listing.jsx" onClick={() => startEdit(c)} className="px-3 py-1 rounded-lg border text-sm">Редактировать</button>
                          <button data-easytag="id29-react/src/pages/Listing.jsx" onClick={() => removeComment(c.id)} disabled={updating} className="px-3 py-1 rounded-lg border text-sm">Удалить</button>
                        </>
                      )}
                    </div>
                  )}
                </header>
                {editingId === c.id ? (
                  <textarea data-easytag="id30-react/src/pages/Listing.jsx" value={editingValue} onChange={(e) => setEditingValue(e.target.value)} className="w-full rounded-xl border px-3 py-2 focus:outline-none" rows={3} />
                ) : (
                  <p data-easytag="id31-react/src/pages/Listing.jsx" className="leading-relaxed">{c.content}</p>
                )}
              </article>
            );
          })}
        </div>
      </section>
    </section>
  );
}

export default Listing;
