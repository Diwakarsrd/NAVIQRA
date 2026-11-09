import React, { useState } from 'react';
import { Alert, ScrollView, StyleSheet, Text, View, Pressable } from 'react-native';
import { router } from 'expo-router';
import { ArrowLeft, Compass, MapPin, Search, Sparkles } from 'lucide-react-native';
import { Screen, Heading, Field, Button, Pill } from '../src/components/ui';
import { colors } from '../src/theme/colors';
import { api } from '../src/lib/api';
import type { ProviderResult } from '../src/types/api';
export default function ExploreScreen() {
  const [destination, setDestination] = useState('Kyoto'); const [results, setResults] = useState<ProviderResult[]>([]); const [notice, setNotice] = useState(''); const [loading, setLoading] = useState(false);
  async function search() { if (!destination.trim()) return; setLoading(true); try { const data = await api.search(destination.trim()); setResults(data.results); setNotice(data.notice); } catch (e) { Alert.alert('Search unavailable', e instanceof Error ? e.message : 'Check your backend connection.'); } finally { setLoading(false); } }
  return <Screen><ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={{ paddingBottom: 30, gap: 18 }}>
    <Pressable onPress={() => router.back()} style={s.back}><ArrowLeft size={18} color={colors.ink}/><Text style={s.backText}>BACK TO DISCOVER</Text></Pressable>
    <View style={s.icon}><Compass color={colors.green} size={23}/></View><Heading subtitle="Search the connected travel provider layer and discover what's available in the current demo environment.">Explore a place.</Heading>
    <View style={s.search}><Field label="DESTINATION" value={destination} onChangeText={setDestination} placeholder="Try Kyoto, Bali or Rome"/><Button title="Search places" onPress={search} loading={loading}/></View>
    {notice ? <View style={s.notice}><Sparkles color={colors.green} size={16}/><Text style={s.noticeText}>{notice}</Text></View> : null}
    {results.map(item => <View key={item.id} style={s.result}><View style={s.resultIcon}><MapPin color={colors.green} size={18}/></View><View style={{ flex: 1, gap: 5 }}><Text style={s.resultType}>{item.type.toUpperCase()} · {item.source.toUpperCase()}</Text><Text style={s.resultName}>{item.name}</Text><Text style={s.resultPrice}>{item.currency} {item.price.toFixed(0)}</Text></View><Pill>{item.bookable ? 'BOOKABLE' : 'DEMO'}</Pill></View>)}
    {results.length > 0 ? <Text style={s.disclaimer}>Demo inventory is illustrative only. It is not live availability and cannot be booked.</Text> : <View style={s.empty}><Search color={colors.green} size={22}/><Text style={s.emptyText}>Search a destination to query the provider adapter.</Text></View>}
  </ScrollView></Screen>;
}
const s = StyleSheet.create({ back: { flexDirection: 'row', alignItems: 'center', gap: 9, marginTop: 8 }, backText: { color: colors.ink, fontSize: 10, fontWeight: '900', letterSpacing: 1.2 }, icon: { width: 50, height: 50, backgroundColor: colors.mint, borderRadius: 17, alignItems: 'center', justifyContent: 'center', marginTop: 8 }, search: { backgroundColor: '#fff', borderWidth: 1, borderColor: colors.line, borderRadius: 21, padding: 16, gap: 13 }, notice: { backgroundColor: colors.mint, borderRadius: 14, padding: 13, flexDirection: 'row', alignItems: 'center', gap: 9 }, noticeText: { color: colors.greenDark, fontSize: 11, flex: 1, lineHeight: 16 }, result: { backgroundColor: '#fff', borderRadius: 18, borderWidth: 1, borderColor: colors.line, padding: 15, flexDirection: 'row', alignItems: 'center', gap: 12 }, resultIcon: { width: 42, height: 42, backgroundColor: colors.mint, borderRadius: 14, alignItems: 'center', justifyContent: 'center' }, resultType: { color: colors.muted, fontSize: 9, fontWeight: '900', letterSpacing: 1 }, resultName: { color: colors.ink, fontSize: 13, fontWeight: '800' }, resultPrice: { color: colors.green, fontSize: 12, fontWeight: '800' }, disclaimer: { color: colors.gold, fontSize: 11, lineHeight: 16 }, empty: { backgroundColor: '#fff', borderRadius: 20, padding: 25, alignItems: 'center', gap: 12 }, emptyText: { color: colors.muted, fontSize: 12, textAlign: 'center' } });
