import { useState } from 'react';
import LocationSearch from './components/LocationSearch';
import BestWindow from './components/BestWindow';
import DayView from './components/DayView';
import DetailModal from './components/DetailModal';
import { geocode, getScore, GeocodeResult, ScoreResponse, WindowScore } from './lib/api';

function App() {
  const [selectedLocation, setSelectedLocation] = useState<GeocodeResult | null>(null);
  const [boatType, setBoatType] = useState('velero_medio');
  const [skill, setSkill] = useState('intermedio');
  const [forecastData, setForecastData] = useState<ScoreResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [useKnots, setUseKnots] = useState(true);
  const [selectedWindow, setSelectedWindow] = useState<WindowScore | null>(null);
  const [showNightSlots, setShowNightSlots] = useState(false);
  const [minWind, setMinWind] = useState(10);
  const [maxWind, setMaxWind] = useState(25);
  const [maxGust, setMaxGust] = useState(35);
  const [maxWave, setMaxWave] = useState(2.5);

  const handleLocationSelect = (location: GeocodeResult) => {
    setSelectedLocation(location);
    setForecastData(null);
  };

  const handleSkillChange = (newSkill: string) => {
    setSkill(newSkill);
    if (newSkill === 'principiante') {
      setMinWind(8);
      setMaxWind(20);
      setMaxGust(28);
      setMaxWave(1.5);
    } else if (newSkill === 'intermedio') {
      setMinWind(10);
      setMaxWind(25);
      setMaxGust(35);
      setMaxWave(2.5);
    } else {
      setMinWind(12);
      setMaxWind(32);
      setMaxGust(40);
      setMaxWave(3.0);
    }
  };

  const filterTimeSlots = (windows: WindowScore[]) => {
    if (showNightSlots) return windows;
    
    return windows.filter(window => {
      const hour = new Date(window.time).getHours();
      return hour >= 8 && hour <= 21;
    });
  };

  const groupWindowsByDay = (windows: WindowScore[]) => {
    const grouped: { [key: string]: WindowScore[] } = {};
    windows.forEach(window => {
      const date = window.time.split('T')[0];
      if (!grouped[date]) {
        grouped[date] = [];
      }
      grouped[date].push(window);
    });
    return Object.entries(grouped).map(([date, windows]) => ({ date, windows }));
  };

  const handleCalculate = async () => {
    if (!selectedLocation) {
      setError('Por favor, selecciona una ubicación');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const today = new Date().toISOString().split('T')[0];
      const data = await getScore({
        lat: selectedLocation.lat,
        lon: selectedLocation.lon,
        boat_type: boatType,
        skill: skill,
        date: today,
        timezone: 'Europe/Madrid'
      });
      setForecastData(data);
    } catch (err) {
      setError('Error al obtener los datos. Por favor, intenta de nuevo.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-6 py-6 max-w-6xl">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-1">
            Sailing Day Score
          </h1>
          <p className="text-gray-600 text-sm">
            Calcula la navegabilidad del día según condiciones meteorológicas y marinas
          </p>
        </header>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 mb-6">
          <div className="space-y-6">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-2">
                Ubicación
              </label>
              <LocationSearch onSelect={handleLocationSelect} onSearch={geocode} />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-2">
                  Tipo de embarcación
                </label>
                <select
                  value={boatType}
                  onChange={(e) => setBoatType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-gray-400 bg-white text-sm"
                >
                  <option value="dinghy">Vela ligera/dinghy (7-15 pies)</option>
                  <option value="catamaran_ligero">Catamarán ligero (14-20 pies)</option>
                  <option value="velero_pequeno">Velero pequeño (20-30 pies)</option>
                  <option value="velero_medio">Velero medio (30-40 pies)</option>
                  <option value="velero_grande">Velero grande (40-50 pies)</option>
                  <option value="tablas">Tablas (windsurf/wing/foil)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-600 mb-2">
                  Nivel de experiencia
                </label>
                <select
                  value={skill}
                  onChange={(e) => handleSkillChange(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-gray-400 bg-white text-sm"
                >
                  <option value="principiante">Principiante</option>
                  <option value="intermedio">Intermedio</option>
                  <option value="avanzado">Avanzado</option>
                </select>
              </div>
            </div>

            <div className="bg-gray-50 rounded-xl p-4">
              <h3 className="text-xs font-medium text-gray-600 mb-3">Límites de seguridad (personalizables)</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Viento mín. (kn)</label>
                  <input
                    type="number"
                    value={minWind}
                    onChange={(e) => setMinWind(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-gray-400 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Viento máx. (kn)</label>
                  <input
                    type="number"
                    value={maxWind}
                    onChange={(e) => setMaxWind(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-gray-400 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Rachas máx. (kn)</label>
                  <input
                    type="number"
                    value={maxGust}
                    onChange={(e) => setMaxGust(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-gray-400 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Ola máx. (m)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={maxWave}
                    onChange={(e) => setMaxWave(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-gray-400 text-sm"
                  />
                </div>
              </div>
            </div>

            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div className="flex flex-wrap items-center gap-4">
                <div className="flex items-center space-x-2">
                  <label className="text-xs font-medium text-gray-600">Unidades:</label>
                  <button
                    onClick={() => setUseKnots(true)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${useKnots ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
                  >
                    Nudos (kn)
                  </button>
                  <button
                    onClick={() => setUseKnots(false)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${!useKnots ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
                  >
                    m/s
                  </button>
                </div>
                
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={showNightSlots}
                    onChange={(e) => setShowNightSlots(e.target.checked)}
                    className="w-4 h-4 text-gray-900 rounded focus:ring-gray-500"
                  />
                  <span className="text-xs text-gray-600">Mostrar franjas nocturnas</span>
                </label>
              </div>

              <button
                onClick={handleCalculate}
                disabled={loading || !selectedLocation}
                className="px-6 py-2.5 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-800 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? 'Calculando...' : 'Calcular Score'}
              </button>
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {forecastData && (
          <div>
            {forecastData.best_window && (
              <BestWindow window={forecastData.best_window} useKnots={useKnots} />
            )}

            <h2 className="text-2xl font-bold mb-4">Previsión 5 días</h2>
            <p className="text-sm text-gray-600 mb-4">
              {showNightSlots ? 'Mostrando todas las franjas (24h)' : 'Mostrando franjas de 8:00 a 21:00'}
            </p>
            {groupWindowsByDay(filterTimeSlots(forecastData.windows)).map(({ date, windows }) => (
              <DayView
                key={date}
                date={date}
                windows={windows}
                onSlotClick={setSelectedWindow}
              />
            ))}

            <div className="mt-8 p-4 bg-blue-50 rounded-lg text-sm text-gray-700">
              <p>
                <strong>Nota:</strong> Los datos provienen de Open-Meteo (gratuito, sin clave API) 
                y pueden contener incertidumbre. Esta herramienta no sustituye los partes meteorológicos 
                oficiales y es solo una ayuda para la planificación.
              </p>
            </div>
          </div>
        )}

        {!forecastData && !loading && (
          <div className="text-center text-gray-500 py-12">
            <span className="text-6xl mb-4 block">🌊</span>
            <p className="text-xl">Selecciona una ubicación y configura tus preferencias para comenzar</p>
          </div>
        )}
      </div>

      <DetailModal
        window={selectedWindow}
        onClose={() => setSelectedWindow(null)}
        useKnots={useKnots}
        boatType={boatType}
        skill={skill}
      />
    </div>
  );
}

export default App;
