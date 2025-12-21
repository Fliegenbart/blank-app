import { Challenge, MCQChallenge, CodeChallenge } from '../types';

// Python Challenges
const pythonChallenges: Challenge[] = [
  {
    id: 'py-mcq-1',
    skillId: 'python',
    type: 'mcq',
    difficulty: 'easy',
    question: 'Was ist der Output von `print(type([]))`?',
    timeLimit: 30,
    options: [
      { id: 'a', text: "<class 'tuple'>", isCorrect: false },
      { id: 'b', text: "<class 'list'>", isCorrect: true },
      { id: 'c', text: "<class 'array'>", isCorrect: false },
      { id: 'd', text: "<class 'set'>", isCorrect: false },
    ],
  } as MCQChallenge,
  {
    id: 'py-mcq-2',
    skillId: 'python',
    type: 'mcq',
    difficulty: 'easy',
    question: 'Welches Keyword wird verwendet, um eine Funktion in Python zu definieren?',
    timeLimit: 30,
    options: [
      { id: 'a', text: 'function', isCorrect: false },
      { id: 'b', text: 'def', isCorrect: true },
      { id: 'c', text: 'func', isCorrect: false },
      { id: 'd', text: 'lambda', isCorrect: false },
    ],
  } as MCQChallenge,
  {
    id: 'py-mcq-3',
    skillId: 'python',
    type: 'mcq',
    difficulty: 'medium',
    question: 'Was ist der Unterschied zwischen `is` und `==` in Python?',
    timeLimit: 45,
    options: [
      { id: 'a', text: 'Sie sind identisch und austauschbar', isCorrect: false },
      { id: 'b', text: '`is` vergleicht Identität (Speicheradresse), `==` vergleicht Werte', isCorrect: true },
      { id: 'c', text: '`is` ist schneller als `==`', isCorrect: false },
      { id: 'd', text: '`==` kann nur für Zahlen verwendet werden', isCorrect: false },
    ],
  } as MCQChallenge,
  {
    id: 'py-mcq-4',
    skillId: 'python',
    type: 'mcq',
    difficulty: 'medium',
    question: 'Was ist ein Python Decorator?',
    timeLimit: 45,
    options: [
      { id: 'a', text: 'Ein Muster zum Erstellen von Klassen', isCorrect: false },
      { id: 'b', text: 'Eine Funktion, die eine andere Funktion modifiziert oder erweitert', isCorrect: true },
      { id: 'c', text: 'Ein Tool zur Code-Formatierung', isCorrect: false },
      { id: 'd', text: 'Eine Art von Datenstruktur', isCorrect: false },
    ],
  } as MCQChallenge,
  {
    id: 'py-mcq-5',
    skillId: 'python',
    type: 'mcq',
    difficulty: 'hard',
    question: 'Was ist das Ergebnis von `[x*2 for x in range(5) if x % 2 == 0]`?',
    timeLimit: 60,
    options: [
      { id: 'a', text: '[0, 2, 4, 6, 8]', isCorrect: false },
      { id: 'b', text: '[0, 4, 8]', isCorrect: true },
      { id: 'c', text: '[2, 4, 6, 8]', isCorrect: false },
      { id: 'd', text: '[0, 2, 4]', isCorrect: false },
    ],
  } as MCQChallenge,
  {
    id: 'py-code-1',
    skillId: 'python',
    type: 'code',
    difficulty: 'medium',
    question: 'Schreibe eine Funktion `reverse_string(s)`, die einen String umkehrt, ohne `[::-1]` oder die `reverse()` Methode zu verwenden.',
    timeLimit: 300,
    language: 'python',
    starterCode: `def reverse_string(s: str) -> str:
    # Dein Code hier
    pass

# Beispiel:
# reverse_string("hello") -> "olleh"
# reverse_string("Python") -> "nohtyP"`,
    testCases: [
      { input: '"hello"', expectedOutput: '"olleh"', isHidden: false },
      { input: '""', expectedOutput: '""', isHidden: false },
      { input: '"a"', expectedOutput: '"a"', isHidden: true },
      { input: '"Python"', expectedOutput: '"nohtyP"', isHidden: true },
    ],
  } as CodeChallenge,
];

