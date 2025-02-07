import os
import logging
import base64
import pandas as pd
from io import StringIO
from openai import OpenAI
from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine


log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(levelname)s - %(message)s'
)

try:
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
    ORGANZIATION_KEY = os.environ['ORGANZIATION_KEY']
    PROJECT_KEY = os.environ['PROJECT_KEY']
    GPT_API_KEY =  os.environ['GPT_API_KEY']
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS").split(',')
    POSTGRES_HOST = os.environ['POSTGRES_HOST']
    POSTGRES_PORT = os.environ["POSTGRES_PORT"]
    POSTGRES_USER = os.environ['POSTGRES_USER']
    POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
    POSTGRES_DB = os.environ['POSTGRES_DB']
    POSTGRES_TABLE = os.environ['POSTGRES_TABLE']

except Exception as ex:
    logging.error(f"Configuration Error: Missing env var {ex}")
    exit(1)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProcessResult(BaseModel):
    message: str

client = OpenAI(
    api_key=GPT_API_KEY,
    organization=ORGANZIATION_KEY,
    project=PROJECT_KEY
)

def get_llm_response(base64_image):
    try:
        response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "developer", "content": [
                            {"type": "text", 
                             "text": """You are a receipt processor assistant. 
                             Given an image of a receipt, you will return a CSV table of the items in the receipt. 
                             Output only the CSV, nothing more, no markdown formatting either.
                             The following is an example of the header of the CSV table:
                             ID, Item Name, Item Category, Item Price, Location, Date"""
                            }
                        ]},
                        {"role": "user", "content": [
                            {"type": "text", "text": "Output the itemized CSV of the following receipt, use the item type as the categories:"},
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
        raise HTTPException(status_code=500, detail=f"Error communicating with GPT API: {str(e)}")

def write_to_db(output):
    try:
        df = pd.read_csv(StringIO(output))
        df = df.drop(columns=['ID'], errors='ignore')
        
        db_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        engine = create_engine(db_url)

        df.to_sql(POSTGRES_TABLE, engine, index=False, if_exists='append')

    except Exception as e:
        logging.error(f"Error writing dataframe to DB. {e}")
        logging.debug(f"LLM Output:\n{output}")
        raise HTTPException(status_code=500, detail=f"Error writing dataframe to DB: {str(e)}")

@app.post("/api/process-receipt")
async def process_receipt(image: UploadFile = File(...)):
    """
    Endpoint to process an uploaded receipt image and extract itemized data using a GPT-based service.
    
    Processing Steps:
        1. Validate that the uploaded file is an image.
        2. Read and encode the image in Base64 format.
        3. Send the image to a GPT-based API with instructions to extract itemized receipt information.
        4. Parse the GPT response as a CSV and convert it into a JSON-friendly format.
        5. Return the parsed data as a JSON response.

    Args:
        image (UploadFile): An image file containing a receipt to be processed.

    Returns:
        List[Dict]: A list of dictionaries representing the itemized data from the receipt, 
        with columns such as 'Item Name', 'Item Category', 'Item Price', 'Location', and 'Date'.

    Raises:
        HTTPException: 
            - 400 if the uploaded file is not an image or if there is an error reading the image.
            - 500 if there is an error communicating with the GPT API or processing its response.


    """
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    
    try:
        image_data = await image.read()
        base64_image = base64.b64encode(image_data).decode("utf-8")
    except Exception as e:
        logging.error(f"Error proccessing image. {e}")
        raise HTTPException(status_code=400, detail=f"Error proccessing image: {str(e)}")

    logging.debug(f"Is test? {os.getenv('IS_TEST', False)}")
    if os.getenv("IS_TEST", False):
        output = """ID,Item Name,Item Category,Item Price,Location,Date
        1,US Tomato,Vegetable,7.00,Test Supermarket,2025-01-25
        2,Green Bell Pepper,Vegetable,1.63,Test Supermarket,2025-01-25
        3,Carrot Large & Short,Vegetable,2.92,Test Supermarket,2025-01-25
        4,Cooking Onion 2Lb,Vegetable,1.79,Test Supermarket,2025-01-25
        5,Purple Garlic (Loose),Vegetable,0.48,Test Supermarket,2025-01-25
        6,Mini Cucumber (P),Vegetable,4.21,Test Supermarket,2025-01-25
        7,Snow Peas,Vegetable,3.24,Test Supermarket,2025-01-25"""
    else:
        output = get_llm_response(base64_image)
    write_to_db(output)

    logging.debug(f"LLM Output:\n{output}")
    return "Receipt processed successfully"