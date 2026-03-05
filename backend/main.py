import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime

# Import All Agents
from agents.ceo_agent import CEOAgent
from agents.content_agent import ContentAgent
from agents.video_agent import VideoAgent
from agents.platform_agent import PlatformAgent
from agents.analytics_agent import AnalyticsAgent
from memory.memory_manager import MemoryManager

# Initialize App
app = FastAPI(title="AI Free Social Media Office")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize All Agents
ceo = CEOAgent()
content = ContentAgent()
video = VideoAgent()
platform = PlatformAgent()
analytics = AnalyticsAgent()
memory = MemoryManager()

# Request Models
class GrowthRequest(BaseModel):
    auto: bool = True

# CEO GROWTH WORKFLOW (PDF Architecture)
@app.post("/auto-growth")
async def run_growth_cycle(request: GrowthRequest = None):
    """
    Complete Autonomous Growth Cycle:
    1. CEO Plans Strategy
    2. Content Agent Writes Scripts
    3. Video Agent Creates Videos
    4. Platform Agent Uploads
    5. Memory Stores & Learns
    """
    
    # 1. CEO Plans Growth Strategy
    strategy = ceo.plan_growth_strategy()
    
    results = []
    
    # 2. Execute for Each Topic
    for item in strategy.get('topics', []):
        try:
            # 3. Check Uniqueness (Memory)
            is_unique = memory.check_topic_uniqueness(
                item['topic'],
                item['platform']
            )
            
            if not is_unique:
                continue  # Skip duplicate topics
            
            # 4. Write Human Script
            script = content.write_script(
                topic=item['topic'],
                platform=item['platform'],
                language=item['language']
            )
            
            # 5. Create Video
            video_result = video.create_avatar_video(
                script=script['script'],
                language=item['language']
            )
            
            # 6. Upload to Platform
            if item['platform'] == 'YouTube':
                payload = platform.prepare_youtube(script, video_result.get('url', ''))
                upload_result = platform.upload_youtube(payload)
            else:
                payload = platform.prepare_instagram(script, video_result.get('url', ''))
                upload_result = platform.upload_instagram(payload)
            
            # 7. Store in Memory (Learning)
            memory.save_posted_topic(
                topic=item['topic'],
                platform=item['platform'],
                language=item['language']
            )
            
            memory.save_post({
                'topic': item['topic'],
                'platform': item['platform'],
                'language': item['language'],
                'script': script['script'],
                'video': video_result,
                'upload_result': upload_result,
                'reason': item.get('reason', '')
            })
            
            results.append({
                'topic': item['topic'],
                'platform': item['platform'],
                'language': item['language'],
                'status': upload_result.get('status', 'unknown'),
                'reason': item.get('reason', '')
            })
            
        except Exception as e:
            results.append({
                'topic': item.get('topic', 'unknown'),
                'error': str(e)
            })
    
    return {
        'status': 'success',
        'posts_created': len(results),
        'details': results,
        'timestamp': datetime.now().isoformat()
    }

@app.get("/analytics")
async def get_analytics():
    """Get Dashboard Analytics"""
    return analytics.generate_dashboard_data()

@app.get("/posts")
async def get_posts(limit: int = 50):
    """Get All Posts"""
    posts = list(memory.posts_collection.find().sort('created_at', -1).limit(limit))
    for post in posts:
        post['_id'] = str(post['_id'])
    return posts

@app.get("/health")
async def health():
    return {
        'status': 'online',
        'ceo': 'active',
        'goal': 'Maximize Views, Subs, Followers',
        'agents': {
            'ceo': 'ready',
            'content': 'ready',
            'video': 'ready',
            'platform': 'ready',
            'analytics': 'ready'
        }
    }

# Background Automation (Daily Posts)
async def auto_scheduler():
    """Auto-post daily at 9 AM"""
    while True:
        now = datetime.now()
        if now.hour == 9 and now.minute == 0:
            try:
                await run_growth_cycle()
            except:
                pass
        await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(auto_scheduler())
    print("[SYSTEM] Free AI Social Office Started")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=7860)