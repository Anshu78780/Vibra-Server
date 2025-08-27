from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
from datetime import datetime
from config import Config
from music_extractor import MusicExtractor

# Load environment variables from .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, skip loading .env file
    pass

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, origins=Config.CORS_ORIGINS)

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Initialize the music extractor
music_extractor = MusicExtractor()

@app.route('/')
def home():
    """Home endpoint with API information"""
    return jsonify({
        'message': 'Music Backend API',
        'version': '1.0.0',
        'endpoints': {
            '/search': 'Search for songs (GET) - ?q=query&limit=10',
            '/song/<song_id>': 'Get specific song details (GET)',
            '/audio/<video_id>': 'Get audio URL for video ID (GET)',
            '/extract': 'Extract song from URL (POST)',
            '/playlist': 'Extract songs from playlist (POST)',
            '/homepage': 'Get YouTube homepage/trending data (GET) - ?limit=20',
            '/category/<category>': 'Get videos by category (GET) - ?limit=20',
            '/health': 'Health check (GET)'
        },
        'example_usage': {
            'search': '/search?q=imagine%20dragons&limit=5',
            'song': '/song/dQw4w9WgXcQ',
            'audio': '/audio/dQw4w9WgXcQ',
            'extract': 'POST /extract with {"url": "https://youtube.com/watch?v=..."}',
            'playlist': 'POST /playlist with {"url": "https://youtube.com/playlist?list=..."}',
            'homepage': '/homepage?limit=20',
            'category': '/category/pop?limit=15'
        },
        'performance_note': 'Search and homepage endpoints use YTMusic API for fast metadata. Use /audio/<video_id> to get playable URLs on demand.'
    })

@app.route('/search', methods=['GET'])
def search_songs():
    """Search for songs endpoint"""
    query = request.args.get('q', '').strip()
    max_results = request.args.get('limit', Config.DEFAULT_SEARCH_RESULTS, type=int)
    
    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400
    
    if max_results > Config.MAX_SEARCH_RESULTS:
        max_results = Config.MAX_SEARCH_RESULTS  # Limit to prevent abuse
    
    try:
        songs = music_extractor.search_songs(query, max_results)
        return jsonify({
            'success': True,
            'query': query,
            'results_count': len(songs),
            'songs': songs
        })
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({'error': 'Internal server error during search'}), 500

@app.route('/song/<song_id>', methods=['GET'])
def get_song(song_id):
    """Get specific song details by ID"""
    try:
        # Construct YouTube URL from ID
        url = f"https://www.youtube.com/watch?v={song_id}"
        song_details = music_extractor.get_song_details(url)
        
        if song_details:
            return jsonify({
                'success': True,
                'song': song_details
            })
        else:
            return jsonify({'error': 'Song not found'}), 404
            
    except Exception as e:
        logger.error(f"Get song error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/audio/<video_id>', methods=['GET'])
def get_audio_url(video_id):
    """Get audio URL for a specific video ID"""
    try:
        audio_url = music_extractor.get_audio_url(video_id)
        
        if audio_url:
            return jsonify({
                'success': True,
                'video_id': video_id,
                'audio_url': audio_url,
                'message': 'Audio URL retrieved successfully'
            })
        else:
            return jsonify({'error': 'Could not get audio URL for this video'}), 404
            
    except Exception as e:
        logger.error(f"Get audio URL error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/extract', methods=['POST'])
def extract_from_url():
    """Extract song details from a given URL"""
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required in request body'}), 400
    
    url = data['url'].strip()
    
    if not url:
        return jsonify({'error': 'URL cannot be empty'}), 400
    
    try:
        song_details = music_extractor.get_song_details(url)
        
        if song_details:
            return jsonify({
                'success': True,
                'song': song_details
            })
        else:
            return jsonify({'error': 'Could not extract song details from URL'}), 400
            
    except Exception as e:
        logger.error(f"Extract error: {str(e)}")
        return jsonify({'error': 'Internal server error during extraction'}), 500

@app.route('/playlist', methods=['POST'])
def get_playlist():
    """Extract songs from a playlist"""
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'error': 'Playlist URL is required in request body'}), 400
    
    url = data['url'].strip()
    max_results = data.get('limit', 50)
    
    if not url:
        return jsonify({'error': 'URL cannot be empty'}), 400
    
    if max_results > Config.MAX_SEARCH_RESULTS:
        max_results = Config.MAX_SEARCH_RESULTS
    
    try:
        playlist_info = music_extractor.get_playlist_info(url, max_results)
        
        if playlist_info:
            return jsonify({
                'success': True,
                'playlist': playlist_info
            })
        else:
            return jsonify({'error': 'Could not extract playlist information'}), 400
            
    except Exception as e:
        logger.error(f"Playlist extraction error: {str(e)}")
        return jsonify({'error': 'Internal server error during playlist extraction'}), 500

@app.route('/homepage', methods=['GET'])
def get_homepage_data():
    """Get YouTube homepage/trending data"""
    max_results = request.args.get('limit', 20, type=int)
    
    if max_results > Config.MAX_SEARCH_RESULTS:
        max_results = Config.MAX_SEARCH_RESULTS
    
    try:
        homepage_data = music_extractor.get_youtube_homepage_data(max_results)
        
        if homepage_data:
            return jsonify({
                'success': True,
                'data': homepage_data,
                'message': 'YouTube homepage data retrieved successfully'
            })
        else:
            return jsonify({'error': 'Could not retrieve homepage data'}), 500
            
    except Exception as e:
        logger.error(f"Homepage data error: {str(e)}")
        return jsonify({'error': 'Internal server error while fetching homepage data'}), 500

@app.route('/category/<category>', methods=['GET'])
def get_category_data(category):
    """Get videos by category"""
    max_results = request.args.get('limit', 20, type=int)
    
    if max_results > Config.MAX_SEARCH_RESULTS:
        max_results = Config.MAX_SEARCH_RESULTS
    
    try:
        category_videos = music_extractor.get_category_videos(category, max_results)
        
        return jsonify({
            'success': True,
            'category': category,
            'results_count': len(category_videos),
            'videos': category_videos
        })
            
    except Exception as e:
        logger.error(f"Category data error: {str(e)}")
        return jsonify({'error': 'Internal server error while fetching category data'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with system status"""
    try:
        # Test YTMusic API
        ytmusic_status = "OK" if music_extractor.ytmusic else "Unavailable"
        
        # Test basic functionality
        test_search = music_extractor.search_songs("test", 1)
        search_status = "OK" if test_search else "Error"
        
        return jsonify({
            'status': 'healthy',
            'timestamp': str(datetime.now()),
            'services': {
                'ytmusic_api': ytmusic_status,
                'search_function': search_status,
                'yt_dlp': 'OK'  # Always available if imported
            },
            'version': '1.0.0',
            'environment': 'production' if not Config.DEBUG else 'development'
        })
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': str(datetime.now()),
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
