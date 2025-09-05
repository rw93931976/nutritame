import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Alert, AlertDescription } from './components/ui/alert';
import { AlertTriangle, Check } from 'lucide-react';
import { api } from './apiClient';

const MedicalDisclaimer = ({ onAccept, onDecline }) => {
  const [hasRead, setHasRead] = useState(false);
  const [scrolledToBottom, setScrolledToBottom] = useState(false);

  const handleScroll = (e) => {
    const { scrollTop, scrollHeight, clientHeight } = e.target;
    // More lenient scroll detection - consider scrolled if user scrolled at least 70%
    const scrollPercent = (scrollTop + clientHeight) / scrollHeight;
    if (scrollPercent >= 0.7) {
      setScrolledToBottom(true);
    }
  };

  useEffect(() => {
    // Check if user has already accepted disclaimer in this session
    const disclaimerAccepted = sessionStorage.getItem('medical_disclaimer_accepted');
    if (disclaimerAccepted === 'true') {
      onAccept();
    }
    
    // Auto-detect if content is already fully visible (for smaller screens)
    const checkIfContentVisible = () => {
      const scrollContainer = document.querySelector('[data-disclaimer-scroll]');
      if (scrollContainer) {
        const { scrollHeight, clientHeight } = scrollContainer;
        if (scrollHeight <= clientHeight + 20) {
          // Content is already fully visible
          setScrolledToBottom(true);
        }
      }
    };
    
    // Check after a longer delay to ensure DOM and CSS layout are ready (production timing)
    setTimeout(checkIfContentVisible, 500);
    
    // Add a retry mechanism to handle production timing issues
    const retryCheck = () => {
      setTimeout(() => {
        if (!scrolledToBottom) {
          checkIfContentVisible();
        }
      }, 1000);
    };
    retryCheck();
  }, [onAccept]);

  const handleAccept = () => {
    sessionStorage.setItem('medical_disclaimer_accepted', 'true');
    onAccept();
  };

  const handleDecline = () => {
    sessionStorage.setItem('medical_disclaimer_declined', 'true');
    onDecline();
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card className="max-w-3xl w-full max-h-[90vh] flex flex-col shadow-2xl">
        <CardHeader className="text-center border-b bg-gradient-to-r from-red-50 to-orange-50">
          <div className="flex items-center justify-center gap-3 mb-2">
            <AlertTriangle className="h-8 w-8 text-red-600" />
            <CardTitle className="text-2xl font-bold text-red-700">
              IMPORTANT MEDICAL DISCLAIMER
            </CardTitle>
          </div>
        </CardHeader>
        
        <CardContent className="flex-1 overflow-hidden flex flex-col p-6">
          <div 
            className="flex-1 overflow-y-auto pr-2 space-y-4 text-gray-700 leading-relaxed"
            onScroll={handleScroll}
            data-disclaimer-scroll="true"
          >
            <div className="text-lg font-semibold text-red-600 mb-4">
              ⚠️ Please Read Carefully Before Using NutriTame
            </div>
            
            <p className="text-base">
              <strong>This application provides meal planning guidance and nutritional information for educational purposes only. This is NOT medical advice</strong>
            </p>
            
            <p className="text-base">
              <strong>and should never be used as a substitute for professional medical care, diagnosis, or treatment. NutriTame does not diagnose, treat, cure, or prevent any medical conditions or diseases.</strong>
            </p>

            <Alert className="border-red-200 bg-red-50">
              <AlertTriangle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800 font-medium">
                <strong>CRITICAL SAFETY INFORMATION:</strong>
              </AlertDescription>
            </Alert>

            <div className="space-y-3 text-sm">
              <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                <h3 className="font-semibold text-yellow-800 mb-2">🩺 Medical Professional Consultation Required</h3>
                <ul className="space-y-1 text-yellow-700">
                  <li>• Always consult your healthcare provider before making dietary changes</li>
                  <li>• Never stop or modify medications based on app recommendations</li>
                  <li>• Seek immediate medical attention for concerning symptoms</li>
                  <li>• Regular medical monitoring is essential for diabetes management</li>
                </ul>
              </div>

              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <h3 className="font-semibold text-blue-800 mb-2">📊 Nutritional Information Limitations</h3>
                <ul className="space-y-1 text-blue-700">
                  <li>• Nutritional data may not be 100% accurate</li>
                  <li>• Individual dietary needs vary significantly</li>
                  <li>• Food allergies and intolerances are serious - verify all ingredients</li>
                  <li>• Portion sizes should be confirmed with healthcare providers</li>
                </ul>
              </div>

              <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                <h3 className="font-semibold text-purple-800 mb-2">⚕️ Diabetes Management Reminders</h3>
                <ul className="space-y-1 text-purple-700">
                  <li>• Monitor blood glucose levels as directed by your doctor</li>
                  <li>• This app does not replace blood sugar testing equipment</li>
                  <li>• Emergency medical conditions require immediate professional care</li>
                  <li>• Medication timing and dosage should never be app-determined</li>
                </ul>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <h3 className="font-semibold text-gray-800 mb-2">🚫 Liability and Responsibility</h3>
                <p className="text-gray-700">
                  By using NutriTame, you acknowledge that you are solely responsible for your health decisions. 
                  The developers, AI providers, and service operators are not liable for any health outcomes 
                  resulting from app usage. This tool is meant to support, not replace, professional medical care.
                </p>
              </div>
            </div>

            {!scrolledToBottom && (
              <div className="text-center text-sm text-gray-500 animate-pulse">
                ↓ Please scroll to read the complete disclaimer ↓
              </div>
            )}
          </div>

          <div className="mt-6 pt-4 border-t">
            <div className="mb-4">
              <label className="flex items-center gap-3 cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={hasRead} 
                  onChange={(e) => setHasRead(e.target.checked)}
                  className="w-4 h-4 text-emerald-600 rounded focus:ring-emerald-500"
                />
                <span className="text-sm font-medium text-gray-700">
                  I have read and understand this medical disclaimer
                </span>
              </label>
            </div>
            
            <div className="flex gap-3 justify-center">
              <Button
                onClick={handleDecline}
                variant="outline"
                className="px-8 py-2 border-gray-300 text-gray-700 hover:bg-gray-50"
              >
                Decline & Exit
              </Button>
              <Button
                onClick={handleAccept}
                disabled={!hasRead || !scrolledToBottom}
                className="px-8 py-2 bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700 text-white disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Check className="h-4 w-4 mr-2" />
                Accept & Continue
              </Button>
            </div>
            
            {(!hasRead || !scrolledToBottom) && (
              <p className="text-xs text-gray-500 text-center mt-2">
                Please read the complete disclaimer and check the box to continue
              </p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default MedicalDisclaimer;