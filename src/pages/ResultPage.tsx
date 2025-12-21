import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import confetti from 'canvas-confetti';
import { Award, Share2, RotateCcw, Home, Star, TrendingUp } from 'lucide-react';
import { getSkillById } from '../data/skills';
import { useStore } from '../store';
import { getLevelLabel } from '../types';
import Button from '../components/ui/Button';
import DynamicIcon from '../components/ui/DynamicIcon';

export default function ResultPage() {
  const { skillId } = useParams<{ skillId: string }>();
  const navigate = useNavigate();
  const { currentSession, completeAssessment, resetAssessment, getVerifiedSkillBySkillId } = useStore();
  const [verifiedSkill, setVerifiedSkill] = useState<ReturnType<typeof getVerifiedSkillBySkillId>>(undefined);
  const [hasAnimated, setHasAnimated] = useState(false);

  const skill = skillId ? getSkillById(skillId) : null;

  useEffect(() => {
    if (currentSession && !currentSession.finalScore) {
      const result = completeAssessment();
      if (result) {
        setVerifiedSkill(result);
      }
    } else if (skillId) {
      const existing = getVerifiedSkillBySkillId(skillId);
      setVerifiedSkill(existing);
    }
  }, [currentSession, skillId]);

  useEffect(() => {
    if (verifiedSkill && !hasAnimated && verifiedSkill.score >= 50) {
      // Trigger confetti for passing score
      const end = Date.now() + 2000;
      const colors = ['#8B5CF6', '#06B6D4', '#10B981'];

      (function frame() {
        confetti({
          particleCount: 3,
          angle: 60,
          spread: 55,
          origin: { x: 0 },
          colors: colors,
        });
        confetti({
          particleCount: 3,
          angle: 120,
          spread: 55,
          origin: { x: 1 },
          colors: colors,
        });

        if (Date.now() < end) {
          requestAnimationFrame(frame);
        }
      })();

      setHasAnimated(true);
    }
  }, [verifiedSkill, hasAnimated]);

  if (!skill || !verifiedSkill) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto" />
        <p className="text-gray-400 mt-4">Ergebnis wird berechnet...</p>
      </div>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    if (score >= 40) return 'text-orange-400';
    return 'text-red-400';
  };

  const getScoreMessage = (score: number) => {
    if (score >= 90) return 'Herausragend! Du bist ein Experte.';
    if (score >= 75) return 'Sehr gut! Du hast Senior-Level erreicht.';
    if (score >= 50) return 'Gut gemacht! Solide Mid-Level Kenntnisse.';
    if (score >= 25) return 'Ein guter Anfang. Mit etwas Übung wirst du besser.';
    return 'Nicht aufgeben! Übung macht den Meister.';
  };

  const handleRetry = () => {
    resetAssessment();
    navigate(`/assessment/${skillId}`);
  };

  const handleShare = async () => {
    const shareData = {
      title: 'Mein verifizierter Skill auf SkillVerify',
      text: `Ich habe ${skill.name} mit einem Score von ${verifiedSkill.score}/100 verifiziert!`,
      url: window.location.origin + `/profile`,
    };

    try {
      if (navigator.share) {
        await navigator.share(shareData);
      } else {
        // Fallback: Copy to clipboard
        await navigator.clipboard.writeText(
          `${shareData.text}\n${shareData.url}`
        );
        alert('Link wurde in die Zwischenablage kopiert!');
      }
    } catch (err) {
      console.error('Share failed:', err);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="card text-center"
      >
        {/* Badge Animation */}
        <motion.div
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
          className="relative inline-block mb-6"
        >
          <div
            className="w-32 h-32 rounded-3xl flex items-center justify-center mx-auto animate-glow"
            style={{ backgroundColor: `${skill.color}20` }}
          >
            <DynamicIcon name={skill.iconName} className="w-16 h-16" style={{ color: skill.color }} />
          </div>
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.6, type: 'spring' }}
            className="absolute -top-2 -right-2 w-12 h-12 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center"
          >
            <Award className="w-6 h-6 text-white" />
          </motion.div>
        </motion.div>

        {/* Skill Name */}
        <h1 className="text-3xl font-bold text-white mb-2">{skill.name}</h1>
        <p className="text-gray-400 mb-8">Assessment abgeschlossen!</p>

        {/* Score Circle */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="relative w-48 h-48 mx-auto mb-8"
        >
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
            {/* Background circle */}
            <circle
              cx="50"
              cy="50"
              r="45"
              stroke="currentColor"
              strokeWidth="8"
              fill="none"
              className="text-dark-border"
            />
            {/* Progress circle */}
            <motion.circle
              cx="50"
              cy="50"
              r="45"
              stroke="url(#gradient)"
              strokeWidth="8"
              fill="none"
              strokeLinecap="round"
              initial={{ strokeDasharray: '0 283' }}
              animate={{
                strokeDasharray: `${(verifiedSkill.score / 100) * 283} 283`,
              }}
              transition={{ delay: 0.6, duration: 1.5, ease: 'easeOut' }}
            />
            <defs>
              <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#8B5CF6" />
                <stop offset="100%" stopColor="#06B6D4" />
              </linearGradient>
            </defs>
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <motion.span
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1 }}
              className={`text-5xl font-bold ${getScoreColor(verifiedSkill.score)}`}
            >
              {verifiedSkill.score}
            </motion.span>
            <span className="text-gray-500 text-sm">von 100</span>
          </div>
        </motion.div>

        {/* Level Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-primary-500/10 border border-primary-500/20 mb-6"
        >
          <Star className="w-5 h-5 text-primary-400" />
          <span className="text-primary-400 font-medium">
            {getLevelLabel(verifiedSkill.level)} Level
          </span>
        </motion.div>

        {/* Message */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="text-gray-300 mb-8"
        >
          {getScoreMessage(verifiedSkill.score)}
        </motion.p>

        {/* Stats */}
        {currentSession && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.2 }}
            className="grid grid-cols-3 gap-4 mb-8 p-4 bg-dark-bg rounded-xl"
          >
            <div className="text-center">
              <div className="text-2xl font-bold text-white">
                {currentSession.attempts.filter((a) => a.isCorrect).length}
              </div>
              <div className="text-xs text-gray-500">Richtig</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white">
                {currentSession.attempts.filter((a) => !a.isCorrect).length}
              </div>
              <div className="text-xs text-gray-500">Falsch</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white flex items-center justify-center">
                <TrendingUp className="w-5 h-5 mr-1 text-primary-400" />
                {verifiedSkill.score >= 50 ? '+' : '-'}
              </div>
              <div className="text-xs text-gray-500">Trend</div>
            </div>
          </motion.div>
        )}

        {/* Actions */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.4 }}
          className="flex flex-col sm:flex-row gap-4"
        >
          <Button
            variant="secondary"
            onClick={handleRetry}
            leftIcon={<RotateCcw className="w-4 h-4" />}
            className="flex-1"
          >
            Erneut versuchen
          </Button>
          <Button
            onClick={handleShare}
            leftIcon={<Share2 className="w-4 h-4" />}
            className="flex-1"
          >
            Teilen
          </Button>
        </motion.div>

        <Link
          to="/profile"
          className="inline-flex items-center space-x-2 text-gray-400 hover:text-white transition-colors mt-8"
        >
          <Home className="w-4 h-4" />
          <span>Zum Profil</span>
        </Link>
      </motion.div>
    </div>
  );
}
