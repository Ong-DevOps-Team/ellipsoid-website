# Ellipsoid Labs Frontend Documentation

## Overview

The Ellipsoid Labs frontend is a React-based web application that provides a modern user interface for interacting with the GIS Expert AI chatbot and RAG (Retrieval Augmented Generation) services.

## Architecture

### Technology Stack
- **Framework**: React 18+
- **Routing**: React Router for navigation
- **State Management**: React Context API for authentication state
- **Styling**: CSS modules for component-specific styles
- **HTTP Client**: Built-in fetch API for backend communication

### Project Structure
```
frontend/
├── public/
│   └── index.html          # Main HTML template
├── src/
│   ├── components/         # React components
│   │   ├── About.js        # About page component
│   │   ├── Chatbot.js      # ChatGIS AI chatbot with session persistence
│   │   ├── Home.js         # Home page component
│   │   ├── Login.js        # User authentication
│   │   ├── Navbar.js       # Navigation component
│   │   ├── RAGChatbot.js   # GeoRAG chatbot with map integration and persistence
│   │   └── Settings.js     # User settings with real-time sessionStorage
│   ├── contexts/
│   │   └── AuthContext.js  # Authentication context
│   ├── config.js           # Frontend configuration
│   ├── App.js              # Main application component
│   └── index.js            # Application entry point
└── package.json            # Dependencies and scripts
```

## Components

### Core Components

#### App.js
- Main application component
- Handles routing and authentication state
- Provides authentication context to child components

#### Navbar.js
- Navigation component with authentication status
- Shows login/logout buttons based on user state
- Responsive navigation menu

#### Login.js
- User authentication form
- Handles login requests to backend
- Stores JWT token in authentication context

### Feature Components

#### Chatbot.js (ChatGIS)
- GIS Expert AI chatbot interface with comprehensive geographic capabilities
- Real-time chat with OpenAI-powered GIS expert and geographic entity recognition
- **Interactive Map Integration**: Esri ArcGIS MapView with topographic basemap
- **Clickable Geographic Entities**: Location references in chat become interactive map links  
- **Map Toggle Functionality**: Minimize/intermediate/maximize map with state persistence
- **Geo-XML Processing**: Backend processes text for geographic entities and tagging
- **Areas of Interest Filtering**: Geographic filtering for enhanced location-based responses
- SessionStorage-based chat history and map state that persists across navigation
- Saved chat loading and management from MongoDB
- System prompt persistence and restoration
- Automatic state cleanup on logout

#### RAGChatbot.js (GeoRAG)
- RAG (Retrieval Augmented Generation) chatbot with comprehensive state persistence
- AWS Bedrock integration with Areas of Interest filtering
- Advanced document retrieval capabilities with geographic context
- **Interactive Map Integration**: Esri ArcGIS MapView with topographic basemap
- **Map Toggle Functionality**: Minimize/maximize map with state persistence across navigation
- **Geo-XML Processing**: Clickable location links in chat history
- **California Area Focus**: Map centered on California with appropriate zoom levels
- **Chat History Persistence**: SessionStorage-based state management
- **Settings Integration**: Real-time Areas of Interest filtering from Settings page
- **Areas of Interest Filtering**: Geographic filtering for enhanced location-based responses
- **Navigation Persistence**: Complete state restoration when returning to page

#### Settings.js
- Comprehensive user settings management with real-time updates
- **Real-time SessionStorage**: Settings changes immediately available across components
- **ChatGIS Settings**: Salutation preferences and Areas of Interest configuration with instant persistence
- **GeoRAG Settings**: Model selection and Areas of Interest configuration
- **Geographic Areas**: Up to 3 configurable areas with coordinate input and presets for both ChatGIS and GeoRAG
- **Navigation Persistence**: Settings values preserved when navigating away and returning
- **Protected Loading**: Prevents race conditions during initial state restoration

#### About.js
- Company information and background
- Static content about Ellipsoid Labs

#### Home.js
- Landing page component
- Overview of available services

## Areas of Interest Functionality

### Overview
Both ChatGIS and GeoRAG components support configurable Areas of Interest filtering, allowing users to define geographic boundaries that enhance the relevance and accuracy of location-based responses. This functionality is managed through the Settings page and automatically applied to all API calls.

### Features

#### Geographic Filtering
- **Enable/Disable**: Toggle Areas of Interest filtering on/off for each system
- **Multiple Areas**: Configure up to 3 distinct geographic areas
- **Coordinate Precision**: 4-decimal precision for latitude and longitude
- **Preset Areas**: Quick selection from predefined regions:
  - Oceanside, California
  - San Diego County
  - California (state-wide)
  - Texas
  - New York State
- **Custom Coordinates**: Manual input for specific geographic boundaries

