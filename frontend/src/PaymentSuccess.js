import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Badge } from './components/ui/badge';
import { CheckCircle, Loader2, AlertCircle, ChefHat, Calendar, Star } from 'lucide-react';

const API = import.meta.env.REACT_APP_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;

const PaymentSuccess = ({ onAccessApp }) => {
  const [status, setStatus] = useState('checking'); // checking, success, error
  const [paymentData, setPaymentData] = useState(null);
  const [countdown, setCountdown] = useState(3);

  // Get URL parameters
  const getUrlParameter = (name) => {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    const results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
  };

  // Poll payment status
  const pollPaymentStatus = async (sessionId, attempts = 0) => {
    const maxAttempts = 10;
    const pollInterval = 2000; // 2 seconds

    if (attempts >= maxAttempts) {
      setStatus('error');
      return;
    }

    try {
      const response = await fetch(`${API}/payments/status/${sessionId}`);
      if (!response.ok) {
        throw new Error('Failed to check payment status');
      }

      const data = await response.json();
      
      if (data.payment_status === 'paid') {
        setStatus('success');
        setPaymentData(data);
        
        // Start countdown to auto-redirect
        let count = 3;
        const countdownInterval = setInterval(() => {
          count--;
          setCountdown(count);
          if (count <= 0) {
            clearInterval(countdownInterval);
            onAccessApp(data);
          }
        }, 1000);
        
        return;
      } else if (data.status === 'expired') {
        setStatus('error');
        return;
      }

      // If payment is still pending, continue polling
      setTimeout(() => pollPaymentStatus(sessionId, attempts + 1), pollInterval);
    } catch (error) {
      console.error('Error checking payment status:', error);
      setStatus('error');
    }
  };

  useEffect(() => {
    const sessionId = getUrlParameter('session_id');
    if (sessionId) {
      pollPaymentStatus(sessionId);
    } else {
      setStatus('error');
    }
  }, []);

  const handleAccessApp = () => {
    if (paymentData) {
      onAccessApp(paymentData);
    }
  };

  if (status === 'checking') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-blue-50 to-purple-50 flex items-center justify-center">
        <Card className="w-full max-w-md mx-4">
          <CardHeader className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-emerald-100 to-blue-100 flex items-center justify-center">
              <Loader2 className="h-8 w-8 text-emerald-600 animate-spin" />
            </div>
            <CardTitle className="text-2xl">Processing Payment</CardTitle>
            <CardDescription>
              Please wait while we confirm your payment...
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <p className="text-gray-600">
              This should only take a few seconds. Please don't close this window.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-blue-50 to-purple-50 flex items-center justify-center">
        <Card className="w-full max-w-md mx-4">
          <CardHeader className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
              <AlertCircle className="h-8 w-8 text-red-600" />
            </div>
            <CardTitle className="text-2xl text-red-600">Payment Issue</CardTitle>
            <CardDescription>
              There was an issue processing your payment.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-gray-600 text-center">
              Please check your email for payment confirmation, or contact our support team if you need assistance.
            </p>
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                className="flex-1"
                onClick={() => window.location.href = '/'}
              >
                Back to Home
              </Button>
              <Button 
                className="flex-1 bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700"
                onClick={() => window.location.href = 'mailto:support@glucoplanner.com'}
              >
                Contact Support
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-blue-50 to-purple-50 flex items-center justify-center">
      <Card className="w-full max-w-lg mx-4">
        <CardHeader className="text-center">
          <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-emerald-100 to-blue-100 flex items-center justify-center">
            <CheckCircle className="h-12 w-12 text-emerald-600" />
          </div>
          <CardTitle className="text-3xl text-gray-900 mb-2">
            Welcome to GlucoPlanner! 🎉
          </CardTitle>
          <CardDescription className="text-lg">
            Your payment was successful and your account is ready.
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Subscription Details */}
          <div className="bg-gradient-to-r from-emerald-50 to-blue-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-900">Subscription Details</h3>
              <Badge className="bg-gradient-to-r from-emerald-600 to-blue-600 text-white">
                <Star className="h-3 w-3 mr-1" />
                {paymentData?.subscription_tier === 'premium' ? 'Premium' : 'Basic'}
              </Badge>
            </div>
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-600">Plan:</span>
                <p className="font-medium capitalize">{paymentData?.subscription_tier} Plan</p>
              </div>
              <div>
                <span className="text-gray-600">Amount:</span>
                <p className="font-medium">${(paymentData?.amount_total / 100).toFixed(2)}</p>
              </div>
              <div>
                <span className="text-gray-600">Trial Period:</span>
                <p className="font-medium flex items-center gap-1">
                  <Calendar className="h-4 w-4" />
                  15 days free
                </p>
              </div>
              <div>
                <span className="text-gray-600">Status:</span>
                <p className="font-medium text-emerald-600">Active Trial</p>
              </div>
            </div>
          </div>

          {/* What's Next */}
          <div className="space-y-3">
            <h3 className="font-semibold text-gray-900">What's included in your trial:</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-emerald-600" />
                AI-powered diabetes health coach
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-emerald-600" />
                Restaurant search with diabetic ratings
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-emerald-600" />
                Personalized meal planning
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-emerald-600" />
                Smart shopping list generation
              </li>
              {paymentData?.subscription_tier === 'premium' && (
                <>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-emerald-600" />
                    Unlimited AI conversations
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-emerald-600" />
                    Data export and premium features
                  </li>
                </>
              )}
            </ul>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            <Button
              onClick={handleAccessApp}
              className="w-full h-12 text-lg font-semibold bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700"
            >
              <ChefHat className="h-5 w-5 mr-2" />
              Access Your Dashboard {countdown > 0 && `(${countdown}s)`}
            </Button>
            
            <p className="text-xs text-gray-500 text-center">
              You can also bookmark this page and return anytime during your trial period.
              You'll be charged ${paymentData?.subscription_tier === 'premium' ? '$19' : '$9'}/month after the 15-day trial ends.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PaymentSuccess;