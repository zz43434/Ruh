import NetInfo, { NetInfoState } from '@react-native-community/netinfo'

export interface RetryConfig {
  maxRetries: number
  baseDelay: number
  maxDelay: number
  backoffMultiplier: number
  retryCondition?: (error: any) => boolean
  onRetry?: (attempt: number, error: any) => void
}

export const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxRetries: 3,
  baseDelay: 1000, // 1 second
  maxDelay: 30000, // 30 seconds
  backoffMultiplier: 2,
  retryCondition: (error) => {
    // Retry on network errors, 5xx server errors, and timeouts
    if (!error.response) return true // Network error
    const status = error.response.status
    return status >= 500 || status === 408 || status === 429 // Server error, timeout, or rate limit
  },
}

export class RetryableError extends Error {
  public readonly shouldRetry: boolean
  public readonly originalError: any

  constructor(message: string, originalError: any, shouldRetry: boolean = true) {
    super(message)
    this.name = 'RetryableError'
    this.originalError = originalError
    this.shouldRetry = shouldRetry
  }
}

export class NetworkManager {
  private static instance: NetworkManager
  private isConnected: boolean = true
  private connectionListeners: ((isConnected: boolean) => void)[] = []

  private constructor() {
    this.initializeNetworkListener()
  }

  public static getInstance(): NetworkManager {
    if (!NetworkManager.instance) {
      NetworkManager.instance = new NetworkManager()
    }
    return NetworkManager.instance
  }

  private initializeNetworkListener() {
    NetInfo.addEventListener((state: NetInfoState) => {
      const wasConnected = this.isConnected
      this.isConnected = state.isConnected ?? false
      
      if (wasConnected !== this.isConnected) {
        this.connectionListeners.forEach(listener => listener(this.isConnected))
      }
    })
  }

  public isNetworkConnected(): boolean {
    return this.isConnected
  }

  public onConnectionChange(listener: (isConnected: boolean) => void): () => void {
    this.connectionListeners.push(listener)
    
    // Return unsubscribe function
    return () => {
      const index = this.connectionListeners.indexOf(listener)
      if (index > -1) {
        this.connectionListeners.splice(index, 1)
      }
    }
  }

  public async waitForConnection(timeout: number = 30000): Promise<boolean> {
    if (this.isConnected) return true

    return new Promise((resolve) => {
      const timeoutId = setTimeout(() => {
        unsubscribe()
        resolve(false)
      }, timeout)

      const unsubscribe = this.onConnectionChange((isConnected) => {
        if (isConnected) {
          clearTimeout(timeoutId)
          unsubscribe()
          resolve(true)
        }
      })
    })
  }
}

export class RetryManager {
  private static calculateDelay(attempt: number, config: RetryConfig): number {
    const delay = config.baseDelay * Math.pow(config.backoffMultiplier, attempt - 1)
    return Math.min(delay, config.maxDelay)
  }

  private static async sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  public static async executeWithRetry<T>(
    operation: () => Promise<T>,
    config: RetryConfig = DEFAULT_RETRY_CONFIG
  ): Promise<T> {
    const networkManager = NetworkManager.getInstance()
    let lastError: any

    for (let attempt = 1; attempt <= config.maxRetries + 1; attempt++) {
      try {
        // Check network connectivity before attempting
        if (!networkManager.isNetworkConnected()) {
          console.log(`Attempt ${attempt}: No network connection, waiting...`)
          const connected = await networkManager.waitForConnection(10000)
          if (!connected) {
            throw new RetryableError('No network connection available', null, true)
          }
        }

        const result = await operation()
        
        // Success - reset any retry state if needed
        if (attempt > 1) {
          console.log(`Operation succeeded on attempt ${attempt}`)
        }
        
        return result
      } catch (error: unknown) {
        lastError = error
        
        // Check if we should retry this error
        const shouldRetry = config.retryCondition ? config.retryCondition(error) : true
        
        if (!shouldRetry || attempt > config.maxRetries) {
          console.error(`Operation failed after ${attempt} attempts:`, error)
          throw error
        }

        // Calculate delay for next attempt
        const delay = this.calculateDelay(attempt, config)
        
        const errorMessage = error instanceof Error ? error.message : String(error)
        console.log(`Attempt ${attempt} failed, retrying in ${delay}ms:`, errorMessage)
        
        // Call retry callback if provided
        if (config.onRetry) {
          config.onRetry(attempt, error)
        }

        // Wait before next attempt
        await this.sleep(delay)
      }
    }

    throw lastError
  }

