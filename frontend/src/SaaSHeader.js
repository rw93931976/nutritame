import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Badge } from './components/ui/badge';
import { 
  ChefHat, 
  User, 
  LogOut, 
  Crown, 
  Calendar, 
  Settings, 
  HelpCircle,
  Bell
} from 'lucide-react';

const SaaSHeader = ({ user, subscriptionInfo, onLogout }) => {
  const [showUserMenu, setShowUserMenu] = useState(false);

  const getSubscriptionBadge = () => {
    if (!subscriptionInfo) return null;

    const { subscription_status, subscription_tier, remaining_days } = subscriptionInfo;

    if (subscription_status === 'trial') {
      return (
        <Badge className="bg-blue-100 text-blue-800 hover:bg-blue-200">
          <Calendar className="h-3 w-3 mr-1" />
          Trial ({remaining_days} days left)
        </Badge>
      );
    }

    if (subscription_status === 'active') {
      return (
        <Badge className={`${
          subscription_tier === 'premium' 
            ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white' 
            : 'bg-green-100 text-green-800 hover:bg-green-200'
        }`}>
          {subscription_tier === 'premium' && <Crown className="h-3 w-3 mr-1" />}
          {subscription_tier === 'premium' ? 'Premium' : 'Basic'}
        </Badge>
      );
    }

    return (
      <Badge className="bg-red-100 text-red-800">
        Subscription Expired
      </Badge>
    );
  };

  const getWelcomeMessage = () => {
    if (!subscriptionInfo) return "Welcome to NutriTame";

    const { subscription_status, remaining_days } = subscriptionInfo;

    if (subscription_status === 'trial') {
      if (remaining_days <= 3) {
        return "Trial ending soon - upgrade to continue!";
      }
      return `Enjoying your trial? ${remaining_days} days remaining`;
    }

    if (subscription_status === 'active') {
      return "Welcome back to NutriTame";
    }

    return "Please renew your subscription to continue";
  };

  return (
    <header className="bg-white/95 backdrop-blur-md shadow-sm border-b sticky top-0 z-50">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Logo and Brand */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-600 to-blue-600 flex items-center justify-center">
              <ChefHat className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-emerald-600 to-blue-600 bg-clip-text text-transparent">
                NutriTame
              </h1>
              <p className="text-xs text-gray-600 hidden sm:block">
                {getWelcomeMessage()}
              </p>
            </div>
          </div>

          {/* User Info and Controls */}
          <div className="flex items-center gap-4">
            {/* Subscription Badge */}
            {getSubscriptionBadge()}

            {/* Notifications (placeholder) */}
            <Button 
              variant="ghost" 
              size="sm" 
              className="relative"
              onClick={() => {
                // Show notifications or alert
                if (subscriptionInfo?.subscription_status === 'trial' && subscriptionInfo?.remaining_days <= 3) {
                  alert(`Trial notification: Your trial expires in ${subscriptionInfo.remaining_days} day${subscriptionInfo.remaining_days !== 1 ? 's' : ''}! Consider upgrading to continue using NutriTame.`);
                } else {
                  alert('No new notifications. Notification system coming soon!');
                }
              }}
            >
              <Bell className="h-4 w-4" />
              {subscriptionInfo?.subscription_status === 'trial' && subscriptionInfo?.remaining_days <= 3 && (
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></div>
              )}
            </Button>

            {/* User Menu */}
            <div className="relative">
              <Button
                variant="ghost"
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-2"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-100 to-blue-100 flex items-center justify-center">
                  <User className="h-4 w-4 text-emerald-600" />
                </div>
                <span className="hidden sm:block text-sm font-medium">
                  {user?.email?.split('@')[0] || 'User'}
                </span>
              </Button>

              {/* User Dropdown Menu */}
              {showUserMenu && (
                <Card className="absolute right-0 top-12 w-72 shadow-lg z-50">
                  <CardHeader className="pb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-full bg-gradient-to-br from-emerald-100 to-blue-100 flex items-center justify-center">
                        <User className="h-6 w-6 text-emerald-600" />
                      </div>
                      <div>
                        <CardTitle className="text-sm">{user?.email}</CardTitle>
                        <CardDescription className="text-xs">
                          Member since {new Date(user?.created_at).toLocaleDateString()}
                        </CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  
                  <CardContent className="space-y-3">
                    {/* Subscription Info */}
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">Subscription</span>
                        {getSubscriptionBadge()}
                      </div>
                      
                      {subscriptionInfo && (
                        <div className="text-xs text-gray-600 space-y-1">
                          <div>Plan: {subscriptionInfo.plan_name}</div>
                          <div>Price: ${subscriptionInfo.plan_price}/month</div>
                          {subscriptionInfo.subscription_status === 'trial' && (
                            <div className="text-blue-600 font-medium">
                              {subscriptionInfo.remaining_days} trial days remaining
                            </div>
                          )}
                        </div>
                      )}
                    </div>

                    {/* Quick Actions */}
                    <div className="space-y-2">
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="w-full justify-start"
                        onClick={() => {
                          setShowUserMenu(false);
                          // Navigate to profile/account settings
                          window.location.hash = '#profile-settings';
                          // For now, show an alert since full account settings page isn't implemented
                          alert('Account Settings feature coming soon! Use the "← Back to Profile" button in the dashboard to edit your profile.');
                        }}
                      >
                        <Settings className="h-4 w-4 mr-2" />
                        Account Settings
                      </Button>
                      
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="w-full justify-start"
                        onClick={() => {
                          setShowUserMenu(false);
                          // Open help in new tab or show help modal
                          window.open('mailto:support@nutritame.com?subject=Help Request from NutriTame', '_blank');
                        }}
                      >
                        <HelpCircle className="h-4 w-4 mr-2" />
                        Help & Support
                      </Button>

                      {subscriptionInfo?.subscription_status === 'trial' && subscriptionInfo?.remaining_days <= 5 && (
                        <Button 
                          size="sm" 
                          className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                          onClick={() => {
                            setShowUserMenu(false);
                            // Navigate to upgrade page or show pricing
                            alert('Upgrade functionality coming soon! Contact support@nutritame.com for early upgrade options.');
                          }}
                        >
                          <Crown className="h-4 w-4 mr-2" />
                          Upgrade to Premium
                        </Button>
                      )}
                      
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
                        onClick={onLogout}
                      >
                        <LogOut className="h-4 w-4 mr-2" />
                        Sign Out
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>

        {/* Trial Warning Banner */}
        {subscriptionInfo?.subscription_status === 'trial' && subscriptionInfo?.remaining_days <= 3 && (
          <div className="mt-3 p-3 bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-yellow-600" />
                <span className="text-sm font-medium text-yellow-800">
                  Trial expires in {subscriptionInfo.remaining_days} day{subscriptionInfo.remaining_days !== 1 ? 's' : ''}!
                </span>
              </div>
              <Button size="sm" className="bg-gradient-to-r from-yellow-600 to-orange-600 hover:from-yellow-700 hover:to-orange-700">
                Upgrade Now
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Click outside to close menu */}
      {showUserMenu && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setShowUserMenu(false)}
        ></div>
      )}
    </header>
  );
};

export default SaaSHeader;