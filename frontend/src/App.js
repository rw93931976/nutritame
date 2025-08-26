import { useState, useEffect } from "react";
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
import { Heart, MessageCircle, User, ChefHat, Target, Calendar, Clock, CheckCircle, MapPin, Search, Star, Phone, Globe, Navigation, ShoppingCart, List, Plus, Check } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// User Profile Setup Component
const UserProfileSetup = ({ onProfileComplete, existingProfile }) => {
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
    cooking_skill: existingProfile?.cooking_skill || ""
  });

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
      const profileData = {
        ...profile,
        age: profile.age ? parseInt(profile.age) : null
      };

      let response;
      if (existingProfile?.id) {
        response = await axios.put(`${API}/users/${existingProfile.id}`, profileData);
      } else {
        response = await axios.post(`${API}/users`, profileData);
      }

      toast.success(existingProfile?.id ? "Profile updated successfully!" : "Profile created successfully!");
      onProfileComplete(response.data);
    } catch (error) {
      console.error("Profile save error:", error);
      toast.error("Failed to save profile. Please try again.");
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
            Welcome to GlucoPlanner
          </h1>
          <p className="text-gray-700 text-lg">
            Your personalized AI health coach for diabetes-friendly meal planning with restaurant search
          </p>
        </div>

        <Card className="shadow-xl border-0 bg-white/90 backdrop-blur-sm">
          <CardHeader className="bg-gradient-to-r from-emerald-50 to-blue-50 rounded-t-lg">
            <CardTitle className="flex items-center gap-2 text-gray-800">
              <User className="h-5 w-5 text-emerald-600" />
              {existingProfile?.id ? "Update Your Profile" : "Create Your Profile"}
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
                <Select value={profile.diabetes_type} onValueChange={(value) => setProfile({...profile, diabetes_type: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select your diabetes type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="type1">Type 1 Diabetes</SelectItem>
                    <SelectItem value="type2">Type 2 Diabetes</SelectItem>
                    <SelectItem value="prediabetes">Prediabetes</SelectItem>
                  </SelectContent>
                </Select>
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

              <Button 
                type="submit" 
                className="w-full bg-gradient-to-r from-emerald-600 via-blue-600 to-emerald-600 hover:from-emerald-700 hover:via-blue-700 hover:to-emerald-700 text-white font-semibold py-3 px-6 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105" 
                disabled={loading || !profile.diabetes_type}
              >
                {loading ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    Saving...
                  </div>
                ) : (
                  existingProfile?.id ? "Update Profile" : "Create Profile"
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
      toast.error("Failed to search restaurants. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleManualSearch = async () => {
    if (!searchLocation.trim()) {
      toast.error("Please enter a location");
      return;
    }
    
    // For demo, we'll use a default location (San Francisco)
    // In production, you'd use a geocoding service to convert address to coordinates
    const defaultCoords = { lat: 37.7749, lng: -122.4194 };
    await searchRestaurants(defaultCoords.lat, defaultCoords.lng);
  };

  return (
    <div className="space-y-6">
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
                placeholder="Or enter a location (e.g., San Francisco, CA)"
                value={searchLocation}
                onChange={(e) => setSearchLocation(e.target.value)}
                className="flex-1"
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
                  <SelectItem value="1000">1 km</SelectItem>
                  <SelectItem value="2000">2 km</SelectItem>
                  <SelectItem value="5000">5 km</SelectItem>
                  <SelectItem value="10000">10 km</SelectItem>
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

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {restaurants.map((restaurant) => (
          <RestaurantCard 
            key={restaurant.place_id} 
            restaurant={restaurant} 
            onSelect={onRestaurantSelect}
          />
        ))}
      </div>
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

  useEffect(() => {
    // Load chat history
    loadChatHistory();
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
      toast.error("Failed to create shopping list");
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async (messageText = currentMessage) => {
    if (!messageText.trim() || loading) return;

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
      const response = await axios.post(`${API}/chat`, {
        user_id: userProfile.id,
        message: messageText
      });

      // Clean up AI response - remove markdown formatting
      const cleanedResponse = response.data.response
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
        ...response.data,
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
              <h1 className="text-xl font-semibold bg-gradient-to-r from-emerald-600 to-blue-600 bg-clip-text text-transparent">GlucoPlanner Dashboard</h1>
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
            {/* Chat Interface */}
            <div className="h-[calc(100vh-200px)] flex flex-col">
              {/* Messages */}
              <div className="flex-1 space-y-4 overflow-y-auto mb-4 pr-2 min-h-[600px]">
                {messages.map((msg, index) => (
                  <div key={msg.id || index} className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'} message-enter`}>
                    <Card className={`max-w-[85%] transition-all duration-300 ${
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
                            <p className="whitespace-pre-wrap leading-relaxed text-base">
                              {msg.isUser ? msg.message : (msg.response || msg.message)}
                            </p>
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
              </div>

              {/* Shopping List Generation Button */}
              {showShoppingListButton && (
                <div className="mb-4">
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

              {/* Input Area */}
              <Card className="shadow-xl bg-white/90 backdrop-blur-sm border border-gray-200/50 sticky bottom-0">
                <CardContent className="p-6">
                  <div className="flex gap-4">
                    <Textarea
                      value={currentMessage}
                      onChange={(e) => setCurrentMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Ask about meal planning, restaurant recommendations, nutrition analysis..."
                      className="min-h-[80px] resize-none border-2 border-gray-200 focus:border-emerald-400 focus:ring-2 focus:ring-emerald-200 transition-all duration-300 text-base"
                      disabled={loading}
                    />
                    <Button 
                      onClick={() => sendMessage()}
                      disabled={!currentMessage.trim() || loading}
                      className="bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700 text-white px-8 py-4 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 min-h-[80px]"
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
          </TabsContent>

          <TabsContent value="restaurants">
            <RestaurantSearch 
              userProfile={userProfile} 
              onRestaurantSelect={handleRestaurantSelect}
            />
          </TabsContent>

          <TabsContent value="shopping">
            <ShoppingListView userProfile={userProfile} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [showDashboard, setShowDashboard] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if there's an existing user profile
    checkExistingProfile();
  }, []);

  const checkExistingProfile = async () => {
    try {
      // For demo purposes, we'll use localStorage to track the current user
      const savedUserId = localStorage.getItem('glucoplanner_user_id');
      
      if (savedUserId) {
        const response = await axios.get(`${API}/users/${savedUserId}`);
        setCurrentUser(response.data);
        setShowDashboard(true);
      }
    } catch (error) {
      console.error("Error checking existing profile:", error);
      localStorage.removeItem('glucoplanner_user_id');
    } finally {
      setLoading(false);
    }
  };

  const handleProfileComplete = (userProfile) => {
    setCurrentUser(userProfile);
    localStorage.setItem('glucoplanner_user_id', userProfile.id);
    setShowDashboard(true);
    toast.success("Welcome to GlucoPlanner! Let's explore restaurants and plan your meals.");
  };

  const handleBackToProfile = () => {
    setShowDashboard(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-teal-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-emerald-200 border-t-emerald-600 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading GlucoPlanner...</p>
        </div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <div className="App">
        <Routes>
          <Route
            path="/"
            element={
              showDashboard && currentUser ? (
                <Dashboard 
                  userProfile={currentUser} 
                  onBack={handleBackToProfile}
                />
              ) : (
                <UserProfileSetup 
                  onProfileComplete={handleProfileComplete}
                  existingProfile={currentUser}
                />
              )
            }
          />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;