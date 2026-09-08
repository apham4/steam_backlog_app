// Config for consolidating all the env constants

export const config = {
    api: {
        baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
        endpoints: {
            auth: '/api/auth/login',
            getRecommendation: '/api/recommendation/get',
            exclusion: '/api/exclusions',
            library: '/api/steam/library',
            me: '/api/me',
            settings: '/api/settings',
        },
    },
    auth: {
        tokenKey: import.meta.env.VITE_STORAGE_TOKEN_KEY || 'steam_backlog_token',
    },
    steam: {
        runUrl: (appId: number | string) => {
            const template = import.meta.env.VITE_STEAM_RUN_APP || 'steam://run/{app_id}';
            return template.replace('{app_id}', String(appId));
        },
    },
    settingsBounds: {
        backlogThreshold: {
            min: Number(import.meta.env.VITE_BACKLOG_MIN ?? 0),
            sliderMax: Number(import.meta.env.VITE_BACKLOG_SLIDER_MAX ?? 120),
            default: Number(import.meta.env.VITE_BACKLOG_DEFAULT ?? 60),
        },
        recentThreshold: {
            min: Number(import.meta.env.VITE_RECENT_MIN ?? 30),
            sliderMax: Number(import.meta.env.VITE_RECENT_SLIDER_MAX ?? 150),
            default: Number(import.meta.env.VITE_RECENT_DEFAULT ?? 120),
        },
        skipCooldown: {
            min: Number(import.meta.env.VITE_SKIP_CD_MIN ?? 1),
            sliderMax: Number(import.meta.env.VITE_SKIP_CD_SLIDER_MAX ?? 7),
            default: Number(import.meta.env.VITE_SKIP_CD_DEFAULT ?? 3),
        },
    },
} as const;