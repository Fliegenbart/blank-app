# SkillVerify

Eine KI-basierte Skill-Assessment Plattform, die Kandidaten-Skills durch kurze, adaptive Challenges verifiziert.

## Features

- **5 Tech-Skills**: Python, JavaScript, SQL, React, Git
- **Adaptive Assessments**: Multiple-Choice Fragen + Code-Challenges
- **Monaco Code Editor**: Professioneller Code-Editor im Browser
- **Skill-Badges**: Verifizierte Skills mit Score und Level
- **Shareable Profile**: Teile dein Skill-Profil mit Recruitern
- **Dark Mode**: Modernes, dunkles UI-Design

## Tech-Stack

- **Frontend**: React 19 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Routing**: React Router v7
- **Animations**: Framer Motion
- **Code Editor**: Monaco Editor

## Installation

```bash
# Dependencies installieren
npm install

# Development Server starten
npm run dev

# Production Build erstellen
npm run build

# Preview des Builds
npm run preview
```

## Projektstruktur

```
src/
├── components/
│   ├── assessment/    # MCQ & Code Challenge Komponenten
│   ├── layout/        # Navbar, Layout
│   └── ui/            # Button, Cards, etc.
├── data/              # Mock-Daten für Skills & Challenges
├── pages/             # Seiten-Komponenten
├── store/             # Zustand State Management
└── types/             # TypeScript Interfaces
```

## Verwendung

1. **Skill auswählen**: Wähle einen der 5 verfügbaren Skills
2. **Assessment starten**: 5 MCQ + 1 Code-Challenge absolvieren
3. **Badge erhalten**: Score und Level werden berechnet
4. **Profil teilen**: Verifizierte Skills im Profil anzeigen

## Lizenz

MIT
