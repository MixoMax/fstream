import os

port = 80
expose_external = True

os.system("uvicorn main:app --host " + ("0.0.0.0" if expose_external else "127.0.0.1") + " --port " + str(port))