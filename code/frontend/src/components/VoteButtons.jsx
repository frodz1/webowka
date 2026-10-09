import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api.js';
import { useAuth } from '../auth.jsx';

/** Głosowanie w górę/w dół. `kind` to "posts" albo "comments"; ponowne kliknięcie cofa głos. */
export default function VoteButtons({ kind, id, score, myVote }) {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [state, setState] = useState({ score, myVote: myVote ?? null });
  const [busy, setBusy] = useState(false);

  useEffect(() => setState({ score, myVote: myVote ?? null }), [score, myVote]);

  async function vote(value) {
    if (!user) return navigate('/login');
    if (busy) return;
    setBusy(true);
    try {
      const next = state.myVote === value ? 0 : value;
      const res = await api.post(`/${kind}/${id}/vote`, { value: next });
      setState({ score: res.score, myVote: res.my_vote });
    } catch (err) {
      alert(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="votes">
      <button
        className={`vote-btn up ${state.myVote === 1 ? 'active' : ''}`}
        onClick={() => vote(1)}
        aria-label="Głos w górę"
        aria-pressed={state.myVote === 1}
      >
        ▲
      </button>
      <span className={`score ${state.score > 0 ? 'pos' : state.score < 0 ? 'neg' : ''}`}>{state.score}</span>
      <button
        className={`vote-btn down ${state.myVote === -1 ? 'active' : ''}`}
        onClick={() => vote(-1)}
        aria-label="Głos w dół"
        aria-pressed={state.myVote === -1}
      >
        ▼
      </button>
    </div>
  );
}
