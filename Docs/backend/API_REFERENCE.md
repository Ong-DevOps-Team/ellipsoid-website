# Ellipsoid Labs Backend API Reference

## Overview

The Ellipsoid Labs backend provides a RESTful API for GIS Expert AI chatbot services, RAG (Retrieval Augmented Generation) capabilities, user authentication, chat management, and user settings management. This document describes all available endpoints, their parameters, and how to use them.

## Base URL

```
http://localhost:8000
```

## Authentication

All protected endpoints require JWT (JSON Web Token) authentication. Include the token in the `Authorization` header:

```
Authorization: Bearer <your_jwt_token>
```

### JWT Token Format

The JWT token contains:
- `sub`: User ID (as string)
- `username`: Username
- `exp`: Expiration timestamp

### Getting a JWT Token

Use the `/auth/login` endpoint with valid credentials to obtain a JWT token.

## API Endpoints

### System Endpoints

#### GET `/`

**Purpose**: Root endpoint - API information

**Response**:
```json
{
  "message": "Ellipsoid Labs API"
}
```

#### GET `/health`

**Purpose**: Health check endpoint

**Response**:
```json
{
  "status": "healthy"
}
```

### Authentication Endpoints

#### POST `/auth/login`

**Purpose**: Authenticate user and obtain JWT token

**Parameters**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Response**:
```json
{
  "user_id": 123,
  "username": "string",
  "access_token": "string",
  "token_type": "bearer"
}
```

**Error Responses**:

*Database Timeout (503 Service Unavailable)*:
```json
{
  "detail": "database_timeout"
}
```
Headers: `X-Error-Type: database_timeout`

*Authentication Failure (401 Unauthorized)*:
```json
{
  "detail": "Incorrect username or password"
}
```

*System Error (500 Internal Server Error)*:
```json
{
  "detail": "Authentication failed"
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

#### GET `/auth/me`

**Purpose**: Get current user information from JWT token

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "user_id": 123,
  "username": "string"
}
```

**Example**:
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer <your_jwt_token>"
```

### Chat Endpoints

#### POST `/chat/gis`

**Purpose**: Chat with GIS Expert AI

**Headers**: `Authorization: Bearer <token>`

**Parameters**:
```json
{
  "message": "string",
  "chat_history": [
    {
      "role": "string",
      "content": "string"
    }
  ],
  "session_id": "string (optional)"
}
```

**Response**:
```json
{
  "message": "string",
  "chat_history": [
    {
      "role": "string",
      "content": "string"
    }
  ],
  "session_id": "string"
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/chat/gis" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is GIS?",
    "chat_history": [],
    "session_id": "session_123"
  }'
```

#### POST `/chat/rag`

**Purpose**: Chat with RAG AI (Retrieval Augmented Generation) with configurable areas of interest

**Headers**: `Authorization: Bearer <token>`

**Parameters**:
```json
{
  "message": "string",
  "chat_history": [
    {
      "role": "string",
      "content": "string"
    }
  ],
  "session_id": "string (optional)",
  "model_id": "string (optional)",
  "areas_of_interest": [
    {
      "min_lat": 32.0000,
      "max_lat": 33.0000,
      "min_lon": -118.0000,
      "max_lon": -117.0000
    }
  ]
}
```

**Response**:
```json
{
  "message": "string",
  "chat_history": [
    {
      "role": "string",
      "content": "string"
    }
  ],
  "session_id": "string"
}
```

**Areas of Interest Parameter**:
The `areas_of_interest` parameter is optional and allows you to specify geographic regions for filtering geographic named entities. When provided, the system will only recognize and process geographic entities that fall within the specified bounds.

- **min_lat/max_lat**: Minimum and maximum latitude values (decimal degrees)
- **min_lon/max_lon**: Minimum and maximum longitude values (decimal degrees)
- **Precision**: Coordinates support 4 decimal places (e.g., 32.1234)
- **Multiple Areas**: You can specify up to 3 areas for comprehensive coverage

**Example**:
```bash
curl -X POST "http://localhost:8000/chat/rag" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about geographic data in California",
    "chat_history": [],
    "session_id": "rag_session_456",
    "model_id": "arn:aws:bedrock:us-west-2:854669816847:inference-profile/us.amazon.nova-lite-v1:0",
    "areas_of_interest": [
      {
        "min_lat": 32.0000,
        "max_lat": 42.0000,
        "min_lon": -124.0000,
        "max_lon": -114.0000
      }
    ]
  }'
