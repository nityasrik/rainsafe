import { Search, Calendar, MessageSquare, Bell } from 'lucide-react';

export default function Header() {
  return (
    <div className="flex items-center justify-between mb-6">
      <div className="flex items-center space-x-4">
        <div className="w-12 h-12 bg-gradient-to-br from-orange-400 to-orange-500 rounded-full"></div>
        <div>
          <p className="text-sm text-gray-500">Hello,</p>
          <p className="text-lg font-semibold text-gray-800">Sajibur Rahman</p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <div className="relative">
          <input
            type="text"
            placeholder="Search Here..."
            className="w-80 px-4 py-2 pl-10 bg-gray-50 border border-gray-200 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
          />
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
        </div>

        <button className="w-10 h-10 bg-gray-50 rounded-full flex items-center justify-center hover:bg-gray-100 transition-colors">
          <Calendar className="w-5 h-5 text-gray-600" />
        </button>

        <button className="w-10 h-10 bg-gray-50 rounded-full flex items-center justify-center hover:bg-gray-100 transition-colors">
          <MessageSquare className="w-5 h-5 text-gray-600" />
        </button>

        <button className="w-10 h-10 bg-gray-50 rounded-full flex items-center justify-center hover:bg-gray-100 transition-colors">
          <Bell className="w-5 h-5 text-gray-600" />
        </button>
      </div>
    </div>
  );
}
