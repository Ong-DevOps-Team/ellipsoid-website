# Universal User ID Access System

## Overview

The Ellipsoid Labs backend implements a **Universal User ID Access** system that allows any endpoint or service to access the current user's `user_id` and `username` without explicitly passing these values as parameters. This system is built on FastAPI's request state mechanism and provides a clean, maintainable way to handle user context throughout the application.

## How It Works

### 1. Middleware Layer

The system uses FastAPI middleware to automatically extract user information from JWT tokens and store it in `request.state`:

```python
@app.middleware("http")
async def user_context_middleware(request: Request, call_next):
    """Extract user_id from JWT and store in request.state for universal access"""
    try:
        # Get authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
            # Verify token and extract user info
            try:
                token_data = auth_service.verify_token(token)
                if token_data:
                    # Store user_id and username in request.state
                    request.state.user_id = token_data.user_id
                    request.state.username = token_data.username
                else:
                    # Invalid token - set to None
                    request.state.user_id = None
                    request.state.username = None
            except Exception:
                # Token verification failed - set to None
                request.state.user_id = None
                request.state.username = None
        else:
            # No token - set to None
            request.state.user_id = None
            request.state.username = None
        
        # Continue with the request
        response = await call_next(request)
        return response
        
    except Exception as e:
        # If middleware fails, set defaults and continue
        request.state.user_id = None
        request.state.username = None
        response = await call_next(request)
        return response
```

### 2. Helper Functions

The system provides several helper functions for accessing user context:

#### Authentication Check
```python
def require_authentication(request: Request):
    """Require authentication - raises appropriate error based on token status"""
    if not hasattr(request.state, 'user_id') or request.state.user_id is None:
        # Check if there was an Authorization header but token was invalid
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # Had token but it was invalid - return 401
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        else:
            # No token at all - return 403
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authenticated"
            )
    return True
```

#### User ID Access
```python
def get_current_user_id(request: Request) -> int:
    """Get current user_id from request state"""
    if hasattr(request.state, 'user_id') and request.state.user_id is not None:
        return request.state.user_id
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User ID not available in request state"
    )

def get_current_username(request: Request) -> str:
    """Get current username from request state"""
    if hasattr(request.state, 'username') and request.state.username is not None:
        return request.state.username
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Username not available in request state"
    )
```

#### Database Query Helpers
```python
def get_user_filter(request: Request) -> dict:
    """Get a MongoDB filter for the current user"""
    user_id = get_current_user_id(request)
    return {"user_id": user_id}

def get_user_sort_filter(request: Request, sort_field: str = "timestamp", sort_direction: int = -1) -> tuple:
    """Get a MongoDB filter and sort for the current user"""
    user_filter = get_user_filter(request)
    sort = [(sort_field, sort_direction)]
    return user_filter, sort
```

## Usage Examples

### 1. Basic Endpoint with Authentication

```python
@app.post("/chat/gis", response_model=ChatResponse)
async def chat_gis(
    chat_request: ChatRequest,
    request: Request
):
    """Chat with GIS Expert AI"""
    try:
        # Require authentication
        require_authentication(request)
        
        # Note: user_id is available in request.state.user_id if needed for future features
        response = chatbot_service.chat(
            message=chat_request.message,
            chat_history=chat_request.chat_history
        )
        return ChatResponse(
            message=response,
            chat_history=chat_request.chat_history + [
                {"role": "user", "content": chat_request.message},
                {"role": "assistant", "content": response}
            ],
            session_id=chat_request.session_id
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like 401/403) as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}"
        )
```

### 2. Database Operations with User Context

```python
@app.get("/chats/saved", response_model=SavedChatList)
async def get_saved_chats(request: Request):
    """Get list of saved chats for current user"""
    try:
        # Require authentication
        require_authentication(request)
        
        # Use the helper function for universal user_id access
        user_filter, sort = get_user_sort_filter(request, "timestamp", -1)
        chats = mongo_service.list_documents("saved_chats", query=user_filter, sort=sort)
        
        # Transform to match expected response format
        formatted_chats = [
            {"chatname": chat.get("chatname", "Untitled"), "chat_id": str(chat.get("_id"))} 
            for chat in chats
        ]
        return SavedChatList(chats=formatted_chats)
    except HTTPException:
        # Re-raise HTTP exceptions (like 401/403) as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve saved chats: {str(e)}"
        )
```

### 3. Service Layer Access