#### Technical Implementation
- **Real-time Updates**: Settings changes immediately available across components
- **SessionStorage Integration**: Areas configuration persisted in user settings
- **API Integration**: Areas automatically included in `/chat/gis` and `/chat/rag` calls
- **Validation**: Only enabled areas with valid coordinates are sent to backend
- **Format Conversion**: Automatic conversion from Settings format to API format

#### User Experience
- **Immediate Effect**: Changes take effect without requiring "Save Settings"
- **Visual Feedback**: Clear indication of enabled/disabled areas
- **Coordinate Validation**: Real-time validation of coordinate inputs
- **Preset Selection**: Dropdown selection for common geographic regions

## Map Functionality

### Overview
Both the ChatGIS (Chatbot.js) and GeoRAG (RAGChatbot.js) components include interactive maps powered by Esri ArcGIS API for JavaScript, providing users with visual geographic context for location-based queries and responses.

### Map Features

#### Basemap and Display
- **Topographic Basemap**: High-quality topographic map display
- **California Focus**: Map centered on California with appropriate zoom levels
- **Responsive Design**: Map adapts to container size changes
- **Professional Appearance**: Clean, modern map interface

#### Interactive Controls
- **Toggle Button**: Minimize/maximize map with smooth transitions
- **State Persistence**: Map size state maintained across page navigation
- **Visual Feedback**: Clear button states and tooltips
- **Smooth Animations**: CSS transitions for height changes

#### Geographic Integration
- **Geo-XML Processing**: Automatic detection and conversion of location tags
- **Clickable Links**: Location references in chat become interactive map links
- **Marker Management**: Dynamic placement of location markers
- **Zoom and Pan**: Interactive map navigation

### Technical Implementation

#### Esri Integration
- **API Version**: ArcGIS API for JavaScript 4.29
- **Basemap**: Topographic vector tiles for optimal performance
- **Map Container**: Dedicated div with proper sizing and overflow handling
- **Event Handling**: Custom click handlers for map interactions

#### State Management
- **Session Storage**: Map state and chat history persisted across browser sessions
- **Authentication Integration**: All states cleared on logout for security
- **Navigation Persistence**: Map size and chat history maintained when navigating between pages
- **Clear Chat Reset**: Map returns to minimized state and chat history cleared when requested
- **Settings Integration**: Real-time Areas of Interest filtering applied to API calls for both ChatGIS and GeoRAG
- **Protected Loading**: Initial state restoration protected from race conditions

#### Performance Features
- **Lazy Loading**: Map initializes only when needed
- **Efficient Rendering**: Optimized for smooth user experience
- **Memory Management**: Proper cleanup of map resources
- **Responsive Updates**: Map adapts to container size changes

### User Experience

#### Map States
- **Minimized**: Compact 60px height for space efficiency
- **Maximized**: Full 500px height for detailed map viewing
- **Smooth Transitions**: Animated height changes between states
- **Persistent State**: User preferences maintained during session

#### Location Features
- **Clickable Links**: Geographic references in chat become interactive
- **Automatic Markers**: Location markers placed on map when clicked
- **Zoom to Location**: Map automatically centers on selected locations
- **Context Preservation**: Map state maintained during location exploration

### Configuration

#### Map Settings
- **Center Coordinates**: [-119.30, 37.30] (California center)
- **Default Zoom**: Level 6 for optimal California overview
- **Extent Constraints**: California area of interest boundaries
- **Rotation Disabled**: Simplified navigation for better usability

#### Integration Points
- **Chat History**: Geo-XML tags automatically processed
- **Authentication**: Map state cleared on logout
- **Navigation**: State persistence across page changes
- **Responsiveness**: Adapts to different screen sizes

## Authentication

### Authentication Flow
1. User enters credentials in Login component
2. Frontend sends POST request to `/auth/login`
3. Backend validates credentials and returns JWT token
4. Frontend stores token in AuthContext
5. Token is included in all subsequent API requests

### Protected Routes
- Chatbot and RAG chatbot components require authentication
- Unauthenticated users are redirected to login
- JWT token is automatically included in API headers

## API Integration

### Backend Communication
- All API calls use the base URL: `http://localhost:8000`
- JWT tokens are included in Authorization headers
- Error handling for authentication and API failures

### Key Endpoints Used
- `POST /auth/login` - User authentication
- `POST /chat/gis` - ChatGIS chatbot interactions with geographic entity recognition and map integration
- `POST /chat/rag` - GeoRAG chatbot interactions with Areas of Interest filtering and map integration
- `GET /chats/saved` - Retrieve saved chats
- `POST /chats/save` - Save chat history
- `GET /settings` - Retrieve user settings
- `POST /settings` - Create/update user settings
- `GET /system-prompts` - Retrieve system prompts for chatbots

