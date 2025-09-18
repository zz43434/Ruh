import { Animated, Easing } from 'react-native'

// Tab transition animation configuration
export const createTabTransition = () => {
  const fadeAnim = new Animated.Value(0)
  const scaleAnim = new Animated.Value(0.95)

  const animateIn = () => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 250,
        easing: Easing.out(Easing.quad),
        useNativeDriver: true,
      }),
      Animated.timing(scaleAnim, {
        toValue: 1,
        duration: 250,
        easing: Easing.out(Easing.back(1.1)),
        useNativeDriver: true,
      }),
    ]).start()
  }

  const animateOut = () => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 0,
        duration: 200,
        easing: Easing.in(Easing.quad),
        useNativeDriver: true,
      }),
      Animated.timing(scaleAnim, {
        toValue: 0.95,
        duration: 200,
        easing: Easing.in(Easing.quad),
        useNativeDriver: true,
      }),
    ]).start()
  }

  return {
    fadeAnim,
    scaleAnim,
    animateIn,
    animateOut,
  }
}

// Tab icon animation
export const createTabIconAnimation = () => {
  const bounceAnim = new Animated.Value(1)

  const bounce = () => {
    Animated.sequence([
      Animated.timing(bounceAnim, {
        toValue: 1.2,
        duration: 150,
        easing: Easing.out(Easing.quad),
        useNativeDriver: true,
      }),
      Animated.timing(bounceAnim, {
        toValue: 1,
        duration: 150,
        easing: Easing.out(Easing.quad),
        useNativeDriver: true,
      }),
    ]).start()
  }

  return {
    bounceAnim,
    bounce,
  }
}