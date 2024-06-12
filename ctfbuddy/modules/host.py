from os import path

import ollama

from modules.config import get_config


def get_host_url():
    return get_config()["ollama_server_url"]


def get_host():
    return ollama.Client(get_host_url())
