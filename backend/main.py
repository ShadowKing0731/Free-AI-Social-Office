import os
import asyncio
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import shutil
import json

# Import All Agents
from agents.ceo_agent import CEOAgent
from agents.content_agent import ContentAgent
from agents.video_agent import VideoAgent
from agents.platform_agent import PlatformAgent
from agents.trend_agent import TrendAgent
from agents.analytics_agent import AnalyticsAgent
from memory.memory_manager import MemoryManager

# Initialize App
app = FastAPI(title="AI Social Media Office - Auto + Manual")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create storage directory
os.makedirs('storage/uploads', exist_ok=True)

# Initialize All Agents
ceo = None
content = None
video = None
platform = None
trend = None
analytics = None
memory = None

try:
    ceo = CEOAgent()
    print("[MAIN] ✅ CEO Agent initialized")
except Exception as e:
    print(f"[MAIN] ⚠️ CEO Agent init failed: {e}")

try:
    content = ContentAgent()
    print("[MAIN] ✅ Content Agent initialized")
except Exception as e:
    print(f"[MAIN] ⚠️ Content Agent init failed: {e}")

try:
    video = VideoAgent()
    print("[MAIN] ✅ Video Agent initialized")
except Exception as e:
    print(f"[MAIN] ⚠️ Video Agent init failed: {e}")

try:
    platform = PlatformAgent()
    print("[MAIN] ✅ Platform Agent initialized")
except Exception as e:
    print(f"[MAIN] ⚠️ Platform Agent init failed: {e}")

try:
    trend = TrendAgent()
    print("[MAIN] ✅ Trend Agent initialized")
except Exception as e:
    print(f"[MAIN] ⚠️ Trend Agent init failed: {e}")

try:
    analytics = AnalyticsAgent()
    print("[MAIN] ✅ Analytics Agent initialized")
except Exception as e:
    print(f"[MAIN] ⚠️ Analytics Agent init failed: {e}")

try:
    memory = MemoryManager()
    print("[MAIN] ✅ Memory Manager initialized")
except Exception as e:
    print(f"[MAIN] ⚠️ Memory Manager init failed: {e}")

# Request Models
class AutoVideoRequest(BaseModel):
    category: str = 'all'
    language: str = 'hindi'
    platform: str = 'YouTube'

class ManualVideoRequest(BaseModel):
    topic: str
    language: str = 'hindi'
    platform: str = 'YouTube'
    custom_instructions: Optional[str] = None

