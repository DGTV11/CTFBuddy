from os import path
import configparser


def get_config():
    config = configparser.ConfigParser()
    config_path = path.join(
        path.dirname(path.dirname(path.dirname(__file__))), "config.ini"
    )
    config.read(config_path)

    server_url = config.get("Server", "server_url")
    google_api_key = config.get("Keys_and_IDs", "google_api_key")
    google_prog_search_engine_id = config.get(
        "Keys_and_IDs", "google_prog_search_engine_id"
    )
    huggingface_user_access_token = config.get(
        "Keys_and_IDs", "huggingface_user_access_token"
    )

    return {
        "server_url": server_url,
        "google_api_key": google_api_key,
        "google_prog_search_engine_id": google_prog_search_engine_id,
        "huggingface_user_access_token": huggingface_user_access_token,
    }


CONFIG = get_config()
