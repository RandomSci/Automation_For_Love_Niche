from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import subprocess
import time
from datetime import datetime

app = FastAPI(title="Viral Shorts Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

current_job = {
    "status": "idle",
    "progress": 0,
    "output": None,
    "error": None,
    "started_at": None
}

@app.get("/")
def root():
    return {
        "service": "Viral Shorts Generator",
        "status": "running",
        "endpoints": {
            "POST /generate": "Start video generation (uses new_love.mp3 from repo)",
            "GET /status": "Check generation status",
            "GET /download": "Download completed video"
        }
    }

@app.post("/generate")
async def generate_video(background_tasks: BackgroundTasks):
    """
    Start video generation using the new_love.mp3 already in the repo
    """
    global current_job
    
    if current_job["status"] == "processing":
        return {
            "message": "Already processing a video",
            "status": current_job["status"],
            "progress": current_job["progress"]
        }
    
    if not os.path.exists("Audio_Voice/new_love.mp3"):
        raise HTTPException(400, "Audio file not found: Audio_Voice/new_love.mp3")

    current_job = {
        "status": "processing",
        "progress": 0,
        "output": None,
        "error": None,
        "started_at": datetime.now().isoformat()
    }
    
    background_tasks.add_task(process_video)
    
    return {
        "message": "Video generation started",
        "status": "processing",
        "check_status": "/status",
        "download_when_ready": "/download"
    }

def process_video():
    """Run the main.py script"""
    global current_job
    
    try:
        current_job["progress"] = 10
        
        for old_file in ["new_love.mp4", "new_love_cta.mp4", "subtitles.srt"]:
            if os.path.exists(old_file):
                os.remove(old_file)
        
        current_job["progress"] = 20
        
        print("🎬 Starting video generation...")
        
        result = subprocess.run(
            ["python", "main.py"],
            capture_output=True,
            text=True,
            timeout=600 
        )
        
        if result.returncode != 0:
            raise Exception(f"Script failed: {result.stderr}")
        
        print("✅ Script completed!")
        print(result.stdout)
        
        current_job["progress"] = 90
        
        if os.path.exists("new_love_cta.mp4"):
            current_job["status"] = "completed"
            current_job["progress"] = 100
            current_job["output"] = "new_love_cta.mp4"
            print(f"✅ Video ready: new_love_cta.mp4")
        else:
            raise Exception("Output video not found")
        
    except subprocess.TimeoutExpired:
        current_job["status"] = "error"
        current_job["error"] = "Processing timeout (>10 min)"
        print("❌ Timeout!")
        
    except Exception as e:
        current_job["status"] = "error"
        current_job["error"] = str(e)
        print(f"❌ Error: {e}")

@app.get("/status")
def check_status():
    """Check the current job status"""
    return {
        "status": current_job["status"],
        "progress": current_job["progress"],
        "error": current_job["error"],
        "started_at": current_job["started_at"],
        "ready_for_download": current_job["status"] == "completed"
    }

@app.get("/download")
def download_video():
    """Download the generated video"""
    if current_job["status"] != "completed":
        raise HTTPException(400, f"Video not ready. Status: {current_job['status']}")
    
    if not current_job["output"] or not os.path.exists(current_job["output"]):
        raise HTTPException(404, "Video file not found")
    
    return FileResponse(
        current_job["output"],
        media_type="video/mp4",
        filename=f"viral_video_{int(time.time())}.mp4"
    )

@app.post("/webhook/github")
async def github_webhook(background_tasks: BackgroundTasks):
    """
    GitHub webhook endpoint - auto-generates video when repo updates
    """
    print("🔔 GitHub webhook received!")
    
    if current_job["status"] != "processing":
        background_tasks.add_task(process_video)
        return {"message": "Auto-generation triggered"}
    
    return {"message": "Already processing"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)