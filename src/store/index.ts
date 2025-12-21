import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import {
  AssessmentSession,
  VerifiedSkill,
  Challenge,
  ChallengeAttempt,
  getLevelFromScore,
  User
} from '../types';
import { getAssessmentChallenges } from '../data/challenges';
import { getSkillById } from '../data/skills';
// Simple UUID generator
const generateId = (): string => {
  return Math.random().toString(36).substring(2, 9) + Date.now().toString(36);
};

interface AppState {
  // User
  user: User | null;
  setUser: (user: User | null) => void;

  // Assessment
  currentSession: AssessmentSession | null;
  startAssessment: (skillId: string) => void;
  submitAnswer: (answer: string, timeSpent: number) => void;
  getCurrentChallenge: () => Challenge | null;
  completeAssessment: () => VerifiedSkill | null;
  resetAssessment: () => void;

  // Verified Skills
  verifiedSkills: VerifiedSkill[];
  addVerifiedSkill: (skill: VerifiedSkill) => void;
  getVerifiedSkillBySkillId: (skillId: string) => VerifiedSkill | undefined;

  // UI State
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

export const useStore = create<AppState>()(
  persist(
    (set, get) => ({
      // User
      user: null,
      setUser: (user) => set({ user }),

      // Assessment
      currentSession: null,

      startAssessment: (skillId: string) => {
        const challenges = getAssessmentChallenges(skillId);
        const session: AssessmentSession = {
          id: generateId(),
          skillId,
          startedAt: new Date(),
          currentChallengeIndex: 0,
          challenges,
          attempts: [],
        };
        set({ currentSession: session });
      },

      submitAnswer: (answer: string, timeSpent: number) => {
        const { currentSession } = get();
        if (!currentSession) return;

        const currentChallenge = currentSession.challenges[currentSession.currentChallengeIndex];
        if (!currentChallenge) return;

        // Calculate score based on challenge type
        let score = 0;
        let isCorrect = false;
        let feedback = '';

        if (currentChallenge.type === 'mcq') {
          const selectedOption = currentChallenge.options.find(o => o.id === answer);
          isCorrect = selectedOption?.isCorrect || false;
          score = isCorrect ? 100 : 0;
          feedback = isCorrect ? 'Richtig!' : 'Leider falsch.';
        } else if (currentChallenge.type === 'code') {
          // Simulate code evaluation (in real app, this would be API call)
          // For demo, we give partial credit based on code length and complexity
          const codeLength = answer.trim().length;
          const hasFunction = answer.includes('function') || answer.includes('def') || answer.includes('=>');
          const hasReturn = answer.includes('return');

          if (codeLength > 50 && hasFunction && hasReturn) {
            score = 75 + Math.floor(Math.random() * 25);
            feedback = 'Gute Loesung! Code-Struktur und Logik sind solide.';
            isCorrect = true;
          } else if (codeLength > 20 && hasFunction) {
            score = 50 + Math.floor(Math.random() * 25);
            feedback = 'Ansatz ist korrekt, aber die Implementierung koennte verbessert werden.';
            isCorrect = true;
          } else if (codeLength > 10) {
            score = 25 + Math.floor(Math.random() * 25);
            feedback = 'Ein Anfang ist gemacht, aber die Loesung ist unvollstaendig.';
          } else {
            score = 0;
            feedback = 'Die Loesung ist zu kurz oder fehlt wichtige Elemente.';
          }
        }

        const attempt: ChallengeAttempt = {
          challengeId: currentChallenge.id,
          answer,
          timeSpent,
          score,
          feedback,
          isCorrect,
        };

        const nextIndex = currentSession.currentChallengeIndex + 1;
        const isCompleted = nextIndex >= currentSession.challenges.length;

        set({
          currentSession: {
            ...currentSession,
            currentChallengeIndex: nextIndex,
            attempts: [...currentSession.attempts, attempt],
            completedAt: isCompleted ? new Date() : undefined,
          },
        });
      },

      getCurrentChallenge: () => {
        const { currentSession } = get();
        if (!currentSession) return null;
        return currentSession.challenges[currentSession.currentChallengeIndex] || null;
      },

      completeAssessment: () => {
        const { currentSession, addVerifiedSkill } = get();
        if (!currentSession || currentSession.attempts.length === 0) return null;

        // Calculate final score
        const totalScore = currentSession.attempts.reduce((sum, a) => sum + a.score, 0);
        const avgScore = Math.round(totalScore / currentSession.attempts.length);
        const level = getLevelFromScore(avgScore);

        const skill = getSkillById(currentSession.skillId);
        if (!skill) return null;

        const verifiedSkill: VerifiedSkill = {
          id: generateId(),
          skillId: currentSession.skillId,
          skillName: skill.name,
          score: avgScore,
          level,
          verifiedAt: new Date(),
          expiresAt: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000), // 1 year
          iconName: skill.iconName,
          color: skill.color,
        };

        // Update session with final score
        set({
          currentSession: {
            ...currentSession,
            finalScore: avgScore,
            level,
          },
        });

        // Add to verified skills
        addVerifiedSkill(verifiedSkill);

        return verifiedSkill;
      },

      resetAssessment: () => {
        set({ currentSession: null });
      },

      // Verified Skills
      verifiedSkills: [],

      addVerifiedSkill: (skill: VerifiedSkill) => {
        const { verifiedSkills } = get();
        // Remove existing skill with same skillId (update instead of duplicate)
        const filtered = verifiedSkills.filter(s => s.skillId !== skill.skillId);
        set({ verifiedSkills: [...filtered, skill] });
      },

      getVerifiedSkillBySkillId: (skillId: string) => {
        const { verifiedSkills } = get();
        return verifiedSkills.find(s => s.skillId === skillId);
      },

      // UI State
      isLoading: false,
      setIsLoading: (loading: boolean) => set({ isLoading: loading }),
    }),
    {
      name: 'skillverify-storage',
      partialize: (state) => ({
        user: state.user,
        verifiedSkills: state.verifiedSkills,
      }),
    }
  )
);