# ============================================
# AUTOMATIC VIDEO CREATION (Trending Topics)
# ============================================
@app.post("/auto-create-video")
async def auto_create_video(request: AutoVideoRequest):
    """
    COMPLETE AUTOMATIC WORKFLOW:
    1. Check Trending Topics
    2. Select Best Topic
    3. Generate Script + Title + Description + Tags
    4. Create AI Video
    5. Upload to YouTube/Instagram
    6. Store in Memory
    """
    try:
        if not trend:
            return {'status': 'error', 'message': 'Trend Agent not available'}
        
        if not content:
            return {'status': 'error', 'message': 'Content Agent not available'}
        
        # STEP 1: Get Trending Topics
        trending_data = trend.get_trending_topics(
            category=request.category,
            language=request.language
        )
        
        # STEP 2: Select Best Topic
        best_topic = trend.select_best_topic(
            trending_data.get('topics', []),
            platform=request.platform
        )
        
        if not best_topic:
            return {'status': 'error', 'message': 'No trending topics found'}
        
        # STEP 3: Generate Complete Content (Script + Title + Description + Tags)
        content_data = content.create_complete_content(
            topic=best_topic['topic'],
            platform=request.platform,
            language=request.language,
            auto_mode=True
        )
        
        # STEP 4: Create AI Video
        video_result = {'status': 'mock', 'url': ''}
        if video:
            script_text = content_data.get('content', {}).get('script', {}).get('full_script', '')
            video_result = video.create_avatar_video(
                script=script_text,
                language=request.language
            )
        
        # STEP 5: Upload to Platform
        upload_result = {'status': 'mock', 'platform': request.platform}
        if platform:
            if request.platform == 'YouTube':
                payload = platform.prepare_youtube(content_data, video_result.get('url', ''))
                upload_result = platform.upload_youtube(payload)
            else:
                payload = platform.prepare_instagram(content_data, video_result.get('url', ''))
                upload_result = platform.upload_instagram(payload)
        
        # STEP 6: Store in Memory (Learning)
        if memory:
            memory.save_posted_topic(
                topic=best_topic['topic'],
                platform=request.platform,
                language=request.language
            )
            
            memory.save_auto_post({
                'topic': best_topic['topic'],
                'platform': request.platform,
                'language': request.language,
                'category': best_topic.get('category', 'General'),
                'content': content_data.get('content', {}),
                'video': video_result,
                'upload_result': upload_result,
                'trend_reason': best_topic.get('reason', ''),
                'view_potential': best_topic.get('view_potential', 'medium'),
                'mode': 'automatic'
            })
        
        return {
            'status': 'success',
            'mode': 'automatic',
            'topic': best_topic['topic'],
            'trend_reason': best_topic.get('reason', ''),
            'content': content_data.get('content', {}),
            'video': video_result,
            'upload': upload_result,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# MANUAL VIDEO CREATION (User Prompt)
# ============================================
@app.post("/manual-create-video")
async def manual_create_video(request: ManualVideoRequest):
    """
    COMPLETE MANUAL WORKFLOW:
    1. User Provides Topic/Prompt
    2. Generate Script + Title + Description + Tags
    3. Create AI Video
    4. Upload to YouTube/Instagram
    5. Store in Memory
    """
    try:
        if not content:
            return {'status': 'error', 'message': 'Content Agent not available'}
        
        # STEP 1: Generate Complete Content from User Prompt
        content_data = content.create_complete_content(
            topic=request.topic,
            platform=request.platform,
            language=request.language,
            auto_mode=False
        )
        
        # STEP 2: Create AI Video
        video_result = {'status': 'mock', 'url': ''}
        if video:
            script_text = content_data.get('content', {}).get('script', {}).get('full_script', '')
            video_result = video.create_avatar_video(
                script=script_text,
                language=request.language
            )
        
        # STEP 3: Upload to Platform
        upload_result = {'status': 'mock', 'platform': request.platform}
        if platform:
            if request.platform == 'YouTube':
                payload = platform.prepare_youtube(content_data, video_result.get('url', ''))
                upload_result = platform.upload_youtube(payload)
            else:
                payload = platform.prepare_instagram(content_data, video_result.get('url', ''))
                upload_result = platform.upload_instagram(payload)
        
        # STEP 4: Store in Memory (Learning)
        if memory:
            memory.save_posted_topic(
                topic=request.topic,
                platform=request.platform,
                language=request.language
            )
            
            memory.save_manual_post({
                'topic': request.topic,
                'platform': request.platform,
                'language': request.language,
                'content': content_data.get('content', {}),
                'video': video_result,
                'upload_result': upload_result,
                'custom_instructions': request.custom_instructions,
                'mode': 'manual'
            })
        
        return {
            'status': 'success',
            'mode': 'manual',
            'topic': request.topic,
            'content': content_data.get('content', {}),
            'video': video_result,
            'upload': upload_result,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# MANUAL UPLOAD (Your Own Video File)
# ============================================
@app.post("/manual-upload")
async def manual_upload_video(
    title: str = Form(...),
    description: str = Form(...),
    platform: str = Form(...),
    language: str = Form(...),
    category: str = Form(...),
    tags: str = Form(...),
    video_file: UploadFile = File(...)
):
    """Manual Video File Upload"""
    try:
        file_path = f"storage/uploads/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{video_file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(video_file.file, buffer)
        
        tags_list = [tag.strip() for tag in tags.split(',')]
        
        upload_result = {'status': 'mock'}
        if platform:
            if platform.lower() == 'youtube':
                payload = {
                    'title': title,
                    'description': description,
                    'tags': tags_list,
                    'category': category,
                    'language': language,
                    'video_path': file_path
                }
                upload_result = platform.upload_youtube(payload)
            else:
                payload = {
                    'caption': f"{title}\n\n{description}",
                    'hashtags': tags_list,
                    'language': language,
                    'video_path': file_path
                }
                upload_result = platform.upload_instagram(payload)
        
        if memory:
            memory.save_manual_post({
                'title': title,
                'description': description,
                'platform': platform,
                'language': language,
                'category': category,
                'tags': tags_list,
                'video_path': file_path,
                'upload_result': upload_result,
                'upload_type': 'manual'
            })
            memory.save_posted_topic(title, platform, language)
        
        return {
            'status': 'success',
            'message': 'Video uploaded successfully',
            'upload_result': upload_result,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# ANALYTICS & POSTS
# ============================================
@app.get("/analytics")
async def get_analytics():
    """Get Dashboard Analytics"""
    try:
        if memory:
            return memory.get_analytics()
        else:
            return {
                'total_posts': 0,
                'auto_posts': 0,
                'manual_posts': 0,
                'today_posts': 0,
                'youtube_posts': 0,
                'instagram_posts': 0,
                'languages': {},
                'total_views': 0,
                'subscribers_gained': 0,
                'followers_gained': 0
            }
    except Exception as e:
        return {
            'total_posts': 0,
            'auto_posts': 0,
            'manual_posts': 0,
            'today_posts': 0,
            'youtube_posts': 0,
            'instagram_posts': 0,
            'languages': {},
            'total_views': 0,
            'subscribers_gained': 0,
            'followers_gained': 0,
            'error': str(e)
        }

@app.get("/posts")
async def get_posts(limit: int = 50):
    """Get All Posts"""
    try:
        if memory:
            return memory.get_all_posts(limit)
        else:
            return []
    except Exception as e:
        return []

@app.get("/health")
async def health():
    return {
        'status': 'online',
        'ceo': 'active' if ceo else 'inactive',
        'auto_video': 'enabled',
        'manual_video':
