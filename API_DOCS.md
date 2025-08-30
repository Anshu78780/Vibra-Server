# API Documentation

## Base URL
```
https://your-api-domain.com
```

## Authentication
This API currently does not require authentication. All endpoints are publicly accessible.

## Rate Limiting
- Default: 100 requests per minute per IP
- When exceeded: HTTP 429 Too Many Requests

## Response Format

### Success Response
```json
{
  "success": true,
  "data": {...},
  "message": "Success message"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error description",
  "code": "ERROR_CODE"
}
```

## Endpoints

### 1. Search Songs
**GET** `/search`

Search for songs by query string.

**Parameters:**
- `q` (string, required): Search query
- `limit` (integer, optional): Number of results (1-50, default: 10)

**Example Request:**
```http
GET /search?q=imagine%20dragons&limit=5
```

**Example Response:**
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
      "poster_image": "https://i.ytimg.com/vi/ktvTqknDobU/maxresdefault.jpg",
      "webpage_url": "https://www.youtube.com/watch?v=ktvTqknDobU",
      "view_count": 1234567890,
      "uploader": "Imagine Dragons",
      "source": "ytmusicapi"
    }
  ]
}
```

### 2. Get Audio URL
**GET** `/audio/{video_id}`

Get direct audio streaming URL for a video.

**Parameters:**
- `video_id` (string, required): YouTube video ID

**Example Request:**
```http
GET /audio/ktvTqknDobU
```

**Example Response:**
```json
{
  "success": true,
  "video_id": "ktvTqknDobU",
  "audio_url": "https://example.com/audio.mp3",
  "message": "Audio URL retrieved successfully"
}
```

### 3. Homepage Data
**GET** `/homepage`

Get trending music from YouTube Music homepage.

**Parameters:**
- `limit` (integer, optional): Number of results (1-50, default: 20)

**Example Request:**
```http
GET /homepage?limit=20
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "trending_music": [
      {
        "id": "abc123",
        "title": "Popular Song",
        "artist": "Popular Artist",
        "category": "trending",
        "thumbnail": "https://example.com/thumb.jpg"
      }
    ],
    "categories": ["trending", "charts", "new_releases"],
    "total_results": 20
  }
}
```

### 4. Trending by Country
**GET** `/trending/{country_code}`

Get trending playlists for a specific country.

**Parameters:**
- `country_code` (string, required): 2-letter ISO country code
- `limit` (integer, optional): Number of results (1-50, default: 50)

**Supported Countries:**
`US, IN, GB, DE, FR, CA, AU, JP, KR, BR, MX, ES, IT, RU, TR, AR, etc.`

**Example Request:**
```http
GET /trending/IN?limit=10
```

**Example Response:**
```json
{
  "success": true,
  "country": "IN",
  "total_playlists": 10,
  "playlists": [
    {
      "title": "Trending in India",
      "playlistId": "PLiJ19Xxebz3nkJ7Rg1vgHzu-nSLmSig7t",
      "thumbnail": "https://example.com/playlist-thumb.jpg",
      "description": "Top trending songs in India",
      "url": "https://music.youtube.com/playlist?list=PLiJ19Xxebz3nkJ7Rg1vgHzu-nSLmSig7t"
    }
  ]
}
```

### 5. Recommendations
**GET** `/recommended/{video_id}`

Get song recommendations based on a specific track.

**Parameters:**
- `video_id` (string, required): YouTube video ID
- `limit` (integer, optional): Number of recommendations (1-50, default: 50)

**Example Request:**
```http
GET /recommended/ktvTqknDobU?limit=10
```

**Example Response:**
```json
{
  "success": true,
  "recommendations": {
    "video_id": "ktvTqknDobU",
    "recommendations_count": 10,
    "recommendations": [
      {
        "id": "def456",
        "title": "Similar Song",
        "artist": "Similar Artist",
        "duration": 180,
        "thumbnail": "https://example.com/thumb.jpg"
      }
    ]
  }
}
```

### 6. Health Check
**GET** `/health`

Check API health and service status.

**Example Request:**
```http
GET /health
```

**Example Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-30T13:30:00.000Z",
  "services": {
    "ytmusic_api": "OK",
    "search_function": "OK",
    "yt_dlp": "OK"
  },
  "version": "1.0.0",
  "environment": "production"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `INVALID_QUERY` | Search query is missing or invalid |
| `VIDEO_NOT_FOUND` | Requested video ID does not exist |
| `EXTRACTION_FAILED` | Failed to extract audio URL |
| `RATE_LIMITED` | Too many requests, please wait |
| `SERVICE_UNAVAILABLE` | External service is temporarily unavailable |
| `INTERNAL_ERROR` | Internal server error occurred |

## HTTP Status Codes

| Status | Description |
|--------|-------------|
| 200 | OK - Request successful |
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Resource not found |
| 429 | Too Many Requests - Rate limited |
| 500 | Internal Server Error - Server error |

## Usage Examples

### cURL
```bash
# Search for songs
curl "https://api.example.com/search?q=coldplay&limit=5"

# Get audio URL
curl "https://api.example.com/audio/abc123"

# Get trending in US
curl "https://api.example.com/trending/US?limit=20"
```

### Python
```python
import requests

base_url = "https://api.example.com"

# Search songs
response = requests.get(f"{base_url}/search", params={"q": "coldplay", "limit": 5})
songs = response.json()["songs"]

# Get audio URL
audio_response = requests.get(f"{base_url}/audio/{songs[0]['id']}")
audio_url = audio_response.json()["audio_url"]
```

### JavaScript
```javascript
const baseUrl = 'https://api.example.com';

// Search songs
const searchResponse = await fetch(`${baseUrl}/search?q=coldplay&limit=5`);
const { songs } = await searchResponse.json();

// Get audio URL
const audioResponse = await fetch(`${baseUrl}/audio/${songs[0].id}`);
const { audio_url } = await audioResponse.json();
```

## SDKs and Libraries

### Official SDKs
- JavaScript/TypeScript SDK (coming soon)
- Python SDK (coming soon)

### Community SDKs
- React hooks library
- Vue.js composables
- Flutter package

## Changelog

### v1.0.0 (Latest)
- Initial release
- Search functionality
- Audio URL extraction
- Trending by country
- Homepage data
- Recommendations
- Health checks

## Support

- 📧 Email: support@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/Anshu78780/Song/issues)
- 💬 Discord: [Join our Discord](https://discord.gg/example)
- 📖 Documentation: [Full Documentation](https://docs.example.com)
