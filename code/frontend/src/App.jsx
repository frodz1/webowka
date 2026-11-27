import { Link, NavLink, Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { useAuth } from './auth.jsx';
import Avatar from './components/Avatar.jsx';
import { Plus } from './components/Icon.jsx';
import ThemeToggle from './components/ThemeToggle.jsx';
import Board from './pages/Board.jsx';
import PostPage from './pages/PostPage.jsx';
import PostEditor from './pages/PostEditor.jsx';
import MyContent from './pages/MyContent.jsx';
import Sessions from './pages/Sessions.jsx';
import { Login, Register } from './pages/AuthPages.jsx';

function Logo() {
  return (
    <Link to="/" className="logo" aria-label="QuestLog – tablica">
      <span className="logo-mark" aria-hidden="true">
        Q
      </span>
      <span className="logo-text">
        Quest<span>Log</span>
      </span>
    </Link>
  );
}

function Header() {
  const { user, logout } = useAuth();
  return (
    <header className="topbar">
      <div className="topbar-inner container">
        <Logo />
        <nav className="nav">
          <NavLink to="/" end>
            Tablica
          </NavLink>
          {user && <NavLink to="/me">Moje treści</NavLink>}
          {user && <NavLink to="/sessions">Sesje</NavLink>}
        </nav>
        <div className="topbar-right">
          <ThemeToggle />
          {user ? (
            <>
              <Link to="/submit" className="btn btn-primary">
                <Plus />
                <span className="hide-sm">Dodaj</span>
              </Link>
              <span className="who">
                <Avatar name={user.username} size={30} />
                <span className="who-name">{user.username}</span>
              </span>
              <button className="btn btn-ghost" onClick={logout}>
                Wyloguj
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-ghost">
                Zaloguj
              </Link>
              <Link to="/register" className="btn btn-primary">
                Załóż konto
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

function RequireAuth({ children }) {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading) return <p className="muted">Ładowanie…</p>;
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  return children;
}

function Footer() {
  const { user } = useAuth();
  return (
    <footer className="footer">
      <div className="footer-inner container">
        <div>
          <Logo />
          <p className="muted">Znajdź. Oceń. Skomentuj.</p>
        </div>
        <div className="footer-right">
          <nav className="footer-links">
            <Link to="/">Tablica</Link>
            {user ? (
              <>
                <Link to="/submit">Dodaj znalezisko</Link>
                <Link to="/me">Moje treści</Link>
              </>
            ) : (
              <>
                <Link to="/login">Zaloguj</Link>
                <Link to="/register">Załóż konto</Link>
              </>
            )}
          </nav>
          <p className="muted footer-note">© {new Date().getFullYear()} QuestLog · projekt na zajęcia z aplikacji webowych</p>
        </div>
      </div>
    </footer>
  );
}

export default function App() {
  return (
    <div className="app">
      <Header />
      <main className="container">
        <Routes>
          <Route path="/" element={<Board />} />
          <Route path="/post/:id" element={<PostPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/submit"
            element={
              <RequireAuth>
                <PostEditor />
              </RequireAuth>
            }
          />
          <Route
            path="/post/:id/edit"
            element={
              <RequireAuth>
                <PostEditor />
              </RequireAuth>
            }
          />
          <Route
            path="/me"
            element={
              <RequireAuth>
                <MyContent />
              </RequireAuth>
            }
          />
          <Route
            path="/sessions"
            element={
              <RequireAuth>
                <Sessions />
              </RequireAuth>
            }
          />
          <Route path="*" element={<p className="muted">Nie znaleziono strony.</p>} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}
