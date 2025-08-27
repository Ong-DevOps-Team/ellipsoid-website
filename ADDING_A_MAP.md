# Adding Map Capabilities to Your Frontend

This guide explains how to add the map functionality from the GeoNER Map Explorer to your own project's frontend.

## Prerequisites

- Esri API key from [developers.arcgis.com](https://developers.arcgis.com)
- Geo-XML tagged text from your geo_ner backend (format: `<LOC lat="40.7128" lon="-74.006" zoom_level="10">New York</LOC>`)

## 1. HTML Structure

Add this to your HTML where you want the map to appear:

```html
<div class="map-container">
    <div id="mapView"></div>
    <button type="button" id="toggle-map" class="map-toggle-btn" title="Click to minimize/restore map">
        <span class="minimize-icon">🗗</span>
        <span class="restore-icon" style="display: none;">🗖</span>
    </button>
</div>
```

## 2. CSS Styling

Add these styles to your CSS:

```css
.map-container { 
    margin-top: 30px; 
    border: 2px solid #ddd; 
    border-radius: 10px; 
    box-shadow: 0 4px 8px rgba(0,0,0,0.1); 
    background: #fafafa;
    position: relative;
}

#mapView { 
    width: 100%; 
    height: 500px; 
    border-radius: 10px; 
}

/* Map Toggle Button - positioned over bottom-right corner */
.map-toggle-btn {
    position: absolute;
    bottom: 10px;
    right: 10px;
    background: #1f77b4;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 8px 12px;
    cursor: pointer;
    font-size: 16px;
    transition: background-color 0.3s ease;
    z-index: 1000;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.map-toggle-btn:hover {
    background: #0d5aa7;
}

.map-toggle-btn:active {
    transform: scale(0.95);
}

/* Minimized map state */
.map-container.minimized {
    height: 60px;
    overflow: hidden;
    transition: height 0.3s ease;
}

.map-container.minimized #mapView {
    height: 60px;
    transition: height 0.3s ease;
}

/* Icon transitions */
.minimize-icon, .restore-icon {
    transition: opacity 0.3s ease;
}
```

## 3. JavaScript Map Setup

Include the Esri JavaScript API and set up the map:

```html
<script src="https://js.arcgis.com/4.29/"></script>
```

```javascript
let view, graphicsLayer, currentGraphic, Graphic;

require([
    "esri/config",
    "esri/Map",
    "esri/views/MapView",
    "esri/Graphic",
    "esri/layers/GraphicsLayer"
], (esriConfig, Map, MapView, _Graphic, GraphicsLayer) => {
    esriConfig.apiKey = "YOUR_ESRI_API_KEY_HERE";
    
    // Create map with your preferred basemap
    const map = new Map({ 
        basemap: "topo-vector"  // Options: "topo-vector", "streets-vector", "hybrid", etc.
    });
    
    view = new MapView({
        container: "mapView",
        map,
        zoom: 3,
        center: [-98.5795, 39.8283],  // Center on US
        constraints: {
            rotationEnabled: false
        }
    });
    
    graphicsLayer = new GraphicsLayer();
    map.add(graphicsLayer);
    Graphic = _Graphic;
    
    // Set up map minimize/restore functionality
    setupMapToggle();
});
```

## 4. Map Toggle Functionality

Add this function for the minimize/restore button:

```javascript
function setupMapToggle() {
    const toggleBtn = document.getElementById('toggle-map');
    const mapContainer = document.querySelector('.map-container');
    const mapView = document.getElementById('mapView');
    const minimizeIcon = document.querySelector('.minimize-icon');
    const restoreIcon = document.querySelector('.restore-icon');
    
    let isMinimized = false;
    
    toggleBtn.addEventListener('click', function() {
        if (isMinimized) {
            // Restore map to normal size
            mapContainer.classList.remove('minimized');
            mapView.style.height = '500px';
            mapContainer.style.height = 'auto';
            
            minimizeIcon.style.display = 'inline';
            restoreIcon.style.display = 'none';
            toggleBtn.title = 'Click to minimize map';
            
            isMinimized = false;
            
            if (view) {
                setTimeout(() => view.resize(), 300);
            }
        } else {
            // Minimize map
            mapContainer.classList.add('minimized');
            mapView.style.height = '60px';
            mapContainer.style.height = '60px';
            
            minimizeIcon.style.display = 'none';
            restoreIcon.style.display = 'inline';
            toggleBtn.title = 'Click to restore map';
            
            isMinimized = true;
            
            if (view) {
                setTimeout(() => view.resize(), 300);
            }
        }
    });
}
```

## 5. Marker Management

Add these functions for managing map markers:

```javascript
function addOrReplaceMarker(lon, lat, name, zoom) {
    if (!view || !graphicsLayer) return;
    
    if (currentGraphic) graphicsLayer.remove(currentGraphic);
    
    currentGraphic = new Graphic({
        geometry: { type: 'point', longitude: lon, latitude: lat },
        symbol: {
            type: 'simple-marker',
            color: '#ff7f0e',
            size: '14px',
            outline: { color: '#ffffff', width: 1.5 }
        },
        attributes: { Name: name },
        popupTemplate: { title: '{Name}' }
    });
    
    graphicsLayer.add(currentGraphic);
    view.goTo({ center: [lon, lat], zoom: zoom || 10 });
}
```

## 6. Geo-XML Text Processing

Convert your Geo-XML text to clickable links:

```javascript
function xmlGeotaggedTextToHtml(xmlText) {
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
            
            return `<a href="#" data-lon="${lon}" data-lat="${lat}" data-zoom="${zoom}">${text}</a>`;
        });
}
```

## 7. Click Event Handling

Add click handlers to your processed text:

```javascript
// After processing your Geo-XML text and adding it to the DOM
Array.from(document.getElementsByTagName('a')).forEach(link => {
    link.addEventListener('click', function(ev) {
        ev.preventDefault();
        
        const lon = parseFloat(link.getAttribute('data-lon'));
        const lat = parseFloat(link.getAttribute('data-lat'));
        const name = link.textContent;
        const zoom = parseInt(link.getAttribute('data-zoom'));
        
        // Update the map with the clicked location
        addOrReplaceMarker(lon, lat, name, zoom);
    });
});
```

## 8. Integration Example

Here's how to integrate with your existing text processing:

```javascript
// Assuming you have Geo-XML text from your backend
const geotaggedText = '<LOC lat="40.7128" lon="-74.006" zoom_level="10">New York</LOC> is a great city.';

// Convert to HTML with clickable links
const htmlText = xmlGeotaggedTextToHtml(geotaggedText);

// Add to your DOM
document.getElementById('your-text-container').innerHTML = htmlText;

// Add click handlers
Array.from(document.getElementsByTagName('a')).forEach(link => {
    link.addEventListener('click', function(ev) {
        ev.preventDefault();
        const lon = parseFloat(link.getAttribute('data-lon'));
        const lat = parseFloat(link.getAttribute('data-lat'));
        const name = link.textContent;
        const zoom = parseInt(link.getAttribute('data-zoom'));
        addOrReplaceMarker(lon, lat, name, zoom);
    });
});
```

## Key Features

- **Responsive map** with minimize/restore functionality
- **Clickable location links** that update the map
- **Marker management** with automatic map navigation
- **Smooth animations** for minimize/restore transitions
- **Professional styling** that integrates with your design

## Customization Options

- **Basemap**: Change `"topo-vector"` to any Esri basemap
- **Map size**: Modify the `height: 500px` in CSS
- **Marker style**: Customize colors, size, and symbols
- **Positioning**: Adjust the toggle button position by changing `bottom: 10px` and `right: 10px`
- **Colors**: Update the button colors to match your theme
