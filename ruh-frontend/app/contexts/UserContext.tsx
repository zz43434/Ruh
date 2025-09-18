import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { safeStorage } from '@/services/safeStorage'

interface User {
  id: string
  name?: string
  email?: string
  createdAt: string
}

interface UserContextType {
  user: User | null
  isLoading: boolean
  setUser: (user: User | null) => void
  generateGuestUser: () => Promise<User>
  clearUser: () => Promise<void>
}

const UserContext = createContext<UserContextType | undefined>(undefined)

const STORAGE_KEY = 'ruh_user'

// Generate a unique guest user ID
const generateGuestUserId = (): string => {
  const timestamp = Date.now()
  const random = Math.random().toString(36).substring(2, 8)
  return `guest_${timestamp}_${random}`
}

export const UserProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUserState] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Load user from storage on app start
  useEffect(() => {
    loadUserFromStorage()
  }, [])

  const loadUserFromStorage = async () => {
    try {
      const storedUser = await safeStorage.getItem(STORAGE_KEY)
      if (storedUser) {
        const parsedUser = JSON.parse(storedUser) as User
        setUserState(parsedUser)
      } else {
        // Create a guest user if none exists
        const guestUser = await generateGuestUser()
        setUserState(guestUser)
      }
    } catch (error) {
      console.error('Failed to load user from storage:', error)
      // Fallback: create a guest user
      const guestUser = await generateGuestUser()
      setUserState(guestUser)
    } finally {
      setIsLoading(false)
    }
  }

  const setUser = async (newUser: User | null) => {
    try {
      if (newUser) {
        await safeStorage.setItem(STORAGE_KEY, JSON.stringify(newUser))
      } else {
        await safeStorage.removeItem(STORAGE_KEY)
      }
      setUserState(newUser)
    } catch (error) {
      console.error('Failed to save user to storage:', error)
      setUserState(newUser)
    }
  }

  const generateGuestUser = async (): Promise<User> => {
    const guestUser: User = {
      id: generateGuestUserId(),
      name: 'Guest User',
      createdAt: new Date().toISOString(),
    }
    
    try {
      await safeStorage.setItem(STORAGE_KEY, JSON.stringify(guestUser))
    } catch (error) {
      console.error('Failed to save guest user:', error)
    }
    
    return guestUser
  }

  const clearUser = async () => {
    try {
      await safeStorage.removeItem(STORAGE_KEY)
      setUserState(null)
    } catch (error) {
      console.error('Failed to clear user:', error)
      setUserState(null)
    }
  }

  const value: UserContextType = {
    user,
    isLoading,
    setUser,
    generateGuestUser,
    clearUser,
  }

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>
}

export const useUser = (): UserContextType => {
  const context = useContext(UserContext)
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider')
  }
  return context
}

export type { User, UserContextType }