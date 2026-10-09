import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api } from '../api.js';
import Pagination from '../components/Pagination.jsx';
import PostCard from '../components/PostCard.jsx';

const SORTS = [
  ['hot', 'Gorące'],
  ['new', 'Najnowsze'],
  ['best', 'Najlepsze'],
];

export default function Board() {
  const [params, setParams] = useSearchParams();
  const sort = params.get('sort') || 'hot';
  const tag = params.get('tag') || '';
  const page = Number(params.get('page') || 1);

  const [data, setData] = useState(null);
  const [tags, setTags] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    setError('');
    const qs = new URLSearchParams({ sort, page });
    if (tag) qs.set('tag', tag);
    api
      .get(`/posts?${qs}`)
      .then(setData)
      .catch((err) => setError(err.message));
  }, [sort, tag, page]);

  useEffect(() => {
    api.get('/tags').then((d) => setTags(d.items)).catch(() => {});
  }, []);

  function update(changes) {
    const next = new URLSearchParams(params);
    for (const [k, v] of Object.entries(changes)) (v ? next.set(k, v) : next.delete(k));
    setParams(next);
  }

  return (
    <div className="layout">
      <div>
        <div className="toolbar">
          <div className="toggle">
            {SORTS.map(([key, label]) => (
              <button key={key} className={sort === key ? 'active' : ''} onClick={() => update({ sort: key, page: '' })}>
                {label}
              </button>
            ))}
          </div>
          {tag && (
            <button className="tag removable" onClick={() => update({ tag: '', page: '' })}>
              #{tag} ✕
            </button>
          )}
        </div>

        {error && <p className="error">{error}</p>}
        {!data && !error && <p className="muted">Ładowanie…</p>}
        {data && data.items.length === 0 && (
          <p className="muted">
            Brak znalezisk. <Link to="/submit">Dodaj pierwsze!</Link>
          </p>
        )}
        {data?.items.map((post) => (
          <PostCard key={post.id} post={post} />
        ))}

        {data && <Pagination page={data.page} pages={data.pages} onChange={(n) => { update({ page: String(n) }); window.scrollTo({ top: 0 }); }} />}
      </div>

      <aside className="card sidebar">
        <h3>Tagi</h3>
        {tags.length === 0 && <p className="muted">Brak tagów.</p>}
        <div className="tag-list">
          {tags.map((t) => (
            <button key={t.tag} className={`tag ${t.tag === tag ? 'selected' : ''}`} onClick={() => update({ tag: t.tag, page: '' })}>
              #{t.tag} <small>{t.count}</small>
            </button>
          ))}
        </div>
      </aside>
    </div>
  );
}
