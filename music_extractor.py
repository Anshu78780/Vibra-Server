import yt_dlp
import logging

logger = logging.getLogger(__name__)

class MusicExtractor:
    """Class to handle music extraction and search using yt-dlp"""
    
    def __init__(self):
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
        """Search for songs using yt-dlp"""
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
            logger.error(f"Error searching songs: {str(e)}")
            return []
    
    def get_song_details(self, url):
        """Get detailed information about a specific song"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return self.extract_song_metadata(info)
                
        except Exception as e:
            logger.error(f"Error getting song details: {str(e)}")
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
        """Get YouTube homepage trending/popular videos"""
        try:
            # Get trending videos from YouTube
            trending_query = f"yttrending{max_results}:"
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Try to get trending videos
                try:
                    trending_results = ydl.extract_info(trending_query, download=False)
                    if trending_results and 'entries' in trending_results:
                        trending_videos = []
                        for entry in trending_results['entries']:
                            if entry:
                                video_info = self.extract_song_metadata(entry)
                                trending_videos.append(video_info)
                        
                        return {
                            'trending_music': trending_videos,
                            'categories': ['trending', 'music'],
                            'last_updated': 'now'
                        }
                except:
                    # If trending doesn't work, fall back to popular music searches
                    logger.info("Trending API not available, using popular music search as fallback")
                    pass
                
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
            logger.error(f"Error getting YouTube homepage data: {str(e)}")
            return None
    
    def get_category_videos(self, category="music", max_results=20):
        """Get videos by category"""
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
            logger.error(f"Error getting category videos: {str(e)}")
            return []
