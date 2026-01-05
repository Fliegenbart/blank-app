# 🐝 Apiary Companion - Replit Setup Guide

Complete guide to running Apiary Companion in Replit!

## 🚀 Quick Start (60 seconds)

### Step 1: Start the Development Server

Click the **Run** button in Replit (or type `npm run dev` in Shell).

This will:
- Install all dependencies
- Start the Expo development server
- Create a tunnel for external access

### Step 2: Connect Your Phone

You have **3 options** to test the app:

#### Option A: Expo Go App (Recommended for Testing) 📱

1. **Install Expo Go** on your phone:
   - iOS: [App Store - Expo Go](https://apps.apple.com/app/expo-go/id982107779)
   - Android: [Play Store - Expo Go](https://play.google.com/store/apps/details?id=host.exp.exponent)

2. **Scan the QR Code**:
   - Look for the QR code in the Replit console
   - Open Expo Go app → Tap "Scan QR Code"
   - Point camera at the QR code
   - Wait for the app to load (first time takes 1-2 minutes)

3. **Start Testing!**
   - The app will load with demo data
   - Try creating an inspection
   - Test the Quick Log feature
   - All data is stored locally on your phone

#### Option B: Web Preview (Limited Features) 🌐

1. Click the **Webview** tab in Replit
2. The app will open in browser
3. **Note**: Camera and voice features won't work in browser

#### Option C: Development Build (Advanced)

For full native features, create a development build:
```bash
cd apiary-companion
npx expo install expo-dev-client
eas build --profile development --platform android
```

## 📋 What You'll See

### First Launch

On first run, the app automatically:
1. ✅ Initializes SQLite database
2. ✅ Runs schema migrations
3. ✅ Seeds demo data:
   - 1 Apiary: "Demo Apiary"
   - 3 Hives: H001, H002, H003
   - 5 Inspections with realistic notes
   - 5 Tasks from inspections

### Main Screens

1. **Home/Apiaries** - View all your apiaries
2. **Hive Detail** - Core screen with:
   - Last inspection info
   - Pending tasks
   - "Start Inspection" button (try this!)
3. **Inspection Create** - The inspection form
4. **Review Screen** - AI structuring results (🌟 key feature)
5. **Tasks Tab** - Manage your beekeeping tasks
6. **Insights Tab** - Stats and export data

## 🎯 Try These Features

### 1. Quick Inspection (60 seconds)

1. Tap any hive (H001, H002, or H003)
2. Tap "🔍 Start Inspection"
3. Use Quick Log toggles:
   - Queen Seen: Yes
   - Eggs Seen: Yes
   - Swarm Signs: No
   - Population Strength: 8/10
4. Add notes: "Strong colony, good brood pattern, added super"
5. Tap "✓ Save & Review"
6. See AI-extracted findings!
7. Confirm to create tasks automatically

### 2. Test Camera Feature

**In Expo Go**:
- Camera works on physical device
- Grant permissions when prompted

**In Web**:
- Camera limited/not available

### 3. Export Your Data

1. Go to Insights tab
2. Tap "📄 Export All Data (CSV)"
3. Share the CSV file
4. Open in Excel/Sheets to see all inspection records

### 4. Test AI Structuring

Try these inspection notes to see AI extraction:

**Example 1 - Swarm Warning**:
```
Colony very crowded. Found 3 queen cells on bottom of frames.
Queen still present but bees are preparing to swarm.
Added super to give them more space.
```

**Example 2 - Weak Colony**:
```
Only 3 frames covered with bees. Didn't see queen but eggs are present.
Small brood pattern. Stores are low - added 1:1 sugar syrup feeder.
Bees were gentle during inspection.
```

**Example 3 - Varroa Check**:
```
Alcohol wash showed 4 mites per 100 bees. Population is strong at 8 frames.
Queen seen and laying well. Will need to treat for varroa soon.
```

Watch how the AI extracts:
- Structured findings
- Suggested tasks
- Due dates and priorities

## 🔧 Replit-Specific Configuration

### Environment Variables (Optional)

To enable full AI structuring with Anthropic Claude:

1. Click **Secrets** tab (🔒 icon) in Replit
2. Add secret:
   - Key: `ANTHROPIC_API_KEY`
   - Value: `sk-ant-...` (your API key)
3. Restart the dev server

Without API key: App uses fallback rule-based parser (still works!)

### Troubleshooting in Replit

**Issue: "Cannot find module" errors**

```bash
cd apiary-companion
npm install
```

**Issue: Port already in use**

```bash
# Kill existing processes
pkill -f expo
# Restart
npm run dev
```

**Issue: QR code not showing**

Check the console output - the URL should be visible even if QR doesn't render.

**Issue: Expo Go can't connect**

- Make sure you're on the same network (or use tunnel mode)
- Try stopping and restarting the server
- Check firewall settings

**Issue: Changes not reflecting**

Replit auto-saves, but you may need to:
- Shake phone in Expo Go → Reload
- Or press `r` in terminal to reload

## 📱 Device Testing Recommendations

### Works Great
- ✅ Expo Go on iPhone/Android (recommended)
- ✅ Physical device with camera/mic
- ✅ All features except AI (if no API key)

### Limited Functionality
- ⚠️ Web preview in Replit (no camera/voice)
- ⚠️ iOS Simulator (no camera on Mac)

### Best Testing Flow

1. **Start in Replit**: Edit code here
2. **Live Reload**: Changes appear instantly in Expo Go
3. **Test on Phone**: Use real camera/microphone
4. **Iterate Fast**: Edit → Save → Auto-refresh

## 🗂️ Project Structure in Replit

```
/home/user/blank-app/
├── apiary-companion/           # Main app directory
│   ├── app/                    # Screens (Expo Router)
│   ├── src/
│   │   ├── database/           # SQLite schema
│   │   ├── services/           # Business logic
│   │   │   ├── llmService.ts           # AI structuring
│   │   │   ├── llmStructuringPrompt.ts # Editable prompt!
│   │   │   └── seedService.ts          # Demo data
│   │   └── types/              # TypeScript types
│   ├── package.json
│   └── README.md               # Full documentation
├── .replit                     # Replit run config
├── replit.nix                  # Dependencies
└── REPLIT_SETUP.md            # This file
```

## 🎨 Customizing in Replit

### Edit the LLM Prompt

The AI structuring prompt is **fully editable**:

1. Open: `apiary-companion/src/services/llmStructuringPrompt.ts`
2. Modify `SYSTEM_PROMPT` to change extraction logic
3. Adjust task generation rules
4. Save → Changes apply immediately

### Add Your Own Data

Clear demo data and start fresh:

```typescript
// In app/_layout.tsx, add before setIsReady(true):
await seedService.clearAllData();
// Comment out seedDemoData() to start empty
```

### Change Theme Colors

Primary color is `#FFA500` (orange/honey color):
- Search for `#FFA500` in code
- Replace with your preferred color
- Search for other colors to customize theme

## 📊 Testing the AI Structuring

### With API Key (Full Experience)

1. Add Anthropic API key in Secrets
2. Create inspection with detailed notes
3. Watch AI extract all findings
4. Get confidence score
5. See auto-generated tasks

### Without API Key (Fallback Mode)

- Still works with rule-based parser
- Detects keywords: "queen", "swarm cell", "aggressive", "varroa"
- Creates basic tasks
- Good for testing without API costs

## 🚢 Deployment Options

### From Replit

**Option 1: Expo Development Build**
```bash
npx expo install expo-dev-client
eas build --profile development
```

**Option 2: Production Build**
```bash
eas build --platform android
eas build --platform ios
```

**Option 3: Expo Publish**
```bash
npx expo publish
```

## 💡 Replit Pro Tips

### Fast Iteration

- **Hot Reload**: Shake phone → Enable Fast Refresh
- **Console Logs**: Show in both Replit console and Expo Go
- **Debugger**: Shake phone → Debug Remote JS

### Sharing Your Preview

Expo creates a shareable URL:
- Share the QR code screenshot
- Or share the `exp://` URL
- Others can test with Expo Go

### Database Inspection

View SQLite database in Replit Shell:
```bash
cd apiary-companion
# Database location (in Expo Go, stored on device)
# Can't directly access device DB from Replit
# But export CSV works from app
```

## 🎓 Learning Resources

### Understanding the Code

Start with these files:
1. `app/_layout.tsx` - App initialization & DB setup
2. `app/hive/[id].tsx` - Main hive screen
3. `app/inspection/create.tsx` - Inspection form
4. `app/inspection/review.tsx` - AI structuring (🌟 unique feature)
5. `src/services/llmService.ts` - How AI works
6. `src/database/schema.ts` - Database structure

### Key Concepts

- **Offline-First**: All data in SQLite, syncs to device
- **Expo Router**: File-based navigation (like Next.js)
- **Service Layer**: Clean separation of business logic
- **Type Safety**: TypeScript interfaces for all data

## 🐛 Common Issues & Solutions

### 1. App Won't Start in Expo Go

**Error**: "Something went wrong"

**Solution**:
```bash
cd apiary-companion
rm -rf node_modules package-lock.json
npm install
```

### 2. Database Errors

**Error**: "Database not initialized"

**Solution**: App auto-initializes on first launch. If issues persist:
```typescript
// In app/_layout.tsx
await db.init();
```

### 3. Photos Not Saving

**Issue**: Camera permission denied

**Solution**:
- iOS: Settings → Expo Go → Camera → Allow
- Android: Settings → Apps → Expo Go → Permissions → Camera

### 4. No AI Structuring Results

**Check**:
1. API key set correctly in Secrets?
2. Check console for API errors
3. Fallback parser should still work

## 📞 Need Help?

1. **Check README**: `apiary-companion/README.md` has full docs
2. **Console Logs**: Look for errors in Replit console
3. **Expo Docs**: https://docs.expo.dev
4. **SQLite Issues**: Check database initialization in `_layout.tsx`

## 🎉 You're Ready!

Hit **Run** and start testing the app. The demo data will help you explore all features.

**Recommended first steps**:
1. ✅ Browse the demo hives
2. ✅ Create a test inspection for H001
3. ✅ Try the AI structuring review screen
4. ✅ Check the generated tasks
5. ✅ Export your data to CSV

Happy beekeeping! 🐝🍯
