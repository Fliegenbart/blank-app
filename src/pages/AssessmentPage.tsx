import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Clock, Award } from 'lucide-react';
import { getSkillById } from '../data/skills';
import { useStore } from '../store';
import MCQChallenge from '../components/assessment/MCQChallenge';
import CodeChallenge from '../components/assessment/CodeChallenge';
import ProgressBar from '../components/ui/ProgressBar';
import Button from '../components/ui/Button';
import DynamicIcon from '../components/ui/DynamicIcon';

export default function AssessmentPage() {
  const { skillId } = useParams<{ skillId: string }>();
  const navigate = useNavigate();
  const {
    currentSession,
    startAssessment,
    submitAnswer,
    getCurrentChallenge,
    resetAssessment,
  } = useStore();

  const [isStarted, setIsStarted] = useState(false);
  const skill = skillId ? getSkillById(skillId) : null;

  useEffect(() => {
    // Clean up on unmount
    return () => {
      if (!currentSession?.completedAt) {
        resetAssessment();
      }
    };
  }, []);

  if (!skill) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <h1 className="text-2xl font-bold text-white mb-4">Skill nicht gefunden</h1>
        <Link to="/" className="text-primary-400 hover:underline">
          Zurück zur Übersicht
        </Link>
      </div>
    );
  }

  const handleStart = () => {
    startAssessment(skill.id);
    setIsStarted(true);
  };

  const handleSubmit = (answer: string, timeSpent: number) => {
    submitAnswer(answer, timeSpent);

    // Check if assessment is complete
    const session = useStore.getState().currentSession;
    if (session && session.currentChallengeIndex >= session.challenges.length) {
      navigate(`/result/${skill.id}`);
    }
  };

  const currentChallenge = getCurrentChallenge();

  // Start screen
  if (!isStarted || !currentSession) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8">
        <Link
          to="/"
          className="inline-flex items-center space-x-2 text-gray-400 hover:text-white transition-colors mb-8"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Zurück</span>
        </Link>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card text-center"
        >
          <div
            className="w-20 h-20 rounded-2xl mx-auto flex items-center justify-center mb-6"
            style={{ backgroundColor: `${skill.color}20` }}
          >
            <DynamicIcon name={skill.iconName} className="w-10 h-10" style={{ color: skill.color }} />
          </div>

          <h1 className="text-2xl font-bold text-white mb-2">{skill.name} Assessment</h1>
          <p className="text-gray-400 mb-6">{skill.description}</p>

          <div className="flex justify-center space-x-8 mb-8">
            <div className="text-center">
              <div className="flex items-center justify-center space-x-2 text-gray-300 mb-1">
                <Clock className="w-4 h-4" />
                <span className="font-medium">~{skill.estimatedMinutes} Min.</span>
              </div>
              <span className="text-xs text-gray-500">Geschätzte Zeit</span>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center space-x-2 text-gray-300 mb-1">
                <Award className="w-4 h-4" />
                <span className="font-medium">6 Challenges</span>
              </div>
              <span className="text-xs text-gray-500">5 MCQ + 1 Code</span>
            </div>
          </div>

          <div className="bg-dark-bg rounded-lg p-4 mb-8 text-left">
            <h3 className="text-sm font-medium text-gray-300 mb-3">Was dich erwartet:</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li className="flex items-start space-x-2">
                <span className="text-primary-400">•</span>
                <span>5 Multiple-Choice Fragen mit steigender Schwierigkeit</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="text-primary-400">•</span>
                <span>1 praktische Code-Challenge im Editor</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="text-primary-400">•</span>
                <span>KI-basierte Bewertung deiner Lösungen</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="text-primary-400">•</span>
                <span>Sofortiges Ergebnis mit detailliertem Feedback</span>
              </li>
            </ul>
          </div>

          <Button onClick={handleStart} size="lg" className="w-full">
            Assessment starten
          </Button>
        </motion.div>
      </div>
    );
  }

  // Assessment in progress
  if (!currentChallenge) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto" />
        <p className="text-gray-400 mt-4">Wird geladen...</p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div
            className="w-10 h-10 rounded-lg flex items-center justify-center"
            style={{ backgroundColor: `${skill.color}20` }}
          >
            <DynamicIcon name={skill.iconName} className="w-5 h-5" style={{ color: skill.color }} />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-white">{skill.name}</h1>
            <span className="text-sm text-gray-500">Assessment</span>
          </div>
        </div>
      </div>

      {/* Progress */}
      <ProgressBar
        current={currentSession.currentChallengeIndex + 1}
        total={currentSession.challenges.length}
        className="mb-8"
      />

      {/* Challenge */}
      <AnimatePresence mode="wait">
        {currentChallenge.type === 'mcq' ? (
          <MCQChallenge
            key={currentChallenge.id}
            challenge={currentChallenge}
            onSubmit={handleSubmit}
          />
        ) : currentChallenge.type === 'code' ? (
          <CodeChallenge
            key={currentChallenge.id}
            challenge={currentChallenge}
            onSubmit={handleSubmit}
          />
        ) : null}
      </AnimatePresence>
    </div>
  );
}
