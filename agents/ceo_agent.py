import os
import json
from groq import Groq
from datetime import datetime
from memory.memory_manager import MemoryManager

class CEOAgent:
    """Growth Strategist - Creates 3 Videos Daily"""
    
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        
        # Check if API key exists
        if not api_key:
            print("[WARNING] GROQ_API_KEY not found! Using mock mode.")
            self.client = None
        else:
            try:
                self.client = Groq(api_key=api_key)
                print("[CEO] Groq client initialized successfully")
            except Exception as e:
                print(f"[WARNING] Groq init failed: {e}")
                self.client = None
        
        self.memory = MemoryManager()
    
    def plan_daily_3_videos(self):
        """Plan 3 UNIQUE videos for today (Maximize Growth)"""
        
        # If Groq client failed, return mock plan
        if not self.client:
            return self._get_mock_plan()
        
        try:
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
            
            Return JSON:
            {{
                "daily_plan": [
                    {{
                        "video_number": 1,
                        "topic": "...",
                        "platform": "YouTube",
                        "language": "hindi",
                        "category": "Education",
                        "reason": "..."
                    }},
                    {{
                        "video_number": 2,
                        "topic": "...",
                        "platform": "Instagram",
                        "language": "telugu",
                        "category": "Entertainment",
                        "reason": "..."
                    }},
                    {{
                        "video_number": 3,
                        "topic": "...",
                        "platform": "YouTube",
                        "language": "english",
                        "category": "Motivation",
                        "reason": "..."
                    }}
                ]
            }}
            """
            
            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"[CEO] Planning error: {e}")
            return self._get_mock_plan()
    
    def _get_mock_plan(self):
        """Fallback plan if Groq fails"""
        return {
            "daily_plan": [
                {
                    "video_number": 1,
                    "topic": "Tech News Today",
                    "platform": "YouTube",
                    "language": "hindi",
                    "category": "Education",
                    "reason": "Trending topic with high search volume"
                },
                {
                    "video_number": 2,
                    "topic": "Comedy Skit",
                    "platform": "Instagram",
                    "language": "telugu",
                    "category": "Entertainment",
                    "reason": "Viral potential in regional audience"
                },
                {
                    "video_number": 3,
                    "topic": "Daily Motivation",
                    "platform": "YouTube",
                    "language": "english",
                    "category": "Motivation",
                    "reason": "Evergreen content with consistent views"
                }
            ]
        }
