# Apiary Companion 🐝

A mobile-first beekeeping app MVP for hobby and semi-professional beekeepers in the EU. Built with GDPR compliance and offline-first architecture.

## Core Principle

**Capture → Structure → Remind → Learn**

Users record hive inspections (typed or voice), the app turns notes into structured fields using AI, then generates actionable task lists and seasonal reminders.

---

## Features

### ✅ MVP Features (Implemented)

1. **Offline-First Architecture**
   - All data stored locally in SQLite
   - Works without internet connection
   - Inspections never blocked by connectivity

2. **Apiary & Hive Management**
   - Create and manage multiple apiaries
   - Track hives with unique codes
   - Record hive types, start dates, and colony information
   - Queen tracking (year, origin, temperament)

3. **Fast Inspection Flow**
   - Quick Log mode: key observations with big tap targets
   - Detailed notes field for comprehensive records
   - Camera integration for frame/brood photos
   - Voice recording for hands-free note-taking
   - Works with gloves outdoors

4. **AI-Powered Structuring** 🌟
   - Converts freeform notes into structured findings
   - Extracts: brood pattern, queen sightings, stores, temperament, swarm signs, varroa counts
   - Generates 1-5 actionable task suggestions
   - Review screen for user confirmation
   - Fallback parser when AI unavailable

5. **Task Management**
   - Task list with filters (Pending, Overdue, All)
   - Auto-generated tasks from inspections
   - Priority levels (High, Medium, Low)
   - Source tracking (inspection, seasonal, manual)
   - Quick toggle to mark complete

6. **Privacy & GDPR Compliance**
   - Local-only mode (no account required)
   - Data stored privately on device
   - Full export capability (CSV)
   - No cloud sync without explicit consent

7. **Insights & Export**
   - Dashboard with apiary statistics
   - CSV export of all inspection data
   - Includes hive history, findings, and notes
   - Shareable via device sharing options

---

## Tech Stack

### Choice: React Native (Expo) ✓

**Why React Native over Next.js PWA:**

1. **Better Mobile Experience**: Native feel on iOS/Android with smooth performance
2. **Offline SQLite**: Robust local database with expo-sqlite
3. **Native Features**: Better camera, microphone, and file system access
4. **Distribution**: Can publish to App Store/Play Store
5. **Performance**: Faster for data-heavy operations (inspections, search)

### Core Technologies

- **Framework**: React Native with Expo SDK 54
- **Navigation**: Expo Router (file-based routing)
- **Database**: SQLite (expo-sqlite)
- **Language**: TypeScript
- **Date Handling**: date-fns
- **Validation**: Zod (for LLM response validation)

### Key Libraries

```json
{
  "expo-sqlite": "Local database",
  "expo-camera": "Photo capture",
  "expo-av": "Voice recording",
  "expo-router": "Navigation",
  "expo-file-system": "File operations",
  "expo-sharing": "Data export",
  "date-fns": "Date formatting"
}
```

---

## Project Structure

```
apiary-companion/
├── app/                          # Expo Router screens
│   ├── _layout.tsx              # Root layout with DB initialization
│   ├── index.tsx                # Home/Apiaries list
│   ├── (tabs)/                  # Tab navigation
│   │   ├── apiaries.tsx         # Apiaries tab
│   │   ├── tasks.tsx            # Tasks tab
│   │   └── insights.tsx         # Insights & export
│   ├── apiary/[id].tsx          # Apiary detail
│   ├── hive/[id].tsx            # Hive detail
│   └── inspection/
│       ├── create.tsx           # Inspection form
│       └── review.tsx           # AI structuring review
├── src/
│   ├── database/
│   │   ├── index.ts             # Database service
│   │   └── schema.ts            # SQL schema & migrations
│   ├── services/
│   │   ├── apiaryService.ts     # Apiary CRUD
│   │   ├── hiveService.ts       # Hive CRUD
│   │   ├── inspectionService.ts # Inspection CRUD
│   │   ├── taskService.ts       # Task management
│   │   ├── llmService.ts        # AI structuring
│   │   ├── llmStructuringPrompt.ts  # Versioned prompt
│   │   ├── userService.ts       # User management
│   │   └── seedService.ts       # Demo data
│   ├── types/
│   │   └── index.ts             # TypeScript types
│   └── utils/
│       └── uuid.ts              # UUID generation
├── assets/                      # Images & icons
├── app.json                     # Expo configuration
├── package.json                 # Dependencies
└── README.md                    # This file
```

---

## Data Model

### Entities & Relationships

```
User
├── Apiary (1:N)
    ├── Hive (1:N)
    │   ├── Colony (1:N)
    │   ├── Inspection (1:N)
    │   │   ├── InspectionFindings (1:1)
    │   │   └── Attachment (1:N)
    │   ├── Treatment (1:N)
    │   ├── Harvest (1:N)
    │   └── Task (1:N)
    ├── InventoryItem (1:N)
    ├── SeasonalPlan (1:N)
    └── Task (1:N)
```

