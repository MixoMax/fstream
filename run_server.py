import os

port = 80
expose_external = True

#if windows
if os.name == "nt":
    os.system("uvicorn main:app --host " + ("0.0.0.0" if expose_external else "127.0.0.1") + " --port " + str(port))
#if linux
else:
    os.system("sudo python3 -m uvicorn main:app --host " + ("0.0.0.0" if expose_external else "127.0.0.1") + " --port " + str(port))