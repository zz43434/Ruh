import React, { FC } from "react"
import {
  View,
  ViewStyle,
  TextStyle,
  ScrollView,
  TouchableOpacity,
  Share,
  Alert,
} from "react-native"
import { Screen } from "@/components/Screen"
import { Text } from "@/components/Text"
import { Button } from "@/components/Button"
import { useAppTheme } from "@/theme/context"
import type { ThemedStyle } from "@/theme/types"
import type { AppStackScreenProps } from "@/navigators/AppNavigator"
import type { Verse } from "@/services/api/types"

interface VerseDetailsScreenProps extends AppStackScreenProps<"VerseDetails"> {}

export const VerseDetailsScreen: FC<VerseDetailsScreenProps> = function VerseDetailsScreen({
  navigation,
  route,
}) {
  const { themed, theme } = useAppTheme()
  const verse: Verse = route.params?.verse

  // Debug logging
  console.log("VerseDetailsScreen - route.params:", route.params)
  console.log("VerseDetailsScreen - verse:", verse)

  if (!verse) {
    return (
      <Screen preset="fixed" contentContainerStyle={themed($screenContentContainer)}>
        <Text>Verse not found</Text>
      </Screen>
    )
  }

  const handleShare = async () => {
    try {
      const shareText = `Chapter ${verse.chapter || verse.surah_number}, Verse ${verse.verse || verse.verse_number}\n\n${verse.text || verse.arabic_text}\n\nTranslation: ${verse.translation}`
      
      await Share.share({
        message: shareText,
        title: `Verse ${verse.chapter || verse.surah_number}:${verse.verse || verse.verse_number}`,
      })
    } catch (error) {
      Alert.alert("Error", "Failed to share verse")
    }
  }

  const handleGoBack = () => {
    navigation.goBack()
  }

  return (
    <Screen
      preset="fixed"
      contentContainerStyle={themed($screenContentContainer)}
      safeAreaEdges={["top"]}
    >
      {/* Header */}
      <View style={themed($header)}>
        <TouchableOpacity onPress={handleGoBack} style={themed($backButton)}>
          <Text style={themed($backButtonText)}>← Back</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={handleShare} style={themed($shareButton)}>
          <Text style={themed($shareButtonText)}>Share</Text>
        </TouchableOpacity>
      </View>

      <ScrollView
        style={themed($scrollContainer)}
        contentContainerStyle={themed($scrollContent)}
        showsVerticalScrollIndicator={false}
      >
        {/* Verse Reference */}
        <View style={themed($referenceContainer)}>
          <Text preset="heading" style={themed($referenceText)}>
            Chapter {verse.chapter || verse.surah_number}, Verse {verse.verse || verse.verse_number}
          </Text>
        </View>

        {/* Arabic Text */}
        <View style={themed($verseContainer)}>
          <Text style={themed($arabicText)}>{verse.text || verse.arabic_text}</Text>
        </View>

        {/* Translation */}
        <View style={themed($translationContainer)}>
          <Text style={themed($translationLabel)}>Translation:</Text>
          <Text style={themed($translationText)}>{verse.translation}</Text>
        </View>

        {/* Action Buttons */}
        <View style={themed($actionContainer)}>
          <Button
            text="Share Verse"
            onPress={handleShare}
            style={themed($shareActionButton)}
            textStyle={themed($shareActionButtonText)}
          />
        </View>
      </ScrollView>
    </Screen>
  )
}

const $screenContentContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  flex: 1,
  paddingHorizontal: spacing.lg,
})

const $header: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  flexDirection: "row",
  justifyContent: "space-between",
  alignItems: "center",
  paddingVertical: spacing.md,
  borderBottomWidth: 1,
  borderBottomColor: "rgba(0,0,0,0.1)",
  marginBottom: spacing.lg,
})

const $backButton: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  paddingVertical: spacing.xs,
  paddingHorizontal: spacing.sm,
})

const $backButtonText: ThemedStyle<TextStyle> = ({ colors }) => ({
  fontSize: 16,
  color: colors.palette.primary500,
  fontWeight: "600",
})

const $shareButton: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  paddingVertical: spacing.xs,
  paddingHorizontal: spacing.sm,
})

const $shareButtonText: ThemedStyle<TextStyle> = ({ colors }) => ({
  fontSize: 16,
  color: colors.palette.primary500,
  fontWeight: "600",
})

const $scrollContainer: ThemedStyle<ViewStyle> = () => ({
  flex: 1,
})

const $scrollContent: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  paddingBottom: spacing.xxl,
})

const $referenceContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  alignItems: "center",
  marginBottom: spacing.xl,
  paddingVertical: spacing.lg,
  backgroundColor: "rgba(0,0,0,0.02)",
  borderRadius: 16,
})

const $referenceText: ThemedStyle<TextStyle> = ({ colors }) => ({
  color: colors.palette.primary600,
  fontSize: 20,
  fontWeight: "700",
  textAlign: "center",
})

const $verseContainer: ThemedStyle<ViewStyle> = ({ spacing, colors }) => ({
  backgroundColor: colors.palette.neutral200,
  borderRadius: 20,
  padding: spacing.xl,
  marginBottom: spacing.xl,
  borderWidth: 1,
  borderColor: colors.palette.neutral200,
  shadowColor: "#000",
  shadowOffset: {
    width: 0,
    height: 2,
  },
  shadowOpacity: 0.1,
  shadowRadius: 8,
  elevation: 3,
})

const $arabicText: ThemedStyle<TextStyle> = ({ colors }) => ({
  fontSize: 24,
  lineHeight: 40,
  textAlign: "right",
  color: colors.text,
  fontWeight: "500",
  letterSpacing: 0.5,
})

const $translationContainer: ThemedStyle<ViewStyle> = ({ spacing, colors }) => ({
  backgroundColor: colors.palette.neutral200,
  borderRadius: 20,
  padding: spacing.xl,
  marginBottom: spacing.xl,
  borderWidth: 1,
  borderColor: colors.palette.neutral200,
  shadowColor: "#000",
  shadowOffset: {
    width: 0,
    height: 2,
  },
  shadowOpacity: 0.1,
  shadowRadius: 8,
  elevation: 3,
})

const $translationLabel: ThemedStyle<TextStyle> = ({ colors, spacing }) => ({
  fontSize: 16,
  fontWeight: "600",
  color: colors.palette.primary500,
  marginBottom: spacing.sm,
})

const $translationText: ThemedStyle<TextStyle> = ({ colors }) => ({
  fontSize: 18,
  lineHeight: 28,
  color: colors.text,
  fontWeight: "400",
})

const $actionContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  marginTop: spacing.lg,
  alignItems: "center",
})

const $shareActionButton: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  backgroundColor: colors.palette.primary500,
  borderRadius: 25,
  paddingVertical: spacing.md,
  paddingHorizontal: spacing.xl,
  minWidth: 200,
  shadowColor: "#000",
  shadowOffset: {
    width: 0,
    height: 4,
  },
  shadowOpacity: 0.2,
  shadowRadius: 8,
  elevation: 5,
})

const $shareActionButtonText: ThemedStyle<TextStyle> = ({ colors }) => ({
  color: colors.palette.neutral100,
  fontSize: 16,
  fontWeight: "600",
  textAlign: "center",
})