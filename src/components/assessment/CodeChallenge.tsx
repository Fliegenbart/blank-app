import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Editor from '@monaco-editor/react';
import { Clock, Play, Check, X, Loader2 } from 'lucide-react';
import { CodeChallenge as CodeChallengeType } from '../../types';
import Button from '../ui/Button';

interface CodeChallengeProps {
  challenge: CodeChallengeType;
  onSubmit: (answer: string, timeSpent: number) => void;
}

interface TestResult {
  input: string;
  expected: string;
  passed: boolean;
}

export default function CodeChallenge({ challenge, onSubmit }: CodeChallengeProps) {
  const [code, setCode] = useState(challenge.starterCode);
  const [timeSpent, setTimeSpent] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeSpent((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    setCode(challenge.starterCode);
    setTimeSpent(0);
    setTestResults([]);
    setShowResults(false);
  }, [challenge.id]);

  const runTests = () => {
    setIsRunning(true);
    setShowResults(false);

    // Simulate test execution
    setTimeout(() => {
      const results: TestResult[] = challenge.testCases
        .filter((tc) => !tc.isHidden)
        .map((tc) => ({
          input: tc.input,
          expected: tc.expectedOutput,
          // Simulate random pass/fail based on code content
          passed: code.length > 50 && Math.random() > 0.3,
        }));

      setTestResults(results);
      setShowResults(true);
      setIsRunning(false);
    }, 1500);
  };

  const handleSubmit = () => {
    setIsRunning(true);

    setTimeout(() => {
      onSubmit(code, timeSpent);
    }, 500);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getLanguage = () => {
    switch (challenge.language) {
      case 'python':
        return 'python';
      case 'javascript':
        return 'javascript';
      case 'typescript':
        return 'typescript';
      case 'sql':
        return 'sql';
      default:
        return 'javascript';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <span className="px-3 py-1 rounded-full bg-secondary-500/10 border border-secondary-500/20 text-sm text-secondary-400">
            Code Challenge
          </span>
          <span className="px-3 py-1 rounded-full bg-dark-card border border-dark-border text-sm text-gray-400 capitalize">
            {challenge.language}
          </span>
        </div>
        <div className="flex items-center space-x-2 text-gray-400">
          <Clock className="w-4 h-4" />
          <span className="text-sm font-mono">{formatTime(timeSpent)}</span>
        </div>
      </div>

      {/* Question */}
      <div className="card">
        <h3 className="text-lg font-medium text-white whitespace-pre-wrap">
          {challenge.question}
        </h3>
      </div>

      {/* Code Editor */}
      <div className="card p-0 overflow-hidden">
        <div className="border-b border-dark-border px-4 py-2 flex items-center justify-between">
          <span className="text-sm text-gray-400">Editor</span>
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={runTests}
              disabled={isRunning}
              leftIcon={isRunning ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            >
              Tests ausführen
            </Button>
          </div>
        </div>
        <Editor
          height="300px"
          language={getLanguage()}
          value={code}
          onChange={(value) => setCode(value || '')}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            fontFamily: 'JetBrains Mono, monospace',
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 2,
            padding: { top: 16, bottom: 16 },
          }}
        />
      </div>

      {/* Test Cases */}
      <div className="card">
        <h4 className="text-sm font-medium text-gray-300 mb-4">Testfälle</h4>
        <div className="space-y-3">
          {challenge.testCases
            .filter((tc) => !tc.isHidden)
            .map((tc, index) => {
              const result = testResults[index];
              return (
                <div
                  key={index}
                  className={`p-3 rounded-lg border ${
                    result
                      ? result.passed
                        ? 'border-green-500/30 bg-green-500/5'
                        : 'border-red-500/30 bg-red-500/5'
                      : 'border-dark-border bg-dark-bg'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-gray-500">Test {index + 1}</span>
                    {result && (
                      <span
                        className={`flex items-center space-x-1 text-xs ${
                          result.passed ? 'text-green-400' : 'text-red-400'
                        }`}
                      >
                        {result.passed ? (
                          <>
                            <Check className="w-3 h-3" />
                            <span>Bestanden</span>
                          </>
                        ) : (
                          <>
                            <X className="w-3 h-3" />
                            <span>Fehlgeschlagen</span>
                          </>
                        )}
                      </span>
                    )}
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500 text-xs">Input:</span>
                      <code className="block font-mono text-gray-300 mt-1">{tc.input}</code>
                    </div>
                    <div>
                      <span className="text-gray-500 text-xs">Erwartete Ausgabe:</span>
                      <code className="block font-mono text-gray-300 mt-1">{tc.expectedOutput}</code>
                    </div>
                  </div>
                </div>
              );
            })}
          <div className="p-3 rounded-lg border border-dark-border bg-dark-bg opacity-50">
            <div className="flex items-center space-x-2 text-gray-500 text-sm">
              <span className="text-xs">+ {challenge.testCases.filter((tc) => tc.isHidden).length} versteckte Tests</span>
            </div>
          </div>
        </div>
      </div>

      {/* Submit Button */}
      <div className="flex justify-end space-x-4">
        <Button
          variant="secondary"
          onClick={runTests}
          disabled={isRunning}
          leftIcon={<Play className="w-4 h-4" />}
        >
          Tests ausführen
        </Button>
        <Button
          onClick={handleSubmit}
          disabled={isRunning}
          isLoading={isRunning}
          size="lg"
        >
          Lösung einreichen
        </Button>
      </div>
    </motion.div>
  );
}
