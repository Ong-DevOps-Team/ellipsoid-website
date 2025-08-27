import React, { useState, useEffect, useCallback, useRef } from 'react';
import apiClient from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';
import './RAGChatbot.css';

function RAGChatbot() {
  const { isAuthenticated } = useAuth();
  
  // Helper function to convert display names to model ARNs
  const getModelArn = (modelName) => {
    const modelMap = {
      'Amazon Nova Lite': 'arn:aws:bedrock:us-west-2:854669816847:inference-profile/us.amazon.nova-lite-v1:0',
      'Claude 3.5 Sonnet v2': 'arn:aws:bedrock:us-west-2:854669816847:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0'
    };
    return modelMap[modelName] || modelName; // Return ARN if found, otherwise return as-is
  };
  
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [geoNEREnabled, setGeoNEREnabled] = useState(true);
  const [sessionId, setSessionId] = useState(null);
  // Map state management - using sessionStorage-first approach
  const [mapState, setMapState] = useState(() => {
    // Initialize map state from sessionStorage or default to minimized
    const savedMapState = sessionStorage.getItem('rag_map_state');
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
  
  // GeoRAG Map references
  const georagMapContainerRef = useRef(null);
  const georagMapViewRef = useRef(null);
  const georagMapGraphicsLayerRef = useRef(null);
  const georagMapCurrentGraphicRef = useRef(null);

  // Map state management helper functions
  const getMapStateFromSessionStorage = useCallback(() => {
    try {
      const savedMapState = sessionStorage.getItem('rag_map_state');
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
      sessionStorage.setItem('rag_map_state', JSON.stringify(mapStateObj));
    } catch (error) {
      console.error('Error saving map state to sessionStorage:', error);
    }
  }, []);

  // Chat state persistence functions
  const saveChatState = useCallback((chatMessages, currentSessionId) => {
    try {
      sessionStorage.setItem('rag_chat_messages', JSON.stringify(chatMessages));
      sessionStorage.setItem('rag_session_id', currentSessionId || '');
      sessionStorage.setItem('rag_geo_ner_enabled', JSON.stringify(geoNEREnabled));
      // Map state is now saved separately via saveMapStateToSessionStorage
    } catch (error) {
      console.error('Failed to save RAG chat state:', error);
    }
  }, [geoNEREnabled]);

  const loadChatState = useCallback(() => {
    try {
      const savedMessages = sessionStorage.getItem('rag_chat_messages');
      const savedSessionId = sessionStorage.getItem('rag_session_id');
      const savedGeoNER = sessionStorage.getItem('rag_geo_ner_enabled');
      const mapStateObj = getMapStateFromSessionStorage();
      
      console.log('Loading chat state from sessionStorage:', {
        messages: savedMessages ? 'found' : 'not found',
        sessionId: savedSessionId,
        geoNER: savedGeoNER,
        mapState: mapStateObj
      });
      
      if (savedMessages) {
        const messages = JSON.parse(savedMessages);
        setMessages(messages);
        
        if (savedSessionId) {
          setSessionId(savedSessionId);
        }
        
        if (savedGeoNER) {
          setGeoNEREnabled(JSON.parse(savedGeoNER));
        }
        
        // Set map size state from sessionStorage object
        setMapState(mapStateObj.size);
        
        console.log('Successfully restored chat state, mapState set to:', mapStateObj.size);
        return true; // Successfully restored
      }
      console.log('No saved chat state found');
      return false; // No saved state
    } catch (error) {
      console.error('Failed to load RAG chat state:', error);
      return false;
    }
  }, [getMapStateFromSessionStorage]);

  const clearChatState = useCallback(() => {
    try {
      sessionStorage.removeItem('rag_chat_messages');
      sessionStorage.removeItem('rag_session_id');
      sessionStorage.removeItem('rag_geo_ner_enabled');
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
      console.error('Failed to clear RAG chat state:', error);
    }
  }, [saveMapStateToSessionStorage]);

  // Helper function to apply map state - moved up to fix ESLint warning
  const applyMapState = useCallback((container, button, mainContainer, state) => {
    // Remove all existing state classes
    container.classList.remove('georag-minimized', 'georag-intermediate', 'georag-maximized');
    
    if (state === 'minimized') {
      container.style.height = '60px';
      button.title = 'Click to expand map';
      container.classList.add('georag-minimized');
      
      if (mainContainer) {
        mainContainer.classList.remove('map-expanded', 'map-intermediate');
        mainContainer.classList.add('map-minimized');
      }
      
      const minimizeIcon = button.querySelector('.georag-minimize-icon');
      const restoreIcon = button.querySelector('.georag-restore-icon');
      if (minimizeIcon) minimizeIcon.style.display = 'inline';
      if (restoreIcon) restoreIcon.style.display = 'none';
      
    } else if (state === 'intermediate') {
      container.style.height = '280px';
      button.title = 'Click to minimize map';
      container.classList.add('georag-intermediate');
      
      if (mainContainer) {
        mainContainer.classList.remove('map-minimized', 'map-expanded');
        mainContainer.classList.add('map-intermediate');
      }
      
      const minimizeIcon = button.querySelector('.georag-minimize-icon');
      const restoreIcon = button.querySelector('.georag-restore-icon');
      if (minimizeIcon) minimizeIcon.style.display = 'inline';
      if (restoreIcon) restoreIcon.style.display = 'none';
      
    } else if (state === 'maximized') {
      container.style.height = '500px';
      button.title = 'Click to reduce map';
      container.classList.add('georag-maximized');
      
      if (mainContainer) {
        mainContainer.classList.remove('map-minimized', 'map-intermediate');
        mainContainer.classList.add('map-expanded');
      }
      
      const minimizeIcon = button.querySelector('.georag-minimize-icon');
      const restoreIcon = button.querySelector('.georag-restore-icon');
      if (minimizeIcon) minimizeIcon.style.display = 'none';
      if (restoreIcon) restoreIcon.style.display = 'inline';
    }
  }, []);

  // Monitor authentication state changes
  useEffect(() => {
    // Removed debugging useEffect
  }, [isAuthenticated]);

  // Set initial GeoRAG map state on DOM immediately when component mounts
  // This prevents the visual flash without breaking map display
  useEffect(() => {
    
    if (!isAuthenticated) return;
    
    // Apply saved map state to DOM immediately
    const georagMapContainer = document.querySelector('.georag-map-container');
    const georagMapToggleBtn = document.getElementById('georag-toggle-map');
    const mainContainer = document.querySelector('.rag-chatbot-main');
    
    if (georagMapContainer && georagMapToggleBtn) {
      // Use the current mapState from React state, which should have been restored by loadChatState
      const currentState = mapState || 'minimized';
      
      console.log('Applying map state on mount:', currentState, 'from React state:', mapState);
      
      // Apply the current state
      applyMapState(georagMapContainer, georagMapToggleBtn, mainContainer, currentState);
    }
  }, [isAuthenticated, applyMapState, mapState]);

  // GeoRAG Map functionality - simplified approach using direct DOM manipulation
  const initializeGeoragMap = useCallback(() => {
    if (!georagMapContainerRef.current) {
      return;
    }

    // Check if require function is available (global function from Esri script)
    if (typeof window.require === 'undefined') {
      setTimeout(initializeGeoragMap, 500);
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
          container: georagMapContainerRef.current,
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
        georagMapViewRef.current = view;
        georagMapGraphicsLayerRef.current = graphicsLayer;

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
          georagMapCurrentGraphicRef.current = restoredGraphic;
        }

      });
    } catch (error) {
      console.error('Error initializing GeoRAG map:', error);
    }
  }, [getMapStateFromSessionStorage]); // Need access to getMapStateFromSessionStorage

  

  // Set up GeoRAG map toggle functionality separately from map initialization
  useEffect(() => {
    if (!isAuthenticated) return;
    
    // Wait a bit for the map to be initialized and DOM to be ready
    const setupGeoragMapToggle = () => {
      const georagMapToggleBtn = document.getElementById('georag-toggle-map');
      const georagMapContainer = document.querySelector('.georag-map-container');
      
      if (georagMapToggleBtn && georagMapContainer) {
        
        // Don't apply map state here - it's already handled by the initial map state useEffect
        // Just set up the click handler functionality

        // Remove any existing event listeners by cloning the button
        const newGeoragMapToggleBtn = georagMapToggleBtn.cloneNode(true);
        georagMapToggleBtn.parentNode.replaceChild(newGeoragMapToggleBtn, georagMapToggleBtn);
        
        // Set up click handler with direct DOM manipulation
        newGeoragMapToggleBtn.addEventListener('click', function() {
          const mainContainer = document.querySelector('.rag-chatbot-main');
          
          // Determine current state and cycle to next state
          let currentState = 'minimized';
          if (georagMapContainer.classList.contains('georag-maximized')) {
            currentState = 'maximized';
          } else if (georagMapContainer.classList.contains('georag-intermediate')) {
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
          applyMapState(georagMapContainer, newGeoragMapToggleBtn, mainContainer, newState);
          
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
        setTimeout(setupGeoragMapToggle, 100);
      }
    };
    
         // Start setup after a short delay to ensure DOM is ready
     setTimeout(setupGeoragMapToggle, 200);
   }, [isAuthenticated, applyMapState, mapState, getMapStateFromSessionStorage, saveMapStateToSessionStorage]);

  const addOrReplaceGeoragMapMarker = useCallback((lon, lat, name, zoom) => {
    if (!georagMapViewRef.current || !georagMapGraphicsLayerRef.current || typeof window.require === 'undefined') {
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
        if (georagMapCurrentGraphicRef.current) {
          georagMapGraphicsLayerRef.current.remove(georagMapCurrentGraphicRef.current);
        }
        
        const markerData = mapStateFromStorage.marker;
        georagMapCurrentGraphicRef.current = new Graphic({
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
        
        georagMapGraphicsLayerRef.current.add(georagMapCurrentGraphicRef.current);
        georagMapViewRef.current.goTo({ 
          center: mapStateFromStorage.center, 
          zoom: mapStateFromStorage.zoom 
        });
        
      });
      
    } catch (error) {
      console.error('Error adding GeoRAG map marker:', error);
    }
  }, [getMapStateFromSessionStorage, saveMapStateToSessionStorage]);

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
          addOrReplaceGeoragMapMarker(lon, lat, name, zoom);
        }
      });
    });
  }, [addOrReplaceGeoragMapMarker]);

  // Load Esri API and initialize GeoRAG map - simplified for global require approach
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

  // Initialize GeoRAG map only after chat state has been loaded
  useEffect(() => {
    if (isAuthenticated && typeof window.require !== 'undefined') {
      initializeGeoragMap();
    }
  }, [isAuthenticated, initializeGeoragMap]); // Removed isMapMinimized dependency

  // Add click handlers to geo-links after messages are rendered
  useEffect(() => {
    if (messages.length > 0) {
      // Small delay to ensure DOM is updated
      setTimeout(addGeoLinkHandlers, 100);
    }
  }, [messages, addGeoLinkHandlers]);

  // Removed map state management useEffects - using direct DOM approach instead

  useEffect(() => {
    // Try to restore chat state from sessionStorage first
    const restored = loadChatState();
    
    if (!restored) {
      // Only initialize with empty state if no saved state exists (first visit)
      setMessages([]);
      setSessionId(null);
    }

    // No event listeners needed - sessionStorage naturally persists through page refresh
    // Only clear chat state when user explicitly logs out or clears chat
  }, [loadChatState]);

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

  // Save chat state whenever messages change (except during loading)
  useEffect(() => {
    if (!loading && messages.length > 0) {
      saveChatState(messages, sessionId);
    }
  }, [messages, loading, sessionId, saveChatState]);

  // Save chat state when settings change (model, geoNER)
  useEffect(() => {
    if (messages.length > 0) {
      saveChatState(messages, sessionId);
    }
  }, [geoNEREnabled, messages, sessionId, saveChatState]);

  // Map state is now saved directly in functions, no separate useEffect needed

  // Clear chat state when authentication status changes
  useEffect(() => {
    
    if (!isAuthenticated) {
      // User logged out, clear chat state (this already handles map state reset)
      clearChatState();
      setMessages([]);
      setSessionId(null);
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
  }, [isAuthenticated, clearChatState, getMapStateFromSessionStorage, saveMapStateToSessionStorage]);

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
      // Get model selection from Settings page sessionStorage
      const userSettings = sessionStorage.getItem('userSettings');
      let selectedModel = getModelArn('Amazon Nova Lite'); // Default fallback
      let areasOfInterest = null; // Default to no areas of interest
      
      if (userSettings) {
        try {
          const parsed = JSON.parse(userSettings);
          selectedModel = getModelArn(parsed.geoRAG?.selectedModel || 'Amazon Nova Lite');
          
          // Get areas of interest from settings
          if (parsed.geoRAG?.enableAreasOfInterest === true && parsed.geoRAG?.areas) {
            // Filter out null areas, only include enabled areas, and format for backend API
            areasOfInterest = parsed.geoRAG.areas
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
            if (areasOfInterest.length === 0) {
              areasOfInterest = [];
            }
            
            console.log('Areas of Interest from settings:', areasOfInterest);
          } else {
            console.log('Areas of Interest disabled or not configured');
          }
        } catch (error) {
          console.error('Error parsing user settings:', error);
        }
      }

      console.log('Sending RAG chat request with areas_of_interest:', areasOfInterest);
      console.log('Full request payload:', {
        message: originalMessage,
        chat_history: messages,
        model_id: selectedModel,
        session_id: sessionId,
        areas_of_interest: areasOfInterest
      });

      const response = await apiClient.post('/chat/rag', {
        message: originalMessage,
        chat_history: messages,
        model_id: selectedModel,
        session_id: sessionId,
        areas_of_interest: areasOfInterest
      });

      // Use the enhanced user message from the response if available
      const enhancedUserMessage = response.data.enhanced_user_message || originalMessage;
      const userMessage = { role: 'user', content: enhancedUserMessage };
      
      const assistantMessage = { role: 'assistant', content: response.data.message };
      const updatedMessages = [...messages, userMessage, assistantMessage];
      setMessages(updatedMessages);
      
      // Update session ID if provided in response
      let updatedSessionId = sessionId;
      if (response.data.session_id) {
        updatedSessionId = response.data.session_id;
        setSessionId(updatedSessionId);
      }
      
      // Save chat state after each message to preserve across navigation
      saveChatState(updatedMessages, updatedSessionId);
    } catch (error) {
      console.error('RAG chat failed:', error);
      // On error, add the original user message and error message
      const userMessage = { role: 'user', content: originalMessage };
      const errorMessage = { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' };
      const messagesWithError = [...messages, userMessage, errorMessage];
      setMessages(messagesWithError);
      // Save chat state even with error message
      saveChatState(messagesWithError, sessionId);
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

  const clearChat = () => {
    setMessages([]);
    setInputMessage('');
    setSessionId(null);
    
    // Reset map to default state and remove marker
    const defaultMapState = {
      size: 'minimized',
      center: [-119.30, 37.30],
      zoom: 6,
      marker: null
    };
    saveMapStateToSessionStorage(defaultMapState);
    
    // Also immediately minimize the map in the DOM
    const georagMapContainer = document.querySelector('.georag-map-container');
    const georagMapToggleBtn = document.getElementById('georag-toggle-map');
    const mainContainer = document.querySelector('.rag-chatbot-main');
    
    if (georagMapContainer && georagMapToggleBtn) {
      // Apply minimized state to DOM immediately using the helper function
      applyMapState(georagMapContainer, georagMapToggleBtn, mainContainer, 'minimized');
    }
    
    // Clear any existing marker
    if (georagMapCurrentGraphicRef.current && georagMapGraphicsLayerRef.current) {
      georagMapGraphicsLayerRef.current.remove(georagMapCurrentGraphicRef.current);
      georagMapCurrentGraphicRef.current = null;
    }
    
    clearChatState();
  };

  return (
    <div className="rag-chatbot-container">
      
      {!isAuthenticated ? (
        <div className="auth-required-message">
          <h3>Authentication Required</h3>
          <p>Please log in to access the GeoRAG system.</p>
        </div>
      ) : (
        <>
          <div className="rag-chatbot-sidebar">
            <div className="sidebar-section">
              <h3>RAG Controls</h3>
              
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

              <button onClick={clearChat} className="sidebar-btn">
                Clear Chat
              </button>
            </div>

            <div className="sidebar-section">
              <h3>About GeoRAG</h3>
            </div>
          </div>

          <div className="rag-chatbot-main">
            <div className="chat-messages">
              
              {messages.map((message, index) => (
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
                    <div className="loading-indicator">Retrieving and generating response...</div>
                  </div>
                </div>
              )}
            </div>

            <div className="georag-map-container">
              <div ref={georagMapContainerRef} id="georagMapView"></div>
              <button type="button" id="georag-toggle-map" className="georag-map-toggle-btn" title="Click to expand map">
                <span className="georag-minimize-icon">🗗</span>
                <span className="georag-restore-icon" style={{ display: 'none' }}>🗖</span>
              </button>
            </div>

            <div className="chat-input">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about your documents..."
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
        </>
      )}
    </div>
  );
}

export default RAGChatbot;
