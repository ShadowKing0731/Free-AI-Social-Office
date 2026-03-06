import os
import asyncio
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import shutil

# Import All Agents
from agents.ceo_agent import CEOAgent
from agents.content_agent import ContentAgent
from agents.video_agent import VideoAgent
from agents.platform_agent import PlatformAgent
from agents.analytics_agent import AnalyticsAgent
from memory.memory_manager import MemoryManager

# Initialize App
app = FastAPI(title="AI Free Social Media Office")

# Enable CORS - Allow ALL Origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create storage directory for manual uploads
os.makedirs('storage/uploads', exist_ok=True)

# Initialize All Agents with Error Handling
try:
    ceo = CEOAgent()
    print("[MAIN] ✅ CEO Agent initialized")
except Exception as e:
    print(f"[MAIN] ⚠️ CEO Agent init failed: {e}")
    ceo = None

try:
    content = ContentAgent()
    print("[MAIN] ✅ Content Agent initialized")
except Exception as e:
    print(f"[MAIN] ⚠️ Content Agent init failed: {e}")
    content = None

try:
    video = VideoAgent()
    print("[MAIN] ✅ Video Agent initialized")
except Exception as e:
    print(f"[MAIN] ⚠️ Video Agent init failed: {e}")
    video = None

try:
    platform = PlatformAgent()
    print("[MAIN] ✅ Platform Agent initialized")
except Exception as e:
    print(f"[MAIN] ⚠️ Platform Agent init failed: {e}")
    platform = None

try:
    analytics = AnalyticsAgent()
    print("[MAIN] ✅ Analytics Agent initialized")
except Exception as e:
    print(f"[MAIN] ⚠️ Analytics Agent init failed: {e}")
    analytics = None

try:
    memory = MemoryManager()
    print("[MAIN] ✅ Memory Manager initialized")
except Exception as e:
    print(f"[MAIN] ⚠️ Memory Manager init failed: {e}")
    memory = None

# Request Models
class GrowthRequest(BaseModel):
    auto: bool = True

class ManualUploadRequest(BaseModel):
    title: str
    description: str
    platform: str
    language: str
    category: str
    tags: List[str]

