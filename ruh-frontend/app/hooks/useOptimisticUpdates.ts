import { useQueryClient } from '@tanstack/react-query'
import { chatKeys } from './useChat'
import { wellnessKeys } from './useWellness'
import { versesKeys } from './useVerses'
import { ChatStorage, WellnessStorage, VersesStorage } from '@/services/offlineStorage'
import type { OfflineChatMessage, OfflineWellnessCheckin, OfflineVerse } from '@/services/offlineStorage'

// Optimistic updates for chat messages
export function useOptimisticChat() {
  const queryClient = useQueryClient()

  const addOptimisticMessage = async (
    message: string,
    conversationId: string,
    sender: 'user' | 'bot' = 'user'
  ) => {
    const optimisticMessage: OfflineChatMessage = {
      id: `temp-${Date.now()}`,
      text: message,
      sender,
      timestamp: new Date().toISOString(),
      conversationId,
      synced: false,
    }

    // Add to offline storage immediately
    await ChatStorage.addMessage(optimisticMessage)

    // Update React Query cache optimistically
    queryClient.setQueryData(
      chatKeys.conversation(conversationId),
      (oldData: OfflineChatMessage[] | undefined) => {
        return oldData ? [...oldData, optimisticMessage] : [optimisticMessage]
      }
    )

    return optimisticMessage
  }

  const updateOptimisticMessage = async (
    tempId: string,
    updates: Partial<OfflineChatMessage>
  ) => {
    // Update offline storage
    await ChatStorage.updateMessage(tempId, updates)

    // Update React Query cache
    queryClient.setQueryData(
      chatKeys.conversations(),
      (oldData: OfflineChatMessage[] | undefined) => {
        if (!oldData) return oldData
        return oldData.map(msg => 
          msg.id === tempId ? { ...msg, ...updates } : msg
        )
      }
    )
  }

  const removeOptimisticMessage = async (tempId: string) => {
    // Remove from offline storage
    await ChatStorage.removeMessage(tempId)

    // Update React Query cache
    queryClient.setQueryData(
      chatKeys.conversations(),
      (oldData: OfflineChatMessage[] | undefined) => {
        if (!oldData) return oldData
        return oldData.filter(msg => msg.id !== tempId)
      }
    )
  }

  const rollbackOptimisticMessage = async (tempId: string, conversationId: string) => {
    await removeOptimisticMessage(tempId)
    
    // Invalidate queries to refetch from server
    queryClient.invalidateQueries({ queryKey: chatKeys.conversation(conversationId) })
  }

  return {
    addOptimisticMessage,
    updateOptimisticMessage,
    removeOptimisticMessage,
    rollbackOptimisticMessage,
  }
}

// Optimistic updates for wellness checkins
export function useOptimisticWellness() {
  const queryClient = useQueryClient()

  const addOptimisticCheckin = async (
    checkin: Omit<OfflineWellnessCheckin, 'id' | 'timestamp' | 'synced'>
  ) => {
    const optimisticCheckin: OfflineWellnessCheckin = {
      ...checkin,
      id: `temp-${Date.now()}`,
      timestamp: new Date().toISOString(),
      synced: false,
    }

    // Add to offline storage immediately
    await WellnessStorage.addCheckin(optimisticCheckin)

    // Update React Query cache optimistically
    queryClient.setQueryData(
      wellnessKeys.historyWithParams(10, 0),
      (oldData: any) => {
        if (!oldData) return oldData
        return {
          ...oldData,
          total_entries: oldData.total_entries + 1,
          wellness_history: [
            {
              id: optimisticCheckin.id,
              mood: optimisticCheckin.mood,
              energy_level: optimisticCheckin.energy_level,
              stress_level: optimisticCheckin.stress_level,
              notes: optimisticCheckin.notes || '',
              timestamp: optimisticCheckin.timestamp,
            },
            ...oldData.wellness_history,
          ],
        }
      }
    )

    return optimisticCheckin
  }

  const updateOptimisticCheckin = async (
    tempId: string,
    updates: Partial<OfflineWellnessCheckin>
  ) => {
    // Update offline storage
    await WellnessStorage.updateCheckin(tempId, updates)

    // Update React Query cache
    queryClient.setQueryData(
      wellnessKeys.historyWithParams(10, 0),
      (oldData: any) => {
        if (!oldData) return oldData
        return {
          ...oldData,
          wellness_history: oldData.wellness_history.map((entry: any) =>
            entry.id === tempId ? { ...entry, ...updates } : entry
          ),
        }
      }
    )
  }

  const rollbackOptimisticCheckin = async (tempId: string) => {
    // Remove from offline storage
    const checkins = await WellnessStorage.getCheckins()
    const filteredCheckins = checkins.filter(checkin => checkin.id !== tempId)
    await WellnessStorage.markAsSynced([]) // This will update the storage

    // Update React Query cache
    queryClient.setQueryData(
      wellnessKeys.historyWithParams(10, 0),
      (oldData: any) => {
        if (!oldData) return oldData
        return {
          ...oldData,
          total_entries: Math.max(0, oldData.total_entries - 1),
          wellness_history: oldData.wellness_history.filter((entry: any) => entry.id !== tempId),
        }
      }
    )

    // Invalidate queries to refetch from server
    queryClient.invalidateQueries({ queryKey: wellnessKeys.history() })
  }

  return {
    addOptimisticCheckin,
    updateOptimisticCheckin,
    rollbackOptimisticCheckin,
  }
}