```

### User Settings Endpoints

#### GET `/settings`

**Purpose**: Retrieve user settings for the authenticated user

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "userId": 123,
  "chatGIS": {
    "salutation": "none"
  },
  "geoRAG": {
    "selectedModel": "arn:aws:bedrock:us-west-2:854669816847:inference-profile/us.amazon.nova-lite-v1:0",
    "enableAreasOfInterest": false,
    "areas": [
      {
        "enabled": true,
        "preset": "Custom",
        "minLat": 32.0000,
        "maxLat": 33.0000,
        "minLon": -118.0000,
        "maxLon": -117.0000
      },
      {
        "enabled": false,
        "preset": "Custom",
        "minLat": 0.0000,
        "maxLat": 0.0000,
        "minLon": 0.0000,
        "maxLon": 0.0000
      },
      {
        "enabled": false,
        "preset": "Custom",
        "minLat": 0.0000,
        "maxLat": 0.0000,
        "minLon": 0.0000,
        "maxLon": 0.0000
      }
    ]
  },
  "metadata": {
    "createdAt": "2025-01-27T10:30:00Z",
    "updatedAt": "2025-01-27T10:30:00Z"
  }
}
```

**Example**:
```bash
curl -X GET "http://localhost:8000/settings" \
  -H "Authorization: Bearer <your_jwt_token>"
```

#### POST `/settings`

**Purpose**: Create or update user settings (upsert operation)

**Headers**: `Authorization: Bearer <token>`

**Parameters**:
```json
{
  "userId": 123,
  "chatGIS": {
    "salutation": "Sir"
  },
  "geoRAG": {
    "selectedModel": "arn:aws:bedrock:us-west-2:854669816847:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    "enableAreasOfInterest": true,
    "areas": [
      {
        "enabled": true,
        "preset": "Oceanside, California",
        "minLat": 33.1950,
        "maxLat": 33.2050,
        "minLon": -117.3850,
        "maxLon": -117.3750
      },
      {
        "enabled": true,
        "preset": "San Diego County, California",
        "minLat": 32.5000,
        "maxLat": 33.5000,
        "minLon": -117.5000,
        "maxLon": -116.5000
      },
      {
        "enabled": false,
        "preset": "Custom",
        "minLat": 0.0000,
        "maxLat": 0.0000,
        "minLon": 0.0000,
        "maxLon": 0.0000
      }
    ]
  }
}
```

**Response**:
```json
{
  "message": "Settings saved successfully",
  "settings_id": "507f1f77bcf86cd799439011"
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/settings" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": 123,
    "chatGIS": {"salutation": "Sir"},
    "geoRAG": {
      "selectedModel": "arn:aws:bedrock:us-west-2:854669816847:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0",
      "enableAreasOfInterest": true,
      "areas": [
        {
          "enabled": true,
          "preset": "Oceanside, California",
          "minLat": 33.1950,
          "maxLat": 33.2050,
          "minLon": -117.3850,
          "maxLon": -117.3750
        }
      ]
    }
  }'
```

#### PUT `/settings`

**Purpose**: Update existing user settings

**Headers**: `Authorization: Bearer <token>`

**Parameters**: Same as POST `/settings`

**Response**:
```json
{
  "message": "Settings updated successfully"
}
```

