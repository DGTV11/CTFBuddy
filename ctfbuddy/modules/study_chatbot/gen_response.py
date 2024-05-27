from time import time

import gradio as gr
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama

import modules.logging as log
from modules.host import HOST_URL, HOST
from modules.study_chatbot.surf_web import (
    gen_queries,
    search,
    make_vectorstore_retriever,
)
from modules.latent_space_activation.technique01_dialog import lsa_query
from modules.moderate import moderate, check_moderation
from modules.config import CONFIG


def gen_response(
    autosurfer_model: str,
    online_mode: bool,
    moderator_on: bool,
    prompt: str,
    chat_history: list[list[str | None | tuple]],
) -> tuple[str, list[list[str | None | tuple]]]:
    if moderator_on:
        log.log_info("Autosurfer", "Checking prompt for moderation issues")

        start_time = time()
        check_moderation("Autosurfer", moderate(prompt))
        end_time = time()

        log.log_info(
            "Autosurfer",
            f"Checked prompt for moderation issues ({round(end_time-start_time, 2)}s)",
        )
    else:
        log.log_warning("Autosurfer", "Moderation is disabled. Use at your own risk!")

    response_start_time = time()
    if online_mode:
        log.log_info("Autosurfer", "Generating search queries")

        start_time = time()
        queries = gen_queries(prompt)
        end_time = time()

        log.log_info(
            "Autosurfer",
            f"Generated {len(queries)} search queries ({round(end_time-start_time, 2)}s)",
        )

        len_queries = len(queries)
        for i, query in enumerate(queries, start=1):
            log.log_info("Autosurfer", f"Query {i}/{len_queries}: {query}")

        log.log_info("Autosurfer", "Searching web")

        start_time = time()
        search_docs = search(
            CONFIG["google_api_key"], CONFIG["google_prog_search_engine_id"], queries
        )
        end_time = time()
        log.log_info("Autosurfer", f"Searched web ({round(end_time-start_time, 2)}s)")

        start_time = time()
        log.log_info("Autosurfer", "Processing search results...")
        retriever = make_vectorstore_retriever(search_docs)
        end_time = time()
        log.log_info(
            "Autosurfer", f"Processed search results ({round(end_time-start_time, 2)}s)"
        )

        model_local = ChatOllama(
            model=f"guardrailed_{autosurfer_model}", base_url=HOST_URL
        )
        question = prompt
        after_rag_template = """Answer the question based only on the following context:
        {context}
        Question: {question}
        """
        after_rag_prompt = ChatPromptTemplate.from_template(after_rag_template)
        after_rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | after_rag_prompt
            | model_local
            | StrOutputParser()
        )

        log.log_info("Answering question using RAG")

        start_time = time()
        answer = after_rag_chain.invoke(question)
        end_time = time()

        log.log_info(
            "Autosurfer", f"Answered question ({round(end_time-start_time, 2)}s)"
        )
    else:
        answer = ""

        log.log_info("Autosurfer", "Answering question using LSA")

        start_time = time()
        for message in enumerate(
            lsa_query(
                prompt, model=f"guardrailed_{autosurfer_model}", chatbot=HOST.chat
            )
        ):
            if message[0] % 2 == 0:
                log.log_info(
                    "Autosurfer", f'INTERROGATOR sent \'{message[1]["content"]}\''
                )
                answer += f'\n\nINTERROGATOR: {message[1]["content"]}'
            else:
                answer += f'\n\nCHATBOT:\n{message[1]["content"]}'
        end_time = time()

        log.log_info(
            "Autosurfer", f"Answered question ({round(end_time-start_time, 2)}s)"
        )

    if moderator_on:
        log.log_info("Autosurfer", "Checking answer for moderation issues")

        start_time = time()
        check_moderation("Autosurfer", moderate(answer), raise_error_if_moderated=False)
        end_time = time()

        log.log_info(
            "Autosurfer",
            f"Checked answer for moderation issues ({round(end_time-start_time, 2)}s)",
        )

    response_end_time = time()

    log.log_info(
        "Autosurfer",
        f"Finished generating response ({round(response_end_time-response_start_time, 2)}s)",
    )
    chat_history.append((prompt, answer))
    return "", chat_history
