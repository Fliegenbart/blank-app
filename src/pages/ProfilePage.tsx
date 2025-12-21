import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Award, Share2, Download, Plus, Calendar, Star } from 'lucide-react';
import { useStore } from '../store';
import { getLevelLabel, VerifiedSkill } from '../types';
import Button from '../components/ui/Button';
import DynamicIcon from '../components/ui/DynamicIcon';

export default function ProfilePage() {
  const { verifiedSkills } = useStore();

  const handleShare = async () => {
    const shareData = {
      title: 'Mein SkillVerify Profil',
      text: `Ich habe ${verifiedSkills.length} verifizierte Skills auf SkillVerify!`,
      url: window.location.href,
    };

    try {
      if (navigator.share) {
        await navigator.share(shareData);
      } else {
        await navigator.clipboard.writeText(shareData.url);
        alert('Link wurde in die Zwischenablage kopiert!');
      }
    } catch (err) {
      console.error('Share failed:', err);
    }
  };

  const handleExportPDF = () => {
    // In a real app, this would generate a PDF
    alert('PDF-Export wird in Kürze verfügbar sein!');
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Profile Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card mb-8"
      >
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex items-center space-x-4">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-3xl font-bold text-white">
              S
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Skill-Profil</h1>
              <p className="text-gray-400">Deine verifizierten Kompetenzen</p>
            </div>
          </div>
          <div className="flex flex-wrap gap-3">
            <Button
              variant="secondary"
              onClick={handleShare}
              leftIcon={<Share2 className="w-4 h-4" />}
            >
              Teilen
            </Button>
            <Button
              variant="secondary"
              onClick={handleExportPDF}
              leftIcon={<Download className="w-4 h-4" />}
            >
              Als PDF
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mt-8 pt-8 border-t border-dark-border">
          <div className="text-center">
            <div className="text-3xl font-bold gradient-text">{verifiedSkills.length}</div>
            <div className="text-sm text-gray-500">Verifizierte Skills</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-white">
              {verifiedSkills.length > 0
                ? Math.round(verifiedSkills.reduce((sum, s) => sum + s.score, 0) / verifiedSkills.length)
                : 0}
            </div>
            <div className="text-sm text-gray-500">Durchschnitt</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-white">
              {verifiedSkills.filter((s) => s.level === 'senior' || s.level === 'expert').length}
            </div>
            <div className="text-sm text-gray-500">Senior+ Level</div>
          </div>
        </div>
      </motion.div>

      {/* Verified Skills Section */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <Award className="w-5 h-5 text-primary-400" />
            <span>Verifizierte Skills</span>
          </h2>
          <Link to="/">
            <Button variant="ghost" leftIcon={<Plus className="w-4 h-4" />}>
              Skill hinzufügen
            </Button>
          </Link>
        </div>

        {verifiedSkills.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="card text-center py-12"
          >
            <div className="w-16 h-16 rounded-full bg-dark-bg flex items-center justify-center mx-auto mb-4">
              <Award className="w-8 h-8 text-gray-600" />
            </div>
            <h3 className="text-lg font-medium text-white mb-2">Noch keine Skills verifiziert</h3>
            <p className="text-gray-400 mb-6">
              Absolviere dein erstes Assessment und erhalte dein Badge!
            </p>
            <Link to="/">
              <Button leftIcon={<Plus className="w-4 h-4" />}>Skill verifizieren</Button>
            </Link>
          </motion.div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {verifiedSkills.map((skill, index) => (
              <SkillBadge key={skill.id} skill={skill} delay={index * 0.1} />
            ))}
          </div>
        )}
      </div>

      {/* Tips Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="card bg-gradient-to-br from-primary-500/5 to-secondary-500/5 border-primary-500/20"
      >
        <h3 className="text-lg font-semibold text-white mb-4">Tipps für dein Profil</h3>
        <ul className="space-y-3 text-sm text-gray-400">
          <li className="flex items-start space-x-2">
            <Star className="w-4 h-4 text-primary-400 mt-0.5 flex-shrink-0" />
            <span>Verifiziere mindestens 3 Skills für ein vollständiges Profil</span>
          </li>
          <li className="flex items-start space-x-2">
            <Star className="w-4 h-4 text-primary-400 mt-0.5 flex-shrink-0" />
            <span>Skills verfallen nach 12 Monaten – halte sie aktuell</span>
          </li>
          <li className="flex items-start space-x-2">
            <Star className="w-4 h-4 text-primary-400 mt-0.5 flex-shrink-0" />
            <span>Teile dein Profil mit Recruitern für bessere Jobchancen</span>
          </li>
        </ul>
      </motion.div>
    </div>
  );
}

function SkillBadge({ skill, delay }: { skill: VerifiedSkill; delay: number }) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'from-green-500 to-emerald-500';
    if (score >= 60) return 'from-yellow-500 to-orange-500';
    if (score >= 40) return 'from-orange-500 to-red-500';
    return 'from-red-500 to-rose-500';
  };

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      whileHover={{ scale: 1.02 }}
      className="card group"
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-4">
          <div
            className="w-14 h-14 rounded-xl flex items-center justify-center transition-transform group-hover:scale-110"
            style={{ backgroundColor: `${skill.color}20` }}
          >
            <DynamicIcon name={skill.iconName} className="w-7 h-7" style={{ color: skill.color }} />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">{skill.skillName}</h3>
            <div className="flex items-center space-x-2 mt-1">
              <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-primary-500/10 text-primary-400 border border-primary-500/20">
                {getLevelLabel(skill.level)}
              </span>
              <span className="flex items-center space-x-1 text-xs text-gray-500">
                <Calendar className="w-3 h-3" />
                <span>{formatDate(skill.verifiedAt)}</span>
              </span>
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className={`text-2xl font-bold bg-gradient-to-r ${getScoreColor(skill.score)} bg-clip-text text-transparent`}>
            {skill.score}
          </div>
          <div className="text-xs text-gray-500">/ 100</div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mt-4">
        <div className="h-2 bg-dark-bg rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${skill.score}%` }}
            transition={{ delay: delay + 0.3, duration: 0.8 }}
            className={`h-full bg-gradient-to-r ${getScoreColor(skill.score)} rounded-full`}
          />
        </div>
      </div>
    </motion.div>
  );
}
