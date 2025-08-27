import React, { useState, useEffect, useCallback, useRef } from 'react';
import apiClient from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';
import './Chatbot.css';

function Chatbot() {
  const { isAuthenticated } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [savedChats, setSavedChats] = useState([]);
  const [showSaveForm, setShowSaveForm] = useState(false);
  const [chatTitle, setChatTitle] = useState('');
  const [currentChatId, setCurrentChatId] = useState(null);
  const [authError, setAuthError] = useState(false);
  const [systemPrompt, setSystemPrompt] = useState('');
  const [geoNEREnabled, setGeoNEREnabled] = useState(true);
  // Map state management - using sessionStorage-first approach
  const [mapState, setMapState] = useState(() => {
    // Initialize map state from sessionStorage or default to minimized
    const savedMapState = sessionStorage.getItem('chatgis_map_state');
    if (savedMapState && savedMapState !== 'minimized' && savedMapState !== 'intermediate' && savedMapState !== 'maximized') {
      // If it's the old string format, convert to new object format
      try {
        const parsed = JSON.parse(savedMapState);
        if (parsed.size) {
          return parsed.size;
        }
      } catch (e) {
        // Invalid JSON, reset to default
        return 'minimized';
      }
    }
    return savedMapState || 'minimized';
  }); // 'minimized', 'intermediate', 'maximized'
  
  // ChatGIS Map references
  const chatgisMapContainerRef = useRef(null);
  const chatgisMapViewRef = useRef(null);
  const chatgisMapGraphicsLayerRef = useRef(null);
  const chatgisMapCurrentGraphicRef = useRef(null);

  // Map state management helper functions
  const getMapStateFromSessionStorage = useCallback(() => {
    try {
      const savedMapState = sessionStorage.getItem('chatgis_map_state');
      if (savedMapState) {
        // Try to parse as JSON (new format)
        try {
          const parsed = JSON.parse(savedMapState);
          if (parsed && typeof parsed === 'object' && parsed.size) {
            return parsed;
          }
        } catch (e) {
          // If JSON parsing fails, it might be the old string format
          if (['minimized', 'intermediate', 'maximized'].includes(savedMapState)) {
            // Convert old string format to new object format
            return {
              size: savedMapState,
              center: [-119.30, 37.30], // Default California center
              zoom: 6,
              marker: null
            };
          }
        }
      }
      // Return default state
      return {
        size: 'minimized',
        center: [-119.30, 37.30], // Default California center  
        zoom: 6,
        marker: null
      };
    } catch (error) {
      console.error('Error getting map state from sessionStorage:', error);
      return {
        size: 'minimized',
        center: [-119.30, 37.30],
        zoom: 6,
        marker: null
      };
    }
  }, []);

  const saveMapStateToSessionStorage = useCallback((mapStateObj) => {
    try {
      sessionStorage.setItem('chatgis_map_state', JSON.stringify(mapStateObj));
    } catch (error) {
      console.error('Error saving map state to sessionStorage:', error);
    }
  }, []);

  // Helper function to apply map state - moved up to fix ESLint warning
  const applyMapState = useCallback((container, button, mainContainer, state) => {
    // Remove all existing state classes
    container.classList.remove('chatgis-minimized', 'chatgis-intermediate', 'chatgis-maximized');
    
    if (state === 'minimized') {
      container.style.height = '60px';
      button.title = 'Click to expand map';
      container.classList.add('chatgis-minimized');
      
      if (mainContainer) {
        mainContainer.classList.remove('map-expanded', 'map-intermediate');
        mainContainer.classList.add('map-minimized');
      }
      
      const minimizeIcon = button.querySelector('.chatgis-minimize-icon');
      const restoreIcon = button.querySelector('.chatgis-restore-icon');
      if (minimizeIcon) minimizeIcon.style.display = 'inline';
      if (restoreIcon) restoreIcon.style.display = 'none';
      
    } else if (state === 'intermediate') {
      container.style.height = '280px';
      button.title = 'Click to minimize map';
      container.classList.add('chatgis-intermediate');
      
      if (mainContainer) {
        mainContainer.classList.remove('map-minimized', 'map-expanded');
        mainContainer.classList.add('map-intermediate');
      }
      
      const minimizeIcon = button.querySelector('.chatgis-minimize-icon');
      const restoreIcon = button.querySelector('.chatgis-restore-icon');
      if (minimizeIcon) minimizeIcon.style.display = 'inline';
      if (restoreIcon) restoreIcon.style.display = 'none';
      
    } else if (state === 'maximized') {
      container.style.height = '500px';
      button.title = 'Click to reduce map';
      container.classList.add('chatgis-maximized');
      
      if (mainContainer) {
        mainContainer.classList.remove('map-minimized', 'map-intermediate');
        mainContainer.classList.add('map-expanded');
      }
      
      const minimizeIcon = button.querySelector('.chatgis-minimize-icon');
      const restoreIcon = button.querySelector('.chatgis-restore-icon');
      if (minimizeIcon) minimizeIcon.style.display = 'none';
      if (restoreIcon) restoreIcon.style.display = 'inline';
    }
  }, []);

  // Function to convert Geo-XML text to clickable HTML links - fixed
  const xmlGeotaggedTextToHtml = useCallback((xmlText) => {
    if (!xmlText) return '';
    
    return xmlText
      // Handle <LOC ...>...</LOC> tags
      .replace(/<LOC\s+([^>]+)>([^<]+)<\/LOC>/g, function(match, attrs, text) {
        const lonMatch = attrs.match(/lon=["']([^"']+)["']/);
        const latMatch = attrs.match(/lat=["']([^"']+)["']/);
        const zoomMatch = attrs.match(/zoom_level=["']([^"']+)["']/);
        
        const lon = lonMatch ? lonMatch[1] : '';
        const lat = latMatch ? latMatch[1] : '';
        const zoom = zoomMatch ? zoomMatch[1] : '';
        
        return `<a href="#" class="geo-link" data-lon="${lon}" data-lat="${lat}" data-zoom="${zoom}">${text}</a>`;
      });
  }, []);

  // Function to display text with Geo-XML tags converted to clickable links - fixed
  const displayGeotaggedText = useCallback((text) => {
    if (!text) return '';
    
    // Convert Geo-XML tags to clickable links first
    let processedText = xmlGeotaggedTextToHtml(text);
    
    // Convert line breaks to <br> for display
    processedText = processedText.replace(/\n/g, '<br>');
    
    // Don't escape HTML - let it render properly
    // This allows the geo-links to work and preserves any other HTML formatting
    return processedText;
  }, [xmlGeotaggedTextToHtml]);



  const fetchSystemPrompt = async () => {
    try {
      const response = await apiClient.get('/system-prompts');
      const gisPrompt = response.data.gis_expert;
      
      const newMessages = [
        {
          role: 'system',
          content: gisPrompt
        }
      ];
      
      setSystemPrompt(gisPrompt);
      setMessages(newMessages);
      
      // Save the new system prompt and messages to sessionStorage
      try {
        sessionStorage.setItem('chatgis_chat_messages', JSON.stringify(newMessages));
        sessionStorage.setItem('chatgis_system_prompt', gisPrompt);
      } catch (storageError) {
        console.error('Failed to save system prompt to sessionStorage:', storageError);
      }
      
      return gisPrompt;
    } catch (error) {
      console.error('Failed to fetch system prompt:', error);
      setSystemPrompt('');
      setMessages([]);
      return '';
    }
  };

  // Function to save current ChatGIS chat state to sessionStorage
  const saveChatGISState = useCallback((chatMessages) => {
    try {
      sessionStorage.setItem('chatgis_chat_messages', JSON.stringify(chatMessages));
      // Find the system prompt from the messages array and save it separately
      const systemMessage = chatMessages.find(msg => msg.role === 'system');
      if (systemMessage) {
        sessionStorage.setItem('chatgis_system_prompt', systemMessage.content);
      }
      sessionStorage.setItem('chatgis_geo_ner_enabled', JSON.stringify(geoNEREnabled));
      // Map state is now saved separately via saveMapStateToSessionStorage
    } catch (error) {
      console.error('Failed to save ChatGIS chat state:', error);
    }
  }, [geoNEREnabled]);

  // Function to load ChatGIS chat state from sessionStorage
  const loadChatGISState = useCallback(() => {
    try {
      const savedMessages = sessionStorage.getItem('chatgis_chat_messages');
      const savedPrompt = sessionStorage.getItem('chatgis_system_prompt');
      const savedGeoNER = sessionStorage.getItem('chatgis_geo_ner_enabled');
      const mapStateObj = getMapStateFromSessionStorage();
      
      console.log('Loading ChatGIS chat state from sessionStorage:', {
        messages: savedMessages ? 'found' : 'not found',
        prompt: savedPrompt ? 'found' : 'not found',
        geoNER: savedGeoNER,
        mapState: mapStateObj
      });
      
      if (savedMessages) {
        const messages = JSON.parse(savedMessages);
        
        // If we have messages but no saved prompt, try to extract it from the messages
        if (!savedPrompt) {
          const systemMessage = messages.find(msg => msg.role === 'system');
          if (systemMessage) {
            setSystemPrompt(systemMessage.content);
            // Save the extracted prompt for future use
            sessionStorage.setItem('chatgis_system_prompt', systemMessage.content);
          }
        } else {
          setSystemPrompt(savedPrompt);
        }
        
        if (savedGeoNER) {
          setGeoNEREnabled(JSON.parse(savedGeoNER));
        }
        
        // Set map size state from sessionStorage object
        setMapState(mapStateObj.size);
        
        setMessages(messages);
        console.log('Successfully restored ChatGIS chat state, mapState set to:', mapStateObj.size);
        return true; // Successfully restored
      }
      console.log('No saved ChatGIS chat state found');
      return false; // No saved state
    } catch (error) {
      console.error('Failed to load ChatGIS chat state:', error);
      return false;
    }
  }, [getMapStateFromSessionStorage]);

  // Function to clear saved ChatGIS chat state
  const clearChatGISState = useCallback(() => {
    try {
      sessionStorage.removeItem('chatgis_chat_messages');
      sessionStorage.removeItem('chatgis_system_prompt');
      sessionStorage.removeItem('chatgis_geo_ner_enabled');
      // Reset map state to default when clearing chat
      const defaultMapState = {
        size: 'minimized',
        center: [-119.30, 37.30],
        zoom: 6,
        marker: null
      };
      saveMapStateToSessionStorage(defaultMapState);
      setMapState('minimized');
    } catch (error) {
      console.error('Failed to clear ChatGIS chat state:', error);
    }
  }, [saveMapStateToSessionStorage]);

  // Function to load saved ChatGIS chats from MongoDB
  const loadSavedChatGISChats = useCallback(async () => {
    if (!isAuthenticated) return;
    
    try {
      const response = await apiClient.get('/chats/saved');
      setSavedChats(response.data.chats);
      setAuthError(false); // Clear any previous auth errors
    } catch (error) {
      console.error('Failed to load saved ChatGIS chats:', error);
      if (error.response?.status === 401) {
        console.log('Authentication failed - user may need to log in again');
        setAuthError(true);
      }
    }
  }, [isAuthenticated]);

  // ChatGIS Map functionality - simplified approach using direct DOM manipulation
  const initializeChatgisMap = useCallback(() => {
    if (!chatgisMapContainerRef.current) {
      return;
    }

    // Check if require function is available (global function from Esri script)
    if (typeof window.require === 'undefined') {
      setTimeout(initializeChatgisMap, 500);
      return;
    }

    try {
      // Use the global require function directly like the working example
      window.require([
        "esri/config",
        "esri/Map",
        "esri/views/MapView",
        "esri/Graphic",
        "esri/layers/GraphicsLayer"
      ], (esriConfig, Map, MapView, Graphic, GraphicsLayer) => {
        
        // Set API key
        esriConfig.apiKey = "AAPTxy8BH1VEsoebNVZXo8HurF89yH3U94of2tNjEtGqtHd_oOPwB6Hr-qkkjGSYglqlcPNZ0VCckRFM08AWdYsjNonYUEO27c0o5JX_sbSr8Uc6z49nfpUU9R9YXnwjObx6hGOpUhsJ6c_oa8bAS_fR3urXcvOj13NFnqaU9kwClmwOPV0FkyGImgJqG3DfUEMFESBYGB98_ttyyS6bNAv42iu5xggMftUElUE1kSZMaIs.AT1_5MNNtJR7-KZBGD1zaLOpJ8mFqcYsTj4iP-MoNd8DY0QK3a3rPFby9P6Hss_JYbKKc2MwLAm0uFr7YTX7tquTAdZE0xTsPHVSlHVbxzny8g_lJoh4kg9CTlx32HiatWjEmDYA8.AT1_5MNNtJR7";

        // Create map with your preferred basemap - restored working configuration
        const map = new Map({ 
          basemap: "topo-vector"  // Restored the working basemap that was displaying correctly
        });
        
        // Get map state from sessionStorage for center and zoom
        const mapStateObj = getMapStateFromSessionStorage();
        
        const view = new MapView({
          container: chatgisMapContainerRef.current,
          map,
          zoom: mapStateObj.zoom,  // Use zoom from sessionStorage
          center: mapStateObj.center,  // Use center from sessionStorage
          constraints: {
            rotationEnabled: false
          }
        });
        
        // Only set the California extent if using default center/zoom (no saved location)
        // This preserves user's saved map location while still constraining new users to California
        if (mapStateObj.center[0] === -119.30 && mapStateObj.center[1] === 37.30 && mapStateObj.zoom === 6) {
          // User has default center/zoom, so set the California extent
          const californiaExtent = {
            xmin: -124.50, // Western boundary (Pacific coast)
            ymin: 32.50,   // Southern boundary (near San Diego)
            xmax: -114.10, // Eastern boundary (Nevada border)
            ymax: 42.10,   // Northern boundary (near Oregon border)
            spatialReference: { wkid: 4326 } // WGS84 coordinate system
          };
          view.extent = californiaExtent;
        }
        // If user has saved a specific location, don't override with extent
        
        const graphicsLayer = new GraphicsLayer();
        map.add(graphicsLayer);

        // Store references
        chatgisMapViewRef.current = view;
        chatgisMapGraphicsLayerRef.current = graphicsLayer;

        // Restore marker from sessionStorage if it exists
        if (mapStateObj.marker) {
          const marker = mapStateObj.marker;
          const restoredGraphic = new Graphic({
            geometry: { type: 'point', longitude: marker.longitude, latitude: marker.latitude },
            symbol: {
              type: 'simple-marker',
              color: '#ff7f0e',
              size: '14px',
              outline: { color: '#ffffff', width: 1.5 }
            },
            attributes: { Name: marker.name },
            popupTemplate: { title: '{Name}' }
          });
          
          graphicsLayer.add(restoredGraphic);
          chatgisMapCurrentGraphicRef.current = restoredGraphic;
        }

      });
    } catch (error) {
      console.error('Error initializing ChatGIS map:', error);
    }
  }, [getMapStateFromSessionStorage]); // Need access to getMapStateFromSessionStorage

  const addOrReplaceChatgisMapMarker = useCallback((lon, lat, name, zoom) => {
    if (!chatgisMapViewRef.current || !chatgisMapGraphicsLayerRef.current || typeof window.require === 'undefined') {
      return;
    }
    
    try {
      // First, save the marker data to sessionStorage
      const currentMapState = getMapStateFromSessionStorage();
      const updatedMapState = {
        ...currentMapState,
        center: [lon, lat],
        zoom: zoom || 10,
        marker: {
          longitude: lon,
          latitude: lat,
          name: name,
          zoom: zoom || 10
        }
      };
      saveMapStateToSessionStorage(updatedMapState);
      
      // Then, read from sessionStorage and update the map
      const mapStateFromStorage = getMapStateFromSessionStorage();
      
      // Use the global require function for Graphic module
      window.require(["esri/Graphic"], (Graphic) => {
        if (chatgisMapCurrentGraphicRef.current) {
          chatgisMapGraphicsLayerRef.current.remove(chatgisMapCurrentGraphicRef.current);
        }
        
        const markerData = mapStateFromStorage.marker;
        chatgisMapCurrentGraphicRef.current = new Graphic({
          geometry: { type: 'point', longitude: markerData.longitude, latitude: markerData.latitude },
          symbol: {
            type: 'simple-marker',
            color: '#ff7f0e',
            size: '14px',
            outline: { color: '#ffffff', width: 1.5 }
          },
          attributes: { Name: markerData.name },
          popupTemplate: { title: '{Name}' }
        });
        
        chatgisMapGraphicsLayerRef.current.add(chatgisMapCurrentGraphicRef.current);
        chatgisMapViewRef.current.goTo({ 
          center: mapStateFromStorage.center, 
          zoom: mapStateFromStorage.zoom 
        });
        
      });
      
    } catch (error) {
      console.error('Error adding ChatGIS map marker:', error);
    }
  }, [getMapStateFromSessionStorage, saveMapStateToSessionStorage]);

  // Function to add click handlers to geo-links - simplified
  const addGeoLinkHandlers = useCallback(() => {
    const geoLinks = document.querySelectorAll('.geo-link');
    
    geoLinks.forEach(link => {
      link.addEventListener('click', function(ev) {
        ev.preventDefault();
        
        const lon = parseFloat(link.getAttribute('data-lon'));
        const lat = parseFloat(link.getAttribute('data-lat'));
        const name = link.textContent;
        const zoom = parseInt(link.getAttribute('data-zoom'));
        
        if (!isNaN(lon) && !isNaN(lat)) {
          addOrReplaceChatgisMapMarker(lon, lat, name, zoom);
        }
      });
    });
  }, [addOrReplaceChatgisMapMarker]);

  useEffect(() => {
    // Only proceed if user is authenticated
    if (!isAuthenticated) return;

    // Try to restore ChatGIS chat state from sessionStorage first
    const restored = loadChatGISState();

    if (!restored) {
      // Only fetch system prompt if no saved state exists (first visit)
      fetchSystemPrompt();
    }

    // No event listeners needed - sessionStorage naturally persists through page refresh
    // Only clear chat state when user explicitly logs out or clears chat
  }, [isAuthenticated, loadChatGISState]);

  // Load saved ChatGIS chats when authentication status changes
  useEffect(() => {
    if (isAuthenticated) {
      loadSavedChatGISChats();
    } else {
      // User logged out, clear ChatGIS chat state
      clearChatGISState();
      setMessages([]);
      setCurrentChatId(null);
    }
  }, [isAuthenticated, clearChatGISState, loadSavedChatGISChats]);

  // Set initial ChatGIS map state on DOM immediately when component mounts
  // This prevents the visual flash without breaking map display
  useEffect(() => {
    
    if (!isAuthenticated) return;
    
    // Apply saved map state to DOM immediately
    const chatgisMapContainer = document.querySelector('.chatgis-map-container');
    const chatgisMapToggleBtn = document.getElementById('chatgis-toggle-map');
    const mainContainer = document.querySelector('.chatbot-main');
    
    if (chatgisMapContainer && chatgisMapToggleBtn) {
      // Use the current mapState from React state, which should have been restored by loadChatGISState
      const currentState = mapState || 'minimized';
      
      console.log('Applying ChatGIS map state on mount:', currentState, 'from React state:', mapState);
      
      // Apply the current state
      applyMapState(chatgisMapContainer, chatgisMapToggleBtn, mainContainer, currentState);
    }
  }, [isAuthenticated, applyMapState, mapState]);

  // Load Esri API and initialize ChatGIS map - simplified for global require approach
  useEffect(() => {
    if (!isAuthenticated) return;

    // Check if Esri script is already loaded (global require function available)
    if (typeof window.require !== 'undefined') {
      // Don't initialize map here - wait for chat state to be loaded
    } else {
      // Wait for the script to load and require to become available
      const checkRequire = setInterval(() => {
        if (typeof window.require !== 'undefined') {
          clearInterval(checkRequire);
          // Don't initialize map here - wait for chat state to be loaded
        }
      }, 100);
    }
  }, [isAuthenticated]); // Removed initializeMap dependency

  // Initialize ChatGIS map only after chat state has been loaded
  useEffect(() => {
    if (isAuthenticated && typeof window.require !== 'undefined') {
      initializeChatgisMap();
    }
  }, [isAuthenticated, initializeChatgisMap]); // Removed isMapMinimized dependency

  // Set up ChatGIS map toggle functionality separately from map initialization
  useEffect(() => {
    if (!isAuthenticated) return;
    
    // Wait a bit for the map to be initialized and DOM to be ready
    const setupChatgisMapToggle = () => {
      const chatgisMapToggleBtn = document.getElementById('chatgis-toggle-map');
      const chatgisMapContainer = document.querySelector('.chatgis-map-container');
      
      if (chatgisMapToggleBtn && chatgisMapContainer) {
        
        // Don't apply map state here - it's already handled by the initial map state useEffect
        // Just set up the click handler functionality

        // Remove any existing event listeners by cloning the button
        const newChatgisMapToggleBtn = chatgisMapToggleBtn.cloneNode(true);
        chatgisMapToggleBtn.parentNode.replaceChild(newChatgisMapToggleBtn, chatgisMapToggleBtn);
        
        // Set up click handler with direct DOM manipulation
        newChatgisMapToggleBtn.addEventListener('click', function() {
          const mainContainer = document.querySelector('.chatbot-main');
          
          // Determine current state and cycle to next state
          let currentState = 'minimized';
          if (chatgisMapContainer.classList.contains('chatgis-maximized')) {
            currentState = 'maximized';
          } else if (chatgisMapContainer.classList.contains('chatgis-intermediate')) {
            currentState = 'intermediate';
          }
          
          // Cycle through states: minimized -> maximized -> intermediate -> minimized
          let newState;
          if (currentState === 'minimized') {
            newState = 'maximized';
          } else if (currentState === 'maximized') {
            newState = 'intermediate';
          } else {
            newState = 'minimized';
          }
          
          // Apply the new state
          applyMapState(chatgisMapContainer, newChatgisMapToggleBtn, mainContainer, newState);
          
          // Update React state
          setMapState(newState);
          
          // Save the updated map size to sessionStorage while preserving other map data
          const currentMapState = getMapStateFromSessionStorage();
          const updatedMapState = {
            ...currentMapState,
            size: newState
          };
          saveMapStateToSessionStorage(updatedMapState);
          
          // Force a layout reflow to ensure proper chat area adjustment
          setTimeout(() => {
            const chatMessages = document.querySelector('.chat-messages');
            if (chatMessages) {
              chatMessages.scrollTop = chatMessages.scrollHeight;
            }
          }, 50);
        });
        
      } else {
        setTimeout(setupChatgisMapToggle, 100);
      }
    };
    
         // Start setup after a short delay to ensure DOM is ready
     setTimeout(setupChatgisMapToggle, 200);
   }, [isAuthenticated, applyMapState, mapState, getMapStateFromSessionStorage, saveMapStateToSessionStorage]);

  // Add click handlers to geo-links after messages are rendered
  useEffect(() => {
    if (messages.length > 0) {
      // Small delay to ensure DOM is updated
      setTimeout(addGeoLinkHandlers, 100);
    }
  }, [messages, addGeoLinkHandlers]);

  // Clear chat state when authentication status changes
  useEffect(() => {
    
    if (!isAuthenticated) {
      // User logged out, clear chat state (this already handles map state reset)
      clearChatGISState();
      setMessages([]);
      setCurrentChatId(null);
    } else {
      // User logged in - ensure map state is initialized with default California center/zoom
      const mapStateObj = getMapStateFromSessionStorage();
      if (!mapStateObj || !mapStateObj.center) {
        // Initialize with default California center/zoom 
        const defaultMapState = {
          size: 'minimized',
          center: [-119.30, 37.30],
          zoom: 6,
          marker: null
        };
        saveMapStateToSessionStorage(defaultMapState);
        setMapState('minimized');
      } else {
        // Set the React state to match the sessionStorage size
        setMapState(mapStateObj.size);
      }
    }
  }, [isAuthenticated, clearChatGISState, getMapStateFromSessionStorage, saveMapStateToSessionStorage]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    const chatMessages = document.querySelector('.chat-messages');
    if (chatMessages) {
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  }, [messages, loading]);

  // Auto-focus text input after AI response
  useEffect(() => {
    if (!loading && messages.length > 0) {
      const textarea = document.querySelector('.chat-input textarea');
      if (textarea) {
        textarea.focus();
      }
    }
  }, [loading, messages.length]);

  // Save ChatGIS chat state whenever messages change (except during loading)
  useEffect(() => {
    if (!loading && messages.length > 0) {
      saveChatGISState(messages);
    }
  }, [messages, loading, saveChatGISState]);

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;
    if (!isAuthenticated) {
      console.error('User not authenticated');
      return;
    }

    // Store the original input message for the API call
    const originalMessage = inputMessage;
    setInputMessage('');
    setLoading(true);

    try {
      // Use the current system prompt from state - no need to fetch on every message
      const chatHistory = [
        { role: 'system', content: systemPrompt },
        ...messages.filter(msg => msg.role !== 'system')
      ];
      
      // Get ChatGIS areas of interest from Settings page sessionStorage
      const userSettings = sessionStorage.getItem('userSettings');
      let chatgisAreasOfInterest = null; // Default to no areas of interest
      
      if (userSettings) {
        try {
          const parsed = JSON.parse(userSettings);
          
          // Get ChatGIS areas of interest from settings
          if (parsed.chatGIS?.enableAreasOfInterest === true && parsed.chatGIS?.areas) {
            // Filter out null areas, only include enabled areas, and format for backend API
            chatgisAreasOfInterest = parsed.chatGIS.areas
              .filter(area => area !== null && area.enabled === true)
              .map(area => ({
                min_lat: parseFloat(area.coordinates?.minLat || 0),
                max_lat: parseFloat(area.coordinates?.maxLat || 0),
                min_lon: parseFloat(area.coordinates?.minLon || 0),
                max_lon: parseFloat(area.coordinates?.maxLon || 0)
              }))
              // Filter out invalid coordinates (0,0 areas are not valid geographic areas)
              .filter(area => 
                area.min_lat !== 0 || area.max_lat !== 0 || 
                area.min_lon !== 0 || area.max_lon !== 0
              )
              // Filter out any coordinates that are NaN
              .filter(area => 
                !isNaN(area.min_lat) && !isNaN(area.max_lat) && 
                !isNaN(area.min_lon) && !isNaN(area.max_lon)
              );
            
            // If no valid areas found, set to null
            if (chatgisAreasOfInterest.length === 0) {
              chatgisAreasOfInterest = [];
            }
            
            console.log('ChatGIS Areas of Interest from settings:', chatgisAreasOfInterest);
          } else {
            console.log('ChatGIS Areas of Interest disabled or not configured');
          }
        } catch (error) {
          console.error('Error parsing user settings for ChatGIS areas:', error);
        }
      }

      const response = await apiClient.post('/chat/gis', {
        message: originalMessage,
        chat_history: chatHistory,
        areas_of_interest: chatgisAreasOfInterest
      });

      // Use the enhanced user message from the response if available
      const enhancedUserMessage = response.data.enhanced_user_message || originalMessage;
      const userMessage = { role: 'user', content: enhancedUserMessage };
      
      const assistantMessage = { role: 'assistant', content: response.data.message };
      const updatedMessages = [...messages, userMessage, assistantMessage];
      setMessages(updatedMessages);
      
      // Save ChatGIS chat state after each message to preserve across navigation
      saveChatGISState(updatedMessages);
    } catch (error) {
      console.error('Chat failed:', error);
      // On error, add the original user message and error message
      const userMessage = { role: 'user', content: originalMessage };
      const errorMessage = { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' };
      const messagesWithError = [...messages, userMessage, errorMessage];
      setMessages(messagesWithError);
      // Save ChatGIS chat state even with error message
      saveChatGISState(messagesWithError);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const saveChat = async () => {
    if (!chatTitle.trim()) return;

    try {
      // Include the system prompt when saving to preserve the exact prompt used
      // This allows us to restore the exact system prompt when loading the chat later
      const chatMessages = messages; // Include all messages including system prompt
              await apiClient.post('/chats/save', {
        chatname: chatTitle,
        messages: chatMessages
      });

      setShowSaveForm(false);
      setChatTitle('');
      setAuthError(false); // Clear any previous auth errors
      loadSavedChatGISChats();
    } catch (error) {
      console.error('Failed to save chat:', error);
    }
  };

  const loadChat = async (chatId) => {
    try {
      const response = await apiClient.get(`/chats/saved/${chatId}`);
      
      // Use the system prompt that was saved with the chat (first message)
      // This preserves the exact system prompt used when the chat was created
      const savedMessages = response.data.messages || response.data;
      const systemMessage = savedMessages.find(msg => msg.role === 'system');
      
      if (systemMessage) {
        // Use the saved system prompt
        setSystemPrompt(systemMessage.content);
        setMessages(savedMessages);
        // Save the loaded ChatGIS chat state
        saveChatGISState(savedMessages);
      } else {
        // Fallback: use current system prompt if none was saved
        const fallbackMessages = [
          { role: 'system', content: systemPrompt },
          ...savedMessages
        ];
        setMessages(fallbackMessages);
        // Save the fallback ChatGIS chat state
        saveChatGISState(fallbackMessages);
        // Also update the system prompt state to match what we're using
        setSystemPrompt(systemPrompt);
      }
      
      setCurrentChatId(chatId);
    } catch (error) {
      console.error('Failed to load chat:', error);
    }
  };

  const deleteChat = async (chatId) => {
    if (!window.confirm('Are you sure you want to delete this chat?')) return;

    try {
              await apiClient.delete(`/chats/saved/${chatId}`);
      loadSavedChatGISChats();
      if (currentChatId === chatId) {
        setCurrentChatId(null);
      }
    } catch (error) {
      console.error('Failed to delete chat:', error);
    }
  };

  const clearChat = () => {
    // Clear current chat ID and input
    setCurrentChatId(null);
    setInputMessage('');
    
    // Reset map to default state and remove marker
    const defaultMapState = {
      size: 'minimized',
      center: [-119.30, 37.30],
      zoom: 6,
      marker: null
    };
    saveMapStateToSessionStorage(defaultMapState);
    
    // Also immediately minimize the map in the DOM
    const chatgisMapContainer = document.querySelector('.chatgis-map-container');
    const chatgisMapToggleBtn = document.getElementById('chatgis-toggle-map');
    const mainContainer = document.querySelector('.chatbot-main');
    
    if (chatgisMapContainer && chatgisMapToggleBtn) {
      // Apply minimized state to DOM immediately using the helper function
      applyMapState(chatgisMapContainer, chatgisMapToggleBtn, mainContainer, 'minimized');
    }
    
    // Clear any existing marker
    if (chatgisMapCurrentGraphicRef.current && chatgisMapGraphicsLayerRef.current) {
      chatgisMapGraphicsLayerRef.current.remove(chatgisMapCurrentGraphicRef.current);
      chatgisMapCurrentGraphicRef.current = null;
    }
    
    // Clear the chat state from sessionStorage
    clearChatGISState();
    
    // Reset to just system prompt
    const systemMessages = messages.filter(msg => msg.role === 'system');
    if (systemMessages.length > 0) {
      setMessages(systemMessages);
      // Save the minimal state back to sessionStorage
      saveChatGISState(systemMessages);
    } else {
      // If no system message, create a minimal one
      const minimalMessages = [
        {
          role: 'system',
          content: systemPrompt || 'You are a GIS expert assistant.'
        }
      ];
      setMessages(minimalMessages);
      saveChatGISState(minimalMessages);
    }
  };

  return (
    <div className="chatbot-container">
      {!isAuthenticated ? (
        <div className="auth-required-message">
          <h3>Authentication Required</h3>
          <p>Please log in to access the ChatGIS system.</p>
        </div>
      ) : (
        <>
          <div className="chatbot-sidebar">
            <div className="sidebar-section">
              <h3>Chat Controls</h3>
              
              <div className="control-group">
                <label>
                  <input
                    type="checkbox"
                    checked={geoNEREnabled}
                    onChange={(e) => setGeoNEREnabled(e.target.checked)}
                  />
                  Enable GeoLinks
                </label>
                <small>Toggle geographic entity detection & map links</small>
              </div>

              <button onClick={() => setShowSaveForm(true)} className="sidebar-btn">
                Save Chat
              </button>
              <button onClick={clearChat} className="sidebar-btn">
                Clear Chat
              </button>
            </div>

            <div className="sidebar-section">
              <h3>Saved Chats</h3>
              {authError ? (
                <div className="auth-error">
                  <p>⚠️ Authentication error loading saved chats</p>
                  <p>Please try logging in again</p>
                  <button onClick={() => window.location.href = '/login'} className="sidebar-btn">
                    Go to Login
                  </button>
                </div>
              ) : savedChats.length === 0 ? (
                <p>No saved chats yet.</p>
              ) : (
                <div className="saved-chats-list">
                  {savedChats.map((chat) => (
                    <div key={chat.chat_id} className="saved-chat-item">
                      <button
                        onClick={() => loadChat(chat.chat_id)}
                        className="load-chat-btn"
                      >
                        📄 {chat.chatname}
                      </button>
                      <button
                        onClick={() => deleteChat(chat.chat_id)}
                        className="delete-chat-btn"
                        title="Delete chat"
                      >
                        🗑️
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="chatbot-main">
            <div className="chat-messages">
              {messages.filter(msg => msg.role !== 'system').map((message, index) => (
                <div key={index} className={`message ${message.role}`}>
                  <div className="message-avatar">
                    {message.role === 'user' ? '👤' : '🤖'}
                  </div>
                  <div className="message-content">
                    <div 
                      className="message-text"
                      dangerouslySetInnerHTML={{ __html: displayGeotaggedText(message.content) }}
                    />
                  </div>
                </div>
              ))}
              {loading && (
                <div className="message assistant">
                  <div className="message-avatar">🤖</div>
                  <div className="message-content">
                    <div className="loading-indicator">Thinking...</div>
                  </div>
                </div>
              )}
            </div>

            <div className="chatgis-map-container">
              <div ref={chatgisMapContainerRef} id="chatgisMapView"></div>
              <button type="button" id="chatgis-toggle-map" className="chatgis-map-toggle-btn" title="Click to expand map">
                <span className="chatgis-minimize-icon">🗗</span>
                <span className="chatgis-restore-icon" style={{ display: 'none' }}>🗖</span>
              </button>
            </div>

            <div className="chat-input">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="How can I help?"
                rows={2}
                disabled={loading}
              />
              <button 
                onClick={sendMessage} 
                disabled={loading || !inputMessage.trim()}
                className="send-btn"
              >
                Send
              </button>
            </div>
          </div>

          {showSaveForm && (
            <div className="save-chat-modal">
              <div className="modal-content">
                <h3>Save Chat</h3>
                <input
                  type="text"
                  value={chatTitle}
                  onChange={(e) => setChatTitle(e.target.value)}
                  placeholder="Enter a title for this chat"
                  className="chat-title-input"
                />
                <div className="modal-buttons">
                  <button onClick={saveChat} className="save-btn">
                    Save
                  </button>
                  <button onClick={() => setShowSaveForm(false)} className="cancel-btn">
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Chatbot; 
