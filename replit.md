# Sailing Day Score ⛵

## Overview

Sailing Day Score is a web application that calculates a 0-100 navigability score for different types of boats and experience levels based on real-time weather and marine conditions. The app provides 3-hour interval forecasts to help sailors identify the best sailing windows, using free Open-Meteo APIs for weather, marine, and geocoding data.

**Status**: ✅ Fully implemented and functional with 23 passing pytest tests

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (September 30, 2025)

### Latest Updates
- ✅ **Fixed wave height scoring inconsistencies**: Ensured smaller waves always score better than larger waves
  - Added graduated wave height bonus: +8 pts at 0m scaling to 0 at optimal (0.3m now scores better than 0.7m)
  - Implemented aggressive period bonus scaling: full bonus for ≤0.4m waves, reduces to 40% at 1.5m+ waves
  - Prevents long-period swells from making large waves score better than small waves
  - Example: velero medio 0.3m→59 pts, 0.7m→55 pts (with same Tp=7s)
- ✅ **Reduced gust penalties for optimal wind conditions**: Made scoring more forgiving when base wind is good
  - Increased penalty reduction in optimal range from 50% to 65% (multiplier 0.35)
  - Raised gust factor thresholds by +0.2 when in optimal range (allows up to 1.4x gusts penalty-free)
  - Capped maximum gust penalty at -8 points when wind is in optimal range
  - Principiantes with 6kn wind (optimal for dinghy) now score appropriately despite moderate gusts
- ✅ **Fixed scoring algorithm for low wind conditions**: Adjusted penalties to allow proper score variation
  - Changed from flat -5 pts/kn to progressive: -3 pts/kn (0-3kn below optimal), -4 pts/kn (3-6kn), -5 pts/kn (6+kn)
  - Reduced minimum navigable score from 40 to 25 points to allow realistic low-wind scoring
  - Barcelona now shows score range 25-52 instead of flat 40 across all windows
  - All 23 pytest tests continue passing with adjusted algorithm
- ✅ **Updated boat types with professional classifications**: New system based on eslora and real vessel types
  - Vela ligera/dinghy (7-15 pies): Optimist, Laser, 420, 470 - Wind 6-18 kn, Waves ≤0.6-1.0m
  - Catamarán ligero (14-20 pies): Hobie Cat, Nacra, Dart - Wind 8-22 kn, Waves ≤0.8-1.5m
  - Velero pequeño (20-30 pies): Beneteau First 25, J/80 - Wind 8-20 kn, Waves ≤1.0-2.0m
  - Velero medio (30-40 pies): Bavaria 34, Sun Odyssey 36 - Wind 10-24 kn, Waves ≤1.5-2.5m
  - Velero grande (40-50 pies): Hanse 45, Jeanneau 49 - Wind 10-26 kn, Waves ≤2.0-3.0m
  - Tablas (windsurf/wing/foil): Wind 12-30 kn, Waves ≤0.8-1.5m
  - Updated all scoring matrices with proper wind/wave thresholds per skill level
  - Changed "ft" to "pies" for Spanish consistency
- ✅ **Added contextual descriptions in detail modal**: Personalized guidance based on boat type and skill level
  - Smart recommendations tailored to user's experience (principiante/intermedio/avanzado)
  - Boat-specific advice for different vessel types
  - Score-based messaging adjusts from encouraging (80+) to cautionary (<40)
  - Displayed in blue info box between score and conditions sections
- ✅ **Simplified scoring labels**: "A valorar" (was "A valorar con experiencia"), "Aceptable" (was "Aceptable con cautela")
- ✅ **Consistent card widths**: ForecastCard components now have uniform 320px minimum width
- ✅ **Redesigned UI with minimalist aesthetic**: Clean, professional look with subtle colors and improved spacing
  - Header simplified: Smaller title (text-3xl), left-aligned, no emoji
  - Background changed to lighter shade (#fafafa) for softer appearance
  - Form labels reduced to text-xs font-medium for discretion
  - Buttons changed to gray-900 (dark) from blue-600 for modern feel
  - Card shadows softened (shadow-sm) with subtle borders (border-gray-200)
  - Border radius increased to rounded-2xl for smoother appearance
  - Typography refined across all components for visual hierarchy
  - Color palette balanced: green-600/blue-600/orange-500/red-500 for scores
- ✅ Simplified forecast card UI: 2-3 word brief reasons ("Condiciones ideales", "Mar agitado", "Viento flojo") below score
- ✅ Removed detailed reasons and warning flags blocks for cleaner interface
- ✅ Enhanced scoring algorithm: 75 base points for optimal wind (up from 60), steeper degradation for light winds (-5/kn vs -3/kn)
- ✅ Reduced gust penalties by 50% when wind is in optimal range for more accurate scoring
- ✅ Improved swell bonuses: Tp ≥8s now +10 points, +15 total with low waves (≤1.5m)

### Earlier Implementation
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
- Starts with a base score of 75 points for optimal wind conditions
- Applies steeper degradation for light winds (-5/kn) and moderate for strong winds (-4/kn)
- Reduces gust penalties by 50% when wind is in optimal range (contextual evaluation)
- Enhanced swell bonuses: Tp ≥8s +10 points, +15 total with low waves (≤1.5m)
- Applies penalties/bonuses for: wave height, wave/wind direction alignment, precipitation, temperature
- Implements skill-based "no-go" thresholds that prevent dangerous sailing conditions
- Returns structured scores with brief qualitative reasons (2-3 words)

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