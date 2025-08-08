import React from 'react';

const EventCard = ({ event, userLocation }) => {

  // Helper to calculate countdown
  const getCountdown = (startDateTime) => {
    const now = new Date();
    const startDate = new Date(startDateTime);
    const diffMs = startDate - now;

    if (diffMs <= 0) {
      return 'Started';
    }

    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));

    if (diffHours > 0) {
      return `in ${diffHours} h ${diffMinutes} m`;
    }
    return `in ${diffMinutes} m`;
  };

  // Helper to calculate distance (Haversine formula)
  const haversine = (lat1, lon1, lat2, lon2) => {
      const R = 6371; // Radius of Earth in km
      const dLat = (lat2 - lat1) * Math.PI / 180;
      const dLon = (lon2 - lon1) * Math.PI / 180;
      const a =
          Math.sin(dLat / 2) * Math.sin(dLat / 2) +
          Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
          Math.sin(dLon / 2) * Math.sin(dLon / 2);
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
      return R * c;
  };

  const getDistance = () => {
    if (!userLocation || !event.lat || !event.lng) {
      return null;
    }
    const dist = haversine(userLocation.lat, userLocation.lng, parseFloat(event.lat), parseFloat(event.lng));
    return `${dist.toFixed(1)} km`;
  };

  const formatPrice = (price) => {
    if (price === null || price === undefined) {
      return 'Free';
    }
    const priceNum = parseFloat(price);
    if (priceNum === 0) {
        return 'Free';
    }
    return `$${priceNum.toFixed(2)}`;
  }

  return (
    <div className="bg-white shadow-lg rounded-lg overflow-hidden transform hover:scale-105 transition-transform duration-300 ease-in-out">
      <div className="p-6">
        <h3 className="font-bold text-xl mb-2 text-gray-800">{event.name}</h3>
        <p className="text-gray-600 text-sm mb-4">{event.venue_name}</p>

        <div className="flex justify-between items-center text-sm text-gray-700">
          <span className="font-semibold">{getCountdown(event.start_datetime)}</span>
          <span className="font-semibold">{getDistance()}</span>
        </div>

        <div className="mt-4 flex justify-between items-center">
          <p className="text-lg font-bold text-green-600">{formatPrice(event.price_min)}</p>
          <a
            href={event.url}
            target="_blank"
            rel="noopener noreferrer"
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-full transition-colors duration-300"
          >
            Get Tickets
          </a>
        </div>
      </div>
    </div>
  );
};

export default EventCard;