// JavaScript Challenges
const javascriptChallenges: Challenge[] = [
  {
    id: 'js-mcq-1',
    skillId: 'javascript',
    type: 'mcq',
    difficulty: 'easy',
    question: 'Was ist der Unterschied zwischen `let` und `const`?',
    timeLimit: 30,
    options: [
      { id: 'a', text: 'Es gibt keinen Unterschied', isCorrect: false },
      { id: 'b', text: '`const` kann nicht neu zugewiesen werden, `let` schon', isCorrect: true },
      { id: 'c', text: '`let` ist schneller als `const`', isCorrect: false },
      { id: 'd', text: '`const` existiert nicht in JavaScript', isCorrect: false },
    ],
  } as MCQChallenge,
  {
    id: 'js-mcq-2',
    skillId: 'javascript',
    type: 'mcq',
    difficulty: 'easy',
    question: 'Was gibt `typeof null` zurück?',
    timeLimit: 30,
    options: [
      { id: 'a', text: '"null"', isCorrect: false },
      { id: 'b', text: '"undefined"', isCorrect: false },
      { id: 'c', text: '"object"', isCorrect: true },
      { id: 'd', text: '"boolean"', isCorrect: false },
    ],
  } as MCQChallenge,
  {
    id: 'js-mcq-3',
    skillId: 'javascript',
    type: 'mcq',
    difficulty: 'medium',
    question: 'Was ist das Ergebnis von `Promise.resolve(1).then(x => x + 1).then(x => { throw new Error() }).catch(() => 3)`?',
    timeLimit: 60,
    options: [
      { id: 'a', text: 'Promise<1>', isCorrect: false },
      { id: 'b', text: 'Promise<2>', isCorrect: false },
      { id: 'c', text: 'Promise<3>', isCorrect: true },
      { id: 'd', text: 'Error', isCorrect: false },
    ],
  } as MCQChallenge,
  {
    id: 'js-mcq-4',
    skillId: 'javascript',
    type: 'mcq',
    difficulty: 'medium',
    question: 'Was ist Closures in JavaScript?',
    timeLimit: 45,
    options: [
      { id: 'a', text: 'Eine Methode zum Schliessen von Browserfenstern', isCorrect: false },
      { id: 'b', text: 'Eine Funktion, die Zugriff auf Variablen aus ihrem aeusseren Scope behält', isCorrect: true },
      { id: 'c', text: 'Eine Art von Schleife', isCorrect: false },
      { id: 'd', text: 'Ein Designpattern für Module', isCorrect: false },
    ],
  } as MCQChallenge,
  {
    id: 'js-mcq-5',
    skillId: 'javascript',
    type: 'mcq',
    difficulty: 'hard',
    question: 'Was ist der Output von `console.log([1,2,3].map(parseInt))`?',
    timeLimit: 60,
    options: [
      { id: 'a', text: '[1, 2, 3]', isCorrect: false },
      { id: 'b', text: '[1, NaN, NaN]', isCorrect: true },
      { id: 'c', text: '[NaN, NaN, NaN]', isCorrect: false },
      { id: 'd', text: 'Error', isCorrect: false },
    ],
  } as MCQChallenge,
  {
    id: 'js-code-1',
    skillId: 'javascript',
    type: 'code',
    difficulty: 'medium',
    question: 'Schreibe eine Funktion `debounce(fn, delay)`, die eine "debounced" Version der übergebenen Funktion zurückgibt. Die Funktion soll erst ausgeführt werden, wenn sie für `delay` Millisekunden nicht mehr aufgerufen wurde.',
    timeLimit: 300,
    language: 'javascript',
    starterCode: `function debounce(fn, delay) {
  // Dein Code hier
}

// Beispiel:
// const debouncedLog = debounce(console.log, 1000);
// debouncedLog("Hallo"); // Wartet 1 Sekunde, dann log`,
    testCases: [
      { input: 'debounce(x => x, 100)', expectedOutput: 'function', isHidden: false },
      { input: 'typeof debounce(() => {}, 100)', expectedOutput: '"function"', isHidden: false },
    ],
  } as CodeChallenge,
];

