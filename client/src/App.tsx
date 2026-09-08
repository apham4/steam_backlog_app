// Main entry point for the React app.

import { useEffect, useState } from 'react';
import { useAppDispatch, useAppSelector } from './app/hooks';
import { saveSettingsAndFetchRecommendation, skipAndFetchNewRecommendation, clearExclusionsAndFetchRecommendation } from './features/recommendation/recommendationSlice';
import { fetchCurrentUser, setToken, logout } from './features/auth/authSlice';
import { RecommendationCard } from './components/RecommendationCard';
import { SettingsControls } from './components/SettingsControls';
import type { UserSettings } from './types/api';
import { config } from './config';
import { ERROR_MESSAGES } from './types/errors';

const DEFAULT_SETTINGS: UserSettings = {
  backlog_threshold_mins: config.settingsBounds.backlogThreshold.default,
  recent_threshold_mins: config.settingsBounds.recentThreshold.default,
  skip_cooldown_days: config.settingsBounds.skipCooldown.default,
};

function App() {
  const dispatch = useAppDispatch();

  // exploding state.recommendations. Alias for status because auth also has a status
  const { currentRecommendation, status: recommendationStatus, error: recError } = useAppSelector(
    (state) => state.recommendations
  );

  const { token, user, status: authStatus } = useAppSelector(
    (state) => state.auth
  );

  // Settings state (local var)
  // useState<T> returns a 2-element array: the state variable and the setter function
  const [draftSettings, setDraftSettings] = useState<UserSettings>(DEFAULT_SETTINGS);
  const [settingsDirty, setSettingsDirty] = useState<boolean>(false);

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

  // 3. Initialize settings from user profile after authentication
  useEffect(() => {
    if (user?.settings)
    {
      setDraftSettings(user.settings);
      setSettingsDirty(false);
    }
  }, [user]);

  const handleLogin = () => {
    // Direct browser to backend OpenID route
    window.location.href = config.api.baseUrl + config.api.endpoints.auth;
  };

  const handleLogout = () => {
    dispatch(logout());
  };

  const handleSettingsChanged = (updatedSettings: UserSettings) => {
    setDraftSettings(updatedSettings);
    setSettingsDirty(true);
  };

  const handleFetchRecommendation = () => {
    dispatch(saveSettingsAndFetchRecommendation(draftSettings));
    setSettingsDirty(false);
  };

  const handleClearExclusions = () => {
    dispatch(clearExclusionsAndFetchRecommendation(draftSettings));
    setSettingsDirty(false);
  };

  const handleSkip = (appId: number) => {
    dispatch(skipAndFetchNewRecommendation({ appId, settings: draftSettings }));
    setSettingsDirty(false);
  }

  const shouldShowActionButton = !currentRecommendation || settingsDirty || recommendationStatus === 'failed';
  const errorMessage = recError ? ERROR_MESSAGES[recError.code]?.(recError.params) || 'An unexpected error occured.' : null;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between items-center p-6">
      {/* Header Navbar */}
      <header className="w-full max-w-4xl flex justify-between items-center py-4 border-b border-slate-800/80">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white">Backlog Pick</h1>
          <p className="text-xs text-slate-500">Steam Library Recommendation Engine</p>
        </div>

        {user && (
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
        )}
      </header>

      {/* Main Content */}
      <main className="w-full max-w-xl flex flex-col items-center gap-6 my-auto py-8">
        {!token ? (
          <div className="text-center space-y-5 max-w-md p-8 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl">
            <h2 className="text-2xl font-bold text-white">Sign In to Continue</h2>
            <p className="text-sm text-slate-400">
              Sign in with Steam to evaluate your backlog habits and find tailored recommendations.
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
        ) : (
          <>
            {/* Settings Controls */}
            <SettingsControls
              settings={draftSettings}
              onSettingChanged={handleSettingsChanged}
            />

            {/* Centered Action Button */}
            {shouldShowActionButton && (
              <button
                onClick={handleFetchRecommendation}
                disabled={recommendationStatus === 'loading'}
                className="w-full py-3.5 px-6 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 text-white font-semibold text-base shadow-lg shadow-blue-900/30 transition duration-200"
              >
                {recommendationStatus === 'loading' ? 'Evaluating Library...' : 'Get Your Backlog Recommendation'}
              </button>
            )}

            {/* Error Display */}
            {recommendationStatus === 'failed' && recError && (
              <div className="w-full bg-red-950/40 border border-red-800/80 text-red-200 p-5 rounded-xl text-center space-y-3">
                <p className="text-sm font-medium">{errorMessage}</p>
                <button
                  onClick={handleClearExclusions}
                  className="px-4 py-2 bg-red-800 hover:bg-red-700 text-white text-xs font-semibold rounded-lg transition"
                >
                  Clear All Exclusions
                </button>
              </div>
            )}

            {/* Recommendation Card */}
            {currentRecommendation && (
              <RecommendationCard recommendation={currentRecommendation} onSkip={handleSkip} />
            )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="text-xs text-slate-600 my-4">
        Steam Backlog App &bull; Powered by FastAPI & React
      </footer>
    </div>
  );
}

export default App;