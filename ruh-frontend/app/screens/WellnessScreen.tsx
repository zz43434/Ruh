import React, { FC, useEffect, useState } from "react"
import {
  View,
  ViewStyle,
  TextStyle,
  FlatList,
  RefreshControl,
  Alert,
  TouchableOpacity,
  Modal,
  ScrollView,
} from "react-native"
import { Screen } from "@/components/Screen"
import { Text } from "@/components/Text"
import { Button } from "@/components/Button"
import { AnimatedScreenWrapper } from "@/components/AnimatedScreenWrapper"
import { useAppTheme } from "@/theme/context"
import type { ThemedStyle } from "@/theme/types"
import { api } from "@/services/api"
import { WellnessHistory, WellnessCheckin } from "@/services/api/types"
import { useUser } from "@/contexts/UserContext"

interface WellnessScreenProps {}

interface WellnessEntry {
  id: number
  mood: string
  energy_level: number
  stress_level: number
  notes: string
  timestamp: string
}

export const WellnessScreen: FC<WellnessScreenProps> = function WellnessScreen() {
  const { user } = useUser()
  const { themed, theme } = useAppTheme()
  const [wellnessHistory, setWellnessHistory] = useState<WellnessEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [showCheckinModal, setShowCheckinModal] = useState(false)
  const [checkinData, setCheckinData] = useState({
    mood: "",
    energy_level: 5,
    stress_level: 5,
    notes: "",
  })

  const moods = ["😊 Happy", "😌 Calm", "😐 Neutral", "😔 Sad", "😰 Anxious", "😤 Frustrated"]

  const loadWellnessHistory = async (refresh = false) => {
    if (!user?.id) return
    
    if (refresh) setRefreshing(true)
    else setLoading(true)

    try {
      const response = await api.getWellnessHistory(20, 0, user.id)
      if (response.kind === "ok") {
        setWellnessHistory(response.data.wellness_history)
      } else {
        console.error('Failed to load wellness history:', response.error)
        Alert.alert("Error", "Failed to load wellness history")
      }
    } catch (error) {
      console.error('Error loading wellness history:', error)
      Alert.alert("Error", "Failed to load wellness history")
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const submitCheckin = async () => {
    if (!user?.id) {
      Alert.alert('Error', 'User not found. Please try again.')
      return
    }
    
    if (!checkinData.mood) {
      Alert.alert("Error", "Please select a mood")
      return
    }

    setLoading(true)
    try {
      const checkin: WellnessCheckin = {
        ...checkinData,
        user_id: user.id, // Use actual user ID from context
      }
      
      const response = await api.submitWellnessCheckin(checkin)
      if (response.kind === "ok") {
        Alert.alert("Success", "Wellness check-in submitted successfully!")
        setShowCheckinModal(false)
        setCheckinData({
          mood: "",
          energy_level: 5,
          stress_level: 5,
          notes: "",
        })
        loadWellnessHistory()
      } else {
        Alert.alert("Error", "Failed to submit check-in")
      }
    } catch (error) {
      Alert.alert("Error", "Failed to submit check-in")
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleDateString() + " " + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const getLevelColor = (level: number, type: 'energy' | 'stress') => {
    if (type === 'energy') {
      return level >= 7 ? theme.colors.palette.primary500 : 
             level >= 4 ? theme.colors.palette.accent500 : 
             theme.colors.palette.angry500
    } else {
      return level >= 7 ? theme.colors.palette.angry500 : 
             level >= 4 ? theme.colors.palette.accent500 : 
             theme.colors.palette.primary500
    }
  }

  useEffect(() => {
    if (user?.id) {
      loadWellnessHistory()
    }
  }, [user?.id])

  const renderWellnessEntry = ({ item }: { item: WellnessEntry }) => (
    <View style={themed($entryCard)}>
      <View style={themed($entryHeader)}>
        <Text style={themed($entryMood)}>{item.mood}</Text>
        <Text style={themed($entryDate)}>{formatDate(item.timestamp)}</Text>
      </View>
      
      <View style={themed($levelsContainer)}>
        <View style={themed($levelItem)}>
          <Text style={themed($levelLabel)}>Energy</Text>
          <View style={themed($levelBar)}>
            <View 
              style={[
                themed($levelFill), 
                { 
                  width: `${(item.energy_level / 10) * 100}%`,
                  backgroundColor: getLevelColor(item.energy_level, 'energy')
                }
              ]} 
            />
          </View>
          <Text style={themed($levelValue)}>{item.energy_level}/10</Text>
        </View>
        
        <View style={themed($levelItem)}>
          <Text style={themed($levelLabel)}>Stress</Text>
          <View style={themed($levelBar)}>
            <View 
              style={[
                themed($levelFill), 
                { 
                  width: `${(item.stress_level / 10) * 100}%`,
                  backgroundColor: getLevelColor(item.stress_level, 'stress')
                }
              ]} 
            />
          </View>
          <Text style={themed($levelValue)}>{item.stress_level}/10</Text>
        </View>
      </View>
      
      {item.notes && (
        <Text style={themed($entryNotes)}>{item.notes}</Text>
      )}
    </View>
  )

  const renderCheckinModal = () => (
    <Modal
      visible={showCheckinModal}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={() => setShowCheckinModal(false)}
    >
      <View style={themed($modalContainer)}>
        <View style={themed($modalHeader)}>
          <Text preset="heading" style={themed($modalTitle)}>
            Wellness Check-in
          </Text>
          <TouchableOpacity
            onPress={() => setShowCheckinModal(false)}
            style={themed($closeButton)}
          >
            <Text style={themed($closeButtonText)}>✕</Text>
          </TouchableOpacity>
        </View>
        
        <ScrollView style={themed($modalContent)}>
          <Text style={themed($sectionTitle)}>How are you feeling?</Text>
          <View style={themed($moodsContainer)}>
            {moods.map((mood) => (
              <TouchableOpacity
                key={mood}
                style={[
                  themed($moodButton),
                  checkinData.mood === mood && themed($selectedMoodButton)
                ]}
                onPress={() => setCheckinData({ ...checkinData, mood })}
              >
                <Text style={[
                  themed($moodButtonText),
                  checkinData.mood === mood && themed($selectedMoodButtonText)
                ]}>
                  {mood}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
          
          <Text style={themed($sectionTitle)}>Energy Level: {checkinData.energy_level}/10</Text>
          <View style={themed($sliderContainer)}>
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((level) => (
              <TouchableOpacity
                key={level}
                style={[
                  themed($sliderButton),
                  checkinData.energy_level === level && themed($selectedSliderButton)
                ]}
                onPress={() => setCheckinData({ ...checkinData, energy_level: level })}
              >
                <Text style={[
                  themed($sliderButtonText),
                  checkinData.energy_level === level && themed($selectedSliderButtonText)
                ]}>
                  {level}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
          
          <Text style={themed($sectionTitle)}>Stress Level: {checkinData.stress_level}/10</Text>
          <View style={themed($sliderContainer)}>
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((level) => (
              <TouchableOpacity
                key={level}
                style={[
                  themed($sliderButton),
                  checkinData.stress_level === level && themed($selectedSliderButton)
                ]}
                onPress={() => setCheckinData({ ...checkinData, stress_level: level })}
              >
                <Text style={[
                  themed($sliderButtonText),
                  checkinData.stress_level === level && themed($selectedSliderButtonText)
                ]}>
                  {level}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </ScrollView>
        
        <View style={themed($modalFooter)}>
          <Button
            text="Submit Check-in"
            onPress={submitCheckin}
            style={themed($submitButton)}
            disabled={!checkinData.mood || loading}
          />
        </View>
      </View>
    </Modal>
  )

  return (
    <Screen
      preset="fixed"
      contentContainerStyle={themed($screenContentContainer)}
      safeAreaEdges={["top"]}
    >
      <AnimatedScreenWrapper animationType="slideUp" duration={400}>
        <View style={themed($header)}>
          <Text preset="heading" style={themed($headerTitle)}>
            Wellness
          </Text>
          <Text style={themed($headerSubtitle)}>
            Track your spiritual and emotional well-being
          </Text>
        </View>

        <View style={themed($actionsContainer)}>
          <Button
            text="New Check-in"
            onPress={() => setShowCheckinModal(true)}
            style={themed($checkinButton)}
          />
        </View>

        <FlatList
          data={wellnessHistory}
          renderItem={renderWellnessEntry}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={themed($listContainer)}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={() => loadWellnessHistory(true)} />
          }
          showsVerticalScrollIndicator={false}
          ListEmptyComponent={
            <View style={themed($emptyContainer)}>
              <Text style={themed($emptyText)}>
                {loading ? "Loading wellness history..." : "No wellness entries yet. Start your first check-in!"}
              </Text>
            </View>
          }
        />
      </AnimatedScreenWrapper>

      {renderCheckinModal()}
    </Screen>
  )
}

const $screenContentContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  flex: 1,
  paddingHorizontal: spacing.lg,
})

const $header: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  paddingVertical: spacing.lg,
})

const $headerTitle: ThemedStyle<TextStyle> = ({ spacing }) => ({
  marginBottom: spacing.xs,
})

const $headerSubtitle: ThemedStyle<TextStyle> = ({ colors }) => ({
  color: colors.textDim,
})

const $actionsContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  marginBottom: spacing.lg,
})

const $checkinButton: ThemedStyle<ViewStyle> = ({ colors }) => ({
  backgroundColor: colors.palette.primary500,
})

const $listContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  paddingBottom: spacing.lg,
})

const $entryCard: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  backgroundColor: colors.palette.neutral100,
  borderRadius: 12,
  padding: spacing.md,
  marginBottom: spacing.sm,
  borderWidth: 1,
  borderColor: colors.palette.neutral300,
})

