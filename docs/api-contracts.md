# FlameLens — API Contracts & Specifications

## Base URL & Versioning
- **Base URL**: `http://localhost:8000`
- **Version Prefix**: `/api/v1`
- **Interactive Documentation**:
  - Swagger UI: `/docs`
  - ReDoc: `/redoc`

---

## Standard Error Response Format
All HTTP errors and unhandled exceptions return a standardized JSON envelope:

```json
{
  "error": {
    "type": "HTTPException | ValidationError | FlameLensException",
    "message": "Human-readable description of error.",
    "status_code": 404,
    "details": {}
  }
}
```

---

## Phase 1 Implemented Endpoints

### 1. Root Service Discovery
`GET /`

**Response (200 OK):**
```json
{
  "application": "FlameLens",
  "version": "0.1.0",
  "status": "online",
  "docs_url": "/docs",
  "api_v1": "/api/v1",
  "message": "Welcome to FlameLens API - NASA Microgravity Combustion Research Explorer"
}
```

### 2. System Health & Diagnostics
`GET /api/v1/health`

**Response (200 OK):**
```json
{
  "status": "healthy",
  "application": "FlameLens",
  "version": "0.1.0",
  "environment": "development",
  "timestamp": "2026-11-13T21:40:38.627231+00:00"
}
```
