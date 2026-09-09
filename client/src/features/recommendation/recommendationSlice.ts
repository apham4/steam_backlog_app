// This is for fetching a recommendation and submitting exclusions.

import type { PayloadAction } from '@reduxjs/toolkit';
import { createSlice, createAsyncThunk, isAnyOf } from '@reduxjs/toolkit';
import type { Recommendation, UserSettings } from '../../types/api';
import { apiClient } from '../../api/client';
import { config } from '../../config';
import type { ApiErrorDetail } from '../../types/errors';

interface RecommendationState {
    currentRecommendation: Recommendation | null;
    status: 'idle' | 'loading' | 'succeeded' | 'failed';
    error: ApiErrorDetail | null;
}

const initialState: RecommendationState = {
    currentRecommendation: null,
    status: 'idle',
    error: null,
}

// Thunk = some chunk of delayed logic. Basically declaring an async function
// Async thunk when clicking the action button: Update user settings and get a new recommendation
export const saveSettingsAndFetchRecommendation = createAsyncThunk(
    'recommendation/saveAndFetch',
    async (settings: UserSettings, { rejectWithValue }) => {
        try {
            // Update the settings
            await apiClient.put(config.api.endpoints.settings, settings);
            // Get new recommendation
            const recResponse = await apiClient.get<Recommendation>(config.api.endpoints.getRecommendation);
            return recResponse.data;
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to fetch recommendation.');
        }
    }
);

// Async thunk to skip a game (add to exclusion)
export const skipAndFetchNewRecommendation = createAsyncThunk(
    'recommendation/skipAndFetch',
    async (
        { appId, settings }: { appId: number; settings: UserSettings },
        { dispatch, rejectWithValue }
    ) => {
        try {
            await apiClient.post(config.api.endpoints.exclusion, { app_id: appId });
            return dispatch(saveSettingsAndFetchRecommendation(settings)).unwrap(); // With unwrap, if the inner api call fails, it will go to the catch block below. Without unwrap, it will report as success.
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to skip recommendation and fetch a new one.');
        }
    }
);

// Async thunk to clear exclusions then get a new recommendation (in case all eligible games have been excluded)
export const clearExclusionsAndFetchRecommendation = createAsyncThunk(
    'recommendation/clearExclusionsAndFetch',
    async (settings: UserSettings, { dispatch, rejectWithValue }) => {
        try {
            await apiClient.delete(config.api.endpoints.exclusion);
            return dispatch(saveSettingsAndFetchRecommendation(settings)).unwrap() // With unwrap, if the inner api call fails, it will go to the catch block below. Without unwrap, it will report as success.
        } catch (err: any) {
            return rejectWithValue(err.response?.data?.detail || 'Failed to clear exclusions and fetch a new recommendation.');
        }
    }
);

// The main slice thing
// Reducer: function for state change in response to an action
// Slice = collection of reducer logic for a single feature. Includes: state, actions that modify that state, and the reducer functions.
export const recommendationSlice = createSlice({
    name: 'recommendation', // String identifier for the slice.
    initialState, // Starting value
    reducers: { // Synchronous state transitions, to be called manually
        clearRecommendation: (state) => {
            state.currentRecommendation = null;
            state.status = 'idle';
            state.error = null;
        },
    },
    extraReducers: (builder) => { // Listen and respond to thunk actions defined outside this slice, for async actions.
        builder.addMatcher(
            isAnyOf(
                saveSettingsAndFetchRecommendation.pending,
                skipAndFetchNewRecommendation.pending,
                clearExclusionsAndFetchRecommendation.pending
            ),
            (state) => {
                state.status = 'loading';
                state.currentRecommendation = null; // To hide the recommendation card
                state.error = null;
            }
        )
        .addMatcher(
            isAnyOf(
                saveSettingsAndFetchRecommendation.fulfilled,
                skipAndFetchNewRecommendation.fulfilled,
                clearExclusionsAndFetchRecommendation.fulfilled
            ),
            (state, action: PayloadAction<Recommendation>) => {
                state.status = 'succeeded';
                state.currentRecommendation = action.payload;
            }
        )
        .addMatcher(
            isAnyOf(
                saveSettingsAndFetchRecommendation.rejected,
                skipAndFetchNewRecommendation.rejected,
                clearExclusionsAndFetchRecommendation.rejected
            ),
            (state, action) => {
                state.status = 'failed';
                state.currentRecommendation = null;
                state.error = (action.payload as ApiErrorDetail) ?? {code: 'FETCH_FAILED' };
            }
        )
    },
});

export const { clearRecommendation } = recommendationSlice.actions; // export clearRecommendation from recommendationSlice.actions so that it can be called elsewhere.
export default recommendationSlice.reducer; // export the main generated reducer function to handle state changes. To be imported and registered in Redux store setup file (store.ts).