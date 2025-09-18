/**
 * This Api class lets you define an API endpoint and methods to request
 * data and process it.
 *
 * See the [Backend API Integration](https://docs.infinite.red/ignite-cli/boilerplate/app/services/#backend-api-integration)
 * documentation for more details.
 */
import { ApiResponse, ApisauceInstance, create } from "apisauce"
import Config from "../../config"
import { GeneralApiProblem, getGeneralApiProblem } from "./apiProblem"
import type { 
  ApiConfig, 
  ApiFeedResponse,
  ChatInitResponse, 
  ChatMessage, 
  ChatResponse, 
  VerseChoiceMessage,
  WellnessCheckin, 
  WellnessResponse, 
  WellnessHistory, 
  VersesResponse,
  Chapter,
  ChapterDetails,
  ChaptersResponse,
  ChapterDetailsResponse
} from "./types"

/**
 * Configuring the apisauce instance.
 */
export const DEFAULT_API_CONFIG: ApiConfig = {
  url: Config.API_URL,
  timeout: 30000,
}

/**
 * Manages all requests to the API. You can use this class to build out
 * various requests that you need to call from your backend API.
 */
export class Api {
  apisauce: ApisauceInstance
  config: ApiConfig

  /**
   * Set up our API instance. Keep this lightweight!
   */
  constructor(config: ApiConfig = DEFAULT_API_CONFIG) {
    this.config = config
    this.apisauce = create({
      baseURL: this.config.url,
      timeout: this.config.timeout,
      headers: {
        Accept: "application/json",
      },
    })

    // Add request/response interceptors for debugging
    this.apisauce.addRequestTransform((request) => {
      console.log(`🚀 API Request: ${request.method?.toUpperCase()} ${request.url}`)
      console.log('📤 Request data:', request.data)
      console.log('🔧 Request headers:', request.headers)
    })

    this.apisauce.addResponseTransform((response) => {
      console.log(`📥 API Response: ${response.status} ${response.config?.url}`)
      if (!response.ok) {
        console.error('❌ API Error:', {
          status: response.status,
          problem: response.problem,
          data: response.data,
          originalError: response.originalError
        })
      } else {
        console.log('✅ API Success:', response.data)
      }
    })
  }

  // Chat API methods
  async initChat(): Promise<{ kind: "ok"; data: ChatInitResponse } | { kind: "error"; error: any }> {
    const response = await this.apisauce.get("/chat/init")

    if (!response.ok) {
      const problem = getGeneralApiProblem(response)
      if (problem) return { kind: "error", error: problem }
    }

    return { kind: "ok", data: response.data as ChatInitResponse }
  }

  async sendChatMessage(message: ChatMessage): Promise<{ kind: "ok"; data: ChatResponse } | { kind: "error"; error: any }> {
    const response = await this.apisauce.post("/chat", message)

    if (!response.ok) {
      const problem = getGeneralApiProblem(response)
      if (problem) return { kind: "error", error: problem }
    }

    return { kind: "ok", data: response.data as ChatResponse }
  }

  async sendVerseChoice(verseChoice: VerseChoiceMessage): Promise<{ kind: "ok"; data: ChatResponse } | { kind: "error"; error: any }> {
    const response = await this.apisauce.post("/chat/verse-choice", verseChoice)

    if (!response.ok) {
      const problem = getGeneralApiProblem(response)
      if (problem) return { kind: "error", error: problem }
    }

    return { kind: "ok", data: response.data as ChatResponse }
  }

  // Wellness API methods
  async getWellnessHistory(limit: number = 20, offset: number = 0, userId?: string): Promise<{ kind: "ok"; data: WellnessHistory } | { kind: "error"; error: any }> {
    const params: any = { limit, offset }
    
    if (userId) {
      params.user_id = userId
    }
    
    const response = await this.apisauce.get("/wellness", params)

    if (!response.ok) {
      const problem = getGeneralApiProblem(response)
      if (problem) return { kind: "error", error: problem }
    }

    return { kind: "ok", data: response.data as WellnessHistory }
  }

  async submitWellnessCheckin(checkin: WellnessCheckin): Promise<{ kind: "ok"; data: WellnessResponse } | { kind: "error"; error: any }> {
    const response = await this.apisauce.post("/wellness/checkin", checkin)

    if (!response.ok) {
      const problem = getGeneralApiProblem(response)
      if (problem) return { kind: "error", error: problem }
    }

    return { kind: "ok", data: response.data as WellnessResponse }
  }

