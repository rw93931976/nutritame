import React, { useState, useEffect } from 'react';
import { Alert, AlertDescription } from './components/ui/alert';
import { Button } from './components/ui/button';
import { Badge } from './components/ui/badge';
import { 
  TestTube, 
  Rocket, 
  Calendar, 
  Crown,
  X,
  Gift,
  Clock,
  Star
} from 'lucide-react';

import { BACKEND_URL, API } from './config';

const DemoModeBanner = ({ isMinimized = false, onToggleMinimize = null }) => {
  const [demoConfig, setDemoConfig] = useState(null);
  const [dismissed, setDismissed] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(isMinimized);

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

    // Check if banner was dismissed in this session
    const wasDismissed = sessionStorage.getItem('demo_banner_dismissed') === 'true';
    setDismissed(wasDismissed);
  }, []);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const handleDismiss = () => {
    setDismissed(true);
    sessionStorage.setItem('demo_banner_dismissed', 'true');
  };

  const handleToggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
    if (onToggleMinimize) {
      onToggleMinimize(!isCollapsed);
    }
  };

  // Don't render if dismissed or demo mode is not enabled
  if (dismissed || !demoConfig?.demo_mode) {
    return null;
  }

  // Minimized version (just a small floating badge)
  if (isCollapsed) {
    return (
      <div className="fixed top-4 right-4 z-50">
        <Button
          onClick={handleToggleCollapse}
          className="bg-gradient-to-r from-orange-500 to-pink-500 hover:from-orange-600 hover:to-pink-600 text-white shadow-lg"
          size="sm"
        >
          <TestTube className="h-4 w-4 mr-2" />
          DEMO MODE
        </Button>
      </div>
    );
  }

  return (
    <>
      {/* Full Demo Mode Banner */}
      <div className="bg-gradient-to-r from-orange-500 via-pink-500 to-purple-500 text-white shadow-lg sticky top-0 z-40">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between gap-4">
            {/* Main Banner Content */}
            <div className="flex items-center gap-3 flex-1">
              <div className="flex items-center gap-2">
                <TestTube className="h-5 w-5 animate-pulse" />
                <Badge className="bg-white/20 text-white hover:bg-white/30 backdrop-blur-sm">
                  PRE-LAUNCH DEMO
                </Badge>
              </div>
              
              <div className="hidden sm:flex items-center gap-4 text-sm">
                <div 
                  className="flex items-center gap-1 cursor-pointer hover:bg-white/10 px-2 py-1 rounded transition-colors"
                  onClick={() => {
                    alert('🎁 Demo Mode Active: All premium features including unlimited AI conversations, restaurant search with mapping, shopping list generation, and personalized meal planning are completely free during the pre-launch demo period!');
                  }}
                >
                  <Gift className="h-4 w-4" />
                  <span className="font-medium">All Premium Features Free</span>
                </div>
                
                <div 
                  className="flex items-center gap-1 cursor-pointer hover:bg-white/10 px-2 py-1 rounded transition-colors"
                  onClick={() => {
                    alert('👑 No Account Required: During demo mode, you can access all features without creating an account. After launch, users will need to subscribe to continue using premium features.');
                  }}
                >
                  <Crown className="h-4 w-4" />
                  <span>No Account Required</span>
                </div>
                
                {demoConfig?.launch_date && (
                  <div 
                    className="flex items-center gap-1 cursor-pointer hover:bg-white/10 px-2 py-1 rounded transition-colors"
                    onClick={() => {
                      alert(`🚀 Launch Date: NutriTame will officially launch on ${formatDate(demoConfig.launch_date)}. After this date, subscription plans ($9 Basic, $19 Premium) will be required to access features. Enjoy the free demo until then!`);
                    }}
                  >
                    <Calendar className="h-4 w-4" />
                    <span>Launch: {formatDate(demoConfig.launch_date)}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Mobile-friendly content */}
            <div className="flex sm:hidden items-center text-xs font-medium">
              <span>🚀 FREE DEMO • Full Features</span>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-2">
              <Button
                onClick={handleToggleCollapse}
                variant="ghost"
                size="sm"
                className="text-white hover:bg-white/10 h-8 px-2"
              >
                <span className="text-xs">Minimize</span>
              </Button>
              
              <Button
                onClick={handleDismiss}
                variant="ghost"
                size="sm"
                className="text-white hover:bg-white/10 h-8 w-8 p-0"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Expanded Info for Desktop */}
          <div className="hidden lg:block mt-2 pt-2 border-t border-white/20">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-6">
                <span className="flex items-center gap-1">
                  <Star className="h-4 w-4" />
                  Unlimited AI conversations
                </span>
                <span className="flex items-center gap-1">
                  <Rocket className="h-4 w-4" />
                  Restaurant search & mapping  
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  Demo ends at launch
                </span>
              </div>
              
              <div className="text-xs opacity-90">
                Experience NutriTame before anyone else • No payment required
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Demo Notice Alert (shown once at app start) */}
      {!sessionStorage.getItem('demo_notice_shown') && (
        <Alert className="mx-4 my-2 bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
          <TestTube className="h-4 w-4" />
          <AlertDescription>
            <div className="flex items-center justify-between">
              <div>
                <strong>Welcome to NutriTame Demo!</strong> You have full access to all premium features. 
                After launch on <strong>{demoConfig?.launch_date && formatDate(demoConfig.launch_date)}</strong>, 
                subscription plans will be required.
              </div>
              <Button
                onClick={() => {
                  sessionStorage.setItem('demo_notice_shown', 'true');
                  // Force re-render by updating a dummy state
                  setDemoConfig({...demoConfig});
                }}
                variant="outline"
                size="sm"
                className="ml-4 whitespace-nowrap"
              >
                Got it
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      )}
    </>
  );
};

export default DemoModeBanner;