import yt_dlp
import logging
import os
import tempfile
from ytmusicapi import YTMusic

logger = logging.getLogger(__name__)

class MusicExtractor:
    """Class to handle music extraction and search using ytmusicapi and yt-dlp"""
    
    def __init__(self):
        # Initialize YTMusic API (no authentication needed for basic features)
        try:
            self.ytmusic = YTMusic()
            logger.info("YTMusic API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize YTMusic API: {str(e)}")
            self.ytmusic = None
        
        # yt-dlp configuration (only used for audio URL extraction)
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'no_warnings': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_color': True,
            # Add headers to avoid bot detection
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Accept-Encoding': 'gzip,deflate',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                'Keep-Alive': '300',
                'Connection': 'keep-alive',
            },
            # Additional options to bypass bot detection
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'hls'],
                    'player_skip': ['configs'],
                }
            },
            # Use cookies for authentication (for Render deployment)
            'cookiefile': None,  # Will be set dynamically if needed
            # Fallback options
            'sleep_interval': 1,
            'max_sleep_interval': 5,
            'sleep_interval_subtitles': 1,
        }
        
        # Set up cookies for YouTube authentication if available
        self._setup_cookies()
    
    def _setup_cookies(self):
        """Set up cookies for YouTube authentication to avoid bot detection"""
        try:
            # Get cookies from environment variable (for Render deployment)
            cookies_string = os.environ.get('YOUTUBE_COOKIES')
            
            if cookies_string:
                # Create a temporary cookie file
                temp_dir = tempfile.gettempdir()
                cookie_file = os.path.join(temp_dir, 'youtube_cookies.txt')
                
                # Write cookies in Netscape format
                with open(cookie_file, 'w') as f:
                    f.write("# Netscape HTTP Cookie File\n")
                    f.write("# This is a generated file! Do not edit.\n\n")
                    
                    # Parse the cookie string and convert to Netscape format
                    for cookie in cookies_string.split('; '):
                        if '=' in cookie:
                            name, value = cookie.split('=', 1)
                            # Write in Netscape format: domain, domain_specified, path, secure, expiration, name, value
                            f.write(f".youtube.com\tTRUE\t/\tFALSE\t0\t{name}\t{value}\n")
                
                # Update ydl_opts to use the cookie file
                self.ydl_opts['cookiefile'] = cookie_file
                logger.info("YouTube cookies loaded successfully")
            else:
                logger.info("No YouTube cookies found in environment variables")
                
        except Exception as e:
            logger.warning(f"Failed to set up cookies: {str(e)}")
    
    def search_songs(self, query, max_results=10):
        """Search for songs using ytmusicapi (fast metadata) and yt-dlp (audio URLs when needed)"""
        try:
            if not self.ytmusic:
                logger.warning("YTMusic API not available, falling back to yt-dlp")
                return self._search_songs_fallback(query, max_results)
            
            # Use YTMusic API for fast search
            search_results = self.ytmusic.search(query, filter="songs", limit=max_results)
            
            songs = []
            for result in search_results:
                song_info = self._convert_ytmusic_to_standard(result)
                songs.append(song_info)
            
            return songs
                
        except Exception as e:
            logger.error(f"Error searching songs with YTMusic: {str(e)}")
            # Fallback to yt-dlp if ytmusicapi fails
            return self._search_songs_fallback(query, max_results)
    
    def _search_songs_fallback(self, query, max_results=10):
        """Fallback search using yt-dlp when ytmusicapi is unavailable"""
        try:
            search_query = f"ytsearch{max_results}:{query}"
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                search_results = ydl.extract_info(search_query, download=False)
                
                if not search_results or 'entries' not in search_results:
                    return []
                
                songs = []
                for entry in search_results['entries']:
                    if entry:
                        song_info = self.extract_song_metadata(entry)
                        songs.append(song_info)
                
                return songs
                
        except Exception as e:
            logger.error(f"Error in fallback search: {str(e)}")
            return []
    
    def _convert_ytmusic_to_standard(self, ytmusic_result):
        """Convert YTMusic API result to standard format"""
        try:
            # Extract basic info from YTMusic result
            video_id = ytmusic_result.get('videoId')
            title = ytmusic_result.get('title', 'Unknown Title')
            
            # Get artist info
            artists = ytmusic_result.get('artists', [])
            artist = artists[0].get('name') if artists else 'Unknown Artist'
            
            # Get album info
            album = ytmusic_result.get('album', {})
            album_name = album.get('name') if album else None
            
            # Get duration
            duration_text = ytmusic_result.get('duration_seconds')
            duration = int(duration_text) if duration_text else None
            
            # Get thumbnail
            thumbnails = ytmusic_result.get('thumbnails', [])
            thumbnail = thumbnails[-1]['url'] if thumbnails else None
            
            return {
                'id': video_id,
                'title': title,
                'artist': artist,
                'album': album_name,
                'duration': duration,
                'duration_string': self.format_duration(duration),
                'thumbnail': thumbnail,
                'poster_image': thumbnail,
                'audio_url': None,  # Will be loaded on demand
                'webpage_url': f"https://www.youtube.com/watch?v={video_id}",
                'view_count': None,  # Not available in YTMusic API
                'like_count': None,  # Not available in YTMusic API
                'uploader': artist,
                'upload_date': None,  # Not available in YTMusic API
                'description': '',
                'extractor': 'ytmusic',
                'availability': 'public',
                'live_status': 'not_live',
                'source': 'ytmusicapi'  # Indicate this came from fast API
            }
        except Exception as e:
            logger.error(f"Error converting YTMusic result: {str(e)}")
            return None
    
    def _extract_playlist_id_from_url(self, url):
        """Extract playlist ID from YouTube URL"""
        try:
            import re
            # Match YouTube playlist URL format
            pattern = r'(?:youtube\.com|music\.youtube\.com)/playlist\?list=([a-zA-Z0-9_-]+)'
            match = re.search(pattern, url)
            if match:
                return match.group(1)
            
            # Match playlist ID directly
            if re.match(r'^[a-zA-Z0-9_-]+$', url) and len(url) > 11:  # Most video IDs are 11 chars
                return url
                
            return None
        except Exception as e:
            logger.warning(f"Could not extract playlist ID from URL {url}: {str(e)}")
            return None
    
    def get_audio_url(self, video_id):
        """Get audio URL for a specific video ID using yt-dlp"""
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Try with enhanced configuration first
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Get the best audio format
                audio_url = None
                if 'url' in info:
                    audio_url = info['url']
                elif 'formats' in info:
                    # Find the best audio format
                    audio_formats = [f for f in info['formats'] if f.get('acodec') != 'none']
                    if audio_formats:
                        # Sort by quality and get the best one
                        audio_formats.sort(key=lambda x: x.get('quality', 0) or 0, reverse=True)
                        audio_url = audio_formats[0]['url']
                
                return audio_url
                
        except Exception as e:
            logger.error(f"Error getting audio URL for {video_id}: {str(e)}")
            
            # Try fallback method if bot detection occurs
            if "Sign in to confirm" in str(e) or "bot" in str(e).lower():
                return self._get_audio_url_fallback(video_id)
                
            return None
    
    def _get_audio_url_fallback(self, video_id):
        """Fallback method for audio URL extraction when bot detection occurs"""
        try:
            logger.info(f"Attempting fallback audio extraction for {video_id}...")
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Try with very minimal options
            fallback_opts = {
                'quiet': True,
                'no_warnings': True,
                'format': 'worstaudio/worst',  # Use worst quality to avoid suspicion
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5'
                }
            }
            
            with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if 'url' in info:
                    return info['url']
                elif 'formats' in info:
                    # Get any working format
                    for format_item in info['formats']:
                        if format_item.get('url'):
                            return format_item['url']
                    
        except Exception as e:
            logger.error(f"Fallback audio extraction also failed for {video_id}: {str(e)}")
            
        return None
    
    def format_duration(self, duration):
        """Format duration from seconds to MM:SS or HH:MM:SS"""
        if not duration:
            return "Unknown"
        
        try:
            duration = int(duration)
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            seconds = duration % 60
            
            if hours > 0:
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes:02d}:{seconds:02d}"
        except (ValueError, TypeError):
            return "Unknown"
    
    def get_playlist_info(self, playlist_url, max_results=50):
        """Extract songs from a playlist using yt-dlp"""
        try:
            ydl_opts = self.ydl_opts.copy()
            ydl_opts['playlistend'] = max_results
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlist_info = ydl.extract_info(playlist_url, download=False)
                
                if not playlist_info or 'entries' not in playlist_info:
                    return None
                
                songs = []
                for entry in playlist_info['entries']:
                    if entry:
                        song_info = self.extract_song_metadata(entry)
                        songs.append(song_info)
                
                return {
                    'title': playlist_info.get('title', 'Unknown Playlist'),
                    'id': playlist_info.get('id'),
                    'uploader': playlist_info.get('uploader'),
                    'description': playlist_info.get('description', ''),
                    'entry_count': len(songs),
                    'songs': songs
                }
                
        except Exception as e:
            logger.error(f"Error getting playlist info: {str(e)}")
            return None
            
    def get_ytmusic_playlist(self, playlist_id, max_results=50):
        """Get playlist information using ytmusicapi"""
        try:
            if not self.ytmusic:
                logger.warning("YTMusic API not available, falling back to yt-dlp")
                playlist_url = f"https://music.youtube.com/playlist?list={playlist_id}"
                return self.get_playlist_info(playlist_url, max_results)
            
            # Get playlist information from YTMusic API
            playlist_data = self.ytmusic.get_playlist(playlist_id, max_results)
            
            if not playlist_data or 'tracks' not in playlist_data:
                logger.warning(f"No playlist data found for ID: {playlist_id}")
                return None
            
            # Process tracks
            songs = []
            for track in playlist_data.get('tracks', [])[:max_results]:
                song_info = self._convert_ytmusic_to_standard(track)
                if song_info:
                    songs.append(song_info)
            
            # Return formatted playlist information
            return {
                'title': playlist_data.get('title', 'Unknown Playlist'),
                'id': playlist_id,
                'uploader': playlist_data.get('author', {}).get('name', 'Unknown'),
                'description': playlist_data.get('description', ''),
                'thumbnail': playlist_data.get('thumbnails', [{}])[-1].get('url') if playlist_data.get('thumbnails') else None,
                'year': playlist_data.get('year'),
                'total_tracks': playlist_data.get('trackCount', len(songs)),
                'entry_count': len(songs),
                'songs': songs,
                'source': 'ytmusicapi'
            }
                
        except Exception as e:
            logger.error(f"Error getting playlist info with YTMusic API: {str(e)}")
            # Fallback to traditional method if YTMusic API fails
            playlist_url = f"https://music.youtube.com/playlist?list={playlist_id}"
            return self.get_playlist_info(playlist_url, max_results)
            
    def get_trending_by_country(self, country_code='US', max_results=50):
        """Get trending playlists by country using ytmusicapi"""
        try:
            if not self.ytmusic:
                logger.warning("YTMusic API not available, cannot fetch trending playlists")
                return None
            
            # Get the home page data which includes trending playlists
            home_data = self.ytmusic.get_home(limit=100)  # Get more data
            
            if not home_data:
                logger.warning("No home data available")
                return None
            
            # Extract playlists from home data
            trending_playlists = []
            
            # Process each section in home data
            for section in home_data:
                if isinstance(section, dict) and 'contents' in section:
                    section_title = section.get('title', 'Unknown Section')
                    contents = section.get('contents', [])
                    
                    # Process each item in the section
                    for item in contents:
                        if item and isinstance(item, dict) and 'playlistId' in item:
                            playlist_info = {
                                'title': item.get('title', 'Unknown Playlist'),
                                'playlistId': item.get('playlistId'),
                                'thumbnail': item.get('thumbnails', [{}])[-1].get('url') if item.get('thumbnails') else None,
                                'description': item.get('description', ''),
                                'section': section_title,
                                'url': f"https://music.youtube.com/playlist?list={item.get('playlistId')}" if item.get('playlistId') else None
                            }
                            trending_playlists.append(playlist_info)
                            
                            if len(trending_playlists) >= max_results:
                                break
                
                if len(trending_playlists) >= max_results:
                    break
            
            # If we still don't have enough playlists, try search method
            if len(trending_playlists) < 20:
                try:
                    # Search for popular playlist terms
                    search_terms = [
                        'hindi hits', 'bollywood hits', 'punjabi hits', 'tamil hits',
                        'trending songs', 'top hits', 'viral songs', 'chart toppers',
                        'latest songs', 'popular music'
                    ]
                    
                    for search_term in search_terms:
                        if len(trending_playlists) >= max_results:
                            break
                            
                        try:
                            search_results = self.ytmusic.search(search_term, filter='playlists', limit=10)
                            
                            for result in search_results:
                                if result and isinstance(result, dict):
                                    # For search results, we need to construct playlist info differently
                                    playlist_info = {
                                        'title': result.get('title', 'Unknown Playlist'),
                                        'playlistId': result.get('browseId', '').replace('VL', '') if result.get('browseId', '').startswith('VL') else result.get('browseId'),
                                        'thumbnail': result.get('thumbnails', [{}])[-1].get('url') if result.get('thumbnails') else None,
                                        'description': result.get('description', ''),
                                        'author': result.get('author', 'Unknown'),
                                        'videoCount': result.get('count'),
                                        'section': f'Search: {search_term}',
                                        'url': f"https://music.youtube.com/playlist?list={result.get('browseId', '').replace('VL', '') if result.get('browseId', '').startswith('VL') else result.get('browseId')}" if result.get('browseId') else None
                                    }
                                    
                                    # Only add if we have a valid playlist ID
                                    if playlist_info['playlistId']:
                                        trending_playlists.append(playlist_info)
                                        
                                        if len(trending_playlists) >= max_results:
                                            break
                        except Exception as search_error:
                            logger.warning(f"Error searching for '{search_term}': {str(search_error)}")
                            continue
                            
                except Exception as search_error:
                    logger.warning(f"Error in playlist search fallback: {str(search_error)}")
            
            # Structure to hold playlist data
            result = {
                'country': country_code,
                'trending_playlists': trending_playlists[:max_results],
                'total_playlists': len(trending_playlists),
                'source': 'ytmusicapi'
            }
            
            logger.info(f"Found {len(trending_playlists)} playlists for country {country_code}")
            
            return result
                
        except Exception as e:
            logger.error(f"Error getting trending playlists: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def get_recommended_songs(self, video_id, max_results=50):
        """Get recommended songs for a specific video using ytmusicapi"""
        try:
            if not self.ytmusic:
                logger.warning("YTMusic API not available, cannot fetch recommendations")
                return None
            
            # Get the recommended songs (watch next) for a specific video
            recommended_data = self.ytmusic.get_watch_playlist(videoId=video_id, limit=max_results)
            
            if not recommended_data or 'tracks' not in recommended_data:
                logger.warning(f"No recommendations found for video ID: {video_id}")
                return None
            
            # Process recommended tracks
            recommendations = []
            for track in recommended_data.get('tracks', [])[:max_results]:
                song_info = self._convert_ytmusic_to_standard(track)
                if song_info:
                    recommendations.append(song_info)
            
            # Return formatted recommendations
            return {
                'video_id': video_id,
                'recommendations_count': len(recommendations),
                'recommendations': recommendations,
                'source': 'ytmusicapi'
            }
                
        except Exception as e:
            logger.error(f"Error getting recommendations for video ID {video_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def get_youtube_homepage_data(self, max_results=20):
        """Get YouTube homepage trending/popular videos using ytmusicapi for speed"""
        try:
            if not self.ytmusic:
                logger.warning("YTMusic API not available, falling back to yt-dlp")
                return self._get_homepage_data_fallback(max_results)
            
            # Get trending and popular content from YTMusic
            homepage_data = {
                'trending_music': [],
                'categories': ['trending', 'charts', 'new_releases'],
                'last_updated': 'now',
                'total_results': 0
            }
            
            try:
                # Get charts (trending music)
                charts = self.ytmusic.get_charts()
                if charts and 'countries' in charts:
                    # Get the first country's top songs
                    country_data = charts['countries']['US'] if 'US' in charts['countries'] else list(charts['countries'].values())[0]
                    if 'songs' in country_data:
                        chart_songs = country_data['songs']['playlist']
                        for song in chart_songs[:max_results//2]:
                            converted_song = self._convert_ytmusic_to_standard(song)
                            if converted_song:
                                converted_song['category'] = 'trending'
                                homepage_data['trending_music'].append(converted_song)
            except Exception as e:
                logger.warning(f"Error getting charts: {str(e)}")
            
            try:
                # Get new releases if we don't have enough content
                if len(homepage_data['trending_music']) < max_results:
                    remaining = max_results - len(homepage_data['trending_music'])
                    new_releases = self.ytmusic.get_home()
                    
                    for section in new_releases[:3]:  # Get from first 3 sections
                        if 'contents' in section:
                            for item in section['contents'][:remaining//3]:
                                if item.get('videoId'):  # Only songs with video IDs
                                    converted_song = self._convert_ytmusic_to_standard(item)
                                    if converted_song:
                                        converted_song['category'] = 'new_releases'
                                        homepage_data['trending_music'].append(converted_song)
                                        if len(homepage_data['trending_music']) >= max_results:
                                            break
                        if len(homepage_data['trending_music']) >= max_results:
                            break
            except Exception as e:
                logger.warning(f"Error getting new releases: {str(e)}")
            
            # If still don't have enough, search for popular music
            if len(homepage_data['trending_music']) < max_results:
                try:
                    remaining = max_results - len(homepage_data['trending_music'])
                    popular_search = self.ytmusic.search("popular songs 2024", filter="songs", limit=remaining)
                    for song in popular_search:
                        converted_song = self._convert_ytmusic_to_standard(song)
                        if converted_song:
                            converted_song['category'] = 'popular'
                            homepage_data['trending_music'].append(converted_song)
                except Exception as e:
                    logger.warning(f"Error searching popular songs: {str(e)}")
            
            homepage_data['total_results'] = len(homepage_data['trending_music'])
            return homepage_data
            
        except Exception as e:
            logger.error(f"Error getting YouTube homepage data with YTMusic: {str(e)}")
            return self._get_homepage_data_fallback(max_results)
    
    def _get_homepage_data_fallback(self, max_results=20):
        """Fallback method using yt-dlp when ytmusicapi is unavailable"""
        try:
            # Fallback: Get popular music videos using searches
            popular_searches = [
                "trending music 2024",
                "popular songs",
                "top hits",
                "music charts"
            ]
            
            all_videos = []
            videos_per_search = max_results // len(popular_searches)
            
            for search_term in popular_searches:
                try:
                    search_query = f"ytsearch{videos_per_search}:{search_term}"
                    
                    with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                        search_results = ydl.extract_info(search_query, download=False)
                        
                        if search_results and 'entries' in search_results:
                            for entry in search_results['entries']:
                                if entry and len(all_videos) < max_results:
                                    video_info = self.extract_song_metadata(entry)
                                    # Add category information
                                    video_info['category'] = search_term.replace(' ', '_')
                                    all_videos.append(video_info)
                except Exception as e:
                    logger.warning(f"Error searching for {search_term}: {str(e)}")
                    continue
            
            # Remove duplicates based on video ID
            seen_ids = set()
            unique_videos = []
            for video in all_videos:
                if video['id'] not in seen_ids:
                    seen_ids.add(video['id'])
                    unique_videos.append(video)
            
            return {
                'trending_music': unique_videos[:max_results],
                'categories': ['trending', 'popular', 'top_hits', 'music_charts'],
                'last_updated': 'now',
                'total_results': len(unique_videos)
            }
            
        except Exception as e:
            logger.error(f"Error in fallback homepage data: {str(e)}")
            return None
