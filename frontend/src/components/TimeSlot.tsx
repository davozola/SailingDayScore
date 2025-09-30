import { WindowScore } from '../lib/api';

interface TimeSlotProps {
  window: WindowScore;
  onClick: () => void;
}

export default function TimeSlot({ window, onClick }: TimeSlotProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'bg-green-600';
    if (score >= 60) return 'bg-blue-600';
    if (score >= 40) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getScoreTextColor = (score: number) => {
    if (score >= 80) return 'text-green-700';
    if (score >= 60) return 'text-blue-700';
    if (score >= 40) return 'text-orange-700';
    return 'text-red-700';
  };

  const formatTime = (timeStr: string) => {
    const date = new Date(timeStr);
    return date.toLocaleTimeString('es-ES', { 
      hour: '2-digit', 
      minute: '2-digit',
      timeZone: 'Europe/Madrid'
    });
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
    <button
      onClick={onClick}
      className="flex flex-col items-center p-3 rounded-xl hover:shadow-md transition-all duration-200 bg-white border border-gray-200 hover:border-gray-300 min-w-[140px]"
    >
      <div className="text-xs font-medium text-gray-600 mb-2">
        {formatTime(window.time)}
      </div>
      
      <div className={`w-14 h-14 rounded-full flex items-center justify-center ${getScoreColor(window.score)} text-white font-bold text-lg mb-2`}>
        {window.score}
      </div>
      
      <div className={`text-xs font-medium ${getScoreTextColor(window.score)} mb-1`}>
        {window.label}
      </div>

      <div className="text-xs text-gray-500 mb-2">
        {getBriefReason()}
      </div>
      
      <div className="w-full border-t border-gray-200 pt-2 space-y-0.5">
        <div className="text-xs text-gray-600">
          🌬 {window.raw.wind_kn.toFixed(1)} kn
        </div>
        <div className="text-xs text-gray-600">
          💨 {window.raw.gust_kn.toFixed(1)} kn
        </div>
        <div className="text-xs text-gray-600">
          🌊 {(window.raw.wave_hs_m || 0).toFixed(1)} m
        </div>
      </div>
    </button>
  );
}
