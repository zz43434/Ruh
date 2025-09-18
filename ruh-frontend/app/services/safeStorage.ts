import AsyncStorage from '@react-native-async-storage/async-storage'

// In-memory fallback storage for when AsyncStorage is null
class MemoryStorage {
  private storage: Map<string, string> = new Map()

  async getItem(key: string): Promise<string | null> {
    return this.storage.get(key) || null
  }

  async setItem(key: string, value: string): Promise<void> {
    this.storage.set(key, value)
  }

  async removeItem(key: string): Promise<void> {
    this.storage.delete(key)
  }

  async clear(): Promise<void> {
    this.storage.clear()
  }

  async getAllKeys(): Promise<readonly string[]> {
    return Array.from(this.storage.keys())
  }

  async multiGet(keys: readonly string[]): Promise<readonly [string, string | null][]> {
    return keys.map(key => [key, this.storage.get(key) || null])
  }

  async multiSet(keyValuePairs: readonly [string, string][]): Promise<void> {
    keyValuePairs.forEach(([key, value]) => {
      this.storage.set(key, value)
    })
  }

  async multiRemove(keys: readonly string[]): Promise<void> {
    keys.forEach(key => {
      this.storage.delete(key)
    })
  }
}

// Safe storage wrapper
class SafeStorage {
  private memoryStorage = new MemoryStorage()
  private isAsyncStorageAvailable: boolean | null = null

  private async checkAsyncStorageAvailability(): Promise<boolean> {
    if (this.isAsyncStorageAvailable !== null) {
      return this.isAsyncStorageAvailable
    }

    try {
      // Test if AsyncStorage is available by trying to set and get a test value
      const testKey = '__asyncstorage_test__'
      const testValue = 'test'
      
      await AsyncStorage.setItem(testKey, testValue)
      const retrievedValue = await AsyncStorage.getItem(testKey)
      await AsyncStorage.removeItem(testKey)
      
      this.isAsyncStorageAvailable = retrievedValue === testValue
      
      if (this.isAsyncStorageAvailable) {
        console.log('✅ AsyncStorage is available and working')
      } else {
        console.warn('⚠️ AsyncStorage test failed, using memory storage fallback')
      }
      
      return this.isAsyncStorageAvailable
    } catch (error) {
      console.warn('⚠️ AsyncStorage is not available, using memory storage fallback:', error)
      this.isAsyncStorageAvailable = false
      return false
    }
  }

  async getItem(key: string): Promise<string | null> {
    try {
      const isAvailable = await this.checkAsyncStorageAvailability()
      if (isAvailable) {
        return await AsyncStorage.getItem(key)
      } else {
        return await this.memoryStorage.getItem(key)
      }
    } catch (error) {
      console.warn(`SafeStorage.getItem failed for key "${key}":`, error)
      return await this.memoryStorage.getItem(key)
    }
  }

  async setItem(key: string, value: string): Promise<void> {
    try {
      const isAvailable = await this.checkAsyncStorageAvailability()
      if (isAvailable) {
        await AsyncStorage.setItem(key, value)
      } else {
        await this.memoryStorage.setItem(key, value)
      }
    } catch (error) {
      console.warn(`SafeStorage.setItem failed for key "${key}":`, error)
      await this.memoryStorage.setItem(key, value)
    }
  }

  async removeItem(key: string): Promise<void> {
    try {
      const isAvailable = await this.checkAsyncStorageAvailability()
      if (isAvailable) {
        await AsyncStorage.removeItem(key)
      } else {
        await this.memoryStorage.removeItem(key)
      }
    } catch (error) {
      console.warn(`SafeStorage.removeItem failed for key "${key}":`, error)
      await this.memoryStorage.removeItem(key)
    }
  }

  async clear(): Promise<void> {
    try {
      const isAvailable = await this.checkAsyncStorageAvailability()
      if (isAvailable) {
        await AsyncStorage.clear()
      } else {
        await this.memoryStorage.clear()
      }
    } catch (error) {
      console.warn('SafeStorage.clear failed:', error)
      await this.memoryStorage.clear()
    }
  }

  async getAllKeys(): Promise<readonly string[]> {
    try {
      const isAvailable = await this.checkAsyncStorageAvailability()
      if (isAvailable) {
        return await AsyncStorage.getAllKeys()
      } else {
        return await this.memoryStorage.getAllKeys()
      }
    } catch (error) {
      console.warn('SafeStorage.getAllKeys failed:', error)
      return await this.memoryStorage.getAllKeys()
    }
  }

  async multiGet(keys: readonly string[]): Promise<readonly [string, string | null][]> {
    try {
      const isAvailable = await this.checkAsyncStorageAvailability()
      if (isAvailable) {
        return await AsyncStorage.multiGet(keys)
      } else {
        return await this.memoryStorage.multiGet(keys)
      }
    } catch (error) {
      console.warn('SafeStorage.multiGet failed:', error)
      return await this.memoryStorage.multiGet(keys)
    }
  }

  async multiSet(keyValuePairs: readonly [string, string][]): Promise<void> {
    try {
      const isAvailable = await this.checkAsyncStorageAvailability()
      if (isAvailable) {
        await AsyncStorage.multiSet(keyValuePairs)
      } else {
        await this.memoryStorage.multiSet(keyValuePairs)
      }
    } catch (error) {
      console.warn('SafeStorage.multiSet failed:', error)
      await this.memoryStorage.multiSet(keyValuePairs)
    }
  }

  async multiRemove(keys: readonly string[]): Promise<void> {
    try {
      const isAvailable = await this.checkAsyncStorageAvailability()
      if (isAvailable) {
        await AsyncStorage.multiRemove(keys)
      } else {
        await this.memoryStorage.multiRemove(keys)
      }
    } catch (error) {
      console.warn('SafeStorage.multiRemove failed:', error)
      await this.memoryStorage.multiRemove(keys)
    }
  }

  // Utility method to check if we're using persistent storage
  async isPersistent(): Promise<boolean> {
    return await this.checkAsyncStorageAvailability()
  }

  // Method to force re-check AsyncStorage availability
  recheckAvailability(): void {
    this.isAsyncStorageAvailable = null
  }
}

// Export singleton instance
export const safeStorage = new SafeStorage()

// Export the class for testing purposes
export { SafeStorage, MemoryStorage }

// Export a function to check storage status
export async function getStorageStatus() {
  const isPersistent = await safeStorage.isPersistent()
  return {
    isPersistent,
    storageType: isPersistent ? 'AsyncStorage' : 'MemoryStorage',
    message: isPersistent 
      ? 'Using persistent AsyncStorage' 
      : 'Using temporary memory storage (data will be lost on app restart)'
  }
}