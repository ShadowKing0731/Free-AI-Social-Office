import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import requests

from agents.ceo_agent import CEOAgent
from agents.content_agent import ContentAgent
from agents.video_agent import VideoAgent
from agents.platform_agent import PlatformAgent
from agents.trend_agent import TrendAgent
from agents.analytics_agent import AnalyticsAgent
from memory.memory_manager import MemoryManager

app = FastAPI(title="AI Cloud Office - YouTube Upload")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

os.makedirs('storage/videos', exist_ok=True)
os.makedirs('storage/uploads', exist_ok=True)

ceo = None
content = None
video = None
platform = None
trend = None
analytics = None
memory = None

try:
    ceo = CEOAgent()
    print("[MAIN] ✅ CEO initialized")
except Exception as e:
    print(f"[MAIN] ⚠️ CEO failed: {e}")

try:
    content = ContentAgent()
    print("[MAIN] ✅ Content initialized")
except Exception as e:
    print(f"[MAIN] ⚠️ Content failed: {e}")

try:
    video = VideoAgent()
    print("[MAIN] ✅ Video initialized")
except Exception as e:
    print(f"[MAIN] ⚠️ Video failed: {e}")

try:
    platform = PlatformAgent()
    print("[MAIN] ✅ Platform initialized")
except Exception as e:
    print(f"[MAIN] ⚠️ Platform failed: {e}")

try:
    trend = TrendAgent()
    print("[MAIN] ✅ Trend initialized")
except Exception as e:
    print(f"[MAIN] ⚠️ Trend failed: {e}")

try:
    analytics = AnalyticsAgent()
    print("[MAIN] ✅ Analytics initialized")
except Exception as e:
    print(f"[MAIN] ⚠️ Analytics failed: {e}")

try:
    memory = MemoryManager()
    print("[MAIN] ✅ Memory initialized")
except Exception as e:
    print(f"[MAIN] ⚠️ Memory failed: {e}")

class AutoVideoRequest(BaseModel):
    category: str = 'all'
    language: str = 'hindi'
    platform: str = 'YouTube'

class ManualVideoRequest(BaseModel):
    topic: str
    language: str = 'hindi'
    platform: str = 'YouTube'
    custom_instructions: Optional[str] = None

