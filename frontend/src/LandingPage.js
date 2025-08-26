import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Badge } from './components/ui/badge';
import { Check, Star, Heart, Shield, Users, TrendingUp, ChefHat, Smartphone, MapPin } from 'lucide-react';

const API = import.meta.env.REACT_APP_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;

const LandingPage = ({ onStartTrial }) => {
  const [email, setEmail] = useState('');
  const [selectedPlan, setSelectedPlan] = useState('basic');
  const [loading, setLoading] = useState(false);

  const plans = {
    basic: {
      name: 'Basic Plan',
      price: '$9',
      interval: 'month',
      features: [
        'AI Health Coach',
        'Basic Restaurant Search',
        'Shopping Lists',
        '5 chat sessions per day',
        'Imperial measurements',
        'Email support'
      ],
      popular: false
    },
    premium: {
      name: 'Premium Plan', 
      price: '$19',
      interval: 'month',
      features: [
        'Everything in Basic',
        'Unlimited AI conversations',
        'Advanced Restaurant Search',
        'Recipe favorites & save',
        'Data export (GDPR)',
        'Priority support',
        'Premium meal planning'
      ],
      popular: true
    }
  };

  const handleStartTrial = async (plan) => {
    if (!email) {
      alert('Please enter your email address');
      return;
    }

    if (!email.includes('@')) {
      alert('Please enter a valid email address');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API}/payments/checkout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          plan: plan,
          email: email,
          origin_url: window.location.origin
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create checkout session');
      }

      const data = await response.json();
      
      // Redirect to Stripe Checkout
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        throw new Error('No checkout URL received');
      }
    } catch (error) {
      console.error('Checkout error:', error);
      alert('Failed to start trial. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-blue-50 to-purple-50">
      {/* Header */}
      <header className="bg-white/90 backdrop-blur-md shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-600 to-blue-600 flex items-center justify-center">
                <ChefHat className="h-6 w-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-600 to-blue-600 bg-clip-text text-transparent">
                GlucoPlanner
              </h1>
            </div>
            <div className="hidden md:flex items-center gap-6">
              <a href="#features" className="text-gray-600 hover:text-emerald-600 transition-colors">Features</a>
              <a href="#pricing" className="text-gray-600 hover:text-emerald-600 transition-colors">Pricing</a>
              <a href="#about" className="text-gray-600 hover:text-emerald-600 transition-colors">About</a>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 text-center">
        <div className="max-w-4xl mx-auto">
          <Badge className="mb-6 bg-emerald-100 text-emerald-700 hover:bg-emerald-200">
            <Heart className="h-4 w-4 mr-2" />
            AI-Powered Diabetes Management
          </Badge>
          
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-8">
            Take Control of Your
            <span className="block bg-gradient-to-r from-emerald-600 to-blue-600 bg-clip-text text-transparent">
              Diabetes Journey
            </span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto leading-relaxed">
            Get personalized meal plans, restaurant recommendations, and AI-powered health coaching 
            designed specifically for diabetes management. Start your 15-day free trial today.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
            <Input
              type="email"
              placeholder="Enter your email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="max-w-sm h-12 text-lg"
            />
            <Button
              onClick={() => handleStartTrial(selectedPlan)}
              disabled={loading}
              className="h-12 px-8 bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700 text-lg font-semibold"
            >
              {loading ? 'Starting Trial...' : 'Start Free Trial'}
            </Button>
          </div>

          <p className="text-sm text-gray-500">
            🎉 <strong>15-day free trial</strong> • No credit card required initially • Cancel anytime
          </p>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="bg-white/50 py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Everything You Need for Diabetes Management
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Our AI-powered platform provides comprehensive tools to help you manage diabetes effectively
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {[
              {
                icon: ChefHat,
                title: "AI Health Coach",
                description: "Get personalized meal recommendations and nutrition advice powered by advanced AI technology specifically trained for diabetes management."
              },
              {
                icon: MapPin,
                title: "Restaurant Finder",
                description: "Discover diabetic-friendly restaurants near you with detailed nutritional information and meal suggestions."
              },
              {
                icon: Smartphone,
                title: "Smart Shopping Lists",
                description: "Generate organized shopping lists from meal plans with imperial measurements and diabetes-friendly substitutions."
              },
              {
                icon: Shield,
                title: "HIPAA Compliant",
                description: "Your health data is protected with enterprise-grade security and full GDPR/HIPAA compliance."
              },
              {
                icon: TrendingUp,
                title: "Progress Tracking",
                description: "Monitor your journey with comprehensive analytics and insights to optimize your diabetes management."
              },
              {
                icon: Users,
                title: "Expert Support",
                description: "Access to nutrition experts and dedicated customer support to help you succeed in your health goals."
              }
            ].map((feature, index) => (
              <Card key={index} className="text-center hover:shadow-lg transition-shadow duration-300">
                <CardHeader>
                  <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-gradient-to-br from-emerald-100 to-blue-100 flex items-center justify-center">
                    <feature.icon className="h-8 w-8 text-emerald-600" />
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
      <section id="pricing" className="py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Choose Your Plan
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Start with a 15-day free trial. No credit card required initially.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {Object.entries(plans).map(([planKey, plan]) => (
              <Card 
                key={planKey}
                className={`relative hover:shadow-xl transition-all duration-300 ${
                  plan.popular ? 'ring-2 ring-emerald-500 scale-105' : ''
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-gradient-to-r from-emerald-600 to-blue-600 text-white px-4 py-1">
                      <Star className="h-4 w-4 mr-1" />
                      Most Popular
                    </Badge>
                  </div>
                )}
                
                <CardHeader className="text-center pb-8">
                  <CardTitle className="text-2xl font-bold">{plan.name}</CardTitle>
                  <div className="mt-4">
                    <span className="text-5xl font-bold text-gray-900">{plan.price}</span>
                    <span className="text-xl text-gray-500">/{plan.interval}</span>
                  </div>
                </CardHeader>
                
                <CardContent className="space-y-6">
                  <ul className="space-y-3">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-center gap-3">
                        <Check className="h-5 w-5 text-emerald-600 flex-shrink-0" />
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  
                  <Button
                    onClick={() => {
                      setSelectedPlan(planKey);
                      handleStartTrial(planKey);
                    }}
                    disabled={loading}
                    className={`w-full h-12 text-lg font-semibold ${
                      plan.popular
                        ? 'bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700'
                        : 'bg-gray-900 hover:bg-gray-800'
                    }`}
                  >
                    {loading && selectedPlan === planKey ? 'Starting Trial...' : 'Start Free Trial'}
                  </Button>
                  
                  <p className="text-sm text-gray-500 text-center">
                    15-day free trial included
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="text-center">
            <div className="flex items-center justify-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-600 to-blue-600 flex items-center justify-center">
                <ChefHat className="h-6 w-6 text-white" />
              </div>
              <h2 className="text-2xl font-bold">GlucoPlanner</h2>
            </div>
            
            <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
              Empowering people with diabetes to take control of their health through AI-powered meal planning, 
              restaurant recommendations, and personalized coaching.
            </p>
            
            <div className="flex justify-center gap-8 text-sm">
              <a href="#" className="text-gray-400 hover:text-white transition-colors">Privacy Policy</a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">Terms of Service</a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">HIPAA Compliance</a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">Support</a>
            </div>
            
            <div className="mt-8 pt-8 border-t border-gray-800">
              <p className="text-gray-500">
                © 2025 GlucoPlanner. All rights reserved. | Built with ❤️ for the diabetes community.
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;