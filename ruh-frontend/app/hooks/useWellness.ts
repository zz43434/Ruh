import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { safeStorage } from '@/services/safeStorage'
import { api } from '@/services/api'
import type { WellnessCheckin, WellnessResponse, WellnessHistory } from '@/services/api/types'

// Query keys for wellness-related queries
export const wellnessKeys = {
  all: ['wellness'] as const,
  history: () => [...wellnessKeys.all, 'history'] as const,
  historyWithParams: (limit: number, offset: number) => [...wellnessKeys.history(), { limit, offset }] as const,
  checkins: () => [...wellnessKeys.all, 'checkins'] as const,
}

// Get wellness history
export function useWellnessHistory(limit: number = 10, offset: number = 0) {
  return useQuery({
    queryKey: wellnessKeys.historyWithParams(limit, offset),
    queryFn: async () => {
      const response = await api.getWellnessHistory(limit, offset)
      if (response.kind === 'error') {
        throw new Error('Failed to fetch wellness history')
      }
      return response.data
    },
    staleTime: 2 * 60 * 1000, // 2 minutes - wellness data changes more frequently
    gcTime: 10 * 60 * 1000, // 10 minutes cache time
  })
}

// Submit wellness check-in with optimistic updates
export function useSubmitWellnessCheckin() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (checkin: WellnessCheckin) => {
      const response = await api.submitWellnessCheckin(checkin)
      if (response.kind === 'error') {
        throw new Error('Failed to submit wellness check-in')
      }
      return response.data
    },
    onMutate: async (newCheckin) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: wellnessKeys.history() })

      // Snapshot the previous value
      const previousHistory = queryClient.getQueryData(wellnessKeys.historyWithParams(10, 0))

      // Optimistically update the cache
      queryClient.setQueryData(wellnessKeys.historyWithParams(10, 0), (old: WellnessHistory | undefined) => {
        if (!old) return old

        const optimisticEntry = {
          id: Date.now(), // Temporary ID
          mood: newCheckin.mood,
          energy_level: newCheckin.energy_level,
          stress_level: newCheckin.stress_level,
          notes: newCheckin.notes || '',
          timestamp: new Date().toISOString(),
        }

        return {
          ...old,
          total_entries: old.total_entries + 1,
          wellness_history: [optimisticEntry, ...old.wellness_history],
        }
      })

      // Store offline for later sync if needed
      try {
        const offlineCheckins = await safeStorage.getItem('offline_wellness_checkins')
        const checkins = offlineCheckins ? JSON.parse(offlineCheckins) : []
        checkins.push({ ...newCheckin, timestamp: new Date().toISOString(), synced: false })
        await safeStorage.setItem('offline_wellness_checkins', JSON.stringify(checkins))
      } catch (error) {
        console.warn('Failed to store offline wellness checkin:', error)
      }

      return { previousHistory }
    },
    onError: (err, newCheckin, context) => {
      // Rollback optimistic update on error
      if (context?.previousHistory) {
        queryClient.setQueryData(wellnessKeys.historyWithParams(10, 0), context.previousHistory)
      }
      console.error('Wellness checkin failed:', err)
    },
    onSuccess: async (data, variables) => {
      // Mark as synced in offline storage
      try {
        const offlineCheckins = await safeStorage.getItem('offline_wellness_checkins')
        if (offlineCheckins) {
          const checkins = JSON.parse(offlineCheckins)
          const updatedCheckins = checkins.map((checkin: any) => 
            checkin.mood === variables.mood && 
            checkin.energy_level === variables.energy_level && 
            checkin.stress_level === variables.stress_level
              ? { ...checkin, synced: true }
              : checkin
          )
          await safeStorage.setItem('offline_wellness_checkins', JSON.stringify(updatedCheckins))
        }
      } catch (error) {
        console.warn('Failed to update offline wellness checkin status:', error)
      }

      // Invalidate and refetch wellness history
      queryClient.invalidateQueries({ queryKey: wellnessKeys.history() })
    },
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  })
}

// Sync offline wellness checkins
export function useSyncOfflineWellnessCheckins() {
  const queryClient = useQueryClient()
  const submitCheckin = useSubmitWellnessCheckin()

  return useMutation({
    mutationFn: async () => {
      const offlineCheckins = await safeStorage.getItem('offline_wellness_checkins')
      if (!offlineCheckins) return []

      const checkins = JSON.parse(offlineCheckins)
      const unsyncedCheckins = checkins.filter((checkin: any) => !checkin.synced)

      const syncPromises = unsyncedCheckins.map(async (checkin: any) => {
        try {
          const { timestamp, synced, ...checkinData } = checkin
          await submitCheckin.mutateAsync(checkinData)
          return { ...checkin, synced: true }
        } catch (error) {
          console.error('Failed to sync wellness checkin:', error)
          return checkin
        }
      })

      const syncedCheckins = await Promise.all(syncPromises)
      const allCheckins = [...checkins.filter((c: any) => c.synced), ...syncedCheckins]
      
      await safeStorage.setItem('offline_wellness_checkins', JSON.stringify(allCheckins))
      return syncedCheckins
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: wellnessKeys.history() })
    },
  })
}

// Get offline wellness checkins
export function useOfflineWellnessCheckins() {
  return useQuery({
    queryKey: [...wellnessKeys.all, 'offline'],
    queryFn: async () => {
      const offlineCheckins = await safeStorage.getItem('offline_wellness_checkins')
      return offlineCheckins ? JSON.parse(offlineCheckins) : []
    },
    staleTime: 0, // Always check for offline data
  })
}

// Combined hook for wellness functionality
export function useWellness() {
  const queryClient = useQueryClient()
  const submitCheckin = useSubmitWellnessCheckin()
  const syncOffline = useSyncOfflineWellnessCheckins()

  const invalidateWellnessData = () => {
    queryClient.invalidateQueries({ queryKey: wellnessKeys.all })
  }

  const clearWellnessCache = () => {
    queryClient.removeQueries({ queryKey: wellnessKeys.all })
  }

  const clearOfflineData = async () => {
    try {
      await safeStorage.removeItem('offline_wellness_checkins')
      queryClient.invalidateQueries({ queryKey: [...wellnessKeys.all, 'offline'] })
    } catch (error) {
      console.error('Failed to clear offline wellness data:', error)
    }
  }

  return {
    // Mutations
    submitWellnessCheckin: submitCheckin.mutate,
    syncOfflineCheckins: syncOffline.mutate,
    
    // States
    isSubmittingCheckin: submitCheckin.isPending,
    isSyncingOffline: syncOffline.isPending,
    submitError: submitCheckin.error,
    syncError: syncOffline.error,
    
    // Utilities
    invalidateWellnessData,
    clearWellnessCache,
    clearOfflineData,
    
    // Reset functions
    resetSubmitCheckin: submitCheckin.reset,
    resetSync: syncOffline.reset,
  }
}