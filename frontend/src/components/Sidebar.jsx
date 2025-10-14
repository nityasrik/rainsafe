import { Home, MapPin, Cloud, Bell, Calendar, Settings, User } from 'lucide-react';

export default function Sidebar() {
  return (
    <div className="w-20 bg-white/80 backdrop-blur-sm flex flex-col items-center py-6 space-y-6 rounded-l-3xl">
      <div className="w-12 h-12 bg-gradient-to-br from-orange-400 to-orange-500 rounded-xl flex items-center justify-center mb-4">
        <Cloud className="w-7 h-7 text-white" />
      </div>

      <nav className="flex flex-col space-y-4">
        <button className="w-12 h-12 rounded-xl bg-orange-400 text-white flex items-center justify-center hover:bg-orange-500 transition-colors">
          <Home className="w-6 h-6" />
        </button>
        <button className="w-12 h-12 rounded-xl text-gray-400 flex items-center justify-center hover:bg-gray-100 transition-colors">
          <MapPin className="w-6 h-6" />
        </button>
        <button className="w-12 h-12 rounded-xl text-gray-400 flex items-center justify-center hover:bg-gray-100 transition-colors">
          <Calendar className="w-6 h-6" />
        </button>
        <button className="w-12 h-12 rounded-xl text-gray-400 flex items-center justify-center hover:bg-gray-100 transition-colors">
          <Bell className="w-6 h-6" />
        </button>
        <button className="w-12 h-12 rounded-xl text-gray-400 flex items-center justify-center hover:bg-gray-100 transition-colors">
          <User className="w-6 h-6" />
        </button>
        <button className="w-12 h-12 rounded-xl text-gray-400 flex items-center justify-center hover:bg-gray-100 transition-colors">
          <Settings className="w-6 h-6" />
        </button>
      </nav>
    </div>
  );
}
