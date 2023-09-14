import os
import requests
import json
import imdb
ia = imdb.IMDb()

path = "./data"

extensions = ["mp4", "avi", "mkv", "mov", "wmv", "flv", "webm", "mpg", "mpeg", "m4v"]


def get_metadata(move_name: str):
    
    raw = ia.search_movie(move_name)
    if len(raw) == 0:
        print("No results found for " + move_name)
        return None
    else:
        movie = raw[0]
    
    
    
    
    movie_dict = {
        "title": "",
        "year": "",
        "genre": "",
        "director": "",
        "writer": "",
        "actors": "",
        "plot": "",
        "rating": "",
        "runtime_minutes": "",
        "cover_url": ""
    }
    
    for key, val in movie.data.items():
        key = key.replace(" ", "_")
        if key in movie_dict:
            movie_dict[key] = val
    
    out_dict = {}
    for key, val in movie_dict.items():
        if val != "":
            out_dict[key] = val
    
    return out_dict
        
    
total_json = {
    "movies": []
}

for file in os.listdir(path):
    # {id}_{title including _}.{extension}
    title = " ".join(file.split("_")[1:])
    title = " ".join(title.split(".")[:-1])
    ext = file.split(".")[-1]
    print(title)
    if ext in extensions:
        r = get_metadata(title)
        id = file.split("_")[0]
        r["id"] = id
        total_json["movies"].append(r)

os.remove("./data/_metadata.json")

with open("./data/_metadata.json", "w") as f:
    json.dump(total_json, f, indent=4)
    
    