import { useQuery, useInfiniteQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/services/api'
import type { VersesResponse, Verse } from '@/services/api/types'

// Query keys for verses-related queries
export const versesKeys = {
  all: ['verses'] as const,
  lists: () => [...versesKeys.all, 'list'] as const,
  list: (limit: number, offset: number) => [...versesKeys.lists(), { limit, offset }] as const,
  search: (query: string) => [...versesKeys.all, 'search', query] as const,
  random: () => [...versesKeys.all, 'random'] as const,
}

// Get verses with pagination
export function useVerses(limit: number = 10, offset: number = 0) {
  return useQuery({
    queryKey: versesKeys.list(limit, offset),
    queryFn: async () => {
      const response = await api.getVerses(limit, offset)
      if (response.kind === 'error') {
        throw new Error('Failed to fetch verses')
      }
      return response.data
    },
    staleTime: 10 * 60 * 1000, // 10 minutes - verses don't change often
    gcTime: 30 * 60 * 1000, // 30 minutes cache time
  })
}

// Infinite query for verses with pagination
export function useInfiniteVerses(limit: number = 10) {
  return useInfiniteQuery({
    queryKey: [...versesKeys.lists(), 'infinite', limit],
    queryFn: async ({ pageParam = 0 }) => {
      const response = await api.getVerses(limit, pageParam)
      if (response.kind === 'error') {
        throw new Error('Failed to fetch verses')
      }
      return response.data
    },
    getNextPageParam: (lastPage, allPages) => {
      const totalFetched = allPages.reduce((sum, page) => sum + page.verses.length, 0)
      return totalFetched < lastPage.total_count ? totalFetched : undefined
    },
    initialPageParam: 0,
    staleTime: 10 * 60 * 1000,
    gcTime: 30 * 60 * 1000,
  })
}

// Search verses
export function useSearchVerses(query: string, enabled: boolean = true) {
  return useQuery({
    queryKey: versesKeys.search(query),
    queryFn: async () => {
      if (!query.trim()) {
        return { verses: [], total_count: 0 }
      }
      const response = await api.searchVerses(query)
      if (response.kind === 'error') {
        throw new Error('Failed to search verses')
      }
      return response.data
    },
    enabled: enabled && !!query.trim(),
    staleTime: 5 * 60 * 1000, // 5 minutes for search results
    gcTime: 15 * 60 * 1000, // 15 minutes cache time
  })
}

// Get random verse
export function useRandomVerse() {
  return useQuery({
    queryKey: versesKeys.random(),
    queryFn: async () => {
      const response = await api.getRandomVerse()
      if (response.kind === 'error') {
        throw new Error('Failed to fetch random verse')
      }
      return response.data
    },
    staleTime: 0, // Always fresh for random verses
    gcTime: 5 * 60 * 1000, // 5 minutes cache time
  })
}

// Prefetch verses for better UX
export function usePrefetchVerses() {
  const queryClient = useQueryClient()

  const prefetchNextPage = (currentOffset: number, limit: number = 10) => {
    queryClient.prefetchQuery({
      queryKey: versesKeys.list(limit, currentOffset + limit),
      queryFn: async () => {
        const response = await api.getVerses(limit, currentOffset + limit)
        if (response.kind === 'error') {
          throw new Error('Failed to prefetch verses')
        }
        return response.data
      },
      staleTime: 10 * 60 * 1000,
    })
  }

  const prefetchRandomVerse = () => {
    queryClient.prefetchQuery({
      queryKey: versesKeys.random(),
      queryFn: async () => {
        const response = await api.getRandomVerse()
        if (response.kind === 'error') {
          throw new Error('Failed to prefetch random verse')
        }
        return response.data
      },
      staleTime: 0,
    })
  }

  return {
    prefetchNextPage,
    prefetchRandomVerse,
  }
}

// Combined hook for verses functionality
export function useVersesManager() {
  const queryClient = useQueryClient()
  const prefetch = usePrefetchVerses()

  const invalidateVerses = () => {
    queryClient.invalidateQueries({ queryKey: versesKeys.all })
  }

  const clearVersesCache = () => {
    queryClient.removeQueries({ queryKey: versesKeys.all })
  }

  return {
    invalidateVerses,
    clearVersesCache,
    ...prefetch,
  }
}