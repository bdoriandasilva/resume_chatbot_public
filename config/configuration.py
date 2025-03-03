import os
def load_config():
    parameters = {
        'openai_api_version': "2023-05-15",
        'model': "text-embedding-ada-002",
        'llm_model': "gpt-4o-mini",
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'azure_ai_search_api_key': os.getenv('AZURE_AI_SEARCH_API_KEY'),
        'azure_ai_search_url': os.getenv('AZURE_AI_SEARCH_URL'),
        'index_name': 'resume_chatbot_index_v2',
        'sql_conn_str': os.getenv('SQL_CONN_STR'),
        'resume_owner_name': os.getenv('RESUME_OWNER_NAME')
    }
    return parameters