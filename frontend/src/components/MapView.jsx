import { useState } from 'react';
import Map, { Marker, NavigationControl } from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { MapPin } from 'lucide-react';

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN;

const cities = [
  { name: 'Dhaka', lat: 23.8103, lng: 90.4125, temp: 25 },
  { name: 'New York', lat: 40.7128, lng: -74.0060, temp: 22 },
  { name: 'London', lat: 51.5074, lng: -0.1278, temp: 21 },
  { name: 'Tokyo', lat: 35.6762, lng: 139.6503, temp: 27 },
];

export default function MapView() {
  const [viewState, setViewState] = useState({
    longitude: 20,
    latitude: 30,
    zoom: 1.5
  });

  return (
    <div className="bg-white rounded-3xl shadow-lg overflow-hidden h-full relative">
      <div className="absolute top-4 right-4 z-10 bg-white/90 backdrop-blur-sm rounded-full px-4 py-2 shadow-lg">
        <span className="text-2xl font-bold text-gray-800">22°C</span>
      </div>

      <div className="absolute top-4 right-20 z-10 bg-lime-400 rounded-full p-2 shadow-lg">
        <MapPin className="w-5 h-5 text-gray-800" />
      </div>

      <Map
        {...viewState}
        onMove={evt => setViewState(evt.viewState)}
        mapStyle="mapbox://styles/mapbox/light-v11"
        mapboxAccessToken={MAPBOX_TOKEN}
        style={{ width: '100%', height: '100%' }}
      >
        <NavigationControl position="bottom-right" />

        {cities.map((city, index) => (
          <Marker
            key={index}
            longitude={city.lng}
            latitude={city.lat}
            anchor="bottom"
          >
            <div className="relative group cursor-pointer">
              <div className="w-8 h-8 bg-orange-400 rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform">
                <MapPin className="w-5 h-5 text-white" />
              </div>
              <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 bg-white px-3 py-1 rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                <p className="text-sm font-semibold">{city.name}</p>
                <p className="text-xs text-gray-600">{city.temp}°C</p>
              </div>
            </div>
          </Marker>
        ))}
      </Map>

      <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm rounded-2xl p-3 shadow-lg">
        <p className="text-sm font-semibold text-gray-700">Monday</p>
        <p className="text-2xl font-bold text-gray-800">25°C</p>
        <p className="text-xs text-gray-500">Mostly Sunny</p>
      </div>
    </div>
  );
}
