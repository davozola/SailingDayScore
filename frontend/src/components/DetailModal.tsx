import { WindowScore } from '../lib/api';

interface DetailModalProps {
  window: WindowScore | null;
  onClose: () => void;
  useKnots: boolean;
  boatType?: string;
  skill?: string;
}

export default function DetailModal({ window, onClose, useKnots, boatType, skill }: DetailModalProps) {
  if (!window) return null;

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-50 border-green-500';
    if (score >= 60) return 'text-blue-600 bg-blue-50 border-blue-500';
    if (score >= 40) return 'text-yellow-600 bg-yellow-50 border-yellow-500';
    return 'text-red-600 bg-red-50 border-red-500';
  };

  const formatDateTime = (timeStr: string) => {
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

  const getContextualDescription = () => {
    if (!boatType || !skill) return null;

    const boatNames: { [key: string]: string } = {
      'vela_ligera': 'vela ligera',
      'cruiser_35': 'crucero menor de 35 pies',
      'cruiser_35_45': 'crucero de 35-45 pies',
      'catamaran': 'catamarán',
      'dinghy': 'dinghy',
      'windsurf': 'windsurf/wingfoil'
    };

    const skillNames: { [key: string]: string } = {
      'principiante': 'principiante',
      'intermedio': 'intermedio',
      'avanzado': 'avanzado'
    };

    const boatName = boatNames[boatType] || 'embarcación';
    const skillName = skillNames[skill] || 'navegante';
    const score = window.score;

    if (score >= 80) {
      if (skill === 'principiante') {
        return `Condiciones excelentes para tu ${boatName}. Como navegante ${skillName}, encontrarás condiciones muy favorables y seguras para disfrutar de una jornada en el agua.`;
      } else if (skill === 'intermedio') {
        return `Condiciones ideales para tu ${boatName}. Perfecto para aprovechar al máximo la navegación con tu nivel de experiencia.`;
      } else {
        return `Excelente ventana para tu ${boatName}. Condiciones óptimas que te permitirán sacar el máximo rendimiento.`;
      }
    } else if (score >= 60) {
      if (skill === 'principiante') {
        return `Buenas condiciones para tu ${boatName}. Como navegante ${skillName}, deberías sentirte cómodo navegando, aunque conviene estar atento a los cambios.`;
      } else if (skill === 'intermedio') {
        return `Condiciones apropiadas para tu ${boatName}. Tu experiencia te permitirá gestionar bien estas condiciones.`;
      } else {
        return `Buenas condiciones para tu ${boatName}. Sin complicaciones significativas para tu nivel de experiencia.`;
      }
    } else if (score >= 40) {
      if (skill === 'principiante') {
        return `Condiciones límite para tu ${boatName}. Como navegante ${skillName}, considera posponer la salida o navegar cerca de puerto con compañía experimentada.`;
      } else if (skill === 'intermedio') {
        return `Condiciones exigentes para tu ${boatName}. Requieren atención y estar preparado para gestionar situaciones complejas.`;
      } else {
        return `Condiciones desafiantes para tu ${boatName}. Tu experiencia será clave para evaluar si procede la salida.`;
      }
    } else {
      if (skill === 'principiante') {
        return `Condiciones no recomendables para tu ${boatName}. Como navegante ${skillName}, es muy aconsejable posponer la salida.`;
      } else if (skill === 'intermedio') {
        return `Condiciones adversas para tu ${boatName}. Se recomienda no navegar excepto en caso de necesidad.`;
      } else {
        return `Condiciones muy adversas para tu ${boatName}. Navegación no recomendable.`;
      }
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        <div className="p-6">
          <div className="flex justify-between items-start mb-6">
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-800 mb-2 capitalize">
                {formatDateTime(window.time)}
              </h2>
              <div className={`inline-block px-4 py-2 rounded-lg text-lg font-semibold border-2 ${getScoreColor(window.score)}`}>
                {window.label} - {window.score}/100
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-3xl font-bold leading-none"
            >
              ×
            </button>
          </div>

          {getContextualDescription() && (
            <div className="mb-6 bg-blue-50 border border-blue-200 rounded-xl p-4">
              <p className="text-sm text-gray-700 leading-relaxed">
                {getContextualDescription()}
              </p>
            </div>
          )}

          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-3">Condiciones</h3>
            <div className="space-y-2">
              {window.reasons.map((reason, idx) => (
                <div key={idx} className="flex items-start text-gray-700">
                  <span className="text-green-500 mr-2 font-bold">✓</span>
                  <span>{reason}</span>
                </div>
              ))}
            </div>
          </div>

          {window.flags.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-orange-600 mb-3">Advertencias</h3>
              <div className="space-y-2">
                {window.flags.map((flag, idx) => (
                  <div key={idx} className="flex items-start text-orange-700 bg-orange-50 p-2 rounded">
                    <span className="mr-2">⚠</span>
                    <span>{flag}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-3">Datos meteorológicos</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-500 mb-1">Viento</div>
                <div className="text-xl font-bold text-gray-800">{convertWindSpeed(window.raw.wind_kn)}</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-500 mb-1">Rachas</div>
                <div className="text-xl font-bold text-gray-800">{convertWindSpeed(window.raw.gust_kn)}</div>
              </div>
              {window.raw.wave_hs_m !== null && window.raw.wave_hs_m !== undefined && (
                <>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="text-sm text-gray-500 mb-1">Altura de ola (Hs)</div>
                    <div className="text-xl font-bold text-gray-800">{window.raw.wave_hs_m.toFixed(1)} m</div>
                  </div>
                  {window.raw.wave_tp_s && (
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="text-sm text-gray-500 mb-1">Periodo (Tp)</div>
                      <div className="text-xl font-bold text-gray-800">{window.raw.wave_tp_s.toFixed(1)} s</div>
                    </div>
                  )}
                </>
              )}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-500 mb-1">Precipitación</div>
                <div className="text-xl font-bold text-gray-800">{window.raw.precip_mm_h.toFixed(1)} mm/h</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-500 mb-1">Temperatura</div>
                <div className="text-xl font-bold text-gray-800">{window.raw.temp_c.toFixed(1)}°C</div>
              </div>
              {window.raw.wind_dir_deg !== null && window.raw.wind_dir_deg !== undefined && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-500 mb-1">Dirección viento</div>
                  <div className="text-xl font-bold text-gray-800">{window.raw.wind_dir_deg.toFixed(0)}°</div>
                </div>
              )}
              {window.raw.wave_dir_deg !== null && window.raw.wave_dir_deg !== undefined && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-500 mb-1">Dirección ola</div>
                  <div className="text-xl font-bold text-gray-800">{window.raw.wave_dir_deg.toFixed(0)}°</div>
                </div>
              )}
            </div>
          </div>

          <button
            onClick={onClose}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
}
