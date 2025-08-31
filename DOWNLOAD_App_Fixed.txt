import { useState, useEffect, useRef } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import "./App.css";

// Import shadcn components
import { Button } from "./components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Textarea } from "./components/ui/textarea";
import { Badge } from "./components/ui/badge";
import { Separator } from "./components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { toast } from "sonner";
import { Heart, MessageCircle, User, ChefHat, Target, Calendar, Clock, CheckCircle, MapPin, Search, Star, Phone, Globe, Navigation, ShoppingCart, List, Plus, Check, Smartphone, ChevronUp, ChevronDown, RotateCcw, Save, FolderOpen, MessageSquarePlus, Trash2, BookOpen, LogOut, Crown } from "lucide-react";

// Import SaaS components
import LandingPage from './LandingPage';
import DemoLandingPage from './DemoLandingPage';
import DemoModeBanner from './DemoModeBanner';
import PaymentSuccess from './PaymentSuccess';
import AdminDashboard from './AdminDashboard';
import AdminLogin from './AdminLogin';
import SaaSHeader from './SaaSHeader';
import MedicalDisclaimer from './MedicalDisclaimer';
import DemoCountdownTimer from './components/DemoCountdownTimer';

import { BACKEND_URL, API } from './config';

// Map Component for displaying restaurant locations
const RestaurantMap = ({ center, restaurants, selectedRestaurant, onRestaurantSelect }) => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersRef = useRef([]);
  const [isGoogleMapsLoaded, setIsGoogleMapsLoaded] = useState(false);

  useEffect(() => {
    // Check if Google Maps is already loaded
    if (window.google && window.google.maps) {
      setIsGoogleMapsLoaded(true);
      return;
    }

    // Listen for Google Maps loaded event
    const handleGoogleMapsLoaded = () => {
      setIsGoogleMapsLoaded(true);
    };

    window.addEventListener('google-maps-loaded', handleGoogleMapsLoaded);

    // Cleanup
    return () => {
      window.removeEventListener('google-maps-loaded', handleGoogleMapsLoaded);
    };
  }, []);

  useEffect(() => {
    if (!mapRef.current || !isGoogleMapsLoaded || !window.google || !window.google.maps) {
      console.log('Map not ready:', { 
        mapRef: !!mapRef.current, 
        isGoogleMapsLoaded, 
        hasGoogle: !!window.google,
        hasMaps: !!(window.google && window.google.maps)
      });
      return;
    }

    console.log('Initializing Google Map with:', { center, restaurantCount: restaurants.length });

    try {
      // Initialize map
      const map = new window.google.maps.Map(mapRef.current, {
        center: center ? { lat: center.latitude, lng: center.longitude } : { lat: 32.7767, lng: -96.7970 }, // Default to Dallas
        zoom: 13,
        styles: [
          {
            featureType: "poi",
            elementType: "labels",
            stylers: [{ visibility: "off" }]
          }
        ]
      });

      mapInstanceRef.current = map;
      console.log('Map initialized successfully');

      // Clear existing markers
      markersRef.current.forEach(marker => marker.setMap(null));
      markersRef.current = [];

      // Add markers for restaurants
      restaurants.forEach((restaurant, index) => {
        const marker = new window.google.maps.Marker({
          position: { lat: restaurant.latitude, lng: restaurant.longitude },
          map: map,
          title: restaurant.name,
          icon: {
            url: selectedRestaurant?.place_id === restaurant.place_id 
              ? 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                <svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="16" cy="16" r="12" fill="#059669" stroke="#ffffff" stroke-width="3"/>
                  <circle cx="16" cy="16" r="6" fill="#ffffff"/>
                </svg>
              `)
              : 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="8" fill="#3b82f6" stroke="#ffffff" stroke-width="2"/>
                  <circle cx="12" cy="12" r="4" fill="#ffffff"/>
                </svg>
              `),
            scaledSize: new window.google.maps.Size(
              selectedRestaurant?.place_id === restaurant.place_id ? 32 : 24, 
              selectedRestaurant?.place_id === restaurant.place_id ? 32 : 24
            )
          }
        });

        // Add click listener
        marker.addListener('click', () => {
          onRestaurantSelect(restaurant);
        });

        markersRef.current.push(marker);
      });

      console.log(`Added ${restaurants.length} restaurant markers`);

      // Center search location marker
      if (center) {
        const centerMarker = new window.google.maps.Marker({
          position: { lat: center.latitude, lng: center.longitude },
          map: map,
          title: 'Search Center',
          icon: {
            url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
              <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="8" fill="#dc2626" stroke="#ffffff" stroke-width="2"/>
                <circle cx="12" cy="12" r="3" fill="#ffffff"/>
              </svg>
            `),
            scaledSize: new window.google.maps.Size(24, 24)
          }
        });
        markersRef.current.push(centerMarker);
        console.log('Added search center marker');
      }
    } catch (error) {
      console.error('Error initializing Google Map:', error);
    }

  }, [center, restaurants, selectedRestaurant, isGoogleMapsLoaded]);

  if (!isGoogleMapsLoaded) {
    return (
      <div 
        className="w-full h-64 md:h-80 rounded-lg border border-gray-200 shadow-sm bg-gray-100 flex items-center justify-center"
        style={{ minHeight: '300px' }}
      >
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600 mx-auto mb-2"></div>
          <p className="text-gray-600">Loading map...</p>
        </div>
      </div>
    );
  }

  return (
    <div 
      ref={mapRef} 
      className="w-full h-64 md:h-80 rounded-lg border border-gray-200 shadow-sm"
      style={{ minHeight: '300px' }}
    />
  );
};

// User Profile Setup Component
const UserProfileSetup = ({ onProfileComplete, existingProfile }) => {
  console.log('UserProfileSetup initialized with existingProfile:', existingProfile);
  
  const [profile, setProfile] = useState({
    diabetes_type: existingProfile?.diabetes_type || "",
    age: existingProfile?.age || "",
    gender: existingProfile?.gender || "",
    activity_level: existingProfile?.activity_level || "",
    health_goals: existingProfile?.health_goals || [],
    food_preferences: existingProfile?.food_preferences || [],
    cultural_background: existingProfile?.cultural_background || "",
    allergies: existingProfile?.allergies || [],
    dislikes: existingProfile?.dislikes || [],
    cooking_skill: existingProfile?.cooking_skill || "",
    phone_number: existingProfile?.phone_number || ""
  });

  console.log('Initial profile state:', profile);

  const [loading, setLoading] = useState(false);

  const healthGoals = [
    "weight_loss", "energy_boost", "blood_sugar_control", 
    "heart_health", "digestive_health", "muscle_building"
  ];

  const foodPreferences = [
    "vegetarian", "vegan", "mediterranean", "low_carb", 
    "gluten_free", "dairy_free", "keto", "paleo", "whole_foods"
  ];

  const handleArrayField = (field, value) => {
    setProfile(prev => ({
      ...prev,
      [field]: prev[field].includes(value)
        ? prev[field].filter(item => item !== value)
        : [...prev[field], value]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      console.log('Profile submission started:', { profile, existingProfile });
      
      const profileData = {
        ...profile,
        age: profile.age ? parseInt(profile.age) : null
      };

      console.log('Sending profile data:', profileData);

      let response;
      // Check if this is a real profile update (has diabetes_type) or should be treated as new profile creation
      const isRealProfileUpdate = existingProfile?.id && existingProfile?.diabetes_type;
      
      if (isRealProfileUpdate) {
        console.log(`Updating existing profile with ID: ${existingProfile.id}`);
        response = await axios.put(`${API}/users/${existingProfile.id}`, profileData);
      } else {
        console.log('Creating new profile');
        response = await axios.post(`${API}/users`, profileData);
      }

      console.log('Profile save response:', response.data);
      const isUpdate = existingProfile?.id && existingProfile?.diabetes_type;
      toast.success(isUpdate ? "Profile updated successfully!" : "Profile created successfully!");
      onProfileComplete(response.data);
    } catch (error) {
      console.error("Profile save error details:", {
        error,
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        config: error.config
      });
      
      // More specific error messages
      if (error.response?.status === 404) {
        toast.error("Profile not found. Please try creating a new profile.");
      } else if (error.response?.status === 400) {
        toast.error(`Invalid profile data: ${error.response?.data?.detail || 'Please check your input'}`);
      } else if (error.response?.status >= 500) {
        toast.error("Server error. Please try again later.");
      } else if (error.code === 'NETWORK_ERROR') {
        toast.error("Network error. Please check your internet connection.");
      } else {
        toast.error(`Failed to save profile: ${error.response?.data?.detail || error.message || 'Unknown error'}`);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-cyan-50 to-blue-50 p-4">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="p-4 bg-gradient-to-br from-emerald-100 to-blue-100 rounded-full shadow-lg">
              <Heart className="h-8 w-8 text-emerald-600" />
            </div>
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-emerald-600 via-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
            Welcome to NutriTame
          </h1>
          <p className="text-gray-700 text-lg">
            Your personalized AI health coach for diabetes-friendly meal planning with restaurant search
          </p>
        </div>

        <Card className="shadow-xl border-0 bg-white/90 backdrop-blur-sm">
          <CardHeader className="bg-gradient-to-r from-emerald-50 to-blue-50 rounded-t-lg">
            <CardTitle className="flex items-center gap-2 text-gray-800">
              <User className="h-5 w-5 text-emerald-600" />
              {(existingProfile?.id && existingProfile?.diabetes_type) ? "Update Your Profile" : "Create Your Profile"}
            </CardTitle>
            <CardDescription className="text-gray-600">
              Help us understand your needs so we can provide the best meal recommendations and restaurant suggestions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Diabetes Type */}
              <div className="space-y-2">
                <Label htmlFor="diabetes_type">Diabetes Type *</Label>
                <select 
                  name="diabetes_type"
                  value={profile.diabetes_type} 
                  onChange={(e) => {
                    console.log('Diabetes type selected:', e.target.value);
                    setProfile({...profile, diabetes_type: e.target.value});
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                >
                  <option value="">Select your diabetes type</option>
                  <option value="type1">Type 1 Diabetes</option>
                  <option value="type2">Type 2 Diabetes</option>
                  <option value="prediabetes">Prediabetes</option>
                </select>
              </div>

              {/* Basic Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="age">Age</Label>
                  <Input
                    id="age"
                    type="number"
                    value={profile.age}
                    onChange={(e) => setProfile({...profile, age: e.target.value})}
                    placeholder="Your age"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="gender">Gender</Label>
                  <Select value={profile.gender} onValueChange={(value) => setProfile({...profile, gender: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select gender" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="male">Male</SelectItem>
                      <SelectItem value="female">Female</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                      <SelectItem value="prefer_not_to_say">Prefer not to say</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Activity Level */}
              <div className="space-y-2">
                <Label htmlFor="activity_level">Activity Level</Label>
                <Select value={profile.activity_level} onValueChange={(value) => setProfile({...profile, activity_level: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select your activity level" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low (Sedentary)</SelectItem>
                    <SelectItem value="moderate">Moderate (2-3 times/week)</SelectItem>
                    <SelectItem value="high">High (4+ times/week)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Health Goals */}
              <div className="space-y-3">
                <Label className="text-gray-700 font-medium">Health Goals</Label>
                <div className="flex flex-wrap gap-2">
                  {healthGoals.map(goal => (
                    <Badge
                      key={goal}
                      variant={profile.health_goals.includes(goal) ? "default" : "outline"}
                      className={`cursor-pointer px-4 py-2 capitalize transition-all duration-300 ${
                        profile.health_goals.includes(goal)
                          ? 'bg-gradient-to-r from-emerald-500 to-blue-500 text-white shadow-lg hover:from-emerald-600 hover:to-blue-600 transform hover:scale-105'
                          : 'border-2 border-emerald-200 text-emerald-700 hover:border-emerald-400 hover:bg-emerald-50 hover:scale-105'
                      }`}
                      onClick={() => handleArrayField('health_goals', goal)}
                    >
                      {goal.replace('_', ' ')}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Food Preferences */}
              <div className="space-y-3">
                <Label className="text-gray-700 font-medium">Food Preferences</Label>
                <div className="flex flex-wrap gap-2">
                  {foodPreferences.map(pref => (
                    <Badge
                      key={pref}
                      variant={profile.food_preferences.includes(pref) ? "default" : "outline"}
                      className={`cursor-pointer px-4 py-2 capitalize transition-all duration-300 ${
                        profile.food_preferences.includes(pref)
                          ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg hover:from-purple-600 hover:to-pink-600 transform hover:scale-105'
                          : 'border-2 border-purple-200 text-purple-700 hover:border-purple-400 hover:bg-purple-50 hover:scale-105'
                      }`}
                      onClick={() => handleArrayField('food_preferences', pref)}
                    >
                      {pref.replace('_', ' ')}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Cultural Background */}
              <div className="space-y-2">
                <Label htmlFor="cultural_background">Cultural Background (Optional)</Label>
                <Input
                  id="cultural_background"
                  value={profile.cultural_background}
                  onChange={(e) => setProfile({...profile, cultural_background: e.target.value})}
                  placeholder="e.g., Mediterranean, Asian, Latin American"
                />
              </div>

              {/* Allergies */}
              <div className="space-y-2">
                <Label htmlFor="allergies">Food Allergies</Label>
                <Textarea
                  id="allergies"
                  value={profile.allergies.join(', ')}
                  onChange={(e) => setProfile({...profile, allergies: e.target.value.split(',').map(item => item.trim()).filter(Boolean)})}
                  placeholder="List any food allergies (separated by commas)"
                  rows={2}
                />
              </div>

              {/* Dislikes */}
              <div className="space-y-2">
                <Label htmlFor="dislikes">Food Dislikes</Label>
                <Textarea
                  id="dislikes"
                  value={profile.dislikes.join(', ')}
                  onChange={(e) => setProfile({...profile, dislikes: e.target.value.split(',').map(item => item.trim()).filter(Boolean)})}
                  placeholder="List foods you dislike (separated by commas)"
                  rows={2}
                />
              </div>

              {/* Cooking Skill */}
              <div className="space-y-2">
                <Label htmlFor="cooking_skill">Cooking Skill Level</Label>
                <Select value={profile.cooking_skill} onValueChange={(value) => setProfile({...profile, cooking_skill: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select your cooking skill level" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="beginner">Beginner (Simple meals)</SelectItem>
                    <SelectItem value="intermediate">Intermediate (Some experience)</SelectItem>
                    <SelectItem value="advanced">Advanced (Confident cook)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Phone Number */}
              <div className="space-y-2">
                <Label htmlFor="phone_number">Phone Number (Optional)</Label>
                <Input
                  id="phone_number"
                  type="tel"
                  value={profile.phone_number}
                  onChange={(e) => setProfile({...profile, phone_number: e.target.value})}
                  placeholder="+1 (555) 123-4567"
                />
                <p className="text-xs text-gray-500">
                  📱 Add your phone number to receive restaurant details via text message
                </p>
              </div>

              <Button 
                type="submit" 
                className="w-full bg-gradient-to-r from-emerald-600 via-blue-600 to-emerald-600 hover:from-emerald-700 hover:via-blue-700 hover:to-emerald-700 text-white font-semibold py-3 px-6 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105" 
                disabled={loading || !profile.diabetes_type}
                onClick={() => console.log('Button clicked, profile state:', profile)}
              >
                {loading ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    Saving...
                  </div>
                ) : (
                  // Check if this is a real profile update or should be treated as creation
                  (existingProfile?.id && existingProfile?.diabetes_type) ? "Update Profile" : "Create Profile"
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// API Usage Monitor Component
const APIUsageMonitor = ({ userProfile }) => {
  const [usage, setUsage] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUsageStats();
    // Refresh usage stats every 30 seconds
    const interval = setInterval(loadUsageStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadUsageStats = async () => {
    try {
      const response = await axios.get(`${API}/usage/google-places`);
      setUsage(response.data);
    } catch (error) {
      console.error("Failed to load usage stats:", error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'limit_exceeded': return 'bg-red-100 text-red-700 border-red-200';
      case 'approaching_limit': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'moderate_usage': return 'bg-blue-100 text-blue-700 border-blue-200';
      default: return 'bg-green-100 text-green-700 border-green-200';
    }
  };

  const getStatusText = (status) => {
    switch(status) {
      case 'limit_exceeded': return '🚫 Limit Exceeded';
      case 'approaching_limit': return '⚠️ Approaching Limit';
      case 'moderate_usage': return '📊 Moderate Usage';
      default: return '✅ Under Limit';
    }
  };

  if (loading) return null;
  if (!usage) return null;

  return (
    <div className="mb-4">
      <Card className={`border-2 ${getStatusColor(usage.status)}`}>
        <CardContent className="p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Google Places API Usage</span>
              <Badge className={getStatusColor(usage.status)}>
                {getStatusText(usage.status)}
              </Badge>
            </div>
            <div className="text-sm font-mono">
              {usage.calls_made} / {usage.monthly_limit} calls
            </div>
          </div>
          <div className="mt-2">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full ${
                  usage.percentage_used >= 100 ? 'bg-red-500' :
                  usage.percentage_used >= 90 ? 'bg-yellow-500' :
                  usage.percentage_used >= 70 ? 'bg-blue-500' : 'bg-green-500'
                }`}
                style={{ width: `${Math.min(usage.percentage_used, 100)}%` }}
              ></div>
            </div>
            <div className="flex justify-between text-xs text-gray-600 mt-1">
              <span>{usage.percentage_used}% used</span>
              <span>{usage.calls_remaining} calls remaining</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Restaurant Search Component
const RestaurantSearch = ({ userProfile, onRestaurantSelect }) => {
  const [searchLocation, setSearchLocation] = useState("");
  const [searchRadius, setSearchRadius] = useState(2000);
  const [searchKeyword, setSearchKeyword] = useState("");
  const [restaurants, setRestaurants] = useState([]);
  const [loading, setLoading] = useState(false);
  const [userLocation, setUserLocation] = useState(null);
  const [selectedRestaurant, setSelectedRestaurant] = useState(null);
  const [searchCenter, setSearchCenter] = useState(null);

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      setLoading(true);
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const location = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          };
          setUserLocation(location);
          setSearchCenter(location);
          searchRestaurants(location.latitude, location.longitude);
        },
        (error) => {
          toast.error("Unable to get your location. Please enter a location manually.");
          setLoading(false);
        }
      );
    } else {
      toast.error("Geolocation is not supported by your browser.");
    }
  };

  const searchRestaurants = async (lat, lng, keyword = searchKeyword) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/restaurants/search`, {
        latitude: lat,
        longitude: lng,
        radius: searchRadius,
        keyword: keyword
      });
      setRestaurants(response.data);
      toast.success(`Found ${response.data.length} restaurants`);
    } catch (error) {
      console.error("Restaurant search error:", error);
      if (error.response?.data?.detail?.includes("Monthly API limit reached")) {
        toast.error("🚫 Restaurant search temporarily unavailable - monthly limit reached");
        setRestaurants([]);
      } else {
        toast.error("Failed to search restaurants. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleManualSearch = async () => {
    if (!searchLocation.trim()) {
      toast.error("Please enter a location");
      return;
    }
    
    setLoading(true);
    try {
      // Use the new location-based search API
      const response = await axios.post(`${API}/restaurants/search-by-location`, {
        location: searchLocation,
        radius: searchRadius,
        keyword: searchKeyword
      });
      
      // Also get the geocoded coordinates for the map
      const locationResponse = await axios.post(`${API}/geocode`, {
        location: searchLocation
      });
      
      setSearchCenter({
        latitude: locationResponse.data.latitude,
        longitude: locationResponse.data.longitude
      });
      
      setRestaurants(response.data);
      toast.success(`Found ${response.data.length} restaurants in ${searchLocation}`);
    } catch (error) {
      console.error("Location search error:", error);
      if (error.response?.data?.detail?.includes("Monthly API limit reached")) {
        toast.error("🚫 Restaurant search temporarily unavailable - monthly limit reached");
      } else if (error.response?.data?.detail?.includes("Could not find location")) {
        toast.error(`Could not find location: ${searchLocation}. Please try a different search term.`);
      } else {
        toast.error("Failed to search restaurants. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRestaurantClick = (restaurant) => {
    setSelectedRestaurant(restaurant);
  };

  const handleGetAIAnalysis = async (restaurant) => {
    // Call the parent's onRestaurantSelect which will switch to chat and get AI analysis
    onRestaurantSelect(restaurant);
  };

  const handleBackToSearch = () => {
    setSelectedRestaurant(null);
  };

  // If a restaurant is selected, show details
  if (selectedRestaurant) {
    return (
      <RestaurantDetails 
        restaurant={selectedRestaurant}
        onGetAIAnalysis={handleGetAIAnalysis}
        onBack={handleBackToSearch}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* API Usage Monitor */}
      <APIUsageMonitor userProfile={userProfile} />
      
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5 text-emerald-600" />
            Find Diabetic-Friendly Restaurants
          </CardTitle>
          <CardDescription>
            Search for restaurants near you with healthy options for diabetes management
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Button 
              onClick={getCurrentLocation}
              disabled={loading}
              className="bg-emerald-600 hover:bg-emerald-700"
            >
              <Navigation className="h-4 w-4 mr-2" />
              Use My Location
            </Button>
            <div className="flex-1 flex gap-2">
              <Input
                placeholder="Enter city or address (e.g., Dallas, Texas)"
                value={searchLocation}
                onChange={(e) => setSearchLocation(e.target.value)}
                className="flex-1"
                onKeyPress={(e) => e.key === 'Enter' && handleManualSearch()}
              />
              <Button onClick={handleManualSearch} disabled={loading}>
                Search
              </Button>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>Search Radius</Label>
              <Select value={searchRadius.toString()} onValueChange={(value) => setSearchRadius(parseInt(value))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1609">1 mile</SelectItem>
                  <SelectItem value="3218">2 miles</SelectItem>
                  <SelectItem value="8047">5 miles</SelectItem>
                  <SelectItem value="16093">10 miles</SelectItem>
                  <SelectItem value="32186">20 miles</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Cuisine Type (Optional)</Label>
              <Input
                placeholder="e.g., Mediterranean, Healthy, Salad"
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {loading && (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
          <p className="mt-2 text-gray-600">Searching for restaurants...</p>
        </div>
      )}

      {/* Map Display */}
      {searchCenter && restaurants.length > 0 && (
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="h-5 w-5 text-emerald-600" />
              Restaurant Locations
            </CardTitle>
            <CardDescription>
              📍 {restaurants.length} restaurants within {(searchRadius/1609).toFixed(1)} miles • Click markers to view details
            </CardDescription>
          </CardHeader>
          <CardContent>
            <RestaurantMap 
              center={searchCenter}
              restaurants={restaurants}
              selectedRestaurant={null}
              onRestaurantSelect={handleRestaurantClick}
            />
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {restaurants.map((restaurant) => (
          <RestaurantCard 
            key={restaurant.place_id} 
            restaurant={restaurant} 
            onSelect={handleRestaurantClick}
          />
        ))}
      </div>

      {restaurants.length === 0 && !loading && searchCenter && (
        <div className="text-center py-8">
          <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-600 mb-2">No restaurants found</h3>
          <p className="text-gray-500">Try expanding your search radius or using different keywords</p>
        </div>
      )}
    </div>
  );
};

// Shopping List Component
const ShoppingListView = ({ userProfile }) => {
  const [shoppingLists, setShoppingLists] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadShoppingLists();
  }, []);

  const loadShoppingLists = async () => {
    try {
      const response = await axios.get(`${API}/shopping-lists/${userProfile.id}`);
      setShoppingLists(response.data);
    } catch (error) {
      console.error("Failed to load shopping lists:", error);
    }
  };

  const toggleItem = async (listId, itemIndex) => {
    try {
      const list = shoppingLists.find(l => l.id === listId);
      const updatedItems = [...list.items];
      updatedItems[itemIndex].checked = !updatedItems[itemIndex].checked;
      
      await axios.put(`${API}/shopping-lists/${listId}`, {
        items: updatedItems
      });
      
      setShoppingLists(prev => prev.map(l => 
        l.id === listId ? {...l, items: updatedItems} : l
      ));
    } catch (error) {
      console.error("Failed to update item:", error);
      toast.error("Failed to update item");
    }
  };

  const getCategoryIcon = (category) => {
    switch(category) {
      case 'produce': return '🥬';
      case 'proteins': return '🥩';
      case 'pantry': return '🥫';
      case 'frozen': return '🧊';
      default: return '📦';
    }
  };

  const getCategoryColor = (category) => {
    switch(category) {
      case 'produce': return 'bg-green-100 text-green-700';
      case 'proteins': return 'bg-red-100 text-red-700';
      case 'pantry': return 'bg-yellow-100 text-yellow-700';
      case 'frozen': return 'bg-blue-100 text-blue-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  if (shoppingLists.length === 0) {
    return (
      <div className="text-center py-12">
        <ShoppingCart className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-600 mb-2">No Shopping Lists Yet</h3>
        <p className="text-gray-500">Ask the AI health coach for meal planning to generate shopping lists!</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <ShoppingCart className="h-6 w-6 text-emerald-600" />
          My Shopping Lists
        </h2>
      </div>

      <div className="grid gap-6">
        {shoppingLists.map((list) => (
          <Card key={list.id} className="bg-white/90 backdrop-blur-sm shadow-lg border border-gray-200/50">
            <CardHeader className="bg-gradient-to-r from-emerald-50 to-blue-50">
              <CardTitle className="flex items-center justify-between">
                <span>{list.title}</span>
                <Badge variant="outline" className="bg-white">
                  {list.items.filter(item => item.checked).length} / {list.items.length} completed
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              {['produce', 'proteins', 'pantry', 'frozen', 'other'].map(category => {
                const categoryItems = list.items.filter(item => item.category === category);
                if (categoryItems.length === 0) return null;
                
                return (
                  <div key={category} className="mb-6">
                    <h4 className={`font-semibold mb-3 px-3 py-1 rounded-full inline-block capitalize ${getCategoryColor(category)}`}>
                      {getCategoryIcon(category)} {category === 'proteins' ? 'Proteins (Meat/Fish/Dairy)' : category.replace('_', ' ')}
                    </h4>
                    <div className="space-y-2 ml-4">
                      {categoryItems.map((item, index) => {
                        const globalIndex = list.items.findIndex(i => i === item);
                        return (
                          <div 
                            key={globalIndex}
                            className={`flex items-center gap-3 p-2 rounded-lg transition-all duration-200 ${
                              item.checked ? 'bg-gray-50 opacity-60' : 'hover:bg-gray-50'
                            }`}
                          >
                            <button
                              onClick={() => toggleItem(list.id, globalIndex)}
                              className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-all duration-200 ${
                                item.checked 
                                  ? 'bg-emerald-500 border-emerald-500 text-white' 
                                  : 'border-gray-300 hover:border-emerald-400'
                              }`}
                            >
                              {item.checked && <Check className="h-3 w-3" />}
                            </button>
                            <span className={`flex-1 ${item.checked ? 'line-through text-gray-500' : 'text-gray-800'}`}>
                              {item.item}
                            </span>
                            {item.quantity && (
                              <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">
                                {item.quantity}
                              </span>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

// Restaurant Details Component
const RestaurantDetails = ({ restaurant, onGetAIAnalysis, onBack }) => {
  const [loading, setLoading] = useState(false);
  const [smsLoading, setSmsLoading] = useState(false);
  const [showPhoneInput, setShowPhoneInput] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState("");

  const getDiabeticRatingColor = (score) => {
    if (score >= 4) return "bg-gradient-to-r from-green-500 to-emerald-500 text-white";
    if (score >= 3) return "bg-gradient-to-r from-blue-500 to-cyan-500 text-white";
    if (score >= 2) return "bg-gradient-to-r from-yellow-500 to-orange-500 text-white";
    return "bg-gradient-to-r from-red-500 to-pink-500 text-white";
  };

  const getDiabeticRatingText = (score) => {
    if (score >= 4) return "Excellent for Diabetics";
    if (score >= 3) return "Good for Diabetics";
    if (score >= 2) return "Fair - Use Caution";
    return "Requires Careful Selection";
  };

  const handleAIAnalysis = async () => {
    setLoading(true);
    await onGetAIAnalysis(restaurant);
    setLoading(false);
  };

  const handleSendToPhone = async () => {
    // Get user profile to check if phone number is saved
    const userId = localStorage.getItem('nutritame_user_id');
    if (!userId) {
      toast.error("Please create a profile first");
      return;
    }

    let phoneToUse = phoneNumber;
    
    // If no phone number entered, try to get from profile
    if (!phoneToUse) {
      try {
        const response = await axios.get(`${API}/users/${userId}`);
        phoneToUse = response.data.phone_number;
      } catch (error) {
        console.error("Error getting user profile:", error);
      }
    }

    if (!phoneToUse) {
      setShowPhoneInput(true);
      return;
    }

    setSmsLoading(true);
    try {
      const response = await axios.post(`${API}/sms/send-restaurant`, {
        user_id: userId,
        phone_number: phoneToUse,
        restaurant_place_id: restaurant.place_id
      });

      toast.success(`📱 Restaurant info sent to ${phoneToUse}!`);
      setShowPhoneInput(false);
      setPhoneNumber("");
    } catch (error) {
      console.error("SMS sending error:", error);
      if (error.response?.data?.detail?.includes("Invalid phone number")) {
        toast.error("Invalid phone number format. Please use format: +1234567890");
      } else {
        toast.error("Failed to send SMS. Please try again.");
      }
    } finally {
      setSmsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <Button 
        variant="outline" 
        onClick={onBack}
        className="mb-4"
      >
        ← Back to Restaurant Search
      </Button>

      {/* Restaurant Header */}
      <Card className="shadow-xl bg-white/90 backdrop-blur-sm">
        <CardHeader className="bg-gradient-to-r from-emerald-50 to-blue-50">
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-2xl text-gray-800">{restaurant.name}</CardTitle>
              <CardDescription className="flex items-center gap-2 text-gray-600 mt-2">
                <MapPin className="h-4 w-4" />
                {restaurant.address}
              </CardDescription>
            </div>
            {restaurant.diabetic_friendly_score && (
              <Badge className={`px-4 py-2 text-sm font-semibold ${getDiabeticRatingColor(restaurant.diabetic_friendly_score)}`}>
                {getDiabeticRatingText(restaurant.diabetic_friendly_score)}
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Restaurant Info */}
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                {restaurant.rating && (
                  <div className="flex items-center gap-1 bg-yellow-50 px-3 py-2 rounded-full">
                    <Star className="h-5 w-5 text-yellow-500 fill-current" />
                    <span className="font-semibold text-yellow-700">{restaurant.rating}</span>
                    <span className="text-sm text-yellow-600">Google Rating</span>
                  </div>
                )}
                {restaurant.price_level && (
                  <div className="bg-gray-50 px-3 py-2 rounded-full">
                    <span className="font-semibold text-gray-700">
                      {"$".repeat(restaurant.price_level)} Price Level
                    </span>
                  </div>
                )}
              </div>

              {restaurant.phone_number && (
                <div className="flex items-center gap-2 text-gray-600">
                  <Phone className="h-4 w-4" />
                  <span>{restaurant.phone_number}</span>
                </div>
              )}

              {restaurant.website && (
                <div className="flex items-center gap-2 text-gray-600">
                  <Globe className="h-4 w-4" />
                  <a 
                    href={restaurant.website} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    Visit Website
                  </a>
                </div>
              )}

              {restaurant.opening_hours && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-800 mb-2">Hours</h4>
                  <div className="text-sm text-gray-600">
                    {restaurant.opening_hours.open_now ? (
                      <span className="text-green-600 font-medium">🟢 Open Now</span>
                    ) : (
                      <span className="text-red-600 font-medium">🔴 Closed</span>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Diabetic Score Details */}
            <div className="space-y-4">
              <div className="bg-gradient-to-br from-emerald-50 to-blue-50 p-4 rounded-lg border border-emerald-200">
                <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <Target className="h-5 w-5 text-emerald-600" />
                  Diabetic Friendliness
                </h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Overall Score</span>
                    <span className="font-bold text-lg">
                      {restaurant.diabetic_friendly_score?.toFixed(1) || "N/A"}/5.0
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div 
                      className={`h-3 rounded-full ${
                        (restaurant.diabetic_friendly_score || 0) >= 4 ? 'bg-green-500' :
                        (restaurant.diabetic_friendly_score || 0) >= 3 ? 'bg-blue-500' :
                        (restaurant.diabetic_friendly_score || 0) >= 2 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${((restaurant.diabetic_friendly_score || 0) / 5) * 100}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-600">
                    Score based on menu options, preparation methods, and customer reviews
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Phone Number Input (if needed) */}
          {showPhoneInput && (
            <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <Smartphone className="h-5 w-5 text-blue-600" />
                  <h4 className="font-semibold text-gray-800">Enter Phone Number</h4>
                </div>
                <Input
                  type="tel"
                  placeholder="+1 (555) 123-4567"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  className="border-blue-300 focus:border-blue-500"
                />
                <div className="flex gap-2">
                  <Button 
                    onClick={handleSendToPhone}
                    disabled={smsLoading || !phoneNumber.trim()}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    {smsLoading ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                        Sending...
                      </>
                    ) : (
                      <>
                        <Smartphone className="h-4 w-4 mr-2" />
                        Send SMS
                      </>
                    )}
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => setShowPhoneInput(false)}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="mt-8 flex flex-col sm:flex-row gap-4">
            <Button 
              onClick={handleAIAnalysis}
              disabled={loading}
              className="flex-1 bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700 text-white shadow-lg"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                  Getting AI Analysis...
                </>
              ) : (
                <>
                  <MessageCircle className="h-4 w-4 mr-2" />
                  Get AI Diabetic Analysis
                </>
              )}
            </Button>
            
            <Button 
              onClick={handleSendToPhone}
              disabled={smsLoading}
              className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg"
            >
              {smsLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                  Sending...
                </>
              ) : (
                <>
                  <Smartphone className="h-4 w-4 mr-2" />
                  Send to Phone
                </>
              )}
            </Button>
            
            {restaurant.website && (
              <Button 
                variant="outline"
                onClick={() => window.open(restaurant.website, '_blank')}
                className="flex-1"
              >
                <Globe className="h-4 w-4 mr-2" />
                View Menu Online
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Photos */}
      {restaurant.photos && restaurant.photos.length > 0 && (
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle>Photos</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {restaurant.photos.slice(0, 6).map((photo, index) => (
                <div key={index} className="aspect-square overflow-hidden rounded-lg">
                  <img 
                    src={photo} 
                    alt={`${restaurant.name} photo ${index + 1}`}
                    className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                  />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

const RestaurantCard = ({ restaurant, onSelect }) => {
  const getDiabeticRatingColor = (score) => {
    if (score >= 4) return "bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-lg";
    if (score >= 3) return "bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-lg";
    if (score >= 2) return "bg-gradient-to-r from-yellow-500 to-orange-500 text-white shadow-lg";
    return "bg-gradient-to-r from-red-500 to-pink-500 text-white shadow-lg";
  };

  const getDiabeticRatingText = (score) => {
    if (score >= 4) return "Excellent";
    if (score >= 3) return "Good";
    if (score >= 2) return "Fair";
    return "Needs Care";
  };

  return (
    <Card className="hover:shadow-xl transition-all duration-300 cursor-pointer transform hover:scale-105 bg-white/90 backdrop-blur-sm border border-gray-200/50" onClick={() => onSelect(restaurant)}>
      <CardContent className="p-4">
        <div className="space-y-3">
          <div>
            <h3 className="font-semibold text-lg text-gray-800">{restaurant.name}</h3>
            <p className="text-sm text-gray-600 flex items-center gap-1">
              <MapPin className="h-3 w-3 text-emerald-500" />
              {restaurant.address}
            </p>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {restaurant.rating && (
                <div className="flex items-center gap-1 bg-yellow-50 px-2 py-1 rounded-full">
                  <Star className="h-4 w-4 text-yellow-500 fill-current" />
                  <span className="text-sm font-medium text-yellow-700">{restaurant.rating}</span>
                </div>
              )}
              {restaurant.price_level && (
                <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded-full font-medium">
                  {"$".repeat(restaurant.price_level)}
                </span>
              )}
            </div>
            
            {restaurant.diabetic_friendly_score && (
              <Badge className={getDiabeticRatingColor(restaurant.diabetic_friendly_score)}>
                {getDiabeticRatingText(restaurant.diabetic_friendly_score)}
              </Badge>
            )}
          </div>
          
          <div className="flex items-center justify-between">
            <div className="text-xs text-gray-500 bg-gradient-to-r from-emerald-50 to-blue-50 px-2 py-1 rounded-full">
              Diabetic Score: <span className="font-semibold">{restaurant.diabetic_friendly_score?.toFixed(1) || "N/A"}/5.0</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Main Dashboard Component
const Dashboard = ({ userProfile, onBack }) => {
  const [activeTab, setActiveTab] = useState("chat");
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedRestaurant, setSelectedRestaurant] = useState(null);
  const [showShoppingListButton, setShowShoppingListButton] = useState(false);
  const [lastMealPlan, setLastMealPlan] = useState("");
  const [showBackToTop, setShowBackToTop] = useState(false);
  const [showScrollToBottom, setShowScrollToBottom] = useState(false);
  const [savedChats, setSavedChats] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [showSavedChats, setShowSavedChats] = useState(false);
  const [favoriteRecipes, setFavoriteRecipes] = useState([]);
  const [showFavorites, setShowFavorites] = useState(false);
  const [deleteConfirmId, setDeleteConfirmId] = useState(null);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);

  // Auto-scroll to show start of latest AI response (not the very bottom)
  const scrollToLatestResponse = () => {
    // Find all messages
    const messageElements = messagesContainerRef.current?.querySelectorAll('.message-enter');
    if (messageElements && messageElements.length > 0) {
      // Get the last message
      const lastMessage = messageElements[messageElements.length - 1];
      // Scroll to show the beginning of this message, with some padding
      lastMessage.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  // Scroll to bottom function (for manual bottom navigation)
  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // New Chat functionality - Opens in new window/tab
  const startNewChat = () => {
    // Open new window/tab with fresh chat
    const newWindow = window.open(window.location.href, '_blank');
    if (newWindow) {
      // Focus the new window
      newWindow.focus();
      toast.success("New chat opened in new window");
    } else {
      // Fallback if popup blocked - clear current chat
      setMessages([{
        id: 'welcome-' + Date.now(),
        message: `Hi! I'm your AI health coach. I can help you with meal planning, restaurant recommendations, and nutrition analysis. What would you like to explore today?`,
        response: '',
        isWelcome: true
      }]);
      setCurrentChatId(null);
      setLastMealPlan("");
      setShowShoppingListButton(false);
      toast.success("Started new chat session (popup blocked - cleared current)");
    }
  };

  // Save current chat
  const saveCurrentChat = () => {
    if (messages.length <= 1) {
      toast.error("No conversation to save");
      return;
    }

    const chatTitle = messages[1]?.message?.substring(0, 50) + '...' || 'Untitled Chat';
    const chatId = currentChatId || 'chat-' + Date.now();
    
    const chatData = {
      id: chatId,
      title: chatTitle,
      messages: messages,
      timestamp: new Date().toISOString(),
      lastMealPlan: lastMealPlan
    };

    // Save to localStorage
    const existingChats = JSON.parse(localStorage.getItem('nutritame_chats') || '[]');
    const updatedChats = existingChats.filter(chat => chat.id !== chatId);
    updatedChats.unshift(chatData);
    
    // Keep only last 10 chats
    if (updatedChats.length > 10) {
      updatedChats.splice(10);
    }
    
    localStorage.setItem('nutritame_chats', JSON.stringify(updatedChats));
    setSavedChats(updatedChats);
    setCurrentChatId(chatId);
    
    toast.success("Chat saved successfully!");
  };

  // Load saved chat
  const loadSavedChat = (chatData) => {
    setMessages(chatData.messages);
    setCurrentChatId(chatData.id);
    setLastMealPlan(chatData.lastMealPlan || "");
    setShowSavedChats(false);
    toast.success("Chat loaded successfully!");
  };

  // Load saved chats from localStorage
  const loadSavedChats = () => {
    const saved = JSON.parse(localStorage.getItem('nutritame_chats') || '[]');
    setSavedChats(saved);
    setShowSavedChats(!showSavedChats);
  };

  // Delete saved chat
  const deleteSavedChat = (chatId, event) => {
    event.stopPropagation(); // Prevent loading the chat when clicking delete
    
    if (deleteConfirmId === chatId) {
      // Actually delete
      const existingChats = JSON.parse(localStorage.getItem('nutritame_chats') || '[]');
      const updatedChats = existingChats.filter(chat => chat.id !== chatId);
      localStorage.setItem('nutritame_chats', JSON.stringify(updatedChats));
      setSavedChats(updatedChats);
      setDeleteConfirmId(null);
      
      // If we deleted the current chat, clear the current chat ID
      if (currentChatId === chatId) {
        setCurrentChatId(null);
      }
      
      toast.success("Chat deleted successfully");
    } else {
      // Show confirmation
      setDeleteConfirmId(chatId);
      setTimeout(() => setDeleteConfirmId(null), 3000); // Auto-cancel after 3 seconds
    }
  };

  // Add to favorites (for specific AI responses containing recipes/meal plans)
  const addToFavorites = (messageContent, messageIndex) => {
    const favoriteItem = {
      id: 'fav-' + Date.now(),
      title: messageContent.substring(0, 60) + '...',
      content: messageContent,
      timestamp: new Date().toISOString(),
      fromChatId: currentChatId,
      messageIndex: messageIndex
    };

    const existingFavorites = JSON.parse(localStorage.getItem('nutritame_favorites') || '[]');
    existingFavorites.unshift(favoriteItem);
    
    // Keep only last 20 favorites
    if (existingFavorites.length > 20) {
      existingFavorites.splice(20);
    }
    
    localStorage.setItem('nutritame_favorites', JSON.stringify(existingFavorites));
    setFavoriteRecipes(existingFavorites);
    
    toast.success("Added to favorites!");
  };

  // Load favorites
  const loadFavorites = () => {
    const saved = JSON.parse(localStorage.getItem('nutritame_favorites') || '[]');
    setFavoriteRecipes(saved);
    setShowFavorites(!showFavorites);
  };

  // Delete favorite
  const deleteFavorite = (favId, event) => {
    event.stopPropagation();
    const existingFavorites = JSON.parse(localStorage.getItem('nutritame_favorites') || '[]');
    const updatedFavorites = existingFavorites.filter(fav => fav.id !== favId);
    localStorage.setItem('nutritame_favorites', JSON.stringify(updatedFavorites));
    setFavoriteRecipes(updatedFavorites);
    toast.success("Favorite deleted");
  };

  // Scroll to top function
  const scrollToTop = () => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  // Handle scroll to show/hide back to top button
  const handleScroll = () => {
    if (messagesContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current;
      // Show back to top button if scrolled down more than 200px from the top
      const isScrolledDown = scrollTop > 200;
      // Show scroll to bottom if not at the bottom and scrolled up from bottom
      const isNearBottom = scrollTop > (scrollHeight - clientHeight - 100);
      
      setShowBackToTop(isScrolledDown && messages.length > 2);
      setShowScrollToBottom(!isNearBottom && messages.length > 2);
    }
  };

  // Auto scroll to show start of latest response when new messages arrive
  useEffect(() => {
    const timer = setTimeout(() => {
      if (messagesContainerRef.current && messages.length > 0) {
        // For AI responses, scroll to show the beginning of the response
        const lastMessage = messages[messages.length - 1];
        if (lastMessage && !lastMessage.isUser) {
          scrollToLatestResponse();
        } else {
          // For user messages, scroll to bottom
          messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
        }
      }
    }, 200);
    return () => clearTimeout(timer);
  }, [messages]);

  // Auto-scroll to show start of latest AI response when messages update
  useEffect(() => {
    // Only auto-scroll when there are messages and we're not in loading state
    if (messages.length > 0 && !loading) {
      // Delay slightly to ensure message is rendered
      setTimeout(() => {
        scrollToLatestResponse();
      }, 100);
    }
    // When loading starts, scroll to show the "AI is thinking" indicator
    else if (loading && messages.length > 0) {
      setTimeout(() => {
        scrollToBottom();
      }, 100);
    }
  }, [messages, loading]);

  // Add scroll listener to messages container
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (container) {
      container.addEventListener('scroll', handleScroll);
      return () => container.removeEventListener('scroll', handleScroll);
    }
  }, []);

  useEffect(() => {
    // Load chat history
    loadChatHistory();
    
    // Load saved chats from localStorage
    const saved = JSON.parse(localStorage.getItem('nutritame_chats') || '[]');
    setSavedChats(saved);
    
    // Load favorites from localStorage
    const favorites = JSON.parse(localStorage.getItem('nutritame_favorites') || '[]');
    setFavoriteRecipes(favorites);
    
    // Add welcome message
    const welcomeMsg = {
      id: 'welcome',
      message: `Hi! I'm your AI health coach. I can help you with meal planning, restaurant recommendations, and nutrition analysis. What would you like to explore today?`,
      response: '',
      isWelcome: true
    };
    setMessages([welcomeMsg]);
  }, []);

  const loadChatHistory = async () => {
    try {
      const response = await axios.get(`${API}/chat/${userProfile.id}`);
      // Only load recent messages to avoid overwhelming the UI
      const recentMessages = response.data.slice(-10);
      if (recentMessages.length > 0) {
        setMessages(prev => [...prev, ...recentMessages.map(msg => ({ ...msg, isUser: false }))]);
      }
    } catch (error) {
      console.error("Failed to load chat history:", error);
    }
  };

  const generateShoppingList = async () => {
    if (!lastMealPlan) {
      toast.error("No meal plan found to generate shopping list");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/shopping-lists/generate`, {
        user_id: userProfile.id,
        meal_plan_text: lastMealPlan
      });

      toast.success("Shopping list created successfully!");
      setActiveTab("shopping");
      setShowShoppingListButton(false);
    } catch (error) {
      console.error("Shopping list generation error:", error);
      toast.error("Failed to create shopping list. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!currentMessage.trim()) return;
    
    const userMsg = {
      id: Date.now(),
      message: currentMessage,
      isUser: true
    };
    
    setMessages(prev => [...prev, userMsg]);
    setCurrentMessage("");
    setLoading(true);

    try {
      const response = await axios.post(`${API}/chat`, {
        user_id: userProfile.id,
        message: currentMessage,
        restaurant_context: selectedRestaurant ? {
          name: selectedRestaurant.name,
          address: selectedRestaurant.address,
          rating: selectedRestaurant.rating,
          price_level: selectedRestaurant.price_level,
          diabetic_friendly_score: selectedRestaurant.diabetic_friendly_score
        } : null
      });

      const aiMsg = {
        id: Date.now() + 1,
        message: response.data.response,
        isUser: false
      };

      setMessages(prev => [...prev, aiMsg]);
      
      // Check if response contains meal planning keywords for shopping list button
      const responseText = response.data.response.toLowerCase();
      if (responseText.includes('meal plan') || responseText.includes('shopping') || responseText.includes('ingredients') || responseText.includes('grocery')) {
        setShowShoppingListButton(true);
        setLastMealPlan(response.data.response);
      }

    } catch (error) {
      console.error("Chat error:", error);
      toast.error("Failed to send message. Please try again.");
      const errorMsg = {
        id: Date.now() + 1,
        message: "Sorry, I'm having trouble connecting right now. Please try again in a moment.",
        isUser: false,
        isError: true
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleRestaurantSelect = (restaurant) => {
    setSelectedRestaurant(restaurant);
    setActiveTab("chat");
    
    // Add a message about the selected restaurant to the chat
    const restaurantMsg = {
      id: Date.now(),
      message: `Please analyze ${restaurant.name} for diabetes-friendly options. The restaurant is located at ${restaurant.address} and has a ${restaurant.rating} star rating.`,
      isUser: true
    };
    
    setMessages(prev => [...prev, restaurantMsg]);
    setLoading(true);

    // Auto-send AI analysis request
    setTimeout(async () => {
      try {
        const response = await axios.post(`${API}/chat`, {
          user_id: userProfile.id,
          message: `Analyze ${restaurant.name} for diabetic-friendly menu options and provide recommendations.`,
          restaurant_context: {
            name: restaurant.name,
            address: restaurant.address,
            rating: restaurant.rating,
            price_level: restaurant.price_level,
            diabetic_friendly_score: restaurant.diabetic_friendly_score
          }
        });

        const aiMsg = {
          id: Date.now(),
          message: response.data.response,
          isUser: false
        };

        setMessages(prev => [...prev, aiMsg]);
      } catch (error) {
        console.error("Restaurant analysis error:", error);
        const errorMsg = {
          id: Date.now(),
          message: "I'm having trouble analyzing this restaurant right now. Please try asking me directly about diabetic-friendly options.",
          isUser: false,
          isError: true
        };
        setMessages(prev => [...prev, errorMsg]);
      } finally {
        setLoading(false);
      }
    }, 1000);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-cyan-50 to-blue-50">
      <SaaSHeader 
        userProfile={userProfile} 
        onLogout={onBack}
        currentUser={userProfile}
      />
      
      <div className="pt-16">
        <div className="max-w-7xl mx-auto p-4">
          {/* Dashboard Header */}
          <div className="mb-6">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-emerald-600 via-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
              NutriTame AI Health Coach
            </h1>
            <p className="text-gray-700 text-lg">
              Your personalized diabetes management assistant with restaurant search and meal planning
            </p>
          </div>

          {/* Navigation Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-3 lg:grid-cols-3 mb-6 bg-white/70 backdrop-blur-sm shadow-lg">
              <TabsTrigger 
                value="chat" 
                className="flex items-center gap-2 text-sm md:text-base data-[state=active]:bg-gradient-to-r data-[state=active]:from-emerald-500 data-[state=active]:to-blue-500 data-[state=active]:text-white"
              >
                <MessageCircle className="h-4 w-4" />
                AI Health Coach
              </TabsTrigger>
              <TabsTrigger 
                value="restaurants" 
                className="flex items-center gap-2 text-sm md:text-base data-[state=active]:bg-gradient-to-r data-[state=active]:from-emerald-500 data-[state=active]:to-blue-500 data-[state=active]:text-white"
              >
                <Search className="h-4 w-4" />
                Restaurants
              </TabsTrigger>
              <TabsTrigger 
                value="shopping" 
                className="flex items-center gap-2 text-sm md:text-base data-[state=active]:bg-gradient-to-r data-[state=active]:from-emerald-500 data-[state=active]:to-blue-500 data-[state=active]:text-white"
              >
                <ShoppingCart className="h-4 w-4" />
                Shopping Lists
              </TabsTrigger>
            </TabsList>

            {/* AI Health Coach Tab */}
            <TabsContent value="chat">
              <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-xl border border-gray-200/50">
                <div className="p-6">
                  <div className="flex flex-col h-[calc(100vh-320px)]">
                    {/* Chat Header with controls */}
                    <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-200">
                      <div className="flex items-center gap-2">
                        <div className="p-2 bg-gradient-to-br from-emerald-100 to-blue-100 rounded-full">
                          <MessageCircle className="h-5 w-5 text-emerald-600" />
                        </div>
                        <h2 className="text-xl font-bold text-gray-800">AI Health Coach</h2>
                        {selectedRestaurant && (
                          <Badge variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-200">
                            Analyzing: {selectedRestaurant.name}
                          </Badge>
                        )}
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <Button
                          onClick={loadSavedChats}
                          variant="outline"
                          size="sm"
                          className="hidden md:flex items-center gap-2"
                        >
                          <FolderOpen className="h-4 w-4" />
                          Saved Chats ({savedChats.length})
                        </Button>
                        
                        <Button
                          onClick={loadFavorites}
                          variant="outline"
                          size="sm"
                          className="hidden md:flex items-center gap-2"
                        >
                          <BookOpen className="h-4 w-4" />
                          Favorites ({favoriteRecipes.length})
                        </Button>
                        
                        <Button
                          onClick={saveCurrentChat}
                          disabled={messages.length <= 1}
                          variant="outline"
                          size="sm"
                          className="flex items-center gap-2"
                        >
                          <Save className="h-4 w-4" />
                          Save
                        </Button>
                        
                        <Button
                          onClick={startNewChat}
                          variant="outline"
                          size="sm"
                          className="flex items-center gap-2"
                        >
                          <MessageSquarePlus className="h-4 w-4" />
                          New Chat
                        </Button>
                      </div>
                    </div>

                    {/* Demo Countdown Timer - Show in demo mode */}
                    <DemoCountdownTimer />

                    {/* Messages Container */}
                    <div 
                      ref={messagesContainerRef}
                      className="flex-1 overflow-y-auto space-y-4 mb-4 max-h-[500px] pr-2"
                      style={{ maxHeight: 'calc(100vh - 500px)' }}
                    >
                      {messages.map((msg, index) => (
                        <div key={msg.id} className={`message-enter flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}>
                          <div className={`max-w-[85%] p-4 rounded-lg ${
                            msg.isUser 
                              ? 'bg-gradient-to-r from-emerald-500 to-blue-500 text-white'
                              : msg.isWelcome
                                ? 'bg-gradient-to-r from-emerald-50 to-blue-50 text-gray-800 border border-emerald-200'
                                : msg.isError
                                  ? 'bg-red-50 text-red-700 border border-red-200'
                                  : 'bg-white border border-gray-200 shadow-sm text-gray-800'
                          }`}>
                            <div className="whitespace-pre-wrap">{msg.message}</div>
                            
                            {/* Add to favorites button for AI responses */}
                            {!msg.isUser && !msg.isWelcome && !msg.isError && (
                              <div className="flex gap-2 mt-3 pt-3 border-t border-gray-200">
                                <Button
                                  onClick={() => addToFavorites(msg.message, index)}
                                  variant="outline"
                                  size="sm"
                                  className="text-xs"
                                >
                                  <Heart className="h-3 w-3 mr-1" />
                                  Save
                                </Button>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                      
                      {/* Shopping List Card - appears after AI responses when meal plan is detected */}
                      {showShoppingListButton && (
                        <div className="flex justify-center">
                          <Card className="bg-gradient-to-r from-emerald-50 to-blue-50 border-emerald-200 max-w-md w-full">
                            <CardContent className="p-4 text-center">
                              <ShoppingCart className="h-6 w-6 text-emerald-600 mx-auto mb-2" />
                              <h3 className="font-semibold text-gray-800 mb-2">Create Shopping List</h3>
                              <p className="text-sm text-gray-600 mb-4">
                                Generate a shopping list based on this meal plan
                              </p>
                              <Button 
                                onClick={generateShoppingList}
                                className="bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700 text-white"
                                disabled={loading}
                              >
                                <List className="h-4 w-4 mr-2" />
                                Generate Shopping List
                              </Button>
                            </CardContent>
                          </Card>
                        </div>
                      )}
                      
                      {loading && (
                        <div className="flex justify-start">
                          <div className="bg-white border border-gray-200 shadow-sm text-gray-800 p-4 rounded-lg">
                            <div className="flex items-center gap-2">
                              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-emerald-600"></div>
                              <span>AI is thinking...</span>
                            </div>
                          </div>
                        </div>
                      )}
                      <div ref={messagesEndRef} />
                    </div>

                    {/* Fixed Input Area */}
                    <div className="flex-shrink-0 sticky bottom-0 bg-white/95 backdrop-blur-sm rounded-lg border border-gray-200 p-4">
                      <div className="flex gap-3">
                        <Textarea
                          value={currentMessage}
                          onChange={(e) => setCurrentMessage(e.target.value)}
                          onKeyPress={handleKeyPress}
                          placeholder="Ask about meal planning, restaurants, nutrition, or diabetes management..."
                          className="flex-1 resize-none border-gray-300 focus:border-emerald-500 focus:ring-emerald-500"
                          rows={2}
                          style={{ height: '80px' }}
                        />
                        <Button 
                          onClick={sendMessage}
                          disabled={loading || !currentMessage.trim()}
                          className="bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700 text-white px-6 h-full"
                        >
                          {loading ? (
                            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          ) : (
                            'Send'
                          )}
                        </Button>
                      </div>
                    </div>

                    {/* Floating Action Buttons */}
                    {showBackToTop && (
                      <Button
                        onClick={scrollToTop}
                        className="fixed bottom-24 right-6 z-50 rounded-full p-3 bg-emerald-600 hover:bg-emerald-700 text-white shadow-lg"
                        size="sm"
                      >
                        <ChevronUp className="h-4 w-4" />
                      </Button>
                    )}
                    
                    {showScrollToBottom && (
                      <Button
                        onClick={scrollToBottom}
                        className="fixed bottom-24 right-16 z-50 rounded-full p-3 bg-blue-600 hover:bg-blue-700 text-white shadow-lg"
                        size="sm"
                      >
                        <ChevronDown className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>

                {/* Saved Chats Sidebar */}
                {showSavedChats && (
                  <div className="fixed inset-y-0 right-0 w-80 bg-white shadow-xl border-l border-gray-200 z-50 overflow-y-auto">
                    <div className="p-4 bg-gradient-to-r from-emerald-50 to-blue-50 border-b">
                      <div className="flex items-center justify-between">
                        <h3 className="font-semibold text-gray-800">Saved Chats</h3>
                        <Button
                          onClick={() => setShowSavedChats(false)}
                          variant="ghost"
                          size="sm"
                        >
                          ×
                        </Button>
                      </div>
                    </div>
                    <div className="p-4 space-y-3">
                      {savedChats.map((chat) => (
                        <div
                          key={chat.id}
                          onClick={() => loadSavedChat(chat)}
                          className="p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors"
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <p className="font-medium text-sm text-gray-800 mb-1 line-clamp-2">
                                {chat.title}
                              </p>
                              <p className="text-xs text-gray-500">
                                {new Date(chat.timestamp).toLocaleDateString()}
                              </p>
                            </div>
                            <Button
                              onClick={(e) => deleteSavedChat(chat.id, e)}
                              variant="ghost"
                              size="sm"
                              className={`ml-2 p-1 h-auto ${
                                deleteConfirmId === chat.id 
                                  ? 'text-red-600 hover:text-red-700' 
                                  : 'text-gray-400 hover:text-gray-600'
                              }`}
                            >
                              {deleteConfirmId === chat.id ? '✓ Delete?' : <Trash2 className="h-3 w-3" />}
                            </Button>
                          </div>
                        </div>
                      ))}
                      {savedChats.length === 0 && (
                        <p className="text-gray-500 text-center py-8">No saved chats yet</p>
                      )}
                    </div>
                  </div>
                )}

                {/* Favorites Sidebar */}
                {showFavorites && (
                  <div className="fixed inset-y-0 right-0 w-80 bg-white shadow-xl border-l border-gray-200 z-50 overflow-y-auto">
                    <div className="p-4 bg-gradient-to-r from-emerald-50 to-blue-50 border-b">
                      <div className="flex items-center justify-between">
                        <h3 className="font-semibold text-gray-800">Favorite Recipes</h3>
                        <Button
                          onClick={() => setShowFavorites(false)}
                          variant="ghost"
                          size="sm"
                        >
                          ×
                        </Button>
                      </div>
                    </div>
                    <div className="p-4 space-y-3">
                      {favoriteRecipes.map((fav) => (
                        <div
                          key={fav.id}
                          className="p-3 bg-gray-50 rounded-lg"
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <p className="font-medium text-sm text-gray-800 mb-2 line-clamp-2">
                                {fav.title}
                              </p>
                              <p className="text-xs text-gray-600 mb-2 line-clamp-3">
                                {fav.content.substring(0, 150)}...
                              </p>
                              <p className="text-xs text-gray-500">
                                {new Date(fav.timestamp).toLocaleDateString()}
                              </p>
                            </div>
                            <Button
                              onClick={(e) => deleteFavorite(fav.id, e)}
                              variant="ghost"
                              size="sm"
                              className="ml-2 p-1 h-auto text-gray-400 hover:text-gray-600"
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                      ))}
                      {favoriteRecipes.length === 0 && (
                        <p className="text-gray-500 text-center py-8">No favorites yet</p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </TabsContent>

            {/* Restaurant Search Tab */}
            <TabsContent value="restaurants">
              <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-xl border border-gray-200/50 p-6">
                <RestaurantSearch 
                  userProfile={userProfile}
                  onRestaurantSelect={handleRestaurantSelect}
                />
              </div>
            </TabsContent>

            {/* Shopping Lists Tab */}
            <TabsContent value="shopping">
              <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-xl border border-gray-200/50 p-6">
                <ShoppingListView userProfile={userProfile} />
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [user, setUser] = useState(null);
  const [authToken, setAuthToken] = useState(null);
  const [appMode, setAppMode] = useState('landing');
  const [currentUser, setCurrentUser] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [showDisclaimer, setShowDisclaimer] = useState(true);
  const [disclaimerAccepted, setDisclaimerAccepted] = useState(false);
  const [adminMode, setAdminMode] = useState(false);
  const [demoMode, setDemoMode] = useState(false);
  const [demoUser, setDemoUser] = useState(null);

  useEffect(() => {
    // Check for disclaimer acceptance
    const disclaimerState = localStorage.getItem('nutritame_disclaimer_accepted');
    if (disclaimerState === 'true') {
      setDisclaimerAccepted(true);
      setShowDisclaimer(false);
    }

    // Check for existing authentication
    const savedToken = localStorage.getItem('nutritame_auth_token');
    const savedUserId = localStorage.getItem('nutritame_user_id');
    const adminToken = localStorage.getItem('adminToken');
    
    if (adminToken) {
      setAdminMode(true);
      setAppMode('admin');
    } else if (savedToken && savedUserId) {
      setAuthToken(savedToken);
      loadUserProfile(savedUserId, savedToken);
    }

    // Check for demo mode
    checkDemoMode();
  }, []);

  const checkDemoMode = async () => {
    try {
      const response = await axios.get(`${API}/demo/config`);
      if (response.data.demo_mode) {
        console.log('Demo mode is enabled');
      }
    } catch (error) {
      console.error('Failed to check demo mode:', error);
    }
  };

  const loadUserProfile = async (userId, token) => {
    try {
      const config = { headers: { Authorization: `Bearer ${token}` } };
      const response = await axios.get(`${API}/users/${userId}`, config);
      setUser(response.data);
      setCurrentUser(response.data);
      setAppMode('app');
    } catch (error) {
      console.error('Failed to load user profile:', error);
      // Clear invalid tokens
      localStorage.removeItem('nutritame_auth_token');
      localStorage.removeItem('nutritame_user_id');
    }
  };

  const handleDisclaimerAccept = () => {
    setDisclaimerAccepted(true);
    setShowDisclaimer(false);
    localStorage.setItem('nutritame_disclaimer_accepted', 'true');
  };

  const handleDisclaimerDecline = () => {
    // Redirect to external site or show message
    window.location.href = 'https://google.com';
  };

  const handleAppAccess = async (paymentData) => {
    try {
      console.log('Processing app access with payment data:', paymentData);
      
      // Here you would validate the payment and create the user account
      const response = await axios.post(`${API}/users`, {
        email: paymentData.email,
        subscription_tier: paymentData.plan === 'basic' ? 'basic' : 'premium',
        subscription_status: 'active'
      });
      
      console.log('User created:', response.data);
      
      setUser(response.data.user);
      setAuthToken(response.data.access_token);
      setCurrentUser({
        id: response.data.user.id,
        email: response.data.user.email,
        diabetes_type: response.data.user.diabetes_type,
        age: response.data.user.age,
        gender: response.data.user.gender,
        activity_level: response.data.user.activity_level,
        health_goals: response.data.user.health_goals || [],
        food_preferences: response.data.user.food_preferences || [],
        allergies: response.data.user.allergies || [],
        cooking_skill: response.data.user.cooking_skill,
        phone_number: response.data.user.phone_number
      });
      setShowForm(false);
      
      toast.success("Welcome to NutriTame! Your account is ready.");
    } catch (error) {
      console.error('App access error:', error);
      toast.error("There was an issue accessing your account. Please contact support.");
    }
  };

  // FIXED: Handle demo access - Complete fixed version
  const handleDemoAccess = async (demoData) => {
    try {
      console.log('Demo access data received:', demoData);
      setDemoMode(true);
      setDemoUser(demoData.user);
      setAuthToken(demoData.access_token);
      setAppMode('app');
      
      // Set up profile for demo mode - don't set diabetes_type so it's treated as new profile
      setCurrentUser({
        id: demoData.user.id,
        email: demoData.user.email,
        diabetes_type: "", // Empty so form treats as new profile
        age: null,
        gender: null,
        activity_level: null,
        health_goals: [],
        food_preferences: [],
        allergies: [],
        cooking_skill: null,
        phone_number: null
      });
      setShowForm(true); // Show profile setup for demo users
      
      // Scroll to top of page when profile form loads
      setTimeout(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }, 100);
      
      toast.success("Welcome to NutriTame Demo! All premium features unlocked.");
    } catch (error) {
      console.error('Demo access error:', error);
      toast.error("Failed to create demo access. Please try again.");
    }
  };

  // Handle admin login
  const handleAdminLogin = (token) => {
    localStorage.setItem('adminToken', token);
    setAdminMode(true);
    setAppMode('admin');
  };

  // Handle profile completion
  const handleProfileComplete = (profileData) => {
    console.log('Profile completed with data:', profileData);
    setCurrentUser(profileData);
    setShowForm(false);
    
    // Store user info in localStorage for session persistence
    localStorage.setItem('nutritame_user_id', profileData.id);
    if (authToken) {
      localStorage.setItem('nutritame_auth_token', authToken);
    }
    
    toast.success("Profile setup complete! Welcome to NutriTame!");
  };

  // Handle logout
  const handleLogout = () => {
    setUser(null);
    setAuthToken(null);
    setCurrentUser(null);
    setAppMode('landing');
    setShowForm(false);
    setAdminMode(false);
    setDemoMode(false);
    setDemoUser(null);
    localStorage.removeItem('nutritame_auth_token');
    localStorage.removeItem('nutritame_user_id');
    localStorage.removeItem('adminToken');
    toast.success("Logged out successfully");
  };

  const handleLandingGetStarted = (mode) => {
    if (mode === 'demo') {
      setAppMode('demo'); // Route to DemoLandingPage
    } else {
      setAppMode('signup'); // Route to normal signup flow
    }
  };

  // Medical Disclaimer Check - Show before any other content
  if (showDisclaimer && !disclaimerAccepted) {
    return (
      <MedicalDisclaimer 
        onAccept={handleDisclaimerAccept}
        onDecline={handleDisclaimerDecline}
      />
    );
  }

  // Demo Mode Rendering
  if (appMode === 'demo') {
    return <DemoLandingPage onDemoAccess={handleDemoAccess} />;
  }

  // Landing Page (Default)
  if (appMode === 'landing') {
    return <LandingPage onGetStarted={handleLandingGetStarted} />;
  }

  // SaaS Mode Rendering (Payment/Signup Flow)
  if (appMode === 'signup') {
    return (
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage onStartTrial={() => setAppMode('landing')} />} />
          <Route path="/success" element={<PaymentSuccess onAccessApp={handleAppAccess} />} />
          <Route path="/cancel" element={<LandingPage onStartTrial={() => setAppMode('landing')} />} />
          <Route path="/admin" element={<AdminLogin onAdminLogin={handleAdminLogin} />} />
        </Routes>
      </BrowserRouter>
    );
  }

  // Admin Dashboard
  if (adminMode && appMode === 'admin') {
    return <AdminDashboard onLogout={handleLogout} />;
  }

  // Main App Rendering
  if (appMode === 'app' && currentUser) {
    return (
      <div className="min-h-screen">
        {/* Demo Mode Banner */}
        {demoMode && <DemoModeBanner />}
        
        {/* Show Profile Setup if needed */}
        {showForm ? (
          <UserProfileSetup 
            onProfileComplete={handleProfileComplete}
            existingProfile={currentUser}
          />
        ) : (
          <Dashboard 
            userProfile={currentUser}
            onBack={handleLogout}
          />
        )}
      </div>
    );
  }

  // Fallback to Landing Page
  return <LandingPage onGetStarted={handleLandingGetStarted} />;
}

export default App;