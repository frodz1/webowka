import { useState } from 'react';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth.jsx';

function AuthForm({ mode }) {
  const isRegister = mode === 'register';
  const { user, login, register } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ login: '', username: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to={location.state?.from || '/'} replace />;

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError('');
    try {
      if (isRegister) await register({ username: form.username, email: form.email, password: form.password });
      else await login({ login: form.login, password: form.password });
      navigate(location.state?.from || '/', { replace: true });
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <div className="auth">
    <form className="card form auth-card" onSubmit={submit}>
      <div className="auth-head">
        <span className="logo-mark lg" aria-hidden="true">
          Q
        </span>
        <h2>{isRegister ? 'Załóż konto' : 'Witaj ponownie'}</h2>
        <p className="muted">{isRegister ? 'Dołącz i dziel się ciekawymi znaleziskami.' : 'Zaloguj się, aby głosować i komentować.'}</p>
      </div>
      {isRegister ? (
        <>
          <label>
            Nazwa użytkownika
            <input value={form.username} onChange={set('username')} minLength={3} maxLength={32} pattern="[A-Za-z0-9_]+" title="Litery, cyfry i _" required autoFocus />
          </label>
          <label>
            E-mail
            <input type="email" value={form.email} onChange={set('email')} required />
          </label>
        </>
      ) : (
        <label>
          Nazwa użytkownika lub e-mail
          <input value={form.login} onChange={set('login')} required autoFocus />
        </label>
      )}
      <label>
        Hasło
        <input type="password" value={form.password} onChange={set('password')} minLength={isRegister ? 10 : undefined} maxLength={isRegister ? 128 : undefined} required />
      </label>
      {error && <p className="error">{error}</p>}
      <button className="btn btn-primary btn-block btn-lg" disabled={busy}>
        {isRegister ? 'Załóż konto' : 'Zaloguj'}
      </button>
      <p className="muted auth-foot">
        {isRegister ? (
          <>
            Masz już konto? <Link to="/login" state={location.state}>Zaloguj się</Link>
          </>
        ) : (
          <>
            Nie masz konta? <Link to="/register" state={location.state}>Zarejestruj się</Link>
          </>
        )}
      </p>
    </form>
    </div>
  );
}

export const Login = () => <AuthForm mode="login" />;
export const Register = () => <AuthForm mode="register" />;
