import { Easing } from 'react-native-reanimated'
import { NativeStackNavigationOptions } from '@react-navigation/native-stack'

// Animation timing configurations
export const transitionConfig = {
  duration: 300,
  easing: Easing.out(Easing.poly(4)),
}

export const fastTransitionConfig = {
  duration: 200,
  easing: Easing.out(Easing.quad),
}

// Slide from right animation (default iOS style)
export const slideFromRightAnimation: NativeStackNavigationOptions = {
  animation: 'slide_from_right',
  animationDuration: 300,
}

// Slide from bottom animation (modal style)
export const slideFromBottomAnimation: NativeStackNavigationOptions = {
  animation: 'slide_from_bottom',
  animationDuration: 300,
}

// Fade animation
export const fadeAnimation: NativeStackNavigationOptions = {
  animation: 'fade',
  animationDuration: 300,
}

// Scale animation (zoom effect)
export const scaleAnimation: NativeStackNavigationOptions = {
  animation: 'fade_from_bottom',
  animationDuration: 300,
}

// Flip animation
export const flipAnimation: NativeStackNavigationOptions = {
  animation: 'flip',
  animationDuration: 300,
}

// No animation
export const noAnimation: NativeStackNavigationOptions = {
  animation: 'none',
}

// Fast slide animation
export const fastSlideAnimation: NativeStackNavigationOptions = {
  animation: 'slide_from_right',
  animationDuration: 200,
}

// Custom animation presets for different screen types
export const screenAnimations = {
  // Main navigation screens
  main: slideFromRightAnimation,
  
  // Modal screens
  modal: slideFromBottomAnimation,
  
  // Detail screens
  detail: fadeAnimation,
  
  // Settings/profile screens
  settings: scaleAnimation,
  
  // Quick actions
  quick: fastSlideAnimation,
  
  // No animation for tabs
  tab: noAnimation,
}