  // Chapters API methods
  async getChapters(): Promise<{ kind: "ok"; chapters: Chapter[] } | GeneralApiProblem> {
    // make the api call
    const response: ApiResponse<ChaptersResponse> = await this.apisauce.get(`/chapters`)

    // the typical ways to die when calling an api
    if (!response.ok) {
      const problem = getGeneralApiProblem(response)
      if (problem) return problem
    }

    // transform the data into the format we are expecting
    try {
      const rawData = response.data
      
      // This is where we transform the data into the shape the app expects.
      const chapters: Chapter[] = rawData?.chapters || []
      return { kind: "ok", chapters }
    } catch (e) {
      if (__DEV__ && e instanceof Error) {
        console.error(`Bad data: ${e.message}\n${response.data}`, e.stack)
      }
      return { kind: "bad-data" }
    }
  }

  async searchChapters(query: string, maxResults: number = 10): Promise<{ kind: "ok"; chapters: Chapter[] } | GeneralApiProblem> {
    // make the api call
    const response: ApiResponse<ChaptersResponse> = await this.apisauce.get(`/chapters/search`, {
      theme: query,
      max_results: maxResults
    })

    // the typical ways to die when calling an api
    if (!response.ok) {
      const problem = getGeneralApiProblem(response)
      if (problem) return problem
    }

    // transform the data into the format we are expecting
    try {
      const rawData = response.data
      
      // This is where we transform the data into the shape the app expects.
      const chapters: Chapter[] = rawData?.chapters || []
      return { kind: "ok", chapters }
    } catch (e) {
      if (__DEV__ && e instanceof Error) {
        console.error(`Bad data: ${e.message}\n${response.data}`, e.stack)
      }
      return { kind: "bad-data" }
    }
  }

  async getChapterDetails(surahNumber: number): Promise<{ kind: "ok"; chapter: ChapterDetails } | GeneralApiProblem> {
    // make the api call
    const response: ApiResponse<ChapterDetailsResponse> = await this.apisauce.get(`/chapters/${surahNumber}`)

    // the typical ways to die when calling an api
    if (!response.ok) {
      const problem = getGeneralApiProblem(response)
      if (problem) return problem
    }

    // transform the data into the format we are expecting
    try {
      const rawData = response.data
      
      // This is where we transform the data into the shape the app expects.
      const chapter: ChapterDetails = rawData?.chapter
      if (!chapter) {
        return { kind: "bad-data" }
      }
      return { kind: "ok", chapter }
    } catch (e) {
      if (__DEV__ && e instanceof Error) {
        console.error(`Bad data: ${e.message}\n${response.data}`, e.stack)
      }
      return { kind: "bad-data" }
    }
  }

  // Verses API methods
  async getVerses(page: number = 1, limit: number = 20): Promise<{ kind: "ok"; verses: any[] } | GeneralApiProblem> {
    const response = await this.apisauce.get("/verses", { page, limit })

    if (!response.ok) {
      const problem = getGeneralApiProblem(response)
      if (problem) return problem
    }

    return { kind: "ok", verses: response.data as any[] }
  }

  async searchVerses(query: string): Promise<{ kind: "ok"; data: VersesResponse } | { kind: "error"; error: any }> {
    const response = await this.apisauce.post("/verses/search", { query })

    if (!response.ok) {
      const problem = getGeneralApiProblem(response)
      if (problem) return { kind: "error", error: problem }
    }

    return { kind: "ok", data: response.data as VersesResponse }
  }

  async getRandomVerse(): Promise<{ kind: "ok"; data: any } | { kind: "error"; error: any }> {
    const response = await this.apisauce.get("/verses/random")

    if (!response.ok) {
      const problem = getGeneralApiProblem(response)
      if (problem) return { kind: "error", error: problem }
    }

    return { kind: "ok", data: response.data }
  }

  // Translation API methods
  async translateVerse(arabicText: string): Promise<{ kind: "ok"; translation: string } | { kind: "error"; error: any }> {
    const response = await this.apisauce.post("/translate", { arabic_text: arabicText })

    if (!response.ok) {
      const problem = getGeneralApiProblem(response)
      if (problem) return { kind: "error", error: problem }
    }

    const data = response.data as { translation: string; status: string }
    return { kind: "ok", translation: data.translation }
  }
}

// Singleton instance of the API for convenience
export const api = new Api()