// SQL Challenges
const sqlChallenges: Challenge[] = [
  {
    id: 'sql-mcq-1',
    skillId: 'sql',
    type: 'mcq',
    difficulty: 'easy',
    question: 'Welches SQL-Keyword wird verwendet, um Duplikate aus den Ergebnissen zu entfernen?',
    timeLimit: 30,
    options: [
      { id: 'a', text: 'UNIQUE', isCorrect: false },
      { id: 'b', text: 'DISTINCT', isCorrect: true },
      { id: 'c', text: 'DIFFERENT', isCorrect: false },
      { id: 'd', text: 'SINGLE', isCorrect: false },
    ],
  } as MCQChallenge,
  {
    id: 'sql-mcq-2',
    skillId: 'sql',
    type: 'mcq',
    difficulty: 'easy',
    question: 'Was macht der `INNER JOIN`?',
    timeLimit: 30,
    options: [
      { id: 'a', text: 'Gibt alle Zeilen aus beiden Tabellen zurück', isCorrect: false },
      { id: 'b', text: 'Gibt nur übereinstimmende Zeilen aus beiden Tabellen zurück', isCorrect: true },
      { id: 'c', text: 'Gibt alle Zeilen aus der linken Tabelle zurück', isCorrect: false },
      { id: 'd', text: 'Verbindet Tabellen ohne Bedingung', isCorrect: false },
    ],
  } as MCQChallenge,
  {
    id: 'sql-mcq-3',
    skillId: 'sql',
    type: 'mcq',
    difficulty: 'medium',
    question: 'Was ist der Unterschied zwischen `WHERE` und `HAVING`?',
    timeLimit: 45,
    options: [
      { id: 'a', text: 'Sie sind identisch', isCorrect: false },
      { id: 'b', text: '`WHERE` filtert vor Gruppierung, `HAVING` filtert nach Gruppierung', isCorrect: true },
      { id: 'c', text: '`HAVING` ist schneller als `WHERE`', isCorrect: false },
      { id: 'd', text: '`WHERE` funktioniert nur mit Zahlen', isCorrect: false },
    ],
  } as MCQChallenge,
  {
    id: 'sql-mcq-4',
    skillId: 'sql',
    type: 'mcq',
    difficulty: 'medium',
    question: 'Was macht `COALESCE(a, b, c)` in SQL?',
    timeLimit: 45,
    options: [
      { id: 'a', text: 'Addiert alle Werte', isCorrect: false },
      { id: 'b', text: 'Gibt den ersten Nicht-NULL Wert zurück', isCorrect: true },
      { id: 'c', text: 'Prüft ob alle Werte gleich sind', isCorrect: false },
      { id: 'd', text: 'Erstellt eine neue Spalte', isCorrect: false },
    ],
  } as MCQChallenge,
  {
    id: 'sql-mcq-5',
    skillId: 'sql',
    type: 'mcq',
    difficulty: 'hard',
    question: 'Welche Aussage über Window Functions ist korrekt?',
    timeLimit: 60,
    options: [
      { id: 'a', text: 'Sie reduzieren die Anzahl der Zeilen wie GROUP BY', isCorrect: false },
      { id: 'b', text: 'Sie können nur mit numerischen Spalten verwendet werden', isCorrect: false },
      { id: 'c', text: 'Sie berechnen Werte über eine Menge von Zeilen, ohne diese zu gruppieren', isCorrect: true },
      { id: 'd', text: 'Sie sind nur in PostgreSQL verfügbar', isCorrect: false },
    ],
  } as MCQChallenge,
  {
    id: 'sql-code-1',
    skillId: 'sql',
    type: 'code',
    difficulty: 'medium',
    question: 'Schreibe eine SQL-Abfrage, die die Top 3 Produkte nach Umsatz aus einer Tabelle `sales` (columns: product_id, product_name, quantity, price) zurückgibt. Der Umsatz ist quantity * price.',
    timeLimit: 300,
    language: 'sql',
    starterCode: `-- Tabelle: sales (product_id, product_name, quantity, price)
-- Gib zurück: product_name, total_revenue
-- Sortiert nach Umsatz (absteigend), Top 3

SELECT
  -- Dein Code hier`,
    testCases: [
      { input: 'SELECT query', expectedOutput: 'product_name, total_revenue, LIMIT 3', isHidden: false },
    ],
  } as CodeChallenge,
];

