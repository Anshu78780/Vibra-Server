import yt_dlp
import logging
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
        }
    
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
    
    def get_song_details(self, url):
        """Get detailed information about a specific song"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return self.extract_song_metadata(info)
                
        except Exception as e:
            logger.error(f"Error getting song details: {str(e)}")
            return None
    
    def get_audio_url(self, video_id):
        """Get audio URL for a specific video ID using yt-dlp"""
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            
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
            return None
    
    def extract_song_metadata(self, entry):
        """Extract relevant metadata from yt-dlp entry"""
        # Get the best audio format
        audio_url = None
        if 'url' in entry:
            audio_url = entry['url']
        elif 'formats' in entry:
            # Find the best audio format
            audio_formats = [f for f in entry['formats'] if f.get('acodec') != 'none']
            if audio_formats:
                # Sort by quality and get the best one
                audio_formats.sort(key=lambda x: x.get('quality', 0) or 0, reverse=True)
                audio_url = audio_formats[0]['url']
        
        # Extract artist and title from title
        title = entry.get('title', 'Unknown Title')
        artist = entry.get('uploader', 'Unknown Artist')
        
        # Try to parse artist and title from title field
        if ' - ' in title:
            parts = title.split(' - ', 1)
            artist = parts[0].strip()
            title = parts[1].strip()
        elif 'by' in title.lower():
            # Handle cases like "Song Title by Artist"
            parts = title.lower().split(' by ')
            if len(parts) == 2:
                title = parts[0].strip().title()
                artist = parts[1].strip().title()
        
        # Get thumbnail/poster image
        thumbnail = entry.get('thumbnail')
        if not thumbnail and 'thumbnails' in entry and entry['thumbnails']:
            # Get the highest quality thumbnail
            thumbnails = entry['thumbnails']
            # Sort by resolution and get the best one
            thumbnails.sort(key=lambda x: (x.get('width', 0) or 0) * (x.get('height', 0) or 0), reverse=True)
            thumbnail = thumbnails[0]['url'] if thumbnails else None
        
        return {
            'id': entry.get('id'),
            'title': title,
            'artist': artist,
            'duration': entry.get('duration'),
            'duration_string': self.format_duration(entry.get('duration')),
            'thumbnail': thumbnail,
            'poster_image': thumbnail,  # Same as thumbnail for compatibility
            'audio_url': audio_url,
            'webpage_url': entry.get('webpage_url'),
            'view_count': entry.get('view_count'),
            'like_count': entry.get('like_count'),
            'uploader': entry.get('uploader'),
            'upload_date': entry.get('upload_date'),
            'description': entry.get('description', '')[:500] if entry.get('description') else '',  # Truncate description
            'extractor': entry.get('extractor', 'youtube'),
            'availability': entry.get('availability'),
            'live_status': entry.get('live_status'),
        }
    
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
        """Extract songs from a playlist"""
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
    
    def get_category_videos(self, category="music", max_results=20):
        """Get videos by category using ytmusicapi for speed"""
        try:
            if not self.ytmusic:
                logger.warning("YTMusic API not available, falling back to yt-dlp")
                return self._get_category_videos_fallback(category, max_results)
            
            # Map categories to YTMusic search terms
            category_queries = {
                'music': 'music',
                'pop': 'pop music',
                'rock': 'rock music',
                'hip_hop': 'hip hop',
                'electronic': 'electronic music',
                'indie': 'indie music',
                'classical': 'classical music',
                'jazz': 'jazz music',
                'country': 'country music',
                'r&b': 'r&b music'
            }
            
            query = category_queries.get(category.lower(), f"{category} music")
            
            # Use YTMusic search for fast results
            search_results = self.ytmusic.search(query, filter="songs", limit=max_results)
            
            videos = []
            for result in search_results:
                video_info = self._convert_ytmusic_to_standard(result)
                if video_info:
                    video_info['category'] = category
                    videos.append(video_info)
            
            return videos
            
        except Exception as e:
            logger.error(f"Error getting category videos with YTMusic: {str(e)}")
            return self._get_category_videos_fallback(category, max_results)
    
    def _get_category_videos_fallback(self, category="music", max_results=20):
        """Fallback method using yt-dlp for category videos"""
        try:
            category_queries = {
                'music': 'latest music videos',
                'pop': 'pop music hits',
                'rock': 'rock music songs',
                'hip_hop': 'hip hop rap music',
                'electronic': 'electronic dance music',
                'indie': 'indie alternative music',
                'classical': 'classical music',
                'jazz': 'jazz music',
                'country': 'country music',
                'r&b': 'r&b soul music'
            }
            
            query = category_queries.get(category.lower(), f"{category} music")
            search_query = f"ytsearch{max_results}:{query}"
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                search_results = ydl.extract_info(search_query, download=False)
                
                if not search_results or 'entries' not in search_results:
                    return []
                
                videos = []
                for entry in search_results['entries']:
                    if entry:
                        video_info = self.extract_song_metadata(entry)
                        video_info['category'] = category
                        videos.append(video_info)
                
                return videos
                
        except Exception as e:
            logger.error(f"Error getting category videos fallback: {str(e)}")
            return []
