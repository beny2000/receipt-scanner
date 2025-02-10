import os
import logging
import pandas as pd
from io import StringIO
from openai import OpenAI
from fastapi import HTTPException

from app.db import engine
from app.config import ai_settings, settings


logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Scanner:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.gpt_api_key,
            organization=settings.organziation_key,
            project=settings.project_key
        )

    def get_llm_response(self, base64_image):
        try:
            response = self.client.chat.completions.create(
                model=ai_settings.model_name,
                messages=[
                    {"role": "developer", "content": [
                        {"type": "text", "text": ai_settings.system_prompt}
                    ]},
                    {"role": "user", "content": [
                        {"type": "text", "text": ai_settings.user_prompt},
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/jpg;base64,{base64_image}"
                        }}
                    ]}
                ],
                temperature=0.0,
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Error communicating with GPT API. {e}")
            raise HTTPException(status_code=500, 
                                detail=f"Error communicating with GPT API: {str(e)}")

    def write_to_db(self, output):
        try:
            df = pd.read_csv(StringIO(output))
            df.columns = df.columns.str.strip()
            df = df.drop(columns=['ID'], errors='ignore')
            df.to_sql(
                settings.postgres_table, 
                engine, 
                index=False, 
                if_exists='append'
            )

        except Exception as e:
            logging.error(f"Error writing dataframe to DB. {e}")
            logging.debug(f"LLM Output:\n{output}")
            raise HTTPException(status_code=500, 
                                detail=f"Error writing dataframe to DB: {str(e)}")
