import axios from 'axios';

// Axios is used for making API calls.
// Having an axios instance instead of using a global axios object allows specifying common config options in one place.
export const apiClient = axios.create({
    baseURL: 'http://localhost:8000', // This needs to be in a config
    headers: {
        'Content-Type': 'application/json',
    },
});