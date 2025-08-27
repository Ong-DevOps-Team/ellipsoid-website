// Frontend configuration file
// This file contains configuration values needed by the frontend

export const config = {
  // ESRI API key for geographic entity detection and mapping
  ESRI_API_KEY: "AAPTxy8BH1VEsoebNVZXo8HurF89yH3U94of2tNjEtGqtHcZwLP_VXPel9LtcRPY0kjS8eWa2yDHBgrcEOlpZhUDLEE8jjdpzFPN4eJir7Bp6jmkL-KZBGD1zaLOpN4eJir7Bp6jmkL-KZBGD1zaLOpJ8mFqcYsTj4iP-MoNd8DY0QK3a3rPFby9P6Hss_JYbKKc2MwLAm0uFr7YTX7tquTAdZE0xTsPHVSlHVbxzny8g_lJoh4kg9CTlx32HiatWjEmDYA8.AT1_5MNNtJR7",
  
  // ShipEngine API key for address parsing
  SHIPENGINE_API_KEY: "TEST_ioChwePt81jYSvpcx+miyWf2Ubw9unDuMtEYUQgRAVo",
  
  // Backend API base URL
  API_BASE_URL: process.env.REACT_APP_API_URL || "http://localhost:8000",
  
  // California areas of interest for geographic entity filtering
  CALIFORNIA_AREAS_OF_INTEREST: [
    {
      min_lat: 32.50,
      max_lat: 42.10,
      min_lon: -124.50,
      max_lon: -114.10,
    }
  ]
};

// Debug function to log environment variable status
const logEnvironmentDebug = () => {
  console.log('🔍 DEBUG: REACT_APP_API_URL environment variable:', process.env.REACT_APP_API_URL);
  console.log('🔍 DEBUG: Final API_BASE_URL:', config.API_BASE_URL);
};

// Call debug function to show values in console
logEnvironmentDebug();