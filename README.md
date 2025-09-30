# Sailing Day Score ⛵

Aplicación web que calcula una puntuación 0-100 de navegabilidad para diferentes tipos de embarcaciones y niveles de experiencia, basándose en condiciones meteorológicas y marinas en tiempo real.

## Características

- **Cálculo de Score 0-100**: Algoritmo completo que evalúa viento, rachas, altura de ola, periodo, dirección, precipitación y temperatura
- **Múltiples tipos de embarcación**: Vela ligera, cruceros, catamarán, dinghy, windsurf/wingfoil
- **Niveles de experiencia**: Principiante, intermedio, avanzado con umbrales de seguridad específicos
- **Predicción por franjas de 3 horas**: Visualiza las mejores ventanas de navegación
- **Sin claves API**: Usa Open-Meteo (APIs gratuitas de forecast, marine y geocoding)
- **Tests completos**: Suite de pytest con 23 tests para validar lógica de scoring
- **Diseño responsive**: Interfaz en español optimizada para móvil y desktop

## Stack Tecnológico

### Backend
- Python 3.11
- FastAPI con Pydantic
- Uvicorn (servidor ASGI)
- httpx (cliente HTTP asíncrono)
- pytest (testing)

### Frontend
- React 18
- Vite (build tool)
- Tailwind CSS
- TypeScript

## Instalación y Ejecución

### Backend

```bash
PYTHONPATH=/home/runner/workspace python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

El backend estará disponible en `http://localhost:8000`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

El frontend estará disponible en `http://localhost:5000`

## Endpoints API

### GET /api/health
Verifica el estado del servidor.

**Respuesta:**
```json
{"status": "ok"}
```

### GET /api/geocode?q=BARCELONA
Busca ubicaciones usando geocoding de Open-Meteo.

**Parámetros:**
- `q`: Nombre de la ubicación (ciudad, puerto)

**Respuesta:**
```json
{
  "results": [
    {
      "name": "Barcelona",
      "lat": 41.38879,
      "lon": 2.15899,
      "country": "España",
      "admin1": "Cataluña"
    }
  ]
}
```

### POST /api/score
Calcula el score de navegabilidad para una ubicación y configuración.

**Body:**
```json
{
  "lat": 41.34,
  "lon": 2.16,
  "boat_type": "cruiser_35_45",
  "skill": "intermediate",
  "date": "2025-09-30",
  "timezone": "Europe/Madrid"
}
```

**Tipos de embarcación válidos:**
- `vela_ligera`
- `cruiser_35` (crucero <35')
- `cruiser_35_45` (crucero 35'-45')
- `catamaran`
- `dinghy`
- `windsurf`

**Niveles de experiencia válidos:**
- `principiante`
- `intermedio`
- `avanzado`

**Respuesta:**
```json
{
  "location": {
    "name": "Lat 41.34, Lon 2.16",
    "lat": 41.34,
    "lon": 2.16
  },
  "windows": [
    {
      "time": "2025-09-30T12:00:00+02:00",
      "score": 78,
      "label": "Bueno",
      "reasons": [
        "Viento 12.3 kn en rango óptimo",
        "Ola 0.7 m (favorable)",
        "Tp 7.2 s (mar de fondo)"
      ],
      "flags": [],
      "raw": {
        "wind_kn": 12.3,
        "gust_kn": 15.1,
        "wave_hs_m": 0.7,
        "wave_tp_s": 7.2,
        "wave_dir_deg": 180,
        "wind_dir_deg": 45,
        "precip_mm_h": 0.0,
        "temp_c": 22.5
      }
    }
  ],
  "best_window": { },
  "safety": {
    "no_go": false,
    "why": []
  }
}
```

## Algoritmo de Puntuación

El algoritmo calcula un score de 0-100 basándose en:

1. **Viento base (0-60 puntos)**: Según matriz óptima por barco/nivel
2. **Factor de rachas**: Penalización si gust/wind > 1.2
3. **Altura de ola (Hs)**: Penalización piecewise según barco/nivel
4. **Periodo de ola (Tp)**: Bonus si Tp ≥ 7s, penalización si < 5s
5. **Dirección ola vs viento**: Penaliza mar de viento, premia mar de largo
6. **Precipitación**: Penalización progresiva
7. **Temperatura**: Penalización si fuera de 10-32°C

### Etiquetas de Score
- 80-100: "Muy bueno"
- 60-79: "Bueno"
- 40-59: "Regular / con cautela"
- 0-39: "No recomendable"

### Umbrales de Seguridad (no_go)

**Principiante:**
- Viento > 20 kn
- Rachas > 28 kn
- Ola > 1.5 m

**Intermedio:**
- Viento > 25 kn
- Rachas > 35 kn
- Ola > 2.5 m

**Avanzado:**
- Viento > 32 kn
- Rachas > 40 kn
- Ola > 3.0 m

## Tests

Ejecutar los tests:

```bash
cd backend
python -m pytest tests/test_scoring.py -v
```

La suite incluye 23 tests que cubren:
- Scoring de viento en diferentes rangos
- Factores de rachas
- Penalizaciones por ola
- Normalización 0-100
- Umbrales no_go por nivel

## Fuente de Datos

Esta aplicación utiliza las APIs gratuitas de **Open-Meteo**:

- **Forecast API**: Datos de viento, temperatura, precipitación
- **Marine API**: Datos de oleaje (altura, periodo, dirección)
- **Geocoding API**: Búsqueda de ubicaciones

### Importante

Los datos pueden contener incertidumbre y esta herramienta **no sustituye** los partes meteorológicos oficiales. Use esta aplicación solo como ayuda para la planificación, no como única fuente de información para decisiones de navegación.

## Estructura del Proyecto

```
/backend
  main.py                 # Endpoints FastAPI
  models.py              # Modelos Pydantic
  scoring/
    wind.py              # Lógica scoring de viento
    waves.py             # Lógica scoring de olas
    combined.py          # Scoring combinado
  services/
    openmeteo.py         # Cliente API forecast
    marine.py            # Cliente API marine
    geocode.py           # Cliente API geocoding
  tests/
    test_scoring.py      # Tests unitarios

/frontend
  src/
    App.tsx              # Componente principal
    main.tsx             # Punto de entrada
    components/
      LocationSearch.tsx  # Búsqueda con autocompletado
      ForecastCard.tsx    # Tarjeta de pronóstico
      BestWindow.tsx      # Mejor ventana destacada
    lib/
      api.ts             # Cliente API backend
```

## Licencia

Este proyecto utiliza datos de Open-Meteo bajo licencia CC-BY 4.0.

## Créditos

Datos meteorológicos y marinos proporcionados por [Open-Meteo](https://open-meteo.com/)
