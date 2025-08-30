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
            '/audio/<video_id>': 'Get audio URL for video ID (GET)',
            '/recommended/<video_id>': 'Get recommended songs for a video ID (GET) - ?limit=50',
            '/trending/<country_code>': 'Get trending playlists by country code (GET) - ?limit=50',
            '/homepage': 'Get YouTube homepage/trending data (GET) - ?limit=20',
            '/health': 'Health check (GET)'
        },
        'example_usage': {
            'search': '/search?q=imagine%20dragons&limit=5',
            'audio': '/audio/dQw4w9WgXcQ',
            'playlist_id': '/playlist/PLiJ19Xxebz3nkJ7Rg1vgHzu-nSLmSig7t?limit=20',
            'recommended': '/recommended/dQw4w9WgXcQ?limit=20',
            'trending': '/trending/IN?limit=50 (country codes: US, IN, GB, etc.)',
            'homepage': '/homepage?limit=20'
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

@app.route('/playlist/<playlist_id>', methods=['GET'])
def get_ytmusic_playlist(playlist_id):
    """Get playlist details by ID using YTMusic API"""
    max_results = request.args.get('limit', 50, type=int)
    
    if max_results > Config.MAX_SEARCH_RESULTS:
        max_results = Config.MAX_SEARCH_RESULTS
    
    try:
        # Check if the input is a URL and extract playlist ID if so
        if playlist_id.startswith('http'):
            extracted_id = music_extractor._extract_playlist_id_from_url(playlist_id)
            if not extracted_id:
                return jsonify({'error': 'Invalid playlist URL'}), 400
            playlist_id = extracted_id
        
        # Get playlist data using YTMusic API
        playlist_info = music_extractor.get_ytmusic_playlist(playlist_id, max_results)
        
        if playlist_info:
            return jsonify({
                'success': True,
                'playlist': playlist_info
            })
        else:
            return jsonify({'error': 'Could not extract playlist information'}), 400
            
    except Exception as e:
        logger.error(f"YTMusic playlist extraction error: {str(e)}")
        return jsonify({'error': 'Internal server error during playlist extraction'}), 500

@app.route('/trending/<country_code>', methods=['GET'])
def get_trending_by_country(country_code):
    """Get trending playlists by country code using YTMusic API"""
    max_results = request.args.get('limit', 50, type=int)
    
    if max_results > Config.MAX_SEARCH_RESULTS:
        max_results = Config.MAX_SEARCH_RESULTS
    
    # Convert to uppercase
    country_code = country_code.upper()
    
    try:
        # Get trending playlists by country
        trending_data = music_extractor.get_trending_by_country(country_code, max_results)
        
        if trending_data and trending_data.get('trending_playlists'):
            return jsonify({
                'success': True,
                'country': country_code,
                'total_playlists': trending_data.get('total_playlists', 0),
                'playlists': trending_data.get('trending_playlists', []),
                'message': f'Found {len(trending_data.get("trending_playlists", []))} trending playlists'
            })
        else:
            # Provide a helpful message if no playlists are returned
            return jsonify({
                'success': False,
                'error': f'Could not fetch trending playlists for country code: {country_code}',
                'message': 'No playlists found. This might be due to regional restrictions or API limitations.'
            }), 400
            
    except Exception as e:
        logger.error(f"YTMusic trending extraction error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error during trending data extraction',
            'message': 'Try using a different country code or try again later.'
        }), 500

@app.route('/recommended/<video_id>', methods=['GET'])
def get_recommended_songs(video_id):
    """Get recommended songs for a specific video ID using YTMusic API"""
    max_results = request.args.get('limit', 50, type=int)
    
    if max_results > Config.MAX_SEARCH_RESULTS:
        max_results = Config.MAX_SEARCH_RESULTS
    
    try:
        # Get recommended songs using YTMusic API
        recommended_data = music_extractor.get_recommended_songs(video_id, max_results)
        
        if recommended_data:
            return jsonify({
                'success': True,
                'recommendations': recommended_data
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Could not fetch recommendations for video ID: {video_id}',
                'message': 'Ensure you are providing a valid YouTube video ID'
            }), 400
            
    except Exception as e:
        logger.error(f"YTMusic recommendations error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error while fetching recommendations',
            'message': 'Try again later or check if the video ID is valid'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
