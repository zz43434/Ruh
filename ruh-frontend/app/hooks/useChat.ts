import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/services/api'
import type { ChatMessage, ChatResponse, VerseChoiceMessage, ChatInitResponse } from '@/services/api/types'

// Query keys for chat-related queries
export const chatKeys = {
  all: ['chat'] as const,
  conversations: () => [...chatKeys.all, 'conversations'] as const,
  conversation: (id: string) => [...chatKeys.conversations(), id] as const,
  init: () => [...chatKeys.all, 'init'] as const,
}

// Initialize chat conversation
export function useChatInit() {
  return useQuery({
    queryKey: chatKeys.init(),
    queryFn: async () => {
      const response = await api.initChat()
      if (response.kind === 'error') {
        throw new Error('Failed to initialize chat')
      }
      return response.data
    },
    staleTime: Infinity, // Chat init should only happen once
    retry: 3,
  })
}

// Send chat message with optimistic updates
export function useSendChatMessage() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (message: ChatMessage) => {
      const response = await api.sendChatMessage(message)
      if (response.kind === 'error') {
        throw new Error('Failed to send message')
      }
      return response.data
    },
    onMutate: async (newMessage) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: chatKeys.all })

      // Optimistically add the user message to the conversation
      const optimisticMessage = {
        id: Date.now().toString(),
        text: newMessage.message,
        sender: 'user' as const,
        timestamp: new Date(),
      }

      // Store the optimistic message for potential rollback
      return { optimisticMessage }
    },
    onError: (err, newMessage, context) => {
      // Rollback optimistic update on error
      console.error('Chat message failed:', err)
    },
    onSuccess: (data, variables) => {
      // Invalidate and refetch chat-related queries
      queryClient.invalidateQueries({ queryKey: chatKeys.conversations() })
    },
  })
}

// Send verse choice
export function useSendVerseChoice() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (verseChoice: VerseChoiceMessage) => {
      const response = await api.sendVerseChoice(verseChoice)
      if (response.kind === 'error') {
        throw new Error('Failed to send verse choice')
      }
      return response.data
    },
    onSuccess: () => {
      // Invalidate chat queries to refetch updated conversation
      queryClient.invalidateQueries({ queryKey: chatKeys.conversations() })
    },
    retry: 2,
  })
}

// Custom hook for managing chat state with React Query
export function useChat(conversationId?: string) {
  const chatInit = useChatInit()
  const sendMessage = useSendChatMessage()
  const sendVerseChoice = useSendVerseChoice()

  return {
    // Query states
    isInitializing: chatInit.isLoading,
    initError: chatInit.error,
    conversationData: chatInit.data,
    
    // Mutation states
    isSendingMessage: sendMessage.isPending,
    isSendingVerseChoice: sendVerseChoice.isPending,
    sendMessageError: sendMessage.error,
    verseChoiceError: sendVerseChoice.error,
    
    // Actions
    sendChatMessage: sendMessage.mutate,
    sendVerseChoiceMessage: sendVerseChoice.mutate,
    
    // Reset functions
    resetSendMessage: sendMessage.reset,
    resetVerseChoice: sendVerseChoice.reset,
  }
}