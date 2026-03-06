import os
import requests
from datetime import datetime

class PlatformAgent:
    """Handles YouTube & Instagram Uploads with REAL Upload"""
    
    def __init__(self):
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY', '')
        self.instagram_token = os.getenv('INSTAGRAM_TOKEN', '')
        self.instagram_business_id = os.getenv('INSTAGRAM_BUSINESS_ID', '')
    
    def prepare_youtube(self, content, video_url):
        content_data = content.get('content', content)
        return {
            'title': content_data.get('title', 'Auto Generated Video')[:100],
            'description': content_data.get('description', '')[:5000],
            'tags': content_data.get('tags', [])[:30],
            'category': content_data.get('category', '22'),
            'language': content_data.get('language', 'en'),
            'privacy': 'public',
            'video_url': video_url,
            'auto_generated': True
        }
    
    def prepare_instagram(self, content, video_url):
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
        """Upload to YouTube (Mock for free tier, Real with OAuth2)"""
        try:
            # Check if OAuth2 is configured (check for credentials file)
            oauth_configured = os.path.exists('storage/youtube_creds.pickle')
            
            if oauth_configured and payload.get('video_path'):
                # REAL UPLOAD CODE
                from google.oauth2.credentials import Credentials
                from googleapiclient.discovery import build
                from googleapiclient.http import MediaFileUpload
                import pickle
                
                with open('storage/youtube_creds.pickle', 'rb') as token:
                    creds = pickle.load(token)
                
                youtube = build('youtube', 'v3', credentials=creds)
                
                video_body = {
                    'snippet': {
                        'title': payload['title'],
                        'description': payload['description'],
                        'tags': payload['tags'],
                        'categoryId': payload.get('category', '22')
                    },
                    'status': {
                        'privacyStatus': payload.get('privacy', 'public'),
                        'selfDeclaredMadeForKids': False
                    }
                }
                
                media = MediaFileUpload(payload['video_path'], chunksize=-1, resumable=True)
                request = youtube.videos().insert(part='snippet,status', body=video_body, media_body=media)
                response = request.execute()
                
                video_id = response.get('id', '')
                video_url = f'https://youtube.com/watch?v={video_id}'
                
                return {
                    'status': 'uploaded',
                    'platform': 'YouTube',
                    'title': payload['title'],
                    'url': video_url,
                    'video_id': video_id,
                    'uploaded_at': datetime.now().isoformat(),
                    'auto_generated': True,
                    'youtube_link': video_url
                }
            else:
                # MOCK UPLOAD (Free Tier)
                video_id = f'MOCK_{datetime.now().strftime("%Y%m%d%H%M%S")}'
                video_url = f'https://youtube.com/watch?v={video_id}'
                
                return {
                    'status': 'ready_for_upload',
                    'platform': 'YouTube',
                    'title': payload['title'],
                    'url': video_url,
                    'video_id': video_id,
                    'uploaded_at': datetime.now().isoformat(),
                    'auto_generated': True,
                    'youtube_link': video_url,
                    'note': 'OAuth2 not configured. Video metadata ready. Download and upload manually to YouTube.',
                    'download_url': payload.get('video_url', '')
                }
        except Exception as e:
            return {
                'status': 'failed',
                'platform': 'YouTube',
                'error': str(e),
                'youtube_link': ''
            }
    
    def upload_instagram(self, payload):
        try:
            if not self.instagram_token or not self.instagram_business_id:
                return {
                    'status': 'ready_for_upload',
                    'platform': 'Instagram',
                    'media_id': f'IG_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                    'posted_at': datetime.now().isoformat(),
                    'note': 'Instagram credentials not configured'
                }
            
            base_url = 'https://graph.facebook.com/v18.0'
            container_url = f'{base_url}/{self.instagram_business_id}/media'
            container_params = {'video_url': payload.get('video_url', ''), 'caption': payload.get('caption', ''), 'access_token': self.instagram_token}
            container_response = requests.post(container_url, data=container_params)
            container_id = container_response.json().get('id', '')
            
            publish_url = f'{base_url}/{self.instagram_business_id}/media_publish'
            publish_params = {'creation_id': container_id, 'access_token': self.instagram_token}
            publish_response = requests.post(publish_url, data=publish_params)
            
            return {
                'status': 'posted',
                'platform': 'Instagram',
                'media_id': publish_response.json().get('id', ''),
                'posted_at': datetime.now().isoformat(),
                'instagram_link': f'https://instagram.com/p/{publish_response.json().get("id", "")}'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'platform': 'Instagram',
                'error': str(e),
                'instagram_link': ''
            }
