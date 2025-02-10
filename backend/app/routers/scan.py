import os
import base64
import logging
from fastapi import APIRouter, FastAPI, File, UploadFile, HTTPException

from app.config import ai_settings, settings
from app.services.scanner import Scanner


logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
    format='%(asctime)s - %(levelname)s - %(message)s'
)

router = APIRouter(prefix="/api", tags=["Items"])

@router.post("/process-receipt")
async def process_receipt(image: UploadFile = File(...)):
    """
    Endpoint to process an uploaded receipt image and extract itemized data using a GPT-based service.
    
    Processing Steps:
        1. Validate that the uploaded file is an image.
        2. Read and encode the image in Base64 format.
        3. Send the image to a GPT-based API with instructions to extract itemized receipt information.
        4. Parse the GPT response as a CSV and write it the postgres DB

    Args:
        image (UploadFile): An image file containing a receipt to be processed.

    Returns:
        str: processing response

    Raises:
        HTTPException: 
            - 400 if the uploaded file is not an image or if there is an error reading the image.
            - 500 if there is an error communicating with the GPT API or processing its response.
    """
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, 
                            detail="Invalid file type. Please upload an image.")
    
    try:
        image_data = await image.read()
        base64_image = base64.b64encode(image_data).decode("utf-8")
    except Exception as e:
        logging.error(f"Error proccessing image. {e}")
        raise HTTPException(status_code=400, 
                            detail=f"Error proccessing image: {str(e)}")

    logging.debug(f"Is test? {settings.is_test}")

    if settings.is_test == True:
        output = ai_settings.sample_output
    else:
        scanner = Scanner()
        output = scanner.get_llm_response(base64_image)
        scanner.write_to_db(output)

    logging.debug(f"LLM Output:\n{output}")
    return "Receipt processed successfully"