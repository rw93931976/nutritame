import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { CheckCircle, ArrowRight } from 'lucide-react';
import { API } from './config';

const PaymentSuccess = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [sessionData, setSessionData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    
    if (sessionId) {
      // Verify the payment session
      fetch(`${API}/payments/verify-session/${sessionId}`)
        .then(response => response.json())
        .then(data => {
          setSessionData(data);
          setLoading(false);
        })
        .catch(error => {
          console.error('Error verifying payment:', error);
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, [searchParams]);

  const handleContinue = () => {
    navigate('/');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-cyan-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Verifying your payment...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-cyan-50 to-blue-50 flex items-center justify-center p-4">
      <Card className="max-w-md w-full shadow-xl border-0 bg-white/90 backdrop-blur-sm">
        <CardHeader className="text-center bg-gradient-to-r from-emerald-50 to-blue-50 rounded-t-lg">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-emerald-100 to-blue-100 flex items-center justify-center">
            <CheckCircle className="h-8 w-8 text-emerald-600" />
          </div>
          <CardTitle className="text-2xl text-gray-800">Payment Successful!</CardTitle>
          <CardDescription className="text-gray-600">
            Welcome to NutriTame Premium
          </CardDescription>
        </CardHeader>
        <CardContent className="p-6 text-center space-y-6">
          <div className="space-y-4">
            <p className="text-gray-700">
              Thank you for your purchase! Your premium subscription is now active.
            </p>
            
            {sessionData && (
              <div className="bg-gradient-to-r from-emerald-50 to-blue-50 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-800 mb-2">Subscription Details</h3>
                <div className="text-sm text-gray-600 space-y-1">
                  <p><strong>Plan:</strong> {sessionData.plan_name || 'Premium'}</p>
                  <p><strong>Amount:</strong> ${(sessionData.amount_total / 100).toFixed(2)}</p>
                  <p><strong>Status:</strong> Active</p>
                </div>
              </div>
            )}
            
            <div className="space-y-2 text-sm text-gray-600">
              <p>✅ Unlimited AI health coaching</p>
              <p>✅ Advanced restaurant search</p>
              <p>✅ Smart shopping lists</p>
              <p>✅ Recipe favorites & export</p>
              <p>✅ Priority support</p>
            </div>
          </div>

          <Button 
            onClick={handleContinue}
            className="w-full bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700 text-white font-semibold py-3"
          >
            Continue to Dashboard
            <ArrowRight className="h-4 w-4 ml-2" />
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default PaymentSuccess;