// Optimistic updates for favorite verses
export function useOptimisticVerses() {
  const queryClient = useQueryClient()

  const addOptimisticFavorite = async (verse: Omit<OfflineVerse, 'favorited_at'>) => {
    const optimisticVerse: OfflineVerse = {
      ...verse,
      favorited_at: new Date().toISOString(),
    }

    // Add to offline storage immediately
    await VersesStorage.addFavoriteVerse(optimisticVerse)

    // Update React Query cache optimistically
    queryClient.setQueryData(
      [...versesKeys.all, 'favorites'],
      (oldData: OfflineVerse[] | undefined) => {
        return oldData ? [...oldData, optimisticVerse] : [optimisticVerse]
      }
    )

    return optimisticVerse
  }

  const removeOptimisticFavorite = async (chapter: number, verse: number) => {
    // Remove from offline storage
    await VersesStorage.removeFavoriteVerse(chapter, verse)

    // Update React Query cache
    queryClient.setQueryData(
      [...versesKeys.all, 'favorites'],
      (oldData: OfflineVerse[] | undefined) => {
        if (!oldData) return oldData
        return oldData.filter(fav => !(fav.chapter === chapter && fav.verse === verse))
      }
    )
  }

  const rollbackOptimisticFavorite = async (chapter: number, verse: number, wasOriginallyFavorited: boolean) => {
    if (wasOriginallyFavorited) {
      // Re-add to favorites if it was originally favorited
      const verseData: OfflineVerse = {
        chapter,
        verse,
        text: '', // These would need to be provided
        translation: '',
        favorited_at: new Date().toISOString(),
      }
      await VersesStorage.addFavoriteVerse(verseData)
    } else {
      // Remove from favorites if it wasn't originally favorited
      await VersesStorage.removeFavoriteVerse(chapter, verse)
    }

    // Invalidate queries to refetch from server
    queryClient.invalidateQueries({ queryKey: [...versesKeys.all, 'favorites'] })
  }

  return {
    addOptimisticFavorite,
    removeOptimisticFavorite,
    rollbackOptimisticFavorite,
  }
}

// Combined optimistic updates hook
export function useOptimisticUpdates() {
  const chat = useOptimisticChat()
  const wellness = useOptimisticWellness()
  const verses = useOptimisticVerses()

  return {
    chat,
    wellness,
    verses,
  }
}

// Hook for handling optimistic update errors
export function useOptimisticErrorHandling() {
  const queryClient = useQueryClient()

  const handleOptimisticError = async (
    error: Error,
    rollbackFn: () => Promise<void>,
    queryKeys: string[][]
  ) => {
    console.error('Optimistic update failed:', error)

    // Execute rollback function
    await rollbackFn()

    // Invalidate related queries to refetch from server
    for (const queryKey of queryKeys) {
      queryClient.invalidateQueries({ queryKey })
    }

    // Show error to user (you might want to use a toast or notification system)
    // This could be integrated with your app's error handling system
  }

  const retryOptimisticUpdate = async (
    updateFn: () => Promise<void>,
    maxRetries: number = 3,
    delay: number = 1000
  ) => {
    let retries = 0
    
    while (retries < maxRetries) {
      try {
        await updateFn()
        return true
      } catch (error) {
        retries++
        if (retries >= maxRetries) {
          throw error
        }
        
        // Exponential backoff
        await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, retries - 1)))
      }
    }
    
    return false
  }

  return {
    handleOptimisticError,
    retryOptimisticUpdate,
  }
}