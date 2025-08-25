#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # exit on error

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔧 Setting up yt-dlp..."
# Ensure yt-dlp is properly configured
python -c "import yt_dlp; print('yt-dlp version:', yt_dlp.version.__version__)"

echo "🎵 Setting up YTMusic API..."
# Test YTMusic API
python -c "from ytmusicapi import YTMusic; ytmusic = YTMusic(); print('YTMusic API initialized successfully')"

echo "✅ Build completed successfully!"
