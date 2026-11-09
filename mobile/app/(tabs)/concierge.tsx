import React, { useState } from 'react';
import { Alert, KeyboardAvoidingView, Platform, ScrollView, StyleSheet, Text, View } from 'react-native';
import { router, useLocalSearchParams } from 'expo-router';
import { Sparkles, Plane, CalendarDays, Wallet, Users, ArrowRight, ShieldCheck } from 'lucide-react-native';
import { Screen, Eyebrow, Heading, Field, Button, Pill } from '../../src/components/ui';
import { colors } from '../../src/theme/colors';
import { api } from '../../src/lib/api';
import { useAppStore } from '../../src/store/app-store';
export default function ConciergeScreen() {
  const params = useLocalSearchParams<{ destination?: string }>();
  const travelerId = useAppStore(s => s.travelerId); const setPlan = useAppStore(s => s.setActivePlan);
  const [origin, setOrigin] = useState('Bengaluru'); const [destination, setDestination] = useState(params.destination || 'Kyoto');
  const [start, setStart] = useState('2026-12-12'); const [end, setEnd] = useState('2026-12-17'); const [budget, setBudget] = useState('1800'); const [travelers, setTravelers] = useState('2'); const [interests, setInterests] = useState('food, culture, architecture'); const [loading, setLoading] = useState(false);
  async function createPlan() {
    if (!origin.trim() || !destination.trim() || !/^\d{4}-\d{2}-\d{2}$/.test(start) || !/^\d{4}-\d{2}-\d{2}$/.test(end) || Number.isNaN(Number(budget)) || Number(budget) <= 0) { Alert.alert('Check your trip details', 'Enter an origin, destination, valid dates (YYYY-MM-DD), and a positive budget.'); return; }
    if (new Date(end) <= new Date(start)) { Alert.alert('Check your dates', 'Your return date must be after your departure date.'); return; }
    setLoading(true);
    try {
      const plan = await api.planTrip({ traveler_id: travelerId, origin, destination, start_date: start, end_date: end, budget: Number(budget), currency: 'USD', travelers: Math.max(1, Math.min(30, Number(travelers) || 1)), interests: interests.split(',').map(x => x.trim()).filter(Boolean), constraints: [] });
      setPlan(plan); router.push(`/trip/${plan.trip_id}`);
    } catch (error) { Alert.alert('Could not plan your trip', error instanceof Error ? error.message : 'Please try again.'); }
    finally { setLoading(false); }
  }
  return <Screen><KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}><ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={{ paddingBottom: 30, gap: 18 }}>
    <View style={s.top}><View style={s.spark}><Sparkles color={colors.green} size={22}/></View><Pill active>YOUR PERSONAL TRAVEL INTELLIGENCE</Pill></View>
    <Heading subtitle="A little context is all your travel agents need to start shaping something special.">Let's make a journey of it.</Heading>
    <View style={s.assistant}><Text style={s.assistantLabel}>NAVIQRA CONCIERGE</Text><Text style={s.assistantText}>I'll bring together the details, shape a thoughtful itinerary, and remember what matters to you.</Text></View>
    <View style={s.form}><Field label="WHERE ARE YOU STARTING?" value={origin} onChangeText={setOrigin} placeholder="Your city"/><Field label="WHERE TO?" value={destination} onChangeText={setDestination} placeholder="Destination"/><View style={s.row}><View style={{ flex: 1 }}><Field label="DEPARTURE · YYYY-MM-DD" value={start} onChangeText={setStart} autoCapitalize="none"/></View><View style={{ flex: 1 }}><Field label="RETURN · YYYY-MM-DD" value={end} onChangeText={setEnd} autoCapitalize="none"/></View></View><View style={s.row}><View style={{ flex: 1 }}><Field label="TOTAL BUDGET · USD" value={budget} onChangeText={setBudget} keyboardType="decimal-pad"/></View><View style={{ flex: 1 }}><Field label="TRAVELERS" value={travelers} onChangeText={setTravelers} keyboardType="number-pad"/></View></View><Field label="WHAT ARE YOU INTO?" value={interests} onChangeText={setInterests} placeholder="Food, nature, design..."/></View>
    <View style={s.note}><ShieldCheck size={16} color={colors.green}/><Text style={s.noteText}>Your preferences stay attached to your traveler profile. No booking is made without your approval.</Text></View>
    <Button title="Build my journey" onPress={createPlan} loading={loading}/>
  </ScrollView></KeyboardAvoidingView></Screen>;
}
const s = StyleSheet.create({ top: { flexDirection: 'row', alignItems: 'center', gap: 11, marginTop: 8 }, spark: { width: 48, height: 48, borderRadius: 16, backgroundColor: colors.mint, alignItems: 'center', justifyContent: 'center' }, assistant: { backgroundColor: colors.green, padding: 18, borderRadius: 20, gap: 8 }, assistantLabel: { color: colors.lime, fontSize: 9, fontWeight: '900', letterSpacing: 1.5 }, assistantText: { color: '#fff', fontSize: 14, lineHeight: 21 }, form: { gap: 15 }, row: { flexDirection: 'row', gap: 12 }, note: { backgroundColor: colors.mint, padding: 13, borderRadius: 14, flexDirection: 'row', alignItems: 'center', gap: 9 }, noteText: { flex: 1, color: colors.greenDark, fontSize: 11, lineHeight: 16 } });
