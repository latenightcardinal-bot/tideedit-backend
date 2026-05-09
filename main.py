from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
import os
import shutil
import uuid

from moviepy.editor import VideoFileClip, concatenate_videoclips

app = FastAPI()

# 🌐 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📁 STORAGE
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 🧠 CORE STATE
projects = {}

# 🌍 YARD SYSTEM
yard = {
    "posts": [],
    "leaderboard": []
}

# 🎮 CREATOR SYSTEM
creators = {}


# -------------------------
# 🧠 CREATOR INIT
# -------------------------
@app.post("/creator/init")
def init_creator(user: str = Form(...)):

    if user not in creators:
        creators[user] = {
            "xp": 0,
            "level": 1,
            "rank": "BEGINNER",
            "unlocks": []
        }

    return creators[user]


# 📈 XP SYSTEM (REAL USER SUPPORT)
def add_xp(user: str, amount: int):

    if user not in creators:
        creators[user] = {
            "xp": 0,
            "level": 1,
            "rank": "BEGINNER",
            "unlocks": []
        }

    creators[user]["xp"] += amount
    xp = creators[user]["xp"]

    if xp > 500:
        creators[user]["level"] = 5
        creators[user]["rank"] = "TEACHER"
    elif xp > 250:
        creators[user]["level"] = 4
        creators[user]["rank"] = "ELITE"
    elif xp > 100:
        creators[user]["level"] = 3
        creators[user]["rank"] = "PRO"
    elif xp > 50:
        creators[user]["level"] = 2
        creators[user]["rank"] = "ADVANCED"


# 🎯 CREATE PROJECT
@app.post("/project/create")
def create_project():
    project_id = str(uuid.uuid4())

    projects[project_id] = {
        "media_bins": {
            "A_ROLL": [],
            "B_ROLL": [],
            "TALKING_HEAD": [],
            "SCREEN_RECORDING": [],
            "STOCK": [],
            "CUSTOM": {}
        },
        "timeline": [],
        "state": "BENCH"
    }

    return {"project_id": project_id}


# 📤 UPLOAD
@app.post("/project/{project_id}/upload")
async def upload_video(
    project_id: str,
    file: UploadFile = File(...),
    bin_name: str = Form("A_ROLL"),
    user: str = Form("guest")
):

    if project_id not in projects:
        return {"error": "Project not found"}

    file_id = str(uuid.uuid4())
    path = f"{UPLOAD_FOLDER}/{file_id}_{file.filename}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    media_item = {
        "id": file_id,
        "path": path,
        "name": file.filename,
        "bin": bin_name
    }

    projects[project_id]["media_bins"][bin_name].append(media_item)

    # 🧠 XP GAIN
    add_xp(user, 10)

    return {"file_id": file_id}


# ✂️ TIMELINE
@app.post("/project/{project_id}/timeline")
def add_to_timeline(
    project_id: str,
    file_id: str = Form(...),
    user: str = Form("guest")
):

    if project_id not in projects:
        return {"error": "Project not found"}

    clip = None

    for bin_group in projects[project_id]["media_bins"].values():
        if isinstance(bin_group, list):
            clip = next((c for c in bin_group if c["id"] == file_id), None)
            if clip:
                break

    if not clip:
        return {"error": "Clip not found"}

    projects[project_id]["timeline"].append(clip)
    projects[project_id]["state"] = "EDIT"

    add_xp(user, 5)

    return {"message": "Added to timeline"}


# 🎬 RENDER
@app.post("/project/{project_id}/render")
def render(project_id: str, user: str = Form("guest")):

    if project_id not in projects:
        return {"error": "Project not found"}

    timeline = projects[project_id]["timeline"]

    if not timeline:
        return {"error": "No clips"}

    clips = [VideoFileClip(c["path"]) for c in timeline]
    final = concatenate_videoclips(clips)

    output_path = f"{OUTPUT_FOLDER}/final_{project_id}.mp4"
    final.write_videofile(output_path)

    add_xp(user, 25)

    return FileResponse(output_path, media_type="video/mp4")


# 🧠 LENS AI
@app.post("/project/{project_id}/lens/analyze")
def lens_analyze(project_id: str, user: str = Form("guest")):

    if project_id not in projects:
        return {"error": "Project not found"}

    add_xp(user, 20)

    return {
        "hook_strength": 82,
        "pacing": "fast",
        "fx": ["zoom", "motion blur"],
        "fonts": ["Bebas Neue", "Anton"],
        "teaching": "Cut faster in first 2 seconds"
    }


# 🔴 LIVE AI
@app.post("/project/{project_id}/live/analyze")
def live_analyze(project_id: str, user: str = Form("guest")):

    if project_id not in projects:
        return {"error": "Project not found"}

    add_xp(user, 15)

    return {
        "live_feedback": {
            "pacing": "slightly slow",
            "fix": "increase cut frequency"
        },
        "viral_score": 74
    }


# 🌍 YARD POST
@app.post("/yard/post")
def create_post(user: str = Form(...), content: str = Form(...)):

    post = {
        "id": str(uuid.uuid4()),
        "user": user,
        "content": content,
        "likes": 0
    }

    yard["posts"].append(post)
    return post


# 📡 FEED
@app.get("/yard/feed")
def get_feed():
    return {
        "feed": sorted(yard["posts"], key=lambda x: x["likes"], reverse=True)
    }


# ❤️ LIKE
@app.post("/yard/like/{post_id}")
def like_post(post_id: str):

    for post in yard["posts"]:
        if post["id"] == post_id:
            post["likes"] += 1
            return post

    return {"error": "Not found"}


# 🧭 BASE44 SYSTEM MAP (IMPORTANT FOR UI LINKING)
@app.get("/system/map")
def system_map():

    return {
        "project": {
            "create": "/project/create",
            "upload": "/project/{id}/upload",
            "timeline": "/project/{id}/timeline",
            "render": "/project/{id}/render"
        },
        "ai": {
            "lens": "/project/{id}/lens/analyze",
            "live": "/project/{id}/live/analyze"
        },
        "social": {
            "feed": "/yard/feed",
            "post": "/yard/post",
            "like": "/yard/like/{id}"
        },
        "creator": {
            "init": "/creator/init",
            "status": "/creator/status"
        }
    }