  public static createRetryableOperation<T>(
    operation: () => Promise<T>,
    config?: Partial<RetryConfig>
  ) {
    const finalConfig = { ...DEFAULT_RETRY_CONFIG, ...config }
    
    return () => this.executeWithRetry(operation, finalConfig)
  }
}

// Specific retry configurations for different types of operations
export const RETRY_CONFIGS = {
  // Critical operations (chat, wellness data)
  critical: {
    maxRetries: 5,
    baseDelay: 1000,
    maxDelay: 60000,
    backoffMultiplier: 2,
    retryCondition: (error: any) => {
      if (!error.response) return true
      const status = error.response.status
      return status >= 500 || status === 408 || status === 429 || status === 503
    },
  } as RetryConfig,

  // Standard operations (verses, general API calls)
  standard: DEFAULT_RETRY_CONFIG,

  // Quick operations (search, autocomplete)
  quick: {
    maxRetries: 2,
    baseDelay: 500,
    maxDelay: 5000,
    backoffMultiplier: 2,
    retryCondition: (error: any) => {
      if (!error.response) return true
      const status = error.response.status
      return status >= 500 || status === 503
    },
  } as RetryConfig,

  // Background operations (sync, prefetch)
  background: {
    maxRetries: 10,
    baseDelay: 2000,
    maxDelay: 300000, // 5 minutes
    backoffMultiplier: 1.5,
    retryCondition: (error: any) => {
      if (!error.response) return true
      const status = error.response.status
      return status >= 500 || status === 408 || status === 429 || status === 503
    },
  } as RetryConfig,
}

// Helper functions for common retry patterns
export const withRetry = {
  critical: <T>(operation: () => Promise<T>) => 
    RetryManager.createRetryableOperation(operation, RETRY_CONFIGS.critical),
    
  standard: <T>(operation: () => Promise<T>) => 
    RetryManager.createRetryableOperation(operation, RETRY_CONFIGS.standard),
    
  quick: <T>(operation: () => Promise<T>) => 
    RetryManager.createRetryableOperation(operation, RETRY_CONFIGS.quick),
    
  background: <T>(operation: () => Promise<T>) => 
    RetryManager.createRetryableOperation(operation, RETRY_CONFIGS.background),
}

// Queue for managing failed operations that need to be retried later
export class RetryQueue {
  private static instance: RetryQueue
  private queue: Array<{
    id: string
    operation: () => Promise<any>
    config: RetryConfig
    attempts: number
    lastAttempt: number
    maxRetries: number
  }> = []
  private isProcessing: boolean = false

  private constructor() {
    // Start processing queue when network becomes available
    NetworkManager.getInstance().onConnectionChange((isConnected) => {
      if (isConnected && !this.isProcessing) {
        this.processQueue()
      }
    })
  }

  public static getInstance(): RetryQueue {
    if (!RetryQueue.instance) {
      RetryQueue.instance = new RetryQueue()
    }
    return RetryQueue.instance
  }

  public addToQueue(
    id: string,
    operation: () => Promise<any>,
    config: RetryConfig = DEFAULT_RETRY_CONFIG
  ) {
    // Remove existing operation with same ID
    this.queue = this.queue.filter(item => item.id !== id)
    
    // Add new operation
    this.queue.push({
      id,
      operation,
      config,
      attempts: 0,
      lastAttempt: Date.now(),
      maxRetries: config.maxRetries,
    })

    // Start processing if network is available
    if (NetworkManager.getInstance().isNetworkConnected() && !this.isProcessing) {
      this.processQueue()
    }
  }

  private async processQueue() {
    if (this.isProcessing || this.queue.length === 0) return
    
    this.isProcessing = true
    
    while (this.queue.length > 0) {
      const item = this.queue[0]
      
      try {
        await RetryManager.executeWithRetry(item.operation, item.config)
        // Success - remove from queue
        this.queue.shift()
      } catch (error) {
        // Failed - either retry later or remove if max attempts reached
        item.attempts++
        item.lastAttempt = Date.now()
        
        if (item.attempts >= item.maxRetries) {
          console.error(`Removing failed operation ${item.id} from retry queue after ${item.attempts} attempts`)
          this.queue.shift()
        } else {
          // Move to end of queue for later retry
          this.queue.push(this.queue.shift()!)
        }
      }
      
      // Small delay between operations
      await new Promise(resolve => setTimeout(resolve, 100))
    }
    
    this.isProcessing = false
  }

  public getQueueStatus() {
    return {
      queueLength: this.queue.length,
      isProcessing: this.isProcessing,
      items: this.queue.map(item => ({
        id: item.id,
        attempts: item.attempts,
        maxRetries: item.maxRetries,
        lastAttempt: item.lastAttempt,
      })),
    }
  }

  public clearQueue() {
    this.queue = []
  }
}