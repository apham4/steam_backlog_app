// This is for fetching a recommendation and submitting exclusions.

import type { PayloadAction } from '@reduxjs/toolkit';
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { Recommendation } from '../../types/api';
import { apiClient } from '../../api/client';

interface RecommendationState {
    currentRecommendation: Recommendation | null;
    status: 'idle' | 'loading' | 'succeeded' | 'failed';
    error: string | null;
}

const initialState: RecommendationState = {
    currentRecommendation: null,
    status: 'idle',
    error: null,
}

// Thunk = some chunk of delayed logic. Basically declaring an async function
// This is for getting the next backlog recommendation
export const fetchNextRecommendation = createAsyncThunk(
    'recommendation/fetchNext', // name to call by 
    async (_, { rejectWithValue }) => { // The _ is for params to pass in.
        try {
            const response = await apiClient.get<Recommendation>('api/recommendation/get'); // TODO: maybe config here?
            return response.data;
        } catch (error: any) {
            return rejectWithValue(
                error.response?.data?.detail || 'Failed to fetch recommendation.'
            );
        }
    }
);

// Async thunk to skip a game (add to exclusion)
export const skipRecommendation = createAsyncThunk(
    'recommendation/skip',
    async (appId: number, { dispatch, rejectWithValue }) => { // dispatch is for calling another async thunk i guess.
        try {
            await apiClient.post('api/exclusions', { app_id: appId });
            // Call to get the next recommendation immediately (what for?)
            dispatch(fetchNextRecommendation());
        } catch (error: any) {
            return rejectWithValue(
                error.response?.data?.detail || 'Failed to skip recommendation.'
            );
        };
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
        builder.addCase(
            fetchNextRecommendation.pending, (state) => {
                state.status = 'loading';
                state.error = null;
            }
        )
        .addCase(
            fetchNextRecommendation.fulfilled, (state, action: PayloadAction<Recommendation>) => {
                state.status = 'succeeded';
                state.currentRecommendation = action.payload;
            }
        )
        .addCase(
            fetchNextRecommendation.rejected, (state, action) => {
                state.status = 'failed';
                state.error = (action.payload as string) || 'Recommendation failed error message.';
            }
        );
    },
});

export const { clearRecommendation } = recommendationSlice.actions; // export clearRecommendation from recommendationSlice.actions so that it can be called elsewhere.
export default recommendationSlice.reducer; // export the main generated reducer function to handle state changes. To be imported and registered in Redux store setup file (store.ts).