from time import time

from gradio import Error as GradioError

import modules.logging as log
from modules.ollama_chat import OllamaChat
from modules.host import HOST

CA_SYSTEM_PROMPT = """You are an AI language model specializing in cybersecurity and Capture The Flag (CTF) competitions. You assist users in solving challenges by providing expert guidance and step-by-step solutions. You are knowledgeable in the Cryptography CTF category, knowing Python libraries such as PyCryptodome (Crypto) and math, and tools such as sagemath and FactorDB.
## Guidelines:
1. **Understand the Challenge**:
   - Analyze the problem statement and provided materials.
   - Identify the challenge type.
2. **Provide Clear Explanations**:
   - Simplify complex concepts.
   - Use examples and analogies.
3. **Offer Step-by-Step Solutions**:
   - Guide users through solving the challenge.
   - Provide code snippets, commands, or algorithms.
   - Suggest relevant tools and techniques.
4. **Encourage Learning**:
   - Explain the rationale behind steps and methods.
5. **Stay Up-to-Date**:
   - Use the latest tools, techniques, and best practices in cybersecurity and CTFs.
   - Incorporate current trends and advancements.
## Challenge information:
You will assist the user with the following challenge (remember to pay attention to the challenge files, if any) (do NOT infer unnecessary things about the flag format; only use the flag format when necessary during method suggestion or solve script generation):
- Challenge name: <<chall_name>>
- Flag format: <<flag_format>>
- Challenge description: <<chall_desc>>
- Challenge files:"""

CA_STARTING_PROMPTS = [
    "What clues can you extract, literal or figurative, from the given challenge name, challenge description and challenge files (if any) that can be used to find a solution (DO NOT SUGGEST A SOLUTION)? Let's think step by step.",
    "Based on the given challenge and extracted clues, state and explain the technique(s) that might have been used to encrypt/obfuscate the flag. Let's think step by step.",
    "Based on the given challenge, extracted clues and possible techniques, further analyse the challenge for any vulnerabilities that you can exploit to solve the given challenge. Let's think step by step.",
    "Based on the given challenge, extracted clues possible techniques and analysed vulnerabilities, what is a possible method that can be used to solve the given challenge? Let's think step by step.",
    "Based on the given challenge, extracted clues, possible techniques, analysed vulnerabilities and suggested method, explain how you would write a script to solve the given challenge, then give me a possible solve script for the given challenge in Python. ONLY provide the explanation and given solve script in that order, and nothing else",
]


def send_message_to_crypto_autosolver(ollama_chat, history, message):
    conv_no_tokens = f"{ollama_chat.conv_no_tokens}/{ollama_chat.ctx_window} ({round((ollama_chat.conv_no_tokens/ollama_chat.ctx_window)*100, 2)}%)"
    history.append([message, None])
    ollama_chat.append_message("user", message)
    yield history, conv_no_tokens

    start_time = time()
    res = ollama_chat.invoke_and_append_generated_message(stream=True)
    first_token_recvd = False
    for res_str in res:
        if not first_token_recvd:
            log.log_info(
                "Method Suggestor",
                f"Received first token in {round(time()-start_time, 2)}s",
            )
            first_token_recvd = True
        history[-1][1] = res_str
        yield history, conv_no_tokens
    end_time = time()
    log.log_info(
        "Method Suggestor", f"Generated response in {round(end_time-start_time, 2)}s"
    )
    conv_no_tokens = f"{ollama_chat.conv_no_tokens}/{ollama_chat.ctx_window} ({round((ollama_chat.conv_no_tokens/ollama_chat.ctx_window)*100, 2)}%)"
    yield history, conv_no_tokens


def crypto_autosolver(
    autosolver_model,
    chall_name,
    flag_format,
    chall_desc,
    chall_filepaths,
    chat_history,
):
    chat_history = []
    if not (chall_name and flag_format and chall_desc):
        raise GradioError(
            'Please provide "Challenge name", "Flag format", and "Challenge description"'
        )

    system_prompt = (
        CA_SYSTEM_PROMPT.replace("<<chall_name>>", chall_name)
        .replace("<<flag_format>>", flag_format)
        .replace("<<chall_desc>>", chall_desc)
    )
    if chall_filepaths:
        for fp in chall_filepaths:
            with open(fp, "r") as f:
                system_prompt += f"\n###<{fp}>\n{f.read()}"
    else:
        system_prompt += " Nil"

    ollama_chat = OllamaChat(HOST, autosolver_model, system_prompt)

    for prompt in CA_STARTING_PROMPTS:
        for history, conv_token_frac in send_message_to_crypto_autosolver(
            ollama_chat, chat_history, prompt
        ):
            chat_history = history
            yield history, conv_token_frac

    yield history, conv_token_frac
