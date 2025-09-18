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
import { api } from "@/services/api"
import { Verse } from "@/services/api/types"

interface VersesScreenProps {}

export const VersesScreen: FC<VersesScreenProps> = function VersesScreen() {
  const { themed, theme } = useAppTheme()
  const [verses, setVerses] = useState<Verse[]>([])
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [searchMode, setSearchMode] = useState(false)

  const loadVerses = async (refresh = false) => {
    if (refresh) setRefreshing(true)
    else setLoading(true)

    try {
      const response = await api.getVerses(20, 0)
      if (response.kind === "ok") {
        setVerses(response.data.verses)
      } else {
        Alert.alert("Error", "Failed to load verses")
      }
    } catch (error) {
      Alert.alert("Error", "Failed to load verses")
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const searchVerses = async () => {
    if (!searchQuery.trim()) return

    setLoading(true)
    try {
      const response = await api.searchVerses(searchQuery)
      if (response.kind === "ok") {
        setVerses(response.data.verses)
        setSearchMode(true)
      } else {
        Alert.alert("Error", "Failed to search verses")
      }
    } catch (error) {
      Alert.alert("Error", "Failed to search verses")
    } finally {
      setLoading(false)
    }
  }

  const getRandomVerse = async () => {
    setLoading(true)
    try {
      const response = await api.getRandomVerse()
      if (response.kind === "ok") {
        setVerses([response.data])
        setSearchMode(true)
      } else {
        Alert.alert("Error", "Failed to get random verse")
      }
    } catch (error) {
      Alert.alert("Error", "Failed to get random verse")
    } finally {
      setLoading(false)
    }
  }

  const clearSearch = () => {
    setSearchQuery("")
    setSearchMode(false)
    loadVerses()
  }

  useEffect(() => {
    loadVerses()
  }, [])

  const renderVerse = ({ item }: { item: Verse }) => (
    <View style={themed($verseCard)}>
      <View style={themed($verseHeader)}>
        <Text style={themed($verseReference)}>
          Chapter {item.chapter}, Verse {item.verse}
        </Text>
      </View>
      <Text style={themed($verseText)}>{item.text}</Text>
      {item.translation && (
        <Text style={themed($verseTranslation)}>{item.translation}</Text>
      )}
    </View>
  )

  return (
    <Screen
      preset="fixed"
      contentContainerStyle={themed($screenContentContainer)}
      safeAreaEdges={["top"]}
    >
      <View style={themed($header)}>
        <Text preset="heading" style={themed($headerTitle)}>
          Verses
        </Text>
        <Text style={themed($headerSubtitle)}>
          Explore and search through verses
        </Text>
      </View>

      <View style={themed($searchContainer)}>
        <TextInput
          value={searchQuery}
          onChangeText={setSearchQuery}
          placeholder="Search verses..."
          style={themed($searchInput)}
          onSubmitEditing={searchVerses}
          placeholderTextColor={theme.colors.palette.neutral500}
        />
        <View style={themed($buttonRow)}>
          <Button
            text="Search"
            onPress={searchVerses}
            style={themed($searchButton)}
            disabled={!searchQuery.trim()}
          />
          <Button
            text="Random"
            onPress={getRandomVerse}
            style={themed($randomButton)}
          />
          {searchMode && (
            <Button
              text="Clear"
              onPress={clearSearch}
              style={themed($clearButton)}
            />
          )}
        </View>
      </View>

      <FlatList
        data={verses}
        renderItem={renderVerse}
        keyExtractor={(item, index) => `${item.chapter}-${item.verse}-${index}`}
        contentContainerStyle={themed($listContainer)}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={() => loadVerses(true)} />
        }
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={
          <View style={themed($emptyContainer)}>
            <Text style={themed($emptyText)}>
              {loading ? "Loading verses..." : "No verses found"}
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