const $entryHeader: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  flexDirection: "row",
  justifyContent: "space-between",
  alignItems: "center",
  marginBottom: spacing.sm,
})

const $entryMood: ThemedStyle<TextStyle> = ({ colors }) => ({
  fontSize: 18,
  fontWeight: "600",
  color: colors.text,
})

const $entryDate: ThemedStyle<TextStyle> = ({ colors }) => ({
  fontSize: 12,
  color: colors.textDim,
})

const $levelsContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  marginBottom: spacing.sm,
})

const $levelItem: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  flexDirection: "row",
  alignItems: "center",
  marginBottom: spacing.xs,
})

const $levelLabel: ThemedStyle<TextStyle> = ({ colors }) => ({
  fontSize: 14,
  fontWeight: "500",
  color: colors.text,
  width: 60,
})

const $levelBar: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  flex: 1,
  height: 8,
  backgroundColor: colors.palette.neutral300,
  borderRadius: 4,
  marginHorizontal: spacing.sm,
  overflow: "hidden",
})

const $levelFill: ThemedStyle<ViewStyle> = () => ({
  height: "100%",
  borderRadius: 4,
})

const $levelValue: ThemedStyle<TextStyle> = ({ colors }) => ({
  fontSize: 12,
  color: colors.textDim,
  width: 30,
  textAlign: "right",
})