// React Challenges
const reactChallenges: Challenge[] = [
  {
    id: 'react-mcq-1',
    skillId: 'react',
    type: 'mcq',
    difficulty: 'easy',
    question: 'Was ist der Zweck von `useState` in React?',
    timeLimit: 30,
    options: [
      { id: 'a', text: 'Um API-Aufrufe zu machen', isCorrect: false },
      { id: 'b', text: 'Um lokalen State in funktionalen Komponenten zu verwalten', isCorrect: true },
      { id: 'c', text: 'Um zwischen Seiten zu navigieren', isCorrect: false },
      { id: 'd', text: 'Um CSS-Styles anzuwenden', isCorrect: false },
    ],
  } as MCQChallenge,
  {
    id: 'react-mcq-2',
    skillId: 'react',
    type: 'mcq',
    difficulty: 'easy',
    question: 'Was ist JSX?',
    timeLimit: 30,
    options: [
      { id: 'a', text: 'Eine neue Programmiersprache', isCorrect: false },
      { id: 'b', text: 'Eine Syntax-Erweiterung für JavaScript, die HTML-aehnlichen Code ermoeglicht', isCorrect: true },
      { id: 'c', text: 'Ein CSS-Framework', isCorrect: false },
      { id: 'd', text: 'Ein State-Management Tool', isCorrect: false },
    ],
  } as MCQChallenge,
  {
    id: 'react-mcq-3',
    skillId: 'react',
    type: 'mcq',
    difficulty: 'medium',
    question: 'Wann wird `useEffect` mit einem leeren Dependency-Array `[]` aufgerufen?',
    timeLimit: 45,
    options: [
      { id: 'a', text: 'Bei jedem Render', isCorrect: false },
      { id: 'b', text: 'Nur beim initialen Render (Mount)', isCorrect: true },
      { id: 'c', text: 'Niemals', isCorrect: false },
      { id: 'd', text: 'Nur beim Unmount', isCorrect: false },
    ],
  } as MCQChallenge,
  {
    id: 'react-mcq-4',
    skillId: 'react',
    type: 'mcq',
    difficulty: 'medium',
    question: 'Was ist der Unterschied zwischen `useMemo` und `useCallback`?',
    timeLimit: 45,
    options: [
      { id: 'a', text: 'Sie sind identisch', isCorrect: false },
      { id: 'b', text: '`useMemo` memorisiert Werte, `useCallback` memorisiert Funktionen', isCorrect: true },
      { id: 'c', text: '`useCallback` ist schneller', isCorrect: false },
      { id: 'd', text: '`useMemo` funktioniert nur mit Objekten', isCorrect: false },
    ],
  } as MCQChallenge,
  {
    id: 'react-mcq-5',
    skillId: 'react',
    type: 'mcq',
    difficulty: 'hard',
    question: 'Was verursacht einen Infinite Loop in diesem Code?\n`useEffect(() => { setCount(count + 1) })`',
    timeLimit: 60,
    options: [
      { id: 'a', text: 'Fehlendes Dependency-Array - Effect läuft bei jedem Render', isCorrect: true },
      { id: 'b', text: 'setCount ist nicht definiert', isCorrect: false },
      { id: 'c', text: 'count muss ein Objekt sein', isCorrect: false },
      { id: 'd', text: 'useEffect kann setCount nicht aufrufen', isCorrect: false },
    ],
  } as MCQChallenge,
  {
    id: 'react-code-1',
    skillId: 'react',
    type: 'code',
    difficulty: 'medium',
    question: 'Erstelle einen Custom Hook `useLocalStorage(key, initialValue)`, der Werte im localStorage speichert und bei Änderungen automatisch aktualisiert.',
    timeLimit: 300,
    language: 'typescript',
    starterCode: `import { useState } from 'react';

function useLocalStorage<T>(key: string, initialValue: T) {
  // Dein Code hier
  // Tipp: Verwende useState mit einer Initialisierungsfunktion
}

// Beispiel:
// const [name, setName] = useLocalStorage('name', 'Max');
// setName('Lisa'); // Speichert 'Lisa' im localStorage unter 'name'`,
    testCases: [
      { input: 'useLocalStorage("test", "value")', expectedOutput: '[value, function]', isHidden: false },
    ],
  } as CodeChallenge,
];

