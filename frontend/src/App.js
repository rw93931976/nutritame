import { useState, useEffect, useRef } from "react";
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import axios from "axios";
import "./App.css";

// CRITICAL DEBUG: This should appear in console immediately
console.log('🏗️ App.js file loaded - module executing');

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

// =============================================
// AI HEALTH COACH SERVICE FUNCTIONS
// =============================================

// AI Health Coach API Service
const aiCoachService = {
  // Check feature flags
  async getFeatureFlags() {
    try {
      const response = await axios.get(`${API}/coach/feature-flags`);
      return response.data;
    } catch (error) {
      console.error('Error getting feature flags:', error);
      throw error;
    }
  },

  // Disclaimer management
  async acceptDisclaimer(userId) {
    try {
      const response = await axios.post(`${API}/coach/accept-disclaimer`, {
        user_id: userId
      });
      return response.data;
    } catch (error) {
      console.error('Error accepting disclaimer:', error);
      throw error;
    }
  },

  async getDisclaimerStatus(userId) {
    try {
      const response = await axios.get(`${API}/coach/disclaimer-status/${userId}`);
      return response.data;
    } catch (error) {
      console.error('Error getting disclaimer status:', error);
      throw error;
    }
  },

  // Consultation limits
  async getConsultationLimit(userId) {
    try {
      const response = await axios.get(`${API}/coach/consultation-limit/${userId}`);
      return response.data;
    } catch (error) {
      console.error('Error getting consultation limit:', error);
      throw error;
    }
  },

  // Session management
  async createSession(userId, title = "New Conversation") {
    try {
      const response = await axios.post(`${API}/coach/sessions?user_id=${userId}`, {
        title: title
      });
      return response.data;
    } catch (error) {
      console.error('Error creating session:', error);
      throw error;
    }
  },

  async getSessions(userId) {
    try {
      const response = await axios.get(`${API}/coach/sessions/${userId}`);
      return response.data;
    } catch (error) {
      console.error('Error getting sessions:', error);
      throw error;
    }
  },

  // Message handling
  async sendMessage(payload) {
    try {
      const response = await axios.post(`${API}/coach/message`, payload);
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },

  async getMessages(sessionId) {
    try {
      const response = await axios.get(`${API}/coach/messages/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('Error getting messages:', error);
      throw error;
    }
  },

  // Search functionality
  async searchHistory(userId, query) {
    try {
      const response = await axios.get(`${API}/coach/search/${userId}?query=${encodeURIComponent(query)}`);
      return response.data;
    } catch (error) {
      console.error('Error searching history:', error);
      throw error;
    }
  }
};

// Mock AI response generator for preview environment
const generateMockAIResponse = (messageText) => {
  const responses = [
    "Based on your diabetes management needs, I recommend focusing on low-glycemic foods. Here are some meal suggestions:\n\n**Breakfast:**\n- Greek yogurt with berries and nuts\n- Oatmeal with cinnamon and almonds\n- Vegetable omelet with whole grain toast\n\n**Lunch:**\n- Grilled chicken salad with olive oil dressing\n- Quinoa bowl with roasted vegetables\n- Lentil soup with a side of mixed greens\n\n**Dinner:**\n- Baked salmon with steamed broccoli\n- Turkey and vegetable stir-fry\n- Lean beef with roasted sweet potato\n\nRemember to monitor your blood sugar levels and consult with your healthcare provider.",
    
    "For restaurant dining with diabetes, here are some tips:\n\n**What to Look For:**\n- Grilled, baked, or steamed options\n- Salads with dressing on the side\n- Lean proteins like fish, chicken, or tofu\n- Vegetable-based dishes\n- Whole grain options when available\n\n**What to Avoid:**\n- Fried foods\n- Sugary sauces and dressings\n- Large portion sizes\n- Refined carbohydrates\n\n**Questions to Ask:**\n- Can you prepare this without added sugar?\n- Is this grilled or fried?\n- Can I substitute vegetables for the starch?\n\nWould you like specific restaurant recommendations in your area?",
    
    "Here's a diabetes-friendly meal plan for the week:\n\n**Monday:**\nBreakfast: Scrambled eggs with spinach\nLunch: Chicken and vegetable soup\nDinner: Grilled fish with asparagus\n\n**Tuesday:**\nBreakfast: Greek yogurt parfait\nLunch: Turkey wrap with whole wheat tortilla\nDinner: Lean beef stir-fry\n\n**Wednesday:**\nBreakfast: Oatmeal with nuts\nLunch: Quinoa salad\nDinner: Baked chicken with green beans\n\nThis plan focuses on balanced nutrition, portion control, and blood sugar management. Each meal includes protein, healthy fats, and complex carbohydrates.",
    
    "Great question about managing blood sugar! Here are some key strategies:\n\n**Timing:**\n- Eat regular meals every 3-4 hours\n- Don't skip meals\n- Consider smaller, more frequent meals\n\n**Food Choices:**\n- Choose complex carbohydrates over simple sugars\n- Include protein with each meal\n- Add healthy fats like avocado, nuts, or olive oil\n- Fill half your plate with non-starchy vegetables\n\n**Monitoring:**\n- Check blood sugar as recommended by your doctor\n- Keep a food diary to identify patterns\n- Stay hydrated with water\n\n**Exercise:**\n- Take a short walk after meals\n- Aim for 150 minutes of moderate activity per week\n\nAlways consult with your healthcare team for personalized advice!"
  ];
  
  // Simple keyword matching to provide relevant responses
  const lowerMessage = messageText.toLowerCase();
  
  if (lowerMessage.includes('restaurant') || lowerMessage.includes('dining')) {
    return responses[1];
  } else if (lowerMessage.includes('meal plan') || lowerMessage.includes('weekly')) {
    return responses[2];
  } else if (lowerMessage.includes('blood sugar') || lowerMessage.includes('glucose')) {
    return responses[3];
  } else {
    return responses[0];
  }
};

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
      // FIXED: Check if this is a real profile update from database vs demo profile creation
      // Demo users and new users should always create via POST, not update via PUT
      const isDemoUser = existingProfile?.email?.includes('@demo.nutritame.com') || 
                        existingProfile?.is_demo_user === true;
      const isRealProfileUpdate = existingProfile?.id && 
                                 existingProfile?.diabetes_type && 
                                 !isDemoUser && 
                                 existingProfile?.created_at; // Indicates it came from database
      
      if (isRealProfileUpdate) {
        console.log(`Updating existing profile with ID: ${existingProfile.id}`);
        response = await axios.put(`${API}/users/${existingProfile.id}`, profileData);
      } else {
        console.log('Creating new profile (demo user or new user)');
        // Create new profile via backend API for demo users and new users
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
const RestaurantSearch = ({ userProfile, onRestaurantSelect, authToken }) => {
  const [searchLocation, setSearchLocation] = useState("");
  const [searchRadius, setSearchRadius] = useState(2000);
  const [searchKeyword, setSearchKeyword] = useState("");
  const [restaurants, setRestaurants] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
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

  const searchRestaurants = async (lat, lng, searchRadius = 5000, keyword = '') => {
    setLoading(true);
    setError(null);
    
    try {
      // Mock restaurant data for preview environment
      const mockRestaurants = [
        {
          place_id: 'demo_restaurant_1',
          name: 'Healthy Harvest Cafe',
          address: '123 Wellness Blvd, Demo City',
          latitude: lat + 0.001,
          longitude: lng + 0.001,
          rating: 4.5,
          price_level: 2,
          phone_number: '(555) 123-4567',
          website: 'https://healthyharvest.demo',
          types: ['restaurant', 'healthy_food', 'cafe'],
          diabetic_friendly: true,
          opening_hours: {
            open_now: true,
            weekday_text: [
              'Monday: 7:00 AM – 8:00 PM',
              'Tuesday: 7:00 AM – 8:00 PM',
              'Wednesday: 7:00 AM – 8:00 PM',
              'Thursday: 7:00 AM – 8:00 PM',
              'Friday: 7:00 AM – 9:00 PM',
              'Saturday: 8:00 AM – 9:00 PM',
              'Sunday: 8:00 AM – 7:00 PM'
            ]
          },
          description: 'Farm-to-table restaurant specializing in diabetic-friendly meals with detailed nutrition information.',
          special_features: ['Carb counts on menu', 'Portion control options', 'Sugar-free desserts']
        },
        {
          place_id: 'demo_restaurant_2',
          name: 'Mediterranean Garden',
          address: '456 Olive Street, Demo City',
          latitude: lat - 0.002,
          longitude: lng + 0.003,
          rating: 4.7,
          price_level: 3,
          phone_number: '(555) 234-5678',
          website: 'https://medgarden.demo',
          types: ['restaurant', 'mediterranean', 'healthy'],
          diabetic_friendly: true,
          opening_hours: {
            open_now: true,
            weekday_text: [
              'Monday: 11:00 AM – 10:00 PM',
              'Tuesday: 11:00 AM – 10:00 PM',
              'Wednesday: 11:00 AM – 10:00 PM',
              'Thursday: 11:00 AM – 10:00 PM',
              'Friday: 11:00 AM – 11:00 PM',
              'Saturday: 11:00 AM – 11:00 PM',
              'Sunday: 12:00 PM – 9:00 PM'
            ]
          },
          description: 'Authentic Mediterranean cuisine with heart-healthy options and customizable portions.',
          special_features: ['Grilled proteins', 'Fresh vegetables', 'Whole grain options']
        },
        {
          place_id: 'demo_restaurant_3',
          name: 'Green Leaf Bistro',
          address: '789 Nutrition Ave, Demo City',
          latitude: lat + 0.003,
          longitude: lng - 0.001,
          rating: 4.3,
          price_level: 2,
          phone_number: '(555) 345-6789',
          website: 'https://greenleaf.demo',
          types: ['restaurant', 'organic', 'vegetarian'],
          diabetic_friendly: true,
          opening_hours: {
            open_now: false,
            weekday_text: [
              'Monday: 8:00 AM – 6:00 PM',
              'Tuesday: 8:00 AM – 6:00 PM',
              'Wednesday: 8:00 AM – 6:00 PM',
              'Thursday: 8:00 AM – 6:00 PM',
              'Friday: 8:00 AM – 7:00 PM',
              'Saturday: 9:00 AM – 7:00 PM',
              'Sunday: Closed'
            ]
          },
          description: 'Organic cafe with extensive salad bar and build-your-own bowl options.',
          special_features: ['Organic ingredients', 'Customizable meals', 'Nutrition calculator']
        }
      ];
      
      // Filter by keyword if provided
      let filteredRestaurants = mockRestaurants;
      if (keyword) {
        const keywordLower = keyword.toLowerCase();
        filteredRestaurants = mockRestaurants.filter(restaurant => 
          restaurant.name.toLowerCase().includes(keywordLower) ||
          restaurant.description.toLowerCase().includes(keywordLower) ||
          restaurant.types.some(type => type.toLowerCase().includes(keywordLower))
        );
      }
      
      setRestaurants(filteredRestaurants);
      if (filteredRestaurants.length > 0) {
        setSearchCenter({ latitude: filteredRestaurants[0].latitude, longitude: filteredRestaurants[0].longitude });
      }
      
    } catch (error) {
      console.error('Restaurant search error:', error);
      setError('Failed to search restaurants. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleManualSearch = async () => {
    if (!searchLocation.trim()) {
      setError('Please enter a location');
      return;
    }
    
    setLoading(true);
    try {
      // Mock coordinates for demo (defaulting to Dallas, TX area)
      const mockCoordinates = {
        latitude: 32.7767,
        longitude: -96.7970
      };
      
      const mockRestaurants = [
        {
          place_id: 'demo_location_1',
          name: 'Local Healthy Eats',
          address: `${searchLocation} Area`,
          latitude: mockCoordinates.latitude + 0.001,
          longitude: mockCoordinates.longitude + 0.001,
          rating: 4.3,
          price_level: 2,
          types: ['restaurant', 'healthy'],
          diabetic_friendly: true,
          description: 'Local restaurant with diabetic-friendly options',
          special_features: ['Low-carb menu', 'Portion control']
        },
        {
          place_id: 'demo_location_2',
          name: 'Nutrition Corner',
          address: `${searchLocation} Downtown`,
          latitude: mockCoordinates.latitude - 0.001,
          longitude: mockCoordinates.longitude + 0.002,
          rating: 4.6,
          price_level: 2,
          types: ['restaurant', 'healthy', 'organic'],
          diabetic_friendly: true,
          description: 'Organic meals with detailed nutrition information',
          special_features: ['Macro tracking', 'Diabetic-friendly desserts']
        }
      ];
      
      setRestaurants(mockRestaurants);
      setSearchCenter({ latitude: mockCoordinates.latitude, longitude: mockCoordinates.longitude });
      
    } catch (error) {
      console.error('Location search error:', error);
      setError('Failed to search by location. Please try again.');
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
const ShoppingListView = ({ userProfile, shoppingLists, setShoppingLists }) => {
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (shoppingLists.length === 0) {
      loadShoppingLists();
    }
  }, []);

  const loadShoppingLists = async () => {
    try {
      // Mock shopping lists for preview environment
      const mockShoppingLists = [
        {
          id: 'sample_list_1',
          name: 'Demo Shopping List',
          created_date: new Date().toISOString().split('T')[0],
          items: [
            { name: 'Greek yogurt (plain)', category: 'proteins', quantity: '32 oz', checked: false },
            { name: 'Spinach (fresh)', category: 'produce', quantity: '1 bag', checked: false },
            { name: 'Salmon fillets', category: 'proteins', quantity: '1 lb', checked: true },
            { name: 'Quinoa', category: 'pantry', quantity: '1 bag', checked: false },
            { name: 'Mixed berries', category: 'produce', quantity: '1 container', checked: false }
          ]
        }
      ];
      setShoppingLists(mockShoppingLists);
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
                <span>{list.name}</span>
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
                              {item.name}
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
const Dashboard = ({ userProfile, onBack, demoMode, authToken, shoppingLists, setShoppingLists }) => {
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

  // AI Health Coach State
  const [aiCoachFeatureFlags, setAiCoachFeatureFlags] = useState(null);
  const [aiCoachDisclaimerAccepted, setAiCoachDisclaimerAccepted] = useState(false);
  const [showAiCoachDisclaimer, setShowAiCoachDisclaimer] = useState(false);
  const [consultationLimit, setConsultationLimit] = useState(null);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [aiCoachSessions, setAiCoachSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [showSessionHistory, setShowSessionHistory] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState(null);
  const [showSearchResults, setShowSearchResults] = useState(false);

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

  // =============================================
  // AI HEALTH COACH FUNCTIONS
  // =============================================

  // Initialize AI Health Coach
  useEffect(() => {
    const initializeAiCoach = async () => {
      try {
        // Get feature flags
        const flags = await aiCoachService.getFeatureFlags();
        setAiCoachFeatureFlags(flags);

        // Check if user has accepted disclaimer
        if (userProfile?.id) {
          const disclaimerStatus = await aiCoachService.getDisclaimerStatus(userProfile.id);
          setAiCoachDisclaimerAccepted(disclaimerStatus.disclaimer_accepted);

          // Get consultation limit
          const limitInfo = await aiCoachService.getConsultationLimit(userProfile.id);
          setConsultationLimit(limitInfo);

          // Load user sessions
          const sessions = await aiCoachService.getSessions(userProfile.id);
          setAiCoachSessions(sessions);
        }
      } catch (error) {
        console.error('Error initializing AI Health Coach:', error);
      }
    };

    if (userProfile) {
      initializeAiCoach();
    }
  }, [userProfile]);

  // Handle AI Health Coach disclaimer acceptance
  const handleAiCoachDisclaimerAccept = async () => {
    try {
      if (!userProfile?.id) {
        toast.error("User profile required");
        return;
      }

      await aiCoachService.acceptDisclaimer(userProfile.id);
      setAiCoachDisclaimerAccepted(true);
      setShowAiCoachDisclaimer(false);
      toast.success("AI Health Coach disclaimer accepted");

      // Refresh consultation limit after accepting disclaimer
      const limitInfo = await aiCoachService.getConsultationLimit(userProfile.id);
      setConsultationLimit(limitInfo);
    } catch (error) {
      console.error('Error accepting AI Coach disclaimer:', error);
      toast.error("Failed to accept disclaimer");
    }
  };

  // Create new AI Coach session
  const createAiCoachSession = async (title = "New Conversation") => {
    try {
      if (!userProfile?.id) {
        toast.error("User profile required");
        return;
      }

      const session = await aiCoachService.createSession(userProfile.id, title);
      setCurrentSessionId(session.id);
      setAiCoachSessions(prev => [session, ...prev]);
      
      // Clear current messages and start fresh
      setMessages([{
        id: 'welcome-' + Date.now(),
        message: `Hi! I'm your AI health coach. I can help you with meal planning, restaurant recommendations, and nutrition analysis. What would you like to explore today?`,
        response: '',
        isWelcome: true
      }]);
      
      return session;
    } catch (error) {
      console.error('Error creating AI Coach session:', error);
      toast.error("Failed to create session");
      return null;
    }
  };

  // Send message to AI Health Coach
  const sendAiCoachMessage = async (messageText) => {
    try {
      if (!userProfile?.id) {
        toast.error("User profile required");
        return;
      }

      // Check if user has accepted disclaimer
      if (!aiCoachDisclaimerAccepted) {
        setShowAiCoachDisclaimer(true);
        return;
      }

      // Check consultation limits
      if (consultationLimit && !consultationLimit.can_use) {
        setShowUpgradeModal(true);
        return;
      }

      // Create session if doesn't exist
      let sessionId = currentSessionId;
      if (!sessionId) {
        const session = await createAiCoachSession();
        if (!session) return;
        sessionId = session.id;
      }

      // Send message to backend AI
      const response = await aiCoachService.sendMessage(sessionId, messageText);
      
      // Check if consultation limit reached
      if (response.error === 'consultation_limit_reached') {
        setShowUpgradeModal(true);
        toast.error("Monthly consultation limit reached");
        return;
      }

      // Update consultation limit
      const limitInfo = await aiCoachService.getConsultationLimit(userProfile.id);
      setConsultationLimit(limitInfo);

      return response;
    } catch (error) {
      console.error('Error sending AI Coach message:', error);
      throw error;
    }
  };

  // Search AI Coach history
  const searchAiCoachHistory = async () => {
    try {
      if (!userProfile?.id || !searchQuery.trim()) {
        return;
      }

      const results = await aiCoachService.searchHistory(userProfile.id, searchQuery);
      setSearchResults(results);
      setShowSearchResults(true);
    } catch (error) {
      console.error('Error searching AI Coach history:', error);
      toast.error("Failed to search history");
    }
  };

  // Load AI Coach session
  const loadAiCoachSession = async (session) => {
    try {
      const messages = await aiCoachService.getMessages(session.id);
      
      // Convert AI Coach messages to UI format
      const uiMessages = messages.map(msg => ({
        id: msg.id,
        message: msg.role === 'user' ? msg.text : '',
        response: msg.role === 'assistant' ? msg.text : '',
        isUser: msg.role === 'user',
        timestamp: msg.created_at
      }));

      // Add welcome message if needed
      if (uiMessages.length === 0) {
        uiMessages.unshift({
          id: 'welcome-' + Date.now(),
          message: `Hi! I'm your AI health coach. I can help you with meal planning, restaurant recommendations, and nutrition analysis. What would you like to explore today?`,
          response: '',
          isWelcome: true
        });
      }

      setMessages(uiMessages);
      setCurrentSessionId(session.id);
      setShowSessionHistory(false);
      toast.success(`Loaded session: ${session.title}`);
    } catch (error) {
      console.error('Error loading AI Coach session:', error);
      toast.error("Failed to load session");
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
      const response = await axios.get(`${API}/chat/${userProfile.id}`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });
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
      // Mock shopping list generation for preview environment
      const mockShoppingList = {
        id: 'shopping_' + Math.random().toString(36).substr(2, 9),
        name: 'Weekly Meal Plan Shopping List',
        created_date: new Date().toISOString().split('T')[0],
        items: [
          // Produce
          { name: 'Spinach (fresh bag)', category: 'produce', quantity: '1 bag', checked: false },
          { name: 'Broccoli crowns', category: 'produce', quantity: '2 lbs', checked: false },
          { name: 'Mixed berries', category: 'produce', quantity: '1 container', checked: false },
          { name: 'Avocados', category: 'produce', quantity: '3 count', checked: false },
          { name: 'Bell peppers (mixed)', category: 'produce', quantity: '3 count', checked: false },
          
          // Proteins
          { name: 'Salmon fillets', category: 'proteins', quantity: '1 lb', checked: false },
          { name: 'Chicken breast', category: 'proteins', quantity: '2 lbs', checked: false },
          { name: 'Greek yogurt (plain)', category: 'proteins', quantity: '32 oz container', checked: false },
          { name: 'Eggs (large)', category: 'proteins', quantity: '1 dozen', checked: false },
          { name: 'Lean ground turkey', category: 'proteins', quantity: '1 lb', checked: false },
          
          // Pantry
          { name: 'Quinoa', category: 'pantry', quantity: '1 bag', checked: false },
          { name: 'Brown rice', category: 'pantry', quantity: '2 lb bag', checked: false },
          { name: 'Olive oil (extra virgin)', category: 'pantry', quantity: '1 bottle', checked: false },
          { name: 'Almonds (raw)', category: 'pantry', quantity: '1 bag', checked: false },
          { name: 'Whole grain bread', category: 'pantry', quantity: '1 loaf', checked: false },
          
          // Frozen
          { name: 'Frozen mixed vegetables', category: 'frozen', quantity: '2 bags', checked: false },
          { name: 'Frozen wild-caught fish', category: 'frozen', quantity: '1 bag', checked: false }
        ]
      };

      // Add to shopping lists state
      setShoppingLists(prev => [...prev, mockShoppingList]);
      
      toast.success("Shopping list created successfully!");
      setActiveTab("shopping");
      setShowShoppingListButton(false);
    } catch (error) {
      console.error("Shopping list generation error:", error);
      toast.error("Failed to create shopping list");
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async (messageText = currentMessage) => {
    if (!messageText.trim() || loading) return;

    console.log('Sending message:', messageText);
    setCurrentMessage("");
    setLoading(true);

    // Add user message to UI
    const tempUserMsg = {
      id: Date.now(),
      message: messageText,
      response: '',
      isUser: true
    };
    setMessages(prev => [...prev, tempUserMsg]);

    try {
      console.log('Making API call to AI Health Coach...');
      
      // Use real AI Health Coach integration
      const aiResponse = await sendAiCoachMessage(messageText);
      
      if (!aiResponse) {
        // If no response (due to disclaimer or limit), remove user message
        setMessages(prev => prev.slice(0, -1));
        return;
      }

      // Extract AI response text
      const aiResponseText = aiResponse.ai_response?.text || "I apologize, but I couldn't generate a response. Please try again.";
      
      // Clean up AI response - remove markdown formatting
      const cleanedResponse = aiResponseText
        .replace(/\*\*(.*?)\*\*/g, '$1')  // Remove **bold**
        .replace(/\*(.*?)\*/g, '$1')     // Remove *italic*
        .replace(/#{1,6}\s/g, '')        // Remove # headers
        .replace(/^\s*[-*+]\s/gm, '- ') // Normalize bullet points
        .trim();

      // Check if response contains meal planning and show shopping list button
      const containsMealPlan = cleanedResponse.toLowerCase().includes('meal') && 
                              (cleanedResponse.toLowerCase().includes('plan') || 
                               cleanedResponse.toLowerCase().includes('breakfast') || 
                               cleanedResponse.toLowerCase().includes('lunch') || 
                               cleanedResponse.toLowerCase().includes('dinner'));
      
      if (containsMealPlan) {
        setLastMealPlan(cleanedResponse);
        setShowShoppingListButton(true);
      }

      // Add AI response to UI
      setMessages(prev => [...prev.slice(0, -1), {
        id: `ai-${Date.now()}`,
        message: messageText,
        response: cleanedResponse,
        isUser: false
      }]);

      toast.success("Response received!");
    } catch (error) {
      console.error("Chat error:", error);
      toast.error("Failed to get AI response. Please try again.");
      setMessages(prev => prev.slice(0, -1)); // Remove failed message
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleRestaurantSelect = async (restaurant) => {
    setSelectedRestaurant(restaurant);
    setActiveTab("chat");
    
    // Send restaurant analysis message to AI
    const restaurantMessage = `I'm interested in eating at ${restaurant.name} located at ${restaurant.address}. Can you help me understand what diabetic-friendly options might be available there and give me tips for ordering healthy meals?`;
    await sendMessage(restaurantMessage);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white/90 backdrop-blur-sm border-b border-gray-200/50 shadow-sm p-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button variant="outline" onClick={onBack} className="hover:bg-emerald-50 hover:border-emerald-300 transition-all duration-300">
              ← Back to Profile
            </Button>
            <div className="flex items-center gap-2">
              <ChefHat className="h-6 w-6 text-emerald-600" />
              <h1 className="text-xl font-semibold bg-gradient-to-r from-emerald-600 to-blue-600 bg-clip-text text-transparent">NutriTame Dashboard</h1>
            </div>
          </div>
          <div className="text-sm text-gray-600">
            {userProfile.diabetes_type && (
              <Badge variant="secondary" className="capitalize bg-gradient-to-r from-emerald-100 to-blue-100 text-emerald-700 border-emerald-200">
                {userProfile.diabetes_type.replace('_', ' ')}
              </Badge>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto p-4">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 bg-white/90 backdrop-blur-sm shadow-lg border border-gray-200/50">
            <TabsTrigger 
              value="chat" 
              className={`flex items-center gap-2 transition-all duration-300 ${
                activeTab === 'chat' 
                  ? 'bg-gradient-to-r from-emerald-500 to-blue-500 text-white shadow-lg' 
                  : 'hover:bg-gradient-to-r hover:from-emerald-50 hover:to-blue-50 hover:text-emerald-700'
              }`}
            >
              <MessageCircle className="h-4 w-4" />
              AI Health Coach
            </TabsTrigger>
            <TabsTrigger 
              value="restaurants" 
              className={`flex items-center gap-2 transition-all duration-300 ${
                activeTab === 'restaurants' 
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg' 
                  : 'hover:bg-gradient-to-r hover:from-purple-50 hover:to-pink-50 hover:text-purple-700'
              }`}
            >
              <MapPin className="h-4 w-4" />
              Restaurant Search
            </TabsTrigger>
            <TabsTrigger 
              value="shopping" 
              className={`flex items-center gap-2 transition-all duration-300 ${
                activeTab === 'shopping' 
                  ? 'bg-gradient-to-r from-orange-500 to-red-500 text-white shadow-lg' 
                  : 'hover:bg-gradient-to-r hover:from-orange-50 hover:to-red-50 hover:text-orange-700'
              }`}
            >
              <ShoppingCart className="h-4 w-4" />
              Shopping Lists
            </TabsTrigger>
          </TabsList>

          <TabsContent value="chat" className="space-y-4">
            {/* Chat Controls Header */}
            <div className="flex items-center justify-between bg-white/90 backdrop-blur-sm rounded-lg p-4 shadow-sm border border-gray-200/50">
              <div className="flex items-center gap-2">
                <ChefHat className="h-6 w-6 text-emerald-600" />
                <h2 className="text-lg font-semibold text-gray-800">
                  AI Health Coach {currentChatId && <span className="text-sm text-gray-500">(Saved)</span>}
                </h2>
              </div>
              
              <div className="flex items-center gap-2">
                {/* New AI Coach Session Button */}
                <button
                  onClick={() => createAiCoachSession()}
                  className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50 rounded-lg transition-all duration-200"
                  title="Start new AI Coach session"
                >
                  <MessageSquarePlus className="h-4 w-4" />
                  New Session
                </button>
                
                {/* Session History Button */}
                <button
                  onClick={() => setShowSessionHistory(!showSessionHistory)}
                  className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-all duration-200"
                  title="View session history"
                >
                  <BookOpen className="h-4 w-4" />
                  Sessions ({aiCoachSessions.length})
                </button>
                
                {/* Search Button */}
                <div className="flex items-center gap-1">
                  <Input
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search history..."
                    className="w-32 h-8 text-sm"
                    onKeyPress={(e) => e.key === 'Enter' && searchAiCoachHistory()}
                  />
                  <button
                    onClick={searchAiCoachHistory}
                    disabled={!searchQuery.trim()}
                    className="inline-flex items-center gap-1 px-3 py-2 text-sm font-medium text-purple-600 hover:text-purple-700 hover:bg-purple-50 rounded-lg transition-all duration-200 disabled:opacity-50"
                    title="Search conversations"
                  >
                    <Search className="h-4 w-4" />
                  </button>
                </div>
                
                {/* Legacy Favorites Button */}
                <button
                  onClick={loadFavorites}
                  className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-pink-600 hover:text-pink-700 hover:bg-pink-50 rounded-lg transition-all duration-200"
                  title="View favorite recipes"
                >
                  <Heart className="h-4 w-4" />
                  Favorites ({favoriteRecipes.length})
                </button>
              </div>
            </div>

            {/* Demo Countdown Timer - Only show in demo mode */}
            {demoMode && (
              <DemoCountdownTimer 
                durationMinutes={30}
                onTimeExpired={() => {
                  // Handle when demo time expires
                  const handleExpiry = () => {
                    alert('🕐 Your 30-minute demo session has ended! You\'ve experienced all the premium features of NutriTame. Click "Extend Demo" to continue exploring, or "New Demo" to restart with a fresh 30-minute session.');
                  };
                  handleExpiry();
                }}
                className="mb-4"
              />
            )}

            {/* AI Health Coach Disclaimer Modal */}
            {showAiCoachDisclaimer && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <Card className="w-full max-w-md mx-4">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <ChefHat className="h-5 w-5 text-emerald-600" />
                      AI Health Coach Disclaimer
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <p className="text-sm text-gray-700">
                        <strong>Not a medical device.</strong> The AI Health Coach provides general nutrition guidance only and is not a substitute for professional medical advice. Always consult your healthcare provider.
                      </p>
                    </div>
                    <div className="flex gap-3">
                      <Button 
                        onClick={handleAiCoachDisclaimerAccept}
                        className="flex-1 bg-emerald-600 hover:bg-emerald-700"
                      >
                        Accept & Continue
                      </Button>
                      <Button 
                        variant="outline" 
                        onClick={() => setShowAiCoachDisclaimer(false)}
                        className="flex-1"
                      >
                        Cancel
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Consultation Limit Badge & Upgrade Modal */}
            {consultationLimit && (
              <div className="mb-4">
                <div className="bg-gradient-to-r from-blue-50 to-emerald-50 border border-blue-200 rounded-lg p-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Crown className="h-4 w-4 text-blue-600" />
                      <span className="text-sm font-medium text-gray-700">
                        {consultationLimit.plan === 'premium' ? (
                          "Premium Plan: Unlimited consultations"
                        ) : (
                          `Standard Plan: ${consultationLimit.current_count}/${consultationLimit.limit} consultations used this month`
                        )}
                      </span>
                    </div>
                    {consultationLimit.plan === 'standard' && (
                      <Badge variant={consultationLimit.remaining > 3 ? "default" : "destructive"}>
                        {consultationLimit.remaining} remaining
                      </Badge>
                    )}
                  </div>
                  {consultationLimit.plan === 'standard' && consultationLimit.remaining <= 3 && (
                    <p className="text-xs text-gray-600 mt-2">
                      Running low on consultations. Upgrade to Premium for unlimited access!
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Upgrade to Premium Modal */}
            {showUpgradeModal && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <Card className="w-full max-w-md mx-4">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Crown className="h-5 w-5 text-yellow-600" />
                      Upgrade to Premium
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="text-center">
                      <p className="text-gray-700 mb-4">
                        You've reached your monthly consultation limit. Upgrade to Premium for unlimited AI Health Coach access.
                      </p>
                      <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-lg p-4 mb-4">
                        <h4 className="font-semibold text-gray-800 mb-2">Premium Features:</h4>
                        <ul className="text-sm text-gray-600 space-y-1">
                          <li>• Unlimited AI Health Coach consultations</li>
                          <li>• Priority support</li>
                          <li>• Advanced meal planning</li>
                          <li>• Personalized recommendations</li>
                        </ul>
                      </div>
                    </div>
                    <div className="flex gap-3">
                      <Button 
                        onClick={() => toast.info("Upgrade functionality coming soon!")}
                        className="flex-1 bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600"
                      >
                        Upgrade Now
                      </Button>
                      <Button 
                        variant="outline" 
                        onClick={() => setShowUpgradeModal(false)}
                        className="flex-1"
                      >
                        Maybe Later
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* AI Coach Session History Panel */}
            {showSessionHistory && (
              <Card className="mb-4">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BookOpen className="h-5 w-5 text-emerald-600" />
                    AI Coach Sessions
                  </CardTitle>
                  <CardDescription>
                    Your previous AI Health Coach conversations
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {aiCoachSessions.length === 0 ? (
                    <p className="text-gray-500 text-center py-4">No sessions yet. Start your first AI Health Coach conversation!</p>
                  ) : (
                    <div className="space-y-2 max-h-60 overflow-y-auto">
                      {aiCoachSessions.map((session) => (
                        <div
                          key={session.id}
                          className="flex items-center justify-between p-3 bg-emerald-50 rounded-lg hover:bg-emerald-100 cursor-pointer transition-colors group"
                          onClick={() => loadAiCoachSession(session)}
                        >
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-gray-900 truncate">
                              {session.title}
                            </p>
                            <p className="text-sm text-gray-500">
                              {new Date(session.created_at).toLocaleDateString()}
                            </p>
                          </div>
                          <ChevronDown className="h-4 w-4 text-gray-400 transform -rotate-90" />
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Search Results Panel */}
            {showSearchResults && searchResults && (
              <Card className="mb-4">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Search className="h-5 w-5 text-purple-600" />
                    Search Results for "{searchQuery}"
                  </CardTitle>
                  <CardDescription>
                    Found {searchResults.results?.length || 0} sessions with matching content
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {!searchResults.results || searchResults.results.length === 0 ? (
                    <p className="text-gray-500 text-center py-4">No results found for your search.</p>
                  ) : (
                    <div className="space-y-3 max-h-80 overflow-y-auto">
                      {searchResults.results.map((result) => (
                        <div
                          key={result.session.id}
                          className="p-4 bg-purple-50 rounded-lg border border-purple-100 group cursor-pointer"
                          onClick={() => loadAiCoachSession(result.session)}
                        >
                          <div className="flex items-start justify-between mb-2">
                            <h4 className="font-medium text-gray-900 text-sm">
                              {result.session.title}
                            </h4>
                            <Badge variant="outline" className="text-xs">
                              {result.messages.length} matches
                            </Badge>
                          </div>
                          <p className="text-xs text-gray-500 mb-2">
                            {new Date(result.session.created_at).toLocaleDateString()}
                          </p>
                          {result.messages.slice(0, 2).map((msg) => (
                            <div key={msg.id} className="text-sm text-gray-700 mb-1 truncate">
                              <span className="font-medium">{msg.role}:</span> {msg.text.substring(0, 100)}...
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="mt-3 pt-3 border-t">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => setShowSearchResults(false)}
                      className="w-full"
                    >
                      Close Search Results
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Saved Chats Panel */}
            {showSavedChats && (
              <Card className="mb-4">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FolderOpen className="h-5 w-5 text-purple-600" />
                    Saved Chats
                  </CardTitle>
                  <CardDescription>
                    Load a previously saved conversation
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {savedChats.length === 0 ? (
                    <p className="text-gray-500 text-center py-4">No saved chats yet. Start a conversation and save it!</p>
                  ) : (
                    <div className="space-y-2 max-h-60 overflow-y-auto">
                      {savedChats.map((chat) => (
                        <div
                          key={chat.id}
                          className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors group"
                          onClick={() => loadSavedChat(chat)}
                        >
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-gray-900 truncate">
                              {chat.title}
                            </p>
                            <p className="text-sm text-gray-500">
                              {new Date(chat.timestamp).toLocaleDateString()} • {chat.messages.length} messages
                            </p>
                          </div>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={(e) => deleteSavedChat(chat.id, e)}
                              className={`p-1 rounded-lg transition-all duration-200 opacity-0 group-hover:opacity-100 ${
                                deleteConfirmId === chat.id 
                                  ? 'bg-red-100 text-red-700 hover:bg-red-200' 
                                  : 'text-gray-400 hover:text-red-600 hover:bg-red-50'
                              }`}
                              title={deleteConfirmId === chat.id ? "Click again to confirm delete" : "Delete chat"}
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                            <ChevronDown className="h-4 w-4 text-gray-400 transform -rotate-90" />
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Favorites Panel */}
            {showFavorites && (
              <Card className="mb-4">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Heart className="h-5 w-5 text-pink-600" />
                    Favorite Recipes & Meal Plans
                  </CardTitle>
                  <CardDescription>
                    Your saved recipes and meal recommendations
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {favoriteRecipes.length === 0 ? (
                    <p className="text-gray-500 text-center py-4">No favorites yet. Use the ♡ button on AI responses to save recipes!</p>
                  ) : (
                    <div className="space-y-3 max-h-80 overflow-y-auto">
                      {favoriteRecipes.map((favorite) => (
                        <div
                          key={favorite.id}
                          className="p-4 bg-gradient-to-r from-pink-50 to-purple-50 rounded-lg border border-pink-100 group"
                        >
                          <div className="flex items-start justify-between mb-2">
                            <h4 className="font-medium text-gray-900 text-sm">
                              {favorite.title}
                            </h4>
                            <button
                              onClick={(e) => deleteFavorite(favorite.id, e)}
                              className="opacity-0 group-hover:opacity-100 p-1 rounded-lg text-gray-400 hover:text-red-600 hover:bg-red-50 transition-all duration-200"
                              title="Remove from favorites"
                            >
                              <Trash2 className="h-3 w-3" />
                            </button>
                          </div>
                          <div className="text-sm text-gray-700 mb-2 max-h-20 overflow-y-auto">
                            {favorite.content.substring(0, 200)}...
                          </div>
                          <p className="text-xs text-gray-500">
                            Saved on {new Date(favorite.timestamp).toLocaleDateString()}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Chat Interface - Larger Response Window */}
            <div className="h-[calc(100vh-200px)] flex flex-col">
              {/* Messages Container - Larger Space for Responses */}
              <div 
                ref={messagesContainerRef}
                className="flex-1 space-y-4 overflow-y-auto pr-2 pb-6"
                style={{ scrollBehavior: 'smooth' }}
              >
                {/* Inline AI Health Coach Disclaimer Banner */}
                {messages.length > 1 && !messages.find(m => m.isWelcome) && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 rounded-full bg-yellow-100 flex items-center justify-center">
                        <span className="text-yellow-600 text-xs font-bold">!</span>
                      </div>
                      <p className="text-sm text-yellow-800">
                        <strong>Not a medical device.</strong> For diagnosis or treatment, consult a professional.
                      </p>
                    </div>
                  </div>
                )}

                {messages.map((msg, index) => (
                  <div key={msg.id || index} className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'} message-enter`}>
                    <Card className={`max-w-[85%] transition-all duration-300 group ${
                      msg.isUser 
                        ? 'bg-gradient-to-r from-emerald-600 to-blue-600 text-white shadow-lg' 
                        : msg.isWelcome 
                          ? 'bg-gradient-to-r from-emerald-50 via-blue-50 to-purple-50 border-emerald-200 shadow-lg' 
                          : 'bg-white/90 backdrop-blur-sm shadow-lg border border-gray-200/50'
                    }`}>
                      <CardContent className="p-6">
                        <div className="flex items-start gap-4">
                          {!msg.isUser && (
                            <div className="flex-shrink-0">
                              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-100 to-blue-100 flex items-center justify-center shadow-md">
                                <ChefHat className="h-5 w-5 text-emerald-600" />
                              </div>
                            </div>
                          )}
                          <div className="flex-1">
                            <div className="flex items-start justify-between">
                              <p className="whitespace-pre-wrap leading-relaxed text-base flex-1">
                                {msg.isUser ? msg.message : (msg.response || msg.message)}
                              </p>
                              {/* Add to Favorites button for AI responses */}
                              {!msg.isUser && !msg.isWelcome && (msg.response || msg.message) && (
                                <button
                                  onClick={() => addToFavorites(msg.response || msg.message, index)}
                                  className="ml-3 p-2 text-gray-400 hover:text-pink-600 hover:bg-pink-50 rounded-lg transition-all duration-200 opacity-0 group-hover:opacity-100"
                                  title="Add to favorites"
                                >
                                  <Heart className="h-4 w-4" />
                                </button>
                              )}
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                ))}
                {loading && (
                  <div className="flex justify-start">
                    <Card className="bg-white/90 backdrop-blur-sm shadow-lg border border-gray-200/50">
                      <CardContent className="p-6">
                        <div className="flex items-center gap-4">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-100 to-blue-100 flex items-center justify-center shadow-md">
                            <ChefHat className="h-5 w-5 text-emerald-600" />
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="flex space-x-1">
                              <div className="w-3 h-3 bg-gradient-to-r from-emerald-500 to-blue-500 rounded-full animate-bounce"></div>
                              <div className="w-3 h-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                              <div className="w-3 h-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                            </div>
                            <span className="text-gray-600 ml-2">AI is thinking...</span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )}
                {/* Auto-scroll anchor */}
                <div ref={messagesEndRef} />
                
                {/* Shopping List Generation - Positioned after messages */}
                {showShoppingListButton && (
                  <div className="mt-4 mb-4">
                    <Card className="bg-gradient-to-r from-orange-50 to-yellow-50 border-orange-200 shadow-md">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="p-2 bg-orange-100 rounded-full">
                              <ShoppingCart className="h-5 w-5 text-orange-600" />
                            </div>
                            <div>
                              <h4 className="font-semibold text-gray-800">Generate Shopping List</h4>
                              <p className="text-sm text-gray-600">Create a shopping list based on this meal plan</p>
                            </div>
                          </div>
                          <Button 
                            onClick={generateShoppingList}
                            disabled={loading}
                            className="bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white shadow-lg"
                          >
                            {loading ? (
                              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                            ) : (
                              <Plus className="h-4 w-4 mr-2" />
                            )}
                            Create List
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )}
              </div>

              {/* Fixed Floating Scroll Navigation Buttons */}
              {messages.length > 3 && (
                <div className="fixed bottom-24 right-6 z-50 flex flex-col gap-3">
                  {/* Back to Top Button */}
                  <button
                    onClick={scrollToTop}
                    className="bg-gradient-to-r from-emerald-500 to-blue-500 hover:from-emerald-600 hover:to-blue-600 text-white p-4 rounded-full shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-110 backdrop-blur-sm border border-white/20"
                    title="Scroll to top of conversation"
                  >
                    <ChevronUp className="h-6 w-6" />
                  </button>
                  
                  {/* Scroll to Bottom Button */}
                  <button
                    onClick={scrollToBottom}
                    className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white p-4 rounded-full shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-110 backdrop-blur-sm border border-white/20"
                    title="Scroll to latest message"
                  >
                    <ChevronDown className="h-6 w-6" />
                  </button>
                </div>
              )}

              {/* Input Area - Sticky at bottom */}
              <div className="sticky bottom-0 bg-white border-t border-gray-100 pt-4 pb-2">
                <Card className="shadow-lg bg-white border border-gray-200">
                  <CardContent className="p-4">
                  <div className="flex gap-4">
                    <Textarea
                      value={currentMessage}
                      onChange={(e) => setCurrentMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Ask about meal planning, restaurant recommendations, nutrition analysis..."
                      className="min-h-[100px] resize-none border-2 border-gray-300 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 transition-all duration-300 text-base"
                      disabled={loading}
                    />
                    <Button 
                      onClick={() => sendMessage()}
                      disabled={!currentMessage.trim() || loading}
                      className="bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700 text-white px-6 py-4 shadow-lg hover:shadow-xl transition-all duration-300 min-h-[100px]"
                    >
                      <MessageCircle className="h-5 w-5" />
                    </Button>
                  </div>
                  <div className="text-sm text-gray-600 mt-3 bg-gradient-to-r from-emerald-50 to-blue-50 px-4 py-2 rounded-full inline-block">
                    💡 Ask me about meal plans, restaurants, nutrition, or recipes with Imperial measurements (cups, lbs, oz)!
                  </div>
                </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="restaurants">
            <RestaurantSearch 
              userProfile={userProfile} 
              onRestaurantSelect={handleRestaurantSelect}
              authToken={authToken}
            />
          </TabsContent>

          <TabsContent value="shopping">
            <ShoppingListView 
              userProfile={userProfile} 
              shoppingLists={shoppingLists}
              setShoppingLists={setShoppingLists}
            />
          </TabsContent>
        </Tabs>

        {/* Footer Navigation - Independent navigation buttons */}
        <div className="fixed bottom-0 left-0 right-0 bg-white/95 backdrop-blur-md border-t border-gray-200/50 shadow-lg z-40">
          <div className="container mx-auto px-4 py-3">
            <div className="flex items-center justify-center">
              <div className="grid grid-cols-3 gap-1 w-full max-w-md bg-gradient-to-r from-emerald-50 to-blue-50 rounded-xl p-1">
                <button
                  onClick={() => setActiveTab('chat')}
                  className={`flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition-all duration-300 rounded-lg ${
                    activeTab === 'chat'
                      ? 'bg-gradient-to-r from-emerald-600 to-blue-600 text-white shadow-lg transform scale-105' 
                      : 'hover:bg-gradient-to-r hover:from-emerald-100 hover:to-blue-100 hover:text-emerald-700 text-gray-600'
                  }`}
                >
                  <ChefHat className="h-4 w-4" />
                  AI Coach
                </button>
                <button
                  onClick={() => setActiveTab('restaurants')}
                  className={`flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition-all duration-300 rounded-lg ${
                    activeTab === 'restaurants'
                      ? 'bg-gradient-to-r from-emerald-600 to-blue-600 text-white shadow-lg transform scale-105' 
                      : 'hover:bg-gradient-to-r hover:from-emerald-100 hover:to-blue-100 hover:text-emerald-700 text-gray-600'
                  }`}
                >
                  <Search className="h-4 w-4" />
                  Restaurants
                </button>
                <button
                  onClick={() => setActiveTab('shopping')}
                  className={`flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition-all duration-300 rounded-lg ${
                    activeTab === 'shopping'
                      ? 'bg-gradient-to-r from-emerald-600 to-blue-600 text-white shadow-lg transform scale-105' 
                      : 'hover:bg-gradient-to-r hover:from-emerald-100 hover:to-blue-100 hover:text-emerald-700 text-gray-600'
                  }`}
                >
                  <ShoppingCart className="h-4 w-4" />
                  Shopping
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// =============================================
// LANDING PAGE WRAPPER WITH NAVIGATION
// =============================================

const LandingPageWrapper = ({ onGetStarted }) => {
  const navigate = useNavigate();
  
  const handleNavigateToCoach = () => {
    navigate('/coach');
  };

  return (
    <LandingPage 
      onGetStarted={onGetStarted} 
      onNavigateToCoach={handleNavigateToCoach}
    />
  );
};

// =============================================
// COACH ROUTE COMPONENT
// =============================================

const CoachRoute = ({ currentUser }) => {
  console.log('🚀 CoachRoute component mounted with currentUser:', currentUser);
  
  const [featureFlags, setFeatureFlags] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Single source of truth for disclaimer acceptance with localStorage persistence
  const [ack, setAck] = useState(() => {
    const stored = localStorage.getItem('nt_coach_disclaimer_ack');
    return stored === 'true';
  });

  // State to preserve user question across disclaimer acceptance
  const [pendingQuestion, setPendingQuestion] = useState(() => {
    const stored = localStorage.getItem('nt_coach_pending_question');
    return stored || '';
  });

  useEffect(() => {
    console.log('🔍 CoachRoute useEffect started - checking feature flags...');
    
    const checkFeatureFlags = async () => {
      try {
        console.log('🔍 Fetching feature flags...');
        // Check feature flags
        const flags = await aiCoachService.getFeatureFlags();
        console.log('📋 Feature flags received:', flags);
        setFeatureFlags(flags);
      } catch (error) {
        console.error('❌ Error checking feature flags:', error);
        setFeatureFlags({ coach_enabled: false });
      } finally {
        setLoading(false);
      }
    };

    checkFeatureFlags();
  }, []);

  const handleCoachDisclaimerAccept = async () => {
    console.log('✅ Coach disclaimer accepted');
    
    try {
      // CRITICAL FIX: Use the component-scoped effectiveUser from CoachInterface
      // Don't create a new one here to avoid ID mismatch
      console.log('🎯 Recording disclaimer acceptance for currentUser:', currentUser?.id || 'null');
      console.log('🎯 Will use effectiveUser from CoachInterface component for session creation');
      
      // For now, create a consistent demo user if no currentUser exists
      const userIdForDisclaimer = currentUser?.id || `demo-${Date.now()}`;
      
      await aiCoachService.acceptDisclaimer(userIdForDisclaimer);
      console.log('✅ Backend disclaimer acceptance recorded successfully for:', userIdForDisclaimer);
      
      // Store the user ID for session creation consistency
      localStorage.setItem('nt_coach_user_id', userIdForDisclaimer);
      
      // Update frontend state and persistence
      setAck(true);
      localStorage.setItem('nt_coach_disclaimer_ack', 'true');
      
      // Update pendingQuestion state from localStorage after disclaimer acceptance
      const storedQuestion = localStorage.getItem('nt_coach_pending_question');
      if (storedQuestion) {
        console.log('🔄 Updating pendingQuestion state from localStorage:', storedQuestion);
        setPendingQuestion(storedQuestion);
      }
      
      // Show encouragement toast after disclaimer acceptance
      setTimeout(() => {
        toast.success("Thanks for confirming — remember, this is guidance only, and your healthcare provider is your best resource.");
      }, 500);
      
    } catch (error) {
      console.error('❌ Failed to record disclaimer acceptance:', error);
      // Still proceed with frontend state update for offline functionality
      setAck(true);
      localStorage.setItem('nt_coach_disclaimer_ack', 'true');
      
      toast.error('Disclaimer recorded locally. If connection issues persist, please refresh the page.');
    }
  };

  const handleCoachDisclaimerDecline = () => {
    console.log('❌ Coach disclaimer declined - redirecting to home');
    // Redirect back to home page
    window.location.href = '/';
  };

  console.log('🔄 CoachRoute render - loading:', loading, 'featureFlags:', featureFlags, 'ack:', ack);

  if (loading) {
    console.log('⏳ Rendering loading screen');
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-blue-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-emerald-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading AI Health Coach...</p>
        </div>
      </div>
    );
  }

  if (!featureFlags?.coach_enabled) {
    console.log('❌ Coach feature disabled');
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-blue-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <ChefHat className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-800 mb-2">AI Health Coach Not Available</h2>
          <p className="text-gray-600 mb-4">This feature is currently disabled.</p>
          <Button onClick={() => window.location.href = '/'}>
            Return to Home
          </Button>
        </div>
      </div>
    );
  }

  // Show disclaimer modal if not accepted
  if (!ack) {
    console.log('📋 Rendering coach disclaimer modal');
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-blue-50 to-purple-50 flex items-center justify-center">
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md mx-4">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ChefHat className="h-5 w-5 text-emerald-600" />
                AI Health Coach Disclaimer
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-sm text-gray-700">
                  <strong>Not a medical device.</strong> The AI Health Coach provides general nutrition guidance only and is not a substitute for professional medical advice. Always consult your healthcare provider.
                </p>
              </div>
              <div className="flex gap-3">
                <Button 
                  onClick={handleCoachDisclaimerAccept}
                  className="flex-1 bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700"
                >
                  Accept & Continue
                </Button>
                <Button 
                  variant="outline" 
                  onClick={handleCoachDisclaimerDecline}
                  className="flex-1"
                >
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  console.log('🎯 Rendering coach interface');
  // Render full coach interface component with pending question and current user profile
  return <CoachInterface pendingQuestion={pendingQuestion} currentUser={currentUser} />;
};

// =============================================
// COACH INTERFACE COMPONENT
// =============================================

const CoachInterface = ({ pendingQuestion, currentUser }) => {
  console.log('🎯 CoachInterface component mounted with pendingQuestion:', pendingQuestion, 'currentUser:', currentUser);
  
  // Basic AI Health Coach state
  const [messages, setMessages] = useState([]);
  
  // ZERO-FLICKER FIX: Initialize inputText directly from localStorage to prevent flicker
  const [inputText, setInputText] = useState(() => {
    const storedQuestion = localStorage.getItem('nt_coach_pending_question') || '';
    console.log(`[${performance.now().toFixed(1)}] inputText initialized from localStorage:`, storedQuestion);
    return storedQuestion;
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [consultationLimit, setConsultationLimit] = useState(null);
  const [aiCoachSessions, setAiCoachSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  // Track if user has manually edited input since mount
  const touched = useRef(false);

  // ZERO-FLICKER FIX: Only restore from pendingQuestion prop if it's different and user hasn't typed
  useEffect(() => {
    if (pendingQuestion && pendingQuestion.trim() && !touched.current && pendingQuestion !== inputText) {
      console.log(`[${performance.now().toFixed(1)}] Restoring from pendingQuestion prop:`, pendingQuestion);
      setInputText(pendingQuestion);
    }
  }, [pendingQuestion, inputText]);

  // Generate a proper user for demo/testing if no currentUser
  // Use consistent ID from localStorage if available to match disclaimer acceptance
  const storedUserId = localStorage.getItem('nt_coach_user_id');
  const effectiveUser = currentUser || { 
    id: storedUserId || `demo-${Date.now()}`, 
    plan: 'standard',
    email: 'demo@nutritame.com',
    diabetes_type: 'type2', // Default for demo
    age: 35,
    food_preferences: ['mediterranean'],
    allergies: []
  };

  // Initialize with welcome message
  useEffect(() => {
    console.log('🔧 CoachInterface mounted, setting up welcome message...');
    console.log('🔧 currentUser:', currentUser);
    console.log('🔧 effectiveUser:', effectiveUser);
    
    let welcomeMessage = "Hi! I'm your AI health coach. I can help you with meal planning, restaurant recommendations, and nutrition analysis.";
    
    // Add personalized greeting if profile is available - USE effectiveUser instead of currentUser
    if (effectiveUser && effectiveUser.diabetes_type) {
      welcomeMessage += ` I see you have ${effectiveUser.diabetes_type} - I'll provide personalized guidance based on your profile.`;
    } else {
      welcomeMessage += ` For personalized advice, make sure to complete your profile first.`;
    }
    
    welcomeMessage += ` What would you like to explore today?`;
    
    // Add debug information in development - USE effectiveUser instead of currentUser
    if (process.env.NODE_ENV === 'development' || window.location.search.includes('debug=true')) {
      welcomeMessage += `\n\n🔧 **Debug Info**: Profile: type=${effectiveUser?.diabetes_type || 'none'}, prefs=${effectiveUser?.food_preferences?.join(', ') || 'none'}, allergies=${effectiveUser?.allergies?.join(', ') || 'none'}`;
    }
    
    const welcomeMsg = {
      id: 'welcome-' + Date.now(),
      message: welcomeMessage,
      response: '',
      isWelcome: true
    };
    setMessages([welcomeMsg]);
    
    // Handle pending question if provided
    if (pendingQuestion && pendingQuestion.trim()) {
      console.log('🎯 Processing pending question:', pendingQuestion);
      setInputText(pendingQuestion);
      
      // Clear the pending question from localStorage now that we've processed it
      localStorage.removeItem('nt_coach_pending_question');
      
      // Add encouragement microcopy for restored question
      setTimeout(() => {
        toast.success("Great question! I've restored your message - just hit send when you're ready 💬");
      }, 1000);
    }
  }, [pendingQuestion, currentUser]);

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;
    
    console.log('🚀 handleSendMessage called with input:', inputText);
    console.log('🚀 effectiveUser:', effectiveUser);
    console.log('🚀 currentSessionId:', currentSessionId);
    
    const isFirstMessage = messages.length === 0 || (messages.length === 1 && messages[0].isWelcome);
    const messageCount = messages.filter(msg => msg.isUser).length;
    
    setIsLoading(true);
    const userMessage = {
      id: Date.now(),
      message: inputText,
      response: '',
      isUser: true
    };
    
    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputText;
    
    // DON'T clear input immediately - only clear after successful send
    // setInputText('');
    
    // Clear any pending question since we're sending the message
    localStorage.removeItem('nt_coach_pending_question');

    try {
      // Add encouragement for first question
      if (isFirstMessage) {
        setTimeout(() => {
          toast.success("That's a great question — curiosity is the first step toward progress.");
        }, 500);
      }
      
      // Add encouragement for multiple sessions/messages
      if (messageCount >= 3) {
        setTimeout(() => {
          toast.success("Nice work staying consistent — small steps really add up.");
        }, 1500);
      }
      
      // Create session if not exists
      let sessionId = currentSessionId;
      if (!sessionId) {
        console.log('🎯 Creating new session for user:', effectiveUser.id);
        try {
          const sessionResponse = await aiCoachService.createSession(effectiveUser.id, "New Health Coach Conversation");
          sessionId = sessionResponse.id;
          setCurrentSessionId(sessionId);
          console.log('🎯 Created session:', sessionId);
        } catch (sessionError) {
          console.error('❌ Session creation failed:', sessionError);
          throw new Error(`Session creation failed: ${sessionError.message}`);
        }
      }
      
      // Prepare message payload
      const messagePayload = {
        session_id: sessionId,
        message: currentInput
      };
      
      console.log('🎯 Sending message to AI with payload:', messagePayload);
      console.log('🎯 API URL:', `/api/coach/message`);
      
      // Call real AI backend API
      const response = await aiCoachService.sendMessage(messagePayload);
      console.log('🎯 AI response received:', response);
      
      // Validate response
      if (!response) {
        throw new Error('Empty response from AI service');
      }
      
      // Create AI response message
      const aiResponseText = response.ai_response?.text || response.response || response.message;
      if (!aiResponseText) {
        console.error('❌ No response text found in:', response);
        throw new Error('No response text received from AI');
      }
      
      const aiResponse = {
        id: Date.now() + 1,
        message: '',
        response: aiResponseText,
        isUser: false
      };
      
      setMessages(prev => [...prev, aiResponse]);
      
      // Only clear input after successful send
      setInputText('');
      
      // CRITICAL FIX: Reset touched flag after successful send to allow future question restoration
      touched.current = false;
      
      setIsLoading(false);
      
      console.log('✅ Message sent successfully, AI response added, touched flag reset');
      
    } catch (error) {
      console.error('❌ Error sending message to AI:', error);
      console.error('❌ Error details:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        url: error.config?.url,
        method: error.config?.method,
        data: error.config?.data
      });
      
      // Restore input text since send failed
      setInputText(currentInput);
      
      // Show detailed error to user
      const errorResponse = {
        id: Date.now() + 1,
        message: '',
        response: `❌ **Connection Error**: ${error.message}\n\n**Debug Info:**\n- URL: ${error.config?.url || 'Unknown'}\n- Status: ${error.response?.status || 'No response'}\n\n${currentUser ? `I can see your ${currentUser.diabetes_type || 'profile'} is loaded for personalized guidance once the connection is restored.` : 'Complete your profile for personalized advice.'}\n\nPlease try again or contact support if this persists.`,
        isUser: false,
        isError: true
      };
      
      setMessages(prev => [...prev, errorResponse]);
      setIsLoading(false);
      
      // Show error toast with details
      toast.error(`Send failed: ${error.message.substring(0, 50)}...`);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-blue-50 to-purple-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-md shadow-sm sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <ChefHat className="h-8 w-8 text-emerald-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">AI Health Coach</h1>
                <p className="text-sm text-gray-600">Diabetes-friendly nutrition guidance</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              {/* Consultation Limit Badge */}
              <Badge className="bg-gradient-to-r from-emerald-500 to-blue-500 text-white">
                Standard Plan: 10/month
              </Badge>
              
              {/* Home Button */}
              <Button 
                variant="outline" 
                onClick={() => window.location.href = '/'}
                className="flex items-center gap-2 hover:bg-gray-50 focus:ring-2 focus:ring-emerald-500 transition-all"
                aria-label="Return to home page"
              >
                <Navigation className="h-4 w-4" />
                Home
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto p-4 max-w-4xl">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          
          {/* Chat Interface - Main Column */}
          <div className="md:col-span-3">
            <Card className="h-[600px] flex flex-col">
              <CardHeader className="flex-shrink-0">
                <CardTitle className="flex items-center gap-2">
                  <MessageCircle className="h-5 w-5 text-emerald-600" />
                  Chat
                </CardTitle>
              </CardHeader>
              
              {/* Messages Area */}
              <CardContent className="flex-1 overflow-y-auto p-4">
                <div className="space-y-4">
                  {messages.map((msg) => (
                    <div key={msg.id} className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        msg.isUser 
                          ? 'bg-gradient-to-r from-emerald-500 to-blue-500 text-white' 
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        <p className="text-sm">{msg.isUser ? msg.message : (msg.response || msg.message)}</p>
                      </div>
                    </div>
                  ))}
                  
                  {/* Loading indicator */}
                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 text-gray-800 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
                        <div className="flex items-center gap-2">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-emerald-600"></div>
                          <p className="text-sm">Thinking...</p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
              
              {/* Input Area */}
              <div className="flex-shrink-0 p-4 border-t">
                <div className="flex gap-2">
                  <Input
                    value={inputText}
                    onChange={(e) => {
                      // CRITICAL FIX: Mark as touched when user manually types
                      touched.current = true;
                      
                      const value = e.target.value;
                      setInputText(value);
                      
                      // Persist user input in case disclaimer appears
                      if (value.trim()) {
                        localStorage.setItem('nt_coach_pending_question', value);
                      } else {
                        localStorage.removeItem('nt_coach_pending_question');
                      }
                    }}
                    placeholder="Ask about nutrition, meals, or recipes..."
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    className="flex-1 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
                    aria-label="Enter your nutrition question"
                  />
                  <Button 
                    onClick={handleSendMessage}
                    disabled={!inputText.trim() || isLoading}
                    className="bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700 focus:ring-2 focus:ring-emerald-500 transition-all"
                    aria-label="Send message"
                  >
                    <MessageSquarePlus className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </Card>
          </div>
          
          {/* Sidebar - Session Management */}
          <div className="md:col-span-1">
            <div className="space-y-4">
              
              {/* New Session Button */}
              <Button 
                className="w-full bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700 focus:ring-2 focus:ring-emerald-500 transition-all"
                onClick={() => {
                  setMessages([{
                    id: 'welcome-' + Date.now(),
                    message: `Hi! I'm your AI health coach. I can help you with meal planning, restaurant recommendations, and nutrition analysis. We're here to support your journey with helpful ideas. What would you like to explore today?`,
                    response: '',
                    isWelcome: true
                  }]);
                  setCurrentSessionId(null);
                  
                  // Show encouragement toast for new session
                  setTimeout(() => {
                    toast.success("New session started — a fresh start is always a great way to refocus.");
                  }, 800);
                }}
                aria-label="Start a new conversation"
              >
                <Plus className="h-4 w-4 mr-2" />
                New Chat
              </Button>
              
              {/* Search */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">Search Chats</CardTitle>
                </CardHeader>
                <CardContent>
                  <Input
                    placeholder="Search conversations..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
                    aria-label="Search through your conversations"
                  />
                </CardContent>
              </Card>
              
              {/* Session History */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">Recent Sessions</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-8">
                    <MessageCircle className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                    <p className="text-sm text-gray-500 mb-2">No conversations yet</p>
                    <p className="text-xs text-gray-400">Start chatting to see your history</p>
                  </div>
                </CardContent>
              </Card>
              
              {/* Disclaimer Banner */}
              <Card className="bg-yellow-50 border-yellow-200">
                <CardContent className="p-3">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-4 h-4 rounded-full bg-yellow-100 flex items-center justify-center">
                      <span className="text-yellow-600 text-xs font-bold">!</span>
                    </div>
                    <p className="text-xs font-medium text-yellow-800">Medical Disclaimer</p>
                  </div>
                  <p className="text-xs text-yellow-700">
                    Not a medical device. For diagnosis or treatment, consult a professional.
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  console.log('🔧 App component starting execution...', 'Current pathname:', window.location.pathname);
  
  // SaaS State Management
  const [appMode, setAppMode] = useState('landing'); // landing, demo, success, app, admin
  const [user, setUser] = useState(null);
  const [authToken, setAuthToken] = useState(null);
  const [adminToken, setAdminToken] = useState(null);
  const [subscriptionInfo, setSubscriptionInfo] = useState(null);
  const [demoMode, setDemoMode] = useState(false);
  const [demoUser, setDemoUser] = useState(null);
  
  // Medical Disclaimer State
  const [showDisclaimer, setShowDisclaimer] = useState(true);
  const [disclaimerAccepted, setDisclaimerAccepted] = useState(false);

  // Existing state (preserve all original functionality)
  const [currentUser, setCurrentUser] = useState(null);
  const [showForm, setShowForm] = useState(true);
  const [restaurants, setRestaurants] = useState([]);
  const [selectedRestaurant, setSelectedRestaurant] = useState(null);
  const [searchCenter, setSearchCenter] = useState(null);
  const [searchRadius, setSearchRadius] = useState(8047); // 5 miles in meters
  const [apiUsage, setApiUsage] = useState(null);
  const [shoppingLists, setShoppingLists] = useState([]);
  const [showShoppingListButton, setShowShoppingListButton] = useState(false);
  const [lastMealPain, setLastMealPlan] = useState("");

  // Check authentication on app load (run only once, independent of disclaimer)
  useEffect(() => {
    const checkAuthentication = async () => {
      const token = localStorage.getItem('authToken');
      const adminTokenStored = localStorage.getItem('adminToken');
      
      if (adminTokenStored) {
        setAdminToken(adminTokenStored);
        setAppMode('admin');
        setShowDisclaimer(false); // Admin doesn't need disclaimer
        return;
      }
      
      if (token) {
        try {
          const response = await axios.get(`${API}/auth/me`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          
          if (response.data.user && response.data.subscription_info) {
            setUser(response.data.user);
            setAuthToken(token);
            setSubscriptionInfo(response.data.subscription_info);
            setAppMode('app');
            setShowDisclaimer(false); // Existing users don't need disclaimer
            
            // Set up existing user profile for backward compatibility
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
          }
        } catch (error) {
          console.error('Authentication check failed:', error);
          localStorage.removeItem('authToken');
          // Don't set appMode here - let disclaimer handler do it
        }
      }
      // For new users, disclaimer handler will set the appropriate mode
    };

    checkAuthentication();
  }, []);

  // Handle successful payment and app access
  const handleAppAccess = async (paymentData) => {
    try {
      // For demo purposes, create a simple login
      // In production, this would be handled by the payment success flow
      const response = await axios.post(`${API}/auth/login`, {
        email: paymentData.email || 'demo@example.com'
      }, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      if (response.data.access_token) {
        localStorage.setItem('authToken', response.data.access_token);
        setAuthToken(response.data.access_token);
        setUser(response.data.user);
        setAppMode('app');
        
        // Set up profile for backward compatibility
        setCurrentUser({
          id: response.data.user.id,
          email: response.data.user.email,
          diabetes_type: response.data.user.diabetes_type || 'type2',
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
      }
    } catch (error) {
      console.error('App access error:', error);
      toast.error("There was an issue accessing your account. Please contact support.");
    }
  };

  // Handle demo access
  const handleDemoAccess = async (demoData) => {
    try {
      console.log('Demo access data received:', demoData);
      setDemoMode(true);
      setDemoUser(demoData.user);
      setAuthToken(demoData.access_token); // Fixed: use access_token not token
      setAppMode('app');
      
      // CRITICAL FIX: Set up profile with meaningful demo data for AI Coach
      setCurrentUser({
        id: demoData.user.id,
        email: demoData.user.email,
        diabetes_type: "type2", // Set meaningful default for demo
        age: 35, // Demo default age
        gender: "not_specified",
        activity_level: "moderate",
        health_goals: ["blood_sugar_control", "weight_management"],
        food_preferences: ["mediterranean", "low_carb"],
        allergies: [],
        cooking_skill: "intermediate",
        phone_number: null,
        plan: "premium" // Demo users get premium access
      });
      setShowForm(true); // Show profile setup for demo users to customize further
      
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
    setAdminToken(token);
    setAppMode('admin');
  };

  // Handle logout
  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('adminToken');
    setUser(null);
    setAuthToken(null);
    setAdminToken(null);
    setCurrentUser(null);
    setSubscriptionInfo(null);
    setDemoMode(false);
    setDemoUser(null);
    setAppMode('landing');
    toast.success("Logged out successfully");
  };

  // Medical Disclaimer Handlers
  const handleDisclaimerAccept = async () => {
    setDisclaimerAccepted(true);
    setShowDisclaimer(false);
    
    // Immediately check for demo mode after disclaimer acceptance
    try {
      console.log('Checking for demo mode after disclaimer acceptance...');
      const demoResponse = await axios.get(`${API}/demo/config`);
      console.log('Demo config response:', demoResponse.data);
      
      if (demoResponse.data && demoResponse.data.demo_mode === true) {
        console.log('Demo mode detected - setting app mode to demo');
        setAppMode('demo');
        return;
      }
    } catch (error) {
      console.error('Demo mode check failed:', error);
    }
    
    // If not demo mode, continue with normal flow
    setAppMode('landing');
  };

  const handleDisclaimerDecline = () => {
    // User declined - show warning and exit
    alert('You must accept the medical disclaimer to use NutriTame. The application will now close.');
    window.close(); // Close tab/window
    // If window.close() doesn't work (some browsers block it), redirect to a safe page
    setTimeout(() => {
      window.location.href = 'about:blank';
    }, 1000);
  };

  // Landing page handlers
  const handleLandingGetStarted = (mode) => {
    if (mode === 'demo') {
      setAppMode('demo'); // Route to DemoLandingPage
    } else {
      setAppMode('signup'); // Route to normal signup flow
    }
  };

  // Demo Mode Rendering
  if (appMode === 'demo') {
    return (
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<DemoLandingPage onDemoAccess={handleDemoAccess} />} />
          <Route path="/coach" element={<CoachRoute currentUser={currentUser} />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
    );
  }

  // Landing Page (Default)
  if (appMode === 'landing') {
    return (
      <BrowserRouter>
        <Routes>
          <Route path="/" element={
            showDisclaimer && !disclaimerAccepted ? 
              <MedicalDisclaimer onAccept={handleDisclaimerAccept} onDecline={handleDisclaimerDecline} /> :
              <LandingPageWrapper onGetStarted={handleLandingGetStarted} />
          } />
          <Route path="/coach" element={<CoachRoute currentUser={currentUser} />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
    );
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
          <Route path="/coach" element={<CoachRoute currentUser={currentUser} />} />
        </Routes>
      </BrowserRouter>
    );
  }

  if (appMode === 'success') {
    return <PaymentSuccess onAccessApp={handleAppAccess} />;
  }

  if (appMode === 'admin') {
    return <AdminDashboard adminToken={adminToken} />;
  }

  // Main App Mode (existing NutriTame functionality with SaaS enhancements)
  if (appMode === 'app') {
    return (
      <BrowserRouter>
        <Routes>
          <Route path="/coach" element={<CoachRoute currentUser={currentUser} />} />
          <Route path="/*" element={
            <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-blue-50 to-purple-50">
              {/* Demo Mode Banner - only show when in demo mode */}
              {demoMode && <DemoModeBanner />}
              
              {/* SaaS Header */}
              <SaaSHeader 
                user={user || demoUser} 
                subscriptionInfo={subscriptionInfo} 
                onLogout={handleLogout} 
              />
              
              {/* Main Content */}
              <div className="container mx-auto px-4 py-8">
                {showForm ? (
                  <UserProfileSetup 
                    onProfileComplete={(profile) => {
                      console.log('Profile creation completed:', profile);
                      setCurrentUser(profile);
                      
                      // CRITICAL: Update stored user ID for AI Coach consistency
                      if (profile.id) {
                        localStorage.setItem('nt_coach_user_id', profile.id);
                        console.log('✅ Updated nt_coach_user_id to:', profile.id);
                      }
                      
                      setShowForm(false);
                    }}
                    existingProfile={currentUser}
                  />
                ) : (
                  <Dashboard 
                    userProfile={currentUser} 
                    onBack={() => setShowForm(true)}
                    authToken={authToken}
                    subscriptionInfo={subscriptionInfo}
                    demoMode={demoMode}
                    shoppingLists={shoppingLists}
                    setShoppingLists={setShoppingLists}
                  />
                )}
              </div>
            </div>
          } />
        </Routes>
      </BrowserRouter>
    );
  }

  // Fallback
  return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
}

export default App;