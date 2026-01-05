# 🐝 Apiary Companion

**Mobile-first beekeeping app with AI-powered inspection structuring**

Built for hobby and semi-pro beekeepers in the EU. Offline-first, GDPR-compliant, works on iPhone.

---

## 🚀 Running in Replit

### Quick Start (60 seconds)

1. **Click the Run button** in Replit
2. **Install Expo Go** on your phone:
   - [iOS - App Store](https://apps.apple.com/app/expo-go/id982107779)
   - [Android - Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent)
3. **Scan the QR code** that appears in the console
4. **Wait for the app to load** (first time: ~1-2 minutes)
5. **Explore demo data**: 1 apiary, 3 hives, 5 inspections ready to browse!

### 📱 Testing on Your Phone

The app loads with realistic demo data. Try this:

1. **Browse hives** → Tap on "H001"
2. **Start an inspection** → Tap "🔍 Start Inspection"
3. **Use Quick Log** → Toggle Queen Seen, Eggs Seen, set Population Strength
4. **Add notes** → "Strong colony, good brood pattern, added super"
5. **Save & Review** → See AI extract structured findings! 🌟
6. **Confirm** → Tasks auto-created from your inspection

---

## 📚 Documentation

- **[REPLIT_SETUP.md](REPLIT_SETUP.md)** - Complete Replit setup guide
- **[apiary-companion/README.md](apiary-companion/README.md)** - Full technical documentation
- **[LLM Prompt](apiary-companion/src/services/llmStructuringPrompt.ts)** - Editable AI structuring prompt

---

## ✨ Key Features

### 🎯 Core Functionality
- ✅ **Offline-first** - Works without internet, SQLite local database
- ✅ **Fast inspections** - Quick Log mode with big tap targets (glove-friendly!)
- ✅ **Camera integration** - Photo capture for frames and brood
- ✅ **Voice recording** - Hands-free note-taking during inspections
- ✅ **Task management** - Auto-generated from inspections with priorities

### 🤖 AI-Powered (The Unique Feature)
- ✅ **Smart structuring** - Converts freeform notes → structured findings
- ✅ **Automatic extraction** - Pulls out queen sightings, swarm signs, varroa counts
- ✅ **Task generation** - Creates 1-5 actionable tasks based on findings
- ✅ **Review screen** - Confirm or edit before saving
- ✅ **Fallback parser** - Works without API key (rule-based)

### 🔒 Privacy & Compliance
- ✅ **GDPR-first** - All data stored locally on device
- ✅ **No account required** - Local-only mode
- ✅ **Full export** - CSV export of all data
- ✅ **Data ownership** - You control everything

### 📊 Management & Insights
- ✅ **Multi-apiary** - Manage multiple locations
- ✅ **Hive tracking** - QR codes, types, colony history
- ✅ **Statistics** - Dashboard with inspection counts, tasks
- ✅ **Search** - Find inspections by keywords
- ✅ **Export** - CSV format for Excel/Sheets

---

## 🛠️ Tech Stack

**Why React Native (Expo)?**
- ✅ Better mobile experience than PWA
- ✅ Native camera/microphone access
- ✅ Robust SQLite offline support
- ✅ Can publish to App Store/Play Store

**Technologies:**
- React Native with Expo SDK 54
- TypeScript for type safety
- SQLite for local database
- Expo Router for navigation
- Date-fns for date handling

---

## 🤖 AI Structuring Example

**You write** (freeform inspection notes):
```
Strong colony, 8 frames covered with bees. Saw queen on frame 3.
Good brood pattern, eggs visible. Found 2 swarm cells on bottom of frames.
Bees were calm during inspection. Added honey super.
```

**AI extracts** (structured data):
```json
{
  "findings": {
    "queen_seen": true,
    "eggs_seen": true,
    "brood_pattern": "good",
    "population_strength": 8,
    "temperament": "calm",
    "swarm_signs": true,
    "equipment_changes": "Added honey super"
  },
  "suggestedTasks": [{
    "title": "Recheck for swarm cells",
    "dueInDays": 7,
    "priority": "high"
  }]
}
```

---

## 🔐 Optional: Enable Full AI

To use Anthropic Claude for structuring:

1. Click **Secrets** (🔒) in Replit
2. Add: `ANTHROPIC_API_KEY` = `your-api-key`
3. Restart

Without API key: Uses rule-based fallback (still works!)

---

## 🐛 Troubleshooting

**App won't start?** Run: `cd apiary-companion && npm install`

**QR code not showing?** Check console for Expo URL

**Changes not updating?** Shake phone → Reload

See [REPLIT_SETUP.md](REPLIT_SETUP.md) for detailed troubleshooting

---

## 🛣️ Roadmap

- [ ] QR code scanning
- [ ] PDF export
- [ ] Local notifications
- [ ] Voice transcription
- [ ] Multi-user collaboration
- [ ] Optional cloud sync

---

Built with ❤️ for the beekeeping community 🐝

📖 **Full docs**: [apiary-companion/README.md](apiary-companion/README.md)
