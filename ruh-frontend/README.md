# Ruh Frontend

**Ruh** (Arabic: روح - meaning "soul" or "spirit") is a React Native mobile application that provides AI-powered Islamic spiritual guidance through intelligent conversations and semantic Quranic verse search.

## 🌟 Features

- **Intelligent Chat Interface**: Natural conversations with AI-powered Islamic spiritual guidance
- **Semantic Verse Search**: Find relevant Quranic verses using advanced RAG technology
- **Wellness Tracking**: Monitor your spiritual and emotional well-being journey
- **Comprehensive Verse Library**: Browse all 114 Surahs with detailed verse information
- **Cross-platform**: Native iOS and Android experience with Expo
- **Modern UI**: Clean, intuitive interface with Islamic design elements
- **Offline Support**: Works without internet connection for core features

## 🛠️ Tech Stack

- **React Native** with **Expo** for cross-platform development
- **TypeScript** for type safety
- **React Navigation** for navigation management
- **React Query** for server state management
- **Async Storage** for local data persistence
- **Apisauce** for API communication
- **i18next** for internationalization
- **Custom theming system** with Islamic design elements

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Expo CLI
- iOS Simulator (for iOS development)
- Android Studio (for Android development)

#### iOS Development with Xcode

For iOS development, you'll need Xcode installed on macOS:

**Xcode Requirements:**
- **Xcode 14.0+** (latest version recommended)
- **iOS SDK 16.0+** for target deployment
- **Command Line Tools** for Xcode
- **macOS 12.0+** (Monterey or later)

**Xcode Setup Steps:**

1. **Install Xcode from Mac App Store**
   ```bash
   # Or download from Apple Developer Portal
   # https://developer.apple.com/xcode/
   ```

2. **Install Command Line Tools**
   ```bash
   xcode-select --install
   ```

3. **Accept Xcode License**
   ```bash
   sudo xcodebuild -license accept
   ```

4. **Configure iOS Simulator**
   - Open Xcode → Window → Devices and Simulators
   - Download iOS simulators for testing (iOS 16.0+ recommended)
   - Set up preferred simulator devices (iPhone 14, iPhone 15, etc.)

5. **Development Team Setup** (for device testing)
   - Sign in to Xcode with your Apple ID
   - Configure development team in project settings
   - Enable developer mode on iOS device (Settings → Privacy & Security → Developer Mode)

**Xcode Project Configuration:**
- The app uses Expo development builds with custom native code
- iOS deployment target: **iOS 13.0+**
- Swift version: **5.0+**
- Supports both iPhone and iPad (Universal app)

**Common React Native & Expo Commands:**
```bash
# Run on iOS simulator
npm run ios
# or
npx expo run:ios

# Run on Android emulator/device
npm run android
# or
npx expo run:android

# Start development server
npm start
# or
npx expo start --dev-client

# Open iOS project in Xcode (after prebuild)
npx expo prebuild --clean
open ios/RuhFrontend.xcworkspace

# Clean and rebuild native projects
npx expo prebuild --clean

# Build development version for iOS simulator
npm run build:ios:sim

# Build development version for iOS device
npm run build:ios:dev

# Reset Metro bundler cache
npx expo start --clear

# Reset iOS simulator
xcrun simctl erase all

# Install dependencies and align versions
npm run align-deps
```

**Troubleshooting iOS Development:**
- If build fails, try cleaning derived data: `rm -rf ~/Library/Developer/Xcode/DerivedData`
- For signing issues, check Apple Developer account and certificates
- Ensure iOS deployment target matches project requirements
- Use `expo doctor` to diagnose common setup issues

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ruh-frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run start
   ```

### Development Builds

For local development with custom native code:

```bash
# iOS Simulator
npm run build:ios:sim

# iOS Device (Development)
npm run build:ios:dev

# Android Simulator
npm run build:android:sim