### Key Tables

- **users**: Local user account (email optional)
- **apiaries**: Beekeeping locations
- **hives**: Individual hives with codes
- **colonies**: Queen & colony info per hive
- **inspections**: Core inspection records
- **inspection_findings**: Structured data extracted from notes
- **tasks**: Action items with due dates
- **treatments**: Varroa/disease treatments
- **harvests**: Honey harvest records
- **attachments**: Photos from inspections

See `src/database/schema.ts` for full schema.

---

## LLM Structuring System 🤖

### How It Works

1. **User Creates Inspection**
   - Enters freeform notes: "Strong colony, 8 frames covered. Queen seen on frame 3. Good brood pattern. 2 swarm cells found."
   - Optionally adds voice recording

2. **Save & Structure**
   - Inspection saved to SQLite immediately (offline-safe)
   - Navigate to Review screen
   - LLM service processes notes

3. **AI Analysis**
   - Sends notes + voice transcript to LLM API (if configured)
   - Fallback to rule-based parser if offline/no API key
   - Extracts structured findings + generates tasks

4. **User Review**
   - Review screen shows extracted data
   - Confidence score displayed
   - User confirms or skips
   - Tasks created automatically

### The Prompt

Located in: `src/services/llmStructuringPrompt.ts`

**Version**: 1.0.0 (versioned for tracking changes)

**Key Features**:
- Conservative extraction (null if uncertain)
- Safety constraints (no diagnosis, cautious language)
- JSON schema enforcement
- Task generation based on findings + season
- Confidence scoring

**Example Input**:
```
"Colony looking strong. 8 frames covered with bees. Saw queen on frame 3.
Good brood pattern, eggs visible. Stores looking good - about 3 frames of honey.
Found 2 swarm cells on bottom of frames. Bees were calm."
```

**Example Output**:
```json
{
  "findings": {
    "brood_pattern": "good",
    "eggs_seen": true,
    "queen_seen": true,
    "stores_honey": 7,
    "population_strength": 8,
    "temperament": "calm",
    "swarm_signs": true,
    "swarm_signs_detail": "2 swarm cells found on frame bottoms"
  },
  "suggestedTasks": [
    {
      "title": "Recheck for swarm cells",
      "description": "Swarm cells detected. Inspect again in 7 days to monitor colony intentions.",
      "dueInDays": 7,
      "priority": "high"
    }
  ],
  "confidence": 0.85
}
```

### API Configuration

To enable AI structuring with Claude API:

```typescript
import { llmService } from './src/services/llmService';

llmService.setApiKey('your-anthropic-api-key');
```

Without API key, the app uses a rule-based fallback parser (keyword matching).

### Safety & Disclaimers

- Never diagnoses diseases definitively
- Uses "possible signs" language
- Advises consulting local experts
- No treatment dosages provided
- User must review all extracted data

---

## Setup & Installation

### Prerequisites

- Node.js 18+ and npm
- Expo CLI: `npm install -g expo-cli`
- iOS Simulator (Mac) or Android Studio (for emulator)
- Or use Expo Go app on physical device

### Installation

```bash
# Clone repository
cd apiary-companion

# Install dependencies
npm install

# Start development server
npm start

# Run on specific platform
npm run ios      # iOS Simulator (Mac only)
npm run android  # Android Emulator
npm run web      # Web browser (limited camera/audio)
```

### First Run

On first launch, the app will:
1. Initialize SQLite database
2. Run migrations
3. Seed demo data (1 apiary, 3 hives, 5 inspections)

### Demo Data

- **Apiary**: "Demo Apiary" in Central Europe
- **Hives**:
  - H001: Strong colony with 2024 queen
  - H002: Recent split, building up
  - H003: New package install
- **Inspections**: 5 realistic inspections with findings
- **Tasks**: 5 pending tasks from inspections

---

## Usage Guide

### Quick Inspection Flow (60 seconds)

1. Open app → Select Apiary → Tap Hive
2. Tap "🔍 Start Inspection"
3. Quick Log:
   - Queen Seen? Yes/No
   - Eggs Seen? Yes/No
   - Swarm Signs? Yes/No
   - Population Strength: 1-10
4. Add notes: "Strong colony, good brood pattern"
5. Optional: 📷 Photo or 🎤 Voice note
6. Tap "✓ Save & Review"
7. Review AI-extracted findings
8. Confirm → Tasks auto-created

### Offline Behavior

- All inspections save locally first
- Photos stored in device file system
- Tasks and data accessible offline
- Export works offline

### Conflict Handling

Currently: Last-write-wins (no cloud sync in MVP)

Future: Optional cloud sync with conflict resolution

---

## Export & Data Portability

### CSV Export

From Insights tab → "📄 Export All Data (CSV)"