const $entryNotes: ThemedStyle<TextStyle> = ({ colors, spacing }) => ({
  fontSize: 14,
  color: colors.textDim,
  fontStyle: "italic",
  marginTop: spacing.xs,
})

const $emptyContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  flex: 1,
  justifyContent: "center",
  alignItems: "center",
  paddingVertical: spacing.xxl,
})

const $emptyText: ThemedStyle<TextStyle> = ({ colors }) => ({
  color: colors.textDim,
  textAlign: "center",
})

const $modalContainer: ThemedStyle<ViewStyle> = ({ colors }) => ({
  flex: 1,
  backgroundColor: colors.background,
})

const $modalHeader: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  flexDirection: "row",
  justifyContent: "space-between",
  alignItems: "center",
  padding: spacing.lg,
  borderBottomWidth: 1,
  borderBottomColor: colors.palette.neutral300,
})

const $modalTitle: ThemedStyle<TextStyle> = () => ({})

const $closeButton: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  padding: spacing.xs,
})

const $closeButtonText: ThemedStyle<TextStyle> = ({ colors }) => ({
  fontSize: 18,
  color: colors.textDim,
})

const $modalContent: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  flex: 1,
  padding: spacing.lg,
})

const $sectionTitle: ThemedStyle<TextStyle> = ({ colors, spacing }) => ({
  fontSize: 16,
  fontWeight: "600",
  color: colors.text,
  marginBottom: spacing.sm,
  marginTop: spacing.md,
})

const $moodsContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  flexDirection: "row",
  flexWrap: "wrap",
  gap: spacing.sm,
  marginBottom: spacing.lg,
})

const $moodButton: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  backgroundColor: colors.palette.neutral200,
  borderRadius: 20,
  paddingHorizontal: spacing.md,
  paddingVertical: spacing.sm,
  borderWidth: 1,
  borderColor: colors.palette.neutral300,
})

const $selectedMoodButton: ThemedStyle<ViewStyle> = ({ colors }) => ({
  backgroundColor: colors.palette.primary500,
  borderColor: colors.palette.primary500,
})

const $moodButtonText: ThemedStyle<TextStyle> = ({ colors }) => ({
  fontSize: 14,
  color: colors.text,
})

const $selectedMoodButtonText: ThemedStyle<TextStyle> = ({ colors }) => ({
  color: colors.palette.neutral100,
})

const $sliderContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  flexDirection: "row",
  justifyContent: "space-between",
  marginBottom: spacing.lg,
})

const $sliderButton: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  width: 30,
  height: 30,
  borderRadius: 15,
  backgroundColor: colors.palette.neutral200,
  justifyContent: "center",
  alignItems: "center",
  borderWidth: 1,
  borderColor: colors.palette.neutral300,
})

const $selectedSliderButton: ThemedStyle<ViewStyle> = ({ colors }) => ({
  backgroundColor: colors.palette.primary500,
  borderColor: colors.palette.primary500,
})

const $sliderButtonText: ThemedStyle<TextStyle> = ({ colors }) => ({
  fontSize: 12,
  color: colors.text,
})

const $selectedSliderButtonText: ThemedStyle<TextStyle> = ({ colors }) => ({
  color: colors.palette.neutral100,
})

const $modalFooter: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  padding: spacing.lg,
  borderTopWidth: 1,
  borderTopColor: colors.palette.neutral300,
})

const $submitButton: ThemedStyle<ViewStyle> = ({ colors }) => ({
  backgroundColor: colors.palette.primary500,
})