// Store configuration and typed hooks.
// Redux store is the centralized state container/single source of truth (instead of storing states in separate React components).
// Components can't modify store, they must dispatch actions, which reducers are hooked to, to change data state.
// Components subscribe to store to re-render when there's data updates.

import { configureStore } from '@reduxjs/toolkit';
import recommendationReducer from '../features/recommendation/recommendationSlice'; // This is from the export default recommendationSlice.reducer line.
import authReducer from '../features/auth/authSlice';

// store instance to be used in other spots.
// configureStore defines the top-level keys of state tree.
// state.recommendations branch managed by recommendationReducer.
export const store = configureStore({
    reducer: {
        recommendations: recommendationReducer,
        auth: authReducer,
    },
});

// Export the type of store.getState (to get the complete state object) and store.dispatch (to run actions) matching the definition above so that store.getState will be strongly typed when used.
export type RootState = ReturnType<typeof store.getState>; 
export type AppDispatch = typeof store.dispatch;