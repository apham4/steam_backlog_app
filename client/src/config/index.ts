// Config for consolidating all the env constants

export const config = {
    api: {
        baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
        endpoints: {
            auth: '/api/auth/login',
            getRecommendation: '/api/recommendation/get',
            addExclusion: '/api/exclusions',
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
} as const;