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
> — View warnings, moderation logs, and manage your servers from your browser.

</div>

---

## ✨ Features

| | Feature | Details |
|---|---|---|
| ⚡ | **Slash Commands Only** | All commands are registered as application commands — no prefix mess |
| 🔨 | **Moderation Commands** | `/kick`, `/ban`, `/unban`, `/warn`, `/removewarn`, `/warnings`, `/clear`, `/slowmode`, `/lockdown`, `/unlock` |
| 🛡️ | **Auto‑Moderation** | Anti‑spam · Anti‑invite links · Anti‑mass‑mention |
| 📋 | **Mod Logging** | Every action is logged to a dedicated channel with rich embeds |
| 🗄️ | **MongoDB Storage** | Warnings, infractions & guild configs are persisted |
| 🎨 | **Clean Embeds** | All responses use colored embeds with consistent styling |
| 📖 | **Interactive Help** | `/help` dynamically lists all commands grouped by category |
| 🚀 | **Easy Deployment** | Ready for Railway with `requirements.txt` & `Procfile` |

---

## 🛠️ Commands Overview

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
| `/help` | Show all available slash commands in a categorized embed | Everyone |

---

## 🛡️ Auto‑Moderation Rules

> Users with `Manage Messages` permission are **immune** to auto-mod actions.

| Rule | Threshold | Action |
|---|---|---|
| 🔁 Spam | > 5 messages in 5 seconds | Delete message + warn via DM |
| 🔗 Discord Invites | Any `discord.gg` / `discord.com/invite` link | Delete message + warn |
| 📣 Mass Mention | > 5 user/role mentions or `@everyone` | Delete message + warn |

All violations are logged to the configured mod‑log channel.

---

## 📝 Mod Logging

Set a mod‑log channel with `/setmodlog`. Every moderation action will be sent there as a detailed embed.

Each log embed includes:

- 🏷️ **Action type**
- 👮 **Moderator** — who performed the action
- 🎯 **Target** — member/user affected
- 📄 **Reason** — if applicable
- 🆔 **Warning ID** — for warns
- 🕐 **Timestamp**

---

## 🌐 Web Dashboard

The iSida bot comes with a companion web dashboard where server administrators can:

- 📋 View all warnings issued in their server
- 🔍 Browse moderation logs (kicks, bans, warns, etc.)
- 🖥️ Manage multiple servers from one interface

**🔗 Dashboard URL**: [https://isida-dashboard.onrender.com](https://isida-dashboard.onrender.com)

> To use the dashboard, deploy the separate **iSida Dashboard** repository (FastAPI + MongoDB). Instructions are in that repo's README.

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
# Push your code to GitHub, then:
# 1. Connect your repository on Railway
# 2. Railway auto-detects Procfile and requirements.txt
# 3. Add environment variables in Railway dashboard
```

### 5️⃣ Invite the Bot

Use the **OAuth2 URL Generator** with these scopes & permissions:

- ✅ Scopes: `applications.commands`, `bot`
- ✅ Permissions: `Kick Members`, `Ban Members`, `Manage Messages`, `Manage Channels`, etc.

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
echo "DISCORD_TOKEN=your_token_here" >> .env
echo "MONGO_URI=your_mongo_uri_here" >> .env

# 5. Run the bot
python main.py
```

---

## ⚠️ Important Notes

> **Python 3.12 is required** — The bot uses `audioop` which was removed in Python 3.13.
> A `runtime.txt` file is included to force Python 3.12 on Railway.

- 🚫 The bot uses **slash commands only** — prefix commands are not supported
- 🌐 To use the dashboard, deploy the separate **iSida Dashboard** repo (FastAPI web interface)

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or pull requests.
For major changes, please open an issue first to discuss what you'd like to change.

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](./LICENSE) file for details.

---

## 📬 Support

For questions or support:
- 🐛 Open an **issue** on GitHub
- 💬 Contact the maintainer on **Discord**

---

<div align="center">

Made with ❤️ by [bytesal](https://github.com/bytesal)

[![GitHub](https://img.shields.io/badge/GitHub-bytesal-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/bytesal/iSida)

</div>
