import React, { FC, useState, useEffect } from "react"
import {
  View,
  ViewStyle,
  TextStyle,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from "react-native"
import { Text } from "@/components/Text"
import { Button } from "@/components/Button"
import { useAppTheme } from "@/theme/context"
import type { ThemedStyle } from "@/theme/types"
import { api } from "@/services/api"
import { WellnessAnalysisResult, WellnessVerse } from "@/services/api/types"
import { useUser } from "@/contexts/UserContext"

interface WellnessAnalysisProps {
  onAnalysisComplete?: (result: WellnessAnalysisResult) => void
}

export const WellnessAnalysis: FC<WellnessAnalysisProps> = function WellnessAnalysis({
  onAnalysisComplete,
}) {
  const { themed, theme } = useAppTheme()
  const { user } = useUser()
  const [analysisResult, setAnalysisResult] = useState<WellnessAnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchAnalysis = async () => {
    if (!user?.id) {
      setError("User not found. Please try again.")
      return
    }

    setLoading(true)
    setError(null)
    
    try {
      const response = await api.getAIWellnessAnalysis(user.id, 3)
      if (response.kind === "ok") {
        // Handle both nested analysis object and direct data structure
        const result = response.data.analysis || response.data
        setAnalysisResult(result)
        onAnalysisComplete?.(result)
      } else {
        console.error('Failed to get AI wellness analysis:', response.error)
        setError(response.error?.message || "Failed to get analysis. Please try again.")
      }
    } catch (error) {
      console.error('Error getting AI wellness analysis:', error)
      setError("Failed to get analysis. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    // Automatically fetch analysis when component mounts
    fetchAnalysis()
  }, [user?.id])

  const renderVerse = (verse: WellnessVerse, index: number) => (
    <View key={`${verse.id}-${index}`} style={themed($verseCard)}>
      <View style={themed($verseHeader)}>
        <Text style={themed($verseReference)}>
          {verse.surah_name} {verse.surah_number}:{verse.verse_number}
        </Text>
        <Text style={themed($similarityScore)}>
          {Math.round(verse.similarity_score * 100)}% match
        </Text>
      </View>
      
      <Text style={themed($arabicText)}>{verse.arabic_text}</Text>
      <Text style={themed($translationText)}>{verse.translation}</Text>
      
      {verse.context && (
        <Text style={themed($contextText)}>{verse.context}</Text>
      )}
    </View>
  )

  const renderAnalysisResult = () => {
    if (!analysisResult) return null

    return (
      <ScrollView style={themed($resultsContainer)} showsVerticalScrollIndicator={false}>
        {/* Islamic Themes */}
        {(analysisResult.themes || analysisResult.detected_categories) && 
         (analysisResult.themes?.length > 0 || analysisResult.detected_categories?.length > 0) && (
          <View style={themed($section)}>
            <Text style={themed($sectionTitle)}>Islamic Themes</Text>
            <View style={themed($categoriesContainer)}>
              {(analysisResult.themes || analysisResult.detected_categories)?.map((theme, index) => (
                <View key={index} style={themed($categoryTag)}>
                  <Text style={themed($categoryText)}>{theme}</Text>
                </View>
              ))}
            </View>
          </View>
        )}

        {/* Analysis */}
        {analysisResult.guidance && (
          <View style={themed($section)}>
            <Text style={themed($sectionTitle)}>Spiritual Guidance</Text>
            <Text style={themed($guidanceText)}>{analysisResult.guidance}</Text>
          </View>
        )}

        {/* Relevant Verses */}
        {analysisResult.verses && analysisResult.verses.length > 0 && (
          <View style={themed($section)}>
            <Text style={themed($sectionTitle)}>Relevant Quranic Verses</Text>
            {analysisResult.verses.map((verse, index) => renderVerse(verse, index))}
          </View>
        )}

        {/* Recommendations */}
        {analysisResult.recommendations && analysisResult.recommendations.length > 0 && (
          <View style={themed($section)}>
            <Text style={themed($sectionTitle)}>Recommendations</Text>
            {analysisResult.recommendations.map((recommendation, index) => (
              <View key={index} style={themed($recommendationItem)}>
                <Text style={themed($recommendationText)}>• {recommendation}</Text>
              </View>
            ))}
          </View>
        )}
        
        {/* Spiritual Guidance */}
        {/* Removed duplicate spiritual guidance section */}
      </ScrollView>
    )
  }

  return (
    <View style={themed($container)}>
      {loading && (
        <View style={themed($loadingContainer)}>
          <ActivityIndicator size="large" color={theme.colors.palette.primary500} />
          <Text style={themed($loadingText)}>Generating your wellness analysis...</Text>
        </View>
      )}
      
      {error ? (
        <View style={themed($errorContainer)}>
          <Text style={themed($errorText)}>{error}</Text>
          <Button
            text="Try Again"
            style={themed($retryButton)}
            onPress={fetchAnalysis}
          />
        </View>
      ) : (
        renderAnalysisResult()
      )}
    </View>
  )
}

const $container: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  flex: 1,
  padding: spacing.md,
})

