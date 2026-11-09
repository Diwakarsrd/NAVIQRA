import React from 'react';
import { ImageBackground, ScrollView, StyleSheet, Text, View, Pressable } from 'react-native';
import { Heart, MapPin } from 'lucide-react-native';
import { Screen, Eyebrow, Heading } from '../../src/components/ui';
import { colors } from '../../src/theme/colors';
import { useAppStore } from '../../src/store/app-store';
const catalog: Record<string, { country: string; image: string; note: string }> = {
  Kyoto: { country: 'Japan', image: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=900&q=85', note: 'Temple paths & quiet mornings' },
  'Amalfi Coast': { country: 'Italy', image: 'https://images.unsplash.com/photo-1533105079780-92b9be482077?w=900&q=85', note: 'Sea views & slow afternoons' },
  Bali: { country: 'Indonesia', image: 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=900&q=85', note: 'Island rituals & warm water' },
};
export default function SavedScreen() {
  const saved = useAppStore(s => s.saved); const toggle = useAppStore(s => s.toggleSaved);
  return <Screen><ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={{ paddingBottom: 30, gap: 18 }}><Eyebrow>THE PLACES THAT STAY WITH YOU</Eyebrow><Heading subtitle="Keep the places you can't stop thinking about.">Saved places</Heading>
    {saved.length ? saved.map(name => { const d = catalog[name] || catalog.Kyoto; return <View key={name} style={s.card}><ImageBackground source={{ uri: d.image }} style={s.image} imageStyle={{ borderRadius: 20 }}/><View style={s.info}><View style={{ flex: 1 }}><Text style={s.name}>{name}</Text><View style={{ flexDirection: 'row', alignItems: 'center', gap: 4, marginTop: 4 }}><MapPin size={11} color={colors.muted}/><Text style={s.country}>{d.country}</Text></View><Text style={s.note}>{d.note}</Text></View><Pressable onPress={() => toggle(name)} style={s.remove}><Heart size={17} fill={colors.green} color={colors.green}/></Pressable></View></View>; }) : <View style={s.empty}><Heart color={colors.green} size={24}/><Text style={s.emptyText}>Your saved places will appear here.</Text></View>}
  </ScrollView></Screen>;
}
const s = StyleSheet.create({ card: { backgroundColor: '#fff', borderRadius: 22, padding: 10, borderWidth: 1, borderColor: colors.line }, image: { height: 170 }, info: { flexDirection: 'row', alignItems: 'center', padding: 10, gap: 10 }, name: { color: colors.ink, fontSize: 17, fontWeight: '800' }, country: { color: colors.muted, fontSize: 11 }, note: { color: colors.muted, fontSize: 11, marginTop: 5 }, remove: { width: 40, height: 40, backgroundColor: colors.mint, borderRadius: 14, alignItems: 'center', justifyContent: 'center' }, empty: { padding: 30, alignItems: 'center', backgroundColor: '#fff', borderRadius: 20, gap: 12 }, emptyText: { color: colors.muted, fontSize: 13 } });
