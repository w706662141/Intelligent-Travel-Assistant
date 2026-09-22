import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
_nvidia_model = None
_agnes_model = None
_agnes_tools_model = None
# def get_agnes_model():
# def get_nvidia_model():

def get_nvidia_model():
    global _nvidia_model
    if not _nvidia_model:
        _nvidia_model = ChatOpenAI(
            model='nvidia/nemotron-3.5-lightning:free',
            openai_api_key=os.getenv('OPENROUTER_API_KEY'),
            openai_api_base="https://openrouter.ai/api/v1",
        )

    return _nvidia_model


def get_agnes_model():
    global _agnes_model
    if not _agnes_model:
        _agnes_model = ChatOpenAI(
            model='agnes-3.0-flash',
            openai_api_key=os.getenv('AGNES_API_KEY'),
            openai_api_base="https://apihub.agnes-ai.com/v1",
        )
    return _agnes_model


def get_agnes_tools_model():
    global _agnes_tools_model
    if not _agnes_tools_model:
        _agnes_tools_model = ChatOpenAI(
            model='agnes-3.0-flash',
            openai_api_key=os.getenv('AGNES_API_KEY'),
            openai_api_base="https://apihub.agnes-ai.com/v1",
        )
    return _agnes_tools_model


