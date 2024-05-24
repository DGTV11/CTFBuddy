import gradio as gr


def log_info(module, text, debug_only=False):
    if not debug_only:
        gr.Info(text)
        print(f"{module} (INFO): {text}")
    else:
        print(f"{module} (INFO) (DEBUG ONLY): {text}")


def log_warning(module, text, debug_only=False):
    if not debug_only:
        gr.Warning(text)
        print(f"{module} (WARNING): {text}")
    else:
        print(f"{module} (WARNING) (DEBUG ONLY): {text}")
