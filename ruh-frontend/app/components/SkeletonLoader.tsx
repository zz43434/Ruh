import React from 'react'
import { View, ViewStyle, DimensionValue } from 'react-native'
import SkeletonPlaceholder from 'react-native-skeleton-placeholder'
import { useAppTheme } from '@/theme/context'

interface SkeletonLoaderProps {
  style?: ViewStyle
}

// Chat message skeleton
export const ChatMessageSkeleton: React.FC<SkeletonLoaderProps> = ({ style }) => {
  const { theme } = useAppTheme()
  
  return (
    <SkeletonPlaceholder
      backgroundColor={theme.colors.palette.neutral200}
      highlightColor={theme.colors.palette.neutral100}
      speed={1200}
    >
      <View style={[{ marginVertical: 8, paddingHorizontal: 16 }, style]}>
        {/* Bot message skeleton */}
        <View style={{ flexDirection: 'row', alignItems: 'flex-start', marginBottom: 12 }}>
          <View style={{ width: 32, height: 32, borderRadius: 16, marginRight: 12 }} />
          <View style={{ flex: 1 }}>
            <View style={{ width: '80%', height: 16, borderRadius: 8, marginBottom: 8 }} />
            <View style={{ width: '60%', height: 16, borderRadius: 8, marginBottom: 8 }} />
            <View style={{ width: '40%', height: 16, borderRadius: 8 }} />
          </View>
        </View>
      </View>
    </SkeletonPlaceholder>
  )
}

// Verse card skeleton
export const VerseSkeleton: React.FC<SkeletonLoaderProps> = ({ style }) => {
  const { theme } = useAppTheme()
  
  return (
    <SkeletonPlaceholder
      backgroundColor={theme.colors.palette.neutral200}
      highlightColor={theme.colors.palette.neutral100}
      speed={1200}
    >
      <View style={[{ marginVertical: 8, paddingHorizontal: 16 }, style]}>
        <View style={{ 
          backgroundColor: theme.colors.palette.neutral100,
          borderRadius: 12,
          padding: 16,
        }}>
          {/* Verse reference */}
          <View style={{ width: 120, height: 14, borderRadius: 7, marginBottom: 12 }} />
          
          {/* Arabic text */}
          <View style={{ marginBottom: 12 }}>
            <View style={{ width: '100%', height: 18, borderRadius: 9, marginBottom: 6 }} />
            <View style={{ width: '85%', height: 18, borderRadius: 9, marginBottom: 6 }} />
            <View style={{ width: '70%', height: 18, borderRadius: 9 }} />
          </View>
          
          {/* Translation */}
          <View>
            <View style={{ width: '95%', height: 16, borderRadius: 8, marginBottom: 6 }} />
            <View style={{ width: '80%', height: 16, borderRadius: 8, marginBottom: 6 }} />
            <View style={{ width: '60%', height: 16, borderRadius: 8 }} />
          </View>
        </View>
      </View>
    </SkeletonPlaceholder>
  )
}

// Wellness entry skeleton
export const WellnessEntrySkeleton: React.FC<SkeletonLoaderProps> = ({ style }) => {
  const { theme } = useAppTheme()
  
  return (
    <SkeletonPlaceholder
      backgroundColor={theme.colors.palette.neutral200}
      highlightColor={theme.colors.palette.neutral100}
      speed={1200}
    >
      <View style={[{ marginVertical: 8, paddingHorizontal: 16 }, style]}>
        <View style={{ 
          backgroundColor: theme.colors.palette.neutral100,
          borderRadius: 12,
          padding: 16,
        }}>
          {/* Date and mood */}
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <View style={{ width: 100, height: 14, borderRadius: 7 }} />
            <View style={{ width: 60, height: 24, borderRadius: 12 }} />
          </View>
          
          {/* Metrics */}
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 12 }}>
            <View style={{ alignItems: 'center' }}>
              <View style={{ width: 50, height: 12, borderRadius: 6, marginBottom: 4 }} />
              <View style={{ width: 30, height: 16, borderRadius: 8 }} />
            </View>
            <View style={{ alignItems: 'center' }}>
              <View style={{ width: 50, height: 12, borderRadius: 6, marginBottom: 4 }} />
              <View style={{ width: 30, height: 16, borderRadius: 8 }} />
            </View>
          </View>
          
          {/* Notes */}
          <View>
            <View style={{ width: '100%', height: 14, borderRadius: 7, marginBottom: 6 }} />
            <View style={{ width: '75%', height: 14, borderRadius: 7 }} />
          </View>
        </View>
      </View>
    </SkeletonPlaceholder>
  )
}

// Generic list skeleton
export const ListSkeleton: React.FC<{ 
  itemCount?: number
  renderItem: () => React.ReactElement
  style?: ViewStyle 
}> = ({ itemCount = 3, renderItem, style }) => {
  return (
    <View style={style}>
      {Array.from({ length: itemCount }, (_, index) => (
        <View key={index}>
          {renderItem()}
        </View>
      ))}
    </View>
  )
}

// Search skeleton
export const SearchSkeleton: React.FC<SkeletonLoaderProps> = ({ style }) => {
  const { theme } = useAppTheme()
  
  return (
    <SkeletonPlaceholder
      backgroundColor={theme.colors.palette.neutral200}
      highlightColor={theme.colors.palette.neutral100}
      speed={1200}
    >
      <View style={[{ paddingHorizontal: 16, paddingVertical: 12 }, style]}>
        {/* Search results header */}
        <View style={{ width: 150, height: 16, borderRadius: 8, marginBottom: 16 }} />
        
        {/* Search result items */}
        {Array.from({ length: 3 }, (_, index) => (
          <View key={index} style={{ marginBottom: 16 }}>
            <View style={{ width: '100%', height: 14, borderRadius: 7, marginBottom: 8 }} />
            <View style={{ width: '85%', height: 14, borderRadius: 7, marginBottom: 8 }} />
            <View style={{ width: '60%', height: 14, borderRadius: 7 }} />
          </View>
        ))}
      </View>
    </SkeletonPlaceholder>
  )
}

// Compact skeleton for small loading states
export const CompactSkeleton: React.FC<{ 
  width?: DimensionValue
  height?: number
  borderRadius?: number
  style?: ViewStyle 
}> = ({ width = '100%', height = 16, borderRadius = 8, style }) => {
  const { theme } = useAppTheme()
  
  return (
    <SkeletonPlaceholder
      backgroundColor={theme.colors.palette.neutral200}
      highlightColor={theme.colors.palette.neutral100}
      speed={1200}
    >
      <View style={[{ width, height, borderRadius }, style]} />
    </SkeletonPlaceholder>
  )
}