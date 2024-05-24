import os

import gradio as gr

import modules.host as host_module
import modules.model_regen as mrh
import modules.generate_flashcards as gen
import modules.study_chatbot.gen_response as study_chatbot

if __name__ == "__main__":
    for file in os.listdir(os.path.join(os.path.dirname(__file__), "modelfiles")):
        print(f"Checking if the '{file}' model exists...")
        if file[0] in [".", "_"]:
            continue
        if f"{file}:latest" not in [
            model["name"] for model in host_module.HOST.list()["models"]
        ]:
            mrh.gen_model_from_modelfile(
                f"{file}",
                __file__,
                lambda: print(f"Creating the '{file}' model..."),
                lambda: print(f"'{file}' model created!"),
            )

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

        with gr.Tab("Flashcard Generator"):
            inp_cards_slides = gr.File(
                label="Slides:", file_count="multiple", file_types=[".pptx"]
            )
            inp_cards_images = gr.File(
                label="Images:",
                file_count="multiple",
                file_types=[".png", ".jpg", ".jpeg"],
            )

            inp_cards_words = gr.Textbox(label="Notes:")

            get_slides_images_checkbox = gr.Checkbox(
                label="Get images from slides", value=True
            )
            with gr.Row():
                clear_inputs_btn = gr.ClearButton(
                    components=[inp_cards_slides, inp_cards_images, inp_cards_words]
                )
                generate_cards_btn = gr.Button(value="Generate Flashcards")

            flashcards_helper_model = gr.Dropdown(
                ["phi3", "mistral"], label="Model:", value="phi3"
            )
            stop_flashcards_btn = gr.Button(value="Stop", variant="primary")
            out_cards = gr.Markdown(label="A deck of flashcards:")
            with gr.Row():
                show_markdown_btn = gr.Button(value="Show Markdown")
                clear_cards_btn = gr.ClearButton(components=[out_cards])
        with gr.Tab("Study Chatbot"):
            study_chat = gr.Chatbot()
            prompt = gr.Textbox(label="Prompt:")

            with gr.Row():
                moderate_checkbox = gr.Checkbox(label="Moderate", value=True)
                online_mode_checkbox = gr.Checkbox(label="Search web?", value=True)

            study_chatbot_model = gr.Dropdown(
                ["phi3", "mistral"], label="Model:", value="phi3"
            )

            with gr.Row():
                stop_study_chatbot_btn = gr.Button(value="Stop", variant="primary")
                clear_study_chatbot_btn = gr.ClearButton(
                    components=[prompt, study_chat]
                )

        regen_models_btn = gr.Button(value="Regenerate models", variant="secondary")

        regen_models_btn.click(
            fn=lambda: mrh.regen_models(__file__), inputs=[], outputs=[]
        )

        gen_cards_event = generate_cards_btn.click(
            fn=gen.gen_flashcards,
            inputs=[
                flashcards_helper_model,
                inp_cards_slides,
                inp_cards_images,
                inp_cards_words,
                get_slides_images_checkbox,
            ],
            outputs=[out_cards],
        )
        show_markdown_btn.click(
            fn=gen.show_markdown, inputs=[out_cards], outputs=[out_cards]
        )

        study_chatbot_submit_event = prompt.submit(
            fn=study_chatbot.gen_response,
            inputs=[
                study_chatbot_model,
                online_mode_checkbox,
                moderate_checkbox,
                prompt,
                study_chat,
            ],
            outputs=[prompt, study_chat],
        )

        stop_flashcards_btn.click(
            fn=None, inputs=None, outputs=None, cancels=[gen_cards_event]
        )
        stop_study_chatbot_btn.click(
            fn=None, inputs=None, outputs=None, cancels=[study_chatbot_submit_event]
        )

    print("Launching...")
    studyCopilot.launch()
