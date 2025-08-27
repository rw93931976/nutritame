import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Badge } from './components/ui/badge';
import { MessageCircle, User, Bot, ChefHat, Sparkles, ArrowRight } from 'lucide-react';

const InteractiveDemo = ({ className = "" }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [userInput, setUserInput] = useState("");
  const [showFullDemo, setShowFullDemo] = useState(false);

  const demoSteps = [
    {
      id: 1,
      type: "welcome",
      content: "Hi! I'm your AI Health Coach. I can help you with diabetes-friendly meal planning. What would you like to explore?",
      options: ["Plan breakfast", "Find restaurants", "Carb counting help"]
    },
    {
      id: 2,
      type: "response",
      trigger: "Plan breakfast",
      content: "Great choice! For a diabetes-friendly breakfast, I recommend:\n\n🍳 **Veggie Scramble**: 2 eggs with spinach and bell peppers\n🥑 **Sides**: 1/4 avocado, 1 slice whole grain toast\n📊 **Carbs**: ~15g | **Protein**: 18g\n\n🩸 **Blood Sugar Impact**: LOW - This combination provides steady energy without spikes!"
    },
    {
      id: 3,
      type: "response", 
      trigger: "Find restaurants",
      content: "Perfect! I can help you find diabetic-friendly options nearby:\n\n🔍 **Restaurant Search Features**:\n• Low-carb menu filtering\n• Carb count estimates\n• Portion size guidance\n• Blood sugar impact ratings\n\n📍 **Example**: Chipotle Bowl - Skip rice, add extra veggies, lean protein, and guacamole for a balanced <20g carb meal!"
    },
    {
      id: 4,
      type: "response",
      trigger: "Carb counting help", 
      content: "Excellent! Carb counting is crucial for diabetes management:\n\n📏 **Visual Portion Guide**:\n• 1 cupped palm = ~15g carbs (rice/pasta)\n• 1 slice bread = ~15g carbs\n• 1 small apple = ~15g carbs\n\n⚡ **Smart Tips**:\n• Pair carbs with protein/fiber\n• Choose complex over simple carbs\n• Monitor blood sugar 2hrs after meals"
    }
  ];

  const handleOptionClick = (option) => {
    const nextStep = demoSteps.find(step => step.trigger === option);
    if (nextStep) {
      setCurrentStep(nextStep.id);
    }
  };

  const resetDemo = () => {
    setCurrentStep(0);
    setUserInput("");
  };

  const currentMessage = demoSteps.find(step => step.id === currentStep) || demoSteps[0];

  return (
    <div className={`max-w-4xl mx-auto ${className}`}>
      <div className="text-center mb-8">
        <div className="flex items-center justify-center gap-2 mb-4">
          <Sparkles className="h-6 w-6 text-emerald-600" />
          <h2 className="text-3xl font-bold text-gray-800">Try the AI Coach Now</h2>
        </div>
        <p className="text-gray-600">Experience personalized diabetes management in 30 seconds</p>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Interactive Chat Demo */}
        <Card className="shadow-xl border-2 border-emerald-200">
          <CardHeader className="bg-gradient-to-r from-emerald-50 to-blue-50">
            <CardTitle className="flex items-center gap-2">
              <MessageCircle className="h-5 w-5 text-emerald-600" />
              AI Health Coach Demo
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {/* Chat Messages */}
            <div className="h-80 overflow-y-auto p-4 space-y-4">
              {/* AI Welcome Message */}
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-emerald-500 to-blue-500 flex items-center justify-center">
                  <Bot className="h-4 w-4 text-white" />
                </div>
                <div className="flex-1">
                  <div className="bg-gray-100 rounded-lg p-3 text-sm">
                    {currentMessage.content}
                  </div>
                  {currentMessage.options && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {currentMessage.options.map((option, index) => (
                        <Button
                          key={index}
                          onClick={() => handleOptionClick(option)}
                          size="sm"
                          variant="outline"
                          className="text-xs hover:bg-emerald-50 hover:border-emerald-300"
                        >
                          {option}
                        </Button>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Show user selection if made */}
              {currentStep > 0 && (
                <div className="flex items-start gap-3 justify-end">
                  <div className="flex-1 text-right">
                    <div className="bg-emerald-500 text-white rounded-lg p-3 text-sm inline-block">
                      {demoSteps.find(s => s.id === currentStep)?.trigger || "Let me try this!"}
                    </div>
                  </div>
                  <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center">
                    <User className="h-4 w-4 text-gray-600" />
                  </div>
                </div>
              )}
            </div>

            {/* Demo Controls */}
            <div className="border-t p-4 bg-gray-50">
              <div className="flex items-center justify-between">
                <Button
                  onClick={resetDemo}
                  variant="outline"
                  size="sm"
                  className="text-xs"
                >
                  Reset Demo
                </Button>
                <Badge variant="secondary" className="text-xs">
                  Interactive Preview
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Demo Features Highlight */}
        <div className="space-y-6">
          <Card className="border-emerald-200">
            <CardContent className="p-6">
              <div className="flex items-center gap-3 mb-3">
                <ChefHat className="h-6 w-6 text-emerald-600" />
                <h3 className="text-lg font-semibold text-gray-800">Personalized Meal Planning</h3>
              </div>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>• Carb-counted recipe suggestions</li>
                <li>• Blood sugar impact predictions</li>
                <li>• Portion size guidance</li>
                <li>• Meal timing recommendations</li>
              </ul>
            </CardContent>
          </Card>

          <Card className="border-blue-200">
            <CardContent className="p-6">
              <div className="flex items-center gap-3 mb-3">
                <MessageCircle className="h-6 w-6 text-blue-600" />
                <h3 className="text-lg font-semibold text-gray-800">Smart AI Conversations</h3>
              </div>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>• Understands diabetes context</li>
                <li>• Learns your preferences</li>
                <li>• Provides instant guidance</li>
                <li>• Available 24/7</li>
              </ul>
            </CardContent>
          </Card>

          <Card className="border-purple-200">
            <CardContent className="p-6">
              <div className="flex items-center gap-3 mb-3">
                <Sparkles className="h-6 w-6 text-purple-600" />
                <h3 className="text-lg font-semibold text-gray-800">Coming Soon Premium</h3>
              </div>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>• Healthcare provider portal</li>
                <li>• CGM & fitness tracker sync</li>
                <li>• Progress tracking analytics</li>
                <li>• Community features</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Call to Action */}
      <div className="text-center mt-8">
        <Button
          onClick={() => setShowFullDemo(true)}
          size="lg"
          className="bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700 text-white px-8 py-3"
        >
          <ArrowRight className="h-5 w-5 mr-2" />
          Try Full Demo Now - Free
        </Button>
        <p className="text-sm text-gray-600 mt-2">
          No signup required • Full feature access • Demo ends October 1st
        </p>
      </div>
    </div>
  );
};

export default InteractiveDemo;