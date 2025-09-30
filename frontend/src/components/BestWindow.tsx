import { WindowScore } from '../lib/api';

interface BestWindowProps {
  window: WindowScore;
  useKnots: boolean;
}

export default function BestWindow({ window, useKnots }: BestWindowProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'border-green-300 bg-green-50';
    if (score >= 60) return 'border-blue-300 bg-blue-50';
    if (score >= 40) return 'border-orange-300 bg-orange-50';
    return 'border-red-300 bg-red-50';
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

  const getBriefReason = () => {
    const wind = window.raw.wind_kn;
    const gust = window.raw.gust_kn;
    const wave = window.raw.wave_hs_m || 0;
    const gustFactor = wind > 0 ? gust / wind : 1;

    if (wave > 2.0) return 'Mar agitado';
    if (gustFactor > 2.0) return 'Rachas fuertes';
    if (wind < 5) return 'Viento flojo';
    if (wind >= 10 && wind <= 20 && wave <= 1.5) return 'Condiciones ideales';
    if (wind > 25) return 'Viento fuerte';
    return 'Condiciones moderadas';
  };

  return (
    <div className={`border-2 rounded-2xl p-6 mb-6 ${getScoreColor(window.score)}`}>
      <div className="flex items-center mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Mejor ventana</h2>
      </div>
      
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="text-sm text-gray-600 mb-1">{formatTime(window.time)}</div>
          <div className="text-2xl font-bold mb-2 text-gray-900">{window.label}</div>
          <div className="text-sm text-gray-500">
            {getBriefReason()}
          </div>
        </div>
        
        <div className="flex-shrink-0">
          <div className="text-5xl font-bold text-center text-gray-900">
            {window.score}
          </div>
          <div className="text-center text-xs text-gray-500 mt-1">Puntuación</div>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200 grid grid-cols-2 md:grid-cols-4 gap-3">
        <div>
          <div className="text-xs text-gray-500">Viento</div>
          <div className="font-medium text-gray-900">{convertWindSpeed(window.raw.wind_kn)}</div>
        </div>
        <div>
          <div className="text-xs text-gray-500">Rachas</div>
          <div className="font-medium text-gray-900">{convertWindSpeed(window.raw.gust_kn)}</div>
        </div>
        {window.raw.wave_hs_m !== null && window.raw.wave_hs_m !== undefined && (
          <div>
            <div className="text-xs text-gray-500">Ola</div>
            <div className="font-medium text-gray-900">{window.raw.wave_hs_m.toFixed(1)} m</div>
          </div>
        )}
        <div>
          <div className="text-xs text-gray-500">Temperatura</div>
          <div className="font-medium text-gray-900">{window.raw.temp_c.toFixed(1)}°C</div>
        </div>
      </div>
    </div>
  );
}
