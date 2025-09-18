import { safeStorage } from './safeStorage'

// Storage keys
export const STORAGE_KEYS = {
  CHAT_MESSAGES: 'chat_messages',
  WELLNESS_CHECKINS: 'wellness_checkins',
  FAVORITE_VERSES: 'favorite_verses',
  USER_PREFERENCES: 'user_preferences',
  OFFLINE_QUEUE: 'offline_queue',
  LAST_SYNC: 'last_sync',
} as const

// Types for offline data
export interface OfflineChatMessage {
  id: string
  text: string
  sender: 'user' | 'bot'
  timestamp: string
  conversationId?: string
  synced: boolean
}

export interface OfflineWellnessCheckin {
  id: string
  mood: string
  energy_level: number
  stress_level: number
  notes?: string
  user_id: string
  timestamp: string
  synced: boolean
}

export interface OfflineVerse {
  chapter: number
  verse: number
  text: string
  translation: string
  arabic_text?: string
  surah_name?: string
  favorited_at: string
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system'
  language: string
  notifications_enabled: boolean
  offline_mode: boolean
  auto_sync: boolean
}

export interface OfflineQueueItem {
  id: string
  type: 'chat_message' | 'wellness_checkin' | 'verse_favorite'
  data: any
  timestamp: string
  retries: number
  max_retries: number
}

// Generic storage functions
export class OfflineStorage {
  // Get data from storage
  static async get<T>(key: string): Promise<T | null> {
    try {
      const data = await safeStorage.getItem(key)
      return data ? JSON.parse(data) : null
    } catch (error) {
      console.error(`Failed to get data for key ${key}:`, error)
      return null
    }
  }

  // Set data in storage
  static async set<T>(key: string, data: T): Promise<void> {
    try {
      await safeStorage.setItem(key, JSON.stringify(data))
    } catch (error) {
      console.error(`Failed to set data for key ${key}:`, error)
    }
  }

  // Remove data from storage
  static async remove(key: string): Promise<void> {
    try {
      await safeStorage.removeItem(key)
    } catch (error) {
      console.error(`Failed to remove data for key ${key}:`, error)
    }
  }

  // Clear all storage
  static async clear(): Promise<void> {
    try {
      await safeStorage.clear()
    } catch (error) {
      console.error('Failed to clear storage:', error)
    }
  }

  // Get storage info
  static async getStorageInfo(): Promise<{
    keys: readonly string[]
    totalSize: number
  }> {
    try {
      const keys = await safeStorage.getAllKeys()
      let totalSize = 0
      
      for (const key of keys) {
        const value = await safeStorage.getItem(key)
        if (value) {
          totalSize += value.length
        }
      }
      
      return { keys, totalSize }
    } catch (error) {
      console.error('Failed to get storage info:', error)
      return { keys: [], totalSize: 0 }
    }
  }
}

// Chat messages storage
export class ChatStorage {
  static async getMessages(conversationId?: string): Promise<OfflineChatMessage[]> {
    const messages = await OfflineStorage.get<OfflineChatMessage[]>(STORAGE_KEYS.CHAT_MESSAGES) || []
    return conversationId 
      ? messages.filter(msg => msg.conversationId === conversationId)
      : messages
  }

  static async addMessage(message: OfflineChatMessage): Promise<void> {
    const messages = await this.getMessages()
    messages.push(message)
    await OfflineStorage.set(STORAGE_KEYS.CHAT_MESSAGES, messages)
  }

  static async updateMessage(id: string, updates: Partial<OfflineChatMessage>): Promise<boolean> {
    const messages = await this.getMessages()
    const index = messages.findIndex(msg => msg.id === id)
    if (index !== -1) {
      messages[index] = { ...messages[index], ...updates }
      await OfflineStorage.set(STORAGE_KEYS.CHAT_MESSAGES, messages)
      return true
    }
    return false
  }

  static async removeMessage(id: string): Promise<void> {
    const messages = await this.getMessages()
    const filteredMessages = messages.filter(msg => msg.id !== id)
    await OfflineStorage.set(STORAGE_KEYS.CHAT_MESSAGES, filteredMessages)
  }

  static async getUnsyncedMessages(): Promise<OfflineChatMessage[]> {
    const messages = await this.getMessages()
    return messages.filter(msg => !msg.synced)
  }

  static async markAsSynced(ids: string[]): Promise<void> {
    const messages = await this.getMessages()
    const updatedMessages = messages.map(msg => 
      ids.includes(msg.id) ? { ...msg, synced: true } : msg
    )
    await OfflineStorage.set(STORAGE_KEYS.CHAT_MESSAGES, updatedMessages)
  }
}

// Wellness checkins storage
export class WellnessStorage {
  static async getCheckins(): Promise<OfflineWellnessCheckin[]> {
    return await OfflineStorage.get<OfflineWellnessCheckin[]>(STORAGE_KEYS.WELLNESS_CHECKINS) || []
  }

  static async addCheckin(checkin: OfflineWellnessCheckin): Promise<void> {
    const checkins = await this.getCheckins()
    checkins.push(checkin)
    await OfflineStorage.set(STORAGE_KEYS.WELLNESS_CHECKINS, checkins)
  }

