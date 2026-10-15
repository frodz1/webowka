import { useState } from 'react';
import { api } from '../api.js';

/** Formularz nowego komentarza / odpowiedzi / edycji (gdy podano `comment`). */
export default function CommentForm({ postId, parentId = null, comment = null, onDone, onCancel, autoFocus }) {
  const [body, setBody] = useState(comment?.body ?? '');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError('');
    try {
      if (comment) await api.put(`/comments/${comment.id}`, { body });
      else await api.post(`/posts/${postId}/comments`, { body, parent_id: parentId });
      setBody('');
      onDone();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="comment-form" onSubmit={submit}>
      <textarea
        value={body}
        onChange={(e) => setBody(e.target.value)}
        placeholder="Napisz komentarz…"
        rows={3}
        maxLength={5000}
        autoFocus={autoFocus}
        required
      />
      {error && <p className="error">{error}</p>}
      <div className="form-actions">
        <button className="btn btn-primary" disabled={busy || !body.trim()}>
          {comment ? 'Zapisz' : parentId ? 'Odpowiedz' : 'Skomentuj'}
        </button>
        {onCancel && (
          <button type="button" className="btn btn-ghost" onClick={onCancel}>
            Anuluj
          </button>
        )}
      </div>
    </form>
  );
}
