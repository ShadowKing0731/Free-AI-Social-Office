import os
import requests
from datetime import datetime, timedelta
from memory.memory_manager import MemoryManager

class AnalyticsAgent:
    """Tracks Growth: Views, Subs, Followers"""
    
    def __init__(self):
        self.memory = MemoryManager()
        self.youtube_key = os.getenv('YOUTUBE_API_KEY', '')
        self.instagram_token = os.getenv('INSTAGRAM_TOKEN', '')
    
    def get_youtube_stats(self, video_id):
        """Get YouTube video analytics"""
        try:
            url = 'https://www.googleapis.com/youtube/v3/videos'
            params = {
                'part': 'statistics',
                'id': video_id,
                'key': self.youtube_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            stats = data.get('items', [{}])[0].get('statistics', {})
            
            return {
                'platform': 'YouTube',
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'comments': int(stats.get('commentCount', 0))
            }
        except:
            return {'platform': 'YouTube', 'views': 0, 'likes': 0}
    
    def get_instagram_stats(self, media_id):
        """Get Instagram post analytics"""
        try:
            url = f'https://graph.facebook.com/v18.0/{media_id}'
            params = {
                'fields': 'insights.metric(impressions,reach,engagement)',
                'access_token': self.instagram_token
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            return {
                'platform': 'Instagram',
                'impressions': data.get('insights', {}).get('data', [{}])[0].get('values', [{}])[0].get('value', 0),
                'reach': data.get('insights', {}).get('data', [{}])[1].get('values', [{}])[0].get('value', 0)
            }
        except:
            return {'platform': 'Instagram', 'impressions': 0, 'reach': 0}
    
    def generate_dashboard_data(self):
        """Complete analytics for dashboard"""
        return self.memory.get_analytics()