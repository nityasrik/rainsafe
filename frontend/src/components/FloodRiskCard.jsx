export default function FloodRiskCard({ location, temperature, riskLevel }) {
  return (
    <div className="bg-gradient-to-br from-lime-300 to-lime-200 rounded-3xl p-6 shadow-lg relative overflow-hidden">
      <div className="mb-4">
        <p className="text-sm text-gray-700 mb-1">Dhaka, Bangladesh</p>
        <h3 className="text-3xl font-bold text-gray-800">{temperature}°C</h3>
        <p className="text-xs text-gray-600 mt-1">Mostly sunny</p>
      </div>

      <div className="relative flex items-end justify-center h-40 mt-6">
        <div className="absolute left-4 bottom-0">
          <div className="w-16 bg-orange-400 rounded-t-lg p-2 shadow-lg">
            <div className="w-full h-12 bg-orange-500 rounded"></div>
          </div>
        </div>

        <div className="relative z-10">
          <div className="relative">
            <div className="w-20 h-24 bg-orange-400 rounded-full"></div>
            <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-16 h-16 bg-orange-300 rounded-full"></div>

            <div className="absolute top-6 left-1/2 transform -translate-x-1/2 flex flex-col items-center">
              <div className="w-1 h-2 bg-gray-800 mb-1"></div>
              <div className="w-6 h-6 bg-orange-200 rounded-full border-2 border-gray-800"></div>
              <div className="w-8 h-10 bg-white rounded-lg mt-1 border-2 border-gray-800"></div>
              <div className="flex space-x-1 mt-1">
                <div className="w-3 h-6 bg-blue-400 rounded border border-gray-800"></div>
                <div className="w-3 h-6 bg-blue-400 rounded border border-gray-800"></div>
              </div>
            </div>

            <div className="absolute -right-2 top-8 w-6 h-8 bg-orange-300 rounded-lg"></div>
            <div className="absolute -left-2 top-8 w-6 h-8 bg-orange-300 rounded-lg"></div>
          </div>
        </div>

        <div className="absolute right-4 bottom-0">
          <div className="w-12 h-16 bg-gray-600 rounded-t shadow-lg"></div>
          <div className="w-12 h-2 bg-gray-700"></div>
        </div>

        <div className="absolute inset-x-0 bottom-0 h-8 bg-gradient-to-t from-gray-300 to-transparent rounded-b-3xl"></div>
      </div>
    </div>
  );
}
