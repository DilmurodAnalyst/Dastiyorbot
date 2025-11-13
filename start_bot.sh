#!/bin/bash

# Dastiyorbot Startup Script

echo "🤖 Dastiyorbot - Advanced Media Downloader"
echo "=========================================="

# Kill any existing instances
pkill -f "python index.py" 2>/dev/null || true
sleep 1

# Check if bot token is set
if [ -z "$BOT_TOKEN" ]; then
    echo "❌ Error: BOT_TOKEN environment variable not set"
    echo "Set it with: export BOT_TOKEN='your_token_here'"
    exit 1
fi

# Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ Error: FFmpeg is not installed"
    echo "Install with: sudo apt-get install ffmpeg"
    exit 1
fi

# Install/upgrade dependencies
echo "📦 Installing dependencies..."
pip install -q --upgrade yt-dlp

# Create downloads directory
mkdir -p downloads

# Run the bot
echo "✅ Starting bot..."
echo "Press Ctrl+C to stop"
python index.py
