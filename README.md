# WB Mobile Patcher v1.0

A simple tool that takes your Wife's Bedroom / Deeproom 4.0 PC game folder or mod .zip file and converts it into an Android app (.apk) that you can install and play on your phone or tablet.

---

## Quick Start (3 Steps)

1. Find your mod folder (for example, `Deeproom 4.0(up to date)`) or a mod `.zip` file.
2. Drag and drop that folder or `.zip` directly onto `WB_Mobile_Patcher.bat`.
3. Press Enter when prompted.

When finished, your ready-to-install game will be waiting in the `output` folder!

---

## What This Tool Adds (Enhancements List)

When you convert your game using this tool, it automatically adds full mobile support and fixes common PC mod bugs:

### Touch Controls & Mobile Gameplay
- Built for Touchscreens: Play naturally using taps, swipes, and drags on your phone screen with comfortable on-screen controls.
- Accidental Tap Protection: When menus or character cards are open, background taps are blocked so you don't accidentally trigger actions while browsing.
- Touch & Hold (Long Press): Press and hold on screen to perform right-click actions without needing a keyboard or mouse.
- Smooth Swiping & Scrolling: Glide smoothly through long character lists and menus with responsive touch scrolling.
- Touch-Friendly Bedroom Drawer: Swipe up and down or tap the enlarged navigation arrows to scroll through all your custom room backgrounds.
- Climax Scene Protection: Open menu windows automatically close during climax scenes so you get an unobstructed view of animations.
- Menus Stay on Screen: Draggable menu panels automatically stay within your phone's screen boundaries so they never get lost off the edges.

### Character Selection & Customization
- Visual Character Grid: Browse all your custom characters in a clean thumbnail grid with pose previews.
- Search & Favorites: Type any character's name to find them instantly, or tap the star button on any card to save your favorites.
- Jump to Equipped Character: Opening the character selector automatically scrolls to and centers on the character you currently have equipped.
- Automatic Character Sizing: Custom characters and partners are automatically scaled to fit the screen properly without looking stretched or misaligned.
- Full v1.5 Mod Compatibility in Deeproom: You can use newer Wife's Bedroom v1.5 character and room mods directly inside Deeproom 4.0. The patcher automatically sorts them into your character lists in alphabetical order alongside all existing characters.

### Audio, Dialogue & Custom Content
- Custom Voices & Sound Packs: Modded character voices, sound effects, and background music load and stream smoothly on mobile.
- Custom Dialogue Packs: Community dialogue packs and character-specific conversations load automatically over default lines.
- Custom Bedrooms & Outfits: Modded wallpapers, carpets, dressers, and clothing load seamlessly without graphical glitches.

### Reliability & Convenience
- Instant Startup: Loads thousands of custom mod files in seconds without freezing or hanging when opening the game.
- Crash Protection: Fixes common mobile crashes caused by missing mod images, sound errors, or unassigned PC variables.
- Automatic Mod Safety Check: If a mod is missing critical files that would crash the game on your phone, it is safely moved to the `output/quarantine` folder so the rest of your game runs without issues.
- Keep Screen Awake: Prevents your phone or tablet screen from dimming or going to sleep during gameplay.
- Saves Your Preferences: Remembers your volume, settings, and favorited characters between game sessions.
- Add Mods on Your Phone: Supports opening `.zip` mod packs directly on your Android device to add new characters on the go.

---

## Prerequisites (What You Need on Your Computer)

You only need two free programs installed:

1. Python 3
   - Download from https://www.python.org/downloads/
   - Important: During installation, check the box that says "Add Python to PATH".
2. Java
   - Download from https://www.java.com/download/
   - Needed so the tool can digitally sign the app so your phone will let you install it.

Everything else needed is already included in the folder.

---

## How to Use

### Method 1: Drag and Drop (Easiest)
1. Drag your game folder or `.zip` file onto `WB_Mobile_Patcher.bat`.
   - Tip: You can also select multiple mod folders, `.zip` archives, and your base `.apk` together and drag them onto the file. The patcher will automatically combine all your mods into a single build!
2. A command window will open. Press Enter to proceed with the recommended Default Install.
3. Wait for the tool to finish packaging and signing your app.
4. Open the `output` folder to get your finished `.apk`.

### Method 2: Use the "input" Folder
1. Put your mod folder or `.zip` file into the `input` folder.
2. Put your matching base game APK into the `input` folder:
   - For Deeproom 4.0 mods: Place `wifes_bedroom1_4.apk` (or `base.apk`).
   - For Wife's Bedroom v1.5: Place `wifes_bedroom1_5.apk`.
   The patcher automatically detects which version your mod uses and pairs with the matching base APK!
3. Double-click `WB_Mobile_Patcher.bat`.
4. Press Enter to build. (If multiple mod folders are found in `input`, you can choose which one to build from a simple numbered list).
5. Your finished app will be in the `output` folder.