@app.post("/auto-create-video")
async def auto_create_video(request: AutoVideoRequest):
    try:
        if not trend or not content:
            return {'status': 'error', 'message': 'Agents not available'}
        
        trending_data = trend.get_trending_topics(category=request.category, language=request.language)
        best_topic = trend.select_best_topic(trending_data.get('topics', []), platform=request.platform)
        
        if not best_topic:
            return {'status': 'error', 'message': 'No trending topics found'}
        
        content_data = content.create_complete_content(topic=best_topic['topic'], platform=request.platform, language=request.language, auto_mode=True)
        
        video_result = {'status': 'mock', 'url': '', 'video_path': ''}
        if video:
            script_text = content_data.get('content', {}).get('script', {}).get('full_script', '')
            video_result = video.create_avatar_video(script=script_text, language=request.language)
        
        upload_result = {'status': 'mock', 'platform': request.platform, 'youtube_link': ''}
        if platform:
            if request.platform == 'YouTube':
                payload = platform.prepare_youtube(content_data, video_result.get('url', ''))
                payload['video_path'] = video_result.get('video_path', '')
                upload_result = platform.upload_youtube(payload)
            else:
                payload = platform.prepare_instagram(content_data, video_result.get('url', ''))
                upload_result = platform.upload_instagram(payload)
        
        if memory:
            memory.save_posted_topic(topic=best_topic['topic'], platform=request.platform, language=request.language)
            memory.save_auto_post({
                'topic': best_topic['topic'],
                'platform': request.platform,
                'language': request.language,
                'category': best_topic.get('category', 'General'),
                'content': content_data.get('content', {}),
                'video': video_result,
                'upload_result': upload_result,
                'trend_reason': best_topic.get('reason', ''),
                'mode': 'automatic',
                'youtube_link': upload_result.get('youtube_link', '')
            })
        
        return {
            'status': 'success',
            'mode': 'automatic',
            'topic': best_topic['topic'],
            'trend_reason': best_topic.get('reason', ''),
            'content': content_data.get('content', {}),
            'video': video_result,
            'upload': upload_result,
            'youtube_link': upload_result.get('youtube_link', ''),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/manual-create-video")
async def manual_create_video(request: ManualVideoRequest):
    try:
        if not content:
            return {'status': 'error', 'message': 'Content Agent not available'}
        
        content_data = content.create_complete_content(topic=request.topic, platform=request.platform, language=request.language, auto_mode=False)
        
        video_result = {'status': 'mock', 'url': '', 'video_path': ''}
        if video:
            script_text = content_data.get('content', {}).get('script', {}).get('full_script', '')
            video_result = video.create_avatar_video(script=script_text, language=request.language)
        
        upload_result = {'status': 'mock', 'platform': request.platform, 'youtube_link': ''}
        if platform:
            if request.platform == 'YouTube':
                payload = platform.prepare_youtube(content_data, video_result.get('url', ''))
                payload['video_path'] = video_result.get('video_path', '')
                upload_result = platform.upload_youtube(payload)
            else:
                payload = platform.prepare_instagram(content_data, video_result.get('url', ''))
                upload_result = platform.upload_instagram(payload)
        
        if memory:
            memory.save_posted_topic(topic=request.topic, platform=request.platform, language=request.language)
            memory.save_manual_post({
                'topic': request.topic,
                'platform': request.platform,
                'language': request.language,
                'content': content_data.get('content', {}),
                'video': video_result,
                'upload_result': upload_result,
                'mode': 'manual',
                'youtube_link': upload_result.get('youtube_link', '')
            })
        
        return {
            'status': 'success',
            'mode': 'manual',
            'topic': request.topic,
            'content': content_data.get('content', {}),
            'video': video_result,
            'upload': upload_result,
            'youtube_link': upload_result.get('youtube_link', ''),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics")
async def get_analytics():
    try:
        if memory:
            return memory.get_analytics()
        else:
            return {'total_posts': 0, 'auto_posts': 0, 'manual_posts': 0, 'today_posts': 0, 'youtube_posts': 0, 'instagram_posts': 0, 'languages': {}, 'total_views': 0, 'subscribers_gained': 0, 'followers_gained': 0}
    except Exception as e:
        return {'total_posts': 0, 'auto_posts': 0, 'manual_posts': 0, 'today_posts': 0, 'youtube_posts': 0, 'instagram_posts': 0, 'languages': {}, 'total_views': 0, 'subscribers_gained': 0, 'followers_gained': 0, 'error': str(e)}

@app.get("/posts")
async def get_posts(limit: int = 50):
    try:
        if memory:
            return memory.get_all_posts(limit)
        else:
            return []
    except Exception as e:
        return []

@app.get("/health")
async def health():
    oauth_configured = os.path.exists('storage/youtube_creds.pickle')
    return {
        'status': 'online',
        'ceo': 'active' if ceo else 'inactive',
        'auto_video': 'enabled',
        'manual_video': 'enabled',
        'youtube_oauth': 'configured' if oauth_configured else 'not_configured',
        'memory': 'mock' if (memory and memory.use_mock) else 'mongodb',
        'agents': {
            'ceo': 'ready' if ceo else 'not initialized',
            'content': 'ready' if content else 'not initialized',
            'video': 'ready' if video else 'not initialized',
            'platform': 'ready' if platform else 'not initialized',
            'trend': 'ready' if trend else 'not initialized'
        }
    }

async def auto_scheduler():
    while True:
        now = datetime.now()
        if now.hour == 9 and now.minute == 0:
            try:
                for lang in ['hindi', 'telugu', 'english']:
                    await auto_create_video(AutoVideoRequest(category='all', language=lang, platform='YouTube'))
            except Exception as e:
                print(f"Scheduled video failed: {e}")
        await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    if trend and content:
        asyncio.create_task(auto_scheduler())
        print("[SYSTEM] ✅ Auto + Manual Video Creation Enabled")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=7860)
