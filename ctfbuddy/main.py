#!/usr/bin/env python3

import argparse
import socket

import gradio as gr

from modules.autosolver_categories.crypto_autosolver import crypto_autosolver
from modules.logging import log_warning
from modules.config import get_config, update_config


def is_port_in_use(port):
    server_name = get_config()["server_name"] or "127.0.0.1"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((server_name, port)) == 0


def get_first_usable_port_from_7860():
    server_name = get_config()["server_name"] or "127.0.0.1"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        for port in range(7860, 65536):
            if s.connect_ex((server_name, port)) != 0:
                return port
        log_warning("Configuration", "No available ports from port 7650")
        return "7860"


def load_config_if_tab_is_selected(
    server_name,
    server_port,
    ollama_server_url,
    google_api_key,
    google_prog_search_engine_id,
    huggingface_user_access_token,
    evt_data: gr.SelectData,
):
    if evt_data.selected:
        prev_config = get_config()
        return (
            prev_config["server_name"],
            prev_config["server_port"],
            prev_config["ollama_server_url"],
            prev_config["google_api_key"],
            prev_config["google_prog_search_engine_id"],
            prev_config["huggingface_user_access_token"],
        )
    return (
        server_name,
        server_port,
        ollama_server_url,
        google_api_key,
        google_prog_search_engine_id,
        huggingface_user_access_token,
    )


def config_server_name_update(value):
    stripped_value = value.strip()
    if not stripped_value:
        return "127.0.0.1"
    return stripped_value


def config_ollama_server_url_update(value):
    stripped_value = value.strip()
    if not stripped_value:
        return "http://127.0.0.1:11434"
    return stripped_value


def config_server_port_update(value):
    stripped_value = value.strip()
    stripped_value_int = int(stripped_value)
    if (
        (not stripped_value.isdigit())
        or stripped_value_int < 7860
        or stripped_value_int > 65536
    ) or (get_config()["server_port"] != value and is_port_in_use(stripped_value_int)):
        return str(get_first_usable_port_from_7860())

    return stripped_value


def config_standard_update(value):
    return value.strip()


def config_validate_and_submit(
    server_name,
    server_port,
    ollama_server_url,
    google_api_key,
    google_prog_search_engine_id,
    huggingface_user_access_token,
):
    if not server_name:
        log_warning(
            "Configuration", "Unable to save configuration: Server name is required"
        )
        return

    if not server_port:
        log_warning(
            "Configuration", "Unable to save configuration: Server port is required"
        )
        return

    if not google_api_key:
        log_warning(
            "Configuration", "Unable to save configuration: Google API Key is required"
        )
        return

    if not google_prog_search_engine_id:
        log_warning(
            "Configuration",
            "Unable to save configuration: Google Programmable Search Engine ID is required",
        )
        return

    if not huggingface_user_access_token:
        log_warning(
            "Configuration",
            "Unable to save configuration: Hugging Face User Access Token is required",
        )
        return

    update_config(
        server_name,
        server_port,
        ollama_server_url,
        google_api_key,
        google_prog_search_engine_id,
        huggingface_user_access_token,
    )


parser = argparse.ArgumentParser(prog="CTFBuddy", description="A handy CTF buddy")
parser.add_argument(
    "-cw",
    "--config-writable",
    action="store_true",
    help="Allows user to write to configuration file (DO NOT USE IF YOU HOST CTFBUDDY)",
)

