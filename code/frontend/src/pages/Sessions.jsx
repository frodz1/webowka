import { useCallback, useEffect, useState } from 'react';
import { api } from '../api.js';
import { useAuth } from '../auth.jsx';
import { timeAgo } from '../utils.js';

export default function Sessions() {
  const { logout } = useAuth();
  const [items, setItems] = useState(null);
  const [error, setError] = useState('');

  const load = useCallback(() => {
    setError('');
    api.get('/auth/sessions').then((d) => setItems(d.items)).catch((e) => setError(e.message));
  }, []);

  useEffect(load, [load]);

  async function revoke(session) {
    if (session.current) {
      await logout();
      return;
    }
    await api.del(`/auth/sessions/${session.id}`).catch((e) => setError(e.message));
    load();
  }

  async function revokeOthers() {
    if (!confirm('Wylogować wszystkie pozostałe sesje?')) return;
    await api.del('/auth/sessions').catch((e) => setError(e.message));
    load();
  }

  const others = items ? items.filter((s) => !s.current).length : 0;

  return (
    <div>
      <div className="toolbar">
        <h2>Aktywne sesje</h2>
        {others > 0 && (
          <button className="btn btn-ghost" onClick={revokeOthers}>
            Wyloguj pozostałe ({others})
          </button>
        )}
      </div>
      {error && <p className="error">{error}</p>}
      {items === null && !error && <p className="muted">Ładowanie…</p>}
      {items?.map((s) => (
        <div className="card session" key={s.id}>
          <div>
            <strong title={s.user_agent}>{s.user_agent || 'Nieznane urządzenie'}</strong>
            {s.current && <span className="session-current"> · ta sesja</span>}
            <p className="muted">
              IP {s.ip || '—'} · ostatnia aktywność {timeAgo(s.last_seen)} · zalogowano {timeAgo(s.created_at)}
            </p>
          </div>
          <button className="btn btn-ghost" onClick={() => revoke(s)}>
            Wyloguj
          </button>
        </div>
      ))}
    </div>
  );
}
