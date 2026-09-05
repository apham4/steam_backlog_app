// Main entry point for the React app.

import { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from './app/hooks';
import { fetchNextRecommendation } from './features/recommendation/recommendationSlice';
import { RecommendationCard } from './components/RecommendationCard';

function App() {
  const dispatch = useAppDispatch();

  // exploding state.recommendations?
  const { currentRecommendation, status, error } = useAppSelector(
    (state) => state.recommendations
  );

  // What does this mean?
  useEffect(() => {
    dispatch(fetchNextRecommendation());
  }, [dispatch]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between items-center p-6">
      {/* Header */}
      <header className="text-center space-y-1 my-6">
        <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
          Backlog Pick
        </h1>
        <p className="text-slate-400 text-sm">
          Algorithmic recommendations tailored from your recent Steam library habits.
        </p>
      </header>

      {/* Main Card View */}
      <main className="w-full flex justify-center items-center my-auto">
        {status === 'loading' && (
          <div className="flex flex-col items-center space-y-3">
            <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-slate-400 text-sm">Finding your next game...</p>
          </div>
        )}

        {status === 'failed' && (
          <div className="bg-red-950/50 border border-red-800 text-red-200 p-6 rounded-xl max-w-md text-center space-y-3">
            <p className="font-semibold text-sm">{error}</p>
            <button
              onClick={() => dispatch(fetchNextRecommendation())}
              className="px-4 py-2 bg-red-800 hover:bg-red-700 text-white text-xs font-semibold rounded-lg transition"
            >
              Retry
            </button>
          </div>
        )}

        {status === 'succeeded' && currentRecommendation && (
          <RecommendationCard recommendation={currentRecommendation} />
        )}
      </main>

      {/* Footer */}
      <footer className="text-xs text-slate-600 my-6">
        Steam Backlog App &bull; Powered by FastAPI & React
      </footer>
    </div>
  );
}

export default App;