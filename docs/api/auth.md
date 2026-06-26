# API Authentication & Security Model

## 1. Current State: Single-Tenant / Local Execution
Open-ChatBot is currently implemented as a **single-tenant local application**. 

* **No Authentication Middleware:** The API endpoints (`/chat`, `/characters`, etc.) do not currently enforce JWT, OAuth2, or session cookie verification.
* **Auto-user Provisioning:** The backend dynamically registers/manages a single active user in SQLite database (`chatbot.db`) through the `/users/me` endpoint. See [users.py](file:///G:/Programas/Open-ChatBot/src/backend/api/users.py#L22-L31) for implementation details.
* **Network Isolation Security:** The application binds to `localhost` by default. There is no access control mechanism at the application layer; the security model relies entirely on the local machine's system boundary and loopback interface isolation.

## 2. Recommendations for Multi-Tenant / Production Deployments
To expand this platform for external or cloud deployments, the following auth protocols must be implemented:
1. **OAuth2 / JWT Bearer Tokens:** Wrap API routes with FastAPI `Security` scopes.
2. **User Context Separation:** Update `get_me()` helper to extract user context from the JWT payload rather than querying the default first active user.
3. **CORS Configuration:** Configure restrictive CORS policies to allow requests only from authorized origins.
