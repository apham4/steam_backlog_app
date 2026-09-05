import axios from 'axios';
import { config } from '../config';

// Axios is used for making API calls.
// Having an axios instance instead of using a global axios object allows specifying common config options in one place.
export const apiClient = axios.create({
    baseURL: config.api.baseUrl,
    headers: {
        'Content-Type': 'application/json',
    },
});