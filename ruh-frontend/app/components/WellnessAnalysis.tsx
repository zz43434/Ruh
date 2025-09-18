import React, { FC, useState } from "react"
import {
  View,
  ViewStyle,
  TextStyle,
  TextInput,
  ScrollView,
  TouchableOpacity,
  Alert,
} from "react-native"
import { Text } from "@/components/Text"
import { Button } from "@/components/Button"
import { useAppTheme } from "@/theme/context"
import type { ThemedStyle } from "@/theme/types"
import { api } from "@/services/api"
import { WellnessAnalysisResult, WellnessVerse } from "@/services/api/types"

interface WellnessAnalysisProps {
  onAnalysisComplete?: (result: WellnessAnalysisResult) => void
}

export const WellnessAnalysis: FC<WellnessAnalysisProps> = function WellnessAnalysis({
  onAnalysisComplete,
}) {
  const { themed, theme } = useAppTheme()
  const [userInput, setUserInput] = useState("")
  const [analysisResult, setAnalysisResult] = useState<WellnessAnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)

  const handleAnalyze = async () => {
    if (!userInput.trim()) {
      Alert.alert("Input Required", "Please describe how you're feeling or what you're going through.")
      return
    }

    setLoading(true)
    try {
      const response = await api.analyzeWellness({ user_input: userInput.trim() })
      if (response.kind === "ok") {
        setAnalysisResult(response.data)
        onAnalysisComplete?.(response.data)
      } else {
        console.error('Failed to analyze wellness:', response.error)
        Alert.alert("Error", "Failed to analyze your input. Please try again.")
      }
    } catch (error) {
      console.error('Error analyzing wellness:', error)
      Alert.alert("Error", "Failed to analyze your input. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const handleClear = () => {
    setUserInput("")
    setAnalysisResult(null)
  }

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
        {/* Detected Categories */}
        {analysisResult.detected_categories.length > 0 && (
          <View style={themed($section)}>
            <Text style={themed($sectionTitle)}>Detected Areas of Concern</Text>
            <View style={themed($categoriesContainer)}>
              {analysisResult.detected_categories.map((category, index) => (
                <View key={index} style={themed($categoryTag)}>
                  <Text style={themed($categoryText)}>{category}</Text>
                </View>
              ))}
            </View>
          </View>
        )}

        {/* Guidance */}
        {analysisResult.guidance && (
          <View style={themed($section)}>
            <Text style={themed($sectionTitle)}>Spiritual Guidance</Text>
            <Text style={themed($guidanceText)}>{analysisResult.guidance}</Text>
          </View>
        )}

        {/* Relevant Verses */}
        {analysisResult.verses.length > 0 && (
          <View style={themed($section)}>
            <Text style={themed($sectionTitle)}>Relevant Verses</Text>
            {analysisResult.verses.map((verse, index) => renderVerse(verse, index))}
          </View>
        )}

        {/* Recommendations */}
        {analysisResult.recommendations.length > 0 && (
          <View style={themed($section)}>
            <Text style={themed($sectionTitle)}>Recommendations</Text>
            {analysisResult.recommendations.map((recommendation, index) => (
              <View key={index} style={themed($recommendationItem)}>
                <Text style={themed($recommendationBullet)}>•</Text>
                <Text style={themed($recommendationText)}>{recommendation}</Text>
              </View>
            ))}
          </View>
        )}
      </ScrollView>
    )
  }

  return (
    <View style={themed($container)}>
      <View style={themed($inputSection)}>
        <Text style={themed($inputLabel)}>
          How are you feeling? What's on your mind?
        </Text>
        <TextInput
          style={themed($textInput)}
          value={userInput}
          onChangeText={setUserInput}
          placeholder="Describe your thoughts, feelings, or situation..."
          placeholderTextColor={theme.colors.textDim}
          multiline
          numberOfLines={4}
          textAlignVertical="top"
        />
        
        <View style={themed($buttonContainer)}>
          <Button
            text="Analyze"
            onPress={handleAnalyze}
            style={themed($analyzeButton)}
            disabled={loading || !userInput.trim()}
          />
          {(userInput || analysisResult) && (
            <Button
              text="Clear"
              onPress={handleClear}
              style={themed($clearButton)}
              textStyle={themed($clearButtonText)}
            />
          )}
        </View>
      </View>

      {loading && (
        <View style={themed($loadingContainer)}>
          <Text style={themed($loadingText)}>Analyzing your input...</Text>
        </View>
      )}

      {renderAnalysisResult()}
    </View>
  )
}

const $container: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  flex: 1,
  padding: spacing.md,
})

const $inputSection: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  marginBottom: spacing.lg,
})

const $inputLabel: ThemedStyle<TextStyle> = ({ colors, spacing }) => ({
  fontSize: 16,
  fontWeight: "600",
  color: colors.text,
  marginBottom: spacing.sm,
})

const $textInput: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  backgroundColor: colors.palette.neutral100,
  borderRadius: 12,
  padding: spacing.md,
  fontSize: 16,
  color: colors.text,
  borderWidth: 1,
  borderColor: colors.palette.neutral300,
  minHeight: 100,
  marginBottom: spacing.md,
})

const $buttonContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  flexDirection: "row",
  gap: spacing.sm,
})

const $analyzeButton: ThemedStyle<ViewStyle> = ({ colors }) => ({
  flex: 1,
  backgroundColor: colors.palette.primary500,
})

const $clearButton: ThemedStyle<ViewStyle> = ({ colors }) => ({
  backgroundColor: colors.palette.neutral300,
  paddingHorizontal: 20,
})

const $clearButtonText: ThemedStyle<TextStyle> = ({ colors }) => ({
  color: colors.text,
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