import React, { FC, useEffect, useState } from "react"
import {
  View,
  ViewStyle,
  TextStyle,
  FlatList,
  RefreshControl,
  Alert,
  TouchableOpacity,
} from "react-native"
import { Screen } from "@/components/Screen"
import { Text } from "@/components/Text"
import { Button } from "@/components/Button"
import { useAppTheme } from "@/theme/context"
import type { ThemedStyle } from "@/theme/types"
import { useNavigation, useRoute } from "@react-navigation/native"
import type { NativeStackNavigationProp, NativeStackScreenProps } from "@react-navigation/native-stack"
import type { AppStackParamList } from "@/navigators/AppNavigator"
import { api } from "@/services/api"
import { ChapterDetails, Verse } from "@/services/api/types"
import { translationStorage } from "@/services/translationStorage"

interface ChapterDetailsScreenProps {}

type ChapterDetailsScreenRouteProp = NativeStackScreenProps<AppStackParamList, "ChapterDetails">

export const ChapterDetailsScreen: FC<ChapterDetailsScreenProps> = function ChapterDetailsScreen() {
  const { themed, theme } = useAppTheme()
  const navigation = useNavigation<NativeStackNavigationProp<AppStackParamList>>()
  const route = useRoute<ChapterDetailsScreenRouteProp["route"]>()
  
  const { surahNumber } = route.params
  
  const [chapterDetails, setChapterDetails] = useState<ChapterDetails | null>(null)
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [translatingVerses, setTranslatingVerses] = useState<Set<number>>(new Set())
  const [translations, setTranslations] = useState<Map<number, string>>(new Map())
  const [isTranslatingAll, setIsTranslatingAll] = useState(false)

  const loadChapterDetails = async (refresh = false) => {
    if (refresh) setRefreshing(true)
    else setLoading(true)

    try {
      const response = await api.getChapterDetails(surahNumber)
      if (response.kind === "ok") {
        setChapterDetails(response.chapter)
        
        // Load existing translations for this chapter
        const existingTranslations = await translationStorage.getChapterTranslations(surahNumber)
        setTranslations(existingTranslations)
      } else {
        Alert.alert("Error", "Failed to load chapter details")
      }
    } catch (error) {
      Alert.alert("Error", "Failed to load chapter details")
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const handleTranslateAll = async () => {
    if (!chapterDetails?.verses || isTranslatingAll) return

    setIsTranslatingAll(true)
    
    try {
      const versesToTranslate = chapterDetails.verses.filter((_, index) => !translations.has(index))
      
      for (let i = 0; i < versesToTranslate.length; i++) {
        const verse = versesToTranslate[i]
        const originalIndex = chapterDetails.verses.findIndex(v => v === verse)
        
        try {
          const response = await api.translateVerse(verse.arabic_text || verse.text || "")
          if (response.kind === "ok") {
            setTranslations(prev => new Map(prev).set(originalIndex, response.translation))
            // Save translation to persistent storage
            await translationStorage.saveTranslation(surahNumber, originalIndex, response.translation)
          }
        } catch (error) {
          console.error(`Failed to translate verse ${originalIndex + 1}:`, error)
        }
      }
    } catch (error) {
      Alert.alert("Error", "Failed to translate all verses")
    } finally {
      setIsTranslatingAll(false)
    }
  }

  useEffect(() => {
    loadChapterDetails()
  }, [surahNumber])

  const handleVersePress = (verse: Verse) => {
    // Remove navigation to verse details as requested
    // navigation.navigate("VerseDetails", { verse })
  }

  const handleTranslateVerse = async (verse: Verse, verseIndex: number) => {
    // Check if translation already exists
    if (translations.has(verseIndex)) {
      return
    }

    // Set loading state for this verse
    setTranslatingVerses(prev => new Set(prev).add(verseIndex))

    try {
      const response = await api.translateVerse(verse.arabic_text || verse.text || "")
      if (response.kind === "ok") {
        setTranslations(prev => new Map(prev).set(verseIndex, response.translation))
        // Save translation to persistent storage
        await translationStorage.saveTranslation(surahNumber, verseIndex, response.translation)
      } else {
        Alert.alert("Error", "Failed to translate verse")
      }
    } catch (error) {
      Alert.alert("Error", "Failed to translate verse")
    } finally {
      setTranslatingVerses(prev => {
        const newSet = new Set(prev)
        newSet.delete(verseIndex)
        return newSet
      })
    }
  }

  const renderVerse = ({ item, index }: { item: Verse; index: number }) => {
    const isTranslating = translatingVerses.has(index)
    const translation = translations.get(index)
    
    return (
      <View style={themed($verseCard)}>
        <View style={themed($verseHeader)}>
          <Text style={themed($verseNumber)}>
            {index + 1}
          </Text>
          <TouchableOpacity
            onPress={() => handleTranslateVerse(item, index)}
            style={themed(isTranslating ? $translateButtonLoading : translation ? $translateButtonTranslated : $translateButton)}
            disabled={isTranslating}
          >
            <Text style={themed(isTranslating ? $translateButtonTextLoading : translation ? $translateButtonTextTranslated : $translateButtonText)}>
              {isTranslating ? "Translating..." : translation ? "✓ Translated" : "Translate"}
            </Text>
          </TouchableOpacity>
        </View>
        
        <View style={themed($verseContent)}>
          <Text style={themed($verseText)}>{item.text || item.arabic_text}</Text>
          {translation && (
            <View style={themed($translationContainer)}>
              <Text style={themed($translationLabel)}>Translation:</Text>
              <Text style={themed($verseTranslation)}>{translation}</Text>
            </View>
          )}
        </View>
      </View>
    )
  }

  if (loading && !chapterDetails) {
    return (
      <Screen preset="scroll" safeAreaEdges={["top"]} contentContainerStyle={themed($screenContentContainer)}>
        <View style={themed($loadingContainer)}>
          <Text style={themed($loadingText)}>Loading chapter...</Text>
        </View>
      </Screen>
    )
  }

  if (!chapterDetails) {
    return (
      <Screen preset="scroll" safeAreaEdges={["top"]} contentContainerStyle={themed($screenContentContainer)}>
        <View style={themed($errorContainer)}>
          <Text style={themed($errorText)}>Chapter not found</Text>
          <Button
            text="Go Back"
            onPress={() => navigation.goBack()}
            style={themed($backButton)}
          />
        </View>
      </Screen>
    )
  }

  return (
    <Screen preset="fixed" safeAreaEdges={["top"]} contentContainerStyle={themed($screenContentContainer)}>
      {/* Chapter Header */}
      <View style={themed($header)}>
        {/* Back Button */}
        <View style={themed($headerTop)}>
          <TouchableOpacity
            style={themed($headerBackButton)}
            onPress={() => navigation.goBack()}
          >
            <Text style={themed($headerBackButtonText)}>← Back</Text>
          </TouchableOpacity>
        </View>
        
        <Text preset="heading" style={themed($chapterTitle)}>
          {chapterDetails.name}
        </Text>
        <Text style={themed($chapterMeta)}>
          Chapter {chapterDetails.surah_number} • {chapterDetails.ayah_count} verses • {chapterDetails.revelation_place}
        </Text>
        
        {/* Chapter Summary */}
        {chapterDetails.summary && (
          <View style={themed($summaryContainer)}>
            <Text style={themed($summaryTitle)}>Summary</Text>
            <Text style={themed($summaryText)}>{chapterDetails.summary}</Text>
          </View>
        )}
        
        {/* Translate All Button */}
        <View style={themed($translateAllContainer)}>
          <TouchableOpacity
            style={themed(isTranslatingAll ? $translateAllButtonLoading : $translateAllButton)}
            onPress={handleTranslateAll}
            disabled={isTranslatingAll}
          >
            <Text style={themed(isTranslatingAll ? $translateAllButtonTextLoading : $translateAllButtonText)}>
              {isTranslatingAll ? "Translating..." : "Translate All"}
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Verses List */}
      <FlatList
        data={chapterDetails.verses}
        renderItem={renderVerse}
        keyExtractor={(item, index) => `verse-${index}`}
        contentContainerStyle={themed($listContainer)}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={() => loadChapterDetails(true)} />
        }
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={
          <View style={themed($emptyContainer)}>
            <Text style={themed($emptyText)}>
              No verses found for this chapter
            </Text>
          </View>
        }
      />
    </Screen>
  )
}

