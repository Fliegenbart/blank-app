import { Skill } from '../types';

export const skills: Skill[] = [
  {
    id: 'python',
    name: 'Python',
    category: 'tech',
    subcategory: 'Programmiersprachen',
    description: 'Allgemeine Programmierung, Datenstrukturen, OOP und Python-spezifische Konzepte',
    assessmentTypes: ['mcq', 'code'],
    estimatedMinutes: 15,
    iconName: 'FileCode2',
    color: '#3776AB',
  },
  {
    id: 'javascript',
    name: 'JavaScript',
    category: 'tech',
    subcategory: 'Programmiersprachen',
    description: 'Modernes JavaScript (ES6+), DOM-Manipulation, Async/Await und TypeScript-Grundlagen',
    assessmentTypes: ['mcq', 'code'],
    estimatedMinutes: 15,
    iconName: 'Braces',
    color: '#F7DF1E',
  },
  {
    id: 'sql',
    name: 'SQL',
    category: 'tech',
    subcategory: 'Datenbanken',
    description: 'SQL-Abfragen, JOINs, Aggregationen, Subqueries und Datenbankdesign',
    assessmentTypes: ['mcq', 'code'],
    estimatedMinutes: 12,
    iconName: 'Database',
    color: '#336791',
  },
  {
    id: 'react',
    name: 'React',
    category: 'tech',
    subcategory: 'Frameworks',
    description: 'React-Komponenten, Hooks, State-Management und moderne React-Patterns',
    assessmentTypes: ['mcq', 'code'],
    estimatedMinutes: 15,
    iconName: 'Atom',
    color: '#61DAFB',
  },
  {
    id: 'git',
    name: 'Git',
    category: 'tech',
    subcategory: 'DevOps',
    description: 'Versionskontrolle, Branching-Strategien, Merge-Konflikte und Git-Workflows',
    assessmentTypes: ['mcq'],
    estimatedMinutes: 10,
    iconName: 'GitBranch',
    color: '#F05032',
  },
];

export const getSkillById = (id: string): Skill | undefined => {
  return skills.find(skill => skill.id === id);
};

export const getSkillsByCategory = (category: string): Skill[] => {
  return skills.filter(skill => skill.category === category);
};
