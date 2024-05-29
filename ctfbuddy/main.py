import gradio as gr

from modules.autosolver_categories.crypto_autosolver import crypto_autosolver

if __name__ == "__main__":
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
                    components=[ca_chall_name, ca_flag_format, ca_chall_desc, ca_chall_filepaths],
                )
                ca_run_btn = gr.Button(value="Solve!")

            ca_autosolver_model = gr.Dropdown(
                ["llama3", "openchat", "mistral", "phi3"], label="Model:", value="mistral"
            )
            
            with gr.Column():
                ca_used_token_info = gr.Textbox(
                    label="[Used tokens]/[Context window] ([Used token percentage])"
                )
                ca_chatbox = gr.Chatbot(label="Output")

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

    print("Launching...")
    ctfbuddy.queue()
    ctfbuddy.launch()
