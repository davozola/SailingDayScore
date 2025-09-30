# Sailing Day Score ⛵

## Overview

Sailing Day Score is a web application that calculates a 0-100 navigability score for different types of boats and experience levels based on real-time weather and marine conditions. The app provides 3-hour interval forecasts to help sailors identify the best sailing windows, using free Open-Meteo APIs for weather, marine, and geocoding data.

**Status**: ✅ Fully implemented and functional with 23 passing pytest tests

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (September 30, 2025)

- ✅ Implemented complete backend with FastAPI (Pydantic models, Open-Meteo services, scoring algorithm)
- ✅ Created modular scoring system with wind/wave matrices and no_go safety thresholds
- ✅ Built React + Vite + Tailwind frontend with responsive design in Spanish
- ✅ Added location search with autocomplete, forecast cards, and best window highlighting
- ✅ Implemented 23 pytest tests for scoring logic (all passing)
- ✅ Configured workflows: Backend (port 8000) and Frontend (port 5000)
- ✅ Fixed import structure to use backend.* package imports for pytest/uvicorn compatibility
- ✅ Implemented proper cache management with TTL and cleanup
- ✅ Created comprehensive README with API documentation and algorithm description

## System Architecture

### Application Structure

**Monorepo Layout**: The application is split into two main directories:
- `backend/` - Python/FastAPI server
- `frontend/` - React/TypeScript SPA

This separation allows independent development and deployment of frontend and backend while maintaining clear boundaries between client and server logic.

### Backend Architecture

**Framework**: FastAPI with Uvicorn ASGI server
- Chosen for its modern async support, automatic API documentation, and built-in Pydantic validation
- Enables type-safe request/response handling with minimal boilerplate

**Modular Organization**:
- `models.py` - Pydantic models for request/response validation and enums for boat types and skill levels
- `services/` - External API integrations (Open-Meteo weather, marine, geocoding)
- `scoring/` - Core business logic split by concern (wind, waves, combined calculations)
- `tests/` - Pytest-based unit tests for scoring algorithms

**Scoring Algorithm Design**: Multi-factor scoring system that:
- Starts with a base score of 60 points for optimal wind conditions
- Applies penalties/bonuses for: wind gusts, wave height, wave period, wave/wind direction alignment, precipitation, temperature
- Implements skill-based "no-go" thresholds that prevent dangerous sailing conditions
- Returns structured scores with human-readable reasons and safety flags

**Caching Strategy**: Simple in-memory cache with TTL
- Cache key: `"{lat}_{lon}_{date}"` (rounded to 2 decimals)
- TTL: 600 seconds (10 minutes)
- Prevents redundant API calls when multiple users query the same location/date
- Trade-off: Memory-based (ephemeral), suitable for single-instance deployments

**API Endpoints**:
- `GET /api/health` - Health check
- `GET /api/geocode?q={query}` - Location search (returns top 5 matches)
- `POST /api/score` - Calculate sailing scores for a location/date/boat/skill combination

### Frontend Architecture

**Framework**: React 18 with TypeScript
- Vite as build tool for fast development and optimized production builds
- Chosen for its modern developer experience and strong ecosystem

**Styling**: Tailwind CSS utility-first approach
- Enables responsive design without custom CSS files
- Provides consistent design system with minimal configuration

**Component Structure**:
- `App.tsx` - Main application container with state management
- `LocationSearch.tsx` - Autocomplete search with debounced API calls
- `ForecastCard.tsx` - Individual 3-hour forecast window display
- `BestWindow.tsx` - Highlighted card for optimal sailing window
- `lib/api.ts` - Centralized API client with TypeScript types

**State Management**: Local React state with useState hooks
- Simple approach suitable for application complexity
- No global state management needed (Redux, Zustand, etc.)

**Unit System Toggle**: Users can switch between knots and m/s for wind speed display
- Conversion handled client-side to reduce API calls
- User preference not persisted (resets on page reload)

### Data Flow

1. User enters location → Frontend calls `/api/geocode`
2. User selects location and parameters → Frontend calls `/api/score`
3. Backend checks cache for recent data
4. If cache miss: Backend fetches from Open-Meteo (weather + marine APIs in parallel)
5. Backend samples hourly data to 3-hour intervals
6. Scoring engine processes each window with boat/skill-specific thresholds
7. Response includes all windows + highlighted best window + safety flags
8. Frontend renders cards with color-coded scores and details

### Testing Strategy

**Backend**: Pytest suite in `backend/tests/test_scoring.py`
- 23+ unit tests covering scoring functions
- Tests verify edge cases (optimal wind, low wind, high wind, gust factors, wave conditions)
- No integration tests for external APIs (uses mocked responses in actual implementation would be recommended)

**Frontend**: No test suite currently implemented
- Future: Consider Vitest + React Testing Library for component tests

## External Dependencies

### Third-Party APIs

**Open-Meteo Services** (all free, no API key required):
- **Forecast API** (`https://api.open-meteo.com/v1/forecast`) - Wind speed, gusts, temperature, precipitation, wind direction
- **Marine API** (`https://marine-api.open-meteo.com/v1/marine`) - Wave height, wave direction, wave period
- **Geocoding API** (`https://geocoding-api.open-meteo.com/v1/search`) - Location search with Spanish language support

Design rationale: Open-Meteo was chosen to eliminate API key management and usage costs while providing comprehensive marine meteorological data.

### Python Dependencies

- **FastAPI** - Modern web framework with automatic API docs
- **Pydantic** - Data validation and settings management using Python type annotations
- **Uvicorn** - Lightning-fast ASGI server
- **httpx** - Async HTTP client for external API calls
- **pytest** - Testing framework

### Frontend Dependencies

- **React 18** - UI library with hooks and concurrent features
- **TypeScript** - Static typing for JavaScript
- **Vite** - Next-generation frontend build tool
- **Tailwind CSS** - Utility-first CSS framework
- **PostCSS + Autoprefixer** - CSS processing for browser compatibility

### Infrastructure

**CORS Configuration**: Wide-open CORS (`allow_origins=["*"]`)
- Suitable for development and public APIs
- Production consideration: Restrict to specific frontend domains

**Server Configuration**:
- Backend: Port 8000, host 0.0.0.0
- Frontend: Port 5000, host 0.0.0.0
- Both configured for Replit environment with public accessibility