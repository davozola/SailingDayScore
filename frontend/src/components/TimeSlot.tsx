import { WindowScore } from '../lib/api';

interface TimeSlotProps {
  window: WindowScore;
  onClick: () => void;
}

export default function TimeSlot({ window, onClick }: TimeSlotProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-blue-500';
    if (score >= 40) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getScoreTextColor = (score: number) => {
    if (score >= 80) return 'text-green-700';
    if (score >= 60) return 'text-blue-700';
    if (score >= 40) return 'text-yellow-700';
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

  return (
    <button
      onClick={onClick}
      className="flex flex-col items-center p-3 rounded-lg hover:shadow-lg transition-all duration-200 hover:scale-105 bg-white border-2 border-gray-200 hover:border-gray-400 min-w-[100px]"
    >
      <div className="text-xs font-semibold text-gray-600 mb-2">
        {formatTime(window.time)}
      </div>
      
      <div className={`w-16 h-16 rounded-full flex items-center justify-center ${getScoreColor(window.score)} text-white font-bold text-xl shadow-md mb-2`}>
        {window.score}
      </div>
      
      <div className={`text-xs font-semibold ${getScoreTextColor(window.score)}`}>
        {window.label}
      </div>
      
      {window.flags.length > 0 && (
        <div className="text-xs text-orange-600 mt-1">
          ⚠ {window.flags.length}
        </div>
      )}
    </button>
  );
}
