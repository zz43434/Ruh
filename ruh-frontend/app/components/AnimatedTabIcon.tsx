import React, { useEffect } from 'react'
import { Animated, Text } from 'react-native'
import { createTabIconAnimation } from '@/navigators/tabAnimations'

interface AnimatedTabIconProps {
  icon: string
  color: string
  size: number
  focused: boolean
}

export const AnimatedTabIcon: React.FC<AnimatedTabIconProps> = ({
  icon,
  color,
  size,
  focused,
}) => {
  const { bounceAnim, bounce } = createTabIconAnimation()

  useEffect(() => {
    if (focused) {
      bounce()
    }
  }, [focused, bounce])

  return (
    <Animated.View
      style={{
        transform: [{ scale: bounceAnim }],
      }}
    >
      <Text
        style={{
          color,
          fontSize: size * 0.8,
          textAlign: 'center',
        }}
      >
        {icon}
      </Text>
    </Animated.View>
  )
}