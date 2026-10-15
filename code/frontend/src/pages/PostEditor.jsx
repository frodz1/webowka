import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { api } from '../api.js';
import { useAuth } from '../auth.jsx';

const EMPTY = { title: '', url: '', body: '', tag: '' };

/** Dodawanie (/submit) i edycja (/post/:id/edit) wpisu. */
export default function PostEditor() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState(EMPTY);
  const [loading, setLoading] = useState(Boolean(id));
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!id) return;
    api
      .get(`/posts/${id}`)
      .then(({ post }) => {
        if (post.author_id !== user.id) return setError('Możesz edytować tylko własne wpisy.');
        setForm({ title: post.title, url: post.url ?? '', body: post.body ?? '', tag: post.tag ?? '' });
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id, user.id]);

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError('');
    try {
      const { post } = id ? await api.put(`/posts/${id}`, form) : await api.post('/posts', form);
      navigate(`/post/${post.id}`);
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  if (loading) return <p className="muted">Ładowanie…</p>;

  return (
    <form className="card form" onSubmit={submit}>
      <h2>{id ? 'Edytuj znalezisko' : 'Dodaj znalezisko'}</h2>
      <label>
        Tytuł
        <input value={form.title} onChange={set('title')} maxLength={200} required />
      </label>
      <label>
        Link
        <input type="url" value={form.url} onChange={set('url')} placeholder="https://…" />
      </label>
      <label>
        Krótki tekst
        <textarea value={form.body} onChange={set('body')} rows={5} maxLength={5000} />
      </label>
      <small className="muted">Podaj link, tekst albo oba.</small>
      <label>
        Tag (opcjonalnie)
        <input value={form.tag} onChange={set('tag')} maxLength={32} placeholder="np. gry" />
      </label>
      {error && <p className="error">{error}</p>}
      <div className="form-actions">
        <button className="btn btn-primary" disabled={busy}>
          {id ? 'Zapisz zmiany' : 'Opublikuj'}
        </button>
        <button type="button" className="btn btn-ghost" onClick={() => navigate(-1)}>
          Anuluj
        </button>
      </div>
    </form>
  );
}
