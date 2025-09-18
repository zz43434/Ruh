import React, { FC, useState, useRef, useEffect } from "react"
import {
  View,
  ViewStyle,
  TextStyle,
  FlatList,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  Animated,
  Easing,
} from "react-native"
import { Screen } from "@/components/Screen"
import { Text } from "@/components/Text"
import { Button } from "@/components/Button"
import { Icon } from "@/components/Icon"
import { useAppTheme } from "@/theme/context"
import { $styles } from "@/theme/styles"
import type { ThemedStyle } from "@/theme/types"
import { useSafeAreaInsetsStyle } from "@/utils/useSafeAreaInsetsStyle"
import { api } from "@/services/api"

interface Message {
  id: string
  text: string
  sender: "user" | "bot"
  timestamp: Date
  verses?: any[]
  sentiment?: string
  verseOffer?: {
    show_options: boolean
    message: string
    options: Array<{
      id: string
      text: string
      type: string
    }>
  }
  originalMessage?: string
}

interface TypingIndicatorProps {
  themed: any
}

const TypingIndicator: FC<TypingIndicatorProps> = ({ themed }) => {
  const dot1 = useRef(new Animated.Value(0)).current
  const dot2 = useRef(new Animated.Value(0)).current
  const dot3 = useRef(new Animated.Value(0)).current

  useEffect(() => {
    const animateDots = () => {
      const createAnimation = (dot: Animated.Value, delay: number) =>
        Animated.loop(
          Animated.sequence([
            Animated.timing(dot, {
              toValue: 1,
              duration: 600,
              delay,
              easing: Easing.inOut(Easing.ease),
              useNativeDriver: true,
            }),
            Animated.timing(dot, {
              toValue: 0,
              duration: 600,
              easing: Easing.inOut(Easing.ease),
              useNativeDriver: true,
            }),
          ])
        )

      Animated.parallel([
        createAnimation(dot1, 0),
        createAnimation(dot2, 200),
        createAnimation(dot3, 400),
      ]).start()
    }

    animateDots()
  }, [])

  return (
    <View style={themed($typingContainer)}>
      <View style={themed($typingBubble)}>
        <View style={themed($dotsContainer)}>
          <Animated.View
            style={[
              themed($dot),
              {
                opacity: dot1,
                transform: [
                  {
                    scale: dot1.interpolate({
                      inputRange: [0, 1],
                      outputRange: [1, 1.2],
                    }),
                  },
                ],
              },
            ]}
          />
          <Animated.View
            style={[
              themed($dot),
              {
                opacity: dot2,
                transform: [
                  {
                    scale: dot2.interpolate({
                      inputRange: [0, 1],
                      outputRange: [1, 1.2],
                    }),
                  },
                ],
              },
            ]}
          />
          <Animated.View
            style={[
              themed($dot),
              {
                opacity: dot3,
                transform: [
                  {
                    scale: dot3.interpolate({
                      inputRange: [0, 1],
                      outputRange: [1, 1.2],
                    }),
                  },
                ],
              },
            ]}
          />
        </View>
      </View>
    </View>
  )
}

