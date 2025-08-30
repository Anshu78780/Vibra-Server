# 🎵 Vibra Server - Music Backend API

A powerful, fast, and free music API that provides access to YouTube Music data, trending songs, playlists, recommendations, and audio streaming URLs. Built with Flask, YTMusicAPI, and yt-dlp.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Render](https://img.shields.io/badge/Deploy-Render-purple.svg)](https://render.com)

## ✨ Features

- 🔍 **Fast Music Search** - Search for songs using YTMusic API for lightning-fast results
- 🎧 **Audio Streaming** - Get direct audio URLs for any YouTube video/song
- 📊 **Trending Music** - Get trending playlists by country code (50+ countries supported)
- 🏠 **Homepage Data** - Access YouTube Music homepage and trending content  
- 🎯 **Smart Recommendations** - Get related songs and recommendations for any track
- 🌍 **Global Support** - Multi-country support with localized trending content
- ⚡ **High Performance** - Optimized with dual extraction methods (YTMusicAPI + yt-dlp)
- 🔧 **Easy Integration** - Simple REST API with JSON responses
- 🚀 **Production Ready** - Includes gunicorn, logging, error handling, and health checks

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Anshu78780/Vibra-Server.git
cd Vibra-Server
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## 📚 API Documentation

### Base URL
```
http://localhost:5000
```

### 🔍 Search Songs
Search for songs by query.

**Endpoint:** `GET /search`

**Parameters:**
- `q` (required): Search query
- `limit` (optional): Number of results (default: 10, max: 50)

**Example:**
```bash
curl "http://localhost:5000/search?q=imagine%20dragons&limit=5"
```

**Response:**
```json
{
  "success": true,
  "query": "imagine dragons",
  "results_count": 5,
  "songs": [
    {
      "id": "ktvTqknDobU",
      "title": "Radioactive",
      "artist": "Imagine Dragons",
      "duration": 187,
      "duration_string": "03:07",
      "thumbnail": "https://i.ytimg.com/vi/ktvTqknDobU/maxresdefault.jpg",
      "webpage_url": "https://www.youtube.com/watch?v=ktvTqknDobU"
    }
  ]
}
```

### 🎧 Get Audio URL
Get direct audio streaming URL for any video/song.

**Endpoint:** `GET /audio/{video_id}`

**Example:**
```bash
curl "http://localhost:5000/audio/ktvTqknDobU"
```

**Response:**
```json
{
  "success": true,
  "video_id": "ktvTqknDobU",
  "audio_url": "https://example-audio-url.com/audio.mp3",
  "message": "Audio URL retrieved successfully"
}
```

### 🏠 Homepage Data
Get trending music from YouTube Music homepage.

**Endpoint:** `GET /homepage`

**Parameters:**
- `limit` (optional): Number of results (default: 20, max: 50)

**Example:**
```bash
curl "http://localhost:5000/homepage?limit=20"
```

### 📊 Trending by Country
Get trending playlists for specific countries.

**Endpoint:** `GET /trending/{country_code}`

**Parameters:**
- `country_code` (required): 2-letter country code (US, IN, GB, etc.)
- `limit` (optional): Number of results (default: 50)

**Supported Countries:**
```
US, ZZ, AR, AU, AT, BE, BO, BR, CA, CL, CO, CR, CZ, DK, DO, EC, EG, SV, EE, FI, FR, DE, 
GT, HN, HU, IS, IN, ID, IE, IL, IT, JP, KE, LU, MX, NL, NZ, NI, NG, NO, PA, PY, PE, PL, 
PT, RO, RU, SA, RS, ZA, KR, ES, SE, CH, TZ, TR, UG, UA, AE, GB, UY, ZW
```

**Example:**
```bash
curl "http://localhost:5000/trending/IN?limit=20"
```

### 🎯 Recommendations  
Get song recommendations based on a track.

**Endpoint:** `GET /recommended/{video_id}`

**Parameters:**
- `video_id` (required): YouTube video ID
- `limit` (optional): Number of recommendations (default: 50)

**Example:**
```bash
curl "http://localhost:5000/recommended/ktvTqknDobU?limit=10"
```

### ❤️ Health Check
Check API status and service health.

**Endpoint:** `GET /health`

**Example:**
```bash
curl "http://localhost:5000/health"
```

## 🌐 Environment Variables

Create a `.env` file in the project root:

```env
# Flask Configuration
SECRET_KEY=your-super-secret-key-here
FLASK_DEBUG=false
FLASK_HOST=0.0.0.0
PORT=5000

# CORS Settings
CORS_ORIGINS=*

# YouTube Settings (optional, for avoiding bot detection)
YOUTUBE_COOKIES=your_youtube_cookies_here

# Logging
LOG_LEVEL=INFO
```

## 🐳 Docker Deployment

### Docker
```bash
# Build the image
docker build -t music-api .

# Run the container
docker run -p 5000:5000 music-api
```

### Docker Compose
```yaml
version: '3.8'
services:
  music-api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_DEBUG=false
      - PORT=5000
```

## ☁️ Deploy to Cloud

### Deploy to Render
1. Fork this repository
2. Connect to [Render](https://render.com)
3. Create a new Web Service
4. Connect your GitHub repository
5. Use these settings:
   - **Environment:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`

### Deploy to Railway
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template-id)

### Deploy to Heroku
```bash
# Install Heroku CLI
heroku create your-app-name
git push heroku main
```

## 🔧 Configuration

### Rate Limiting (Optional)
For production use, consider adding rate limiting:

```bash
pip install flask-limiter
```

### Caching (Optional)  
For better performance, add Redis caching:

```bash
pip install flask-caching redis
```

## 📊 API Usage Examples

### Python
```python
import requests

# Search for songs
response = requests.get('http://localhost:5000/search?q=coldplay&limit=5')
songs = response.json()['songs']

# Get audio URL
audio_response = requests.get(f'http://localhost:5000/audio/{songs[0]["id"]}')
audio_url = audio_response.json()['audio_url']
```

### JavaScript/Node.js
```javascript
// Search for songs
const searchResponse = await fetch('http://localhost:5000/search?q=coldplay&limit=5');
const { songs } = await searchResponse.json();

// Get audio URL
const audioResponse = await fetch(`http://localhost:5000/audio/${songs[0].id}`);
const { audio_url } = await audioResponse.json();
```

### cURL
```bash
# Search
curl "http://localhost:5000/search?q=coldplay&limit=5"

# Get trending in India
curl "http://localhost:5000/trending/IN?limit=20"

# Get recommendations
curl "http://localhost:5000/recommended/ktvTqknDobU?limit=10"
```

## 🏗️ Project Structure

```
Vibra-Server/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── music_extractor.py    # Core music extraction logic
├── requirements.txt      # Python dependencies
├── gunicorn_config.py   # Gunicorn configuration
├── Procfile             # Process file for deployment
├── render.yaml          # Render deployment config
└── README.md           # This file
```

## 🛠️ Development

### Running in Development Mode
```bash
export FLASK_DEBUG=true
python app.py
```

### Running Tests
```bash
python test_charts.py
python test_trending.py
```

### Code Formatting
```bash
pip install black
black app.py music_extractor.py config.py
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. 🍴 Fork the repository
2. 🌟 Create a feature branch (`git checkout -b feature/amazing-feature`)
3. 💻 Make your changes
4. ✅ Run tests
5. 📝 Commit your changes (`git commit -m 'Add amazing feature'`)
6. 🚀 Push to the branch (`git push origin feature/amazing-feature`)
7. 🔄 Open a Pull Request

### Development Guidelines
- Follow PEP 8 Python style guidelines
- Add docstrings to all functions
- Include error handling
- Write tests for new features
- Update documentation

## 🐛 Known Issues & Limitations

- **Rate Limiting:** YouTube may rate-limit requests if too many are made quickly
- **Geo-restrictions:** Some content may not be available in certain regions  
- **Bot Detection:** Occasional failures due to YouTube's anti-bot measures
- **Audio URLs:** Direct audio URLs expire after some time (typically 1-6 hours)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube video/audio extraction
- [ytmusicapi](https://github.com/sigma67/ytmusicapi) - Unofficial YouTube Music API  
- [Flask](https://flask.palletsprojects.com/) - Web framework
- YouTube Music - Data source

## 📞 Support

- 🐛 **Issues:** [GitHub Issues](https://github.com/Anshu78780/Vibra-Server/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/Anshu78780/Vibra-Server/discussions)
- 📧 **Email:** [Your Email]

## 🚀 Roadmap

- [ ] Authentication system
- [ ] Rate limiting and caching
- [ ] WebSocket support for real-time updates
- [ ] Playlist management endpoints
- [ ] User favorites and history
- [ ] Audio transcoding options
- [ ] GraphQL support
- [ ] Admin dashboard

---

⭐ **Star this repository if it helped you!**

Made with ❤️ by [Anshu](https://github.com/Anshu78780)
