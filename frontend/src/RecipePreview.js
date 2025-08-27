import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Badge } from './components/ui/badge';
import { Clock, Users, TrendingDown, Star, ChefHat, Heart, Target } from 'lucide-react';

const RecipePreview = ({ className = "" }) => {
  const [selectedCategory, setSelectedCategory] = useState('breakfast');

  const recipes = {
    breakfast: [
      {
        id: 1,
        name: "Diabetes-Friendly Veggie Scramble",
        image: "🍳",
        time: "15 mins",
        servings: 2,
        carbs: "8g",
        impact: "LOW",
        rating: 4.8,
        description: "Protein-rich eggs with colorful vegetables for steady blood sugar.",
        ingredients: ["2 eggs", "1/2 cup spinach", "1/4 cup bell peppers", "1 tbsp olive oil"]
      },
      {
        id: 2,
        name: "Cinnamon Chia Pudding",
        image: "🥣",
        time: "5 mins prep",
        servings: 1,
        carbs: "12g", 
        impact: "LOW",
        rating: 4.6,
        description: "Overnight chia pudding with natural sweetness and fiber.",
        ingredients: ["3 tbsp chia seeds", "1 cup almond milk", "1/2 tsp cinnamon", "1/2 cup berries"]
      }
    ],
    lunch: [
      {
        id: 3,
        name: "Mediterranean Quinoa Bowl",
        image: "🥗",
        time: "20 mins",
        servings: 2,
        carbs: "22g",
        impact: "MEDIUM",
        rating: 4.9,
        description: "Complete protein bowl with healthy Mediterranean flavors.",
        ingredients: ["1/2 cup quinoa", "2 cups mixed greens", "1/4 cup feta", "2 tbsp olive oil"]
      },
      {
        id: 4,
        name: "Grilled Chicken Lettuce Wraps",
        image: "🥬",
        time: "25 mins",
        servings: 3,
        carbs: "6g",
        impact: "LOW",
        rating: 4.7,
        description: "Low-carb, high-protein lunch with Asian-inspired flavors.",
        ingredients: ["6 oz chicken breast", "1 head butter lettuce", "2 tbsp soy sauce", "1 tbsp sesame oil"]
      }
    ],
    dinner: [
      {
        id: 5,
        name: "Baked Salmon with Roasted Vegetables",
        image: "🐟",
        time: "30 mins",
        servings: 4,
        carbs: "15g",
        impact: "LOW",
        rating: 4.9,
        description: "Omega-3 rich salmon with fiber-packed roasted vegetables.",
        ingredients: ["4 salmon fillets", "2 cups broccoli", "1 cup carrots", "2 tbsp herbs"]
      },
      {
        id: 6,
        name: "Turkey Zucchini Lasagna",
        image: "🍆",
        time: "45 mins",
        servings: 6,
        carbs: "18g",
        impact: "MEDIUM",
        rating: 4.8,
        description: "Comfort food reimagined with zucchini noodles and lean turkey.",
        ingredients: ["1 lb ground turkey", "3 large zucchini", "2 cups marinara", "1 cup part-skim ricotta"]
      }
    ]
  };

  const categories = [
    { key: 'breakfast', label: 'Breakfast', icon: '🌅' },
    { key: 'lunch', label: 'Lunch', icon: '☀️' },
    { key: 'dinner', label: 'Dinner', icon: '🌙' }
  ];

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'LOW': return 'text-green-600 bg-green-100';
      case 'MEDIUM': return 'text-yellow-600 bg-yellow-100';
      case 'HIGH': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className={`max-w-6xl mx-auto ${className}`}>
      <div className="text-center mb-12">
        <div className="flex items-center justify-center gap-2 mb-4">
          <ChefHat className="h-6 w-6 text-emerald-600" />
          <h2 className="text-4xl font-bold text-gray-900">Browse 500+ Diabetes-Friendly Recipes</h2>
        </div>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Every recipe includes carb counts, blood sugar impact ratings, and portion guidance from certified nutritionists
        </p>
      </div>

      {/* Category Tabs */}
      <div className="flex justify-center mb-8">
        <div className="bg-white rounded-lg p-1 shadow-md border">
          {categories.map((category) => (
            <Button
              key={category.key}
              onClick={() => setSelectedCategory(category.key)}
              variant={selectedCategory === category.key ? "default" : "ghost"}
              className={`px-6 py-2 rounded-md transition-all ${
                selectedCategory === category.key
                  ? 'bg-emerald-600 text-white shadow-md'
                  : 'text-gray-600 hover:text-emerald-600 hover:bg-emerald-50'
              }`}
            >
              <span className="mr-2">{category.icon}</span>
              {category.label}
            </Button>
          ))}
        </div>
      </div>

      {/* Recipe Grid */}
      <div className="grid md:grid-cols-2 gap-6 mb-12">
        {recipes[selectedCategory].map((recipe) => (
          <Card key={recipe.id} className="hover:shadow-xl transition-all duration-300 border-2 hover:border-emerald-200">
            <CardHeader className="pb-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="text-4xl">{recipe.image}</div>
                  <div>
                    <CardTitle className="text-lg">{recipe.name}</CardTitle>
                    <div className="flex items-center gap-2 mt-1">
                      <div className="flex items-center">
                        {[...Array(5)].map((_, i) => (
                          <Star 
                            key={i} 
                            className={`h-3 w-3 ${i < Math.floor(recipe.rating) ? 'text-yellow-400 fill-current' : 'text-gray-300'}`} 
                          />
                        ))}
                        <span className="text-sm text-gray-600 ml-1">({recipe.rating})</span>
                      </div>
                    </div>
                  </div>
                </div>
                <Badge className={`text-xs font-bold ${getImpactColor(recipe.impact)}`}>
                  {recipe.impact} IMPACT
                </Badge>
              </div>
            </CardHeader>
            
            <CardContent>
              <p className="text-gray-600 mb-4 text-sm">{recipe.description}</p>
              
              {/* Recipe Stats */}
              <div className="grid grid-cols-3 gap-4 mb-4 text-center">
                <div className="flex flex-col items-center">
                  <Clock className="h-4 w-4 text-blue-600 mb-1" />
                  <span className="text-xs text-gray-600">{recipe.time}</span>
                </div>
                <div className="flex flex-col items-center">
                  <Users className="h-4 w-4 text-purple-600 mb-1" />
                  <span className="text-xs text-gray-600">{recipe.servings} servings</span>
                </div>
                <div className="flex flex-col items-center">
                  <TrendingDown className="h-4 w-4 text-green-600 mb-1" />
                  <span className="text-xs text-gray-600">{recipe.carbs} carbs</span>
                </div>
              </div>

              {/* Key Ingredients Preview */}
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-800 mb-2">Key Ingredients:</h4>
                <div className="flex flex-wrap gap-1">
                  {recipe.ingredients.slice(0, 3).map((ingredient, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {ingredient}
                    </Badge>
                  ))}
                  {recipe.ingredients.length > 3 && (
                    <Badge variant="secondary" className="text-xs">
                      +{recipe.ingredients.length - 3} more
                    </Badge>
                  )}
                </div>
              </div>

              <Button 
                className="w-full bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700 text-white"
                size="sm"
              >
                View Full Recipe & Nutrition
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recipe CTA */}
      <div className="text-center bg-gradient-to-r from-emerald-50 to-blue-50 rounded-xl p-8">
        <div className="flex items-center justify-center gap-2 mb-4">
          <Heart className="h-5 w-5 text-red-500" />
          <Target className="h-5 w-5 text-emerald-600" />
        </div>
        <h3 className="text-2xl font-bold text-gray-900 mb-4">
          Access All 500+ Recipes + AI Meal Planning
        </h3>
        <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
          Get personalized recipe recommendations, automatic meal planning, and smart shopping lists 
          tailored to your diabetes management goals.
        </p>
        <Button 
          size="lg"
          className="bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700 text-white px-8 py-3"
        >
          Start Free Demo - Unlock All Recipes
        </Button>
      </div>
    </div>
  );
};

export default RecipePreview;