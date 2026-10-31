# Kind Doctor Bot (@KindDoc_bot) 🩺
## Complete Operator Manual, Command Reference & Feature Architecture

> **Official Telegram Handle:** [@KindDoc_bot](https://t.me/KindDoc_bot)  
> **Bot Title:** `Kind Doctor 🩺 | Sentinel & Index Hub`  
> **Engine:** Asynchronous Python 3 (Telethon MTProto + Telegram Bot API v7.0+)  
> **Persistence:** SQLite3 Multi-tenant Core (`history_core.sqlite`)

---

## 🌟 1. Bot Profile & Identity Overview

- **Custom Luxury 3D Avatar:** Glowing Cyan Stethoscope intertwined with a Polished Golden Caduceus Shield, Holographic Medical DNA Helix, and "KIND DOCTOR" insignia.
- **Short Description (Telegram Bio):**
  > *Official Kind Doctor Desk 🩺 | Medical Study Group Sentinel, Anti-Leak Shield & Automated Dual Index Engine.*
- **Pre-Start Description:**
  > *Welcome to Kind Doctor Bot! 🩺\nYour dedicated Medical Study Group Assistant, Automated Dual Index Engine, Interactive Quiz Poll Generator, and 24/7 Group Sentinel.*

---

## 🛡️ 2. Core Architecture & Multi-Tenant Philosophy

`@KindDoc_bot` is engineered to be simultaneously:
1. **The Private Support Desk for Kind Doctor:** Any direct private message (DM) to the bot is securely routed only to Kind Doctor's master administrators (`master_admin_ids`). Private conversations are never exposed to public groups.
2. **The Ultimate Group Utility for ANY Medical/Study Community:** Any group admin in the world can add `@KindDoc_bot` to their group. The bot automatically provisions an isolated workspace for that group in `history_core.sqlite`, giving them access to:
   - Dual-layer Indexing (Main Index + Topic-Specific Navigation)
   - Real-time Topic & File Search Engine (`/find`)
   - AI-Powered High-Yield Clinical MCQs & Polls (`/mcq`)
   - Zero-Effort Smart FAQ Auto-Responder (`/setfaq`)
   - Custom Commands & Fast Shortcuts (`/addcommand`)
   - Group Security Lockdown & Anti-Raid Guard

---

## 📋 3. Complete Module Breakdown & Working Guide

### Module 1: Automated Dual Index Hub 📚
*Problem Solved:* In large Telegram supergroups with Forum Topics, students constantly lose important notes, lecture slides, and video links.  
*How It Works:* The bot tracks topics and items in SQLite with message link references. Admins can pin a dynamic Main Index in General, and a Topic Index in each sub-topic.

| Command | Permission | Description & Working |
| :--- | :--- | :--- |
| `/help` or `/menu` | All Members | Opens the **1-Click Interactive Dashboard** with tap-to-run inline buttons. |
| `/scan` or `/autoindex` | Admin & All | **1-Click Autonomous Scanner**: Discovers all forum topics and video/PDF files in seconds without typing. |
| `/mainindex` | Admin & All | Generates and sends an overview index listing all registered subjects and topic buttons. Pinned in General. |
| `/topicindex` | Admin & All | Sends the clean, organized Table of Contents of all notes/links under the current topic. |
| `/settopic <num> <Name>` | Admin | Registers a forum topic manually (optional). E.g.: `/settopic 1 Pathology & Pathoma` |
| `/deltopic <num>` | Admin | Removes a topic and its indexed items. |
| `/additem <num> <Title> \| <Link>` | Admin | Adds a study resource to Topic `<num>`. Also supports **Reply to message** with `/additem <title>`. |
| `/topics` | All Members | Displays the interactive list of all available topics in the group. |
| `/indexhelp` | All Members | Shows an interactive quick-reference guide on how to build and maintain indexes. |

---

### Module 2: Instant Group Search Engine 🔍
*Problem Solved:* Students waste hours scrolling through group history or asking admins "where is the pharmacology pdf?".  
*How It Works:* Executes sub-5ms SQLite indexed full-text pattern searches across all registered topic items and resources in the group, outputting directly clickable links.

| Command | Permission | Syntax & Example |
| :--- | :--- | :--- |
| `/find <keyword>` | All Members | `/find Robbins` → Returns direct message links for all Robbins resources. |
| `/search <keyword>` | All Members | `/search Cardiology` → Lists matching materials with parent topic badges. |

---

### Module 3: High-Yield Medical MCQ & Interactive Quiz Engine 🧠
*Problem Solved:* Groups become passive file repositories without active learning and engagement.  
*How It Works:* Generates clinical vignette MCQs with 4 options, a correct answer, and an in-depth clinical explanation. Dispatches native Telegram Quiz Polls (`type="quiz"`) featuring confetti animations and instant explanation tooltips.

| Command | Permission | Description & Working |
| :--- | :--- | :--- |
| `/mcq [subject]` | All Members | Dispatches a clinical question on the specified subject (e.g., `/mcq Pharmacology`, `/mcq Pathology`). |
| `/quiz [subject]` | All Members | Alias for `/mcq`. Supports General Medicine, Surgery, Anatomy, Microbiology, etc. |

*Features:*
- Native Telegram Quiz format with green tick on correct answer and red cross on mistakes.
- Clinical Pearls shown instantly upon answering.
- Works in public groups, forum topics, and private bot chats.

---

### Module 4: Smart FAQ & Keyword Auto-Responder 💡
*Problem Solved:* Admins get burned out answering the same 10 questions every day ("How to get password?", "Where is the drive link?", "Schedule kya hai?").  
*How It Works:* Admins map trigger keywords to formatted answers. When a user sends a `/faq <trigger>` command OR when any member mentions the keyword in group conversation, the bot auto-replies with the saved solution and auto-deletes prompt clutter.

| Command | Permission | Syntax & Example |
| :--- | :--- | :--- |
| `/setfaq <keyword> <Answer>` | Admin | `/setfaq schedule Class timings: Mon-Fri 8PM IST live on Zoom.` |
| `/delfaq <keyword>` | Admin | `/delfaq schedule` |
| `/faqs` | All Members | Lists all registered FAQ trigger keywords in the group. |
| `/faq <keyword>` | All Members | Fetches the saved answer for the keyword immediately. |

---

### Module 5: Custom Command Maker Engine ⚡
*Problem Solved:* Need custom shortcuts without modifying Python code.  
*How It Works:* SQLite-backed dynamic command dispatch table. If `/rules` or `/drive` is created, typing that command triggers the custom response.

| Command | Permission | Syntax & Example |
| :--- | :--- | :--- |
| `/addcommand <name> <response>` | Admin | `/addcommand drive Important study drive: https://drive.google.com/...` |
| `/delcommand <name>` | Admin | Deletes the custom command. |
| `/commands` | Admin | Lists all active custom commands created in the system. |
| `/run <name>` | All Members | Manually triggers any custom command. |

---

### Module 6: Group Security & Sentinel Lockdown 🛡️
*Problem Solved:* Spammers joining at night or bot attacks disrupting studies.

| Command | Permission | Description & Working |
| :--- | :--- | :--- |
| `/lockdown on` | Admin | Restricts normal members from sending messages, photos, and links during raids or study hours. |
| `/lockdown off` | Admin | Restores full standard group messaging permissions. |
| `/block <user_id> [reason]` | Admin | Bans a malicious user and logs their profile in the dossier. |
| `/unblock <user_id>` | Admin | Unblocks a previously banned user. |
| `/blocked` | Admin | Lists all blocked users and offenses. |

---

### Module 7: Multi-Admin & Operations Management 👥

| Command | Permission | Description & Working |
| :--- | :--- | :--- |
| `/promote <user_id>` | Master Admin | Promotes a trusted group manager to bot operator status. |
| `/demote <user_id>` | Master Admin | Revokes operator privileges. |
| `/admins` | Admin | Shows the complete directory of bot admins and master controllers. |
| `/broadcast <msg>` | Master Admin | Broadcasts an announcement across all active group chats managed by the bot. |
| `/status` | Admin | Displays live telemetry: Active Groups, Topics, FAQs, Items Indexed, Uptime. |
| `/invitelink` | Admin | Generates or fetches a safe, single-click join link for the group. |

---

### Module 8: High-Yield Clinical Pearls & Spoiler Flashcards 💎
*Problem Solved:* Passive reading lacks active recall, causing students to forget diagnostic triads and drugs of choice.  
*How It Works:* Generates medical diagnostic clues, triads, and classic signs with Telegram native spoiler tags `||hidden||`. Students can read the question, attempt recall, and tap to reveal the verified answer.

| Command | Permission | Syntax & Example |
| :--- | :--- | :--- |
| `/pearl [subject]` | All Members | `/pearl cardiology` ➔ Beck's Triad, ECG abnormalities, or murmurs with spoiler answers. |
| `/flashcard [subject]` | All Members | Alias for `/pearl`. Supports Neurology, Pharmacology, Surgery, Pathology, etc. |

---

### Module 9: Bedside Clinical Calculators & Medical Scores 🧮
*Problem Solved:* Students and resident doctors waste time searching for medical calculators across multiple apps.  
*How It Works:* Instant in-chat clinical formulas with automatic interpretation, severity classifications, and clinical pearls.

| Command | Permission | Syntax & Example | Description |
| :--- | :--- | :--- | :--- |
| `/score bmi` | All Members | `/score bmi 70 175` | Weight (kg) & Height (cm) ➔ Calculates BMI with WHO and South Asian cutoff categories. |
| `/score map` | All Members | `/score map 120 80` | SBP & DBP ➔ Calculates Mean Arterial Pressure ($MAP = DBP + \frac{SBP-DBP}{3}$) and checks organ perfusion threshold (≥ 65 mmHg). |
| `/score gcs` | All Members | `/score gcs 4 5 6` | Eye (1-4), Verbal (1-5), Motor (1-6) ➔ Evaluates Total GCS / 15 and brain injury severity. |
| `/score aniongap` | All Members | `/score aniongap 140 102 24` | Na⁺, Cl⁻, HCO₃⁻ ➔ Calculates Serum Anion Gap with HAGMA / NAGMA interpretation. |
| `/score list` | All Members | `/score list` | Displays quick guide for all medical calculators. |

---

### Module 10: Synchronized Focus Study Sprint (Pomodoro) ⏳
*Problem Solved:* High distraction levels in study groups.  
*How It Works:* Group members can launch a synchronized focus study sprint (default 25 min or custom 10-120 min). The bot announces deep work rules and non-blocking background async timer sends a celebration alert with a 5-minute break reminder once the sprint concludes.

| Command | Permission | Syntax & Example |
| :--- | :--- | :--- |
| `/pomodoro [minutes]` | All Members | `/pomodoro 25` ➔ Starts a 25-minute deep focus study timer in the group. |
| `/focus [minutes]` | All Members | `/focus 50` ➔ Starts a 50-minute double study sprint. |

---

### Module 11: Student Doubt Drop Box & Discussion Engine ❓
*Problem Solved:* Questions asked in noisy groups get lost without peer or faculty resolution.  
*How It Works:* Formats student doubts into a standardized Case Discussion Card tagged with a unique ticket `#DOUBT-XXXX`. Notifies group members to discuss and simultaneously alerts Master Admins at the Kind Doctor Desk in private DM.

| Command | Permission | Syntax & Example |
| :--- | :--- | :--- |
| `/ask <question>` | All Members | `/ask What is the first-line treatment for acute hyperkalemia with ECG changes?` |

---

---

### Module 12: 100% Anonymous Bidirectional Support Relay 💬
*Problem Solved:* Admin wants to answer student queries, doubts, and batch join requests directly from their personal Telegram, without exposing their personal phone number, private username, or personal identity.  
*How It Works:* 
1. When ANY student sends a private message, question, voice note, photo, or PDF to `@KindDoc_bot`, the bot captures their full intel dossier (Name, Username, ID, Language, Premium status).
2. The bot simultaneously broadcasts this inquiry to **Kind Doctor's two official personal accounts**:
   - **Primary 1**: `@Kinddoctor4u` (`1553619403`)
   - **Primary 2**: `@Ammitrajput1` (`759038032`)
3. The message pair mapping is stored in RAM and permanently written to SQLite table `telegram_relay_map`.
4. The student receives an immediate professional delivery confirmation:
   > *📩 Message Delivered to Kind Doctor Desk! 🩺 Aapka message safely Kind Doctor tak pahunch gaya hai...*
5. **How to Reply:** Admin simply taps Telegram's native **'Reply'** button on the forwarded message and types the response.
6. The bot captures the reply and delivers it to the student under the official brand signature:
   > *👨‍⚕️ Kind Doctor: <Response>*
7. The student NEVER sees the admin's personal profile or account ID. Total anonymity & privacy are guaranteed.

---

### Module 13: 30-Minute Auto-Delete Welcome System 👋
*Problem Solved:* Group chats become clogged with hundreds of spammy "User joined" bubbles and welcome messages.  
*How It Works:*
1. When a new member joins via invite link:
   - Bot mentions the user with clickable link (even if they have no `@username`).
   - Dispatches a 30-minute (`1800s`) auto-delete task in the background.
2. When a member is added by an existing member:
   - Bot detects the inviter and tags BOTH the new member AND the inviter (`Added by: @Inviter`).
3. After exactly 30 minutes, the welcome message is automatically deleted via Telegram API `deleteMessage`, keeping the chat 100% pristine.

---

### Module 14: Personal ID & Support Commands 🆔
| Command | Permission | Description |
| :--- | :--- | :--- |
| `/support` or `/contact` | All Members | Explains how to directly and privately contact Kind Doctor through the bot. |
| `/id` or `/myid` | All Members | Instantly displays the user's permanent numerical Telegram ID (used for admin linking and support). |

---

### Module 15: Universal In-Topic Media Downloader & Multi-Group Forum Engine 🎥
*Problem Solved:* Medical students and faculties frequently find high-yield video lectures, clinical tutorials, reels, and files across YouTube, Instagram, Twitter/X, and the web. Manually downloading, converting, and uploading them into specific Telegram Forum Topics across different study groups is slow, tedious, and prone to cross-group confusion.  
*How It Works:*
1. **Direct In-Topic Execution (100% Group Isolation):** Simply navigate to ANY group Forum Topic (e.g. `🩺 DAMS`, `🧪 Prepladder Pharmacology`, or `📚 Marrow`) and drop a media link with `/ytdl <link>` or `/upload <link>`. Telegram automatically passes that specific group's unique negative ID, guaranteeing **zero cross-talk between different groups**.
2. **Context-Aware Uploading:** The engine automatically captures the active `message_thread_id` and delivers the downloaded media **directly inside that exact topic thread**, keeping all lectures perfectly organized.
3. **Sequential Playlist Uploader:** Provide a full YouTube playlist URL (`/playlist <url> [Topic]`). The bot extracts every lecture, generates serial indices (`Part 01/25`, `Part 02/25`), and sequentially uploads them in perfect curriculum order.
4. **Instant Topic Creator (`/newtopic`):** Create new forum topics dynamically on the fly (e.g. `/newtopic DAMS`). The bot maps it into SQLite and allows immediate lecture delivery.
5. **Multi-Group Target Switcher (`/setgroup`):** When commanding the bot from **Private DM**, type `/setgroup` to view an interactive list of all registered groups where the bot is an admin. Tap your desired group (e.g., `[ 🏛️ Study Help 😉 ]`), and the bot remembers it as your active working group for all subsequent DM actions.
6. **Clinical Tagging & Metadata:** Auto-extracts HD thumbnails, title, duration, author, and applies standardized medical tags:
   `#MedicalLecture #KindDoctor #ClinicalRevision`
7. **Zero Disk Clutter Guarantee:** All downloaded temporary files and thumbnail artifacts are automatically unlinked and purged from local disk immediately upon successful delivery.
8. **Dual Bot API & MTProto Engine:** Automatically routes files $\le 48\text{ MB}$ via native Telegram Bot API `sendVideo`, and seamlessly switches to Telethon MTProto for larger lectures (up to 2GB+) with full video streaming support (`supports_streaming=True`).

| Command | Permission | Syntax & Example | Description |
| :--- | :--- | :--- | :--- |
| `/ytdl <url> [Topic]` | All Members | `/ytdl https://youtu.be/... DAMS` | Downloads YouTube video/Short and uploads directly to the specified or current Forum Topic. |
| `/upload <url> [Topic]` | All Members | `/upload https://instagram.com/reel/...` | Universal uploader for Instagram Reels, Twitter/X videos, TikTok, and direct file links (`.mp4`, `.pdf`, `.zip`). |
| `/playlist <url> [Topic]` | Admin & All | `/playlist https://youtube.com/playlist?list=... DAMS` | Sequentially downloads and uploads an entire lecture playlist into the topic. |
| `/newtopic <Name> [chat_id]` | Admin | `/newtopic DAMS` | Creates a new Forum Topic in the group or active target chat. |
| `/setgroup` | Admin | `/setgroup` | Displays interactive buttons to select which group to manage when issuing commands from Private DM. |
| `/mediahelp` | All Members | `/mediahelp` | Interactive quick manual explaining supported media formats, multi-group handling, and topic uploading. |
| `/dl <url>` or `/leech <url>` | All Members | `/dl https://example.com/lecture.mp4` | Aliases for `/upload` and `/ytdl`. |

*Multi-Group Mechanics (How the Bot Knows Which Group to Target):*
- **Inside Group A or Group B (`chat_id < 0`):** Telegram guarantees group isolation. Running `/newtopic DAMS` or `/ytdl <url>` inside Group A creates/uploads strictly in Group A. Group B is completely untouched.
- **Inside Private DM (`chat_id > 0`):** Since private chat has no forum topics, run `/setgroup` to pick which group you are targeting, or append the target group ID to the command (e.g. `/newtopic DAMS -1003912970546`). Status progress is reported live in your DM while media is delivered into the group!

*Slashless Natural Language Support:*  
In Forum Topics, group members can simply mention the bot or send a message starting with `upload`, `download`, `ytdl`, or `playlist` followed by the URL, and the bot will autonomously detect and process the lecture!

---

### Module 16: Deep Cloner & Permanent Vault Archive Architecture 🛡️
*Problem Solved:* Channels get struck, banned, or deleted by copyright claims. Study groups lose years of meticulously organized medical notes and video libraries.  
*The Permanent Vault Principle:*
- **Zero Deletion Synchronization:** Unlike standard forwarders that blindly mirror deletions, Kind Doctor's Deep Cloner strictly enforces the **Permanent Vault Principle**. If a source channel, admin, or copyright holder deletes messages in the source group, the destination backup vault **NEVER deletes them**.
- **Immutable Archiving:** Destination topics and channels act as an indestructible permanent medical vault.
- **Topic Hierarchy Preservation:** Clones entire forum supergroups recursively, recreating topics and mapping lecture items without broken forward tags.

| Command | Permission | Syntax & Example | Description |
| :--- | :--- | :--- | :--- |
| `/clone <src> <tgt>` | Admin | `/clone -1003504807114 -1004313086843` | Clones entire source forum hierarchy into target group with zero forward tags. |
| `/clone <src> <tgt> <src_top> <tgt_top>` | Admin | `/clone <src> <tgt> 45 102` | Clones a single specific forum topic into a target topic. |
| `/clone <msg_link>` | Admin | `/clone https://t.me/c/3912970546/22803/45` | Instantly mirrors a single lecture message into the active topic. |
| `/clonestatus` | Admin | `/clonestatus` | Real-time interactive radar displaying active clone jobs, throughput, and pause/resume controls. |
| `/pauseclone` / `/resumeclone` | Admin | `/pauseclone` / `/resumeclone` | Non-destructive pause and resume of long-running cloning tasks. |
| `/stopclone` | Admin | `/stopclone` | Cancels a running clone job cleanly. |

---

### Module 17: Watermark & Strip Words Studio 🛡️
*Problem Solved:* Cloned and forwarded medical lectures are often cluttered with competitor watermarks, sponsor channels, promotional hashtags, and unwanted URLs.  
*Capabilities:*
- **Direct Removal:** Words, URLs, or channel tags are completely eliminated from captions and filenames.
- **Replacement Mapping:** `OldBrand => NewBrand` syntax replaces competitor branding with custom signatures.
- **Regex Pattern Matching:** Strips dynamic tags and complex patterns without breaking caption formatting.
- **Case-Insensitive Deduplication:** Auto-deduplicates active strip rule sets across `strip_words.txt`, `Friend_Edition/strip_words.txt`, and SQLite.

| Command | Permission | Syntax & Example | Description |
| :--- | :--- | :--- | :--- |
| `/striphelp` | All Members | `/striphelp` | Interactive Watermark & Strip Words Studio guide card with 1-click action buttons. |
| `/stripwords` | Admin | `/stripwords` | Interactive paginated card showing all active strip and replacement rules. |
| `/addstrip <rule>` | Admin | `/addstrip @SpamChannel` or `/addstrip OldBrand => Kind Doctor` | Adds a direct removal word or replacement mapping rule. |
| `/delstrip <rule>` | Admin | `/delstrip @SpamChannel` | Deletes a rule with automatic safety snapshot creation. |
| `/dedupstrip` | Admin | `/dedupstrip` | Cleans empty lines and deduplicates active rules across storage. |
| `/syncstrip` | Admin | `/syncstrip` | Synchronizes rules between text files and the SQLite database. |
| `/pacing` | Admin | `/pacing` | Opens interactive transmission speed slider and rate-limit delay presets. |

---

## 🚀 4. How ANY Group Admin Can Setup `@KindDoc_bot`

1. Open Telegram and search for [@KindDoc_bot](https://t.me/KindDoc_bot).
2. Click **Add to Group or Channel** and select your group.
3. In Group Settings, promote `@KindDoc_bot` as an **Administrator** with permissions:
   - *Send Messages*, *Pin Messages*, *Manage Topics*, *Delete Messages* (mandatory for auto-delete welcome & cleanups).
4. Run `/topics` or `/settopic 1 Anatomy` to begin organizing notes, or run `/scan` for 1-Click auto-indexing.
5. Setup FAQs via `/setfaq drive <link>` so your members get instant answers.
6. Run `/mcq Physiology` to conduct your first interactive group quiz!
7. Drop any video or playlist link with `/ytdl <link>` inside any forum topic to build your instant media library!

---

## 💻 5. Running the Bot Daemon (Windows PC)

Simply double-click the 1-click launcher script in the project directory:
👉 `START_KIND_DOCTOR_BOT.bat`

*Authored by Kind Doctor Engineering Team | Protected by Forwarder Core 2026*
