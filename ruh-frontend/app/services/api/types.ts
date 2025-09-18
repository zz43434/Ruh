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
  user_id?: string
}

export interface VerseChoiceMessage {
  choice: string
  conversation_id: string
  message_id: string
  original_message: string
  user_id?: string
}

export interface ChatResponse {
  conversation_id: string
  relevant_verses: Array<{
    chapter: number
    verse: number
    text: string
    translation: string
    arabic_text?: string
    surah_name?: string
    verse_number?: number
  }>
  response: string
  sentiment: string
  themes: string[]
  intent?: string
  timestamp: string
  verse_offer?: {
    show_options: boolean
    message: string
    options: Array<{
      id: string
      text: string
      type: string
    }>
  }
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

// Wellness Analysis Types
export interface WellnessCategory {
  id: string
  name: string
  description: string
  keywords: string[]
  theme_words: string[]
}

export interface WellnessCategoriesResponse {
  categories: WellnessCategory[]
  total_count: number
}

export interface WellnessAnalysisRequest {
  user_input: string
}

export interface WellnessVerse {
  id: number
  surah_number: number
  verse_number: number
  arabic_text: string
  translation: string
  similarity_score: number
  surah_name: string
  context?: string
}

export interface WellnessAnalysisResult {
  user_input: string
  detected_categories: string[]
  verses: WellnessVerse[]
  guidance: string
  recommendations: string[]
  success: boolean
}

export interface CategoryVersesResponse {
  verses: WellnessVerse[]
  category_id: string
  total_count: number
}

export interface Verse {
  chapter: number
  verse: number
  text: string
  translation: string
  // Backend fields
  verse_number?: string
  arabic_text?: string
  surah_number?: number
  surah_name?: string
  ayah_count?: number
  revelation_place?: string
  context?: string
}

export interface Chapter {
  surah_number: number
  name: string
  ayah_count: number
  revelation_place: string
  verses_with_translation: number
  summary: string
}

export interface ChapterDetails {
  surah_number: number
  name: string
  ayah_count: number
  revelation_place: string
  summary: string
  verses: Verse[]
}

export interface ChaptersResponse {
  chapters: Chapter[]
  total_chapters: number
}

export interface ChapterDetailsResponse {
  chapter: ChapterDetails
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
