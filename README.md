# 🛰️ Random Gif Sender Discord Bot

A professional, analytics-driven Discord bot built for media deployment, administration, and server connectivity.

## ✨ Core Features
- **Smart Media Engine:** Randomly serves media from a persistent `.txt` database.
- **Global Cooldown Control:** Shared recharge timer to prevent spam, featuring a bypass role system.
- **Live Analytics:** Track uptime, database growth, and recent user interactions via `.status`.
- **Admin Suite:** Effortless database management (`.addgif`, `.giflist`) and chat moderation (`.clear`).
- **Resilient Storage:** Designed for persistent hosting (like Wispbyte), ensuring data survival after restarts.

## 🛠️ Configuration
Edit the `main.py` file to include your specific IDs:
- `ROLE_BYPASS_ID`: Trusted role to ignore cooldowns.
- `LOG_CHANNEL_ID`: Channel for administrative logs.
- `YOUR_BOT_TOKEN_HERE`: Your Discord application token.

## 📦 Requirements
```text
discord.py
datetime
