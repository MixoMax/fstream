import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

data_dir = "./data"
DATA_DIR = os.path.abspath(data_dir)
INDEX_PATH = os.path.join(DATA_DIR, "_metadata.json")