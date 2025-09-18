import { QueryClient } from '@tanstack/react-query'
import AsyncStorage from '@react-native-async-storage/async-storage'

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
export const persistQueryClient = async () => {
  try {
    const queryCache = queryClient.getQueryCache()
    const queries = queryCache.getAll()
    
    const persistData = queries.map(query => ({
      queryKey: query.queryKey,
      queryHash: query.queryHash,
      data: query.state.data,
      dataUpdatedAt: query.state.dataUpdatedAt,
    }))
    
    await AsyncStorage.setItem('react-query-cache', JSON.stringify(persistData))
  } catch (error) {
    console.warn('Failed to persist query cache:', error)
  }
}

// Restore query cache from AsyncStorage
export const restoreQueryClient = async () => {
  try {
    const persistedData = await AsyncStorage.getItem('react-query-cache')
    if (persistedData) {
      const queries = JSON.parse(persistedData)
      const queryCache = queryClient.getQueryCache()
      
      queries.forEach((query: any) => {
        queryCache.build(queryClient, {
          queryKey: query.queryKey,
          queryHash: query.queryHash,
        }).setState({
          data: query.data,
          dataUpdatedAt: query.dataUpdatedAt,
          status: 'success',
        })
      })
    }
  } catch (error) {
    console.warn('Failed to restore query cache:', error)
  }
}