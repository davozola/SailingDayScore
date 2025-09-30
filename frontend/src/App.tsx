import { useState } from 'react';
import LocationSearch from './components/LocationSearch';
import ForecastCard from './components/ForecastCard';
import BestWindow from './components/BestWindow';
import { geocode, getScore, GeocodeResult, ScoreResponse } from './lib/api';

function App() {
  const [selectedLocation, setSelectedLocation] = useState<GeocodeResult | null>(null);
  const [boatType, setBoatType] = useState('cruiser_35_45');
  const [skill, setSkill] = useState('intermedio');
  const [forecastData, setForecastData] = useState<ScoreResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [useKnots, setUseKnots] = useState(true);

  const handleLocationSelect = (location: GeocodeResult) => {
    setSelectedLocation(location);
    setForecastData(null);
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
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <header className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-blue-600 mb-2">
            ⛵ Sailing Day Score
          </h1>
          <p className="text-gray-600 text-lg">
            Calcula la navegabilidad del día según condiciones meteorológicas y marinas
          </p>
        </header>

        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Ubicación
              </label>
              <LocationSearch onSelect={handleLocationSelect} onSearch={geocode} />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Tipo de embarcación
                </label>
                <select
                  value={boatType}
                  onChange={(e) => setBoatType(e.target.value)}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                >
                  <option value="vela_ligera">Vela ligera</option>
                  <option value="cruiser_35">Crucero &lt;35'</option>
                  <option value="cruiser_35_45">Crucero 35'-45'</option>
                  <option value="catamaran">Catamarán</option>
                  <option value="dinghy">Dinghy</option>
                  <option value="windsurf">Windsurf/Wingfoil</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Nivel de experiencia
                </label>
                <select
                  value={skill}
                  onChange={(e) => setSkill(e.target.value)}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                >
                  <option value="principiante">Principiante</option>
                  <option value="intermedio">Intermedio</option>
                  <option value="avanzado">Avanzado</option>
                </select>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <label className="text-sm font-semibold text-gray-700">Unidades:</label>
                <button
                  onClick={() => setUseKnots(true)}
                  className={`px-4 py-2 rounded ${useKnots ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'}`}
                >
                  Nudos (kn)
                </button>
                <button
                  onClick={() => setUseKnots(false)}
                  className={`px-4 py-2 rounded ${!useKnots ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'}`}
                >
                  m/s
                </button>
              </div>

              <button
                onClick={handleCalculate}
                disabled={loading || !selectedLocation}
                className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
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
            {forecastData.safety.no_go && (
              <div className="bg-red-100 border-2 border-red-500 rounded-lg p-6 mb-6">
                <div className="flex items-start">
                  <span className="text-3xl mr-4">🚫</span>
                  <div>
                    <h3 className="text-xl font-bold text-red-800 mb-2">
                      Condiciones NO aptas para navegar
                    </h3>
                    <ul className="space-y-1">
                      {forecastData.safety.why.map((reason, idx) => (
                        <li key={idx} className="text-red-700">• {reason}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {forecastData.best_window && (
              <BestWindow window={forecastData.best_window} useKnots={useKnots} />
            )}

            <h2 className="text-2xl font-bold mb-4">Previsión por franjas de 3 horas</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {forecastData.windows.map((window, idx) => (
                <ForecastCard key={idx} window={window} useKnots={useKnots} />
              ))}
            </div>

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
    </div>
  );
}

export default App;