if __name__ == "__main__":
    args = parser.parse_args()
    config_writable = args.config_writable

    with gr.Blocks(
        theme=gr.themes.Default(primary_hue="red"),
        analytics_enabled=False,
        title="CTFBuddy",
    ) as ctfbuddy:
        gr.Markdown(
            """
		# CTFBuddy
        """
        )

        with gr.Tab("Crypto Autosolver"):
            ca_chall_name = gr.Textbox(label="Challenge name:")
            ca_flag_format = gr.Textbox(label="Flag format:")
            ca_chall_desc = gr.Textbox(label="Challenge description:")
            ca_chall_filepaths = gr.File(
                label="Challenge files (text):",
                file_count="multiple",
                file_types=["text"],
            )

            with gr.Row():
                clear_crypto_autosolver_in_btn = gr.ClearButton(
                    value="Clear inputs",
                    components=[
                        ca_chall_name,
                        ca_flag_format,
                        ca_chall_desc,
                        ca_chall_filepaths,
                    ],
                )
                ca_run_btn = gr.Button(value="Solve!")

            ca_autosolver_model = gr.Dropdown(
                ["llama3", "openchat", "mistral", "phi3"],
                label="Model:",
                value="mistral",
            )

            with gr.Column():
                ca_used_token_info = gr.Textbox(
                    label="[Used tokens]/[Context window] ([Used token percentage])"
                )
                ca_chatbox = gr.Chatbot(label="Output")

        if config_writable:
            with gr.Tab("Configuration") as config_tab:
                config_server_name = gr.Textbox(
                    label="Server name (Restart for change to take effect, default 127.0.0.1):"
                )
                config_server_port = gr.Textbox(
                    label="Server port (Restart for change to take effect, must be a number)"
                )
                config_ollama_server_url = gr.Textbox(
                    label="Ollama server url (Default http://127.0.0.1:11434):"
                )
                config_google_api_key = gr.Textbox(
                    label="Google API Key:", type="password"
                )
                config_google_prog_search_engine_id = gr.Textbox(
                    label="Google Programmable Search Engine ID: ", type="password"
                )
                config_huggingface_user_access_token = gr.Textbox(
                    label="Hugging Face User Access Token:", type="password"
                )
                config_submit_btn = gr.Button(value="Update configuration")

                config_tab.select(
                    fn=load_config_if_tab_is_selected,
                    inputs=[
                        config_server_name,
                        config_server_port,
                        config_ollama_server_url,
                        config_google_api_key,
                        config_google_prog_search_engine_id,
                        config_huggingface_user_access_token,
                    ],
                    outputs=[
                        config_server_name,
                        config_server_port,
                        config_ollama_server_url,
                        config_google_api_key,
                        config_google_prog_search_engine_id,
                        config_huggingface_user_access_token,
                    ],
                )

        ca_run_btn.click(
            fn=crypto_autosolver,
            inputs=[
                ca_autosolver_model,
                ca_chall_name,
                ca_flag_format,
                ca_chall_desc,
                ca_chall_filepaths,
                ca_chatbox,
            ],
            outputs=[ca_chatbox, ca_used_token_info],
        )

        if config_writable:
            config_server_name.change(
                fn=config_server_name_update,
                inputs=[config_server_name],
                outputs=[config_server_name],
            )
            config_server_port.change(
                fn=config_server_port_update,
                inputs=[config_server_port],
                outputs=[config_server_port],
            )
            config_ollama_server_url.change(
                fn=config_ollama_server_url_update,
                inputs=[config_ollama_server_url],
                outputs=[config_ollama_server_url],
            )
            config_google_api_key.change(
                fn=config_standard_update,
                inputs=[config_google_api_key],
                outputs=[config_google_api_key],
            )
            config_google_prog_search_engine_id.change(
                fn=config_standard_update,
                inputs=[config_google_prog_search_engine_id],
                outputs=[config_google_prog_search_engine_id],
            )
            config_huggingface_user_access_token.change(
                fn=config_standard_update,
                inputs=[config_huggingface_user_access_token],
                outputs=[config_huggingface_user_access_token],
            )
            config_submit_btn.click(
                fn=config_validate_and_submit,
                inputs=[
                    config_server_name,
                    config_server_port,
                    config_ollama_server_url,
                    config_google_api_key,
                    config_google_prog_search_engine_id,
                    config_huggingface_user_access_token,
                ],
                outputs=None,
            )

    print("Launching...")
    ctfbuddy.queue()
    ctfbuddy.launch(
        server_name=(get_config()["server_name"] or "127.0.0.1"),
        server_port=(None if not (spi := get_config()["server_port"]) else int(spi)),
    )
