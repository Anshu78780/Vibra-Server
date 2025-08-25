# Music Backend API

A Flask-based backend service for a music app that provides song search, metadata extraction, and playable URLs using yt-dlp.

## Features

- **Song Search**: Search for songs with customizable result limits
- **Metadata Extraction**: Get detailed song information including title, artist, duration, thumbnails
- **Playable URLs**: Extract direct audio URLs for streaming
- **Poster Images**: Get high-quality thumbnail/poster images
- **Playlist Support**: Extract songs from playlists
- **YouTube Integration**: Powered by yt-dlp for reliable extraction

## Installation

1. Clone or download this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Server

```bash
python app.py
```

The server will start on `http://localhost:5000` by default.

### API Endpoints

#### 1. Search Songs
**GET** `/search`

Search for songs using a query string.

**Parameters:**
- `q` (required): Search query
- `limit` (optional): Number of results (default: 10, max: 50)

**Example:**
```
GET /search?q=imagine%20dragons&limit=5
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
      "title": "Imagine Dragons - Thunder",
      "artist": "Imagine Dragons",
      "duration": 187,
      "duration_string": "03:07",
      "thumbnail": "https://i.ytimg.com/vi/ktvTqknDobU/maxresdefault.jpg",
      "poster_image": "https://i.ytimg.com/vi/ktvTqknDobU/maxresdefault.jpg",
      "audio_url": "https://...",
      "webpage_url": "https://www.youtube.com/watch?v=ktvTqknDobU",
      "view_count": 1234567890,
      "like_count": 12345678,
      "uploader": "ImagineDragonsVEVO",
      "upload_date": "20170504",
      "description": "Official music video for Thunder..."
    }
  ]
}
```

#### 2. Get Song Details
**GET** `/song/<song_id>`

Get detailed information about a specific song using its YouTube ID.

**Example:**
```
GET /song/ktvTqknDobU
```

#### 3. Extract from URL
**POST** `/extract`

Extract song details from a YouTube URL.

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=ktvTqknDobU"
}
```

#### 4. Extract Playlist
**POST** `/playlist`

Extract songs from a YouTube playlist.

**Request Body:**
```json
{
  "url": "https://www.youtube.com/playlist?list=PLrALmylex6Y...",
  "limit": 20
}
```

#### 5. Get YouTube Homepage Data
**GET** `/homepage`

Get YouTube homepage/trending music data.

**Parameters:**
- `limit` (optional): Number of results (default: 20, max: 50)

**Example:**
```
GET /homepage?limit=15
```

**Response:**
```json
{
  "success": true,
  "data": {
    "trending_music": [
      {
        "id": "ktvTqknDobU",
        "title": "Trending Song Title",
        "artist": "Artist Name",
        "duration": 187,
        "duration_string": "03:07",
        "thumbnail": "https://i.ytimg.com/vi/ktvTqknDobU/maxresdefault.jpg",
        "audio_url": "https://...",
        "category": "trending"
      }
    ],
    "categories": ["trending", "popular", "top_hits"],
    "last_updated": "now",
    "total_results": 15
  },
  "message": "YouTube homepage data retrieved successfully"
}
```

#### 6. Get Category Videos
**GET** `/category/<category>`

Get videos by music category.

**Parameters:**
- `limit` (optional): Number of results (default: 20, max: 50)

**Available Categories:**
- `music` - General music videos
- `pop` - Pop music hits
- `rock` - Rock music songs
- `hip_hop` - Hip hop/rap music
- `electronic` - Electronic/dance music
- `indie` - Indie/alternative music
- `classical` - Classical music
- `jazz` - Jazz music
- `country` - Country music
- `r&b` - R&B/soul music

**Example:**
```
GET /category/pop?limit=10
```

**Response:**
```json
{
  "success": true,
  "category": "pop",
  "results_count": 10,
  "videos": [
    {
      "id": "abc123",
      "title": "Pop Song Title",
      "artist": "Pop Artist",
      "category": "pop",
      "duration": 200,
      "duration_string": "03:20",
      "thumbnail": "https://...",
      "audio_url": "https://..."
    }
  ]
}
```

#### 7. Health Check
**GET** `/health`

Check if the server is running.

## Configuration

You can configure the server using environment variables:

- `FLASK_DEBUG`: Enable/disable debug mode (default: True)
- `FLASK_HOST`: Server host (default: 0.0.0.0)
- `FLASK_PORT`: Server port (default: 5000)
- `CORS_ORIGINS`: Allowed CORS origins (default: *)
- `LOG_LEVEL`: Logging level (default: INFO)

## Response Format

All endpoints return JSON responses with the following structure:

**Success Response:**
```json
{
  "success": true,
  "data": {...}
}
```

**Error Response:**
```json
{
  "error": "Error description"
}
```

## Song Metadata Structure

Each song object contains:

- `id`: YouTube video ID
- `title`: Song title
- `artist`: Artist name
- `duration`: Duration in seconds
- `duration_string`: Formatted duration (MM:SS or HH:MM:SS)
- `thumbnail`: Thumbnail URL
- `poster_image`: Same as thumbnail (for compatibility)
- `audio_url`: Direct audio stream URL
- `webpage_url`: Original YouTube URL
- `view_count`: Number of views
- `like_count`: Number of likes
- `uploader`: Channel name
- `upload_date`: Upload date (YYYYMMDD)
- `description`: Video description (truncated to 500 chars)

## Frontend Integration

This backend is designed to work with music player frontends. The `audio_url` field provides direct streaming URLs that can be used with HTML5 audio elements or media libraries.

**Example Frontend Usage:**
```javascript
// Search for songs
const response = await fetch('/search?q=favorite%20song&limit=10');
const data = await response.json();

// Get homepage/trending data
const homepageResponse = await fetch('/homepage?limit=20');
const homepageData = await homepageResponse.json();

// Get pop music videos
const categoryResponse = await fetch('/category/pop?limit=15');
const categoryData = await categoryResponse.json();

// Play a song
const audio = new Audio(data.songs[0].audio_url);
audio.play();
```

## Error Handling

The API includes comprehensive error handling:

- Input validation
- Rate limiting (max 50 results per request)
- Graceful degradation for unavailable content
- Detailed error logging

## Dependencies

- Flask: Web framework
- flask-cors: CORS support
- yt-dlp: YouTube extraction
- requests: HTTP requests

## Notes

- This server is intended for personal/educational use
- Respect YouTube's terms of service
- Audio URLs may expire and need to be refreshed
- Some content may not be available due to geographic restrictions
