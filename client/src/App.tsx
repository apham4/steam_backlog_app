// Main entry point for the React app.

import { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from './app/hooks';
import { fetchNextRecommendation } from './features/recommendation/recommendationSlice';
import { fetchCurrentUser, setToken, logout } from './features/auth/authSlice';
import { RecommendationCard } from './components/RecommendationCard';
import { config } from './config';

function App() {
  const dispatch = useAppDispatch();

  // exploding state.recommendations. Alias for status because auth also has a status
  const { currentRecommendation, status: recommendationStatus, error } = useAppSelector(
    (state) => state.recommendations
  );

  const { token, user, status: authStatus } = useAppSelector(
    (state) => state.auth
  );

  // 1. Detect incoming ?token= from Steam redirect
  // useEffect runs after every render. For side effects, redux state changing should not happen in here.
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const tokenParam = urlParams.get('token');
    if (tokenParam) {
      dispatch(setToken(tokenParam));
      // Clear query parameters from browser history
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, [dispatch]);

  // 2. Load authenticated user profile with token active
  useEffect(() => {
    if (token && !user) {
      dispatch(fetchCurrentUser());
    }
  }, [dispatch, token, user]);

  // 3. Fetch recommendation once user profile is confirmed.
  useEffect(() => {
    if (user)
    {
      dispatch(fetchNextRecommendation());
    }
  }, [user, dispatch]);

  const handleLogin = () => {
    // Direct browser to backend OpenID route
    window.location.href = config.api.baseUrl + config.api.endpoints.auth;
  };

  const handleLogout = () => {
    dispatch(logout());
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between items-center p-6">
      {/* Top Navbar */}
      <header className="w-full max-w-4xl flex justify-between items-center py-4 border-b border-slate-800/80">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white">Backlog Pick</h1>
          <p className="text-xs text-slate-500">Steam Library Recommendation Engine</p>
        </div>

        {user ? (
          <div className="flex items-center gap-3">
            <img
              src={user.avatar_url || ''}
              alt={user.username}
              className="w-8 h-8 rounded-full border border-slate-700"
            />
            <span className="text-sm font-semibold text-slate-200">{user.username}</span>
            <button
              onClick={handleLogout}
              className="text-xs text-slate-400 hover:text-red-400 border border-slate-800 hover:border-red-900/50 px-2.5 py-1 rounded transition"
            >
              Log out
            </button>
          </div>
        ) : null}
      </header>

      {/* Main Content Area */}
      <main className="w-full flex justify-center items-center my-auto">
        {!token ? (
          /* Unauthenticated Landing State */
          <div className="text-center space-y-5 max-w-md p-8 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl">
            <h2 className="text-2xl font-bold text-white">Sign In to Continue</h2>
            <p className="text-sm text-slate-400">
              Sign in with your Steam account so we can evaluate your playtime history, analyze recent genres, and find unplayed backlog gems.
            </p>
            <button
              onClick={handleLogin}
              className="inline-flex items-center gap-2 px-6 py-3 bg-[#171a21] hover:bg-[#2a475e] text-white font-medium text-sm rounded-xl border border-slate-700 transition shadow-lg"
            >
              <img
                src="https://community.cloudflare.steamstatic.com/public/images/signinthroughsteam/sits_01.png" // TODO: Probably replace this with something better looking
                alt="Sign in through Steam"
                className="h-8"
              />
            </button>
          </div>
        ) : authStatus === 'loading' ? (
          <div className="flex flex-col items-center space-y-3">
            <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-slate-400 text-sm">Authenticating with Steam...</p>
          </div>
        ) : recommendationStatus === 'loading' ? (
          <div className="flex flex-col items-center space-y-3">
            <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-slate-400 text-sm">Finding your next game...</p>
          </div>
        ) : recommendationStatus === 'failed' ? (
          <div className="bg-red-950/50 border border-red-800 text-red-200 p-6 rounded-xl max-w-md text-center space-y-3">
            <p className="font-semibold text-sm">{error}</p>
            <button
              onClick={() => dispatch(fetchNextRecommendation())}
              className="px-4 py-2 bg-red-800 hover:bg-red-700 text-white text-xs font-semibold rounded-lg transition"
            >
              Retry
            </button>
          </div>
        ) : recommendationStatus === 'succeeded' && currentRecommendation ? (
          <RecommendationCard recommendation={currentRecommendation} />
        ) : null}
      </main>

      {/* Footer */}
      <footer className="text-xs text-slate-600 my-4">
        Steam Backlog App &bull; Powered by FastAPI & React
      </footer>
    </div>
  );
}

export default App;