# Android Device (Development)
npm run build:android:dev
```

### Production Builds

```bash
# iOS Production
npm run build:ios:prod

# Android Production
npm run build:android:prod
```

## 📱 App Structure

### Core Screens
- **Chat Screen**: AI-powered spiritual guidance conversations
- **Verses Screen**: Browse and search Quranic verses
- **Wellness Screen**: Track spiritual and emotional well-being
- **Verse Details**: Detailed view of individual verses
- **Chapter Details**: Complete Surah information and verses

### Navigation
The app uses tab-based navigation with the following main sections:
- 💬 **Chat**: Spiritual guidance conversations
- 📖 **Verses**: Quranic verse library and search
- 🌱 **Wellness**: Spiritual wellness tracking

## 🏗️ Project Structure

```
ruh-frontend/
├── app/
│   ├── components/          # Reusable UI components
│   ├── screens/            # Screen components
│   │   ├── ChatScreen/     # AI chat interface
│   │   ├── VersesScreen/   # Verse browsing and search
│   │   ├── WellnessScreen/ # Wellness tracking
│   │   └── VerseDetailsScreen/ # Individual verse details
│   ├── navigators/         # Navigation configuration
│   ├── services/           # API services and data layer
│   ├── contexts/           # React contexts for state management
│   ├── theme/              # Theming and styling
│   ├── utils/              # Utility functions
│   ├── i18n/               # Internationalization
│   └── config/             # App configuration
├── assets/
│   ├── icons/              # App icons and UI icons
│   └── images/             # Images and graphics
├── .maestro/               # End-to-end test flows
└── test/                   # Unit tests
```

## 🎨 Assets

### Icons
Located in `./assets/icons/` - Used for navigation, buttons, and UI elements. The app includes a built-in `Icon` component for easy icon usage.

### Images
Located in `./assets/images/` - Contains app graphics, backgrounds, and Islamic design elements.

**Usage Example:**
```typescript
import { Image } from 'react-native';

const MyComponent = () => {
  return (
    <Image source={require('assets/images/islamic_pattern.png')} />
  );
};
```

## 🔧 Development

### Available Scripts

- `npm run start` - Start Expo development server
- `npm run android` - Run on Android
- `npm run ios` - Run on iOS
- `npm run web` - Run on web
- `npm run test` - Run unit tests
- `npm run test:watch` - Run tests in watch mode
- `npm run lint` - Run ESLint
- `npm run compile` - TypeScript compilation check

### Testing

#### Unit Tests
```bash
npm run test
```

#### End-to-End Tests (Maestro)
```bash
npm run test:maestro
```

Follow our [Maestro Setup](https://ignitecookbook.com/docs/recipes/MaestroSetup) guide for e2e testing.

### Code Quality

The project uses:
- **ESLint** for code linting
- **TypeScript** for type checking
- **Prettier** for code formatting

## 🌐 API Integration

The app connects to the Ruh backend API for:
- **Chat conversations** with AI spiritual guidance
- **Verse search** using semantic RAG technology
- **Wellness data** tracking and analytics
- **User preferences** and conversation history

API base URL is configured in `app/config/config.ts`

## 🎯 Key Features Implementation

### Chat Interface
- Real-time messaging with AI
- Conversation history persistence
- Verse recommendation system
- Emotional state analysis

### Verse Search
- Semantic search powered by RAG
- Filter by Surah, theme, or keyword
- Detailed verse information with context
- Arabic text with translations

### Wellness Tracking
- Daily mood and energy tracking
- Progress visualization
- Personal reflection notes
- Spiritual journey insights

## 🚀 Deployment

### Development
The app uses Expo's development build system for testing on physical devices.

### Production
Production builds are created using EAS Build:
- iOS: App Store distribution
- Android: Google Play Store distribution

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

**Ruh** - Bridging traditional Islamic wisdom with modern AI technology to provide personalized spiritual guidance for Muslims worldwide.
