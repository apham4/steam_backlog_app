// TypeScript interface matching the Pydantic schemas
// TypeScript is JavaScript + extras, so it needs compiling into JS before running in browser.
// These are the shape of objects to be used, related to the API endpoints defined in the FastAPI backend.

export interface UserSettings {
    backlog_threshold_mins: number;
    recent_threshold_mins: number;
    skip_cooldown_days: number;
}

export interface User {
    id: number;
    steam_id: string;
    username: string;
    avatar_url?: string; // ? means optional
    settings?: UserSettings;
}

export interface GameDetails {
    app_id: number;
    name: string;
    image_url?: string;
    review_score?: string;
    total_reviews?: number;
    review_score_desc?: string;
    developers?: string[];
    publishers?: string[];
    short_description: string;
    categories: string[];
    genres: string[];
}

export interface Recommendation {
    game_details: GameDetails;
    store_url: string;
    trailer_search_url: string;
    matched_genres: string[];
    recent_games_referenced: string[];
}