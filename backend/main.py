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
app = FastAPI(title="AI Free Social Media Office - 3 Daily Videos")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create storage directory for manual uploads
os.makedirs('storage/uploads', exist_ok=True)

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

class ManualUploadRequest(BaseModel):
    title: str
    description: str
    platform: str
    language: str
    category: str
    tags: List[str]

# CEO DAILY 3 VIDEOS WORKFLOW (PDF Architecture)
@app.post("/daily-3-videos")
async def create_daily_3_videos():
    """
    Complete Autonomous Daily Cycle:
    1. CEO Plans 3 Videos
    2. Content Agent Writes 3 Scripts
    3. Video Agent Creates 3 Videos
    4. Platform Agent Uploads All 3
    5. Memory Stores & Learns
    """
    
    # 1. CEO Plans 3 Daily Videos
    daily_plan = ceo.plan_daily_3_videos()
    
    results = []
    
    # 2. Execute for Each of 3 Videos
    for video_plan in daily_plan.get('daily_plan', []):
        try:
            # 3. Check Uniqueness (Memory)
            is_unique = memory.check_topic_uniqueness(
                video_plan['topic'],
                video_plan['platform']
            )
            
            if not is_unique:
                results.append({
                    'video_number': video_plan['video_number'],
                    'topic': video_plan['topic'],
                    'status': 'skipped',
                    'reason': 'Topic already posted recently'
                })
                continue
            
            # 4. Write Human Script
            script = content.write_script(
                topic=video_plan['topic'],
                platform=video_plan['platform'],
                language=video_plan['language']
            )
            
            # 5. Create Video
            video_result = video.create_avatar_video(
                script=script['script'],
                language=video_plan['language']
            )
            
            # 6. Upload to Platform
            if video_plan['platform'] == 'YouTube':
                payload = platform.prepare_youtube(script, video_result.get('url', ''))
                upload_result = platform.upload_youtube(payload)
            else:
                payload = platform.prepare_instagram(script, video_result.get('url', ''))
                upload_result = platform.upload_instagram(payload)
            
            # 7. Store in Memory (Learning)
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
                'script': script['script'],
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
        'videos_created': len([r for r in results if r.get('status') != 'skipped']),
        'details': results,
        'timestamp': datetime.now().isoformat()
    }

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
    """Manual Video Upload (User uploads their own video)"""
    
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
            upload_result = platform.upload_youtube(payload)
        else:
            payload = {
                'caption': f"{title}\n\n{description}",
                'hashtags': tags_list,
                'language': language,
                'video_path': file_path
            }
            upload_result = platform.upload_instagram(payload)
        
        # Store in Memory
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
        
        # Save topic to avoid auto-duplicate
        memory.save_posted_topic(title, platform, language)
        
        return {
            'status': 'success',
            'message': 'Video uploaded successfully',
            'upload_result': upload_result,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics")
async def get_analytics():
    """Get Dashboard Analytics (Auto + Manual)"""
    return analytics.generate_dashboard_data()

@app.get("/posts")
async def get_posts(limit: int = 50):
    """Get All Posts (Auto + Manual)"""
    return memory.get_all_posts(limit)

@app.get("/health")
async def health():
    return {
        'status': 'online',
        'ceo': 'active',
        'daily_videos': '3 per day',
        'manual_upload': 'enabled',
        'goal': 'Maximize Views, Subs, Followers',
        'agents': {
            'ceo': 'ready',
            'content': 'ready',
            'video': 'ready',
            'platform': 'ready',
            'analytics': 'ready'
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
    asyncio.create_task(auto_scheduler())
    print("[SYSTEM] 3 Daily Videos + Manual Upload Enabled")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=7860)