// Styles
const $screenContentContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  flex: 1,
  paddingHorizontal: spacing.lg,
})

const $header: ThemedStyle<ViewStyle> = ({ spacing, colors }) => ({
  paddingVertical: spacing.lg,
  borderBottomWidth: 1,
  borderBottomColor: colors.palette.neutral300,
  marginBottom: spacing.lg,
  backgroundColor: colors.palette.neutral100,
  borderRadius: 12,
  paddingHorizontal: spacing.md,
})

const $chapterTitle: ThemedStyle<TextStyle> = ({ spacing, colors }) => ({
  marginBottom: spacing.xs,
  color: colors.palette.primary600,
  fontSize: 24,
  fontWeight: "700",
})

const $chapterMeta: ThemedStyle<TextStyle> = ({ colors, spacing }) => ({
  color: colors.textDim,
  fontSize: 16,
  marginBottom: spacing.md,
  fontWeight: "500",
})

const $summaryContainer: ThemedStyle<ViewStyle> = ({ spacing, colors }) => ({
  marginTop: spacing.sm,
  backgroundColor: colors.palette.primary100,
  borderRadius: 12,
  padding: spacing.md,
})

const $summaryTitle: ThemedStyle<TextStyle> = ({ colors, spacing }) => ({
  fontSize: 18,
  fontWeight: "700",
  color: colors.palette.primary600,
  marginBottom: spacing.sm,
})

