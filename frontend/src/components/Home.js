import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Home.css';

function Home() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="home-container">
      <div className="hero-section">
        <h1>Ellipsoid Labs</h1>
        <p className="subtitle">
          Applying Artificial Intelligence to Geographic Information Systems.
        </p>
        <p className="description">
          Welcome to Ellipsoid Labs, an experimental GIS AI system.
        </p>
        <p className="info">
          Ellipsoid Labs is currently developing these GIS-Enhanced AI capabilities, 
          and is actively seeking domain partners and early adopters to work with.
        </p>
      </div>

      <div className="features-grid">
        <div className="feature-card">
          <h3>GeoRAG AI</h3>
          <p>
            AI-enhanced Document Retrieval with ArcGIS Pro Integration, GeoRAG is a 
            geographically and spatially enhanced Retrieval Augmented Generation (RAG) 
            AI system. GeoRAG enables the exploration of the information from your 
            organization's documents in a spatially aware manner, visualizing these 
            results in ArcGIS Pro.
          </p>
        </div>

        <div className="feature-card">
          <h3>Hydrology AI</h3>
          <p>
            The Hydrology AI assists Hydrologists with analysis and compliance tasks. 
            This AI enhances Hydrologist's productivity and assists with the complex 
            regulatory environment and analyses of their projects. The AI interfaces 
            with ArcGIS Pro hydrologic models. (The Hydrologist AI is the first of 
            several domain-specific AIs that we are developing.)
          </p>
        </div>

        <div className="feature-card">
          <h3>Digital Twins AI</h3>
          <p>
            This AI enhances a Digital Twin of a city or other geographic entity in 
            ArcGIS Pro to instruct it to run simulations and help analyze the outcomes 
            of these simulations. The Digital Twin is in ArcGIS Pro, and the AI is 
            used to enhance the Digital Twin model's capabilities.
          </p>
        </div>
      </div>

      {isAuthenticated && (
        <div className="cta-section">
          <h2>Ready to get started?</h2>
          <div className="cta-buttons">
            <Link to="/chatbot" className="cta-btn primary">
              Try ChatGIS
            </Link>
            <Link to="/rag" className="cta-btn secondary">
              Explore RAG System
            </Link>
          </div>
        </div>
      )}

      {!isAuthenticated && (
        <div className="cta-section">
          <h2>Ready to get started?</h2>
          <p>Please log in to access our AI systems.</p>
          <Link to="/login" className="cta-btn primary">
            Login
          </Link>
        </div>
      )}
    </div>
  );
}

export default Home;
