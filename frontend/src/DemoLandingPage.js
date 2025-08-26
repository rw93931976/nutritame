import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Badge } from './components/ui/badge';
import { Alert, AlertDescription } from './components/ui/alert';
import { 
  ChefHat, 
  Rocket, 
  TestTube, 
  Calendar,
  Check,
  Star,
  Heart,
  Shield,
  Users,
  TrendingUp,
  Smartphone,
  MapPin,
  Crown,
  Zap,
  Clock,
  Gift
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DemoLandingPage = ({ onDemoAccess }) => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [demoConfig, setDemoConfig] = useState(null);

  useEffect(() => {
    // Load demo configuration
    const loadDemoConfig = async () => {
      try {
        const response = await fetch(`${API}/demo/config`);
        if (response.ok) {
          const config = await response.json();
          setDemoConfig(config);
        }
      } catch (error) {
        console.error('Failed to load demo config:', error);
      }
    };

    loadDemoConfig();
  }, []);

  const handleDemoAccess = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API}/demo/access`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email || undefined
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create demo access');
      }

      const data = await response.json();
      onDemoAccess(data);
      
    } catch (error) {
      console.error('Demo access error:', error);
      alert('Failed to create demo access. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-blue-50 to-purple-50">
      {/* Demo Mode Banner */}
      <div className="bg-gradient-to-r from-orange-500 to-pink-500 text-white py-3">
        <div className="container mx-auto px-4 text-center">
          <div className="flex items-center justify-center gap-2">
            <TestTube className="h-4 w-4" />
            <span className="font-medium">
              🚀 PRE-LAUNCH DEMO • Test All Features Free • Launch Date: {demoConfig && formatDate(demoConfig.launch_date)}
            </span>
          </div>
        </div>
      </div>

      {/* Header */}
      <header className="bg-white/90 backdrop-blur-md shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-600 to-blue-600 flex items-center justify-center">
                <ChefHat className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-600 to-blue-600 bg-clip-text text-transparent">
                  NutriTame
                </h1>
                <Badge className="bg-orange-100 text-orange-800 text-xs">
                  <TestTube className="h-3 w-3 mr-1" />
                  Demo Mode
                </Badge>
              </div>
            </div>
            <div className="hidden md:flex items-center gap-6">
              <a href="#features" className="text-gray-600 hover:text-emerald-600 transition-colors">Features</a>
              <a href="#pricing" className="text-gray-600 hover:text-emerald-600 transition-colors">Launch Pricing</a>
              <a href="#demo" className="text-gray-600 hover:text-emerald-600 transition-colors">Try Demo</a>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 text-center">
        <div className="max-w-4xl mx-auto">
          <Badge className="mb-6 bg-gradient-to-r from-orange-500 to-pink-500 text-white hover:from-orange-600 hover:to-pink-600">
            <Rocket className="h-4 w-4 mr-2" />
            Pre-Launch Demo Available
          </Badge>
          
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-8">
            Test Drive the Future of
            <span className="block bg-gradient-to-r from-emerald-600 to-blue-600 bg-clip-text text-transparent">
              Diabetes Management
            </span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto leading-relaxed">
            Experience all premium features completely free during our pre-launch demo period. 
            No account creation required - just jump in and explore!
          </p>

          {/* Demo Access Section */}
          <Card className="max-w-md mx-auto mb-8 border-2 border-gradient-to-r from-emerald-500 to-blue-500">
            <CardHeader className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-emerald-100 to-blue-100 flex items-center justify-center">
                <Gift className="h-8 w-8 text-emerald-600" />
              </div>
              <CardTitle className="text-2xl">Free Demo Access</CardTitle>
              <CardDescription>
                Try all premium features instantly - no payment required
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-left space-y-2">
                <div className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-600" />
                  <span className="text-sm">Full premium feature access</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-600" />
                  <span className="text-sm">Unlimited AI conversations</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-600" />
                  <span className="text-sm">Restaurant search & mapping</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-600" />
                  <span className="text-sm">Smart shopping lists</span>
                </div>
              </div>

              <Input
                type="email"
                placeholder="Optional: Enter email for updates"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="h-12"
              />
              
              <Button
                onClick={handleDemoAccess}
                disabled={loading}
                className="w-full h-12 text-lg font-semibold bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700"
              >
                {loading ? 'Creating Demo Access...' : 'Start Free Demo Now'}
              </Button>
              
              <p className="text-xs text-gray-500 text-center">
                No account creation required • Instant access • All features unlocked
              </p>
            </CardContent>
          </Card>

          {/* Launch Notice */}
          <Alert className="max-w-2xl mx-auto bg-gradient-to-r from-yellow-50 to-orange-50 border-orange-200">
            <Calendar className="h-4 w-4" />
            <AlertDescription>
              <strong>Official Launch: {demoConfig && formatDate(demoConfig.launch_date)}</strong>
              <br />
              After launch, account creation and subscription ($9-$19/month) will be required. 
              Demo users will receive special early-bird pricing!
            </AlertDescription>
          </Alert>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="bg-white/50 py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Try Every Feature - Completely Free
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Experience the full power of our AI-driven diabetes management platform
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {[
              {
                icon: ChefHat,
                title: "AI Health Coach",
                description: "Unlimited conversations with our diabetes-specialized AI coach. Get personalized meal recommendations and nutrition advice.",
                badge: "Unlimited in Demo"
              },
              {
                icon: MapPin,
                title: "Restaurant Finder",
                description: "Search diabetic-friendly restaurants with interactive maps and detailed nutritional information.",
                badge: "Full Access"
              },
              {
                icon: Smartphone,
                title: "Smart Shopping Lists",
                description: "Generate organized shopping lists from meal plans with diabetes-friendly substitutions.",
                badge: "Premium Feature"
              },
              {
                icon: Heart,
                title: "Recipe Favorites",
                description: "Save and organize your favorite recipes and meal plans for easy access.",
                badge: "Premium Feature"
              },
              {
                icon: TrendingUp,
                title: "Progress Tracking",
                description: "Monitor your nutrition journey with comprehensive analytics and insights.",
                badge: "Premium Feature"
              },
              {
                icon: Shield,
                title: "Data Export",
                description: "GDPR-compliant data export and privacy controls for your health information.",
                badge: "Premium Feature"
              }
            ].map((feature, index) => (
              <Card key={index} className="text-center hover:shadow-lg transition-shadow duration-300 border-2 hover:border-emerald-200">
                <CardHeader>
                  <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-gradient-to-br from-emerald-100 to-blue-100 flex items-center justify-center">
                    <feature.icon className="h-8 w-8 text-emerald-600" />
                  </div>
                  <div className="flex items-center justify-center gap-2 mb-2">
                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                    <Badge className="bg-green-100 text-green-700 text-xs">
                      {feature.badge}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Launch Pricing Section */}
      <section id="pricing" className="py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Launch Pricing - Coming Soon
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              After {demoConfig && formatDate(demoConfig.launch_date)}, these plans will be required for access
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* Basic Plan */}
            <Card className="relative hover:shadow-xl transition-all duration-300">
              <div className="absolute top-4 right-4">
                <Badge className="bg-blue-100 text-blue-700">
                  After Launch
                </Badge>
              </div>
              
              <CardHeader className="text-center pb-8">
                <CardTitle className="text-2xl font-bold">Basic Plan</CardTitle>
                <div className="mt-4">
                  <span className="text-5xl font-bold text-gray-900">$9</span>
                  <span className="text-xl text-gray-500">/month</span>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-6">
                <ul className="space-y-3">
                  {[
                    "AI Health Coach",
                    "Basic Restaurant Search", 
                    "Shopping Lists",
                    "5 chat sessions per day",
                    "Email support"
                  ].map((feature, index) => (
                    <li key={index} className="flex items-center gap-3">
                      <Check className="h-5 w-5 text-emerald-600 flex-shrink-0" />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>
                
                <Button disabled className="w-full h-12 text-lg font-semibold bg-gray-200 text-gray-500">
                  Available After Launch
                </Button>
              </CardContent>
            </Card>

            {/* Premium Plan */}
            <Card className="relative hover:shadow-xl transition-all duration-300 ring-2 ring-emerald-500 scale-105">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <Badge className="bg-gradient-to-r from-emerald-600 to-blue-600 text-white px-4 py-1">
                  <Crown className="h-4 w-4 mr-1" />
                  Most Popular
                </Badge>
              </div>
              <div className="absolute top-4 right-4">
                <Badge className="bg-blue-100 text-blue-700">
                  After Launch
                </Badge>
              </div>
              
              <CardHeader className="text-center pb-8">
                <CardTitle className="text-2xl font-bold">Premium Plan</CardTitle>
                <div className="mt-4">
                  <span className="text-5xl font-bold text-gray-900">$19</span>
                  <span className="text-xl text-gray-500">/month</span>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-6">
                <ul className="space-y-3">
                  {[
                    "Everything in Basic",
                    "Unlimited AI conversations",
                    "Advanced Restaurant Search", 
                    "Recipe favorites & save",
                    "Data export (GDPR)",
                    "Priority support",
                    "Premium meal planning"
                  ].map((feature, index) => (
                    <li key={index} className="flex items-center gap-3">
                      <Check className="h-5 w-5 text-emerald-600 flex-shrink-0" />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>
                
                <Button disabled className="w-full h-12 text-lg font-semibold bg-gray-200 text-gray-500">
                  Available After Launch
                </Button>
              </CardContent>
            </Card>
          </div>

          <div className="text-center mt-8">
            <Alert className="max-w-2xl mx-auto bg-gradient-to-r from-green-50 to-emerald-50 border-emerald-200">
              <Zap className="h-4 w-4" />
              <AlertDescription>
                <strong>Early Bird Special:</strong> Demo users will receive 50% off their first 3 months after launch! 
                Plus 30-day free trial instead of the standard 15 days.
              </AlertDescription>
            </Alert>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="bg-gradient-to-r from-emerald-600 to-blue-600 text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-6">Ready to Transform Your Diabetes Management?</h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto">
            Join hundreds of people already testing NutriTame. Experience the future of personalized diabetes care.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button
              onClick={handleDemoAccess}
              disabled={loading}
              className="px-8 py-4 text-lg font-semibold bg-white text-emerald-600 hover:bg-gray-100 hover:text-emerald-700"
            >
              {loading ? 'Creating Access...' : 'Start Demo Now - Free'}
            </Button>
            
            <div className="text-center">
              <p className="text-sm opacity-90">
                <Clock className="h-4 w-4 inline mr-1" />
                Demo ends on launch day • No credit card required
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="container mx-auto px-4 text-center">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-600 to-blue-600 flex items-center justify-center">
              <ChefHat className="h-5 w-5 text-white" />
            </div>
            <h2 className="text-xl font-bold">NutriTame</h2>
            <Badge className="bg-orange-600 text-white text-xs">
              Pre-Launch Demo
            </Badge>
          </div>
          
          <p className="text-gray-400 text-sm mb-4">
            Currently in demo mode • Official launch {demoConfig && formatDate(demoConfig.launch_date)}
          </p>
          
          <p className="text-gray-500 text-xs">
            © 2025 NutriTame. All rights reserved. | Built with ❤️ for the diabetes community.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default DemoLandingPage;