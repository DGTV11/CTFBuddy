import gradio as gr

import modules.generate_method_suggestions as gen_mtsu

if __name__ == "__main__":
    with gr.Blocks(
        theme=gr.themes.Default(primary_hue="red"),
        analytics_enabled=False,
        title="CTFBuddy",
    ) as studyCopilot:
        gr.Markdown(
            """
		# CTFBuddy
        """
        )

        with gr.Tab("Method Suggestor"):
            chall_name = gr.Textbox(label="Challenge name:")
            flag_format = gr.Textbox(label="Flag format:")
            chall_desc = gr.Textbox(label="Challenge description:")
            chall_filepaths = gr.File(
                label="Challenge files (text):",
                file_count="multiple",
                file_types=["text"],
            )

            with gr.Row():
                clear_mtsu_in_btn = gr.ClearButton(
                    value="Clear inputs",
                    components=[chall_name, flag_format, chall_desc, chall_filepaths],
                )
                generate_mtsu_btn = gr.Button(value="Generate method suggestions")

            method_suggestor_model = gr.Dropdown(
                ["llama3", "openchat", "mistral", "phi3"], label="Model:", value="phi3"
            )
            """
            with gr.Accordion("Extracted clues", open=True):
                extracted_clues = gr.Markdown()
            with gr.Accordion("Technique explanation", open=True):
                technique_explanation = gr.Markdown()
            with gr.Accordion("Suggested method", open=True):
                suggested_method = gr.Markdown()
            with gr.Accordion("Suggested solve script", open=True):
                suggested_solve_script = gr.Markdown()
            """
            with gr.Column():
                conv_token_frac = gr.Textbox(
                    label="[Used tokens]/[Context window] ([Used token percentage])"
                )
                chatbot = gr.Chatbot(label="Output")

            """
            clear_mtsu_out_btn = gr.ClearButton(
                value="Clear outputs",
                components=[extracted_clues, technique_explanation, suggested_method, suggested_solve_script],
            )
            """

        """
        generate_mtsu_btn.click(
            fn=gen_mtsu.generate_mtsu,
            inputs=[method_suggestor_model, chall_name, flag_format, chall_desc, chall_filepaths],
            outputs=[extracted_clues, technique_explanation, suggested_method, suggested_solve_script],
        )
        """
        generate_mtsu_btn.click(
            fn=gen_mtsu.generate_mtsu,
            inputs=[
                method_suggestor_model,
                chall_name,
                flag_format,
                chall_desc,
                chall_filepaths,
                chatbot,
            ],
            outputs=[chatbot, conv_token_frac],
        )

    print("Launching...")
    studyCopilot.queue()
    studyCopilot.launch()
