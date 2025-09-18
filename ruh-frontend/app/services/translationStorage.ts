import { safeStorage } from './safeStorage'

export interface TranslationData {
  [chapterNumber: number]: {
    [verseIndex: number]: string
  }
}

class TranslationStorage {
  private static instance: TranslationStorage
  private translations: TranslationData = {}
  private storageKey = 'verse-translations'
  private initialized = false

  static getInstance(): TranslationStorage {
    if (!TranslationStorage.instance) {
      TranslationStorage.instance = new TranslationStorage()
    }
    return TranslationStorage.instance
  }

  async initialize(): Promise<void> {
    if (this.initialized) return

    try {
      const stored = await safeStorage.getItem(this.storageKey)
      if (stored) {
        this.translations = JSON.parse(stored)
      }
      this.initialized = true
    } catch (error) {
      console.error('Failed to load translations from storage:', error)
      this.translations = {}
      this.initialized = true
    }
  }

  async saveTranslation(chapterNumber: number, verseIndex: number, translation: string): Promise<void> {
    await this.initialize()
    
    if (!this.translations[chapterNumber]) {
      this.translations[chapterNumber] = {}
    }
    
    this.translations[chapterNumber][verseIndex] = translation
    
    try {
      await safeStorage.setItem(this.storageKey, JSON.stringify(this.translations))
    } catch (error) {
      console.error('Failed to save translation to storage:', error)
    }
  }

  async getTranslation(chapterNumber: number, verseIndex: number): Promise<string | null> {
    await this.initialize()
    
    return this.translations[chapterNumber]?.[verseIndex] || null
  }

  async getChapterTranslations(chapterNumber: number): Promise<Map<number, string>> {
    await this.initialize()
    
    const chapterTranslations = this.translations[chapterNumber] || {}
    return new Map(Object.entries(chapterTranslations).map(([index, translation]) => [parseInt(index), translation]))
  }

  async saveChapterTranslations(chapterNumber: number, translations: Map<number, string>): Promise<void> {
    await this.initialize()
    
    if (!this.translations[chapterNumber]) {
      this.translations[chapterNumber] = {}
    }
    
    translations.forEach((translation, verseIndex) => {
      this.translations[chapterNumber][verseIndex] = translation
    })
    
    try {
      await safeStorage.setItem(this.storageKey, JSON.stringify(this.translations))
    } catch (error) {
      console.error('Failed to save chapter translations to storage:', error)
    }
  }

  async clearChapterTranslations(chapterNumber: number): Promise<void> {
    await this.initialize()
    
    delete this.translations[chapterNumber]
    
    try {
      await safeStorage.setItem(this.storageKey, JSON.stringify(this.translations))
    } catch (error) {
      console.error('Failed to clear chapter translations from storage:', error)
    }
  }

  async clearAllTranslations(): Promise<void> {
    this.translations = {}
    
    try {
      await safeStorage.removeItem(this.storageKey)
    } catch (error) {
      console.error('Failed to clear all translations from storage:', error)
    }
  }

  async getStorageStats(): Promise<{ totalChapters: number; totalTranslations: number }> {
    await this.initialize()
    
    const totalChapters = Object.keys(this.translations).length
    const totalTranslations = Object.values(this.translations).reduce(
      (total, chapterTranslations) => total + Object.keys(chapterTranslations).length,
      0
    )
    
    return { totalChapters, totalTranslations }
  }
}

export const translationStorage = TranslationStorage.getInstance()