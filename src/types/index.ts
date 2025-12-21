// User types
export type UserRole = 'candidate' | 'recruiter' | 'admin';

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  company?: string;
  avatarUrl?: string;
  createdAt: Date;
}

// Skill types
export type SkillCategory = 'tech' | 'soft' | 'business';
export type AssessmentType = 'mcq' | 'code' | 'scenario' | 'practical';
export type Difficulty = 'easy' | 'medium' | 'hard';
export type SkillLevel = 'junior' | 'mid' | 'senior' | 'expert';

export interface Skill {
  id: string;
  name: string;
  category: SkillCategory;
  subcategory: string;
  description: string;
  assessmentTypes: AssessmentType[];
  estimatedMinutes: number;
  iconName: string;
  color: string;
}

// Challenge types
export interface TestCase {
  input: string;
  expectedOutput: string;
  isHidden: boolean;
}

export interface MCQOption {
  id: string;
  text: string;
  isCorrect: boolean;
}

export interface ChallengeBase {
  id: string;
  skillId: string;
  difficulty: Difficulty;
  question: string;
  timeLimit: number; // in seconds
}

export interface MCQChallenge extends ChallengeBase {
  type: 'mcq';
  options: MCQOption[];
}

export interface CodeChallenge extends ChallengeBase {
  type: 'code';
  starterCode: string;
  testCases: TestCase[];
  language: string;
}

export interface ScenarioChallenge extends ChallengeBase {
  type: 'scenario';
  evaluationCriteria: string;
}

export type Challenge = MCQChallenge | CodeChallenge | ScenarioChallenge;

// Assessment session types
export interface ChallengeAttempt {
  challengeId: string;
  answer: string;
  timeSpent: number; // in seconds
  score: number;
  feedback?: string;
  isCorrect?: boolean;
}

export interface AssessmentSession {
  id: string;
  skillId: string;
  startedAt: Date;
  completedAt?: Date;
  currentChallengeIndex: number;
  challenges: Challenge[];
  attempts: ChallengeAttempt[];
  finalScore?: number;
  level?: SkillLevel;
}

// Verified skill (Badge)
export interface VerifiedSkill {
  id: string;
  skillId: string;
  skillName: string;
  score: number;
  level: SkillLevel;
  verifiedAt: Date;
  expiresAt: Date;
  iconName: string;
  color: string;
}

// User profile
export interface UserProfile {
  id: string;
  name: string;
  avatarUrl?: string;
  bio?: string;
  location?: string;
  verifiedSkills: VerifiedSkill[];
  isPublic: boolean;
}

// Assessment invitation (for recruiters)
export interface AssessmentInvitation {
  id: string;
  recruiterId: string;
  candidateEmail: string;
  requiredSkills: {
    skillId: string;
    minScore: number;
  }[];
  jobTitle: string;
  message?: string;
  status: 'pending' | 'started' | 'completed' | 'expired';
  createdAt: Date;
  expiresAt: Date;
}

// API response types
export interface EvaluationResult {
  totalScore: number;
  correctness: number;
  quality: number;
  efficiency: number;
  feedback: string;
  level: SkillLevel;
}

// Helper function to determine level from score
export function getLevelFromScore(score: number): SkillLevel {
  if (score >= 90) return 'expert';
  if (score >= 75) return 'senior';
  if (score >= 50) return 'mid';
  return 'junior';
}

// Helper function to get level label in German
export function getLevelLabel(level: SkillLevel): string {
  const labels: Record<SkillLevel, string> = {
    junior: 'Junior',
    mid: 'Mid-Level',
    senior: 'Senior',
    expert: 'Experte',
  };
  return labels[level];
}

// Helper function to get difficulty label
export function getDifficultyLabel(difficulty: Difficulty): string {
  const labels: Record<Difficulty, string> = {
    easy: 'Leicht',
    medium: 'Mittel',
    hard: 'Schwer',
  };
  return labels[difficulty];
}
