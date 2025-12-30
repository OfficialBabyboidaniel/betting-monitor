# 🎯 Rebel Betting Monitor

**Automated 24/7 value betting detection with instant phone notifications**

Never miss a profitable betting opportunity again! This Docker-containerized monitor continuously scans RebelBetting.com for value bets and sends instant notifications to your phone the moment opportunities are detected.

## ✨ Features

- 🔄 **24/7 Automated Monitoring** - Continuously checks for value bets every 60 seconds
- 📱 **Instant Phone Notifications** - Get alerted immediately via Telegram, Pushbullet, Discord, or Email
- 🐳 **Docker Containerized** - Easy deployment and management on any server
- 🛡️ **Undetected Chrome** - Uses stealth browser to avoid bot detection
- 🔄 **Auto-Restart** - Automatically recovers from crashes with health monitoring
- 📊 **Resource Optimized** - Lightweight container with memory and CPU limits
- 🔐 **Secure** - Credentials stored safely in environment variables

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/OfficialBabyboidaniel/betting-monitor.git
cd betting-monitor
```

### 2. Setup Notifications (2 minutes)
**Telegram (Recommended - 100% Free):**
1. Install Telegram Messenger on your phone
2. Message `@BotFather` → send `/newbot` → follow prompts
3. Message `@userinfobot` to get your chat ID
4. Add both tokens to `.env` file

### 3. Configure & Deploy
```bash
# Setup environment
cp .env.example .env
nano .env  # Add your RebelBetting + notification credentials

# Deploy to server
chmod +x deploy.sh
./deploy.sh
```

## 📱 Notification Options (All Free!)

| Service | Setup Time | Reliability | Mobile App |
|---------|------------|-------------|------------|
| **Telegram** | 2 min | ⭐⭐⭐⭐⭐ | ✅ Native |
| **Pushbullet** | 1 min | ⭐⭐⭐⭐ | ✅ Native |
| **Discord** | 3 min | ⭐⭐⭐⭐ | ✅ Native |
| **Email** | 5 min | ⭐⭐⭐ | ✅ Built-in |

## 🛠️ Management Commands

```bash
# View live logs
docker-compose logs -f betting-monitor

# Check container status
docker ps

# Restart service
docker-compose restart betting-monitor

# Update to latest version
git pull && docker-compose up -d --build

# Stop monitoring
docker-compose down
```

## 📋 Requirements

- Ubuntu server with Docker & Docker Compose
- RebelBetting.com account
- Phone with notification app (Telegram recommended)

## 🔧 Configuration

The monitor automatically:
- Logs into your RebelBetting account
- Scans for value bets every 60 seconds
- Closes popup windows automatically
- Sends notifications when bets are detected
- Restarts if it encounters errors

## 📊 What You'll Get

When value bets are detected, you'll receive notifications like:
```
🎯 Value Bets Available!
3 value bets detected on RebelBetting!

Check your dashboard: https://vb.rebelbetting.com/login
```

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for improvements.

## ⚠️ Disclaimer

This tool is for educational purposes. Always comply with betting site terms of service and local gambling regulations.

---

**Made with ❤️ for profitable betting**