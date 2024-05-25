from time import time

from gradio import Error as GradioError

import modules.logging as log
from modules.ollama_chat import OllamaChat
from modules.host import HOST

MTSU_GEN_SYSTEM_PROMPT = """You are an AI language model specializing in cybersecurity and Capture The Flag (CTF) competitions. You assist users in solving challenges by providing expert guidance and step-by-step solutions. You are knowledgeable in the following CTF categories: Pwn, Forensics, Cryptography, Web Exploitation, Reverse Engineering, Steganography, SIGINT, OSINT, Scripting, and Miscellaneous.
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
   - Offer additional resources for deeper understanding.
5. **Stay Up-to-Date**:
   - Use the latest tools, techniques, and best practices in cybersecurity and CTFs.
   - Incorporate current trends and advancements.
## Challenge information:
You will assist the user with the following challenge (remember to pay attention to the challenge files, if any) (do NOT infer unnecessary things about the flag format; only use the flag format when necessary during method suggestion or solve script generation):
- Challenge name: <<chall_name>>
- Flag format: <<flag_format>>
- Challenge description: <<chall_desc>>
- Challenge files:"""


def generate_mtsu(
    method_suggestor_model, chall_name, flag_format, chall_desc, chall_filepaths
):
    if not (chall_name and flag_format and chall_desc):
        raise GradioError(
            'Please provide "Challenge name", "Flag format", and "Challenge description"'
        )

    extracted_clues = technique_explanation = suggested_method = (
        suggested_solve_script
    ) = ""

    prompt = (
        MTSU_GEN_SYSTEM_PROMPT.replace("<<chall_name>>", chall_name)
        .replace("<<flag_format>>", flag_format)
        .replace("<<chall_desc>>", chall_desc)
    )
    if chall_filepaths:
        for fp in chall_filepaths:
            with open(fp, "r") as f:
                prompt += f"\n###<{fp}>\n{f.read()}"
    else:
        prompt += " Nil"

    ollama_chat = OllamaChat(HOST, method_suggestor_model, prompt)

    log.log_info("Method Suggestor", "Extracting clues...")
    start_time = time()
    ollama_chat.append_message(
        "user",
        "What clues can you extract from the given challenge name, challenge description and challenge files (if any) that can be used to find a solution (DO NOT SUGGEST A SOLUTION!)? Let's think step by step.",
    )
    res = ollama_chat.invoke_and_append_generated_message(stream=True)
    for res_str in res:
        extracted_clues = res_str
        yield extracted_clues, technique_explanation, suggested_method, suggested_solve_script
    end_time = time()
    log.log_info(
        "Method Suggestor", f"Extracted clues in {round(end_time-start_time, 2)}s"
    )

    log.log_info("Method Suggestor", "Generating technique explanation...")
    start_time = time()
    ollama_chat.append_message(
        "user",
        "Based on the given challenge and extracted clues, state and explain the technique(s) that may have been used to obfuscate the flag. Let's think step by step.",
    )
    res = ollama_chat.invoke_and_append_generated_message(stream=True)
    for res_str in res:
        technique_explanation = res_str
        yield extracted_clues, technique_explanation, suggested_method, suggested_solve_script
    end_time = time()
    log.log_info(
        "Method Suggestor",
        f"Generated technique explanation in {round(end_time-start_time, 2)}s",
    )

    log.log_info("Method Suggestor", "Suggesting method...")
    start_time = time()
    ollama_chat.append_message(
        "user",
        "Based on the given challenge, extracted clues and technique explanation, what is a possible method that can be used to solve the given challenge? Let's think step by step.",
    )
    res = ollama_chat.invoke_and_append_generated_message(stream=True)
    for res_str in res:
        suggested_method = res_str
        yield extracted_clues, technique_explanation, suggested_method, suggested_solve_script
    end_time = time()
    log.log_info(
        "Method Suggestor", f"Suggested method in {round(end_time-start_time, 2)}s"
    )

    log.log_info("Method Suggestor", "Generating possible solve script...")
    start_time = time()
    ollama_chat.append_message(
        "user",
        "Finally, based on the given challenge, extracted clues, technique explanation and suggested method, explain how you would write a script to solve the given challenge, then give me a possible solve script for the given challenge. ONLY provide the explanation and given solve script in that order, and nothing else",
    )
    res = ollama_chat.invoke_and_append_generated_message(stream=True)
    for res_str in res:
        suggested_solve_script = res_str
        yield extracted_clues, technique_explanation, suggested_method, suggested_solve_script
    end_time = time()
    log.log_info(
        "Method Suggestor",
        f"Generated solve script in {round(end_time-start_time, 2)}s",
    )

    yield extracted_clues, technique_explanation, suggested_method, suggested_solve_script
