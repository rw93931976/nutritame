import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  Clock, 
  AlertTriangle, 
  RotateCcw, 
  CheckCircle, 
  PlayCircle,
  PauseCircle,
  Zap
} from 'lucide-react';

const DemoCountdownTimer = ({ 
  durationMinutes = 30,
  onTimeExpired = null,
  className = "",
  compact = false 
}) => {
  const [timeLeft, setTimeLeft] = useState(0);
  const [isActive, setIsActive] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [hasExpired, setHasExpired] = useState(false);
  const [sessionStarted, setSessionStarted] = useState(false);

  // Initialize timer from localStorage or set new session
  useEffect(() => {
    const savedStartTime = localStorage.getItem('nutri_demo_start_time');
    const savedPausedTime = localStorage.getItem('nutri_demo_paused_time');
    const totalDemoTime = durationMinutes * 60; // Convert to seconds

    if (savedStartTime && !savedPausedTime) {
      // Resume existing session
      const startTime = parseInt(savedStartTime);
      const elapsed = Math.floor((Date.now() - startTime) / 1000);
      const remaining = Math.max(0, totalDemoTime - elapsed);
      
      if (remaining > 0) {
        setTimeLeft(remaining);
        setIsActive(true);
        setSessionStarted(true);
      } else {
        // Session expired
        setTimeLeft(0);
        setHasExpired(true);
        setIsActive(false);
      }
    } else if (savedPausedTime) {
      // Resume from paused state
      const pausedAt = parseInt(savedPausedTime);
      setTimeLeft(pausedAt);
      setIsPaused(true);
      setSessionStarted(true);
    } else {
      // New session
      setTimeLeft(totalDemoTime);
    }
  }, [durationMinutes]);

  // Timer countdown effect
  useEffect(() => {
    let intervalId;

    if (isActive && timeLeft > 0 && !isPaused) {
      intervalId = setInterval(() => {
        setTimeLeft(time => {
          if (time <= 1) {
            setIsActive(false);
            setHasExpired(true);
            localStorage.removeItem('nutri_demo_start_time');
            localStorage.removeItem('nutri_demo_paused_time');
            if (onTimeExpired) {
              onTimeExpired();
            }
            return 0;
          }
          return time - 1;
        });
      }, 1000);
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [isActive, timeLeft, isPaused, onTimeExpired]);

  const startTimer = useCallback(() => {
    const startTime = Date.now() - ((durationMinutes * 60 - timeLeft) * 1000);
    localStorage.setItem('nutri_demo_start_time', startTime.toString());
    localStorage.removeItem('nutri_demo_paused_time');
    setIsActive(true);
    setIsPaused(false);
    setSessionStarted(true);
  }, [timeLeft, durationMinutes]);

  const pauseTimer = useCallback(() => {
    localStorage.setItem('nutri_demo_paused_time', timeLeft.toString());
    localStorage.removeItem('nutri_demo_start_time');
    setIsActive(false);
    setIsPaused(true);
  }, [timeLeft]);

  const restartDemo = useCallback(() => {
    const newDemoTime = durationMinutes * 60;
    setTimeLeft(newDemoTime);
    setHasExpired(false);
    setIsPaused(false);
    localStorage.removeItem('nutri_demo_start_time');
    localStorage.removeItem('nutri_demo_paused_time');
    
    // Auto-start new session
    const startTime = Date.now();
    localStorage.setItem('nutri_demo_start_time', startTime.toString());
    setIsActive(true);
    setSessionStarted(true);
  }, [durationMinutes]);

  const extendDemo = useCallback(() => {
    const additionalTime = 15 * 60; // 15 more minutes
    const newTime = timeLeft + additionalTime;
    setTimeLeft(newTime);
    setHasExpired(false);
    
    if (!isActive && !isPaused) {
      startTimer();
    }
  }, [timeLeft, isActive, isPaused, startTimer]);

  // Format time display
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Calculate progress percentage
  const progressPercentage = (timeLeft / (durationMinutes * 60)) * 100;

  // Determine warning state
  const getWarningState = () => {
    if (hasExpired) return 'expired';
    if (timeLeft <= 300) return 'critical'; // 5 minutes
    if (timeLeft <= 600) return 'warning'; // 10 minutes
    return 'normal';
  };

  const warningState = getWarningState();

  // Color schemes based on state
  const getColors = () => {
    switch (warningState) {
      case 'expired':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          text: 'text-red-700',
          progress: 'bg-red-500',
          badge: 'bg-red-500'
        };
      case 'critical':
        return {
          bg: 'bg-orange-50',
          border: 'border-orange-200',
          text: 'text-orange-700',
          progress: 'bg-orange-500',
          badge: 'bg-orange-500'
        };
      case 'warning':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          text: 'text-yellow-700',
          progress: 'bg-yellow-500',
          badge: 'bg-yellow-500'
        };
      default:
        return {
          bg: 'bg-emerald-50',
          border: 'border-emerald-200',
          text: 'text-emerald-700',
          progress: 'bg-emerald-500',
          badge: 'bg-emerald-500'
        };
    }
  };

  const colors = getColors();

  // Don't show timer if not started and not expired
  if (!sessionStarted && !hasExpired) {
    return (
      <Card className={`${className} ${colors.bg} ${colors.border} border-2`}>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`p-2 ${colors.badge} rounded-full`}>
                <PlayCircle className="h-5 w-5 text-white" />
              </div>
              <div>
                <h3 className={`font-semibold ${colors.text}`}>Start Demo Session</h3>
                <p className="text-sm text-gray-600">
                  You have {durationMinutes} minutes to explore all features
                </p>
              </div>
            </div>
            <Button
              onClick={startTimer}
              className={`${colors.badge} hover:opacity-90 text-white`}
            >
              <PlayCircle className="h-4 w-4 mr-2" />
              Start Timer
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (compact) {
    return (
      <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full ${colors.bg} ${colors.border} border`}>
        <Clock className={`h-4 w-4 ${colors.text}`} />
        <span className={`text-sm font-mono font-medium ${colors.text}`}>
          {formatTime(timeLeft)}
        </span>
        {warningState === 'critical' && <AlertTriangle className="h-4 w-4 text-orange-500 animate-pulse" />}
      </div>
    );
  }

  return (
    <Card className={`${className} ${colors.bg} ${colors.border} border-2 ${hasExpired ? 'ring-2 ring-red-300 ring-opacity-50' : ''}`}>
      <CardContent className="p-4">
        <div className="space-y-4">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className={`p-2 ${colors.badge} rounded-full ${hasExpired ? 'animate-pulse' : ''}`}>
                {hasExpired ? (
                  <AlertTriangle className="h-5 w-5 text-white" />
                ) : (
                  <Clock className="h-5 w-5 text-white" />
                )}
              </div>
              <div>
                <h3 className={`font-semibold ${colors.text}`}>
                  {hasExpired ? 'Demo Session Expired' : 'Demo Time Remaining'}
                </h3>
                <p className="text-sm text-gray-600">
                  {hasExpired 
                    ? 'Extend or restart to continue exploring'
                    : warningState === 'critical' 
                      ? 'Less than 5 minutes left!'
                      : warningState === 'warning'
                        ? 'Demo ending soon'
                        : 'Enjoy exploring all features'
                  }
                </p>
              </div>
            </div>

            {/* Time Display - Responsive */}
            {!hasExpired && (
              <div className="text-center sm:text-right">
                <div className={`text-xl sm:text-2xl font-mono font-bold ${colors.text} ${warningState === 'critical' ? 'animate-pulse' : ''}`}>
                  {formatTime(timeLeft)}
                </div>
                <Badge variant="outline" className={`${colors.text} text-xs`}>
                  {Math.floor(timeLeft / 60)} min left
                </Badge>
              </div>
            )}
          </div>

          {/* Progress Bar */}
          {!hasExpired && (
            <div className="space-y-2">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full transition-all duration-1000 ${colors.progress}`}
                  style={{ width: `${progressPercentage}%` }}
                />
              </div>
              <div className="flex justify-between text-xs text-gray-500">
                <span>0:00</span>
                <span>{formatTime(durationMinutes * 60)}</span>
              </div>
            </div>
          )}

          {/* Controls */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
            {hasExpired ? (
              <>
                <Button
                  onClick={restartDemo}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white flex-1"
                >
                  <RotateCcw className="h-4 w-4 mr-2" />
                  New Demo ({durationMinutes} min)
                </Button>
                <Button
                  onClick={extendDemo}
                  variant="outline"
                  className="border-emerald-300 text-emerald-700 hover:bg-emerald-50 flex-1 sm:flex-initial"
                >
                  <Zap className="h-4 w-4 mr-2" />
                  Extend (+15 min)
                </Button>
              </>
            ) : (
              <>
                {isActive && !isPaused ? (
                  <Button
                    onClick={pauseTimer}
                    variant="outline"
                    size="sm"
                    className={`${colors.text} hover:bg-gray-100`}
                  >
                    <PauseCircle className="h-4 w-4 mr-1" />
                    <span className="hidden sm:inline">Pause</span>
                  </Button>
                ) : isPaused ? (
                  <Button
                    onClick={startTimer}
                    size="sm"
                    className={`${colors.badge} hover:opacity-90 text-white`}
                  >
                    <PlayCircle className="h-4 w-4 mr-1" />
                    <span className="hidden sm:inline">Resume</span>
                  </Button>
                ) : null}
                
                <Button
                  onClick={extendDemo}
                  variant="outline"
                  size="sm"
                  className="border-emerald-300 text-emerald-700 hover:bg-emerald-50"
                >
                  <Zap className="h-4 w-4 mr-1" />
                  +15 min
                </Button>

                {warningState === 'critical' && (
                  <Badge className="bg-orange-500 text-white animate-pulse">
                    <AlertTriangle className="h-3 w-3 mr-1" />
                    <span className="hidden sm:inline">Hurry!</span>
                    <span className="sm:hidden">!</span>
                  </Badge>
                )}
              </>
            )}
          </div>

          {/* Expired state message */}
          {hasExpired && (
            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start gap-2">
                <CheckCircle className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <h4 className="font-medium text-blue-900">Demo Complete!</h4>
                  <p className="text-sm text-blue-700 mt-1">
                    You've experienced NutriTame's AI-powered diabetes management features. 
                    Ready to continue with full access?
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default DemoCountdownTimer;