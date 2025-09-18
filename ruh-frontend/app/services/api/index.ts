/**
 * This Api class lets you define an API endpoint and methods to request
 * data and process it.
 *
 * See the [Backend API Integration](https://docs.infinite.red/ignite-cli/boilerplate/app/services/#backend-api-integration)
 * documentation for more details.
 */
import { ApisauceInstance, create } from "apisauce"

import Config from "@/config"

import type { 
  ApiConfig, 
  ChatInitResponse, 
  ChatMessage, 
  ChatResponse, 
  VerseChoiceMessage,
  WellnessCheckin, 
  WellnessResponse, 
  WellnessHistory, 
  VersesResponse 
} from "./types"
import { getGeneralApiProblem } from "./apiProblem"

/**
 * Configuring the apisauce instance.
 */
export const DEFAULT_API_CONFIG: ApiConfig = {
  url: Config.API_URL,
  timeout: 10000,
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
  async getWellnessHistory(limit: number = 10, offset: number = 0): Promise<{ kind: "ok"; data: WellnessHistory } | { kind: "error"; error: any }> {
    const response = await this.apisauce.get("/wellness", { limit, offset })

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

  // Verses API methods
  async getVerses(limit: number = 10, offset: number = 0): Promise<{ kind: "ok"; data: VersesResponse } | { kind: "error"; error: any }> {
    const response = await this.apisauce.get("/verses", { limit, offset })

    if (!response.ok) {
      const problem = getGeneralApiProblem(response)
      if (problem) return { kind: "error", error: problem }
    }

    return { kind: "ok", data: response.data as VersesResponse }
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
}

// Singleton instance of the API for convenience
export const api = new Api()
