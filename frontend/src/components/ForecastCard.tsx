import { WindowScore } from '../lib/api';

interface ForecastCardProps {
  window: WindowScore;
  useKnots: boolean;
}

export default function ForecastCard({ window, useKnots }: ForecastCardProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-700 bg-green-50';
    if (score >= 60) return 'text-blue-700 bg-blue-50';
    if (score >= 40) return 'text-orange-700 bg-orange-50';
    return 'text-red-700 bg-red-50';
  };

  const formatTime = (timeStr: string) => {
    const date = new Date(timeStr);
    return date.toLocaleTimeString('es-ES', { 
      hour: '2-digit', 
      minute: '2-digit',
      timeZone: 'Europe/Madrid'
    });
  };

  const formatDate = (timeStr: string) => {
    const date = new Date(timeStr);
    return date.toLocaleDateString('es-ES', { 
      day: 'numeric',
      month: 'short',
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
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <div className="text-xs text-gray-500">{formatDate(window.time)}</div>
          <div className="text-lg font-semibold text-gray-900">{formatTime(window.time)}</div>
        </div>
        <div className={`text-3xl font-bold px-3 py-1 rounded-xl ${getScoreColor(window.score)}`}>
          {window.score}
        </div>
      </div>

      <div className="mb-3">
        <div className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${getScoreColor(window.score)}`}>
          {window.label}
        </div>
      </div>

      <div className="mb-4 text-sm text-gray-500">
        {getBriefReason()}
      </div>

      <div className="grid grid-cols-2 gap-2 text-sm">
        <div className="bg-gray-50 rounded-lg p-2">
          <div className="text-xs text-gray-500">Viento</div>
          <div className="font-medium text-gray-900">{convertWindSpeed(window.raw.wind_kn)}</div>
        </div>
        <div className="bg-gray-50 rounded-lg p-2">
          <div className="text-xs text-gray-500">Rachas</div>
          <div className="font-medium text-gray-900">{convertWindSpeed(window.raw.gust_kn)}</div>
        </div>
        {window.raw.wave_hs_m !== null && window.raw.wave_hs_m !== undefined && (
          <>
            <div className="bg-gray-50 rounded-lg p-2">
              <div className="text-xs text-gray-500">Ola (Hs)</div>
              <div className="font-medium text-gray-900">{window.raw.wave_hs_m.toFixed(1)} m</div>
            </div>
            {window.raw.wave_tp_s && (
              <div className="bg-gray-50 rounded-lg p-2">
                <div className="text-xs text-gray-500">Periodo (Tp)</div>
                <div className="font-medium text-gray-900">{window.raw.wave_tp_s.toFixed(1)} s</div>
              </div>
            )}
          </>
        )}
        <div className="bg-gray-50 rounded-lg p-2">
          <div className="text-xs text-gray-500">Precipitación</div>
          <div className="font-medium text-gray-900">{window.raw.precip_mm_h.toFixed(1)} mm/h</div>
        </div>
        <div className="bg-gray-50 rounded-lg p-2">
          <div className="text-xs text-gray-500">Temperatura</div>
          <div className="font-medium text-gray-900">{window.raw.temp_c.toFixed(1)}°C</div>
        </div>
      </div>
    </div>
  );
}
