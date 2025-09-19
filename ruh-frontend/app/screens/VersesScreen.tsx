import React, { FC, useEffect, useState } from "react"
import {
  View,
  ViewStyle,
  TextStyle,
  FlatList,
  RefreshControl,
  Alert,
  TouchableOpacity,
  TextInput,
} from "react-native"
import { Screen } from "@/components/Screen"
import { Text } from "@/components/Text"
import { Button } from "@/components/Button"
import { useAppTheme } from "@/theme/context"
import type { ThemedStyle } from "@/theme/types"
import { useNavigation } from "@react-navigation/native"
import type { NativeStackNavigationProp } from "@react-navigation/native-stack"
import type { AppStackParamList } from "@/navigators/AppNavigator"
import { api } from "@/services/api"
import { Chapter } from "@/services/api/types"

interface VersesScreenProps {}

export const VersesScreen: FC<VersesScreenProps> = function VersesScreen() {
  const { themed, theme } = useAppTheme()
  const navigation = useNavigation<NativeStackNavigationProp<AppStackParamList>>()
  const [chapters, setChapters] = useState<Chapter[]>([])
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [filteredChapters, setFilteredChapters] = useState<Chapter[]>([])

  const loadChapters = async (refresh = false) => {
    if (refresh) setRefreshing(true)
    else setLoading(true)

    try {
      const response = await api.getChapters()
      if (response.kind === "ok") {
        setChapters(response.chapters)
        setFilteredChapters(response.chapters)
      } else {
        Alert.alert("Error", "Failed to load chapters")
      }
    } catch (error) {
      Alert.alert("Error", "Failed to load chapters")
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const searchChapters = async () => {
    if (!searchQuery.trim()) {
      setFilteredChapters(chapters)
      return
    }

    try {
      // Use semantic search API
      const response = await api.searchChapters(searchQuery.trim(), 20)
      if (response.kind === "ok") {
        setFilteredChapters(response.chapters)
      } else {
        // Fallback to local filtering if API fails
        const filtered = chapters.filter(chapter =>
          chapter.surah_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          chapter.surah_number.toString().includes(searchQuery)
        )
        setFilteredChapters(filtered)
      }
    } catch (error) {
      // Fallback to local filtering if API fails
      const filtered = chapters.filter(chapter =>
        chapter.surah_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        chapter.surah_number.toString().includes(searchQuery)
      )
      setFilteredChapters(filtered)
    }
  }

  const clearSearch = () => {
    setSearchQuery("")
    setFilteredChapters(chapters)
  }

  useEffect(() => {
    loadChapters()
  }, [])

  useEffect(() => {
    const delayedSearch = setTimeout(() => {
      searchChapters()
    }, 300) // Debounce search by 300ms

    return () => clearTimeout(delayedSearch)
  }, [searchQuery, chapters])

  const handleChapterPress = (chapter: Chapter) => {
     // Navigate to chapter details - for now using VerseDetails with chapter info
     navigation.navigate("ChapterDetails", { 
       surahNumber: chapter.surah_number
     })
   }

  const renderChapter = ({ item }: { item: Chapter }) => (
    <TouchableOpacity onPress={() => handleChapterPress(item)}>
      <View style={themed($verseCard)}>
        <View style={themed($verseHeader)}>
          <Text style={themed($verseReference)}>
            {item.surah_number}. {item.surah_name}
          </Text>
        </View>
        <Text style={themed($verseText)}>
          {item.themes_found && item.themes_found.length > 0 
            ? `Themes: ${item.themes_found.join(', ')}`
            : `${item.number_of_verses} verses • ${item.revelation_place}`
          }
        </Text>
      </View>
    </TouchableOpacity>
  )

  return (
    <Screen
      preset="fixed"
      contentContainerStyle={themed($screenContentContainer)}
      safeAreaEdges={["top"]}
    >
      <View style={themed($header)}>
        <Text preset="heading" style={themed($headerTitle)}>
          Chapters
        </Text>
        <Text style={themed($headerSubtitle)}>
          Explore Quran chapters
        </Text>
      </View>

      <View style={themed($searchContainer)}>
        <TextInput
          value={searchQuery}
          onChangeText={setSearchQuery}
          placeholder="Search chapters by theme, topic, or name..."
          style={themed($searchInput)}
          placeholderTextColor={theme.colors.palette.neutral500}
        />
        <View style={themed($buttonRow)}>
          <Button
            text="Clear"
            onPress={clearSearch}
            style={themed($clearButton)}
          />
        </View>
      </View>

      <FlatList
        data={filteredChapters}
        renderItem={renderChapter}
        keyExtractor={(item) => `chapter-${item.surah_number}`}
        contentContainerStyle={themed($listContainer)}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={() => loadChapters(true)} />
        }
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={
          <View style={themed($emptyContainer)}>
            <Text style={themed($emptyText)}>
              {loading ? "Loading chapters..." : "No chapters found"}
            </Text>
          </View>
        }
      />
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

const $searchContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  marginBottom: spacing.lg,
})

const $searchInput: ThemedStyle<any> = ({ colors, spacing }) => ({
  backgroundColor: colors.palette.neutral100,
  borderRadius: 12,
  paddingHorizontal: spacing.md,
  paddingVertical: spacing.sm,
  fontSize: 16,
  color: colors.text,
  marginBottom: spacing.sm,
  borderWidth: 1,
  borderColor: colors.palette.neutral300,
})

const $buttonRow: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  flexDirection: "row",
  gap: spacing.sm,
})

const $searchButton: ThemedStyle<ViewStyle> = () => ({
  flex: 1,
})

const $randomButton: ThemedStyle<ViewStyle> = () => ({
  flex: 1,
})

const $clearButton: ThemedStyle<ViewStyle> = () => ({
  flex: 1,
})

const $listContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  paddingBottom: spacing.lg,
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
  marginBottom: spacing.sm,
})

const $verseReference: ThemedStyle<TextStyle> = ({ colors }) => ({
  fontSize: 14,
  fontWeight: "600",
  color: colors.palette.primary500,
})

const $verseText: ThemedStyle<TextStyle> = ({ colors, spacing }) => ({
  fontSize: 16,
  lineHeight: 24,
  marginBottom: spacing.sm,
  color: colors.text,
})

const $verseTranslation: ThemedStyle<TextStyle> = ({ colors }) => ({
  fontSize: 14,
  lineHeight: 20,
  color: colors.textDim,
  fontStyle: "italic",
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