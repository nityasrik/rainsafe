import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import WeatherCard from './components/WeatherCard';
import MapView from './components/MapView';
import CityWeatherCard from './components/CityWeatherCard';
import HourlyForecast from './components/HourlyForecast';
import HumidityCard from './components/HumidityCard';
import FloodRiskCard from './components/FloodRiskCard';

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-orange-50 to-pink-50 flex">
      <Sidebar />

      <div className="flex-1 p-8">
        <Header />

        <div className="grid grid-cols-12 gap-6">
          <div className="col-span-4">
            <WeatherCard
              location="Dhaka, Bangladesh"
              temperature={25}
              condition="Partly Cloudy"
              visibility={4.3}
              humidity={87}
            />
          </div>

          <div className="col-span-8 h-96">
            <MapView />
          </div>

          <div className="col-span-4 space-y-4">
            <div className="bg-white rounded-3xl shadow-lg p-4 space-y-2">
              <CityWeatherCard
                city="New York"
                condition="Sunny"
                currentTemp={22}
                highTemp={28}
              />
              <CityWeatherCard
                city="London"
                condition="Bright"
                currentTemp={24}
                highTemp={28}
              />
            </div>

            <HumidityCard humidity={69} airQuality="Good" />
          </div>

          <div className="col-span-4">
            <HourlyForecast />
          </div>

          <div className="col-span-4">
            <FloodRiskCard
              location="Dhaka, Bangladesh"
              temperature={25}
              riskLevel="moderate"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
