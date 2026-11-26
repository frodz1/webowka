import { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { api } from '../api.js';
import { useAuth } from '../auth.jsx';
import CommentSection from '../components/CommentSection.jsx';
import PostCard from '../components/PostCard.jsx';
import { ArrowLeft } from '../components/Icon.jsx';
import { SkeletonCard } from '../components/Skeleton.jsx';

export default function PostPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [error, setError] = useState('');

  const loadComments = useCallback(
    () =>
      Promise.all([api.get(`/posts/${id}`), api.get(`/posts/${id}/comments`)])
        .then(([p, c]) => {
          setPost(p.post);
          setComments(c.items);
        })
        .catch((err) => setError(err.message)),
    [id],
  );

  useEffect(() => {
    setPost(null);
    setError('');
    loadComments();
  }, [loadComments, user?.id]);

  async function remove() {
    if (!confirm('Usunąć ten wpis razem z komentarzami?')) return;
    try {
      await api.del(`/posts/${id}`);
      navigate('/');
    } catch (err) {
      alert(err.message);
    }
  }

  const back = (
    <Link to="/" className="back">
      <ArrowLeft /> Tablica
    </Link>
  );
  if (error) return <p className="error">{error}</p>;
  if (!post)
    return (
      <div>
        {back}
        <SkeletonCard />
      </div>
    );

  const isOwner = user && user.id === post.author_id;

  return (
    <div>
      {back}
      <PostCard post={post} hideSnippet>
        {isOwner && (
          <>
            <Link to={`/post/${post.id}/edit`}>Edytuj</Link>
            <button className="link-btn danger" onClick={remove}>
              Usuń
            </button>
          </>
        )}
      </PostCard>
      {post.body && <div className="card post-body">{post.body}</div>}
      <CommentSection postId={post.id} comments={comments} onChange={loadComments} />
    </div>
  );
}
