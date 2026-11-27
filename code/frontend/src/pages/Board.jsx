import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api } from '../api.js';
import Pagination from '../components/Pagination.jsx';
import PostCard from '../components/PostCard.jsx';
import { Inbox, Plus } from '../components/Icon.jsx';
import { SkeletonList } from '../components/Skeleton.jsx';

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
        <div className="page-head">
          <div>
            <h1>{tag ? `#${tag}` : 'Tablica'}</h1>
            <p className="muted">{tag ? 'Znaleziska z tym tagiem' : 'Najciekawsze znaleziska społeczności'}</p>
          </div>
          <div className="toggle">
            {SORTS.map(([key, label]) => (
              <button key={key} className={sort === key ? 'active' : ''} onClick={() => update({ sort: key, page: '' })}>
                {label}
              </button>
            ))}
          </div>
        </div>
        {tag && (
          <div className="toolbar">
            <button className="tag removable" onClick={() => update({ tag: '', page: '' })}>
              #{tag} ✕
            </button>
          </div>
        )}

        {error && <p className="error">{error}</p>}
        {!data && !error && <SkeletonList />}
        {data && data.items.length === 0 && (
          <div className="card empty">
            <Inbox />
            <p>Brak znalezisk.</p>
            <Link to="/submit" className="btn btn-primary">
              <Plus /> Dodaj pierwsze
            </Link>
          </div>
        )}
        {data?.items.map((post) => (
          <PostCard key={post.id} post={post} />
        ))}

        {data && <Pagination page={data.page} pages={data.pages} onChange={(n) => { update({ page: String(n) }); window.scrollTo({ top: 0 }); }} />}
      </div>

      <aside className="sidebar-col">
        <div className="card cta">
          <h3>Masz coś ciekawego?</h3>
          <p>Podziel się linkiem albo krótkim tekstem i zbierz głosy społeczności.</p>
          <Link to="/submit" className="btn btn-primary btn-block">
            <Plus /> Dodaj znalezisko
          </Link>
        </div>
        <div className="card sidebar">
          <h3>Tagi</h3>
          {tags.length === 0 && <p className="muted">Brak tagów.</p>}
          <div className="tag-list">
            {tags.map((t) => (
              <button key={t.tag} className={`tag ${t.tag === tag ? 'selected' : ''}`} onClick={() => update({ tag: t.tag, page: '' })}>
                #{t.tag} <small>{t.count}</small>
              </button>
            ))}
          </div>
        </div>
      </aside>
    </div>
  );
}
