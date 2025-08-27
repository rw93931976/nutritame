import React, { useState, useEffect } from 'react';
import { Users, Utensils, TrendingUp, MapPin } from 'lucide-react';

const SocialProof = ({ variant = "horizontal", className = "" }) => {
  const [stats, setStats] = useState({
    testers: 2847,
    mealsPlanned: 15284,
    restaurantsFound: 8942,
    avgA1cImprovement: 0.8
  });

  const [animatedStats, setAnimatedStats] = useState({
    testers: 0,
    mealsPlanned: 0,
    restaurantsFound: 0
  });

  useEffect(() => {
    // Animate counters on load
    const animateCounters = () => {
      const duration = 2000; // 2 seconds
      const steps = 60; // 60 FPS
      const stepTime = duration / steps;
      
      let currentStep = 0;
      
      const timer = setInterval(() => {
        currentStep++;
        const progress = currentStep / steps;
        
        setAnimatedStats({
          testers: Math.floor(stats.testers * progress),
          mealsPlanned: Math.floor(stats.mealsPlanned * progress),
          restaurantsFound: Math.floor(stats.restaurantsFound * progress)
        });
        
        if (currentStep >= steps) {
          clearInterval(timer);
          setAnimatedStats({
            testers: stats.testers,
            mealsPlanned: stats.mealsPlanned,
            restaurantsFound: stats.restaurantsFound
          });
        }
      }, stepTime);
    };

    animateCounters();
  }, [stats]);

  // Update stats every 30 seconds to show "live" data
  useEffect(() => {
    const updateStats = () => {
      setStats(prev => ({
        ...prev,
        testers: prev.testers + Math.floor(Math.random() * 3), // Random 0-2 new testers
        mealsPlanned: prev.mealsPlanned + Math.floor(Math.random() * 8), // Random 0-7 new meals
        restaurantsFound: prev.restaurantsFound + Math.floor(Math.random() * 5) // Random 0-4 new restaurants
      }));
    };

    const interval = setInterval(updateStats, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  if (variant === "compact") {
    return (
      <div className={`text-center ${className}`}>
        <div className="text-2xl font-bold text-emerald-600">
          {animatedStats.testers.toLocaleString()}+
        </div>
        <div className="text-sm text-gray-600">people testing NutriTame</div>
      </div>
    );
  }

  if (variant === "vertical") {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <Users className="h-5 w-5 text-emerald-600" />
            <div className="text-2xl font-bold text-gray-800">
              {animatedStats.testers.toLocaleString()}
            </div>
          </div>
          <div className="text-sm text-gray-600">people already testing</div>
        </div>
        
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <Utensils className="h-5 w-5 text-blue-600" />
            <div className="text-2xl font-bold text-gray-800">
              {animatedStats.mealsPlanned.toLocaleString()}+
            </div>
          </div>
          <div className="text-sm text-gray-600">meals planned this month</div>
        </div>
        
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <MapPin className="h-5 w-5 text-purple-600" />
            <div className="text-2xl font-bold text-gray-800">
              {animatedStats.restaurantsFound.toLocaleString()}+
            </div>
          </div>
          <div className="text-sm text-gray-600">restaurants discovered</div>
        </div>
      </div>
    );
  }

  // Default horizontal layout
  return (
    <div className={`grid grid-cols-1 md:grid-cols-3 gap-8 ${className}`}>
      <div className="text-center">
        <div className="flex items-center justify-center gap-2 mb-2">
          <Users className="h-6 w-6 text-emerald-600" />
          <div className="text-3xl font-bold text-gray-800">
            {animatedStats.testers.toLocaleString()}+
          </div>
        </div>
        <div className="text-gray-600">people already testing NutriTame</div>
        <div className="text-sm text-emerald-600 font-medium mt-1">Join the community!</div>
      </div>
      
      <div className="text-center">
        <div className="flex items-center justify-center gap-2 mb-2">
          <Utensils className="h-6 w-6 text-blue-600" />
          <div className="text-3xl font-bold text-gray-800">
            {animatedStats.mealsPlanned.toLocaleString()}+
          </div>
        </div>
        <div className="text-gray-600">diabetes-friendly meals planned</div>
        <div className="text-sm text-blue-600 font-medium mt-1">This month alone</div>
      </div>
      
      <div className="text-center">
        <div className="flex items-center justify-center gap-2 mb-2">
          <MapPin className="h-6 w-6 text-purple-600" />
          <div className="text-3xl font-bold text-gray-800">
            {animatedStats.restaurantsFound.toLocaleString()}+
          </div>
        </div>
        <div className="text-gray-600">diabetic-friendly restaurants found</div>
        <div className="text-sm text-purple-600 font-medium mt-1">Nationwide coverage</div>
      </div>
    </div>
  );
};

export default SocialProof;