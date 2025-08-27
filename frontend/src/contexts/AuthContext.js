import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../services/apiService';

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in (check sessionStorage for token)
    const token = sessionStorage.getItem('token');
    if (token) {
      // Verify token with backend
      verifyToken(token);
    } else {
      setLoading(false);
    }
  }, []);

  const verifyToken = async (token) => {
    try {
      const response = await apiClient.get('/auth/me');
      
      setCurrentUser(response.data);
      setIsAuthenticated(true);
      // Set token in sessionStorage for future requests
      sessionStorage.setItem('token', token);
    } catch (error) {
      // Token is invalid, remove it
      sessionStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      console.log('🔍 DEBUG: Attempting login for user:', username);
      console.log('🔍 DEBUG: API client base URL:', apiClient.defaults.baseURL);

      const response = await apiClient.post('/auth/login', {
        username,
        password
      });

      console.log('🔍 DEBUG: Login response received:', response.status, response.data);

      const { access_token, user_id, username: user } = response.data;

      // Store token in sessionStorage
      sessionStorage.setItem('token', access_token);

      // Update state
      setCurrentUser({ user_id, username: user });
      setIsAuthenticated(true);

      // Load user settings from backend and store in sessionStorage
      await loadUserSettings(user_id, access_token);

      return { success: true };
    } catch (error) {
      console.error('🔍 DEBUG: Login error details:');
      console.error('🔍 DEBUG: Error message:', error.message);
      console.error('🔍 DEBUG: Error response:', error.response);
      console.error('🔍 DEBUG: Error status:', error.response?.status);
      console.error('🔍 DEBUG: Error headers:', error.response?.headers);
      console.error('🔍 DEBUG: Error data:', error.response?.data);
      console.error('🔍 DEBUG: Error config:', error.config);

      // Check if this is a database timeout error
      if (error.response?.status === 503 && error.response?.headers?.['x-error-type'] === 'database_timeout') {
        return {
          success: false,
          error: 'The authentication database was on standby and is currently slow to respond. Please try again in 60 seconds.'
        };
      }

      // Check for authentication failures (401 status)
      if (error.response?.status === 401) {
        return {
          success: false,
          error: 'Authentication failed'
        };
      }

      // For all other errors, return a generic error message
      return {
        success: false,
        error: 'An unexpected error occurred. Please try again.'
      };
    }
  };

  // Load user settings from backend and store in sessionStorage
  const loadUserSettings = async (userId, token) => {
    try {
      const response = await apiClient.get('/settings');
      
      if (response.data.success && response.data.settings) {
        // Store settings in sessionStorage
        sessionStorage.setItem('userSettings', JSON.stringify(response.data.settings));
      } else {
        // No settings found, create default settings
        const defaultSettings = {
          userId: userId,
          settingsType: "user_settings",
          chatGIS: {
            salutation: "none specified",
            enableAreasOfInterest: false,
            areas: [
              {
                areaId: "chatgis_area1",
                enabled: true,
                coordinates: { minLat: 0, maxLat: 0, minLon: 0, maxLon: 0 },
                presetArea: "custom"
              },
              {
                areaId: "chatgis_area2",
                enabled: false,
                coordinates: { minLat: 0, maxLat: 0, minLon: 0, maxLon: 0 },
                presetArea: "custom"
              },
              {
                areaId: "chatgis_area3",
                enabled: false,
                coordinates: { minLat: 0, maxLat: 0, minLon: 0, maxLon: 0 },
                presetArea: "custom"
              }
            ]
          },
          geoRAG: {
            selectedModel: "Amazon Nova Lite",
            enableAreasOfInterest: false,
            areas: [
              {
                areaId: "area1",
                enabled: true,
                coordinates: { minLat: 0, maxLat: 0, minLon: 0, maxLon: 0 },
                presetArea: "custom"
              },
              {
                areaId: "area2",
                enabled: false,
                coordinates: { minLat: 0, maxLat: 0, minLon: 0, maxLon: 0 },
                presetArea: "custom"
              },
              {
                areaId: "area3",
                enabled: false,
                coordinates: { minLat: 0, maxLat: 0, minLon: 0, maxLon: 0 },
                presetArea: "custom"
              }
            ]
          },
          metadata: {
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            version: "1.0"
          }
        };
        
        sessionStorage.setItem('userSettings', JSON.stringify(defaultSettings));
      }
    } catch (error) {
      console.error('Error loading user settings:', error);
      // If there's an error, create default settings
      const defaultSettings = {
        userId: userId,
        settingsType: "user_settings",
        chatGIS: {
          salutation: "none specified",
          enableAreasOfInterest: false,
          areas: [
            {
              areaId: "chatgis_area1",
              enabled: true,
              coordinates: { minLat: 0, maxLat: 0, minLon: 0, maxLon: 0 },
              presetArea: "custom"
            },
            {
              areaId: "chatgis_area2",
              enabled: false,
              coordinates: { minLat: 0, maxLat: 0, minLon: 0, maxLon: 0 },
              presetArea: "custom"
            },
            {
              areaId: "chatgis_area3",
              enabled: false,
              coordinates: { minLat: 0, maxLat: 0, minLon: 0, maxLon: 0 },
              presetArea: "custom"
            }
          ]
        },
        geoRAG: {
          selectedModel: "Amazon Nova Lite",
          enableAreasOfInterest: false,
          areas: [
            {
              areaId: "area1",
              enabled: true,
              coordinates: { minLat: 0, maxLat: 0, minLon: 0, maxLon: 0 },
              presetArea: "custom"
            },
            {
              areaId: "area2",
              enabled: false,
              coordinates: { minLat: 0, maxLat: 0, minLon: 0, maxLon: 0 },
              presetArea: "custom"
            },
            {
              areaId: "area3",
              enabled: false,
              coordinates: { minLat: 0, maxLat: 0, minLon: 0, maxLon: 0 },
              presetArea: "custom"
            }
          ]
        },
        metadata: {
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          version: "1.0"
        }
      };
      
      sessionStorage.setItem('userSettings', JSON.stringify(defaultSettings));
    }
  };

  const logout = () => {
    // Remove token from sessionStorage
    sessionStorage.removeItem('token');
    
    // Clear user settings
    sessionStorage.removeItem('userSettings');
    
    // Clear all chat-related sessionStorage data
    sessionStorage.removeItem('rag_chat_messages');
    sessionStorage.removeItem('rag_session_id');
    sessionStorage.removeItem('rag_selected_model');
    sessionStorage.removeItem('rag_geo_ner_enabled');
    sessionStorage.removeItem('rag_map_state'); // Clear map state on logout
    sessionStorage.removeItem('chatgis_chat_messages');
    sessionStorage.removeItem('chatgis_system_prompt');
    sessionStorage.removeItem('chatgis_geo_ner_enabled');
    sessionStorage.removeItem('chatgis_map_state'); // Clear ChatGIS map state on logout
    
    // Remove axios default header
          // Token is already removed from sessionStorage
    
    // Update state
    setCurrentUser(null);
    setIsAuthenticated(false);
  };

  const value = {
    currentUser,
    isAuthenticated,
    login,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}
