import os
from groq import Groq
from datetime import datetime

class ContentAgent:
    """Creates Scripts, Descriptions, Tags, Titles - ALL Automated"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    
    def create_complete_content(self, topic, platform='YouTube', language='hindi', auto_mode=True):
        """Generate EVERYTHING: Script + Title + Description + Tags"""
        
        language_names = {
            'hindi': 'Hindi (हिंदी)',
            'telugu': 'Telugu (తెలుగు)',
            'tamil': 'Tamil (தமிழ்)',
            'english': 'English'
        }
        
        prompt = f"""
        You are a Professional Content Creator for {platform}.
        
        Topic: {topic}
        Language: {language_names.get(language, 'English')}
        Mode: {'Automatic (Trending)' if auto_mode else 'Manual (User Request)'}
        
        Generate COMPLETE content package:
        
        1. VIDEO SCRIPT (60 seconds):
           - Hook (0-5 seconds): Grab attention immediately
           - Content (5-50 seconds): Main value/information
           - CTA (50-60 seconds): Subscribe/Follow call-to-action
           - Include visual directions [Show: ...]
           - Natural, human-like tone (NOT robotic)
        
        2. VIDEO TITLE:
           - Under 60 characters
           - Include keywords for SEO
           - Add emotional trigger
           - Platform optimized
        
        3. VIDEO DESCRIPTION:
           - First 2 lines: Hook + Keywords
           - Middle: Detailed explanation
           - End: Call-to-action + Links
           - Total: 200-500 characters
        
        4. TAGS/HASHTAGS:
           - 10-15 relevant tags
           - Mix of high/medium/low competition
           - Include language-specific tags
           - Platform optimized
        
        5. THUMBNAIL TEXT:
           - 3-5 words maximum
           - Bold, attention-grabbing
        
        Return JSON format:
        {{
            "script": {{
                "hook": "...",
                "content": "...",
                "cta": "...",
                "full_script": "..."
            }},
            "title": "...",
            "description": "...",
            "tags": ["...", "..."],
            "hashtags": ["#", "#"],
            "thumbnail_text": "...",
            "category": "...",
            "language": "..."
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=3000
            )
            
            import json
            content = json.loads(response.choices[0].message.content)
            
            return {
                'status': 'success',
                'content': content,
                'created_at': datetime.now().isoformat(),
                'mode': 'auto' if auto_mode else 'manual'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'content': {
                    'script': {'full_script': f'Video about {topic}'},
                    'title': f'{topic} - {language}',
                    'description': f'Watch this amazing video about {topic}',
                    'tags': [topic, language, 'viral', 'trending'],
                    'hashtags': [f'#{topic.replace(" ", "")}', f'#{language}', '#viral'],
                    'thumbnail_text': topic[:20],
                    'category': 'General'
                },
                'created_at': datetime.now().isoformat(),
                'mode': 'auto' if auto_mode else 'manual'
            }
    
    def write_script(self, topic, platform, language):
        """Backward compatibility - calls create_complete_content"""
        result = self.create_complete_content(topic, platform, language, auto_mode=True)
        return result.get('content', {})
