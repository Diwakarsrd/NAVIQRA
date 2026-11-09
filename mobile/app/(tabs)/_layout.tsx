import React from 'react';
import { Tabs } from 'expo-router';
import { Compass, Map, Sparkles, Heart, UserRound } from 'lucide-react-native';
import { colors } from '../../src/theme/colors';
export default function TabLayout() {
  return <Tabs screenOptions={{ headerShown: false, tabBarActiveTintColor: colors.green, tabBarInactiveTintColor: '#9AA39D', tabBarStyle: { height: 82, paddingTop: 10, paddingBottom: 20, borderTopColor: colors.line, backgroundColor: '#FFFFFF', elevation: 0 }, tabBarLabelStyle: { fontSize: 10, fontWeight: '700' } }}>
    <Tabs.Screen name="index" options={{ title: 'Discover', tabBarIcon: ({ color, size }) => <Compass color={color} size={size}/> }}/>
    <Tabs.Screen name="trips" options={{ title: 'My trips', tabBarIcon: ({ color, size }) => <Map color={color} size={size}/> }}/>
    <Tabs.Screen name="concierge" options={{ title: 'AI concierge', tabBarIcon: ({ color, size }) => <Sparkles color={color} size={size}/> }}/>
    <Tabs.Screen name="saved" options={{ title: 'Saved', tabBarIcon: ({ color, size }) => <Heart color={color} size={size}/> }}/>
    <Tabs.Screen name="profile" options={{ title: 'Profile', tabBarIcon: ({ color, size }) => <UserRound color={color} size={size}/> }}/>
  </Tabs>;
}
