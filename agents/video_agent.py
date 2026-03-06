import os
import requests
from datetime import datetime

class VideoAgent:
    """Creates AI Videos with Avatar + Voice"""
    
    def __init__(self):
        self.d_id_api_key = os.getenv('D_ID_API_KEY', '')
        self.heygen_api_key = os.getenv('HEYGEN_API_KEY', '')
    
    def create_avatar_video(self, script, language='hindi'):
        """Create video with AI human avatar"""
        
        # Language to Voice Mapping
        voice_map = {
            'hindi': 'hi-IN-standard',
            'telugu': 'te-IN-standard',
            'tamil': 'ta-IN-standard',
            'english': 'en-US-standard'
        }
        
        # Use D-ID API (Free Trial)
        if self.d_id_api_key:
            try:
                headers = {
                    'Authorization': f'Basic {self.d_id_api_key}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    "source_url": "https://d-id-public-bucket.s3.us-west-2.amazonaws.com/avatar.jpg",
                    "script": {
                        "type": "text",
                        "input": script[:500],  # D-ID character limit
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
                    'method': 'D-ID'
                }
                
            except Exception as e:
                return self._create_mock_video(script, language, str(e))
        else:
            return self._create_mock_video(script, language, 'No D-ID API key')
    
    def _create_mock_video(self, script, language, reason=''):
        """Mock video creation for testing"""
        return {
            'status': 'mock',
            'url': 'https://example.com/video.mp4',
            'language': language,
            'created_at': datetime.now().isoformat(),
            'method': 'Mock',
            'note': reason
        }
    
    def check_video_status(self, talk_id):
        """Check if video is ready"""
        try:
            headers = {'Authorization': f'Basic {self.d_id_api_key}'}
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
