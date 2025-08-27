import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Badge } from './components/ui/badge';
import { ChefHat, Heart, Target, Users, Star, Check, ArrowRight, Smartphone, MapPin, ShoppingCart, Crown } from 'lucide-react';
import { API } from './config';

const LandingPage = ({ onGetStarted }) => {
  const [stats, setStats] = useState({
    users: null,
    recipes: null, 
    restaurants: null
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${API}/stats`);
        if (response.ok) {
          const data = await response.json();
          setStats(data);
        }
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    };

    fetchStats();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-cyan-50 to-blue-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md shadow-sm sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-r from-emerald-600 to-blue-600 rounded-lg flex items-center justify-center">
                <ChefHat className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">NutriTame</span>
            </div>
            
            <nav className="hidden md:flex items-center gap-6">
              <a href="#features" className="text-gray-600 hover:text-emerald-600 transition-colors">Features</a>
              <a href="#pricing" className="text-gray-600 hover:text-emerald-600 transition-colors">Pricing</a>
              <Button 
                onClick={onGetStarted}
                className="bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700 text-white"
              >
                Get Started
              </Button>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20">
        <div className="container mx-auto px-4 text-center">
          <div className="max-w-4xl mx-auto">
            <Badge className="mb-6 bg-gradient-to-r from-emerald-600 to-blue-600 text-white">
              AI-Powered Diabetes Management
            </Badge>
            
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              Your Personal 
              <span className="bg-gradient-to-r from-emerald-600 to-blue-600 bg-clip-text text-transparent">
                Diabetes Health Coach
              </span>
            </h1>
            
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Our AI-powered platform provides comprehensive tools to help you manage diabetes effectively 
              through personalized meal planning, restaurant recommendations, and smart shopping lists.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
              <Button
                onClick={onGetStarted}
                className="px-8 py-4 text-lg font-semibold bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
              >
                Start Your Health Journey
                <ArrowRight className="h-5 w-5 ml-2" />
              </Button>
              
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <div className="flex -space-x-2">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-blue-400 border-2 border-white flex items-center justify-center text-white text-xs font-bold">
                      {i}
                    </div>
                  ))}
                </div>
                <span>Join {stats.users || '1,000+'} users managing their diabetes better</span>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-2xl mx-auto">
              <div className="text-center">
                <div className="text-3xl font-bold text-emerald-600">{stats.users || '1,000+'}+</div>
                <div className="text-gray-600">Active Users</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">{stats.recipes || '5,000+'}+</div>
                <div className="text-gray-600">Healthy Recipes</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600">{stats.restaurants || '10,000+'}+</div>
                <div className="text-gray-600">Partner Restaurants</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Everything You Need for Diabetes Management
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Our comprehensive platform provides all the tools you need to manage your diabetes effectively
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {[
              {
                icon: ChefHat,
                title: "AI Health Coach",
                description: "Get personalized meal recommendations and nutrition advice from our diabetes-specialized AI coach.",
                color: "emerald"
              },
              {
                icon: MapPin,
                title: "Restaurant Finder",
                description: "Discover diabetic-friendly restaurants near you with detailed nutritional information and reviews.",
                color: "blue"
              },
              {
                icon: ShoppingCart,
                title: "Smart Shopping Lists",
                description: "Generate organized shopping lists from your meal plans with healthy substitution suggestions.",
                color: "purple"
              },
              {
                icon: Target,
                title: "Goal Tracking",
                description: "Set and monitor your health goals with comprehensive progress tracking and insights.",
                color: "pink"
              },
              {
                icon: Smartphone,
                title: "Mobile Friendly",
                description: "Access all features on any device with our responsive, mobile-optimized interface.",
                color: "indigo"
              },
              {
                icon: Heart,
                title: "Health Integration",
                description: "Connect with popular health apps and devices to sync your health data automatically.",
                color: "red"
              }
            ].map((feature, index) => (
              <Card key={index} className="text-center hover:shadow-lg transition-shadow duration-300 border-2 hover:border-emerald-200">
                <CardHeader>
                  <div className={`w-16 h-16 mx-auto mb-4 rounded-xl bg-gradient-to-br from-${feature.color}-100 to-${feature.color}-200 flex items-center justify-center`}>
                    <feature.icon className={`h-8 w-8 text-${feature.color}-600`} />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-16 bg-gradient-to-br from-emerald-50 to-blue-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Choose Your Plan
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Start free and upgrade when you're ready for advanced features
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* Free Plan */}
            <Card className="border-2 border-gray-200 hover:border-emerald-300 transition-colors duration-300">
              <CardHeader>
                <CardTitle className="text-2xl">Basic</CardTitle>
                <div className="text-4xl font-bold">$9<span className="text-lg text-gray-600">/month</span></div>
                <CardDescription>Perfect for getting started with diabetes management</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <ul className="space-y-3">
                  {[
                    "AI Health Coach consultations",
                    "Basic meal planning",
                    "Restaurant recommendations",
                    "Mobile app access",
                    "Basic progress tracking"
                  ].map((feature, index) => (
                    <li key={index} className="flex items-center gap-2">
                      <Check className="h-5 w-5 text-emerald-600" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
                <Button 
                  className="w-full bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700"
                  onClick={onGetStarted}
                >
                  Start Free Trial
                </Button>
              </CardContent>
            </Card>

            {/* Premium Plan */}
            <Card className="border-2 border-emerald-300 relative">
              <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-emerald-600 to-blue-600 text-white px-3 py-1">
                <Crown className="h-4 w-4 mr-1" />
                Most Popular
              </Badge>
              <CardHeader>
                <CardTitle className="text-2xl">Premium</CardTitle>
                <div className="text-4xl font-bold">$19<span className="text-lg text-gray-600">/month</span></div>
                <CardDescription>Advanced features for comprehensive diabetes care</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <ul className="space-y-3">
                  {[
                    "Everything in Basic",
                    "Unlimited AI consultations",
                    "Advanced meal planning & recipes",
                    "Smart shopping lists",
                    "Detailed progress analytics",
                    "Health data integration",
                    "Priority customer support"
                  ].map((feature, index) => (
                    <li key={index} className="flex items-center gap-2">
                      <Check className="h-5 w-5 text-emerald-600" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
                <Button 
                  className="w-full bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700"
                  onClick={onGetStarted}
                >
                  Start Premium Trial
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Trusted by Thousands
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              See what our users say about successfully managing their diabetes with NutriTame's AI-powered platform.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {[
              {
                name: "Sarah Chen",
                role: "Type 2 Diabetes Patient",
                content: "NutriTame has completely transformed how I manage my diabetes. The AI coach provides personalized advice that actually works!",
                rating: 5
              },
              {
                name: "Michael Rodriguez", 
                role: "Pre-diabetes Management",
                content: "The restaurant finder is incredible. I can finally eat out without worrying about my blood sugar levels.",
                rating: 5
              },
              {
                name: "Jennifer Park",
                role: "Type 1 Diabetes Patient", 
                content: "The meal planning feature saves me hours every week and helps me maintain stable glucose levels.",
                rating: 5
              }
            ].map((testimonial, index) => (
              <Card key={index} className="text-center">
                <CardContent className="pt-6">
                  <div className="flex justify-center mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  <p className="text-gray-600 mb-4 italic">"{testimonial.content}"</p>
                  <div>
                    <div className="font-semibold">{testimonial.name}</div>
                    <div className="text-sm text-gray-500">{testimonial.role}</div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Accessibility & Inclusivity */}
      <section className="bg-white py-12">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">
              Designed for Everyone
            </h3>
            <div className="grid md:grid-cols-3 gap-6 text-sm text-gray-600">
              <div className="flex items-center justify-center gap-2">
                <Heart className="h-4 w-4 text-red-500" />
                <span>Screen reader compatible</span>
              </div>
              <div className="flex items-center justify-center gap-2">
                <Target className="h-4 w-4 text-blue-500" />
                <span>High contrast mode available</span>
              </div>
              <div className="flex items-center justify-center gap-2">
                <Zap className="h-4 w-4 text-emerald-500" />
                <span>Large text and zoom options</span>
              </div>
            </div>
            <p className="mt-4 text-gray-600 max-w-2xl mx-auto">
              NutriTame is committed to providing an inclusive experience for all users, 
              regardless of ability or technology preferences. We continuously improve 
              accessibility based on user feedback.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-emerald-600 to-blue-600 text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-6">Ready to Take Control of Your Health?</h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto">
            Join thousands of people who are successfully managing their diabetes with NutriTame's AI-powered platform.
          </p>
          
          <Button
            onClick={handleGetStarted}
            className="px-8 py-4 text-lg font-semibold bg-white text-emerald-600 hover:bg-gray-100 hover:text-emerald-700 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
          >
            Start Your Free Trial Today
            <ArrowRight className="h-5 w-5 ml-2" />
          </Button>
          
          <p className="text-sm mt-4 opacity-90">
            No credit card required • 15-day free trial • Cancel anytime
          </p>
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
          </div>
          
          <p className="text-gray-400 text-sm mb-4">
            Empowering people with diabetes to live healthier, happier lives through AI-powered nutrition guidance.
          </p>
          
          <p className="text-gray-500 text-xs">
            © 2025 NutriTame. All rights reserved. | Privacy Policy | Terms of Service
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;