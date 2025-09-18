import React, { useEffect, useRef } from 'react'
import { Animated, ViewStyle } from 'react-native'

interface AnimatedScreenWrapperProps {
  children: React.ReactNode
  animationType?: 'fade' | 'slideUp' | 'slideDown' | 'scale'
  duration?: number
  delay?: number
  style?: ViewStyle
}

export const AnimatedScreenWrapper: React.FC<AnimatedScreenWrapperProps> = ({
  children,
  animationType = 'fade',
  duration = 300,
  delay = 0,
  style,
}) => {
  const fadeAnim = useRef(new Animated.Value(0)).current
  const translateYAnim = useRef(new Animated.Value(50)).current
  const scaleAnim = useRef(new Animated.Value(0.9)).current

  useEffect(() => {
    const animations: Animated.CompositeAnimation[] = []

    switch (animationType) {
      case 'fade':
        animations.push(
          Animated.timing(fadeAnim, {
            toValue: 1,
            duration,
            useNativeDriver: true,
          })
        )
        break
      case 'slideUp':
        animations.push(
          Animated.timing(fadeAnim, {
            toValue: 1,
            duration,
            useNativeDriver: true,
          }),
          Animated.timing(translateYAnim, {
            toValue: 0,
            duration,
            useNativeDriver: true,
          })
        )
        break
      case 'slideDown':
        translateYAnim.setValue(-50)
        animations.push(
          Animated.timing(fadeAnim, {
            toValue: 1,
            duration,
            useNativeDriver: true,
          }),
          Animated.timing(translateYAnim, {
            toValue: 0,
            duration,
            useNativeDriver: true,
          })
        )
        break
      case 'scale':
        animations.push(
          Animated.timing(fadeAnim, {
            toValue: 1,
            duration,
            useNativeDriver: true,
          }),
          Animated.timing(scaleAnim, {
            toValue: 1,
            duration,
            useNativeDriver: true,
          })
        )
        break
    }

    const animation = Animated.parallel(animations)
    
    if (delay > 0) {
      setTimeout(() => animation.start(), delay)
    } else {
      animation.start()
    }
  }, [animationType, duration, delay, fadeAnim, translateYAnim, scaleAnim])

  const getAnimatedStyle = (): ViewStyle => {
    const baseStyle: ViewStyle = {
      opacity: fadeAnim,
      flex: 1,
    }

    switch (animationType) {
      case 'slideUp':
      case 'slideDown':
        return {
          ...baseStyle,
          transform: [{ translateY: translateYAnim }],
        }
      case 'scale':
        return {
          ...baseStyle,
          transform: [{ scale: scaleAnim }],
        }
      default:
        return baseStyle
    }
  }

  return (
    <Animated.View style={[getAnimatedStyle(), style]}>
      {children}
    </Animated.View>
  )
}