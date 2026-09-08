// Slice for authentication feature.
// Check the recommendationSlice's comments for slice stuff.

import type { PayloadAction } from '@reduxjs/toolkit';
import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import type { User } from '../../types/api';
import { apiClient } from '../../api/client';
import { config } from '../../config';

interface AuthState {
    token: string | null;
    user: User | null;
    status: 'idle' | 'loading' | 'succeeded' | 'failed';
}

// localStorage is on the browser, persisting across page refreshes and browser restarts until explicitly cleared.
const savedToken = localStorage.getItem(config.auth.tokenKey);

const initialState: AuthState = {
    token: savedToken,
    user: null,
    status: 'idle',
}

export const fetchCurrentUser = createAsyncThunk(
    'auth/fetchCurrentUser',
    async (_, { rejectWithValue }) => {
        try {
            const response = await apiClient.get<User>(config.api.endpoints.me)
            return response.data;
        } catch (err: any) {
            // Saved token is not returning any user, so the session expired.
            return rejectWithValue(err.response?.data?.detail || 'Session expired'); 
        }
    }
);

export const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        setToken: (state, action: PayloadAction<string>) => {
            state.token = action.payload;
            localStorage.setItem(config.auth.tokenKey, action.payload); 
        },
        logout: (state) => {
            state.token = null;
            state.user = null;
            state.status = 'idle';
            localStorage.removeItem(config.auth.tokenKey); 
        }
    },
    extraReducers: (builder) => {
        builder.addCase(
            fetchCurrentUser.pending, (state) => {
                state.status = 'loading';
            }
        ).addCase(
            fetchCurrentUser.fulfilled, (state, action: PayloadAction<User>) => {
                state.status = 'succeeded';
                state.user = action.payload;
            }
        ).addCase(
            fetchCurrentUser.rejected, (state) => {
                state.status = 'failed';
                state.token = null;
                state.user = null;
                localStorage.removeItem(config.auth.tokenKey); 
            }
        );
    },
});

export const { setToken, logout } = authSlice.actions;
export default authSlice.reducer;