# CEO DAILY 3 VIDEOS WORKFLOW
@app.post("/daily-3-videos")
async def create_daily_3_videos():
    """Complete Autonomous Daily Cycle"""
    try:
        if not ceo:
            return {
                'status': 'error',
                'message': 'CEO Agent not initialized. Check GROQ_API_KEY secret.',
                'videos_planned': 0,
                'videos_created': 0,
                'details': []
            }
        
        # 1. CEO Plans 3 Daily Videos
        daily_plan = ceo.plan_daily_3_videos()
        
        results = []
        
        # 2. Execute for Each of 3 Videos
        for video_plan in daily_plan.get('daily_plan', []):
            try:
                # 3. Check Uniqueness (Memory)
                if memory:
                    is_unique = memory.check_topic_uniqueness(
                        video_plan['topic'],
                        video_plan['platform']
                    )
                else:
                    is_unique = True
                
                if not is_unique:
                    results.append({
                        'video_number': video_plan['video_number'],
                        'topic': video_plan['topic'],
                        'status': 'skipped',
                        'reason': 'Topic already posted recently'
                    })
                    continue
                
                # 4. Write Human Script
                if content:
                    script = content.write_script(
                        topic=video_plan['topic'],
                        platform=video_plan['platform'],
                        language=video_plan['language']
                    )
                else:
                    script = {'script': 'Mock script', 'platform': video_plan['platform'], 'language': video_plan['language']}
                
                # 5. Create Video
                if video:
                    video_result = video.create_avatar_video(
                        script=script['script'],
                        language=video_plan['language']
                    )
                else:
                    video_result = {'status': 'mock', 'url': ''}
                
                # 6. Upload to Platform
                if platform:
                    if video_plan['platform'] == 'YouTube':
                        payload = platform.prepare_youtube(script, video_result.get('url', ''))
                        upload_result = platform.upload_youtube(payload)
                    else:
                        payload = platform.prepare_instagram(script, video_result.get('url', ''))
                        upload_result = platform.upload_instagram(payload)
                else:
                    upload_result = {'status': 'mock', 'platform': video_plan['platform']}
                
                # 7. Store in Memory (Learning)
                if memory:
                    memory.save_posted_topic(
                        topic=video_plan['topic'],
                        platform=video_plan['platform'],
                        language=video_plan['language']
                    )
                    
                    memory.save_auto_post({
                        'topic': video_plan['topic'],
                        'platform': video_plan['platform'],
                        'language': video_plan['language'],
                        'category': video_plan.get('category', 'General'),
                        'script': script.get('script', ''),
                        'video': video_result,
                        'upload_result': upload_result,
                        'reason': video_plan.get('reason', ''),
                        'target_views': video_plan.get('target_views', 0),
                        'video_number': video_plan['video_number']
                    })
                
                results.append({
                    'video_number': video_plan['video_number'],
                    'topic': video_plan['topic'],
                    'platform': video_plan['platform'],
                    'language': video_plan['language'],
                    'status': upload_result.get('status', 'unknown'),
                    'reason': video_plan.get('reason', '')
                })
                
            except Exception as e:
                results.append({
                    'video_number': video_plan.get('video_number', 'unknown'),
                    'topic': video_plan.get('topic', 'unknown'),
                    'error': str(e)
                })
        
        return {
            'status': 'success',
            'videos_planned': len(daily_plan.get('daily_plan', [])),
            'videos_created': len([r for r in results if r.get('status') not in ['skipped', 'error']]),
            'details': results,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# MANUAL UPLOAD ENDPOINT
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
    """Manual Video Upload"""
    try:
        # Save video file
        file_path = f"storage/uploads/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{video_file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(video_file.file, buffer)
        
        # Prepare for platform
        tags_list = [tag.strip() for tag in tags.split(',')]
        
        if platform.lower() == 'youtube':
            payload = {
                'title': title,
                'description': description,
                'tags': tags_list,
                'category': category,
                'language': language,
                'video_path': file_path
            }
            upload_result = platform.upload_youtube(payload) if platform else {'status': 'mock'}
        else:
            payload = {
                'caption': f"{title}\n\n{description}",
                'hashtags': tags_list,
                'language': language,
                'video_path': file_path
            }
            upload_result = platform.upload_instagram(payload) if platform else {'status': 'mock'}
        
        # Store in Memory
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

# ANALYTICS ENDPOINT (With Error Handling)
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

# POSTS ENDPOINT (With Error Handling)
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

# HEALTH ENDPOINT
@app.get("/health")
async def health():
    return {
        'status': 'online',
        'ceo': 'active' if ceo else 'inactive',
        'daily_videos': '3 per day',
        'manual_upload': 'enabled',
        'memory': 'mock' if (memory and memory.use_mock) else 'mongodb',
        'goal': 'Maximize Views, Subs, Followers',
        'agents': {
            'ceo': 'ready' if ceo else 'not initialized',
            'content': 'ready' if content else 'not initialized',
            'video': 'ready' if video else 'not initialized',
            'platform': 'ready' if platform else 'not initialized',
            'analytics': 'ready' if analytics else 'not initialized'
        }
    }

# Background Automation (3 Videos Daily at 9 AM)
async def auto_scheduler():
    """Auto-post 3 videos daily at 9 AM"""
    while True:
        now = datetime.now()
        if now.hour == 9 and now.minute == 0:
            try:
                await create_daily_3_videos()
            except Exception as e:
                print(f"Scheduled post failed: {e}")
        await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    if ceo:
        asyncio.create_task(auto_scheduler())
        print("[SYSTEM] ✅ 3 Daily Videos + Manual Upload Enabled")
    else:
        print("[SYSTEM] ⚠️ CEO Agent not available. Add GROQ_API_KEY secret.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=7860)