*Tip for Multiple Mods*: If you drag multiple mod folders onto `WB_Mobile_Patcher.bat` at the same time, the patcher will automatically combine them all into a single build!

---

## How Prompts Work

Whenever the tool asks a question in the command window:
- Pressing Enter automatically accepts the recommended default choice (the capitalized letter, such as `[Y/n]` for Yes or `[y/N]` for No).
- You can simply press Enter through all prompts to get the best recommended settings.

---

## Custom Installation Options (Feature Synopsis)

When selecting Custom Install (`[N]`), you can toggle each of the patcher's individual features. Here is what each option does:

1. Core Mobile Engine & Fast Manifest Optimization
   - Generates fast in-memory indexes of all character, dialogue, sound, and bedroom files so Android can load thousands of custom mod assets in seconds without freezing or hanging on startup.

2. Universal Origin-Based Model Scaling (160px normalization)
   - Automatically detects non-standard mod character sizes and scales them to fit the 160px GameMaker baseline so custom partners line up properly with bodies without looking stretched or misaligned.

3. Engine Stability & Portrait Parity (cures requested -1 crashes)
   - Adds defensive code shields to prevent crashes caused by missing mod portraits, broken filenames, or uninitialized variables when switching characters or poses.

4. UI Polish & Climax Auto-Closing
   - Force-closes open menu panels during climax animations for an unobstructed view, and prevents draggable menus from sliding off the screen edges.

5. Character Selection Grid & Vector Star Bookmarks
   - Replaces text lists with an interactive visual thumbnail grid, real-time name search, and 8-point geometric star buttons to bookmark your favorite characters. Includes smooth touch swipe scrolling and auto-centers on equipped characters.

6. On-Device Phone Mod Sharing (open .zip mods directly on Android)
   - Bundles a background phone activity allowing you to open and import mod `.zip` files directly on your Android phone without needing a computer.

7. External ToyBridge / Intiface Telemetry (port 45735)
   - Enables optional Bluetooth toy synchronization via local network UDP telemetry. Default is off.

8. Clean Previous APK Builds
   - Cleans older `.apk`, `.idsig`, and `.bak` files from the `output/` folder before compiling a new build to save disk space.

9. Fast Packaging Mode
   - Packages files without compression for ultra-fast (under 10 seconds) builds during quick testing and emulator use.

---

## Automatic File Naming

The patcher automatically names your finished app after your input:
- If your folder is named `Deeproom 4.0(up to date)`, your app will be named `Deeproom 4.0(up to date)_modded.apk`.
- If your zip is named `Summer_Outfits.zip`, your app will be named `Summer_Outfits_modded.apk`.

You will find all finished apps inside the `output` folder.

---

## Missing a Mod? (The Quarantine Folder)

If you notice a character or room mod is missing from your game, check the `output/quarantine` folder.

Before building your app, the patcher inspects every custom character and room mod. If a mod has missing image files, broken formatting, or issues that would cause your phone to crash, the tool automatically isolates that specific mod into `output/quarantine`.

- Your files are never permanently deleted — they are simply set aside so the rest of your game can run smoothly.
- Any working mods will install and run normally.

---

## Building for Official Wife's Bedroom v1.5 (Optional)

While this tool is primarily designed for Deeproom 4.0, it also supports building the official standalone Wife's Bedroom v1.5:
- Place your `wifes_bedroom1_5.apk` in the `input` folder (or drag it alongside your mod folder).
- Custom mods placed in your `custom` folder are loaded directly into the game's built-in custom selection tabs.
- For the full mobile enhancement suite (including the visual character thumbnail grid, star favorites, and custom dialogue packs), Deeproom 4.0 is the recommended platform.

---

## Folder Layout

```
WB_Mobile_Patcher_v1.0/
├── WB_Mobile_Patcher.bat        <- Double-click or drag-and-drop here
├── WB_Mobile_Patcher.py         <- Main tool script
├── README.md                    <- This guide
│
├── input/                       <- Drop your mod folders, zips, or base APK here
│
├── core/                        <- Built-in tools and engines (no need to touch)
│
└── output/                      <- Your finished Android apps appear here
```

---

## Troubleshooting

1. "Python is not recognized as an internal or external command":
   - Python was installed without adding it to your system PATH. Re-run the Python installer, click "Modify", and make sure "Add Python to PATH" is checked.

2. "Java is not recognized as an internal or external command":
   - Java is missing. Install Java from https://www.java.com/download/ and restart your computer.

3. "Base APK not found":
   - Place the matching base game APK into the `input` folder:
     - For Deeproom 4.0 mods: Place `wifes_bedroom1_4.apk` (or `base.apk`).
     - For Wife's Bedroom v1.5 mods: Place `wifes_bedroom1_5.apk`.

4. App won't install on your phone:
   - On your Android phone, make sure you allow installing apps from unknown sources or your file manager app.
