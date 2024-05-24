from os import path
import configparser

if __name__ == "__main__":
    config = configparser.ConfigParser()

    server_url = (
        input(
            "Please input Ollama server url (Default http://127.0.0.1:11434): "
        ).strip()
        or "http://127.0.0.1:11434"
    )
    config["Server"] = {"server_url": server_url}

    google_api_key = input("Please input Google API Key: ").strip()
    google_prog_search_engine_id = input(
        "Please input Google Programmable Search Engine ID: "
    ).strip()
    huggingface_user_access_token = input(
        "Please input Hugging Face User Access Token: "
    ).strip()

    config["Keys_and_IDs"] = {
        "google_api_key": google_api_key,
        "google_prog_search_engine_id": google_prog_search_engine_id,
        "huggingface_user_access_token": huggingface_user_access_token,
    }

    with open(path.join(path.dirname(__file__), "config.ini"), "w") as configfile:
        config.write(configfile)
