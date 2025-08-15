from openai import OpenAI
from flask import g
from .config_manager import get_config

def init_llm_client():
    if 'llm_client' not in g:
        config = get_config()
        g.llm_client = OpenAI(api_key=config['openai_api_key'])

def get_llm_client():
    return g.llm_client
