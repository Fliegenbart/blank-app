import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, X, Clock } from 'lucide-react';
import { MCQChallenge as MCQChallengeType } from '../../types';
import Button from '../ui/Button';

interface MCQChallengeProps {
  challenge: MCQChallengeType;
  onSubmit: (answer: string, timeSpent: number) => void;
}

export default function MCQChallenge({ challenge, onSubmit }: MCQChallengeProps) {
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [timeSpent, setTimeSpent] = useState(0);
  const [showFeedback, setShowFeedback] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeSpent((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    // Reset state when challenge changes
    setSelectedOption(null);
    setTimeSpent(0);
    setShowFeedback(false);
  }, [challenge.id]);

  const handleSubmit = () => {
    if (!selectedOption) return;

    setShowFeedback(true);

    // Delay navigation to show feedback
    setTimeout(() => {
      onSubmit(selectedOption, timeSpent);
    }, 1500);
  };

  const getOptionStyle = (optionId: string) => {
    if (!showFeedback) {
      return selectedOption === optionId
        ? 'border-primary-500 bg-primary-500/10'
        : 'border-dark-border hover:border-primary-500/50';
    }

    const option = challenge.options.find((o) => o.id === optionId);
    if (option?.isCorrect) {
      return 'border-green-500 bg-green-500/10';
    }
    if (selectedOption === optionId && !option?.isCorrect) {
      return 'border-red-500 bg-red-500/10';
    }
    return 'border-dark-border opacity-50';
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      {/* Timer */}
      <div className="flex items-center justify-between">
        <span className="px-3 py-1 rounded-full bg-dark-card border border-dark-border text-sm text-gray-400">
          Multiple Choice
        </span>
        <div className="flex items-center space-x-2 text-gray-400">
          <Clock className="w-4 h-4" />
          <span className="text-sm font-mono">{formatTime(timeSpent)}</span>
        </div>
      </div>

      {/* Question */}
      <div className="card">
        <h3 className="text-lg font-medium text-white mb-6 whitespace-pre-wrap">
          {challenge.question}
        </h3>

        {/* Options */}
        <div className="space-y-3">
          <AnimatePresence>
            {challenge.options.map((option, index) => (
              <motion.button
                key={option.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                onClick={() => !showFeedback && setSelectedOption(option.id)}
                disabled={showFeedback}
                className={`w-full p-4 rounded-lg border text-left transition-all duration-200 ${getOptionStyle(
                  option.id
                )}`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="w-8 h-8 rounded-lg bg-dark-bg flex items-center justify-center text-sm font-medium text-gray-400">
                      {option.id.toUpperCase()}
                    </span>
                    <span className="text-gray-200 font-mono text-sm">{option.text}</span>
                  </div>
                  {showFeedback && option.isCorrect && (
                    <Check className="w-5 h-5 text-green-500" />
                  )}
                  {showFeedback && selectedOption === option.id && !option.isCorrect && (
                    <X className="w-5 h-5 text-red-500" />
                  )}
                </div>
              </motion.button>
            ))}
          </AnimatePresence>
        </div>
      </div>

      {/* Submit Button */}
      <div className="flex justify-end">
        <Button
          onClick={handleSubmit}
          disabled={!selectedOption || showFeedback}
          isLoading={showFeedback}
          size="lg"
        >
          {showFeedback ? 'Wird ausgewertet...' : 'Antwort abschicken'}
        </Button>
      </div>

      {/* Feedback */}
      <AnimatePresence>
        {showFeedback && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className={`p-4 rounded-lg border ${
              challenge.options.find((o) => o.id === selectedOption)?.isCorrect
                ? 'bg-green-500/10 border-green-500/30'
                : 'bg-red-500/10 border-red-500/30'
            }`}
          >
            <div className="flex items-center space-x-2">
              {challenge.options.find((o) => o.id === selectedOption)?.isCorrect ? (
                <>
                  <Check className="w-5 h-5 text-green-500" />
                  <span className="text-green-400 font-medium">Richtig!</span>
                </>
              ) : (
                <>
                  <X className="w-5 h-5 text-red-500" />
                  <span className="text-red-400 font-medium">Leider falsch</span>
                </>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
