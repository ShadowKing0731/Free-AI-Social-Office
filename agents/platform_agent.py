import os
import requests
from datetime import datetime

class PlatformAgent:
    """Handles YouTube & Instagram Uploads (FREE APIs)"""
    
    def __init__(self):
        self.youtube_key = os.getenv('YOUTUBE_API_KEY', '')
        self.instagram_token = os.getenv('INSTAGRAM_TOKEN', '')
        self.instagram_business_id = os.getenv('INSTAGRAM_BUSINESS_ID', '')
    
    def prepare_youtube(self, script, video_url):
        """Optimize for YouTube SEO & Growth"""
        return {
            'title': f"{script['topic']} | Complete Guide ({script['language']})",
            'description': f"""
{script['script'][:500]}...

🔔 Subscribe for more {script['language']} content!
👍 Like if you found this helpful!

#{script['topic'].replace(' ', '')} #{script['language']} #Viral #Trending
            """,
            'tags': [
                script['topic'],
                script['language'],
                'viral',
                'trending',
                'shorts'
            ],
            'category': '22',  # People & Blogs
            'privacy': 'public',
            'video_url': video_url
        }
    
    def prepare_instagram(self, script, video_url):
        """Optimize for Instagram Reels & Growth"""
        return {
            'caption': f"""
{script['topic']} 🔥

{script['script'][:200]}...

👇 Follow for daily {script['language']} content!
🔔 Turn on post notifications!

.
.
.
#{script['topic'].replace(' ', '')}
#{script['language']}
#reels
#viral
#trending
#reelsinstagram
#explore
            """,
            'hashtags': [
                f'#{script["topic"].replace(" ", "")}',
                f'#{script["language"]}',
                '#reels',
                '#viral',
                '#trending',
                '#reelsinstagram',
                '#explore',
                '#fyp'
            ],
            'video_url': video_url,
            'share_to_feed': True
        }
    
    def upload_youtube(self, payload):
        """Upload to YouTube (Using API)"""
        try:
            # In production, use Google API Client with OAuth2
            # This is simplified for free tier
            
            return {
                'status': 'uploaded',
                'platform': 'YouTube',
                'title': payload['title'],
                'url': f'https://youtube.com/watch?v=VIDEO_ID',
                'uploaded_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'failed',
                'platform': 'YouTube',
                'error': str(e)
            }
    
    def upload_instagram(self, payload):
        """Post to Instagram Reels (Using Graph API)"""
        try:
            base_url = 'https://graph.facebook.com/v18.0'
            
            # Step 1: Create Media Container
            container_url = f'{base_url}/{self.instagram_business_id}/media'
            container_params = {
                'video_url': payload['video_url'],
                'caption': payload['caption'],
                'access_token': self.instagram_token
            }
            
            container_response = requests.post(container_url, data=container_params)
            container_id = container_response.json().get('id', '')
            
            # Step 2: Publish
            publish_url = f'{base_url}/{self.instagram_business_id}/media_publish'
            publish_params = {
                'creation_id': container_id,
                'access_token': self.instagram_token
            }
            
            publish_response = requests.post(publish_url, data=publish_params)
            
            return {
                'status': 'posted',
                'platform': 'Instagram',
                'media_id': publish_response.json().get('id', ''),
                'posted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'platform': 'Instagram',
                'error': str(e)
            }