// For translating error codes to error messages

export type RecommendationErrorCode = 
| 'NO_GAMES'
| 'NO_QUALIFYING_BACKLOG'
| 'ALL_EXCLUDED'
| 'FETCH_FAILED';

export interface ApiErrorDetail {
    code: RecommendationErrorCode;
    params?: Record<string, any>;
}

export const ERROR_MESSAGES: Record<RecommendationErrorCode, (params?: Record<string, any>) => string> = {
    NO_GAMES: () => 'You have no games in your Steam library.',
    NO_QUALIFYING_BACKLOG: (params) => `You have no backlog game with a playtime under ${params?.threshold ?? 60} minutes in your library.`,
    ALL_EXCLUDED: () => 'You have gone through your entire backlog recommendation.',
    FETCH_FAILED: () => 'Failed to fetch recommendations. Make sure your Steam profile is public.'
}