// Git Challenges
const gitChallenges: Challenge[] = [
  {
    id: 'git-mcq-1',
    skillId: 'git',
    type: 'mcq',
    difficulty: 'easy',
    question: 'Welcher Befehl zeigt den aktuellen Status des Repositories?',
    timeLimit: 30,
    options: [
      { id: 'a', text: 'git show', isCorrect: false },
      { id: 'b', text: 'git status', isCorrect: true },
      { id: 'c', text: 'git log', isCorrect: false },
      { id: 'd', text: 'git info', isCorrect: false },
    ],
  } as MCQChallenge,
  {
    id: 'git-mcq-2',
    skillId: 'git',
    type: 'mcq',
    difficulty: 'easy',
    question: 'Was macht `git add .`?',
    timeLimit: 30,
    options: [
      { id: 'a', text: 'Erstellt einen neuen Commit', isCorrect: false },
      { id: 'b', text: 'Fügt alle geaenderten Dateien zur Staging Area hinzu', isCorrect: true },
      { id: 'c', text: 'Pushed zum Remote', isCorrect: false },
      { id: 'd', text: 'Loescht alle Dateien', isCorrect: false },
    ],
  } as MCQChallenge,
  {
    id: 'git-mcq-3',
    skillId: 'git',
    type: 'mcq',
    difficulty: 'medium',
    question: 'Was ist der Unterschied zwischen `git merge` und `git rebase`?',
    timeLimit: 45,
    options: [
      { id: 'a', text: 'Sie sind identisch', isCorrect: false },
      { id: 'b', text: 'Merge erstellt einen Merge-Commit, Rebase schreibt die Historie linear um', isCorrect: true },
      { id: 'c', text: 'Rebase ist immer sicherer', isCorrect: false },
      { id: 'd', text: 'Merge funktioniert nur lokal', isCorrect: false },
    ],
  } as MCQChallenge,
  {
    id: 'git-mcq-4',
    skillId: 'git',
    type: 'mcq',
    difficulty: 'medium',
    question: 'Was macht `git stash`?',
    timeLimit: 45,
    options: [
      { id: 'a', text: 'Loescht alle Aenderungen permanent', isCorrect: false },
      { id: 'b', text: 'Speichert Aenderungen temporaer und stellt einen sauberen Working Directory her', isCorrect: true },
      { id: 'c', text: 'Erstellt einen neuen Branch', isCorrect: false },
      { id: 'd', text: 'Zeigt die Commit-Historie', isCorrect: false },
    ],
  } as MCQChallenge,
  {
    id: 'git-mcq-5',
    skillId: 'git',
    type: 'mcq',
    difficulty: 'hard',
    question: 'Wie kannst du den letzten Commit rueckgaengig machen, aber die Aenderungen behalten?',
    timeLimit: 60,
    options: [
      { id: 'a', text: 'git revert HEAD', isCorrect: false },
      { id: 'b', text: 'git reset --soft HEAD~1', isCorrect: true },
      { id: 'c', text: 'git checkout HEAD~1', isCorrect: false },
      { id: 'd', text: 'git undo', isCorrect: false },
    ],
  } as MCQChallenge,
  {
    id: 'git-mcq-6',
    skillId: 'git',
    type: 'mcq',
    difficulty: 'hard',
    question: 'Was bedeutet ein "detached HEAD" Zustand?',
    timeLimit: 60,
    options: [
      { id: 'a', text: 'Git ist beschaedigt', isCorrect: false },
      { id: 'b', text: 'HEAD zeigt direkt auf einen Commit statt auf einen Branch', isCorrect: true },
      { id: 'c', text: 'Der Remote ist nicht erreichbar', isCorrect: false },
      { id: 'd', text: 'Es gibt ungespeicherte Aenderungen', isCorrect: false },
    ],
  } as MCQChallenge,
];

// All challenges by skill
export const challengesBySkill: Record<string, Challenge[]> = {
  python: pythonChallenges,
  javascript: javascriptChallenges,
  sql: sqlChallenges,
  react: reactChallenges,
  git: gitChallenges,
};

// Get challenges for a skill
export const getChallengesForSkill = (skillId: string): Challenge[] => {
  return challengesBySkill[skillId] || [];
};

// Get a random set of challenges for an assessment
export const getAssessmentChallenges = (skillId: string, count: number = 6): Challenge[] => {
  const allChallenges = getChallengesForSkill(skillId);
  const mcqChallenges = allChallenges.filter(c => c.type === 'mcq');
  const codeChallenges = allChallenges.filter(c => c.type === 'code');

  // Shuffle MCQ challenges
  const shuffledMcq = [...mcqChallenges].sort(() => Math.random() - 0.5);

  // Take 5 MCQ + 1 Code challenge (if available)
  const selectedMcq = shuffledMcq.slice(0, Math.min(5, count - (codeChallenges.length > 0 ? 1 : 0)));
  const selectedCode = codeChallenges.length > 0 ? [codeChallenges[0]] : [];

  return [...selectedMcq, ...selectedCode];
};
