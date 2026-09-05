// hooks.ts file generally for exporting pre-typed versions of Redux's primary hooks:
// - useDispatch: for components to trigger state updates.
// - useSelector: for components to read data from Redux store.
// These typed versions make sure the hooks are strongly typed, specifically to the store configuration in store.ts

import type { TypedUseSelectorHook } from 'react-redux';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState, AppDispatch } from './store';

export const useAppDispatch = () => useDispatch<AppDispatch>(); // Calls standard useDispatch with AppDispatch (from store.ts) to return a dispatch function specific to store.ts
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;