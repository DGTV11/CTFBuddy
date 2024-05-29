from transformers import AutoTokenizer
from tokenizers import Tokenizer

from modules.config import CONFIG

def mistral_format_system(conv):
    if not conv:
        return conv
    if conv[0]["role"] == "system":
        if len(conv) > 1:
            if conv[1]["role"] != "user":
                raise ValueError(
                    "First message after system message must be a user message"
                )
            return [
                {
                    "role": "user",
                    "content": conv[0]["content"] + " " + conv[1]["content"],
                }
            ] + conv[2:]
        return [{"role": "user", "content": conv[0]["content"]}]
    return conv

def get_tokeniser_and_context_window(model_name):
    match model_name:
        case "llama3":
            tokenizer = AutoTokenizer.from_pretrained(
                "meta-llama/Meta-Llama-3-8B",
                token=CONFIG["huggingface_user_access_token"],
            )
            ctx_window = 8192
            num_token_func = lambda text: len(tokenizer.encode(text))
            ct_num_token_func = lambda conv: len(tokenizer.apply_chat_template(conv))
        case "mistral":
            tokenizer = AutoTokenizer.from_pretrained(
                "mistralai/Mistral-7B-Instruct-v0.3",
                token=CONFIG["huggingface_user_access_token"],
            )
            ctx_window = 16384 #usually 32768 but reduced to lower RAM usage
            num_token_func = lambda text: len(tokenizer.encode(text))
            ct_num_token_func = lambda conv: len(
                tokenizer.apply_chat_template(mistral_format_system(conv))
            )
        case "openchat":
            tokenizer = AutoTokenizer.from_pretrained(
                "openchat/openchat_3.5",
                token=CONFIG["huggingface_user_access_token"],
            )
            ctx_window = 8192
            num_token_func = lambda text: len(tokenizer.encode(text))
            ct_num_token_func = lambda conv: len(tokenizer.apply_chat_template(conv))
        case "phi3":
            tokenizer = AutoTokenizer.from_pretrained(
                "microsoft/Phi-3-mini-4k-instruct",
                token=CONFIG["huggingface_user_access_token"],
            )
            ctx_window = 4096
            num_token_func = lambda text: len(tokenizer.encode(text))
            ct_num_token_func = lambda conv: len(tokenizer.apply_chat_template(conv))
        case _:
            raise ValueError(f"{modelname} is not a supported model.")

    return tokenizer, ctx_window, num_token_func, ct_num_token_func


NOMIC_EMBED_TEXT_TOKENIZER = Tokenizer.from_pretrained(
    "nomic-ai/nomic-embed-text-v1.5",
    auth_token=CONFIG["huggingface_user_access_token"],
)