```python
@app.post("/chat/rag", response_model=ChatResponse)
async def chat_rag(
    chat_request: ChatRequest,
    request: Request
):
    """Chat with RAG AI"""
    try:
        # Require authentication
        require_authentication(request)
        
        # Get user_id for service layer
        user_id = get_current_user_id(request)
        response = rag_service.chat(
            message=chat_request.message,
            model_id=chat_request.model_id,
            session_id=chat_request.session_id,
            user_id=user_id  # Pass user_id to service if needed
        )
        # ... rest of the implementation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG chat failed: {str(e)}"
        )
```

## Key Benefits

### 1. **Clean Code**
- No need to pass `user_id` through multiple function calls
- Endpoints are cleaner and more focused on business logic
- Reduces parameter pollution in function signatures

### 2. **Consistent Authentication**
- All protected endpoints use the same authentication pattern
- Centralized authentication logic in one place
- Consistent error handling across the application

### 3. **Maintainability**
- Easy to modify authentication behavior globally
- Clear separation of concerns between authentication and business logic
- Reduced risk of forgetting to check authentication in new endpoints

### 4. **Performance**
- User context is extracted once per request
- No repeated JWT verification in multiple functions
- Efficient database query filtering

## Error Handling

The system provides appropriate HTTP status codes based on the authentication scenario:

- **401 Unauthorized**: Invalid or expired token
- **403 Forbidden**: No authentication token provided
- **422 Unprocessable Entity**: Request validation errors (FastAPI handles this before authentication)

## Best Practices

### 1. **Always Use Helper Functions**
```python
# ✅ Good - Use helper functions
user_id = get_current_user_id(request)
require_authentication(request)

# ❌ Bad - Direct access to request.state
user_id = request.state.user_id
```

### 2. **Handle HTTPException Properly**
```python
try:
    require_authentication(request)
    # ... business logic
except HTTPException:
    # Re-raise HTTP exceptions (like 401/403) as-is
    raise
except Exception as e:
    # Handle other exceptions
    raise HTTPException(status_code=500, detail=str(e))
```

### 3. **Use Database Helpers for Queries**
```python
# ✅ Good - Use helper functions
user_filter, sort = get_user_sort_filter(request, "timestamp", -1)
chats = mongo_service.list_documents("saved_chats", query=user_filter, sort=sort)

# ❌ Bad - Manual filter creation
user_id = get_current_user_id(request)
chats = mongo_service.list_documents("saved_chats", query={"user_id": user_id})
```

## Adding New Protected Endpoints

When adding new endpoints that require authentication:

1. **Add the Request parameter**:
   ```python
   async def new_endpoint(data: SomeModel, request: Request):
   ```

2. **Require authentication**:
   ```python
   require_authentication(request)
   ```

3. **Access user context as needed**:
   ```python
   user_id = get_current_user_id(request)
   username = get_current_username(request)
   ```

4. **Use database helpers for queries**:
   ```python
   user_filter = get_user_filter(request)
   ```

## Debugging

The system includes a debug endpoint to help troubleshoot user context issues:

```python
@app.get("/debug/user-context")
async def debug_user_context(request: Request):
    """Debug endpoint to check user context in request state"""
    return {
        "has_user_id": hasattr(request.state, 'user_id'),
        "user_id": getattr(request.state, 'user_id', None),
        "has_username": hasattr(request.state, 'username'),
        "username": getattr(request.state, 'username', None),
        "state_attributes": list(request.state.__dict__.keys()) if hasattr(request.state, '__dict__') else []
    }
```

## Security Considerations

- **Request Scoped**: User context is isolated to each request
- **No Cross-Request Leakage**: Each request gets fresh user context
- **Token Validation**: JWT tokens are validated on every request
- **Graceful Degradation**: Invalid tokens don't crash the application

## Migration from Old System

If you're updating existing endpoints:

1. **Replace `Depends(get_current_user)`** with `request: Request`
2. **Add `require_authentication(request)`** at the start of the function
3. **Use helper functions** instead of extracting user info from dependencies
4. **Update error handling** to catch and re-raise HTTPException

## Conclusion

The Universal User ID Access system provides a clean, maintainable, and secure way to handle user context throughout the Ellipsoid Labs backend. By following the patterns and best practices outlined in this document, you can ensure consistent authentication and user context handling across all endpoints.

For questions or issues, refer to the existing endpoint implementations in `backend/main.py` as examples of proper usage.
