import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ingestListing, getTopListings } from '../api/listings';

function Home({ onRequireAuth }) {
  const [url, setUrl] = useState('');
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState('');
  const [listings, setListings] = useState([]);
  const [loadingTop, setLoadingTop] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        setLoadingTop(true);
        const data = await getTopListings({ sort: 'views', limit: 20 });
        if (active) setListings(data.items || []);
      } catch (e) {
        // noop
      } finally {
        if (active) setLoadingTop(false);
      }
    })();
    return () => { active = false; };
  }, []);

  const submitUrl = async (e) => {
    e.preventDefault();
    setError('');
    if (!url) {
      setError('Введите ссылку на объявление Avito');
      return;
    }
    try {
      setProcessing(true);
      const data = await ingestListing(url);
      const id = data?.listing?.id;
      if (id) {
        navigate(`/ad/${id}`);
      }
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Не удалось обработать ссылку. Попробуйте ещё раз.';
      setError(typeof msg === 'string' ? msg : 'Ошибка обработки');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <section data-easytag="id1-react/src/pages/Home.jsx" className="space-y-12">
      <div data-easytag="id2-react/src/pages/Home.jsx" className="text-center space-y-4">
        <h1 data-easytag="id3-react/src/pages/Home.jsx" className="text-4xl md:text-6xl font-semibold tracking-tight">Авитолог</h1>
        <p data-easytag="id4-react/src/pages/Home.jsx" className="text-neutral-600 max-w-2xl mx-auto">Вставьте ссылку на объявление Avito — мы подготовим карточку с обсуждениями и счётчиком просмотров.</p>
      </div>

      <form data-easytag="id5-react/src/pages/Home.jsx" onSubmit={submitUrl} className="max-w-2xl mx-auto flex items-center gap-3">
        <input
          data-easytag="id6-react/src/pages/Home.jsx"
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://www.avito.ru/..."
          className="flex-1 rounded-2xl border px-5 py-4 bg-white focus:outline-none"
        />
        <button data-easytag="id7-react/src/pages/Home.jsx" type="submit" disabled={processing} className="px-6 py-4 rounded-2xl bg-black text-white hover:bg-neutral-800 transition-colors disabled:opacity-60">{processing ? 'Обработка…' : 'Найти'}</button>
      </form>

      {error && (
        <p data-easytag="id8-react/src/pages/Home.jsx" className="text-center text-red-600">{error}</p>
      )}

      <div data-easytag="id9-react/src/pages/Home.jsx" className="space-y-6">
        <h2 data-easytag="id10-react/src/pages/Home.jsx" className="text-xl font-medium">Самые просматриваемые</h2>
        <div data-easytag="id11-react/src/pages/Home.jsx" className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {loadingTop && (
            <div data-easytag="id12-react/src/pages/Home.jsx" className="col-span-full text-center text-neutral-500">Загрузка…</div>
          )}
          {!loadingTop && listings.length === 0 && (
            <div data-easytag="id13-react/src/pages/Home.jsx" className="col-span-full text-center text-neutral-500">Нет данных</div>
          )}
          {!loadingTop && listings.map((item) => (
            <Link data-easytag="id14-react/src/pages/Home.jsx" key={item.id} to={`/ad/${item.id}`} className="group block rounded-2xl overflow-hidden bg-white border hover:shadow-soft transition-shadow">
              <div data-easytag="id15-react/src/pages/Home.jsx" className="w-full aspect-[16/9] bg-neutral-100">
                {item.image_url ? (
                  <img data-easytag="id16-react/src/pages/Home.jsx" src={item.image_url} alt={item.title || 'listing image'} className="w-full h-full object-cover" />
                ) : (
                  <div data-easytag="id17-react/src/pages/Home.jsx" className="w-full h-full" />
                )}
              </div>
              <div data-easytag="id18-react/src/pages/Home.jsx" className="p-4 space-y-2">
                <h3 data-easytag="id19-react/src/pages/Home.jsx" className="text-base font-medium group-hover:underline underline-offset-4">{item.title || 'Объявление'}</h3>
                <p data-easytag="id20-react/src/pages/Home.jsx" className="text-sm text-neutral-600">Просмотров: {typeof item.view_count === 'number' ? item.view_count : 0}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}

export default Home;
