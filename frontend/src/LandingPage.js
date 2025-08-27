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
      <section className="container mx-auto px-4 py-16 text-center">
        <div className="max-w-4xl mx-auto">
          <Badge className="mb-6 bg-gradient-to-r from-emerald-500 to-blue-500 text-white hover:from-emerald-600 hover:to-blue-600">
            <Heart className="h-4 w-4 mr-2" />
            AI-Powered Diabetes Management
          </Badge>
          
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-8">
            Your Personal
            <span className="block bg-gradient-to-r from-emerald-600 to-blue-600 bg-clip-text text-transparent">
              Diabetes Health Coach
            </span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto leading-relaxed">
            Get personalized meal recommendations, find diabetic-friendly restaurants, and manage your health with AI-powered insights tailored specifically for diabetes management.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
            <Button
              onClick={handleGetStarted}
              className="px-8 py-4 text-lg font-semibold bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
            >
              Start Free Demo Now
              <ArrowRight className="h-5 w-5 ml-2" />
            </Button>
          </div>

          {/* Demo Countdown Timer & Social Proof Combined */}
          <div className="mb-12 bg-gradient-to-r from-orange-50 to-red-50 rounded-xl p-8 border border-orange-200">
            <div className="text-center mb-6">
              <div className="flex items-center justify-center gap-2 mb-3">
                <Clock className="h-5 w-5 text-orange-600" />
                <span className="text-lg font-semibold text-gray-700">Demo ends in:</span>
              </div>
              
              <div className="flex items-center justify-center gap-3 mb-4">
                <div className="text-center">
                  <div className="bg-gradient-to-br from-orange-500 to-red-500 text-white rounded-lg p-3 min-w-[60px]">
                    <div className="text-2xl font-bold">34</div>
                  </div>
                  <div className="text-sm text-gray-600 mt-1">Days</div>
                </div>
                
                <div className="text-2xl font-bold text-gray-400">:</div>
                
                <div className="text-center">
                  <div className="bg-gradient-to-br from-orange-500 to-red-500 text-white rounded-lg p-3 min-w-[60px]">
                    <div className="text-2xl font-bold">12</div>
                  </div>
                  <div className="text-sm text-gray-600 mt-1">Hours</div>
                </div>
                
                <div className="text-2xl font-bold text-gray-400">:</div>
                
                <div className="text-center">
                  <div className="bg-gradient-to-br from-orange-500 to-red-500 text-white rounded-lg p-3 min-w-[60px]">
                    <div className="text-2xl font-bold">23</div>
                  </div>
                  <div className="text-sm text-gray-600 mt-1">Minutes</div>
                </div>
              </div>
              
              <div className="flex items-center justify-center gap-1 text-sm text-gray-600">
                <Calendar className="h-4 w-4" />
                <span>Launch: October 1, 2025</span>
              </div>
            </div>
            
            {/* Social Proof Numbers */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
              <div>
                <div className="flex items-center justify-center gap-2 mb-2">
                  <Users className="h-5 w-5 text-emerald-600" />
                  <div className="text-2xl font-bold text-gray-800">2,847+</div>
                </div>
                <div className="text-gray-600 text-sm">people already testing NutriTame</div>
                <div className="text-emerald-600 font-medium text-xs mt-1">Join the community!</div>
              </div>
              
              <div>
                <div className="flex items-center justify-center gap-2 mb-2">
                  <Utensils className="h-5 w-5 text-blue-600" />
                  <div className="text-2xl font-bold text-gray-800">15,284+</div>
                </div>
                <div className="text-gray-600 text-sm">diabetes-friendly meals planned</div>
                <div className="text-blue-600 font-medium text-xs mt-1">This month alone</div>
              </div>
              
              <div>
                <div className="flex items-center justify-center gap-2 mb-2">
                  <MapPin className="h-5 w-5 text-purple-600" />
                  <div className="text-2xl font-bold text-gray-800">8,942+</div>
                </div>
                <div className="text-gray-600 text-sm">diabetic-friendly restaurants found</div>
                <div className="text-purple-600 font-medium text-xs mt-1">Nationwide coverage</div>
              </div>
            </div>
          </div>

          {/* Security & Trust Badges */}
          <div className="flex flex-wrap justify-center items-center gap-6 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4 text-green-600" />
              <span>HIPAA Compliant</span>
            </div>
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4 text-blue-600" />
              <span>256-bit SSL Encryption</span>
            </div>
            <div className="flex items-center gap-2">
              <Heart className="h-4 w-4 text-red-600" />
              <span>30-Day Money-Back Guarantee</span>
            </div>
          </div>
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
                description: "Get personalized meal recommendations and nutrition advice from our diabetes-specialized AI coach.",
                color: "emerald",
                badge: "Featured"
              },
              {
                icon: Target,
                title: "Smart Carb Counter",
                description: "Visual portion guides with carb estimates and blood sugar impact indicators (Low/Medium/High).",
                color: "orange",
                badge: "New"
              },
              {
                icon: Clock,
                title: "Meal Timing Guidance", 
                description: "Optimal meal timing recommendations based on your medication schedule and activity levels.",
                color: "purple",
                badge: "Premium"
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
                color: "green"
              },
              {
                icon: Smartphone,
                title: "Works Offline",
                description: "Access your meal plans and nutrition data even without internet connection - perfect for daily use.",
                color: "indigo",
                badge: "Essential"
              }
            ].map((feature, index) => (
              <Card key={index} className="text-center hover:shadow-lg transition-shadow duration-300 border-2 hover:border-emerald-200 relative">
                {feature.badge && (
                  <Badge className={`absolute -top-2 -right-2 z-10 ${
                    feature.badge === 'New' ? 'bg-orange-500' :
                    feature.badge === 'Premium' ? 'bg-purple-500' :
                    feature.badge === 'Essential' ? 'bg-blue-500' :
                    'bg-emerald-500'
                  }`}>
                    {feature.badge}
                  </Badge>
                )}
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

      {/* Interactive Demo Section */}
      <section className="py-16 bg-gradient-to-br from-emerald-50 via-cyan-50 to-blue-50">
        <div className="container mx-auto px-4">
          <InteractiveDemo />
        </div>
      </section>

      {/* Recipe Preview Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <RecipePreview />
        </div>
      </section>

      {/* Education Center Section */}
      <section className="py-16 bg-gradient-to-br from-blue-50 to-emerald-50">
        <div className="container mx-auto px-4">
          <EducationCenter />
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Choose Your Plan
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-6">
              Less than one diabetes-friendly meal per month. Saves $200+ monthly on food waste and impulse purchases.
            </p>
            <div className="flex flex-wrap justify-center items-center gap-6 text-sm text-emerald-600 font-medium">
              <span>✅ 30-Day Money-Back Guarantee</span>
              <span>✅ Cancel Anytime</span>
              <span>✅ No Setup Fees</span>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* Free Plan */}
            <Card className="relative hover:shadow-xl transition-all duration-300">
              <CardHeader className="text-center pb-8">
                <CardTitle className="text-2xl font-bold">Free Plan</CardTitle>
                <div className="mt-4">
                  <span className="text-5xl font-bold text-gray-900">$0</span>
                  <span className="text-xl text-gray-500">/month</span>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-6">
                <ul className="space-y-3">
                  {[
                    "Basic AI health coaching",
                    "5 chat sessions per day", 
                    "Basic restaurant search",
                    "Simple meal planning",
                    "Community support"
                  ].map((feature, index) => (
                    <li key={index} className="flex items-center gap-3">
                      <Check className="h-5 w-5 text-emerald-600 flex-shrink-0" />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>
                
                <Button onClick={handleGetStarted} className="w-full h-12 text-lg font-semibold bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-700 hover:to-gray-800 text-white">
                  Get Started Free
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
                    "Unlimited AI conversations",
                    "Advanced restaurant search", 
                    "Smart shopping lists",
                    "Recipe favorites & export",
                    "Progress tracking & analytics",
                    "Priority support",
                    "Health app integrations"
                  ].map((feature, index) => (
                    <li key={index} className="flex items-center gap-3">
                      <Check className="h-5 w-5 text-emerald-600 flex-shrink-0" />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>
                
                <Button onClick={handleGetStarted} className="w-full h-12 text-lg font-semibold bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700 text-white">
                  Start Premium Trial
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Coming Soon Premium Features */}
      <section className="bg-gradient-to-br from-purple-50 to-blue-50 py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <Badge className="mb-4 bg-purple-500 text-white">
              Coming Soon
            </Badge>
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Advanced Premium Features
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Even more powerful tools for comprehensive diabetes management
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <Card className="hover:shadow-lg transition-shadow duration-300 border-purple-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-6 w-6 text-purple-600" />
                  Healthcare Provider Portal
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-gray-600">
                  <li>• Share meal plans with your care team</li>
                  <li>• Provider access and monitoring</li>
                  <li>• Medical-grade integration</li>
                  <li>• Collaborative care planning</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow duration-300 border-blue-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-6 w-6 text-blue-600" />
                  Device Integration
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-gray-600">
                  <li>• Sync with CGMs and glucose meters</li>
                  <li>• Fitness tracker integration</li>
                  <li>• Real-time health data analysis</li>
                  <li>• Automated meal suggestions based on readings</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow duration-300 border-emerald-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-6 w-6 text-emerald-600" />
                  Progress Tracking
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-gray-600">
                  <li>• Comprehensive analytics dashboard</li>
                  <li>• A1C improvement tracking</li>
                  <li>• Nutrition journey monitoring</li>
                  <li>• Weekly progress reports</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow duration-300 border-orange-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-6 w-6 text-orange-600" />
                  Community Hub
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-gray-600">
                  <li>• Connect with other users</li>
                  <li>• Recipe sharing and discussions</li>
                  <li>• Local support groups</li>
                  <li>• Expert Q&A sessions</li>
                </ul>
              </CardContent>
            </Card>
          </div>

          <div className="text-center mt-12">
            <p className="text-gray-600 mb-4">Want early access to these features?</p>
            <Button 
              variant="outline" 
              className="border-purple-500 text-purple-600 hover:bg-purple-50"
            >
              Join Waitlist
            </Button>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="bg-white/50 py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              What Our Users Say
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Real stories from people managing their diabetes with NutriTame
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {[
              {
                name: "Sarah M.",
                role: "Type 2 Diabetes",
                content: "NutriTame has completely changed how I approach meal planning. The AI coach understands my dietary restrictions and always suggests delicious, healthy options.",
                rating: 5
              },
              {
                name: "Michael R.",
                role: "Type 1 Diabetes",
                content: "Finding restaurants that cater to my needs used to be a nightmare. Now I can easily discover great places to eat with confidence.",
                rating: 5
              },
              {
                name: "Jennifer L.",
                role: "Prediabetes",
                content: "The shopping lists feature saves me so much time and helps me stick to my healthy eating goals. Highly recommend!",
                rating: 5
              }
            ].map((testimonial, index) => (
              <Card key={index} className="text-center hover:shadow-lg transition-shadow duration-300">
                <CardContent className="p-6">
                  <div className="flex justify-center mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  <p className="text-gray-600 mb-4 italic">"{testimonial.content}"</p>
                  <div>
                    <p className="font-semibold text-gray-800">{testimonial.name}</p>
                    <p className="text-sm text-gray-500">{testimonial.role}</p>
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