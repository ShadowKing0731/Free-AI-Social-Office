import os
import requests
from datetime import datetime

class VideoAgent:
    """Creates Human-Type AI Videos (FREE Methods)"""
    
    def __init__(self):
        # FREE Options (No Payment Required)
        self.did_api_key = os.getenv('D_ID_API_KEY', '')  # Free trial credits
        self.pictory_api_key = os.getenv('PICTORY_API_KEY', '')  # Free trial
        
    def create_avatar_video(self, script, language):
        """Create video with AI human avatar"""
        
        # Language to Voice Mapping
        voice_map = {
            'hindi': 'hi-IN-standard',
            'telugu': 'te-IN-standard',
            'tamil': 'ta-IN-standard',
            'english': 'en-US-standard'
        }
        
        try:
            # D-ID API (Free Trial - 20 credits)
            headers = {
                'Authorization': f'Basic {self.did_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "source_url": "https://d-id-public-bucket.s3.us-west-2.amazonaws.com/avatar.jpg",
                "script": {
                    "type": "text",
                    "input": script[:500],  # D-ID has character limit
                    "provider": {
                        "type": "microsoft",
                        "voice_id": voice_map.get(language, 'en-US-standard')
                    }
                }
            }
            
            response = requests.post(
                'https://api.d-id.com/talks',
                headers=headers,
                json=payload
            )
            
            talk_id = response.json().get('id', '')
            
            return {
                'status': 'processing',
                'talk_id': talk_id,
                'language': language,
                'created_at': datetime.now().isoformat(),
                'method': 'D-ID Free Trial'
            }
            
        except Exception as e:
            # FALLBACK: Return script for manual video creation
            return {
                'status': 'fallback',
                'error': str(e),
                'script': script,
                'method': 'Manual creation required',
                'free_alternative': 'Use Canva or CapCut for free video creation'
            }
    
    def check_video_status(self, talk_id):
        """Check if D-ID video is ready"""
        try:
            headers = {'Authorization': f'Basic {self.did_api_key}'}
            response = requests.get(
                f'https://api.d-id.com/talks/{talk_id}',
                headers=headers
            )
            
            data = response.json()
            status = data.get('status', '')
            
            if status == 'done':
                video_url = data.get('result_url', '')
                return {'status': 'ready', 'url': video_url}
            else:
                return {'status': status}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}