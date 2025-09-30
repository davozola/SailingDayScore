import { WindowScore } from '../lib/api';

interface BestWindowProps {
  window: WindowScore;
  useKnots: boolean;
}

export default function BestWindow({ window, useKnots }: BestWindowProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'border-green-500 bg-green-50';
    if (score >= 60) return 'border-blue-500 bg-blue-50';
    if (score >= 40) return 'border-yellow-500 bg-yellow-50';
    return 'border-red-500 bg-red-50';
  };

  const formatTime = (timeStr: string) => {
    const date = new Date(timeStr);
    return date.toLocaleString('es-ES', { 
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      hour: '2-digit', 
      minute: '2-digit',
      timeZone: 'Europe/Madrid'
    });
  };

  const convertWindSpeed = (kn: number) => {
    if (useKnots) return `${kn.toFixed(1)} kn`;
    return `${(kn * 0.514444).toFixed(1)} m/s`;
  };

  return (
    <div className={`border-4 rounded-xl p-6 mb-6 ${getScoreColor(window.score)}`}>
      <div className="flex items-center mb-4">
        <span className="text-3xl mr-3">⭐</span>
        <h2 className="text-2xl font-bold">Mejor ventana</h2>
      </div>
      
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="text-lg font-semibold mb-2">{formatTime(window.time)}</div>
          <div className="text-3xl font-bold mb-2">{window.label}</div>
          <div className="space-y-1">
            {window.reasons.map((reason, idx) => (
              <div key={idx} className="text-sm flex items-start">
                <span className="mr-2">✓</span>
                <span>{reason}</span>
              </div>
            ))}
          </div>
        </div>
        
        <div className="flex-shrink-0">
          <div className="text-6xl font-bold text-center">
            {window.score}
          </div>
          <div className="text-center text-sm text-gray-600 mt-2">Puntuación</div>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-300 grid grid-cols-2 md:grid-cols-4 gap-3">
        <div>
          <div className="text-xs text-gray-600">Viento</div>
          <div className="font-semibold">{convertWindSpeed(window.raw.wind_kn)}</div>
        </div>
        <div>
          <div className="text-xs text-gray-600">Rachas</div>
          <div className="font-semibold">{convertWindSpeed(window.raw.gust_kn)}</div>
        </div>
        {window.raw.wave_hs_m !== null && window.raw.wave_hs_m !== undefined && (
          <div>
            <div className="text-xs text-gray-600">Ola</div>
            <div className="font-semibold">{window.raw.wave_hs_m.toFixed(1)} m</div>
          </div>
        )}
        <div>
          <div className="text-xs text-gray-600">Temperatura</div>
          <div className="font-semibold">{window.raw.temp_c.toFixed(1)}°C</div>
        </div>
      </div>
    </div>
  );
}
