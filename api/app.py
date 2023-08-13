from typing import Dict, Optional
import os
from pytube import YouTube
from youtubesearchpython import VideosSearch
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse, FileResponse

app = FastAPI(
    # root_path="/testms"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        return JSONResponse(
                {"detail": f"An unexpected error occurred during report extraction. Error: {e}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

def search_ytb(query):
    searchs = VideosSearch(query)
    searchs = searchs.result()["result"]
    return [{
        "type": s["type"],
        "title": s["title"],
        "publishedTime": s["publishedTime"],
        "duration": s["duration"],
        "viewCount": s["viewCount"]["text"],
        "link": s["link"]
    } for s in searchs]

@app.get("/search")
async def search(query: str):
    searchs = search_ytb(query)
    return searchs

def get_url_n_save(path):
    yt = YouTube(path)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path="src/output/")
    new_file = "src/output/m.mp3"
    os.rename(out_file, new_file)
    return new_file

@app.get("/save")
async def save(url: str):
    file = get_url_n_save(url)
    return FileResponse(file)

# Main entry point for the application.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8502
    )
