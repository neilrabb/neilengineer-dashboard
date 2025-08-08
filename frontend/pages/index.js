import Head from 'next/head';
import { useState, useEffect } from 'react';
import axios from 'axios';
import EventCard from '../components/EventCard';

export default function Home() {
  const [events, setEvents] = useState([]);
  const [location, setLocation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Get user's location
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
        },
        (err) => {
          setError('Please allow location access to find events near you.');
          setLoading(false);
        }
      );
    } else {
      setError('Geolocation is not supported by your browser.');
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (location) {
      setLoading(true);
      setError(null);

      // Fetch events from the backend API
      // In a real deployment, this URL should be an environment variable.
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      axios.get(`${API_URL}/events/`, {
        params: {
          lat: location.lat,
          lng: location.lng,
          radius_km: 50, // Default radius
        }
      })
      .then(response => {
        setEvents(response.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching events:', err);
        setError('Could not fetch events. Please try again later.');
        setLoading(false);
      });
    }
  }, [location]);

  return (
    <div>
      <Head>
        <title>Tonight In-Town</title>
        <meta name="description" content="Find events happening near you in the next 12 hours." />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="container mx-auto p-4">
        <header className="text-center my-8">
          <h1 className="text-5xl font-bold text-gray-800">Tonight In-Town</h1>
          <p className="text-lg text-gray-600 mt-2">Events starting in the next 12 hours near you</p>
        </header>

        {loading && (
          <div className="text-center">
            <p className="text-lg text-gray-600">Finding events near you...</p>
            {/* A simple spinner */}
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mt-4"></div>
          </div>
        )}

        {error && (
          <div className="text-center bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
            <strong className="font-bold">Error:</strong>
            <span className="block sm:inline"> {error}</span>
          </div>
        )}

        {!loading && !error && events.length === 0 && (
          <div className="text-center">
            <p className="text-xl text-gray-700">No events found nearby for tonight.</p>
            <p className="text-md text-gray-500">Try checking back later!</p>
          </div>
        )}

        {!loading && !error && events.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {events.map(event => (
              <EventCard key={event.id} event={event} userLocation={location} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
