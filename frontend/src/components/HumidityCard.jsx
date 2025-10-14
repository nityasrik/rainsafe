import { Cloud } from 'lucide-react';

export default function HumidityCard({ humidity, airQuality }) {
  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-3xl p-6 shadow-lg text-white relative overflow-hidden">
      <div className="absolute top-4 right-4 opacity-20">
        {[...Array(20)].map((_, i) => (
          <span key={i} className="inline-block text-white text-xs">✦ </span>
        ))}
      </div>

      <h3 className="text-lg font-semibold mb-4">Humidity</h3>

      <div className="flex items-center justify-between relative z-10">
        <div>
          <p className="text-xs text-gray-300 mb-1">Good Air Quality</p>
          <p className="text-4xl font-bold">{humidity}%</p>
        </div>

        <div className="relative w-32 h-32">
          <div className="absolute top-0 right-0">
            <div className="w-20 h-20 bg-gradient-to-br from-yellow-300 to-yellow-400 rounded-full shadow-xl"></div>
          </div>
          <div className="absolute bottom-0 left-0">
            <div className="w-24 h-16 bg-gradient-to-br from-blue-300 to-blue-400 rounded-3xl shadow-xl"></div>
          </div>
        </div>
      </div>
    </div>
  );
}
