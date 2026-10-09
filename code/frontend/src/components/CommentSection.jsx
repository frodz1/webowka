import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api.js';
import { useAuth } from '../auth.jsx';
import { timeAgo } from '../utils.js';
import CommentForm from './CommentForm.jsx';
import VoteButtons from './VoteButtons.jsx';

function buildTree(items) {
  const nodes = new Map(items.map((c) => [c.id, { ...c, children: [] }]));
  const roots = [];
  for (const node of nodes.values()) {
    const parent = node.parent_id && nodes.get(node.parent_id);
    (parent ? parent.children : roots).push(node);
  }
  return roots;
}

function Comment({ node, postId, depth, flat, authorsById, onChange }) {
  const { user } = useAuth();
  const [mode, setMode] = useState(null); // null | 'reply' | 'edit'
  const [collapsed, setCollapsed] = useState(false);
  const isOwner = user && node.author_id === user.id;
  const parentAuthor = flat && node.parent_id ? authorsById.get(node.parent_id) : null;

  async function remove() {
    if (!confirm('Usunąć ten komentarz?')) return;
    try {
      await api.del(`/comments/${node.id}`);
      onChange();
    } catch (err) {
      alert(err.message);
    }
  }

  const done = () => {
    setMode(null);
    onChange();
  };

  return (
    <div className={`comment ${depth > 0 && !flat ? 'nested' : ''}`}>
      <div className="comment-row">
        {node.deleted ? <div className="votes-spacer" /> : <VoteButtons kind="comments" id={node.id} score={node.score} myVote={node.my_vote} />}
        <div className="comment-main">
          <div className="meta">
            <strong>{node.author ?? '[usunięto]'}</strong>
            <span>{timeAgo(node.created_at)}</span>
            {node.updated_at && !node.deleted && <span>(edytowano)</span>}
            {parentAuthor && <span>↳ do {parentAuthor}</span>}
            {!flat && node.children.length > 0 && (
              <button className="link-btn" onClick={() => setCollapsed(!collapsed)}>
                {collapsed ? `[+] ${node.children.length}` : '[–]'}
              </button>
            )}
          </div>
          {mode === 'edit' ? (
            <CommentForm comment={node} onDone={done} onCancel={() => setMode(null)} autoFocus />
          ) : (
            <p className={`comment-body ${node.deleted ? 'muted' : ''}`}>{node.body}</p>
          )}
          {!node.deleted && mode !== 'edit' && (
            <div className="actions">
              {user ? (
                <button className="link-btn" onClick={() => setMode(mode === 'reply' ? null : 'reply')}>
                  Odpowiedz
                </button>
              ) : (
                <Link to="/login">Zaloguj się, aby odpowiedzieć</Link>
              )}
              {isOwner && (
                <>
                  <button className="link-btn" onClick={() => setMode('edit')}>
                    Edytuj
                  </button>
                  <button className="link-btn danger" onClick={remove}>
                    Usuń
                  </button>
                </>
              )}
            </div>
          )}
          {mode === 'reply' && (
            <CommentForm postId={postId} parentId={node.id} onDone={done} onCancel={() => setMode(null)} autoFocus />
          )}
        </div>
      </div>
      {!flat && !collapsed && node.children.map((child) => (
        <Comment key={child.id} node={child} postId={postId} depth={depth + 1} flat={false} authorsById={authorsById} onChange={onChange} />
      ))}
    </div>
  );
}

export default function CommentSection({ postId, comments, onChange }) {
  const { user } = useAuth();
  const [flat, setFlat] = useState(false);
  const tree = useMemo(() => buildTree(comments), [comments]);
  const authorsById = useMemo(() => new Map(comments.map((c) => [c.id, c.author ?? '[usunięto]'])), [comments]);
  const flatList = useMemo(
    () => comments.map((c) => ({ ...c, children: [] })),
    [comments],
  );
  const list = flat ? flatList : tree;

  return (
    <section className="comments">
      <div className="comments-head">
        <h3>Komentarze ({comments.filter((c) => !c.deleted).length})</h3>
        <div className="toggle">
          <button className={!flat ? 'active' : ''} onClick={() => setFlat(false)}>
            Drzewo
          </button>
          <button className={flat ? 'active' : ''} onClick={() => setFlat(true)}>
            Płaski widok
          </button>
        </div>
      </div>

      {user ? (
        <CommentForm postId={postId} onDone={onChange} />
      ) : (
        <p className="muted">
          <Link to="/login">Zaloguj się</Link>, aby komentować.
        </p>
      )}

      {list.length === 0 && <p className="muted">Brak komentarzy. Bądź pierwszy!</p>}
      {list.map((node) => (
        <Comment key={node.id} node={node} postId={postId} depth={0} flat={flat} authorsById={authorsById} onChange={onChange} />
      ))}
    </section>
  );
}
