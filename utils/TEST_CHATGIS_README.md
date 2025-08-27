# ChatGIS Test Application

This Streamlit application provides a test interface for the chat/gis endpoint with authentication and geo-XML tag inspection capabilities.

## Features

- **Login Page**: Authenticate with the backend to get access tokens
- **Chat Interface**: Send messages to the chat/gis endpoint 
- **Raw Text Display**: View chat history as raw text to inspect geo-XML tags with full-width display
- **Session Management**: Maintains chat history and session state
- **System Prompt Display**: View the current system prompt from the backend
- **Backend Status**: Monitor backend connection status

## Requirements

Install the required packages:

```powershell
# Activate virtual environment first
.\.venv\Scripts\activate

# Install requirements
pip install -r test_requirements.txt
```

## Running the Application

1. **Start the Backend Server** (in a separate terminal):
   ```powershell
   cd backend
   .\.venv\Scripts\activate
   python main.py
   ```
   The backend should be running on http://localhost:8000

2. **Run the Streamlit Test App**:
   ```powershell
   # Activate virtual environment
   .\.venv\Scripts\activate
   
   # Run the Streamlit app
   streamlit run test_chatgis_app.py
   ```
   The app will open in your browser at http://localhost:8501

## Usage

1. **Login**: Use your backend credentials to authenticate
2. **Chat**: Send messages to test the chat/gis endpoint
3. **Inspect Tags**: View the raw chat history to see geo-XML tags
4. **Monitor**: Check backend status and session information in the sidebar

## Testing Geo-XML Functionality

To test the geo-XML tagging functionality, try messages with geographic entities:

- "Tell me about mapping in San Francisco"
- "I need help with GIS analysis in New York City"  
- "How do I create maps for Los Angeles county?"
- "What are the best practices for mapping in Seattle, Washington?"

The raw text display will show any geo-XML tags that were added to both your input message and the AI's response.

## Wide Display Features

- **Full-Width Layout**: Chat history uses the entire screen width for maximum visibility
- **Dynamic Text Areas**: Message boxes automatically adjust height based on content length
- **No Truncation**: Geo-XML tags are fully visible without cutting off
- **Dynamic Sizing**: 
  - User messages: Height adjusts to content (100-400px)
  - Assistant messages: Height adjusts to content (150-500px)  
  - System messages: Height adjusts to content (100-300px)

## Configuration

- **Backend URL**: Configured to http://localhost:8000 (can be modified in the script)
- **Areas of Interest**: Disabled in this version (set to None)
- **Session Management**: Automatically handled by the application

## Notes

- The application displays chat history as raw text to inspect geo-XML tags
- Areas of interest are disabled for this initial test version  
- System prompts are loaded from the backend's /system-prompts endpoint
- Authentication tokens are managed automatically during the session
- Wide layout ensures complete visibility of geo-XML tags without truncation
