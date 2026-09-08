// Component displaying the recommended game.

import React from 'react';
import type { Recommendation } from '../types/api';
import { config } from '../config';

// properties, used to pass data from parent component to child component.
interface Props {
    recommendation: Recommendation;
    onSkip: (appId: number) => void;
}

export const RecommendationCard: React.FC<Props> = ({ recommendation, onSkip }) => {
    const handleLaunchGameOnSteam = () => {
        // I can just run this with JavaScript from browser? That seems dangerous.
        window.location.href = config.steam.runUrl(recommendation.game_details.app_id);
    };

    return (
        <div className="max-w-xl w-full bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl transition-all duration-300">
            {/* Game Header Image */}
            <div className="relative h-64 w-full bg-slate-950 overflow-hidden">
                {recommendation.game_details.image_url ? (
                <img
                    src={recommendation.game_details.image_url}
                    alt={recommendation.game_details.name}
                    className="w-full h-full object-cover"
                />
                ) : (
                <div className="flex items-center justify-center h-full text-slate-500">
                    No Image Available
                </div>
                )}
                <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent" />
            </div>

            {/* Content */}
            <div className="p-6 space-y-4">
                {/* Title & Review Score */}
                <div className="flex justify-between items-start gap-4">
                    <h2 className="text-2xl font-bold text-white tracking-wide">
                        {recommendation.game_details.name}
                    </h2>
                    {recommendation.game_details.review_score_desc && (
                        <span className="shrink-0 text-xs font-semibold px-2.5 py-1 rounded bg-blue-950 text-blue-400 border border-blue-800">
                            {recommendation.game_details.review_score_desc}
                        </span>
                    )}
                </div>

                {/* Short Description */}
                <p className="text-slate-400 text-sm line-clamp-3">
                    {recommendation.game_details.short_description || 'No description provided.'}
                </p>

                {/* Matched Genre Tags */}
                <div className="space-y-1.5">
                    <span className="text-xs uppercase font-medium text-slate-500 tracking-wider">
                        Matched Taste Profile
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                        {recommendation.matched_genres.map((genre) => (
                            <span
                                key={genre}
                                className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-800 px-2 py-0.5 rounded-full"
                            >
                                ✓ {genre}
                            </span>
                            ))}
                            {recommendation.game_details.genres
                                .filter((g) => !recommendation.matched_genres.includes(g))
                                .slice(0, 3)
                                .map((genre) => (
                                    <span
                                    key={genre}
                                    className="text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full"
                                    >
                                        {genre}
                                    </span>
                        ))}
                    </div>
                </div>

                {/* Recent Game Context */}
                {recommendation.recent_games_referenced.length > 0 && (
                    <p className="text-xs text-slate-500 italic">
                        Recommended based on your recent playtime in: {recommendation.recent_games_referenced.slice(0, 3).join(', ')}
                    </p>
                )}

                {/* Actions Grid */}
                <div className="grid grid-cols-3 gap-3 pt-4 border-t border-slate-800">
                    <button
                        onClick={handleLaunchGameOnSteam}
                        className="flex items-center justify-center py-2.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition shadow-lg shadow-blue-900/30"
                    >
                        Play Now
                    </button>
                    <a
                        href={recommendation.trailer_search_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center justify-center py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-sm transition"
                    >
                        Trailer ↗
                    </a>
                    <button
                        onClick={() => onSkip(recommendation.game_details.app_id)}
                        className="flex items-center justify-center py-2.5 px-4 rounded-xl bg-red-950/40 hover:bg-red-900/60 border border-red-900/50 text-red-300 font-semibold text-sm transition"
                    >
                        Next Game
                    </button>
                </div>

                {/* Secondary Links */}
                <div className="text-center pt-2">
                    <a
                        href={recommendation.store_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-slate-500 hover:text-slate-400 underline underline-offset-4"
                    >
                        View on Steam Store Page ↗
                    </a>
                </div>
            </div>
        </div>
    );
};