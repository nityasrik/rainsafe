import { MapPin, Wind, Droplets } from 'lucide-react';

export default function WeatherCard({ location, temperature, condition, visibility, humidity }) {
  return (
    <div className="bg-gradient-to-br from-blue-100 via-white to-blue-50 rounded-3xl p-6 shadow-lg">
      <div className="flex items-center space-x-2 mb-4">
        <MapPin className="w-4 h-4 text-gray-600" />
        <span className="text-sm text-gray-700">{location}</span>
      </div>

      <div className="mb-2">
        <h2 className="text-gray-700 text-lg font-medium mb-1">Weather</h2>
        <p className="text-gray-500 text-xs">Now</p>
      </div>

      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="text-7xl font-bold text-gray-800">{temperature}°C</div>
          <p className="text-gray-500 text-sm mt-2">Feels like {temperature - 1}°C</p>
        </div>

        <div className="relative">
          <div className="w-32 h-32 relative">
            <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-yellow-300 to-yellow-400 rounded-full shadow-lg"></div>
            <div className="absolute bottom-0 left-0 w-24 h-16 bg-gradient-to-br from-blue-300 to-blue-400 rounded-3xl shadow-lg flex items-center justify-center">
              <div className="flex space-x-1">
                <div className="w-2 h-4 bg-blue-500 rounded-full transform rotate-12"></div>
                <div className="w-2 h-4 bg-blue-500 rounded-full transform -rotate-12"></div>
                <div className="w-2 h-4 bg-blue-500 rounded-full transform rotate-12"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="bg-lime-200 rounded-2xl p-3">
          <div className="flex items-center space-x-2 mb-1">
            <Wind className="w-4 h-4 text-gray-700" />
            <span className="text-xs text-gray-600">Visibility</span>
          </div>
          <p className="text-xl font-bold text-gray-800">{visibility} km</p>
        </div>

        <div className="bg-white rounded-2xl p-3">
          <div className="flex items-center space-x-2 mb-1">
            <Droplets className="w-4 h-4 text-gray-700" />
            <span className="text-xs text-gray-600">Humidity</span>
          </div>
          <p className="text-xl font-bold text-gray-800">{humidity}%</p>
        </div>
      </div>
    </div>
  );
}