const $summaryText: ThemedStyle<TextStyle> = ({ colors }) => ({
  fontSize: 16,
  lineHeight: 24,
  color: colors.text,
  fontStyle: "italic",
})

const $listContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  paddingBottom: spacing.lg,
})

const $verseCard: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  backgroundColor: colors.palette.neutral100,
  borderRadius: 16,
  padding: spacing.lg,
  marginBottom: spacing.md,
  borderWidth: 1,
  borderColor: colors.palette.neutral200,
  shadowColor: colors.palette.neutral900,
  shadowOffset: { width: 0, height: 2 },
  shadowOpacity: 0.1,
  shadowRadius: 4,
  elevation: 3,
})

const $verseHeader: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  flexDirection: "row",
  justifyContent: "space-between",
  alignItems: "center",
  marginBottom: spacing.md,
  paddingBottom: spacing.sm,
  borderBottomWidth: 1,
  borderBottomColor: "#E8E8E8",
})

const $verseNumber: ThemedStyle<TextStyle> = ({ colors }) => ({
  fontSize: 18,
  fontWeight: "700",
  color: colors.palette.primary600,
  backgroundColor: colors.palette.primary100,
  paddingHorizontal: 12,
  paddingVertical: 6,
  borderRadius: 20,
  minWidth: 36,
  textAlign: "center",
})

const $verseContent: ThemedStyle<ViewStyle> = () => ({
  flex: 1,
})

const $verseText: ThemedStyle<TextStyle> = ({ colors, spacing }) => ({
  fontSize: 18,
  lineHeight: 28,
  color: colors.text,
  textAlign: "right",
  fontFamily: "System",
  marginBottom: spacing.sm,
})

const $translateButton: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  backgroundColor: colors.palette.primary500,
  paddingHorizontal: spacing.md,
  paddingVertical: spacing.sm,
  borderRadius: 12,
  minWidth: 100,
  alignItems: "center",
  shadowColor: colors.palette.primary500,
  shadowOffset: { width: 0, height: 2 },
  shadowOpacity: 0.3,
  shadowRadius: 4,
  elevation: 3,
})

const $translateButtonLoading: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  backgroundColor: colors.palette.neutral400,
  paddingHorizontal: spacing.md,
  paddingVertical: spacing.sm,
  borderRadius: 12,
  minWidth: 100,
  alignItems: "center",
  opacity: 0.7,
})

const $translateButtonTranslated: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  backgroundColor: colors.palette.primary600,
  paddingHorizontal: spacing.md,
  paddingVertical: spacing.sm,
  borderRadius: 12,
  minWidth: 100,
  alignItems: "center",
  borderWidth: 2,
  borderColor: colors.palette.primary400,
})

