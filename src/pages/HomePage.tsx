import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Award, Target, Zap, Users } from 'lucide-react';
import SkillCard from '../components/ui/SkillCard';
import { skills } from '../data/skills';
import { useStore } from '../store';

export default function HomePage() {
  const navigate = useNavigate();
  const { verifiedSkills, getVerifiedSkillBySkillId } = useStore();

  const handleSkillClick = (skillId: string) => {
    navigate(`/assessment/${skillId}`);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Hero Section */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center py-16 md:py-24"
      >
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-primary-500/10 border border-primary-500/20 mb-6"
        >
          <Zap className="w-4 h-4 text-primary-400" />
          <span className="text-sm text-primary-400 font-medium">KI-basierte Skill-Verifikation</span>
        </motion.div>

        <h1 className="text-4xl md:text-6xl font-bold mb-6">
          <span className="text-white">Verifiziere deine</span>
          <br />
          <span className="gradient-text">echten Skills</span>
        </h1>

        <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-8">
          Zeig was du kannst – nicht nur was du behauptest.
          Absolviere kurze Assessments und erhalte verifizierte Skill-Badges für dein Profil.
        </p>

        {/* Stats */}
        <div className="flex flex-wrap justify-center gap-8 mb-16">
          <Stat icon={<Target className="w-5 h-5" />} value="5" label="Skills verfügbar" />
          <Stat icon={<Award className="w-5 h-5" />} value={verifiedSkills.length.toString()} label="Verifiziert" />
          <Stat icon={<Users className="w-5 h-5" />} value="1.2k+" label="Nutzer" />
        </div>
      </motion.section>

      {/* Skills Grid */}
      <section className="pb-16">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">Wähle einen Skill</h2>
            <p className="text-gray-400">Starte ein Assessment und erhalte dein Badge</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {skills.map((skill, index) => (
            <SkillCard
              key={skill.id}
              skill={skill}
              verifiedSkill={getVerifiedSkillBySkillId(skill.id)}
              onClick={() => handleSkillClick(skill.id)}
              delay={index * 0.1}
            />
          ))}
        </div>
      </section>

      {/* How it Works */}
      <section className="py-16 border-t border-dark-border">
        <h2 className="text-2xl font-bold text-white text-center mb-12">So funktioniert's</h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            {
              step: '01',
              title: 'Skill auswählen',
              description: 'Wähle einen Skill aus unserem Katalog, den du verifizieren möchtest.',
            },
            {
              step: '02',
              title: 'Assessment absolvieren',
              description: '5-10 Minuten Quiz mit Multiple-Choice und Code-Challenges.',
            },
            {
              step: '03',
              title: 'Badge erhalten',
              description: 'Erhalte dein verifiziertes Badge mit Score und Level.',
            },
          ].map((item, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.2 }}
              className="relative"
            >
              <div className="card text-center">
                <span className="text-5xl font-bold gradient-text opacity-20">{item.step}</span>
                <h3 className="text-lg font-semibold text-white mt-4 mb-2">{item.title}</h3>
                <p className="text-gray-400 text-sm">{item.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
}

function Stat({ icon, value, label }: { icon: React.ReactNode; value: string; label: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.4 }}
      className="flex items-center space-x-3"
    >
      <div className="w-10 h-10 rounded-lg bg-dark-card border border-dark-border flex items-center justify-center text-primary-400">
        {icon}
      </div>
      <div className="text-left">
        <div className="text-2xl font-bold text-white">{value}</div>
        <div className="text-sm text-gray-500">{label}</div>
      </div>
    </motion.div>
  );
}
