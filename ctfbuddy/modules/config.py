from os import path
import configparser

from gradio import Error as GradioError

CONFIG_PATH = config_path = path.join(
    path.dirname(path.dirname(path.dirname(__file__))), "config.ini"
)

def get_config():
    if not path.exists(CONFIG_PATH):
        return {
            "server_name": '',
            "server_port": '',
            "ollama_server_url": '',
            "google_api_key": '',
            "google_prog_search_engine_id": '',
            "huggingface_user_access_token": '',
        }
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    server_name = config.get("Server", "server_name")
    server_port = config.get("Server", "server_port")
    ollama_server_url = config.get("Server", "ollama_server_url")

    google_api_key = config.get("Keys_and_IDs", "google_api_key")
    google_prog_search_engine_id = config.get(
        "Keys_and_IDs", "google_prog_search_engine_id"
    )
    huggingface_user_access_token = config.get(
        "Keys_and_IDs", "huggingface_user_access_token"
    )

    return {
        "server_name": server_name,
        "server_port": server_port,
        "ollama_server_url": ollama_server_url,
        "google_api_key": google_api_key,
        "google_prog_search_engine_id": google_prog_search_engine_id,
        "huggingface_user_access_token": huggingface_user_access_token,
    }

def gradio_assert_config_exists():
    conf = get_config()
    if not (conf['server_url'] and conf["google_api_key"] and conf["google_prog_search_engine_id"] and conf["huggingface_user_access_token"]):
        raise GradioError('Config not found! Please configure CTFBuddy before running any autosolvers!')

def update_config(server_name, server_port, ollama_server_url, google_api_key, google_prog_search_engine_id, huggingface_user_access_token):
    config = configparser.ConfigParser()

    config["Server"] = {
        "server_name": server_name,
        "server_port": server_port,
        "ollama_server_url": ollama_server_url
    }

    config["Keys_and_IDs"] = {
        "google_api_key": google_api_key,
        "google_prog_search_engine_id": google_prog_search_engine_id,
        "huggingface_user_access_token": huggingface_user_access_token,
    }

    with open(CONFIG_PATH, "w") as configfile:
        config.write(configfile)
