# Dastiyorbot - Advanced Media Downloader Bot

A powerful Telegram bot for downloading videos and audio from YouTube, Instagram, and Facebook.

## Features

- 🎬 **YouTube**: Download videos (144p-1080p) or extract audio (MP3)
- 📱 **Instagram**: Download posts, reels, and stories
- 📘 **Facebook**: Download public videos
- 🌐 **Multi-language Support**: Uzbek, Russian, English
- ⚙️ **FFmpeg Integration**: Professional audio/video processing

## Prerequisites

- Python 3.8+
- FFmpeg (automatically installed)
- Telegram Bot Token (from BotFather)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/DilmurodAnalyst/Dastiyorbot.git
cd Dastiyorbot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### 4. Set Up Bot Token
Create a `.env` file:
```bash
cp .env.example .env
# Edit .env and add your bot token
```

Or set environment variable:
```bash
export BOT_TOKEN='your_bot_token_here'
```

## Quick Start

### Local Development
```bash
python index.py
```

### GitHub as Server
Your code is hosted on GitHub. To deploy:

1. **Enable GitHub Actions** in your repository settings
2. **Add your bot token** as a secret:
   - Go to Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `BOT_TOKEN`
   - Value: Your Telegram bot token

3. **Create workflow file** `.github/workflows/bot.yml`:
```yaml
name: Telegram Bot
on:
  push:
    branches: [main]
  workflow_dispatch:
jobs:
  run-bot:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install system dependencies
        run: sudo apt-get update && sudo apt-get install -y ffmpeg
      - name: Install Python dependencies
        run: pip install -r requirements.txt
      - name: Run bot
        env:
          BOT_TOKEN: ${{ secrets.BOT_TOKEN }}
        run: python index.py
```

## Docker Support

```dockerfile
FROM python:3.10-slim
RUN apt-get update && apt-get install -y ffmpeg
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "index.py"]
```

Build and run:
```bash
docker build -t dastiyorbot .
docker run -e BOT_TOKEN='your_token' dastiyorbot
```

## Configuration

Edit `index.py` to customize:
- Maximum file size (50MB default)
- Download quality options
- Supported platforms
- Translations

## How It Works

1. User sends a link from supported platform
2. Bot detects the platform
3. User selects format and quality
4. Bot downloads using yt-dlp + FFmpeg
5. Bot uploads file to Telegram
6. File is deleted after upload

## Security

⚠️ **Never commit your bot token!** Use environment variables or GitHub Secrets instead.

## Troubleshooting

### "Bot already running" error
```bash
pkill -f "python index.py"
```

### FFmpeg not found
Ensure FFmpeg is installed and in PATH:
```bash
ffmpeg -version
```

### Download timeout
Increase socket timeout in download functions (currently 60s)

### Instagram/Facebook downloads not working
- Ensure User-Agent headers are present (✓ Already configured)
- Check if content is public
- Verify yt-dlp is up to date: `pip install --upgrade yt-dlp`

## Deployment

### Option 1: Local Machine / VPS
```bash
# Set bot token
export BOT_TOKEN='your_bot_token_here'

# Optional: Set YouTube cookies for protected videos
export YT_COOKIES_FILE='/path/to/cookies.txt'

# Run the bot
python index.py
```

### Option 2: GitHub Actions (Continuous Deployment)

1. **Add Bot Token as Secret**:
   - Go to: Settings → Secrets and Variables → Actions
   - Click "New repository secret"
   - Name: `BOT_TOKEN`
   - Value: Your Telegram bot token

2. **Optional: Add YouTube Cookies**:
   - Name: `YT_COOKIES_FILE`
   - Value: Base64-encoded cookies.txt content (or path)

3. **The bot will run automatically** with every push via `.github/workflows/deploy-bot.yml`

### Option 3: Docker (Production)

```bash
# Build Docker image
docker build -t dastiyorbot .

# Run container
docker run -e BOT_TOKEN='your_token' dastiyorbot
```

### Option 4: Heroku / Railway / Replit

1. Fork this repository
2. Connect your Git repo to the hosting service
3. Add environment variables in the platform's dashboard:
   - `BOT_TOKEN` = Your bot token
   - `YT_COOKIES_FILE` = (optional) path to cookies file
4. Deploy!

## YouTube Authentication (Cookies Setup)

Some YouTube videos require authentication. To fix this:

**Step 1: Export Your Browser's YouTube Cookies**

```bash
# Using yt-dlp with your browser
yt-dlp --cookies-from-browser chrome --skip-download 'https://www.youtube.com'
```

This creates a `cookies.txt` file.

**Step 2: Use Cookies with Bot**

```bash
# Before running the bot:
export YT_COOKIES_FILE='/path/to/cookies.txt'
export BOT_TOKEN='your_token'
python index.py
```

Alternatively, for GitHub Actions:
- Add `YT_COOKIES_FILE` to repository secrets

**Supported Browsers:**
- Chrome
- Firefox  
- Edge
- Safari

## Dependencies

- `python-telegram-bot==20.5` - Telegram Bot API
- `yt-dlp` - Video downloader with FFmpeg support
- `ffmpeg` - Audio/video processing (system dependency)

## File Structure

```
Dastiyorbot/
├── index.py              # Main bot code
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── README.md            # This file
└── downloads/           # Downloaded files (temporary)
```

## Recent Updates

✅ **Fixed Issues:**
- Installed FFmpeg for video/audio processing
- Improved error handling with try-catch blocks
- Increased socket timeouts from 30s to 60s
- Added User-Agent headers for better compatibility
- Simplified Instagram download logic
- Added file existence verification

## License

MIT License

## Support

For issues, create a GitHub issue or contact the maintainer.

---

Made with ❤️ by DilmurodAnalyst