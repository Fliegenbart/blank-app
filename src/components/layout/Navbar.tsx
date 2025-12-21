import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Award, User, Menu, X } from 'lucide-react';
import { useState } from 'react';
import { useStore } from '../../store';

export default function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();
  const { verifiedSkills } = useStore();

  const navLinks = [
    { path: '/', label: 'Skills' },
    { path: '/profile', label: 'Mein Profil' },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <motion.div
              whileHover={{ rotate: 360 }}
              transition={{ duration: 0.5 }}
              className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center"
            >
              <Award className="w-6 h-6 text-white" />
            </motion.div>
            <span className="text-xl font-bold gradient-text">SkillVerify</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`relative py-2 text-sm font-medium transition-colors ${
                  isActive(link.path)
                    ? 'text-primary-400'
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                {link.label}
                {isActive(link.path) && (
                  <motion.div
                    layoutId="navbar-indicator"
                    className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500 rounded-full"
                  />
                )}
              </Link>
            ))}
          </div>

          {/* Skill Count Badge */}
          <div className="hidden md:flex items-center space-x-4">
            {verifiedSkills.length > 0 && (
              <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-primary-500/10 border border-primary-500/20">
                <Award className="w-4 h-4 text-primary-400" />
                <span className="text-sm text-primary-400 font-medium">
                  {verifiedSkills.length} verifiziert
                </span>
              </div>
            )}
            <Link
              to="/profile"
              className="w-10 h-10 rounded-full bg-dark-card border border-dark-border flex items-center justify-center hover:border-primary-500/50 transition-colors"
            >
              <User className="w-5 h-5 text-gray-400" />
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-dark-card transition-colors"
          >
            {isMenuOpen ? (
              <X className="w-6 h-6 text-gray-300" />
            ) : (
              <Menu className="w-6 h-6 text-gray-300" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="md:hidden glass border-t border-white/10"
        >
          <div className="px-4 py-4 space-y-2">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                onClick={() => setIsMenuOpen(false)}
                className={`block px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                  isActive(link.path)
                    ? 'bg-primary-500/10 text-primary-400'
                    : 'text-gray-300 hover:bg-dark-card hover:text-white'
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>
        </motion.div>
      )}
    </nav>
  );
}
