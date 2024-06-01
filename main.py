from fastapi import FastAPI, APIRouter, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles, StaticFiles
import Levenshtein as lev
import os
import json
import hashlib

from config import DATA_DIR, INDEX_PATH


os.chdir(os.path.dirname(__file__))

app = FastAPI()

session_tokens = []

#streaming video
#sort of like a plex server

# - [x] search(query) -> list of video ids
# - [x] get_video(id) -> get simple html page with video
# - [x] get_metadata(id) -> get metadata for video
# - [ ] upload_video(video) -> upload video to server
# - [ ] upload_metadata(metadata) -> upload metadata to server

def get_session_token(userid, password):
    #userid is email or username
    csv_path = "./data/users.csv"
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    userid = userid.lower()
    
    user_is_valid = False
    with open(csv_path, "r") as f:
        for line in f.readlines():
            line = line.strip()
            line = line.split(",")
            if line[0].lower() == userid and line[1] == hashed_password:
                user_is_valid = True
                break
    
    if user_is_valid:
        #generate token
        token = hashlib.sha256(userid.encode()).hexdigest()
        return token
    else:
        return None

def add_user(userid, password):
    userid = userid.lower()
    csv_path = "./data/users.csv"
    with open(csv_path, "a") as f:
        f.write(f"{userid},{password}\n")

def get_video(id):
    id = str(id)
    extensions = ["mp4", "mkv", "avi", "mov", "wmv", "flv", "webm", "mpg", "mpeg", "m4v"]
    for file in os.listdir(DATA_DIR):
        #{id}_{title}.{extension}
        file_id = file.split("_")[0]
        if file_id == id:
            extension = file.split(".")[-1]
            if extension in extensions:
                #return relative path
                abs_path = os.path.join(DATA_DIR, file)
                rel_path = os.path.relpath(abs_path)
                return rel_path
    return None

def get_id(title):
    index_path = INDEX_PATH
    index_dict = {} # title: id
    
    with open(index_path, "r") as f:
        temp = json.load(f)
        for movie in temp["movies"]:
            index_dict[movie["title"]] = movie["id"]
    
    return index_dict.get(title, None)

def get_title(id):
    index_path = INDEX_PATH
    index_dict = {} # id: title
    
    with open(index_path, "r") as f:
        temp = json.load(f)
        for movie in temp["movies"]:
            index_dict[movie["id"]] = movie["title"]
    
    return index_dict.get(id, None)

def get_metadata(id):
    index_path = INDEX_PATH
    index_dict = {} # id: metadata
    
    with open(index_path, "r") as f:
        temp = json.load(f)
        for movie in temp["movies"]:
            index_dict[movie["id"]] = movie
    
    return index_dict.get(id, None)

def upload_video(video):
    pass

def upload_metadata(metadata):
    pass



def search(query):
    index_path = INDEX_PATH
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

@app.route("/login")
def read_session_token(request: Request):
    user_id = request.args.get("userid")
    password = request.args.get("password")
    session_token = get_session_token(user_id, password)
    if session_token is None:
        return "Invalid login", 401
    else:
        session_tokens.append(session_token)
        return session_token

@app.route("/register")
def read_register(request: Request):
    #/register?userid=userid&password=password
    user_id = request.args.get("userid")
    password = request.args.get("password")
    add_user(user_id, password)
    return "User added"

@app.get("/static/{path}")
def read_static(path):
    static_path = "./static/" + path
    return FileResponse(static_path)

@app.get("/video/{id}")
def read_video(id):
    video_path = get_video(id)
    if video_path is None:
        return "Video not found", 404
    return FileResponse(video_path)



@app.get("/movie/{id}")
def read_movie(id):
    video_url = f"/video/{id}"
    metadata = get_metadata(id)
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <title>{metadata["title"]}</title>
    <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
    <h1>{metadata["title"]}</h1>
    <h2>{metadata["year"]}</h2>
    
    <img src="{metadata.get("cover_url", "")}" alt="Cover image" width="300" height="400">
    
    <video width="1280" height="720" controls poster="{metadata.get("cover_url", "")}" preload="auto">
        <source src="{video_url}" type="video/mp4">
        Your browser does not support the video tag.
    </video>
    </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=200)

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
def read_search_results(q: str, mode: str = "id", session_token: str = ""):
    #/search_results?q=movie+title&mode=id&session_token=token
    
    if session_token not in session_tokens:
        return "Invalid session token", 401
    
    results = read_search(q, mode="both-title")
    
    html = "<html><body>"
    
    for title, id in results.items():
        html += f"<a href='/movie/{id}'>{title}</a><br>"
    
    html += "</body></html>"
    
    return HTMLResponse(content=html, status_code=200)

@app.get("/metadata/{id}")
def read_metadata(id):
    metadata = get_metadata(id)
    if metadata is None:
        return "Metadata not found", 404
    return metadata