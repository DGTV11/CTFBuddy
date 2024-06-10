from os import path

import ollama

from modules.config import get_config

prev_host_url = 'httlocalhost:11434'

def get_host_url():
    return get_config()["server_url"]

def get_host():
    return ollama.Client(get_host_url())
