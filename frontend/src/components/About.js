import React, { useState, useEffect } from 'react';
import apiClient from '../services/apiService';
import './About.css';

function About() {
  const [aboutData, setAboutData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAboutData();
  }, []);

  const fetchAboutData = async () => {
    try {
      console.log('🔍 DEBUG: Fetching about data from:', apiClient.defaults.baseURL + '/about');
      const response = await apiClient.get('/about');
      console.log('🔍 DEBUG: About data received:', response.status, response.data);
      setAboutData(response.data);
    } catch (err) {
      console.error('🔍 DEBUG: About fetch error:');
      console.error('🔍 DEBUG: Error message:', err.message);
      console.error('🔍 DEBUG: Error response:', err.response);
      console.error('🔍 DEBUG: Error status:', err.response?.status);
      console.error('🔍 DEBUG: Error config:', err.config);
      setError('Failed to load about information');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="about-container">Loading...</div>;
  }

  if (error) {
    return <div className="about-container">Error: {error}</div>;
  }

  return (
    <div className="about-container">
      <div className="about-content">
        <h2>About {aboutData?.company_name}</h2>
        
        <div className="about-section">
          <p>{aboutData?.description}</p>
        </div>

        <div className="about-section">
          <h3>Founder</h3>
          <p>{aboutData?.founder}</p>
          <p>{aboutData?.background}</p>
        </div>

        <div className="about-section">
          <h3>GIS Focus</h3>
          <p>{aboutData?.gis_focus}</p>
        </div>

        <div className="about-section">
          <h3>Contact Info</h3>
          <p>{aboutData?.contact}</p>
        </div>
      </div>
    </div>
  );
}

export default About;
