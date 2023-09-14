import os

user = "server-obeli"
ip = "192.168.178.68"

files = []
for file in os.listdir("./data"):
    if file.split(".")[-1] != "mp4":
        continue
    abs_path = os.path.abspath(os.path.join("./data", file))
    files.append(abs_path)

for file in files:
    allow_compression = True
    if not allow_compression:
        pscp_command = f"""pscp -pw "obeli" "{file}" {user}@{ip}:"/home/{user}/fstream/data" """
    else:
        pscp_command = f"""pscp -pw "obeli" -C "{file}" {user}@{ip}:"/home/{user}/fstream/data" """
    print(pscp_command)
    os.system(pscp_command)