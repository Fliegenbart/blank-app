import { motion } from 'framer-motion';
import { Clock, ChevronRight, Award } from 'lucide-react';
import { Skill, VerifiedSkill } from '../../types';
import DynamicIcon from './DynamicIcon';

interface SkillCardProps {
  skill: Skill;
  verifiedSkill?: VerifiedSkill;
  onClick: () => void;
  delay?: number;
}

export default function SkillCard({ skill, verifiedSkill, onClick, delay = 0 }: SkillCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.3 }}
      whileHover={{ scale: 1.02, y: -4 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className="card-hover group relative overflow-hidden"
    >
      {/* Background gradient on hover */}
      <div
        className="absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity duration-300"
        style={{
          background: `radial-gradient(circle at top right, ${skill.color}40, transparent 50%)`,
        }}
      />

      {/* Verified badge */}
      {verifiedSkill && (
        <div className="absolute top-4 right-4">
          <div className="flex items-center space-x-1 px-2 py-1 rounded-full bg-green-500/10 border border-green-500/20">
            <Award className="w-3 h-3 text-green-400" />
            <span className="text-xs font-medium text-green-400">{verifiedSkill.score}</span>
          </div>
        </div>
      )}

      <div className="relative">
        {/* Icon */}
        <div
          className="w-12 h-12 rounded-xl flex items-center justify-center mb-4 transition-transform group-hover:scale-110"
          style={{ backgroundColor: `${skill.color}20` }}
        >
          <DynamicIcon name={skill.iconName} className="w-6 h-6" style={{ color: skill.color }} />
        </div>

        {/* Content */}
        <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-primary-400 transition-colors">
          {skill.name}
        </h3>
        <p className="text-sm text-gray-400 mb-4 line-clamp-2">{skill.description}</p>

        {/* Meta */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-1 text-gray-500 text-sm">
            <Clock className="w-4 h-4" />
            <span>~{skill.estimatedMinutes} Min.</span>
          </div>
          <div className="flex items-center text-primary-400 text-sm font-medium group-hover:translate-x-1 transition-transform">
            <span>{verifiedSkill ? 'Erneut testen' : 'Starten'}</span>
            <ChevronRight className="w-4 h-4" />
          </div>
        </div>
      </div>
    </motion.div>
  );
}