export const ChatScreen: FC = function ChatScreen() {
  const { themed, theme } = useAppTheme()
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      text: "Assalamu Alaikum! I'm here to provide spiritual guidance and support. How are you feeling today? You can share what's on your mind, and I'll offer Islamic wisdom and verses to help guide you.",
      sender: "bot",
      timestamp: new Date(),
    },
  ])
  const [inputText, setInputText] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const flatListRef = useRef<FlatList>(null)

  const $bottomContainerInsets = useSafeAreaInsetsStyle(["bottom"])

  const sendMessage = async () => {
    if (!inputText.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText.trim(),
      sender: "user",
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputText("")
    setIsLoading(true)

    try {
      const response = await api.sendChatMessage({
        message: inputText.trim(),
        conversation_id: conversationId || "",
      })

      if (response.kind === "ok") {
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: response.data.response,
          sender: "bot",
          timestamp: new Date(),
          verses: response.data.relevant_verses,
          sentiment: response.data.sentiment,
          verseOffer: response.data.verse_offer,
          originalMessage: inputText.trim(),
        }

        setMessages((prev) => [...prev, botMessage])
        setConversationId(response.data.conversation_id)
      } else {
        // Handle error
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: "I apologize, but I'm having trouble connecting right now. Please try again in a moment.",
          sender: "bot",
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, errorMessage])
      }
    } catch (error) {
      console.error("Chat error:", error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "I apologize, but I'm having trouble connecting right now. Please try again in a moment.",
        sender: "bot",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (event: any) => {
    if (Platform.OS === 'web' && event.nativeEvent.key === 'Enter' && !event.nativeEvent.shiftKey) {
      event.preventDefault()
      sendMessage()
    }
  }

  const handleVerseChoice = async (choice: string, messageId: string, originalMessage: string) => {
    try {
      const conversationIdToUse = conversationId || "default" // You may want to implement proper conversation ID management
      
      const response = await api.sendVerseChoice({
        choice,
        conversation_id: conversationIdToUse,
        message_id: messageId,
        original_message: originalMessage,
      })

      if (response.kind === "ok") {
        const botMessage: Message = {
          id: Date.now().toString(),
          text: response.data.response,
          sender: "bot",
          timestamp: new Date(),
          verses: response.data.relevant_verses || [],
          sentiment: response.data.sentiment,
        }

        setMessages((prev) => [...prev, botMessage])
      }
    } catch (error) {
      console.error("Error sending verse choice:", error)
    }
  }

  const renderMessage = ({ item }: { item: Message }) => {
    const isUser = item.sender === "user"
    
    return (
      <View style={themed(isUser ? $userMessageContainer : $botMessageContainer)}>
        <View style={themed(isUser ? $userBubble : $botBubble)}>
          <Text style={themed(isUser ? $userMessageText : $botMessageText)}>
            {item.text}
          </Text>
          {item.verses && item.verses.length > 0 && (
            <View style={themed($versesContainer)}>
              {item.verses.slice(0, 1).map((verse, index) => (
                <View key={index} style={themed($verseCard)}>
                  <Text style={themed($verseText)}>{verse.arabic_text}</Text>
                  <Text style={themed($verseReference)}>
                    {verse.surah_name} ({verse.verse_number})
                  </Text>
                </View>
              ))}
            </View>
          )}
          {item.verseOffer && item.verseOffer.show_options && (
            <View style={themed($verseOfferContainer)}>
              <Text style={themed($verseOfferMessage)}>{item.verseOffer.message}</Text>
              <View style={themed($verseOptionsContainer)}>
                {item.verseOffer.options.map((option) => (
                  <TouchableOpacity
                    key={option.id}
                    style={themed($verseOptionButton)}
                    onPress={() => handleVerseChoice(option.type, item.id, item.originalMessage || "")}
                  >
                    <Text style={themed($verseOptionText)}>{option.text}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          )}
        </View>
      </View>
    )
  }

  const scrollToBottom = () => {
    setTimeout(() => {
      flatListRef.current?.scrollToEnd({ animated: true })
    }, 100)
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  return (
    <Screen preset="fixed" contentContainerStyle={$styles.flex1}>
      <KeyboardAvoidingView
        style={$styles.flex1}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        keyboardVerticalOffset={Platform.OS === "ios" ? 0 : 0}
      >
        <View style={themed($header)}>
          <Text preset="heading" style={themed($headerTitle)}>
            Ruh Chat
          </Text>
          <Text style={themed($headerSubtitle)}>
            Islamic Spiritual Guidance
          </Text>
        </View>

        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={renderMessage}
          keyExtractor={(item) => item.id}
          style={themed($messagesList)}
          contentContainerStyle={themed($messagesContent)}
          showsVerticalScrollIndicator={false}
          onContentSizeChange={scrollToBottom}
        />

        {isLoading && <TypingIndicator themed={themed} />}

        <View style={themed([$inputContainer, $bottomContainerInsets])}>
          <View style={themed($inputWrapper)}>
            <TextInput
              style={themed($textInput)}
              value={inputText}
              onChangeText={setInputText}
              placeholder="Share what's on your mind..."
              placeholderTextColor={theme.colors.palette.neutral500}
              multiline
              maxLength={500}
              onKeyPress={handleKeyPress}
              blurOnSubmit={false}
              returnKeyType="send"
              enablesReturnKeyAutomatically={true}
            />
            <TouchableOpacity
              style={themed($sendButton)}
              onPress={sendMessage}
              disabled={!inputText.trim() || isLoading}
            >
              <Icon
                icon="caretRight"
                size={20}
                color={
                  !inputText.trim() || isLoading
                    ? theme.colors.palette.neutral400
                    : theme.colors.palette.primary500
                }
              />
            </TouchableOpacity>
          </View>
        </View>
      </KeyboardAvoidingView>
    </Screen>
  )
}

// Styles
const $header: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  backgroundColor: colors.palette.primary500,
  paddingHorizontal: spacing.lg,
  paddingVertical: spacing.md,
  borderBottomWidth: 1,
  borderBottomColor: colors.palette.primary600,
})

const $headerTitle: ThemedStyle<TextStyle> = ({ colors }) => ({
  color: colors.palette.neutral100,
  textAlign: "center",
})

const $headerSubtitle: ThemedStyle<TextStyle> = ({ colors, spacing }) => ({
  color: colors.palette.primary100,
  textAlign: "center",
  marginTop: spacing.xs,
  fontSize: 14,
})

const $messagesList: ThemedStyle<ViewStyle> = ({ colors }) => ({
  flex: 1,
  backgroundColor: colors.background,
})

const $messagesContent: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  paddingVertical: spacing.md,
})

const $userMessageContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  alignItems: "flex-end",
  marginVertical: spacing.xs,
  marginHorizontal: spacing.md,
})

