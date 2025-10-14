export default function HourlyForecast() {
  const hours = [
    { time: 'Morning', temp: 20, icon: '🌤️' },
    { time: 'Afternoon', temp: 24, icon: '☀️' },
    { time: 'Evening', temp: 28, icon: '🌤️' },
    { time: 'Night', temp: 22, icon: '🌙' },
  ];

  return (
    <div className="bg-white rounded-3xl p-6 shadow-lg">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">How is the temperature today?</h3>

      <div className="flex justify-around items-end space-x-4">
        {hours.map((hour, index) => (
          <div key={index} className="flex flex-col items-center space-y-2">
            <span className="text-3xl">{hour.icon}</span>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-800">{hour.temp}°</p>
              <p className="text-xs text-gray-500 mt-1">{hour.time}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
