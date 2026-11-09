import 'react-native-gesture-handler';
import React, { useEffect } from 'react';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { configureApi } from '../src/lib/api';
import { colors } from '../src/theme/colors';
const client = new QueryClient({ defaultOptions: { queries: { retry: 1, staleTime: 30_000 } } });
export default function RootLayout() {
  useEffect(() => { AsyncStorage.multiGet(['naviqra.apiUrl', 'naviqra.apiKey']).then(([url, key]) => { if (url[1]) configureApi(url[1], key[1] || ''); }); }, []);
  return <QueryClientProvider client={client}><StatusBar style="dark"/><Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.canvas } }}><Stack.Screen name="(tabs)"/><Stack.Screen name="trip/[id]" options={{ presentation: 'card', animation: 'slide_from_right' }}/></Stack></QueryClientProvider>;
}