const $botMessageContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  alignItems: "flex-start",
  marginVertical: spacing.xs,
  marginHorizontal: spacing.md,
})

const $userBubble: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  backgroundColor: colors.palette.primary500,
  borderRadius: 20,
  borderBottomRightRadius: 4,
  paddingHorizontal: spacing.md,
  paddingVertical: spacing.sm,
  maxWidth: "80%",
})

const $botBubble: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  backgroundColor: colors.palette.neutral200,
  borderRadius: 20,
  borderBottomLeftRadius: 4,
  paddingHorizontal: spacing.md,
  paddingVertical: spacing.sm,
  maxWidth: "85%",
})

const $userMessageText: ThemedStyle<TextStyle> = ({ colors }) => ({
  color: colors.palette.neutral100,
  fontSize: 16,
  lineHeight: 22,
})

const $botMessageText: ThemedStyle<TextStyle> = ({ colors }) => ({
  color: colors.palette.neutral900,
  fontSize: 16,
  lineHeight: 22,
})

const $versesContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  marginTop: spacing.sm,
})

const $verseCard: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  backgroundColor: colors.palette.primary100,
  borderRadius: 12,
  padding: spacing.sm,
  marginTop: spacing.xs,
  borderLeftWidth: 3,
  borderLeftColor: colors.palette.primary500,
})

const $verseText: ThemedStyle<TextStyle> = ({ colors }) => ({
  color: colors.palette.neutral800,
  fontSize: 15,
  lineHeight: 24,
  textAlign: "right",
  fontFamily: "serif",
})

const $verseReference: ThemedStyle<TextStyle> = ({ colors, spacing }) => ({
  color: colors.palette.primary600,
  fontSize: 12,
  marginTop: spacing.xs,
  fontWeight: "600",
})

const $typingContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  alignItems: "flex-start",
  marginVertical: spacing.xs,
  marginHorizontal: spacing.md,
})

const $typingBubble: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  backgroundColor: colors.palette.neutral200,
  borderRadius: 20,
  borderBottomLeftRadius: 4,
  paddingHorizontal: spacing.md,
  paddingVertical: spacing.sm,
})

const $dotsContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  flexDirection: "row",
  alignItems: "center",
  justifyContent: "center",
  paddingHorizontal: spacing.xs,
})

const $dot: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  width: 8,
  height: 8,
  borderRadius: 4,
  backgroundColor: colors.palette.neutral500,
  marginHorizontal: spacing.xxs,
})

const $inputContainer: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  backgroundColor: colors.background,
  paddingHorizontal: spacing.md,
  paddingVertical: spacing.sm,
  borderTopWidth: 1,
  borderTopColor: colors.palette.neutral300,
})

const $inputWrapper: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  flexDirection: "row",
  alignItems: "flex-end",
  backgroundColor: colors.palette.neutral100,
  borderRadius: 25,
  paddingHorizontal: spacing.md,
  paddingVertical: spacing.xs,
  minHeight: 50,
})

const $textInput: ThemedStyle<any> = ({ colors, spacing }) => ({
  flex: 1,
  fontSize: 16,
  color: colors.text,
  maxHeight: 100,
  paddingVertical: spacing.sm,
  paddingRight: spacing.sm,
})

const $sendButton: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  padding: spacing.xs,
  justifyContent: "center",
  alignItems: "center",
})

const $verseOfferContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  marginTop: spacing.sm,
})

const $verseOfferMessage: ThemedStyle<TextStyle> = ({ colors, spacing }) => ({
  color: colors.palette.neutral700,
  fontSize: 14,
  marginBottom: spacing.sm,
  fontStyle: "italic",
})

const $verseOptionsContainer: ThemedStyle<ViewStyle> = ({ spacing }) => ({
  flexDirection: "row",
  flexWrap: "wrap",
  gap: spacing.xs,
})

const $verseOptionButton: ThemedStyle<ViewStyle> = ({ colors, spacing }) => ({
  backgroundColor: colors.palette.primary500,
  borderRadius: 20,
  paddingHorizontal: spacing.md,
  paddingVertical: spacing.sm,
  marginRight: spacing.xs,
  marginBottom: spacing.xs,
})

const $verseOptionText: ThemedStyle<TextStyle> = ({ colors }) => ({
  color: colors.palette.neutral100,
  fontSize: 14,
  fontWeight: "600",
})