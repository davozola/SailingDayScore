const API_BASE = '';

export interface GeocodeResult {
  name: string;
  lat: number;
  lon: number;
  country?: string;
  admin1?: string;
}

export interface RawMetrics {
  wind_kn: number;
  gust_kn: number;
  wave_hs_m?: number;
  wave_tp_s?: number;
  wave_dir_deg?: number;
  wind_dir_deg?: number;
  precip_mm_h: number;
  temp_c: number;
}

export interface WindowScore {
  time: string;
  score: number;
  label: string;
  reasons: string[];
  flags: string[];
  raw: RawMetrics;
}

export interface ScoreResponse {
  location: {
    name: string;
    lat: number;
    lon: number;
  };
  windows: WindowScore[];
  best_window?: WindowScore;
  safety: {
    no_go: boolean;
    why: string[];
  };
}

export interface ScoreRequest {
  lat: number;
  lon: number;
  boat_type: string;
  skill: string;
  date: string;
  timezone: string;
}

export async function geocode(query: string): Promise<GeocodeResult[]> {
  const response = await fetch(`${API_BASE}/api/geocode?q=${encodeURIComponent(query)}`);
  if (!response.ok) {
    throw new Error('Error al buscar ubicación');
  }
  const data = await response.json();
  return data.results || [];
}

export async function getScore(request: ScoreRequest): Promise<ScoreResponse> {
  const response = await fetch(`${API_BASE}/api/score`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error('Error al calcular puntuación');
  }
  return response.json();
}
