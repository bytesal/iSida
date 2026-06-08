<div align="center">

<img src="https://img.shields.io/badge/iSida-Discord%20Bot-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="iSida Discord Bot"/>

# 🤖 iSida — Discord Moderation Bot

**Professional moderation bot built with `discord.py` & MongoDB**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![discord.py](https://img.shields.io/badge/discord.py-2.x-5865F2?style=flat-square&logo=discord&logoColor=white)](https://discordpy.readthedocs.io/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=flat-square&logo=mongodb&logoColor=white)](https://www.mongodb.com/cloud/atlas)
[![Railway](https://img.shields.io/badge/Deploy-Railway-0B0D0E?style=flat-square&logo=railway&logoColor=white)](https://railway.app/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](./LICENSE)

<br/>

> 🌐 **Web Dashboard**: [isida-dashboard.onrender.com](https://isida-dashboard.onrender.com)
> — Manage warnings, mod logs, verification settings & transcripts from any browser.

</div>

---

## ✨ Features

| | Feature | Details |
|---|---|---|
| ⚡ | **Slash Commands Only** | Fully typed commands with descriptions — no prefix confusion |
| 🔨 | **Full Moderation Suite** | `/kick`, `/ban`, `/unban`, `/warn`, `/removewarn`, `/warnings`, `/clear`, `/slowmode`, `/lockdown`, `/unlock` |
| 🛡️ | **Auto‑Moderation** | Anti‑spam · Anti‑invite links · Anti‑mass‑mention |
| 📌 | **Sticky Messages** | `/sticky set` keeps a message always at the bottom of a channel |
| ✅ | **Reaction Role Verification** | New members muted until they react — fully configurable |
| 🎫 | **Ticket Transcripts** | Save full ticket conversations to MongoDB & view on dashboard |
| 🌐 | **Web Dashboard** | Manage everything via browser with secure Discord OAuth2 login |
| 📋 | **Detailed Logging** | Every action stored in MongoDB + sent as rich embed to Discord |
| 🗄️ | **MongoDB Persistence** | Warnings, configs, sticky messages, transcripts — all permanent |
| 🎨 | **Clean Embeds** | Colored embeds with consistent styling across all responses |
| 📖 | **Dynamic Help** | `/help` auto-updates when new cogs are added |

---

## 📁 Repository Structure

```
iSida/
├── main.py
├── requirements.txt
├── runtime.txt
├── Procfile
├── .env.example
├── cogs/
│   ├── moderation.py
│   ├── help.py
│   ├── sticky.py
│   ├── verification.py
│   └── transcripts.py
├── utils/
│   ├── database.py
│   ├── embeds.py
│   ├── anti_spam.py
│   ├── logger.py
│   └── permissions.py
└── models/
    └── warning.py
```

---

## 🛠️ Commands Overview

### 🔨 Moderation

| Command | Description | Required Permission |
|---|---|---|
| `/kick` | Kick a member from the server | `Kick Members` |
| `/ban` | Ban a user (by ID or mention) | `Ban Members` |
| `/unban` | Unban a user by their ID | `Ban Members` |
| `/warn` | Issue a warning to a member | `Moderate Members` |
| `/removewarn` | Remove a warning using its MongoDB ObjectId | `Moderate Members` |
| `/warnings` | List all warnings for a specific member | `Moderate Members` |
| `/clear` | Delete up to 100 messages (optionally filter by member) | `Manage Messages` |
| `/slowmode` | Set slowmode delay (0–21600 seconds) for the channel | `Manage Channels` |
| `/lockdown` | Lock the current channel (prevent @everyone from sending) | `Manage Channels` |
| `/unlock` | Unlock the current channel | `Manage Channels` |
| `/setmodlog` | Set a channel where all moderation logs will be sent | `Administrator` |

### 📌 Sticky Messages

| Command | Description | Required Permission |
|---|---|---|
| `/sticky set` | Set a sticky message in the current channel | `Manage Messages` |
| `/sticky remove` | Remove the sticky message from the current channel | `Manage Messages` |
| `/sticky view` | View the current sticky message | Everyone |

### ✅ Verification

| Command | Description | Required Permission |
|---|---|---|
| `/verify set_channel` | Set the channel for verification messages | `Administrator` |
| `/verify set_role` | Set the role to assign after verification | `Administrator` |
| `/verify set_emoji` | Set the emoji to react with (default: ✅) | `Administrator` |
| `/verify create` | Create the verification message in the configured channel | `Administrator` |
| `/verify setup_mute` | Apply Muted role permissions to all channels | `Administrator` |
| `/verify disable` | Disable the verification system | `Administrator` |

### 🎫 Transcripts & Help

| Command | Description | Required Permission |
|---|---|---|
| `/transcript` | Save the current ticket channel as a transcript | `Manage Messages` |
| `/help` | Show all available slash commands | Everyone |

---

## 🛡️ Auto‑Moderation Rules

> Users with `Manage Messages` permission are **immune** to auto-mod actions.

| Rule | Threshold | Action |
|---|---|---|
| 🔁 Spam | > 5 messages in 5 seconds | Delete message + warn via DM |
| 🔗 Discord Invites | Any `discord.gg` / `discord.com/invite` link | Delete message + warn |
| 📣 Mass Mention | > 5 user/role mentions or `@everyone` | Delete message + warn |

All violations are logged to the configured mod‑log channel and stored in MongoDB.

---

## 📌 Sticky Messages

Use `/sticky set` to make any message stay at the bottom of a channel. If deleted by a user or another bot, iSida reposts it automatically. Background check runs every **10 seconds**.

---

## ✅ Verification System

When configured, new members receive the `Muted` role upon joining (cannot send messages or create threads). After reacting with the configured emoji:

- ✅ `Muted` role is removed
- 🎭 Optional verification role is assigned
- 💬 Confirmation DM is sent to the member

> All settings are stored in MongoDB and can also be managed via the web dashboard.

---

## 🎫 Ticket Transcripts

Use `/transcript` inside any ticket channel. The bot saves the **last 500 messages** into the `ticket_transcripts` MongoDB collection.

Then visit: **Dashboard → Select Server → Transcripts** to view all saved conversations.

---

## 🌐 Web Dashboard

The dashboard is a separate **FastAPI** application connecting to the same MongoDB database.

- 📋 View all warnings (moderator name, reason, timestamp)
- 🔍 Browse all moderation logs (kick, ban, warn, clear, slowmode, etc.)
- ⚙️ Configure verification settings without slash commands
- 📄 View saved ticket transcripts
- 🔐 Secure Discord OAuth2 login — only server admins/owners can access

> Dashboard repository and deployment instructions are available separately.

**🔗 Dashboard URL**: [https://isida-dashboard.onrender.com](https://isida-dashboard.onrender.com)

---

## 🚀 Deployment (Railway)

### 1️⃣ Create a Discord Application

- Go to [Discord Developer Portal](https://discord.com/developers/applications)
- Create a new application → **Bot** → Copy token
- Enable **MESSAGE CONTENT INTENT** and **SERVER MEMBERS INTENT**

### 2️⃣ Set up MongoDB Atlas

- Create a free cluster at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- Get your connection string: `mongodb+srv://...`

### 3️⃣ Configure Environment Variables

Create a `.env` file (or set them directly in Railway):

```env
DISCORD_TOKEN=your_bot_token_here
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
```

### 4️⃣ Deploy to Railway

```bash
# 1. Push your code to GitHub
# 2. Connect your repository on Railway
# 3. Railway auto-detects Procfile and requirements.txt
# 4. Add environment variables in Railway dashboard
```

### 5️⃣ Verify the Bot is Running

- Check Railway logs for `Logged in as iSida#...`
- Type `/help` in your server

---

## 💻 Local Development

```bash
# 1. Clone the repository
git clone https://github.com/bytesal/iSida.git
cd iSida

# 2. Create virtual environment (Python 3.12)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Then fill in DISCORD_TOKEN and MONGO_URI

# 5. Run the bot
python main.py
```

---

## ⚠️ Important Notes

> **Python 3.12 is required** — The bot uses `audioop` which was removed in Python 3.13.
> A `runtime.txt` file is included to force Python 3.12 on Railway.

- 🚫 The bot uses **slash commands only** — prefix commands are not supported
- 🔽 The `Muted` role must be **below** the bot's role in the role hierarchy
- 📊 For the dashboard to display logs, the bot must have stored data in MongoDB first
- 🌐 To use the dashboard, deploy the separate **iSida Dashboard** repo (FastAPI)

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or pull requests.
For major changes, please open an issue first to discuss what you'd like to change.

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](./LICENSE) file for details.

---

## 📬 Support

| | Link |
|---|---|
| 🌐 Dashboard | [isida-dashboard.onrender.com](https://isida-dashboard.onrender.com) |
| 🤖 Invite Bot | [Invite Link](https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=6711012374&scope=bot+applications.commands) |
| 💬 Support Server | [Join Discord](https://discord.gg/AK4qMNdaWp) |
| 🐛 Issues | [Open an Issue on GitHub](https://github.com/bytesal/iSida/issues) |

---

<div align="center">

Made by [bytesal](https://github.com/bytesal)

[![GitHub](https://img.shields.io/badge/GitHub-bytesal-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/bytesal/iSida)
[![Discord](https://img.shields.io/badge/Support-Discord-5865F2?style=flat-square&logo=discord&logoColor=white)](https://discord.gg/AK4qMNdaWp)

</div>
