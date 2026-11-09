import React from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, TextInput, View, type TextInputProps, type ViewStyle } from 'react-native';
import { colors } from '../theme/colors';
export function Screen({ children, style }: React.PropsWithChildren<{ style?: ViewStyle }>) { return <View style={[styles.screen, style]}>{children}</View>; }
export function Eyebrow({ children }: React.PropsWithChildren) { return <Text style={styles.eyebrow}>{children}</Text>; }
export function Heading({ children, subtitle }: React.PropsWithChildren<{ subtitle?: string }>) { return <View style={{ gap: 6 }}><Text style={styles.heading}>{children}</Text>{subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}</View>; }
export function Button({ title, onPress, loading, secondary, disabled }: { title: string; onPress: () => void; loading?: boolean; secondary?: boolean; disabled?: boolean }) { return <Pressable onPress={onPress} disabled={disabled || loading} style={({ pressed }) => [styles.button, secondary && styles.buttonSecondary, (pressed || disabled) && { opacity: 0.72 }]}>{loading ? <ActivityIndicator color={secondary ? colors.green : '#fff'} /> : <Text style={[styles.buttonText, secondary && { color: colors.green }]}>{title}</Text>}</Pressable>; }
export function Field({ label, ...props }: TextInputProps & { label: string }) { return <View style={{ gap: 8 }}><Text style={styles.fieldLabel}>{label}</Text><TextInput placeholderTextColor={colors.muted} style={styles.input} {...props} /></View>; }
export function Pill({ children, active }: React.PropsWithChildren<{ active?: boolean }>) { return <View style={[styles.pill, active && { backgroundColor: colors.mint }]}><Text style={[styles.pillText, active && { color: colors.green }]}>{children}</Text></View>; }
export function SectionTitle({ title, action, onAction }: { title: string; action?: string; onAction?: () => void }) { return <View style={styles.sectionRow}><Text style={styles.sectionTitle}>{title}</Text>{action ? <Text onPress={onAction} style={styles.action}>{action}</Text> : null}</View>; }
export const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.canvas, paddingHorizontal: 22, paddingTop: 12 },
  eyebrow: { color: colors.green, fontSize: 10, letterSpacing: 1.8, fontWeight: '800' },
  heading: { color: colors.ink, fontSize: 30, lineHeight: 36, letterSpacing: -1.1, fontWeight: '700' },
  subtitle: { color: colors.muted, fontSize: 14, lineHeight: 21 },
  button: { backgroundColor: colors.green, minHeight: 54, borderRadius: 18, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 20 },
  buttonSecondary: { backgroundColor: colors.mint }, buttonText: { color: '#fff', fontSize: 15, fontWeight: '700' },
  fieldLabel: { color: colors.ink, fontSize: 12, fontWeight: '700' },
  input: { backgroundColor: colors.paper, borderWidth: 1, borderColor: colors.line, borderRadius: 15, minHeight: 52, paddingHorizontal: 15, color: colors.ink, fontSize: 15 },
  pill: { backgroundColor: '#F0F1EB', paddingHorizontal: 13, paddingVertical: 8, borderRadius: 30 }, pillText: { color: colors.muted, fontSize: 11, fontWeight: '700' },
  sectionRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }, sectionTitle: { color: colors.ink, fontSize: 18, fontWeight: '700', letterSpacing: -0.4 }, action: { color: colors.green, fontSize: 12, fontWeight: '700' },
});
