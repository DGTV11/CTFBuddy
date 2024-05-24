import re
from time import time, sleep
import textwrap
import yaml

from modules.host import HOST

###     constants
PROMPTS = [
    "What information do you already know about this topic? What information do you need to recall into your working memory to best answer this?",
    "What techniques or methods do you know that you can use to answer this question or solve this problem? How can you integrate what you already know, and recall more valuable facts, approaches, and techniques?",
    "And finally, with all this in mind, you will now discuss the question or problem and render your final answer.",
]

SYSTEM = """# MISSION
You are an internal dialog iterator for an LLM (large language model) neural network. LLMs possess "latent space" (embedded knowledge and capabilities). You will be given a main query as well as a sequence of questions. Your role is to answer the queries as a way of "activating" the latent space inside your own neural network. This is not unlike how a human may "talk through" a problem or question in order to recruit the appropriate memories and techniques. The ultimate goal is to answer the main query listed below.

# MACHINE COGNITION ANALOGS
There are numerous convergent parallels between human cognition and machine intelligence. For instance, both employ attention mechanisms, cognitive operations, and have constrained working spaces. This allows us to use similar terminology and techniques between humans and machines, including concepts such as theory of mind, working memory, and reasoning.

# INTERACTION SCHEMA
The USER will play the role of interrogator. Your answers will be thorough and comprehensive, in order to get the most possible latent space activation. Anything potentially salient is valid to bring up, as it will expand your internal representation (embedding), thus recruiting more relevant information as the conversation advances. 

# MAIN QUERY
<<QUERY>>"""


###     API functions
def chatbot(messages, model="mistral"):
    print("Thinking...")

    response = HOST.chat(messages=messages, model=model)

    return response


def chat_print(text):
    formatted_lines = [
        textwrap.fill(line, width=120, initial_indent="    ", subsequent_indent="    ")
        for line in text.split("\n")
    ]
    formatted_text = "\n".join(formatted_lines)
    print("\n\n\nCHATBOT:\n\n%s" % formatted_text)


def lsa_query(main_question, model="mistral", chatbot=HOST.chat):
    conversation = list()
    conversation.append(
        {"role": "system", "content": SYSTEM.replace("<<QUERY>>", main_question)}
    )

    for p in PROMPTS:
        interrogator_message = {"role": "user", "content": p}
        conversation.append(interrogator_message)
        yield interrogator_message

        response = chatbot(messages=conversation, model=model)["message"]["content"]

        assistant_message = {"role": "assistant", "content": response}
        conversation.append(assistant_message)
        yield assistant_message


if __name__ == "__main__":
    main_question = input("What is your main query or question? ")

    for message in enumerate(
        lsa_query(main_question, model="mistral", chatbot=chatbot)
    ):
        if message[0] % 2 == 0:
            print("\n\n\nINTERROGATOR: %s" % message[1]["content"])
        else:
            print("\n\n\nCHATBOT:\n%s" % message[1]["content"])

    a = input("Press enter to end.")