const $loadingContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  alignItems: "center",
  paddingVertical: spacing.lg,
})

const $loadingText: ThemedStyle<TextStyle> = ({ colors }) => ({
  color: colors.textDim,
  fontStyle: "italic",
})

const $resultsContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  flex: 1,
  marginTop: spacing.md,
})

const $section: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  marginBottom: spacing.lg,
})

const $sectionTitle: ThemedStyle<TextStyle> = ({ colors, spacing }) => ({
  fontSize: 18,
  fontWeight: "700",
  color: colors.text,
  marginBottom: spacing.md,
})

const $categoriesContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  flexDirection: "row",
  flexWrap: "wrap",
  gap: spacing.sm,
})

const $categoryTag: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  backgroundColor: colors.palette.primary100,
  borderRadius: 16,
  paddingHorizontal: spacing.sm,
  paddingVertical: spacing.xs,
})

const $categoryText: ThemedStyle<TextStyle> = ({ colors }) => ({
  fontSize: 12,
  fontWeight: "600",
  color: colors.palette.primary600,
})

const $guidanceText: ThemedStyle<TextStyle> = ({ colors, spacing }) => ({
  fontSize: 16,
  lineHeight: 24,
  color: colors.text,
  marginBottom: spacing.sm,
})

const $verseCard: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  backgroundColor: colors.palette.neutral100,
  borderRadius: 12,
  padding: spacing.md,
  marginBottom: spacing.sm,
  borderWidth: 1,
  borderColor: colors.palette.neutral300,
})

const $verseHeader: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  flexDirection: "row",
  justifyContent: "space-between",
  alignItems: "center",
  marginBottom: spacing.sm,
})

const $verseReference: ThemedStyle<TextStyle> = ({ colors }) => ({
  fontSize: 14,
  fontWeight: "600",
  color: colors.palette.primary600,
})

const $similarityScore: ThemedStyle<TextStyle> = ({ colors }) => ({
  fontSize: 12,
  color: colors.textDim,
  backgroundColor: colors.palette.accent100,
  paddingHorizontal: 8,
  paddingVertical: 2,
  borderRadius: 10,
})

const $arabicText: ThemedStyle<TextStyle> = ({ colors, spacing }) => ({
  fontSize: 18,
  lineHeight: 28,
  color: colors.text,
  textAlign: "right",
  marginBottom: spacing.sm,
  fontFamily: "System", // You might want to use a specific Arabic font
})

const $translationText: ThemedStyle<TextStyle> = ({ colors, spacing }) => ({
  fontSize: 16,
  lineHeight: 24,
  color: colors.text,
  marginBottom: spacing.sm,
})

const $contextText: ThemedStyle<TextStyle> = ({ colors }) => ({
  fontSize: 14,
  fontStyle: "italic",
  color: colors.textDim,
})

const $recommendationItem: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  flexDirection: "row",
  alignItems: "flex-start",
  marginBottom: spacing.sm,
})

const $recommendationBullet: ThemedStyle<TextStyle> = ({ colors, spacing }) => ({
  fontSize: 16,
  color: colors.palette.primary500,
  marginRight: spacing.sm,
  marginTop: 2,
})

const $recommendationText: ThemedStyle<TextStyle> = ({ colors }) => ({
  flex: 1,
  fontSize: 16,
  lineHeight: 24,
  color: colors.text,
})