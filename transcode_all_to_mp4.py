import os

video_extensions = ["avi", "mkv", "m4a", "mov", "mp4", "mpg", "mpeg", "wmv", "flv", "webm", "m4v"]

#transcode all files in ./data to mp4
for file in os.listdir("./data"):
    ext = file.split(".")[-1]
    if ext == "mp4":
        continue
    elif ext in video_extensions:
        print("Transcoding " + file)
        #transcode using h264
        ffmpeg_str = f"ffmpeg -i ./data/{file} -c:v libx264 -preset veryfast -pix_fmt yuv420p -r 30 -c:a copy ./data/{file.split('.')[0]}.mp4"
        os.system(ffmpeg_str)
    else:
        print("Skipping " + file)

