from fastapi import FastAPI, APIRouter, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles, StaticFiles
import Levenshtein as lev
import os
import json


os.chdir(os.path.dirname(__file__))

app = FastAPI()


#streaming video
#sort of like a plex server

# - [ ] search(query) -> list of video ids
# - [ ] get_video(id) -> get simple html page with video
# - [ ] get_metadata(id) -> get metadata for video
# - [ ] upload_video(video) -> upload video to server
# - [ ] upload_metadata(metadata) -> upload metadata to server


def get_video(id):
    id = str(id)
    extensions = ["mp4", "mkv", "avi", "mov", "wmv", "flv", "webm", "mpg", "mpeg", "m4v"]
    for file in os.listdir("./data"):
        #{id}_{title}.{extension}
        file_id = file.split("_")[0]
        if file_id == id:
            extension = file.split(".")[-1]
            if extension in extensions:
                return "./data/" + file
    return None



def get_id(title):
    index_path = "./data/_metadata.json"
    index_dict = {} # title: id
    
    with open(index_path, "r") as f:
        temp = json.load(f)
        for movie in temp["movies"]:
            index_dict[movie["title"]] = movie["id"]
    
    return index_dict.get(title, None)

def get_title(id):
    index_path = "./data/_metadata.json"
    index_dict = {} # id: title
    
    with open(index_path, "r") as f:
        temp = json.load(f)
        for movie in temp["movies"]:
            index_dict[movie["id"]] = movie["title"]
    
    return index_dict.get(id, None)

def get_metadata(id):
    pass

def upload_video(video):
    pass

def upload_metadata(metadata):
    pass



def search(query):
    index_path = "./data/_metadata.json"
    index_dict = {} # title: id
    
    #metadata index=
    """{
    "movies": [
      {
        "id": "integer",
        "title": "string",
        #everything else is optional
        "year": "integer",
        "genre": ["string"],
        "director": "string",
        "writers": ["string"],
        "actors": ["string"],
        "plot": "string",
        "rating": "float",
        "runtime_minutes": "integer",
    ]
  }"""
    
    #we only need title and id
    with open(index_path, "r") as f:
        temp = json.load(f)
        for movie in temp["movies"]:
            index_dict[movie["title"]] = movie["id"]

    
    #search
    
    #calculate distance between query and each title
    #return top 10 results
    
    distances = {}
    for title in index_dict.keys():
        #lower penalty for adding
        distances[title] = lev.distance(query, title, weights=(0.5, 1, 1))
    
    #sort by distance
    sorted_distances = sorted(distances.items(), key=lambda x: x[1])
    if len(sorted_distances) > 10:
        sorted_distances = sorted_distances[:10]
    
    
    ids = []
    for title, distance in sorted_distances:
        ids.append(index_dict[title])
    
    return ids
    

@app.get("/")
def read_root():
    html_path = "./static/index.html"
    return FileResponse(html_path)

@app.get("/static/{path}")
def read_static(path):
    static_path = "./static/" + path
    return FileResponse(static_path)

@app.get("/video/{id}")
def read_video(id):
    #return static file
    video_path = get_video(id)
    if video_path is None:
        return "Video not found", 404
    return FileResponse(video_path)

@app.get("/search")
def read_search(q: str, mode: str = "id"):
    #/search?q=movie+title&mode=id
    
    if mode == "id":
        return search(q)
    elif mode == "title":
        r = search(q)
        titles = []
        for id in r:
            titles.append(get_title(id))
        return titles
    elif mode == "both-title":
        r = search(q)
        out_dict = {} # title: id
        for id in r:
            out_dict[get_title(id)] = id
        return out_dict
    elif mode == "both-id":
        r = search(q)
        out_dict = {} # id: title
        for id in r:
            out_dict[id] = get_title(id)
        return out_dict
    
    #TODO
    # - all metadata
    
    else:
        return "Invalid mode", 501

@app.get("/search_results")
def read_search_results(q: str):
    #/search_results?q=movie+title&mode=id
    
    results = read_search(q, mode="both-title")
    
    html = "<html><body>"
    
    for title, id in results.items():
        html += f'<a href="/video/{id}">{title}</a><br>'
    
    html += "</body></html>"
    
    return HTMLResponse(content=html, status_code=200)
    