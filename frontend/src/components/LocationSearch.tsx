import { useState } from 'react';
import { GeocodeResult } from '../lib/api';

interface LocationSearchProps {
  onSelect: (result: GeocodeResult) => void;
  onSearch: (query: string) => Promise<GeocodeResult[]>;
}

export default function LocationSearch({ onSelect, onSearch }: LocationSearchProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<GeocodeResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);

  const handleSearch = async (value: string) => {
    setQuery(value);
    if (value.length < 2) {
      setResults([]);
      setShowResults(false);
      return;
    }
    
    setLoading(true);
    try {
      const data = await onSearch(value);
      setResults(data);
      setShowResults(true);
    } catch (error) {
      console.error('Error al buscar:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (result: GeocodeResult) => {
    setQuery(result.name);
    setShowResults(false);
    onSelect(result);
  };

  return (
    <div className="relative w-full">
      <input
        type="text"
        value={query}
        onChange={(e) => handleSearch(e.target.value)}
        onFocus={() => results.length > 0 && setShowResults(true)}
        placeholder="Buscar ubicación (ej: Barcelona, Palma de Mallorca)"
        className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
      />
      {loading && (
        <div className="absolute right-3 top-4">
          <div className="animate-spin h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full"></div>
        </div>
      )}
      {showResults && results.length > 0 && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-auto">
          {results.map((result, index) => (
            <button
              key={index}
              onClick={() => handleSelect(result)}
              className="w-full px-4 py-3 text-left hover:bg-blue-50 border-b last:border-b-0"
            >
              <div className="font-medium">{result.name}</div>
              <div className="text-sm text-gray-600">
                {result.admin1 && `${result.admin1}, `}
                {result.country}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
