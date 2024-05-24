from os import path

import ollama

from modules.config import CONFIG

HOST_URL = CONFIG["server_url"]
HOST = ollama.Client(HOST_URL)
