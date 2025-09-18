/**
 * These types indicate the shape of the data you expect to receive from your
 * API endpoint, assuming it's a JSON object like we have.
 */
export interface EpisodeItem {
  title: string
  pubDate: string
  link: string
  guid: string
  author: string
  thumbnail: string
  description: string
  content: string
  enclosure: {
    link: string
    type: string
    length: number
    duration: number
    rating: { scheme: string; value: string }
  }
  categories: string[]
}

export interface ApiFeedResponse {
  status: string
  feed: {
    url: string
    title: string
    link: string
    author: string
    description: string
    image: string
  }
  items: EpisodeItem[]
}

// Ruh App API Types
export interface ChatInitResponse {
  conversation_id: string
  response: string
  timestamp: string
}

export interface ChatMessage {
  message: string
  conversation_id: string
}

export interface ChatResponse {
  conversation_id: string
  relevant_verses: Array<{
    chapter: number
    verse: number
    text: string
    translation: string
  }>
  response: string
  sentiment: string
  timestamp: string
}

export interface WellnessCheckin {
  mood: string
  energy_level: number
  stress_level: number
  notes?: string
  user_id: string
}

export interface WellnessResponse {
  status: string
  message: string
  guidance?: {
    verses: Array<{
      chapter: number
      verse: number
      text: string
      translation: string
    }>
    recommendations: string[]
  }
  timestamp: string
}

export interface WellnessHistory {
  total_entries: number
  user_id: string
  wellness_history: Array<{
    id: number
    mood: string
    energy_level: number
    stress_level: number
    notes: string
    timestamp: string
  }>
}

export interface Verse {
  chapter: number
  verse: number
  text: string
  translation: string
}

export interface VersesResponse {
  verses: Verse[]
  total_count: number
}

/**
 * The options used to configure apisauce.
 */
export interface ApiConfig {
  /**
   * The URL of the api.
   */
  url: string

  /**
   * Milliseconds before we timeout the request.
   */
  timeout: number
}
