import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Badge } from './components/ui/badge';
import { BookOpen, Clock, User, TrendingUp, Heart, Target, Lightbulb, CheckCircle } from 'lucide-react';

const EducationCenter = ({ className = "" }) => {
  const [selectedCategory, setSelectedCategory] = useState('nutrition');

  const articles = {
    nutrition: [
      {
        id: 1,
        title: "Understanding Carb Counting: A Complete Guide",
        excerpt: "Master the art of carb counting with visual portion guides and practical tips for better blood sugar management.",
        readTime: "8 min read",
        category: "Nutrition Basics",
        author: "Dr. Sarah Chen, RD",
        difficulty: "Beginner",
        image: "📊",
        topics: ["Carb Counting", "Portion Control", "Blood Sugar", "Meal Planning"]
      },
      {
        id: 2,
        title: "The Science of Meal Timing for Diabetes",
        excerpt: "Learn how when you eat can be just as important as what you eat for optimal glucose control.",
        readTime: "12 min read",
        category: "Advanced Nutrition",
        author: "Dr. Michael Rodriguez, MD",
        difficulty: "Intermediate",
        image: "⏰",
        topics: ["Meal Timing", "Metabolism", "Insulin Response", "Circadian Rhythm"]
      },
      {
        id: 3,
        title: "Reading Nutrition Labels Like a Pro",
        excerpt: "Decode food labels to make informed choices and avoid hidden sugars and refined carbs.",
        readTime: "6 min read",
        category: "Practical Skills",
        author: "Jennifer Liu, CDE",
        difficulty: "Beginner",
        image: "🏷️",
        topics: ["Food Labels", "Hidden Sugars", "Ingredients", "Shopping Tips"]
      }
    ],
    lifestyle: [
      {
        id: 4,
        title: "Exercise and Blood Sugar: What You Need to Know",
        excerpt: "Understand how different types of exercise affect your blood glucose and how to exercise safely.",
        readTime: "10 min read",
        category: "Exercise & Diabetes",
        author: "Dr. James Park, PhD",
        difficulty: "Intermediate",
        image: "🏃‍♀️",
        topics: ["Exercise", "Blood Sugar", "Safety", "Workout Planning"]
      },
      {
        id: 5,
        title: "Stress Management for Better Blood Sugar Control",
        excerpt: "Discover evidence-based techniques to reduce stress and its impact on your diabetes management.",
        readTime: "9 min read",
        category: "Mental Health",
        author: "Dr. Lisa Thompson, LCSW",
        difficulty: "Beginner",
        image: "🧘‍♀️",
        topics: ["Stress Management", "Mental Health", "Cortisol", "Mindfulness"]
      },
      {
        id: 6,
        title: "Building Sustainable Healthy Habits",
        excerpt: "Create lasting lifestyle changes with psychology-backed strategies for habit formation.",
        readTime: "15 min read",
        category: "Behavior Change",
        author: "Dr. Robert Kim, PhD",
        difficulty: "Advanced",
        image: "🎯",
        topics: ["Habit Formation", "Behavior Change", "Motivation", "Goal Setting"]
      }
    ],
    medical: [
      {
        id: 7,
        title: "A1C Explained: Your 3-Month Blood Sugar Average",
        excerpt: "Understand what A1C means, target ranges, and how to improve your numbers through lifestyle changes.",
        readTime: "7 min read",
        category: "Medical Basics",
        author: "Dr. Patricia Wong, MD",
        difficulty: "Beginner",
        image: "🩺",
        topics: ["A1C", "Blood Tests", "Target Ranges", "Medical Monitoring"]
      },
      {
        id: 8,
        title: "Continuous Glucose Monitors: Pros and Cons",
        excerpt: "Everything you need to know about CGMs, including who benefits most and how to use the data.",
        readTime: "11 min read",
        category: "Technology",
        author: "Dr. Alex Johnson, MD",
        difficulty: "Intermediate",
        image: "📱",
        topics: ["CGM", "Technology", "Monitoring", "Data Analysis"]
      },
      {
        id: 9,
        title: "Working with Your Healthcare Team",
        excerpt: "Maximize your appointments and build effective partnerships with doctors, dietitians, and specialists.",
        readTime: "8 min read",
        category: "Healthcare Navigation",
        author: "Maria Garcia, RN, CDE",
        difficulty: "Beginner",
        image: "👥",
        topics: ["Healthcare Team", "Communication", "Appointments", "Advocacy"]
      }
    ]
  };

  const categories = [
    { key: 'nutrition', label: 'Nutrition 101', icon: '🍎', count: 3 },
    { key: 'lifestyle', label: 'Lifestyle', icon: '💪', count: 3 },
    { key: 'medical', label: 'Medical Insights', icon: '🩺', count: 3 }
  ];

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'Beginner': return 'text-green-600 bg-green-100';
      case 'Intermediate': return 'text-yellow-600 bg-yellow-100';
      case 'Advanced': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className={`max-w-6xl mx-auto ${className}`}>
      <div className="text-center mb-12">
        <div className="flex items-center justify-center gap-2 mb-4">
          <BookOpen className="h-6 w-6 text-emerald-600" />
          <h2 className="text-4xl font-bold text-gray-900">Diabetes Education Center</h2>
        </div>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Evidence-based articles and guides written by certified diabetes educators, nutritionists, and medical professionals
        </p>
      </div>

      {/* Category Navigation */}
      <div className="flex justify-center mb-8">
        <div className="bg-white rounded-lg p-1 shadow-md border max-w-md">
          {categories.map((category) => (
            <Button
              key={category.key}
              onClick={() => setSelectedCategory(category.key)}
              variant={selectedCategory === category.key ? "default" : "ghost"}
              className={`px-4 py-2 rounded-md transition-all text-sm ${
                selectedCategory === category.key
                  ? 'bg-emerald-600 text-white shadow-md'
                  : 'text-gray-600 hover:text-emerald-600 hover:bg-emerald-50'
              }`}
            >
              <span className="mr-2">{category.icon}</span>
              {category.label}
              <Badge className="ml-2 bg-gray-200 text-gray-700 text-xs">
                {category.count}
              </Badge>
            </Button>
          ))}
        </div>
      </div>

      {/* Articles Grid */}
      <div className="grid lg:grid-cols-3 md:grid-cols-2 gap-6 mb-12">
        {articles[selectedCategory].map((article) => (
          <Card key={article.id} className="hover:shadow-xl transition-all duration-300 border-2 hover:border-emerald-200 flex flex-col">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between mb-3">
                <div className="text-3xl">{article.image}</div>
                <Badge className={`text-xs font-medium ${getDifficultyColor(article.difficulty)}`}>
                  {article.difficulty}
                </Badge>
              </div>
              <CardTitle className="text-lg leading-tight mb-2">{article.title}</CardTitle>
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <Clock className="h-3 w-3" />
                <span>{article.readTime}</span>
                <span>•</span>
                <User className="h-3 w-3" />
                <span className="truncate">{article.author}</span>
              </div>
            </CardHeader>
            
            <CardContent className="flex flex-col flex-1 p-4 pt-0">
              <p className="text-gray-600 mb-4 text-sm leading-relaxed flex-1">{article.excerpt}</p>
              
              {/* Topic Tags */}
              <div className="mb-4">
                <div className="flex flex-wrap gap-1">
                  {article.topics.slice(0, 2).map((topic, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {topic}
                    </Badge>
                  ))}
                  {article.topics.length > 2 && (
                    <Badge variant="secondary" className="text-xs">
                      +{article.topics.length - 2}
                    </Badge>
                  )}
                </div>
              </div>

              <Button 
                className="w-full bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700 text-white"
                size="sm"
              >
                Read Full Article
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Featured Learning Paths */}
      <div className="bg-gradient-to-r from-blue-50 to-emerald-50 rounded-xl p-8 mb-8">
        <div className="text-center mb-6">
          <div className="flex items-center justify-center gap-2 mb-4">
            <TrendingUp className="h-6 w-6 text-emerald-600" />
            <h3 className="text-2xl font-bold text-gray-900">Structured Learning Paths</h3>
          </div>
          <p className="text-gray-600">Follow our expert-designed curricula for comprehensive diabetes education</p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          <Card className="text-center border-emerald-200">
            <CardContent className="p-6">
              <div className="text-3xl mb-3">🎓</div>
              <h4 className="font-semibold text-gray-800 mb-2">Diabetes 101</h4>
              <p className="text-sm text-gray-600 mb-4">Complete beginner's guide to diabetes management</p>
              <div className="flex items-center justify-center gap-1 text-xs text-emerald-600">
                <CheckCircle className="h-3 w-3" />
                <span>5 modules • 2 weeks</span>
              </div>
            </CardContent>
          </Card>

          <Card className="text-center border-blue-200">
            <CardContent className="p-6">
              <div className="text-3xl mb-3">🍽️</div>
              <h4 className="font-semibold text-gray-800 mb-2">Nutrition Mastery</h4>
              <p className="text-sm text-gray-600 mb-4">Advanced meal planning and nutrition strategies</p>
              <div className="flex items-center justify-center gap-1 text-xs text-blue-600">
                <CheckCircle className="h-3 w-3" />
                <span>8 modules • 4 weeks</span>
              </div>
            </CardContent>
          </Card>

          <Card className="text-center border-purple-200">
            <CardContent className="p-6">
              <div className="text-3xl mb-3">💪</div>
              <h4 className="font-semibold text-gray-800 mb-2">Lifestyle Optimization</h4>
              <p className="text-sm text-gray-600 mb-4">Exercise, stress management, and habit building</p>
              <div className="flex items-center justify-center gap-1 text-xs text-purple-600">
                <CheckCircle className="h-3 w-3" />
                <span>6 modules • 3 weeks</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Education CTA */}
      <div className="text-center bg-gradient-to-r from-emerald-600 to-blue-600 text-white rounded-xl p-8">
        <div className="flex items-center justify-center gap-2 mb-4">
          <Lightbulb className="h-6 w-6" />
          <h3 className="text-2xl font-bold">Get Personalized Education</h3>
        </div>
        <p className="text-emerald-100 mb-6 max-w-2xl mx-auto">
          Access personalized article recommendations, interactive quizzes, and progress tracking 
          tailored to your diabetes management goals and experience level.
        </p>
        <Button 
          size="lg"
          className="bg-white text-emerald-600 hover:bg-gray-100 px-8 py-3 font-semibold"
        >
          Start Learning Journey - Free
        </Button>
      </div>
    </div>
  );
};

export default EducationCenter;