import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api.js';
import PostCard from '../components/PostCard.jsx';
import { timeAgo } from '../utils.js';

export default function MyContent() {
  const [tab, setTab] = useState('posts');
  const [posts, setPosts] = useState(null);
  const [comments, setComments] = useState(null);
  const [error, setError] = useState('');

  const load = useCallback(() => {
    setError('');
    api.get('/me/posts').then((d) => setPosts(d.items)).catch((e) => setError(e.message));
    api.get('/me/comments').then((d) => setComments(d.items)).catch((e) => setError(e.message));
  }, []);

  useEffect(load, [load]);

  async function removePost(id) {
    if (!confirm('Usunąć ten wpis razem z komentarzami?')) return;
    await api.del(`/posts/${id}`).catch((e) => alert(e.message));
    load();
  }

  async function removeComment(id) {
    if (!confirm('Usunąć ten komentarz?')) return;
    await api.del(`/comments/${id}`).catch((e) => alert(e.message));
    load();
  }

  return (
    <div>
      <div className="toolbar">
        <div className="toggle">
          <button className={tab === 'posts' ? 'active' : ''} onClick={() => setTab('posts')}>
            Moje wpisy {posts && `(${posts.length})`}
          </button>
          <button className={tab === 'comments' ? 'active' : ''} onClick={() => setTab('comments')}>
            Moje komentarze {comments && `(${comments.length})`}
          </button>
        </div>
      </div>
      {error && <p className="error">{error}</p>}

      {tab === 'posts' && (
        <>
          {posts?.length === 0 && (
            <p className="muted">
              Nie dodałeś jeszcze żadnych wpisów. <Link to="/submit">Dodaj pierwszy</Link>.
            </p>
          )}
          {posts?.map((post) => (
            <PostCard key={post.id} post={post}>
              <Link to={`/post/${post.id}/edit`}>Edytuj</Link>
              <button className="link-btn danger" onClick={() => removePost(post.id)}>
                Usuń
              </button>
            </PostCard>
          ))}
        </>
      )}

      {tab === 'comments' && (
        <>
          {comments?.length === 0 && <p className="muted">Nie napisałeś jeszcze żadnych komentarzy.</p>}
          {comments?.map((c) => (
            <article key={c.id} className="card">
              <div className="meta">
                <span>
                  w <Link to={`/post/${c.post_id}`}>{c.post_title}</Link> · {timeAgo(c.created_at)} · wynik {c.score}
                </span>
                <button className="link-btn danger" onClick={() => removeComment(c.id)}>
                  Usuń
                </button>
              </div>
              <p className="comment-body">{c.body}</p>
            </article>
          ))}
        </>
      )}
    </div>
  );
}
