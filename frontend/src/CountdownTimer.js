import React, { useState, useEffect } from 'react';
import { Clock, Calendar } from 'lucide-react';

const CountdownTimer = ({ targetDate = "2025-10-01", className = "" }) => {
  const [timeLeft, setTimeLeft] = useState({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0
  });

  useEffect(() => {
    const calculateTimeLeft = () => {
      const target = new Date(targetDate).getTime();
      const now = new Date().getTime();
      const difference = target - now;

      if (difference > 0) {
        const days = Math.floor(difference / (1000 * 60 * 60 * 24));
        const hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((difference % (1000 * 60)) / 1000);

        setTimeLeft({ days, hours, minutes, seconds });
      } else {
        setTimeLeft({ days: 0, hours: 0, minutes: 0, seconds: 0 });
      }
    };

    calculateTimeLeft();
    const timer = setInterval(calculateTimeLeft, 1000);

    return () => clearInterval(timer);
  }, [targetDate]);

  return (
    <div className={`flex flex-col items-center ${className}`}>
      <div className="flex items-center gap-2 mb-3">
        <Clock className="h-5 w-5 text-orange-600" />
        <span className="text-lg font-semibold text-gray-700">Demo ends in:</span>
      </div>
      
      <div className="flex items-center gap-3">
        <div className="text-center">
          <div className="bg-gradient-to-br from-orange-500 to-red-500 text-white rounded-lg p-3 min-w-[60px]">
            <div className="text-2xl font-bold">{timeLeft.days}</div>
          </div>
          <div className="text-sm text-gray-600 mt-1">Days</div>
        </div>
        
        <div className="text-2xl font-bold text-gray-400">:</div>
        
        <div className="text-center">
          <div className="bg-gradient-to-br from-orange-500 to-red-500 text-white rounded-lg p-3 min-w-[60px]">
            <div className="text-2xl font-bold">{timeLeft.hours}</div>
          </div>
          <div className="text-sm text-gray-600 mt-1">Hours</div>
        </div>
        
        <div className="text-2xl font-bold text-gray-400">:</div>
        
        <div className="text-center">
          <div className="bg-gradient-to-br from-orange-500 to-red-500 text-white rounded-lg p-3 min-w-[60px]">
            <div className="text-2xl font-bold">{timeLeft.minutes}</div>
          </div>
          <div className="text-sm text-gray-600 mt-1">Minutes</div>
        </div>
      </div>
      
      <div className="mt-3 text-center">
        <div className="flex items-center gap-1 text-sm text-gray-600">
          <Calendar className="h-4 w-4" />
          <span>Launch: October 1, 2025</span>
        </div>
      </div>
    </div>
  );
};

export default CountdownTimer;