### Map Integration
- **Esri ArcGIS API**: External API integration for map functionality
- **Geo-XML Processing**: Backend processes text for geographic entities
- **Location Markers**: Dynamic marker placement based on chat content
- **Areas of Interest**: Backend provides California-focused geographic context with configurable filtering for both ChatGIS and GeoRAG

## State Management

### Authentication Context
- Global authentication state using React Context
- JWT token storage and management with sessionStorage cleanup
- User information (user_id, username)
- Login/logout functions with comprehensive state cleanup
- User settings loading and management during authentication flow

### Component State
- Local component state for forms and UI interactions
- **SessionStorage-based Persistence**: Chat history and settings maintained across navigation
- **Real-time State Synchronization**: Settings changes immediately available across components
- **Protected State Loading**: Initial state restoration with race condition prevention
- Form validation and error handling with proper state management

### SessionStorage Architecture

#### Chat History Persistence
- **ChatGIS Storage**: 
  - `chatgis_chat_messages` - Complete chat conversation history
  - `chatgis_system_prompt` - System prompt for consistent AI behavior
  - `chatgis_geo_ner_enabled` - Geographic entity recognition settings
  - `chatgis_map_state` - Map display state (minimized/intermediate/maximized)
- **GeoRAG Storage**:
  - `rag_chat_messages` - Chat history with geographic context
  - `rag_session_id` - Backend session identifier for continuity
  - `rag_geo_ner_enabled` - Geographic entity recognition settings
  - `rag_map_state` - Map display state (minimized/intermediate/maximized)

#### Settings Storage
- **User Settings**: `userSettings` - Complete user preferences in structured JSON
  - Real-time updates on any settings change
  - Immediate availability across all frontend components
  - Automatic loading on component mount with race condition protection

#### State Management Lifecycle
1. **Component Mount**: Load from sessionStorage with protected initialization
2. **User Interaction**: Update React state and immediately sync to sessionStorage
3. **Navigation**: State persists automatically across page changes
4. **Logout**: Complete sessionStorage cleanup for security
5. **Login**: Fresh state initialization with user-specific settings loading

## Styling

### CSS Architecture
- Component-specific CSS files
- Responsive design for mobile and desktop
- Modern UI with clean, professional appearance
- Consistent color scheme and typography

### Responsive Design
- Mobile-first approach
- Breakpoints for tablet and desktop
- Flexible layouts that adapt to screen size

## Development

### Getting Started
1. Navigate to frontend directory
2. Install dependencies: `npm install`
3. Start development server: `npm start`
4. Access application at `http://localhost:3000`

### Available Scripts
- `npm start` - Start development server
- `npm build` - Build production bundle
- `npm test` - Run test suite
- `npm eject` - Eject from Create React App

### Development Notes
- Frontend runs on port 3000
- Backend must be running on port 8000
- CORS is configured to allow frontend-backend communication
- Hot reloading enabled for development

## Testing

### Testing Strategy
- Component testing with React Testing Library
- Integration testing for API communication
- User interaction testing for chatbot functionality

### Running Tests
```bash
cd frontend
npm test
```

## Deployment

### Production Build
- Optimized bundle creation with `npm run build`
- Static file serving from build directory
- Environment-specific configuration

### Environment Variables
- API base URL configuration
- Feature flags for development/production
- External service configuration

## Troubleshooting

### Common Issues
- **CORS Errors**: Ensure backend is running and CORS is configured
- **Authentication Failures**: Check JWT token validity and expiration
- **API Connection Issues**: Verify backend URL and port configuration
- **Chat History Not Persisting**: Check browser sessionStorage and ensure no errors in console
- **Settings Not Loading**: Verify sessionStorage contains `userSettings` and check initial load timing
- **Areas of Interest Not Working**: Check Settings page has enabled areas with valid coordinates for both ChatGIS and GeoRAG
- **Map State Issues**: Verify `rag_map_state` in sessionStorage and check map initialization

### Debug Tools
- React Developer Tools for component inspection
- Browser DevTools for network and console debugging
- Authentication context debugging in React DevTools

## Future Enhancements

### Planned Features
- Enhanced error handling and user feedback
- Offline capability for saved chats with Service Worker implementation
- Advanced chat history search and filtering with full-text search
- Export/import functionality for chat histories and settings
- Keyboard shortcuts for common actions
- Mobile app development with React Native
- Advanced Areas of Interest features (polygon shapes, named regions) for both ChatGIS and GeoRAG
- Real-time collaboration features for shared chat sessions

### Performance Improvements
- Code splitting for better load times
- Lazy loading of chatbot components
- Optimized bundle size and caching

## Support

For frontend-related questions or issues:
- Check this documentation
- Review component source code
- Check browser console for errors
- Verify backend API connectivity
