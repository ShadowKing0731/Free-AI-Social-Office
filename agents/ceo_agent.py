import os
import json
from groq import Groq
from datetime import datetime
from memory.memory_manager import MemoryManager

class CEOAgent:
    """Growth Strategist - Creates 3 Videos Daily"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.memory = MemoryManager()
    
    def plan_daily_3_videos(self):
        """Plan 3 UNIQUE videos for today (Maximize Growth)"""
        
        # Get past performance (Learning)
        yt_best = self.memory.get_best_performing_topics('YouTube')
        ig_best = self.memory.get_best_performing_topics('Instagram')
        
        # Get posted topics (Avoid Repetition - Last 30 Days)
        yt_posted = [t['topic'] for t in self.memory.topics_collection.find(
            {'platform': 'YouTube'}
        ).sort('posted_at', -1).limit(30)]
        
        ig_posted = [t['topic'] for t in self.memory.topics_collection.find(
            {'platform': 'Instagram'}
        ).sort('posted_at', -1).limit(30)]
        
        prompt = f"""
        You are a YouTube & Instagram Growth Expert.
        Goal: Create 3 VIRAL videos for TODAY (Maximum Views, Subs, Followers).
        
        YouTube Best Topics: {yt_best}
        Instagram Best Topics: {ig_best}
        
        YouTube Posted Recently (DO NOT REPEAT): {yt_posted}
        Instagram Posted Recently (DO NOT REPEAT): {ig_posted}
        
        Task: Select 3 COMPLETELY NEW topics (unique, not in posted lists)
        
        Requirements:
        1. Video 1: YouTube + Hindi (Educational/Tech)
        2. Video 2: Instagram + Telugu (Entertainment/Trending)
        3. Video 3: YouTube Shorts + Tamil OR English (Motivation/News)
        
        Each must have:
        - Unique topic (not repeated)
        - Viral potential reason
        - Platform-optimized strategy
        - Target audience
        
        Return JSON:
        {{
            "daily_plan": [
                {{
                    "video_number": 1,
                    "topic": "...",
                    "platform": "YouTube",
                    "language": "hindi",
                    "category": "Education",
                    "reason": "...",
                    "target_views": 1000
                }},
                {{
                    "video_number": 2,
                    "topic": "...",
                    "platform": "Instagram",
                    "language": "telugu",
                    "category": "Entertainment",
                    "reason": "...",
                    "target_views": 5000
                }},
                {{
                    "video_number": 3,
                    "topic": "...",
                    "platform": "YouTube",
                    "language": "tamil",
                    "category": "Motivation",
                    "reason": "...",
                    "target_views": 2000
                }}
            ]
        }}
        """
        
        response = self.client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return json.loads(response.choices[0].message.content)