  static async updateCheckin(id: string, updates: Partial<OfflineWellnessCheckin>): Promise<boolean> {
    const checkins = await this.getCheckins()
    const index = checkins.findIndex(checkin => checkin.id === id)
    if (index !== -1) {
      checkins[index] = { ...checkins[index], ...updates }
      await OfflineStorage.set(STORAGE_KEYS.WELLNESS_CHECKINS, checkins)
      return true
    }
    return false
  }

  static async getUnsyncedCheckins(): Promise<OfflineWellnessCheckin[]> {
    const checkins = await this.getCheckins()
    return checkins.filter(checkin => !checkin.synced)
  }

  static async markAsSynced(ids: string[]): Promise<void> {
    const checkins = await this.getCheckins()
    const updatedCheckins = checkins.map(checkin => 
      ids.includes(checkin.id) ? { ...checkin, synced: true } : checkin
    )
    await OfflineStorage.set(STORAGE_KEYS.WELLNESS_CHECKINS, updatedCheckins)
  }
}

// Favorite verses storage
export class VersesStorage {
  static async getFavoriteVerses(): Promise<OfflineVerse[]> {
    return await OfflineStorage.get<OfflineVerse[]>(STORAGE_KEYS.FAVORITE_VERSES) || []
  }

  static async addFavoriteVerse(verse: OfflineVerse): Promise<void> {
    const favorites = await this.getFavoriteVerses()
    // Check if already favorited
    const exists = favorites.some(fav => 
      fav.chapter === verse.chapter && fav.verse === verse.verse
    )
    if (!exists) {
      favorites.push(verse)
      await OfflineStorage.set(STORAGE_KEYS.FAVORITE_VERSES, favorites)
    }
  }

  static async removeFavoriteVerse(chapter: number, verse: number): Promise<void> {
    const favorites = await this.getFavoriteVerses()
    const filteredFavorites = favorites.filter(fav => 
      !(fav.chapter === chapter && fav.verse === verse)
    )
    await OfflineStorage.set(STORAGE_KEYS.FAVORITE_VERSES, filteredFavorites)
  }

  static async isFavorite(chapter: number, verse: number): Promise<boolean> {
    const favorites = await this.getFavoriteVerses()
    return favorites.some(fav => fav.chapter === chapter && fav.verse === verse)
  }
}

// User preferences storage
export class PreferencesStorage {
  static async getPreferences(): Promise<UserPreferences> {
    const defaultPreferences: UserPreferences = {
      theme: 'system',
      language: 'en',
      notifications_enabled: true,
      offline_mode: false,
      auto_sync: true,
    }
    
    const stored = await OfflineStorage.get<UserPreferences>(STORAGE_KEYS.USER_PREFERENCES)
    return { ...defaultPreferences, ...stored }
  }

  static async updatePreferences(updates: Partial<UserPreferences>): Promise<void> {
    const current = await this.getPreferences()
    const updated = { ...current, ...updates }
    await OfflineStorage.set(STORAGE_KEYS.USER_PREFERENCES, updated)
  }
}

// Offline queue for failed requests
export class OfflineQueue {
  static async getQueue(): Promise<OfflineQueueItem[]> {
    return await OfflineStorage.get<OfflineQueueItem[]>(STORAGE_KEYS.OFFLINE_QUEUE) || []
  }

  static async addToQueue(item: Omit<OfflineQueueItem, 'id' | 'timestamp' | 'retries'>): Promise<void> {
    const queue = await this.getQueue()
    const queueItem: OfflineQueueItem = {
      ...item,
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
      retries: 0,
    }
    queue.push(queueItem)
    await OfflineStorage.set(STORAGE_KEYS.OFFLINE_QUEUE, queue)
  }

  static async removeFromQueue(id: string): Promise<void> {
    const queue = await this.getQueue()
    const filteredQueue = queue.filter(item => item.id !== id)
    await OfflineStorage.set(STORAGE_KEYS.OFFLINE_QUEUE, filteredQueue)
  }

  static async incrementRetries(id: string): Promise<boolean> {
    const queue = await this.getQueue()
    const index = queue.findIndex(item => item.id === id)
    if (index !== -1) {
      queue[index].retries += 1
      await OfflineStorage.set(STORAGE_KEYS.OFFLINE_QUEUE, queue)
      return true
    }
    return false
  }

  static async getRetryableItems(): Promise<OfflineQueueItem[]> {
    const queue = await this.getQueue()
    return queue.filter(item => item.retries < item.max_retries)
  }

  static async clearQueue(): Promise<void> {
    await OfflineStorage.set(STORAGE_KEYS.OFFLINE_QUEUE, [])
  }
}

// Sync status tracking
export class SyncStorage {
  static async getLastSync(): Promise<string | null> {
    return await OfflineStorage.get<string>(STORAGE_KEYS.LAST_SYNC)
  }

  static async setLastSync(timestamp: string = new Date().toISOString()): Promise<void> {
    await OfflineStorage.set(STORAGE_KEYS.LAST_SYNC, timestamp)
  }

  static async needsSync(maxAge: number = 5 * 60 * 1000): Promise<boolean> {
    const lastSync = await this.getLastSync()
    if (!lastSync) return true
    
    const lastSyncTime = new Date(lastSync).getTime()
    const now = Date.now()
    
    return (now - lastSyncTime) > maxAge
  }
}