const $translateButtonText: ThemedStyle<TextStyle> = ({ colors }) => ({
  color: colors.palette.neutral100,
  fontSize: 14,
  fontWeight: "600",
  textAlign: "center",
})

const $translateButtonTextLoading: ThemedStyle<TextStyle> = ({ colors }) => ({
  color: colors.palette.neutral100,
  fontSize: 14,
  fontWeight: "600",
  textAlign: "center",
  opacity: 0.8,
})

const $translateButtonTextTranslated: ThemedStyle<TextStyle> = ({ colors }) => ({
  color: colors.palette.neutral100,
  fontSize: 14,
  fontWeight: "700",
  textAlign: "center",
})

const $translationContainer: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  backgroundColor: colors.palette.neutral100,
  borderRadius: 12,
  padding: spacing.md,
  marginTop: spacing.md,
  borderLeftWidth: 4,
  borderLeftColor: colors.palette.primary400,
})

const $translationLabel: ThemedStyle<TextStyle> = ({ colors, spacing }) => ({
  fontSize: 12,
  fontWeight: "600",
  color: colors.palette.primary600,
  textTransform: "uppercase",
  letterSpacing: 0.5,
  marginBottom: spacing.xs,
})

const $verseTranslation: ThemedStyle<TextStyle> = ({ colors }) => ({
  fontSize: 16,
  lineHeight: 24,
  color: colors.textDim,
  fontStyle: "italic",
})

const $loadingContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  flex: 1,
  justifyContent: "center",
  alignItems: "center",
  paddingVertical: spacing.xxl,
})

const $loadingText: ThemedStyle<TextStyle> = ({ colors }) => ({
  color: colors.textDim,
})

const $errorContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  flex: 1,
  justifyContent: "center",
  alignItems: "center",
  paddingVertical: spacing.xxl,
})

const $errorText: ThemedStyle<TextStyle> = ({ colors, spacing }) => ({
  color: colors.textDim,
  marginBottom: spacing.md,
})

const $backButton: ThemedStyle<ViewStyle> = () => ({
  minWidth: 120,
})

const $emptyContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  flex: 1,
  justifyContent: "center",
  alignItems: "center",
  paddingVertical: spacing.xxl,
})

const $emptyText: ThemedStyle<TextStyle> = ({ colors }) => ({
  color: colors.textDim,
})

const $translateAllContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  marginTop: spacing.md,
  alignItems: "center",
})

const $translateAllButton: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  backgroundColor: colors.palette.primary500,
  paddingHorizontal: spacing.lg,
  paddingVertical: spacing.md,
  borderRadius: 16,
  minWidth: 150,
  alignItems: "center",
  shadowColor: colors.palette.primary500,
  shadowOffset: { width: 0, height: 3 },
  shadowOpacity: 0.4,
  shadowRadius: 6,
  elevation: 5,
})

const $translateAllButtonLoading: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  backgroundColor: colors.palette.neutral400,
  paddingHorizontal: spacing.lg,
  paddingVertical: spacing.md,
  borderRadius: 16,
  minWidth: 150,
  alignItems: "center",
  opacity: 0.7,
})

const $translateAllButtonText: ThemedStyle<TextStyle> = ({ colors }) => ({
  color: colors.palette.neutral100,
  fontSize: 16,
  fontWeight: "700",
  textAlign: "center",
})

const $translateAllButtonTextLoading: ThemedStyle<TextStyle> = ({ colors }) => ({
  color: colors.palette.neutral100,
  fontSize: 16,
  fontWeight: "700",
  textAlign: "center",
  opacity: 0.8,
})

const $headerTop: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  marginBottom: spacing.md,
})

const $headerBackButton: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  backgroundColor: colors.palette.neutral200,
  paddingHorizontal: spacing.md,
  paddingVertical: spacing.sm,
  borderRadius: 8,
  alignSelf: "flex-start",
})

const $headerBackButtonText: ThemedStyle<TextStyle> = ({ colors }) => ({
  color: colors.palette.primary600,
  fontSize: 16,
  fontWeight: "600",
})