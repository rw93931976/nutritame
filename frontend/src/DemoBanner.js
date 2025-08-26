import React, { useState } from 'react';
import { Alert, AlertDescription } from './components/ui/alert';
import { Button } from './components/ui/button';
import { Badge } from './components/ui/badge';
import { 
  TestTube, 
  Rocket, 
  X, 
  Calendar,
  Crown,
  Gift,
  Zap,
  Users
} from 'lucide-react';

const DemoBanner = ({ demoConfig, onDismiss, showMinimal = false }) => {
  const [dismissed, setDismissed] = useState(false);

  if (dismissed && showMinimal) return null;

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const handleDismiss = () => {
    setDismissed(true);
    if (onDismiss) onDismiss();
  };

  // Minimal banner for in-app usage
  if (showMinimal && !dismissed) {
    return (
      <div className="bg-gradient-to-r from-orange-500 to-pink-500 text-white py-2 px-4 relative">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm">
            <TestTube className="h-4 w-4" />
            <span className="font-medium">
              DEMO MODE • Launch: {demoConfig && formatDate(demoConfig.launch_date)}
            </span>
          </div>
          <button
            onClick={handleDismiss}
            className="text-white hover:text-gray-200 ml-2"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>
    );
  }

  // Full banner for main pages
  return (
    <div className="bg-gradient-to-r from-purple-600 via-pink-500 to-orange-500 text-white py-4 px-4 relative">
      <div className="container mx-auto">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          {/* Demo Notice */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
                <TestTube className="h-5 w-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-bold">You're using the FREE DEMO</h3>
                  <Badge className="bg-white/20 text-white border-white/30">
                    <Gift className="h-3 w-3 mr-1" />
                    All Features Unlocked
                  </Badge>
                </div>
                <p className="text-sm opacity-90">
                  Full premium access until launch • No account needed
                </p>
              </div>
            </div>
          </div>

          {/* Launch Information */}
          <div className="flex flex-col md:flex-row items-center gap-4">
            <div className="text-center md:text-right">
              <div className="flex items-center gap-2 justify-center md:justify-end">
                <Calendar className="h-4 w-4" />
                <span className="font-medium">
                  Official Launch: {demoConfig && formatDate(demoConfig.launch_date)}
                </span>
              </div>
              <p className="text-xs opacity-90">
                After launch: $9-$19/month • Demo users get 50% off first 3 months
              </p>
            </div>

            <div className="flex items-center gap-2">
              <Button 
                size="sm" 
                className="bg-white text-purple-600 hover:bg-gray-100 font-medium"
              >
                <Crown className="h-4 w-4 mr-1" />
                Reserve Early Bird
              </Button>
              
              {!showMinimal && (
                <button
                  onClick={handleDismiss}
                  className="text-white/70 hover:text-white ml-2"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Additional Benefits */}
        <div className="mt-4 pt-4 border-t border-white/20">
          <div className="grid md:grid-cols-3 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-yellow-300" />
              <span>Unlimited AI conversations</span>
            </div>
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-green-300" />
              <span>Join 500+ beta testers</span>
            </div>
            <div className="flex items-center gap-2">
              <Gift className="h-4 w-4 text-pink-300" />
              <span>Early access to new features</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DemoBanner;