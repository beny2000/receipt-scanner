import os
import logging
from pydantic_settings import BaseSettings


logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def read_env(env_var_name: str, default_value: str ='') -> str:
    if os.getenv(env_var_name):
        return os.getenv(env_var_name)
    elif os.getenv(f"{env_var_name}_FILE"):
        with open(os.getenv(f"{env_var_name}_FILE")) as f:
            return f.read()
    elif default_value:
        return default_value
    else:
        logging.error(f"Configuration Error. Missing env value for {env_var_name}")


class Settings(BaseSettings):
    is_test: str = os.getenv("IS_TEST", 'False').lower() == 'true'
    organziation_key: str = read_env('ORGANZIATION_KEY')
    project_key: str = read_env('PROJECT_KEY')
    gpt_api_key: str = read_env('GPT_API_KEY')
    allowed_origins: str = read_env('ALLOWED_ORIGINS').split(',')
    postgres_host: str = read_env('POSTGRES_HOST')
    postgres_port: str = read_env('POSTGRES_PORT', 5432) 
    postgres_user: str = read_env('POSTGRES_USER')
    postgres_password: str = read_env('POSTGRES_PASSWORD')
    postgres_database: str = read_env('POSTGRES_DB')
    postgres_table: str = read_env('POSTGRES_TABLE')


class AISettings: 
    model_name: str = read_env("MODEL_NAME", "gpt-4o-mini")

    system_prompt: str = read_env("SYSTEM_PROMPT")
    
    user_prompt: str = read_env("USER_PROMPT")
    
    sample_output: str = """ID,Item Name,Item Category,Item Price,Location,Date
        1,US Tomato,Vegetable,7.00,Test Supermarket,2025-01-25
        2,Green Bell Pepper,Vegetable,1.63,Test Supermarket,2025-01-25
        3,Carrot Large & Short,Vegetable,2.92,Test Supermarket,2025-01-25
        4,Cooking Onion 2Lb,Vegetable,1.79,Test Supermarket,2025-01-25
        5,Garlic,Vegetable,0.48,Test Supermarket,2025-01-25
        6,Mini Cucumber,Vegetable,4.21,Test Supermarket,2025-01-25
        7,Snow Peas,Vegetable,3.24,Test Supermarket,2025-01-25"""



settings = Settings()
ai_settings = AISettings()


