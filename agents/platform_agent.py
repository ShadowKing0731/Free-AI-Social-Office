import os
import requests
from datetime import datetime

class PlatformAgent:
    """Handles YouTube & Instagram Uploads with Auto Metadata"""
    
    def __init__(self):
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY', '')
        self.instagram_token = os.getenv('INSTAGRAM_TOKEN', '')
        self.instagram_business_id = os.getenv('INSTAGRAM_BUSINESS_ID', '')
    
    def prepare_youtube(self, content, video_url):
        """Auto-prepare YouTube upload with ALL metadata"""
        
        content_data = content.get('content', content)
        
        return {
            'title': content_data.get('title', 'Auto Generated Video'),
            'description': content_data.get('description', ''),
            'tags': content_data.get('tags', []),
            'category': content_data.get('category', '22'),  # People & Blogs
            'language': content_data.get('language', 'en'),
            'privacy': 'public',
            'video_url': video_url,
            'thumbnail_text': content_data.get('thumbnail_text', ''),
            'auto_generated': True
        }
    
    def prepare_instagram(self, content, video_url):
        """Auto-prepare Instagram Reels with ALL metadata"""
        
        content_data = content.get('content', content)
        hashtags = content_data.get('hashtags', [])
        
        return {
            'caption': f"{content_data.get('title', '')}\n\n{content_data.get('description', '')[:200]}...\n\n{' '.join(hashtags)}",
            'hashtags': hashtags,
            'video_url': video_url,
            'share_to_feed': True,
            'auto_generated': True
        }
    
    def upload_youtube(self, payload):
        """Upload to YouTube (Mock for free tier)"""
        try:
            # In production, use Google API Client with OAuth2
            # For free tier, return mock success
            
            return {
                'status': 'uploaded',
                'platform': 'YouTube',
                'title': payload['title'],
                'url': f'https://youtube.com/watch?v=MOCK_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'uploaded_at': datetime.now().isoformat(),
                'auto_generated': payload.get('auto_generated', False)
            }
        except Exception as e:
            return {
                'status': 'failed',
                'platform': 'YouTube',
                'error': str(e)
            }
    
    def upload_instagram(self, payload):
        """Post to Instagram Reels (Mock for free tier)"""
        try:
            return {
                'status': 'posted',
                'platform': 'Instagram',
                'media_id': f'IG_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'posted_at': datetime.now().isoformat(),
                'auto_generated': payload.get('auto_generated', False)
            }
        except Exception as e:
            return {
                'status': 'failed',
                'platform': 'Instagram',
                'error': str(e)
            }