**Example**:
```bash
curl -X PUT "http://localhost:8000/settings" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": 123,
    "chatGIS": {"salutation": "Madam"},
    "geoRAG": {
      "selectedModel": "arn:aws:bedrock:us-west-2:854669816847:inference-profile/us.amazon.nova-lite-v1:0",
      "enableAreasOfInterest": false,
      "areas": []
    }
  }'
```

### Saved Chat Management

#### GET `/chats/saved`

**Purpose**: Get list of saved chats for current user

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "chats": [
    {
      "chatname": "string",
      "chat_id": "string"
    }
  ]
}
```

**Example**:
```bash
curl -X GET "http://localhost:8000/chats/saved" \
  -H "Authorization: Bearer <your_jwt_token>"
```

#### GET `/chats/saved/{chat_id}`

**Purpose**: Get a specific saved chat by ID

**Headers**: `Authorization: Bearer <token>`

**Path Parameters**:
- `chat_id`: MongoDB ObjectId string

**Response**:
```json
{
  "chatname": "string",
  "chat_history": [
    {
      "role": "string",
      "content": "string"
    }
  ],
  "timestamp": "2025-01-27T10:30:00Z"
}
```

**Example**:
```bash
curl -X GET "http://localhost:8000/chats/saved/507f1f77bcf86cd799439011" \
  -H "Authorization: Bearer <your_jwt_token>"
```

#### POST `/chats/save`

**Purpose**: Save a new chat

**Headers**: `Authorization: Bearer <token>`

**Parameters**:
```json
{
  "chatname": "string",
  "chat_history": [
    {
      "role": "string",
      "content": "string"
    }
  ]
}
```

**Response**:
```json
{
  "chat_id": "string",
  "message": "Chat saved successfully"
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/chats/save" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "chatname": "GIS Discussion",
    "chat_history": [
      {"role": "user", "content": "What is GIS?"},
      {"role": "assistant", "content": "GIS stands for Geographic Information System..."}
    ]
  }'
```

#### PUT `/chats/saved/{chat_id}`

**Purpose**: Update an existing saved chat

**Headers**: `Authorization: Bearer <token>`

**Path Parameters**:
- `chat_id`: MongoDB ObjectId string

**Parameters**:
```json
{
  "chatname": "string",
  "chat_history": [
    {
      "role": "string",
      "content": "string"
    }
  ]
}
```

**Response**:
```json
{
  "message": "Chat updated successfully"
}
```

**Example**:
```bash
curl -X PUT "http://localhost:8000/chats/saved/507f1f77bcf86cd799439011" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "chatname": "Updated GIS Discussion",
    "chat_history": [
      {"role": "user", "content": "What is GIS?"},
      {"role": "assistant", "content": "GIS stands for Geographic Information System..."},
      {"role": "user", "content": "How is it used?"}
    ]
  }'
```

#### DELETE `/chats/saved/{chat_id}`

**Purpose**: Delete a saved chat

**Headers**: `Authorization: Bearer <token>`

**Path Parameters**:
- `chat_id`: MongoDB ObjectId string

**Response**:
```json
{
  "message": "Chat deleted successfully"
}
```

**Example**:
```bash
curl -X DELETE "http://localhost:8000/chats/saved/507f1f77bcf86cd799439011" \
  -H "Authorization: Bearer <your_jwt_token>"
```

### System Endpoints

#### GET `/system-prompts`

**Purpose**: Get system prompts for AI services

**Response**:
```json
{
  "gis_expert": "string"
}
```

**Example**:
```bash
curl -X GET "http://localhost:8000/system-prompts"
```

#### GET `/about`

**Purpose**: Get company information

**Response**:
```json
{
  "company_name": "Ellipsoid Labs",
  "description": "string",
  "founder": "string",
  "background": "string",
  "gis_focus": "string",
  "contact": "string"
}
```

**Example**:
```bash
curl -X GET "http://localhost:8000/about"
```

### Debug Endpoints

#### GET `/debug/user-context`

**Purpose**: Debug endpoint to check user context in request state

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "has_user_id": true,
  "user_id": 123,
  "has_username": true,
  "username": "string",
  "state_attributes": ["user_id", "username"]
}
```

