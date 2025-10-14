import { Cloud } from 'lucide-react';

export default function CityWeatherCard({ city, condition, currentTemp, highTemp }) {
  return (
    <div className="flex items-center justify-between p-4 hover:bg-gray-50 rounded-2xl transition-colors">
      <div className="flex items-center space-x-3">
        <div className="relative">
          <Cloud className="w-8 h-8 text-blue-300" />
          <div className="absolute -right-1 -bottom-1 w-3 h-3 bg-yellow-400 rounded-full"></div>
        </div>
        <div>
          <p className="font-semibold text-gray-800">{city}</p>
          <p className="text-xs text-gray-500">{condition}</p>
        </div>
      </div>

      <div className="text-right">
        <p className="text-2xl font-bold text-gray-800">{currentTemp}°C</p>
        <p className="text-xs text-orange-500">{highTemp}°C</p>
      </div>
    </div>
  );
}
