// This is to parse the .env file

interface ImportMetaEnv {
    readonly VITE_API_BASE_URL: string;
    readonly VITE_STEAM_RUN_APP: string;
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
}