**Exported Fields**:
- Apiary name
- Hive code
- Inspection date/time
- Weather, inspector
- Freeform notes
- Queen seen, eggs seen, swarm signs
- Population strength, temperament
- Varroa count

**Use Cases**:
- Share with mentor
- Import to spreadsheet
- Backup before device change
- Compliance documentation

---

## GDPR Compliance

### Privacy by Default

- ✅ Local-only mode (no account needed)
- ✅ Data stored on device only
- ✅ No automatic cloud sync
- ✅ Full export capability
- ✅ Clear data ownership

### User Rights

- **Right to Access**: Export all data anytime
- **Right to Portability**: CSV export
- **Right to Erasure**: Uninstall app = data deleted
- **Right to Restrict Processing**: No processing without user action

### Future Considerations

If cloud sync added:
- Explicit opt-in required
- Consent flow before first sync
- Encryption in transit & at rest
- EU-based servers
- Clear privacy policy

---

## Development

### Database Migrations

To add a new table/field:

1. Edit `src/database/schema.ts`
2. Increment `SCHEMA_VERSION`
3. Add migration to `migrations` array
4. Restart app (auto-applies on launch)

### Adding New Screens

Using Expo Router (file-based):

```typescript
// Create: app/new-screen.tsx
export default function NewScreen() {
  return <View><Text>New Screen</Text></View>;
}

// Navigate: router.push('/new-screen');
```

### Extending LLM Prompt

Edit: `src/services/llmStructuringPrompt.ts`

- Update `SYSTEM_PROMPT` for new fields
- Update `InspectionStructuredData` type
- Increment `STRUCTURING_PROMPT_VERSION`
- Test with various inputs

---

## Roadmap (Post-MVP)

### Near-Term

- [ ] QR code scanning for instant hive access
- [ ] PDF export (Hive Report: last 5 inspections + tasks)
- [ ] Local notifications for task due dates
- [ ] Weather integration (forecast snapshot in inspection)
- [ ] Seasonal plan templates (North/Central/South Europe)

### Medium-Term

- [ ] Multi-user shared apiaries (roles: owner/editor/viewer)
- [ ] On-device voice transcription (Whisper model)
- [ ] Basic charts (varroa trends, inspection frequency)
- [ ] Search across all notes/transcripts
- [ ] Treatment compliance reminders

### Long-Term

- [ ] Optional cloud sync (Supabase backend)
- [ ] Sync conflict resolution UI
- [ ] Colony performance predictions
- [ ] Integration with local beekeeping associations
- [ ] Multi-language support (DE, FR, ES, IT, PL)

---

## Testing

### Manual Testing Checklist

- [ ] Create apiary and hive
- [ ] Start inspection with Quick Log
- [ ] Add notes and photo
- [ ] Record voice note
- [ ] Save and review structured data
- [ ] Confirm tasks created
- [ ] Mark task complete
- [ ] Export data to CSV
- [ ] Test offline (airplane mode)

### Unit Tests (TODO)

```bash
npm test
```

Priority areas:
- LLM prompt parsing
- Data transformations
- Task generation logic
- CSV export formatting

---

## Troubleshooting

### Database Issues

**Reset database:**
```typescript
// In app/_layout.tsx, temporarily add:
await seedService.clearAllData();
await seedService.seedDemoData();
```

**View database:**
```bash
# iOS Simulator
cd ~/Library/Developer/CoreSimulator/Devices/[DEVICE_ID]/data/Containers/Data/Application/[APP_ID]/Library/LocalDatabase
sqlite3 apiary_companion.db

# Android Emulator
adb root
adb pull /data/data/com.apiarycompanion.app/databases/apiary_companion.db
sqlite3 apiary_companion.db
```

### Camera Not Working

- Check permissions in Settings → App → Permissions
- iOS: Requires physical device (simulator limited)
- Web: Browser camera API limitations

### Voice Recording Issues

- Check microphone permissions
- iOS: May require HTTPS in production
- Recording quality preset: `HIGH_QUALITY` (configurable)

---

## Contributing

This is an MVP. Contributions welcome for:

- Bug fixes
- Performance improvements
- Additional language support
- Test coverage
- Documentation improvements

Please open issues for discussion before major features.

---

## License

MIT License - see LICENSE file

---

## Credits

Built with:
- React Native & Expo
- SQLite for local storage
- Anthropic Claude for AI structuring
- Date-fns for date handling
- Expo ecosystem (Camera, FileSystem, Sharing, etc.)

Designed for the beekeeping community 🐝

---

## Support

For bugs and feature requests:
- Open a GitHub issue
- Include: device type, OS version, steps to reproduce

For beekeeping questions:
- Consult local beekeeping associations
- This app is a record-keeping tool, not a diagnostic service

---

**Version**: 1.0.0 (MVP)
**Last Updated**: January 2025
**Maintained by**: The Apiary Companion Team