**Example**:
```bash
curl -X GET "http://localhost:8000/debug/user-context" \
  -H "Authorization: Bearer <your_jwt_token>"
```

## Data Models

### ChatMessage
```json
{
  "role": "string",     // "user" or "assistant"
  "content": "string"   // The message content
}
```

### ChatRequest
```json
{
  "message": "string",                    // User's message
  "chat_history": [ChatMessage],          // Previous conversation
  "session_id": "string",                 // Optional session identifier
  "model_id": "string",                   // Optional model override (RAG only)
  "areas_of_interest": [                  // Optional geographic filtering (RAG only)
    {
      "min_lat": "float",
      "max_lat": "float", 
      "min_lon": "float",
      "max_lon": "float"
    }
  ]
}
```

### ChatResponse
```json
{
  "message": "string",           // AI response
  "chat_history": [ChatMessage], // Updated conversation history
  "session_id": "string"         // Session identifier
}
```

### UserSettings
```json
{
  "userId": "integer",           // User ID (integer)
  "chatGIS": {
    "salutation": "string"       // "none", "Sir", or "Madam"
  },
  "geoRAG": {
    "selectedModel": "string",   // AWS Bedrock model ARN
    "enableAreasOfInterest": "boolean",
    "areas": [
      {
        "enabled": "boolean",
        "preset": "string",      // Predefined area name or "Custom"
        "minLat": "float",       // 4-decimal precision
        "maxLat": "float",       // 4-decimal precision
        "minLon": "float",       // 4-decimal precision
        "maxLon": "float"        // 4-decimal precision
      }
    ]
  },
  "metadata": {
    "createdAt": "string",       // ISO 8601 timestamp
    "updatedAt": "string"        // ISO 8601 timestamp
  }
}
```

### SavedChat
```json
{
  "chatname": "string",          // Name of the saved chat
  "chat_history": [ChatMessage], // Full conversation
  "timestamp": "string",         // ISO 8601 timestamp
  "user_id": 123                 // Owner's user ID
}
```

## Error Handling

### HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request parameters
- **401 Unauthorized**: Invalid or expired JWT token
- **403 Forbidden**: No authentication token provided
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation errors
- **500 Internal Server Error**: Server error
- **503 Service Unavailable**: Database connection timeout (Azure SQL database sleeping)

### Error Response Format

```json
{
  "detail": "Error message description"
}
```

### Common Error Scenarios

#### Authentication Errors
```json
// 401 Unauthorized - Invalid token
{
  "detail": "Could not validate credentials"
}

// 403 Forbidden - No token
{
  "detail": "Not authenticated"
}

// 401 Unauthorized - Incorrect credentials
{
  "detail": "Incorrect username or password"
}
```

#### Database Errors
```json
// 503 Service Unavailable - Database timeout during login
{
  "detail": "database_timeout"
}
```

**Headers**: `X-Error-Type: database_timeout`

**Description**: This error occurs when the Azure SQL database is in a "sleeping" state due to inactivity and fails to respond within the timeout period. This typically happens after several hours of no database activity when Azure SQL automatically scales down for cost optimization.

**Client Handling**: Frontend applications should detect this specific error code and display a user-friendly message suggesting the user wait 60 seconds before retrying, as the database needs time to "wake up" and become fully responsive again.

#### Validation Errors
```json
// 422 Unprocessable Entity - Missing required fields
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Usage Examples

### Complete Chat Flow with Areas of Interest

1. **Login to get JWT token**:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

2. **Start a RAG chat session with geographic filtering**:
```bash
curl -X POST "http://localhost:8000/chat/rag" \
  -H "Authorization: Bearer <token_from_login>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about cities in Southern California",
    "chat_history": [],
    "session_id": "rag_session_001",
    "areas_of_interest": [
      {
        "min_lat": 32.0000,
        "max_lat": 35.0000,
        "min_lon": -120.0000,
        "max_lon": -114.0000
      }
    ]
  }'
