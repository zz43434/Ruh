import { QueryClient } from '@tanstack/react-query'
import { safeStorage } from './safeStorage'

// Create a client with optimized settings for mobile
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Cache data for 5 minutes by default
      staleTime: 5 * 60 * 1000,
      // Keep data in cache for 10 minutes
      gcTime: 10 * 60 * 1000,
      // Retry failed requests 3 times with exponential backoff
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      // Don't refetch on window focus for mobile
      refetchOnWindowFocus: false,
      // Refetch on reconnect
      refetchOnReconnect: true,
      // Network mode for offline support
      networkMode: 'offlineFirst',
    },
    mutations: {
      // Retry mutations once
      retry: 1,
      // Network mode for offline support
      networkMode: 'offlineFirst',
    },
  },
})

// Persist query cache to AsyncStorage
export async function persistQueryClient(queryClient: QueryClient) {
  try {
    const persistData = {
      clientState: queryClient.getQueryCache().getAll().map(query => ({
        queryKey: query.queryKey,
        queryHash: query.queryHash,
        state: query.state,
      })),
      timestamp: Date.now(),
    }
    
    await safeStorage.setItem('react-query-cache', JSON.stringify(persistData))
    console.log('Query cache persisted successfully')
  } catch (error) {
    console.error('Failed to persist query cache:', error)
  }
}

// Restore query cache from AsyncStorage
export async function restoreQueryClient(queryClient: QueryClient) {
  try {
    const persistedData = await safeStorage.getItem('react-query-cache')
    if (persistedData) {
      const { clientState, timestamp } = JSON.parse(persistedData)
      
      // Only restore if data is less than 24 hours old
      if (Date.now() - timestamp < 24 * 60 * 60 * 1000) {
        const queryCache = queryClient.getQueryCache()
        
        clientState.forEach((query: any) => {
          queryCache.build(queryClient, {
            queryKey: query.queryKey,
            queryHash: query.queryHash,
          }).setState(query.state)
        })
        
        console.log('Query cache restored successfully')
      } else {
        console.log('Cached data too old, skipping restore')
      }
    }
  } catch (error) {
    console.error('Failed to restore query cache:', error)
  }
}