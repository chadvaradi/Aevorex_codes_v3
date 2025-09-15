# Authentication Endpoints

**Category:** Authentication  
**Total Endpoints:** 8  
**Authentication:** Not required (for login endpoints)  
**Caching:** No caching

This category handles user authentication, session management, and OAuth integration.

---

## 1. GET /api/v1/auth/login

**Description:** Initiates OAuth login process and redirects to authentication provider.

**Parameters:** None

**Response:** HTTP 302 redirect to OAuth provider

**Behavior:**
- No authentication required
- Redirects to configured OAuth provider
- Sets secure session cookies
- Generates CSRF state token

**Usage:**
```bash
curl -L https://api.aevorex.com/api/v1/auth/login
```

---

## 2. GET /api/v1/auth/start

**Description:** Returns HTML page that starts the OAuth authentication flow.

**Parameters:** None

**Response:**
- **Type:** `text/html`
- **Content:** HTML page with OAuth initialization script

**Behavior:**
- No authentication required
- Returns HTML page for browser-based authentication
- Includes JavaScript for OAuth flow initiation

**Usage:**
```bash
curl https://api.aevorex.com/api/v1/auth/start
```

---

## 3. GET /api/v1/auth/callback

**Description:** OAuth callback endpoint that processes authentication response.

**Parameters:**
- **Query:**
  - `code` (string, required): Authorization code from OAuth provider
  - `state` (string, required): State parameter for security

**Response:** HTTP 302 redirect to application with session established

**Behavior:**
- No authentication required
- Validates state parameter for CSRF protection
- Exchanges authorization code for access token
- Creates user session
- Redirects to application dashboard

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/auth/callback?code=abc123&state=xyz789"
```

---

## 4. GET /api/v1/auth/status

**Description:** Returns current authentication status.

**Parameters:** None

**Response:**
```json
{
  "authenticated": true,
  "user_id": "user123",
  "expires_at": "2024-01-15T12:00:00Z",
  "session_id": "sess_abc123"
}
```

**Response Fields:**
- `authenticated` (boolean): Whether user is authenticated
- `user_id` (string): User identifier
- `expires_at` (string): Session expiration time
- `session_id` (string): Current session identifier

**Behavior:**
- No authentication required
- Returns authentication status based on session cookies
- Returns 401 if session is invalid

**Usage:**
```bash
curl https://api.aevorex.com/api/v1/auth/status
```

---

## 5. GET /api/v1/auth/me

**Description:** Returns current user profile information.

**Parameters:** None

**Response:**
```json
{
  "user_id": "user123",
  "email": "user@example.com",
  "name": "John Doe",
  "subscription_tier": "pro",
  "created_at": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-15T10:30:00Z",
  "preferences": {
    "timezone": "UTC",
    "currency": "USD",
    "language": "en"
  }
}
```

**Response Fields:**
- `user_id` (string): Unique user identifier
- `email` (string): User email address
- `name` (string): User display name
- `subscription_tier` (string): Subscription level (free, pro, enterprise)
- `created_at` (string): Account creation timestamp
- `last_login` (string): Last login timestamp
- `preferences` (object): User preferences

**Behavior:**
- No authentication required
- Returns user profile from session
- Returns 401 if not authenticated

**Usage:**
```bash
curl https://api.aevorex.com/api/v1/auth/me
```

---

## 6. GET /api/v1/auth/logout

**Description:** Logout endpoint (GET method).

**Parameters:** None

**Response:**
```json
{
  "message": "Logged out successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Behavior:**
- No authentication required
- Clears session cookies
- Invalidates current session
- Redirects to login page

**Usage:**
```bash
curl https://api.aevorex.com/api/v1/auth/logout
```

---

## 7. POST /api/v1/auth/logout

**Description:** Logout endpoint (POST method).

**Parameters:** None

**Response:**
```json
{
  "message": "Logged out successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Behavior:**
- No authentication required
- Clears session cookies
- Invalidates current session
- Returns JSON response (no redirect)

**Usage:**
```bash
curl -X POST https://api.aevorex.com/api/v1/auth/logout
```

---

## 8. POST /api/v1/auth/refresh-token

**Description:** Refreshes access token using refresh token.

**Parameters:**
- **Body:**
  - `refresh_token` (string, required): Valid refresh token

**Request Body:**
```json
{
  "refresh_token": "rt_abc123def456"
}
```

**Response:**
```json
{
  "access_token": "at_new_access_token_here",
  "refresh_token": "rt_new_refresh_token_here",
  "expires_in": 3600,
  "token_type": "Bearer",
  "scope": "read write"
}
```

**Response Fields:**
- `access_token` (string): New access token
- `refresh_token` (string): New refresh token
- `expires_in` (integer): Token expiration time in seconds
- `token_type` (string): Token type (always "Bearer")
- `scope` (string): Token permissions

**Behavior:**
- No authentication required
- Invalidates old refresh token
- Issues new token pair
- Returns 401 if refresh token is invalid

**Usage:**
```bash
curl -X POST https://api.aevorex.com/api/v1/auth/refresh-token \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "rt_abc123def456"}'
```

---

## Authentication Flow

### **OAuth Login Process**
1. User visits `/api/v1/auth/login`
2. Redirected to OAuth provider
3. User authorizes application
4. OAuth provider redirects to `/api/v1/auth/callback`
5. Application exchanges code for tokens
6. User session is created
7. User is redirected to application

### **Session Management**
- Sessions stored in secure HTTP-only cookies
- CSRF protection via state parameter
- Automatic session refresh
- Secure logout with session invalidation

### **Token Management**
- Access tokens: Short-lived (1 hour)
- Refresh tokens: Long-lived (30 days)
- Automatic token rotation on refresh
- Secure token storage

---

## Security Features

### **CSRF Protection**
- State parameter validation
- Secure session cookies
- Origin header validation

### **Session Security**
- HTTP-only cookies
- Secure flag for HTTPS
- SameSite attribute
- Session timeout

### **Token Security**
- JWT-based tokens
- Short expiration times
- Secure refresh mechanism
- Token blacklisting on logout

---

## Error Responses

### **401 Unauthorized**
```json
{
  "error": "unauthorized",
  "message": "Invalid or expired session",
  "code": 401
}
```

### **400 Bad Request**
```json
{
  "error": "invalid_request",
  "message": "Invalid refresh token",
  "code": 400
}
```

---

**Total Auth Endpoints: 8** ✅

