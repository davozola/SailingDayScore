import { WindowScore } from '../lib/api';
import TimeSlot from './TimeSlot';

interface DayViewProps {
  date: string;
  windows: WindowScore[];
  onSlotClick: (window: WindowScore) => void;
}

export default function DayView({ windows, onSlotClick }: DayViewProps) {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('es-ES', { 
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      timeZone: 'Europe/Madrid'
    });
  };

  const bestWindowOfDay = windows.reduce((best, current) => 
    current.score > best.score ? current : best
  , windows[0]);

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-2xl font-bold text-gray-800 capitalize">
          {formatDate(windows[0].time)}
        </h3>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">Mejor:</span>
          <div className={`px-3 py-1 rounded-full font-semibold ${
            bestWindowOfDay.score >= 80 ? 'bg-green-100 text-green-700' :
            bestWindowOfDay.score >= 60 ? 'bg-blue-100 text-blue-700' :
            bestWindowOfDay.score >= 40 ? 'bg-yellow-100 text-yellow-700' :
            'bg-red-100 text-red-700'
          }`}>
            {bestWindowOfDay.score}
          </div>
        </div>
      </div>
      
      <div className="overflow-x-auto">
        <div className="flex space-x-4 pb-2">
          {windows.map((window, idx) => (
            <TimeSlot 
              key={idx} 
              window={window} 
              onClick={() => onSlotClick(window)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
