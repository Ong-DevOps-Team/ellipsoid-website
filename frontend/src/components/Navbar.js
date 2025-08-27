import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Navbar.css';

function Navbar() {
  const { isAuthenticated, currentUser, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  // Function to check if a nav item is active
  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/" className="navbar-logo">
          🌍 Ellipsoid Labs
        </Link>
      </div>
      
      <div className="navbar-menu">
        <Link 
          to="/" 
          className={`navbar-item ${isActive('/') ? 'active' : ''}`}
        >
          Home
        </Link>
        <Link 
          to="/about" 
          className={`navbar-item ${isActive('/about') ? 'active' : ''}`}
        >
          About
        </Link>
        
        {isAuthenticated ? (
          <>
            <Link 
              to="/chatbot" 
              className={`navbar-item ${isActive('/chatbot') ? 'active' : ''}`}
            >
              ChatGIS
            </Link>
            <Link 
              to="/rag" 
              className={`navbar-item ${isActive('/rag') ? 'active' : ''}`}
            >
              GeoRAG
            </Link>
            <div className="navbar-user">
              <span className="username">Welcome, {currentUser?.username}</span>
              <Link 
                to="/settings" 
                className={`navbar-item ${isActive('/settings') ? 'active' : ''}`}
              >
                Settings
              </Link>
              <button onClick={handleLogout} className="logout-btn">Logout</button>
            </div>
          </>
        ) : (
          <Link 
            to="/login" 
            className={`navbar-item ${isActive('/login') ? 'active' : ''}`}
          >
            Login
          </Link>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
