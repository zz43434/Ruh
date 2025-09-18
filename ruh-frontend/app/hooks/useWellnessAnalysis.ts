import { useMutation, useQuery } from "@tanstack/react-query"
import { api } from "@/services/api"
import type { 
  WellnessCategory, 
  WellnessCategoriesResponse, 
  WellnessAnalysisRequest, 
  WellnessAnalysisResult,
  CategoryVersesResponse 
} from "@/services/api/types"

// Query keys for wellness analysis
export const wellnessAnalysisKeys = {
  all: ['wellness-analysis'] as const,
  categories: () => [...wellnessAnalysisKeys.all, 'categories'] as const,
  categoryVerses: (category: string) => [...wellnessAnalysisKeys.all, 'category-verses', category] as const,
}

/**
 * Hook to fetch wellness categories
 */
export const useWellnessCategories = () => {
  return useQuery({
    queryKey: wellnessAnalysisKeys.categories(),
    queryFn: async (): Promise<WellnessCategory[]> => {
      const response = await api.getWellnessCategories()
      if (response.kind === "ok") {
        return response.data.categories
      }
      throw new Error(response.kind)
    },
    staleTime: 1000 * 60 * 30, // 30 minutes - categories don't change often
    gcTime: 1000 * 60 * 60, // 1 hour
  })
}

/**
 * Hook to analyze wellness text and get recommendations
 */
export const useWellnessAnalysis = () => {
  return useMutation({
    mutationFn: async (request: WellnessAnalysisRequest): Promise<WellnessAnalysisResult> => {
      const response = await api.analyzeWellness(request)
      if (response.kind === "ok") {
        return response.data
      }
      throw new Error(response.kind)
    },
    onError: (error) => {
      console.error('Wellness analysis failed:', error)
    },
  })
}

/**
 * Hook to fetch verses for a specific wellness category
 */
export const useCategoryVerses = (category: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: wellnessAnalysisKeys.categoryVerses(category),
    queryFn: async (): Promise<CategoryVersesResponse> => {
      const response = await api.getCategoryVerses(category)
      if (response.kind === "ok") {
        return response.data
      }
      throw new Error(response.kind)
    },
    enabled: enabled && !!category,
    staleTime: 1000 * 60 * 15, // 15 minutes
    gcTime: 1000 * 60 * 30, // 30 minutes
  })
}

/**
 * Combined hook that provides all wellness analysis functionality
 */
export const useWellnessAnalysisFlow = () => {
  const categoriesQuery = useWellnessCategories()
  const analysisMutation = useWellnessAnalysis()

  return {
    // Categories
    categories: categoriesQuery.data,
    categoriesLoading: categoriesQuery.isLoading,
    categoriesError: categoriesQuery.error,
    
    // Analysis
    analyzeWellness: analysisMutation.mutate,
    analysisResult: analysisMutation.data,
    analysisLoading: analysisMutation.isPending,
    analysisError: analysisMutation.error,
    
    // Reset analysis state
    resetAnalysis: analysisMutation.reset,
  }
}