```

3. **Continue the conversation**:
```bash
curl -X POST "http://localhost:8000/chat/rag" \
  -H "Authorization: Bearer <token_from_login>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What about the climate in this region?",
    "chat_history": [
      {"role": "user", "content": "Tell me about cities in Southern California"},
      {"role": "assistant", "content": "Southern California includes major cities like Los Angeles, San Diego..."}
    ],
    "session_id": "rag_session_001",
    "areas_of_interest": [
      {
        "min_lat": 32.0000,
        "max_lat": 35.0000,
        "min_lon": -120.0000,
        "max_lon": -114.0000
      }
    ]
  }'
```

### User Settings Management

1. **Retrieve current settings**:
```bash
curl -X GET "http://localhost:8000/settings" \
  -H "Authorization: Bearer <your_jwt_token>"
```

2. **Update settings with areas of interest**:
```bash
curl -X POST "http://localhost:8000/settings" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": 123,
    "chatGIS": {"salutation": "Sir"},
    "geoRAG": {
      "selectedModel": "arn:aws:bedrock:us-west-2:854669816847:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0",
      "enableAreasOfInterest": true,
      "areas": [
        {
          "enabled": true,
          "preset": "Oceanside, California",
          "minLat": 33.1950,
          "maxLat": 33.2050,
          "minLon": -117.3850,
          "maxLon": -117.3750
        }
      ]
    }
  }'
```

### Mobile App Integration

For mobile applications, store the JWT token securely and include it in all API requests:

```javascript
// React Native example
const apiCall = async (endpoint, data) => {
  const token = await SecureStore.getItemAsync('jwt_token');
  
  const response = await fetch(`http://localhost:8000${endpoint}`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
  });
  
  return response.json();
};
```

## Rate Limiting

Currently, no rate limiting is implemented. However, it's recommended to implement reasonable limits in client applications to avoid overwhelming the server.

## Session Management

- **GIS Expert AI**: Stateless - no server-side session storage
- **RAG AI**: Frontend-maintained session IDs for conversation continuity with configurable areas of interest
- **Saved Chats**: Persistent storage in MongoDB with user isolation
- **User Settings**: Persistent storage in MongoDB with automatic loading on login

## Security Notes

- JWT tokens should be stored securely (not in localStorage for web apps)
- Tokens expire automatically - implement refresh logic if needed
- All sensitive endpoints require valid JWT authentication
- User data is isolated by `user_id` in the database
- Settings are user-specific and cannot be accessed by other users

## Areas of Interest Configuration

The `areas_of_interest` parameter allows you to configure geographic filtering for the RAG chatbot:

### Coordinate System
- **Latitude**: -90.0000 to 90.0000 (4 decimal precision)
- **Longitude**: -180.0000 to 180.0000 (4 decimal precision)
- **Precision**: 4 decimal places provide approximately 11-meter accuracy

### Predefined Areas
The system includes several predefined geographic areas:
- **Oceanside, California**: 33.1950°N to 33.2050°N, 117.3850°W to 117.3750°W
- **San Diego County, California**: 32.5000°N to 33.5000°N, 117.5000°W to 116.5000°W
- **Texas**: 26.0000°N to 37.0000°N, 106.0000°W to 93.0000°W
- **New York State**: 40.0000°N to 45.0000°N, 79.0000°W to 72.0000°W

### Custom Areas
You can define custom geographic bounds by specifying:
- Minimum and maximum latitude values
- Minimum and maximum longitude values
- All coordinates must be valid decimal degrees

## Support

For API-related questions or issues, refer to:
- This documentation
- The backend source code in `backend/main.py`
- The universal user ID access documentation in `docs/backend/UNIVERSAL_USER_ID_ACCESS.md`
- The test programs in `tests/backend/` for usage examples
