import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import apiClient from '../services/apiService';
import './Settings.css';

function Settings() {
  const { isAuthenticated, currentUser } = useAuth();
  
  // ChatGIS Settings
  const [salutation, setSalutation] = useState('none specified');
  
  // ChatGIS Areas of Interest Settings
  const [chatgisEnableAreasOfInterest, setChatgisEnableAreasOfInterest] = useState(false);
  const [chatgisArea2Enabled, setChatgisArea2Enabled] = useState(false);
  const [chatgisArea3Enabled, setChatgisArea3Enabled] = useState(false);
  
  // ChatGIS Area coordinates - all start at 0 for consistent positioning
  const [chatgisArea1, setChatgisArea1] = useState({
    minLat: 0,
    maxLat: 0,
    minLon: 0,
    maxLon: 0
  });
  
  const [chatgisArea2, setChatgisArea2] = useState({
    minLat: 0,
    maxLat: 0,
    minLon: 0,
    maxLon: 0
  });
  
  const [chatgisArea3, setChatgisArea3] = useState({
    minLat: 0,
    maxLat: 0,
    minLon: 0,
    maxLon: 0
  });

  // ChatGIS Selected predefined areas
  const [chatgisSelectedArea1, setChatgisSelectedArea1] = useState('custom');
  const [chatgisSelectedArea2, setChatgisSelectedArea2] = useState('custom');
  const [chatgisSelectedArea3, setChatgisSelectedArea3] = useState('custom');
  
  // GeoRAG Settings
  const [selectedModel, setSelectedModel] = useState('arn:aws:bedrock:us-west-2:854669816847:inference-profile/us.amazon.nova-lite-v1:0');
  const [enableAreasOfInterest, setEnableAreasOfInterest] = useState(false);
  const [area2Enabled, setArea2Enabled] = useState(false);
  const [area3Enabled, setArea3Enabled] = useState(false);
  
  // Area coordinates - all start at 0 for consistent positioning
  const [area1, setArea1] = useState({
    minLat: 0,
    maxLat: 0,
    minLon: 0,
    maxLon: 0
  });
  
  const [area2, setArea2] = useState({
    minLat: 0,
    maxLat: 0,
    minLon: 0,
    maxLon: 0
  });
  
  const [area3, setArea3] = useState({
    minLat: 0,
    maxLat: 0,
    minLon: 0,
    maxLon: 0
  });

  // Predefined areas of interest
  const predefinedAreas = {
    'oceanside-ca': {
      minLat: 33.1234,
      maxLat: 33.3456,
      minLon: -117.4567,
      maxLon: -117.2345
    },
    'san-diego-county': {
      minLat: 32.4567,
      maxLat: 33.5678,
      minLon: -117.6789,
      maxLon: -116.0123
    },
    'california': {
      minLat: 32.4567,
      maxLat: 42.0123,
      minLon: -124.5678,
      maxLon: -114.0123
    },
    'texas': {
      minLat: 26.0123,
      maxLat: 36.5678,
      minLon: -106.7890,
      maxLon: -93.4567
    },
    'new-york': {
      minLat: 40.4567,
      maxLat: 45.0123,
      minLon: -79.8901,
      maxLon: -71.7890
    }
  };

  // Selected predefined areas
  const [selectedArea1, setSelectedArea1] = useState('custom');
  const [selectedArea2, setSelectedArea2] = useState('custom');
  const [selectedArea3, setSelectedArea3] = useState('custom');

  // Save functionality state
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');
  const [saveMessageType, setSaveMessageType] = useState('success');
  
  // Flag to track if initial settings have been loaded
  const [isInitialLoadComplete, setIsInitialLoadComplete] = useState(false);

  // Helper function to migrate old display names to model ARNs
  const migrateModelSelection = (modelName) => {
    const modelMap = {
      'Amazon Nova Lite': 'arn:aws:bedrock:us-west-2:854669816847:inference-profile/us.amazon.nova-lite-v1:0',
      'Claude 3.5 Sonnet v2': 'arn:aws:bedrock:us-west-2:854669816847:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0'
    };
    return modelMap[modelName] || modelName; // Return ARN if found, otherwise return as-is
  };

  // Load settings from sessionStorage on component mount
  useEffect(() => {
    const loadSettingsFromStorage = () => {
      try {
        const savedSettings = sessionStorage.getItem('userSettings');
        if (savedSettings) {
          const parsed = JSON.parse(savedSettings);
          
          // Update ChatGIS settings
          if (parsed.chatGIS?.salutation) {
            setSalutation(parsed.chatGIS.salutation);
          }
          
          // Update ChatGIS Areas of Interest settings
          if (parsed.chatGIS?.enableAreasOfInterest !== undefined) {
            setChatgisEnableAreasOfInterest(parsed.chatGIS.enableAreasOfInterest);
          }
          
          // Update ChatGIS areas
          if (parsed.chatGIS?.areas && Array.isArray(parsed.chatGIS.areas)) {
            const chatgisAreas = parsed.chatGIS.areas;
            
            if (chatgisAreas[0]) {
              setChatgisArea1(chatgisAreas[0].coordinates || { minLat: 0, maxLat: 0, minLon: 0, maxLon: 0 });
              setChatgisSelectedArea1(chatgisAreas[0].presetArea || 'custom');
            }
            
            if (chatgisAreas[1]) {
              setChatgisArea2(chatgisAreas[1].coordinates || { minLat: 0, maxLat: 0, minLon: 0, maxLon: 0 });
              setChatgisArea2Enabled(chatgisAreas[1].enabled || false);
              setChatgisSelectedArea2(chatgisAreas[1].presetArea || 'custom');
            }
            
            if (chatgisAreas[2]) {
              setChatgisArea3(chatgisAreas[2].coordinates || { minLat: 0, maxLat: 0, minLon: 0, maxLon: 0 });
              setChatgisArea3Enabled(chatgisAreas[2].enabled || false);
              setChatgisSelectedArea3(chatgisAreas[2].presetArea || 'custom');
            }
          }
          
          // Update GeoRAG settings
          if (parsed.geoRAG?.selectedModel) {
            setSelectedModel(migrateModelSelection(parsed.geoRAG.selectedModel));
          }
          
          if (parsed.geoRAG?.enableAreasOfInterest !== undefined) {
            setEnableAreasOfInterest(parsed.geoRAG.enableAreasOfInterest);
          }
          
          // Update areas
          if (parsed.geoRAG?.areas && Array.isArray(parsed.geoRAG.areas)) {
            const areas = parsed.geoRAG.areas;
            
            if (areas[0]) {
              setArea1(areas[0].coordinates || { minLat: 0, maxLat: 0, minLon: 0, maxLon: 0 });
              setSelectedArea1(areas[0].presetArea || 'custom');
            }
            
            if (areas[1]) {
              setArea2(areas[1].coordinates || { minLat: 0, maxLat: 0, minLon: 0, maxLon: 0 });
              setArea2Enabled(areas[1].enabled || false);
              setSelectedArea2(areas[1].presetArea || 'custom');
            }
            
            if (areas[2]) {
              setArea3(areas[2].coordinates || { minLat: 0, maxLat: 0, minLon: 0, maxLon: 0 });
              setArea3Enabled(areas[2].enabled || false);
              setSelectedArea3(areas[2].presetArea || 'custom');
            }
          }
        }
      } catch (error) {
        console.error('Error loading settings from sessionStorage:', error);
      }
    };

    loadSettingsFromStorage();
    // Mark initial load as complete after a brief delay to ensure all setState calls have completed
    setTimeout(() => {
      setIsInitialLoadComplete(true);
    }, 0);
  }, []);

  // Function to immediately update sessionStorage with current settings
  const updateSessionStorage = useCallback(() => {
    if (isAuthenticated && currentUser) {
      try {
        const currentSettings = {
          userId: currentUser?.user_id || '',
          settingsType: "user_settings",
          chatGIS: {
            salutation: salutation,
            enableAreasOfInterest: chatgisEnableAreasOfInterest,
            areas: [
              {
                areaId: "chatgis_area1",
                enabled: true, // Area 1 is always enabled when filtering is on
                coordinates: chatgisArea1,
                presetArea: chatgisSelectedArea1
              },
              {
                areaId: "chatgis_area2",
                enabled: chatgisArea2Enabled,
                coordinates: chatgisArea2,
                presetArea: chatgisSelectedArea2
              },
              {
                areaId: "chatgis_area3",
                enabled: chatgisArea3Enabled,
                coordinates: chatgisArea3,
                presetArea: chatgisSelectedArea3
              }
            ]
          },
          geoRAG: {
            selectedModel: selectedModel,
            enableAreasOfInterest: enableAreasOfInterest,
            areas: [
              {
                areaId: "area1",
                enabled: true, // Area 1 is always enabled when filtering is on
                coordinates: area1,
                presetArea: selectedArea1
              },
              {
                areaId: "area2",
                enabled: area2Enabled,
                coordinates: area2,
                presetArea: selectedArea2
              },
              {
                areaId: "area3",
                enabled: area3Enabled,
                coordinates: area3,
                presetArea: selectedArea3
              }
            ]
          },
          metadata: {
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            version: "1.0"
          }
        };
        sessionStorage.setItem('userSettings', JSON.stringify(currentSettings));
      } catch (error) {
        console.error('Error updating sessionStorage:', error);
      }
    }
  }, [
    isAuthenticated,
    currentUser,
    salutation,
    chatgisEnableAreasOfInterest,
    chatgisArea2Enabled,
    chatgisArea3Enabled,
    chatgisArea1,
    chatgisArea2,
    chatgisArea3,
    chatgisSelectedArea1,
    chatgisSelectedArea2,
    chatgisSelectedArea3,
    selectedModel,
    enableAreasOfInterest,
    area2Enabled,
    area3Enabled,
    area1,
    area2,
    area3,
    selectedArea1,
    selectedArea2,
    selectedArea3
  ]);

  // Update sessionStorage immediately whenever any setting changes (but only after initial load)
  useEffect(() => {
    if (isInitialLoadComplete) {
      updateSessionStorage();
    }
  }, [updateSessionStorage, isInitialLoadComplete]);

  // In-memory settings storage for display purposes
  const settings = {
    chatGIS: {
      salutation: salutation,
      enableAreasOfInterest: chatgisEnableAreasOfInterest,
      areas: chatgisEnableAreasOfInterest ? [
        chatgisArea1, // Area 1 is always enabled when filtering is on
        chatgisArea2Enabled ? chatgisArea2 : null,
        chatgisArea3Enabled ? chatgisArea3 : null
      ].filter(Boolean) : []
    },
    geoRAG: {
      selectedModel: selectedModel,
      enableAreasOfInterest: enableAreasOfInterest,
      areas: enableAreasOfInterest ? [
        area1, // Area 1 is always enabled when filtering is on
        area2Enabled ? area2 : null,
        area3Enabled ? area3 : null
      ].filter(Boolean) : []
    }
  };

  // Update area2 enabled state
  const handleArea2EnabledChange = (enabled) => {
    setArea2Enabled(enabled);
    if (!enabled) {
      setArea3Enabled(false);
    }
  };

  // Update area3 enabled state
  const handleArea3EnabledChange = (enabled) => {
    if (area2Enabled) {
      setArea3Enabled(enabled);
    }
  };

  // ChatGIS Areas of Interest handlers
  // Update ChatGIS area2 enabled state
  const handleChatgisArea2EnabledChange = (enabled) => {
    setChatgisArea2Enabled(enabled);
    if (!enabled) {
      setChatgisArea3Enabled(false);
    }
  };

  // Update ChatGIS area3 enabled state
  const handleChatgisArea3EnabledChange = (enabled) => {
    if (chatgisArea2Enabled) {
      setChatgisArea3Enabled(enabled);
    }
  };

  // Handle predefined area selection
  const handlePresetSelection = (areaNumber, selectedValue) => {
    if (selectedValue === 'custom') {
      // Reset coordinates to 0 for consistent positioning when Custom is selected
      const resetCoordinates = { minLat: 0, maxLat: 0, minLon: 0, maxLon: 0 };
      switch (areaNumber) {
        case 1:
          setArea1(resetCoordinates);
          setSelectedArea1(selectedValue);
          break;
        case 2:
          setArea2(resetCoordinates);
          setSelectedArea2(selectedValue);
          break;
        case 3:
          setArea3(resetCoordinates);
          setSelectedArea3(selectedValue);
          break;
        default:
          break;
      }
      return;
    }
    
    const coordinates = predefinedAreas[selectedValue];
    if (coordinates) {
      switch (areaNumber) {
        case 1:
          setArea1(coordinates);
          setSelectedArea1(selectedValue);
          break;
        case 2:
          setArea2(coordinates);
          setSelectedArea2(selectedValue);
          break;
        case 3:
          setArea3(coordinates);
          setSelectedArea3(selectedValue);
          break;
        default:
          break;
      }
    }
  };

  // Handle ChatGIS predefined area selection
  const handleChatgisPresetSelection = (areaNumber, selectedValue) => {
    if (selectedValue === 'custom') {
      // Reset coordinates to 0 for consistent positioning when Custom is selected
      const resetCoordinates = { minLat: 0, maxLat: 0, minLon: 0, maxLon: 0 };
      switch (areaNumber) {
        case 1:
          setChatgisArea1(resetCoordinates);
          setChatgisSelectedArea1(selectedValue);
          break;
        case 2:
          setChatgisArea2(resetCoordinates);
          setChatgisSelectedArea2(selectedValue);
          break;
        case 3:
          setChatgisArea3(resetCoordinates);
          setChatgisSelectedArea3(selectedValue);
          break;
        default:
          break;
      }
      return;
    }
    
    const coordinates = predefinedAreas[selectedValue];
    if (coordinates) {
      switch (areaNumber) {
        case 1:
          setChatgisArea1(coordinates);
          setChatgisSelectedArea1(selectedValue);
          break;
        case 2:
          setChatgisArea2(coordinates);
          setChatgisSelectedArea2(selectedValue);
          break;
        case 3:
          setChatgisArea3(coordinates);
          setChatgisSelectedArea3(selectedValue);
          break;
        default:
          break;
      }
    }
  };

  // Refresh settings from backend
  const refreshSettingsFromBackend = async () => {
    // Check if user is authenticated
    if (!isAuthenticated || !currentUser) {
      setSaveMessage('User not authenticated. Please log in again.');
      setSaveMessageType('error');
      return;
    }

    try {
      const token = sessionStorage.getItem('token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await apiClient.get('/settings');

      if (response.status === 200) {
        const result = response.data;
        if (result.success && result.settings) {
          sessionStorage.setItem('userSettings', JSON.stringify(result.settings));
          // Reload the component to reflect the updated settings
          window.location.reload();
        }
      }
    } catch (error) {
      console.error('Error refreshing settings:', error);
    }
  };

  // Save settings to backend
  const handleSaveSettings = async () => {
    // Check if user is authenticated and currentUser exists
    if (!isAuthenticated || !currentUser) {
      setSaveMessage('User not authenticated. Please log in again.');
      setSaveMessageType('error');
      return;
    }

    setIsSaving(true);
    setSaveMessage('');
    
    try {
                  // Get current model from sessionStorage
            const currentSettings = sessionStorage.getItem('userSettings');
            let currentModel = 'arn:aws:bedrock:us-west-2:854669816847:inference-profile/us.amazon.nova-lite-v1:0'; // Default fallback
            if (currentSettings) {
              try {
                const parsed = JSON.parse(currentSettings);
                currentModel = parsed.geoRAG?.selectedModel || 'arn:aws:bedrock:us-west-2:854669816847:inference-profile/us.amazon.nova-lite-v1:0';
              } catch (error) {
                console.error('Error parsing current settings:', error);
              }
            }

            // Prepare settings data for API
            const settingsData = {
              userId: currentUser.user_id,
              settingsType: "user_settings",
              chatGIS: {
                salutation: salutation,
                enableAreasOfInterest: chatgisEnableAreasOfInterest,
                areas: [
                  {
                    areaId: "chatgis_area1",
                    enabled: true, // Area 1 is always enabled when filtering is on
                    coordinates: chatgisArea1,
                    presetArea: chatgisSelectedArea1
                  },
                  {
                    areaId: "chatgis_area2",
                    enabled: chatgisArea2Enabled,
                    coordinates: chatgisArea2,
                    presetArea: chatgisSelectedArea2
                  },
                  {
                    areaId: "chatgis_area3",
                    enabled: chatgisArea3Enabled,
                    coordinates: chatgisArea3,
                    presetArea: chatgisSelectedArea3
                  }
                ]
              },
              geoRAG: {
                selectedModel: currentModel,
                enableAreasOfInterest: enableAreasOfInterest,
                areas: [
                  {
                    areaId: "area1",
                    enabled: true, // Area 1 is always enabled when filtering is on
                    coordinates: area1,
                    presetArea: selectedArea1
                  },
                  {
                    areaId: "area2",
                    enabled: area2Enabled,
                    coordinates: area2,
                    presetArea: selectedArea2
                  },
                  {
                    areaId: "area3",
                    enabled: area3Enabled,
                    coordinates: area3,
                    presetArea: selectedArea3
                  }
                ]
              },
              metadata: {
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString(),
                version: "1.0"
              }
            };

      // Get auth token from sessionStorage
      const token = sessionStorage.getItem('token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await apiClient.post('/settings', settingsData);

      if (response.status !== 200) {
        const errorData = response.data;
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const result = response.data;
      
      if (result.success) {
        // Update sessionStorage with the saved settings using our helper function
        updateSessionStorage();
        
        setSaveMessage('Settings saved successfully!');
        setSaveMessageType('success');
      } else {
        throw new Error(result.message || 'Failed to save settings');
      }

    } catch (error) {
      console.error('Error saving settings:', error);
      setSaveMessage(`Error saving settings: ${error.message}`);
      setSaveMessageType('error');
    } finally {
      setIsSaving(false);
      
      // Clear message after 5 seconds
      setTimeout(() => {
        setSaveMessage('');
      }, 5000);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="settings-container">
        <div className="auth-required-message">
          <h3>Authentication Required</h3>
          <p>Please log in to access the Settings page.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="settings-container">
      <h2>Settings</h2>
      
      {/* ChatGIS Section */}
      <div className="settings-section">
        <h3>ChatGIS</h3>
        <div className="setting-item">
          <label className="setting-label">Salutation:</label>
          <select
            value={salutation}
            onChange={(e) => setSalutation(e.target.value)}
            className="salutation-select"
          >
            <option value="none specified">none specified</option>
            <option value="Sir">Sir</option>
            <option value="Madam">Madam</option>
          </select>
        </div>

        {/* ChatGIS Areas of Interest Section */}
        <div className="areas-section">
          <label>
            <input 
              type="checkbox" 
              id="chatgis-enable-areas"
              checked={chatgisEnableAreasOfInterest}
              onChange={(e) => setChatgisEnableAreasOfInterest(e.target.checked)}
            />
            Enable Areas of Interest Filtering
          </label>
          
          {chatgisEnableAreasOfInterest && (
            <div id="chatgis-areas-container">
              <div className="areas-header">
                <span>Areas of Interest:</span>
              </div>
              
              <div id="chatgis-areas-inputs" className="areas-inputs">
                {/* ChatGIS Area 1 */}
                <div className="area-input" data-area="1">
                  <h4>Area 1</h4>
                  <div className="area-preset-selector">
                    <select 
                      id="chatgis-preset-area1" 
                      className="preset-select"
                      value={chatgisSelectedArea1}
                      onChange={(e) => handleChatgisPresetSelection(1, e.target.value)}
                    >
                      <option value="custom">Custom</option>
                      <option value="oceanside-ca">Oceanside, California</option>
                      <option value="san-diego-county">San Diego County</option>
                      <option value="california">California</option>
                      <option value="texas">Texas</option>
                      <option value="new-york">New York State</option>
                    </select>
                  </div>
                  <div className="coordinate-inputs">
                    <div className="coord-group">
                      <label>Min Latitude:</label>
                      <input 
                        type="number" 
                        step="0.0001" 
                        id="chatgis-area1-min-lat" 
                        placeholder="-90.0"
                        value={chatgisArea1.minLat}
                        onChange={(e) => {
                          const newValue = parseFloat(e.target.value) || 0;
                          setChatgisArea1({...chatgisArea1, minLat: newValue});
                        }}
                      />
                    </div>
                    <div className="coord-group">
                      <label>Max Latitude:</label>
                      <input 
                        type="number" 
                        step="0.0001" 
                        id="chatgis-area1-max-lat" 
                        placeholder="90.0"
                        value={chatgisArea1.maxLat}
                        onChange={(e) => {
                          const newValue = parseFloat(e.target.value) || 0;
                          setChatgisArea1({...chatgisArea1, maxLat: newValue});
                        }}
                      />
                    </div>
                    <div className="coord-group">
                      <label>Min Longitude:</label>
                      <input 
                        type="number" 
                        step="0.0001" 
                        id="chatgis-area1-min-lon" 
                        placeholder="-180.0"
                        value={chatgisArea1.minLon}
                        onChange={(e) => {
                          const newValue = parseFloat(e.target.value) || 0;
                          setChatgisArea1({...chatgisArea1, minLon: newValue});
                        }}
                      />
                    </div>
                    <div className="coord-group">
                      <label>Max Longitude:</label>
                      <input 
                        type="number" 
                        step="0.0001" 
                        id="chatgis-area1-max-lon" 
                        placeholder="180.0"
                        value={chatgisArea1.maxLon}
                        onChange={(e) => {
                          const newValue = parseFloat(e.target.value) || 0;
                          setChatgisArea1({...chatgisArea1, maxLon: newValue});
                        }}
                      />
                    </div>
                  </div>
                </div>
                
                {/* ChatGIS Area 2 */}
                <div className="area-input" data-area="2">
                  <h4>
                    <input 
                      type="checkbox" 
                      id="chatgis-enable-area2"
                      checked={chatgisArea2Enabled}
                      onChange={(e) => handleChatgisArea2EnabledChange(e.target.checked)}
                    />
                    Area 2
                  </h4>
                  <div className="area-preset-selector">
                    <select 
                      id="chatgis-preset-area2" 
                      className="preset-select"
                      value={chatgisSelectedArea2}
                      onChange={(e) => handleChatgisPresetSelection(2, e.target.value)}
                    >
                      <option value="custom">Custom</option>
                      <option value="oceanside-ca">Oceanside, California</option>
                      <option value="san-diego-county">San Diego County</option>
                      <option value="california">California</option>
                      <option value="texas">Texas</option>
                      <option value="new-york">New York State</option>
                    </select>
                  </div>
                  <div className="coordinate-inputs">
                    <div className="coord-group">
                      <label>Min Latitude:</label>
                      <input 
                        type="number" 
                        step="0.0001" 
                        id="chatgis-area2-min-lat" 
                        placeholder="-90.0"
                        value={chatgisArea2.minLat}
                        onChange={(e) => {
                          const newValue = parseFloat(e.target.value) || 0;
                          setChatgisArea2({...chatgisArea2, minLat: newValue});
                        }}
                        disabled={!chatgisArea2Enabled}
                      />
                    </div>
                    <div className="coord-group">
                      <label>Max Latitude:</label>
                      <input 
                        type="number" 
                        step="0.0001" 
                        id="chatgis-area2-max-lat" 
                        placeholder="90.0"
                        value={chatgisArea2.maxLat}
                        onChange={(e) => {
                          const newValue = parseFloat(e.target.value) || 0;
                          setChatgisArea2({...chatgisArea2, maxLat: newValue});
                        }}
                        disabled={!chatgisArea2Enabled}
                      />
                    </div>
                    <div className="coord-group">
                      <label>Min Longitude:</label>
                      <input 
                        type="number" 
                        step="0.0001" 
                        id="chatgis-area2-min-lon" 
                        placeholder="-180.0"
                        value={chatgisArea2.minLon}
                        onChange={(e) => {
                          const newValue = parseFloat(e.target.value) || 0;
                          setChatgisArea2({...chatgisArea2, minLon: newValue});
                        }}
                        disabled={!chatgisArea2Enabled}
                      />
                    </div>
                    <div className="coord-group">
                      <label>Max Longitude:</label>
                      <input 
                        type="number" 
                        step="0.0001" 
                        id="chatgis-area2-max-lon" 
                        placeholder="180.0"
                        value={chatgisArea2.maxLon}
                        onChange={(e) => {
                          const newValue = parseFloat(e.target.value) || 0;
                          setChatgisArea2({...chatgisArea2, maxLon: newValue});
                        }}
                        disabled={!chatgisArea2Enabled}
                      />
                    </div>
                  </div>
                </div>
                
                {/* ChatGIS Area 3 */}
                <div className="area-input" data-area="3">
                  <h4>
                    <input 
                      type="checkbox" 
                      id="chatgis-enable-area3"
                      checked={chatgisArea3Enabled}
                      onChange={(e) => handleChatgisArea3EnabledChange(e.target.checked)}
                      disabled={!chatgisArea2Enabled}
                    />
                    Area 3
                  </h4>
                  <div className="area-preset-selector">
                    <select 
                      id="chatgis-preset-area3" 
                      className="preset-select"
                      value={chatgisSelectedArea3}
                      onChange={(e) => handleChatgisPresetSelection(3, e.target.value)}
                    >
                      <option value="custom">Custom</option>
                      <option value="oceanside-ca">Oceanside, California</option>
                      <option value="san-diego-county">San Diego County</option>
                      <option value="california">California</option>
                      <option value="texas">Texas</option>
                      <option value="new-york">New York State</option>
                    </select>
                  </div>
                  <div className="coordinate-inputs">
                    <div className="coord-group">
                      <label>Min Latitude:</label>
                      <input 
                        type="number" 
                        step="0.0001" 
                        id="chatgis-area3-min-lat" 
                        placeholder="-90.0"
                        value={chatgisArea3.minLat}
                        onChange={(e) => {
                          const newValue = parseFloat(e.target.value) || 0;
                          setChatgisArea3({...chatgisArea3, minLat: newValue});
                        }}
                        disabled={!chatgisArea3Enabled}
                      />
                    </div>
                    <div className="coord-group">
                      <label>Max Latitude:</label>
                      <input 
                        type="number" 
                        step="0.0001" 
                        id="chatgis-area3-max-lat" 
                        placeholder="90.0"
                        value={chatgisArea3.maxLat}
                        onChange={(e) => {
                          const newValue = parseFloat(e.target.value) || 0;
                          setChatgisArea3({...chatgisArea3, maxLat: newValue});
                        }}
                        disabled={!chatgisArea3Enabled}
                      />
                    </div>
                    <div className="coord-group">
                      <label>Min Longitude:</label>
                      <input 
                        type="number" 
                        step="0.0001" 
                        id="chatgis-area3-min-lon" 
                        placeholder="-180.0"
                        value={chatgisArea3.minLon}
                        onChange={(e) => {
                          const newValue = parseFloat(e.target.value) || 0;
                          setChatgisArea3({...chatgisArea3, minLon: newValue});
                        }}
                        disabled={!chatgisArea3Enabled}
                      />
                    </div>
                    <div className="coord-group">
                      <label>Max Longitude:</label>
                      <input 
                        type="number" 
                        step="0.0001" 
                        id="chatgis-area3-max-lon" 
                        placeholder="180.0"
                        value={chatgisArea3.maxLon}
                        onChange={(e) => {
                          const newValue = parseFloat(e.target.value) || 0;
                          setChatgisArea3({...chatgisArea3, maxLon: newValue});
                        }}
                        disabled={!chatgisArea3Enabled}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* GeoRAG Section */}
      <div className="settings-section">
        <h3>GeoRAG</h3>
        
        {/* Model Selection */}
        <div className="setting-item">
          <label className="setting-label">Model Selection:</label>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="model-select"
          >
            <option value="arn:aws:bedrock:us-west-2:854669816847:inference-profile/us.amazon.nova-lite-v1:0">Amazon Nova Lite</option>
            <option value="arn:aws:bedrock:us-west-2:854669816847:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0">Claude 3.5 Sonnet v2</option>
          </select>
        </div>

        {/* Areas of Interest Section */}
        <div className="areas-section">
          <label>
            <input 
              type="checkbox" 
              id="enable-areas"
              checked={enableAreasOfInterest}
              onChange={(e) => setEnableAreasOfInterest(e.target.checked)}
            />
            Enable Areas of Interest Filtering
          </label>
          
          {enableAreasOfInterest && (
            <div id="areas-container">
              <div className="areas-header">
                <span>Areas of Interest:</span>
              </div>
              
              <div id="areas-inputs">
                {/* Area 1 */}
                <div className="area-input" data-area="1">
                  <h4>Area 1</h4>
                  <div className="area-preset-selector">
                    <select 
                      id="preset-area1" 
                      className="preset-select"
                      value={selectedArea1}
                      onChange={(e) => handlePresetSelection(1, e.target.value)}
                    >
                      <option value="custom">Custom</option>
                      <option value="oceanside-ca">Oceanside, California</option>
                      <option value="san-diego-county">San Diego County</option>
                      <option value="california">California</option>
                      <option value="texas">Texas</option>
                      <option value="new-york">New York State</option>
                    </select>
                  </div>
                  <div className="coordinate-inputs">
                    <div className="coord-group">
                      <label>Min Latitude:</label>
                      <input 
                        type="number" 
                        step="0.0001" 
                        id="area1-min-lat" 
                        placeholder="-90.0"
                        value={area1.minLat}
                        onChange={(e) => {
                          const newValue = parseFloat(e.target.value) || 0;
                          setArea1({...area1, minLat: newValue});
                        }}
                      />
                    </div>
                    <div className="coord-group">
                      <label>Max Latitude:</label>
                      <input 
                        type="number" 
                        step="0.0001" 
                        id="area1-max-lat" 
                        placeholder="90.0"
                        value={area1.maxLat}
                        onChange={(e) => {
                          const newValue = parseFloat(e.target.value) || 0;
                          setArea1({...area1, maxLat: newValue});
                        }}
                      />
                    </div>
                    <div className="coord-group">
                      <label>Min Longitude:</label>
                      <input 
                        type="number" 
                        step="0.0001" 
                        id="area1-min-lon" 
                        placeholder="-180.0"
                        value={area1.minLon}
                        onChange={(e) => {
                          const newValue = parseFloat(e.target.value) || 0;
                          setArea1({...area1, minLon: newValue});
                        }}
                      />
                    </div>
                    <div className="coord-group">
                      <label>Max Longitude:</label>
                      <input 
                        type="number" 
                        step="0.0001" 
                        id="area1-max-lon" 
                        placeholder="180.0"
                        value={area1.maxLon}
                        onChange={(e) => {
                          const newValue = parseFloat(e.target.value) || 0;
                          setArea1({...area1, maxLon: newValue});
                        }}
                      />
                    </div>
                  </div>
                </div>
                
                {/* Area 2 */}
                <div className="area-input" data-area="2">
                  <h4>
                    <input 
                      type="checkbox" 
                      id="enable-area2"
                      checked={area2Enabled}
                      onChange={(e) => handleArea2EnabledChange(e.target.checked)}
                    />
                    Area 2
                  </h4>
                  <div className="area-preset-selector">
                    <select 
                      id="preset-area2" 
                      className="preset-select"
                      value={selectedArea2}
                      onChange={(e) => handlePresetSelection(2, e.target.value)}
                    >
                      <option value="custom">Custom</option>
                      <option value="oceanside-ca">Oceanside, California</option>
                      <option value="san-diego-county">San Diego County</option>
                      <option value="california">California</option>
                      <option value="texas">Texas</option>
                      <option value="new-york">New York State</option>
                    </select>
                  </div>
                  <div className="coordinate-inputs">
                    <div className="coord-group">
                      <label>Min Latitude:</label>
                      <input 
                        type="number" 
                        step="0.0001" 
                        id="area2-min-lat" 
                        placeholder="-90.0"
                        value={area2.minLat}
                        onChange={(e) => {
                          const newValue = parseFloat(e.target.value) || 0;
                          setArea2({...area2, minLat: newValue});
                        }}
                        disabled={!area2Enabled}
                      />
                    </div>
                    <div className="coord-group">
                      <label>Max Latitude:</label>
                      <input 
                        type="number" 
                        step="0.0001" 
                        id="area2-max-lat" 
                        placeholder="90.0"
                        value={area2.maxLat}
                        onChange={(e) => {
                          const newValue = parseFloat(e.target.value) || 0;
                          setArea2({...area2, maxLat: newValue});
                        }}
                        disabled={!area2Enabled}
                      />
                    </div>
                    <div className="coord-group">
                      <label>Min Longitude:</label>
                      <input 
                        type="number" 
                        step="0.0001" 
                        id="area2-min-lon" 
                        placeholder="-180.0"
                        value={area2.minLon}
                        onChange={(e) => {
                          const newValue = parseFloat(e.target.value) || 0;
                          setArea2({...area2, minLon: newValue});
                        }}
                        disabled={!area2Enabled}
                      />
                    </div>
                    <div className="coord-group">
                      <label>Max Longitude:</label>
                      <input 
                        type="number" 
                        step="0.0001" 
                        id="area2-max-lon" 
                        placeholder="180.0"
                        value={area2.maxLon}
                        onChange={(e) => {
                          const newValue = parseFloat(e.target.value) || 0;
                          setArea2({...area2, maxLon: newValue});
                        }}
                        disabled={!area2Enabled}
                      />
                    </div>
                  </div>
                </div>
                
                {/* Area 3 */}
                <div className="area-input" data-area="3">
                  <h4>
                    <input 
                      type="checkbox" 
                      id="enable-area3"
                      checked={area3Enabled}
                      onChange={(e) => handleArea3EnabledChange(e.target.checked)}
                      disabled={!area2Enabled}
                    />
                    Area 3
                  </h4>
                  <div className="area-preset-selector">
                    <select 
                      id="preset-area3" 
                      className="preset-select"
                      value={selectedArea3}
                      onChange={(e) => handlePresetSelection(3, e.target.value)}
                    >
                      <option value="custom">Custom</option>
                      <option value="oceanside-ca">Oceanside, California</option>
                      <option value="san-diego-county">San Diego County</option>
                      <option value="california">California</option>
                      <option value="texas">Texas</option>
                      <option value="new-york">New York State</option>
                    </select>
                  </div>
                  <div className="coordinate-inputs">
                    <div className="coord-group">
                      <label>Min Latitude:</label>
                      <input 
                        type="number" 
                        step="0.0001" 
                        id="area3-min-lat" 
                        placeholder="-90.0"
                        value={area3.minLat}
                        onChange={(e) => {
                          const newValue = parseFloat(e.target.value) || 0;
                          setArea3({...area3, minLat: newValue});
                        }}
                        disabled={!area3Enabled}
                      />
                    </div>
                    <div className="coord-group">
                      <label>Max Latitude:</label>
                      <input 
                        type="number" 
                        step="0.0001" 
                        id="area3-max-lat" 
                        placeholder="90.0"
                        value={area3.maxLat}
                        onChange={(e) => {
                          const newValue = parseFloat(e.target.value) || 0;
                          setArea3({...area3, maxLat: newValue});
                        }}
                        disabled={!area3Enabled}
                      />
                    </div>
                    <div className="coord-group">
                      <label>Min Longitude:</label>
                      <input 
                        type="number" 
                        step="0.0001" 
                        id="area3-min-lon" 
                        placeholder="-180.0"
                        value={area3.minLon}
                        onChange={(e) => {
                          const newValue = parseFloat(e.target.value) || 0;
                          setArea3({...area3, minLon: newValue});
                        }}
                        disabled={!area3Enabled}
                      />
                    </div>
                    <div className="coord-group">
                      <label>Max Longitude:</label>
                      <input 
                        type="number" 
                        step="0.0001" 
                        id="area3-max-lon" 
                        placeholder="180.0"
                        value={area3.maxLon}
                        onChange={(e) => {
                          const newValue = parseFloat(e.target.value) || 0;
                          setArea3({...area3, maxLon: newValue});
                        }}
                        disabled={!area3Enabled}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Save and Refresh Buttons */}
        <div className="setting-item">
          <div className="button-group">
            <button 
              className="save-button"
              onClick={handleSaveSettings}
              disabled={isSaving}
            >
              {isSaving ? 'Saving...' : 'Save Settings'}
            </button>
            <button 
              className="refresh-button"
              onClick={refreshSettingsFromBackend}
            >
              🔄 Undo Unsaved Changes
            </button>
          </div>
          {saveMessage && (
            <div className={`save-message ${saveMessageType}`}>
              {saveMessage}
            </div>
          )}
        </div>
        
        {/* Debug Section - Remove after testing */}
        <div className="debug-section">
          <details>
            <summary>🔍 Debug: Current Settings JSON</summary>
            <pre>{JSON.stringify(settings, null, 2)}</pre>
          </details>
        </div>
      </div>
    </div>
  );
}

export default Settings;
